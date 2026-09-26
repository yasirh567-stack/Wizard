import hashlib
import uuid
from datetime import date as date_type
from decimal import Decimal


def compute_content_hash(
    account_id: uuid.UUID, txn_date: date_type, amount: Decimal, merchant_name: str | None
) -> str:
    """WIZ-5 dedup key for the CSV/demo path: date+amount+merchant+account."""
    raw = f"{account_id}|{txn_date.isoformat()}|{amount}|{merchant_name or ''}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
