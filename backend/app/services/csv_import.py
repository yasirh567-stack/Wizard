"""WIZ-4: CSV transaction import.

Documented column format (header required, extra columns ignored):
    date,amount,name,merchant_name,category

- date: YYYY-MM-DD or MM/DD/YYYY
- amount: decimal; Plaid convention — positive = money out, negative = money in
- name: required, the transaction description
- merchant_name, category: optional

Malformed rows are reported individually (row number + reason) and skipped;
they never abort the rest of the file.
"""

import csv
import io
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction
from app.services.content_hash import compute_content_hash

REQUIRED_COLUMNS = {"date", "amount", "name"}
_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y")


class CsvFormatError(ValueError):
    """The file itself is malformed (no header, missing required columns)."""


@dataclass
class RowError:
    row: int
    reason: str


@dataclass
class ImportResult:
    imported: int = 0
    skipped: int = 0
    errors: list[RowError] = field(default_factory=list)


def _parse_date(raw: str) -> date:
    raw = raw.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognized date format: {raw!r}")


def import_csv(db: Session, account: Account, csv_text: str) -> ImportResult:
    reader = csv.DictReader(io.StringIO(csv_text))

    if not reader.fieldnames:
        raise CsvFormatError("file is empty or has no header row")

    normalized_fieldnames = {name: name.strip().lower() for name in reader.fieldnames}
    missing = REQUIRED_COLUMNS - set(normalized_fieldnames.values())
    if missing:
        raise CsvFormatError(f"missing required column(s): {', '.join(sorted(missing))}")

    result = ImportResult()

    for row_number, raw_row in enumerate(reader, start=2):  # header is row 1
        row = {
            normalized_fieldnames[key]: (value.strip() if value else value)
            for key, value in raw_row.items()
            if key in normalized_fieldnames
        }

        try:
            txn_date = _parse_date(row.get("date") or "")
        except ValueError as exc:
            result.errors.append(RowError(row=row_number, reason=str(exc)))
            result.skipped += 1
            continue

        raw_amount = row.get("amount") or ""
        try:
            amount = Decimal(raw_amount)
        except InvalidOperation:
            result.errors.append(RowError(row=row_number, reason=f"invalid amount: {raw_amount!r}"))
            result.skipped += 1
            continue

        name = row.get("name") or ""
        if not name:
            result.errors.append(RowError(row=row_number, reason="name is required"))
            result.skipped += 1
            continue

        merchant_name = row.get("merchant_name") or None
        category = row.get("category") or None

        content_hash = compute_content_hash(account.id, txn_date, amount, merchant_name)
        existing = db.scalar(select(Transaction).where(Transaction.content_hash == content_hash))
        if existing is None:
            db.add(
                Transaction(
                    account_id=account.id,
                    content_hash=content_hash,
                    date=txn_date,
                    amount=amount,
                    merchant_name=merchant_name,
                    name=name,
                    category=category,
                    pending=False,
                )
            )
        result.imported += 1

    return result
