"""Transaction sync via Plaid's /transactions/sync endpoint.

This is the single place WIZ-5 (no duplicate rows on re-sync) and WIZ-6
(pending -> posted updates in place) get implemented, because both are
consequences of how this endpoint's cursor and added/modified/removed
payload are handled, not separate logic bolted on afterward.
"""

from typing import Any

from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.encryption import decrypt
from app.models.account import Account
from app.models.plaid_item import PlaidItem
from app.models.transaction import Transaction


def sync_transactions(db: Session, client: plaid_api.PlaidApi, item: PlaidItem) -> dict[str, int]:
    access_token = decrypt(item.access_token_encrypted)
    cursor = item.cursor
    has_more = True
    added_count = modified_count = removed_count = 0

    accounts_by_plaid_id = {
        account.plaid_account_id: account
        for account in db.scalars(select(Account).where(Account.plaid_item_id == item.id))
    }

    while has_more:
        # The SDK's request model rejects cursor=None outright — omit it
        # entirely for the very first page instead of passing null.
        request_kwargs = {"access_token": access_token}
        if cursor is not None:
            request_kwargs["cursor"] = cursor
        response = client.transactions_sync(TransactionsSyncRequest(**request_kwargs))

        for txn in response.added:
            _upsert_transaction(db, accounts_by_plaid_id, txn)
            added_count += 1

        for txn in response.modified:
            _upsert_transaction(db, accounts_by_plaid_id, txn)
            modified_count += 1

        # Flush before processing removals: a pending transaction posting
        # shows up as an "added" row that repoints an existing transaction's
        # plaid_transaction_id (see _upsert_transaction) *and* a "removed"
        # entry for that same old id. Without flushing first, the removed
        # lookup below still sees the old id in the database and deletes the
        # row the added step just relinked, instead of leaving it alone.
        db.flush()

        for removed in response.removed:
            existing = db.scalar(
                select(Transaction).where(Transaction.plaid_transaction_id == removed.transaction_id)
            )
            if existing is not None:
                db.delete(existing)
                removed_count += 1

        cursor = response.next_cursor
        has_more = response.has_more

    item.cursor = cursor
    db.add(item)
    db.commit()

    return {"added": added_count, "modified": modified_count, "removed": removed_count}


def _upsert_transaction(db: Session, accounts_by_plaid_id: dict[str, Account], txn: Any) -> None:
    account = accounts_by_plaid_id.get(txn.account_id)
    if account is None:
        # Transaction belongs to an account this item wasn't connected for.
        return

    existing = db.scalar(
        select(Transaction).where(Transaction.plaid_transaction_id == txn.transaction_id)
    )

    if existing is None and txn.pending_transaction_id:
        # WIZ-6: this is the posted counterpart of a pending row we already
        # have — update it in place instead of inserting a second row.
        existing = db.scalar(
            select(Transaction).where(Transaction.plaid_transaction_id == txn.pending_transaction_id)
        )

    if existing is None:
        existing = Transaction(account_id=account.id)

    category = None
    if getattr(txn, "personal_finance_category", None) is not None:
        category = txn.personal_finance_category.primary
    elif txn.category:
        category = txn.category[0]

    existing.plaid_transaction_id = txn.transaction_id
    existing.pending_transaction_id = txn.pending_transaction_id
    existing.date = txn.date
    existing.amount = txn.amount
    existing.merchant_name = txn.merchant_name
    existing.name = txn.name
    existing.category = category
    existing.pending = txn.pending

    db.add(existing)
