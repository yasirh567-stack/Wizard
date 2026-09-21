"""Tests for WIZ-5 (no duplicates on re-sync) and WIZ-6 (pending -> posted
updates in place), against a fake Plaid client so these don't depend on
live sandbox credentials.
"""

import uuid
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.core.encryption import encrypt
from app.core.security import hash_password
from app.models.account import Account
from app.models.plaid_item import PlaidItem
from app.models.transaction import Transaction
from app.models.user import User
from app.services.plaid_sync import sync_transactions


class FakePlaidClient:
    def __init__(self, responses):
        self._responses = list(responses)

    def transactions_sync(self, request):
        return self._responses.pop(0)


def _txn(transaction_id, account_id, amount, pending, pending_transaction_id=None):
    return SimpleNamespace(
        transaction_id=transaction_id,
        account_id=account_id,
        pending_transaction_id=pending_transaction_id,
        date=date(2026, 1, 1),
        amount=Decimal(str(amount)),
        merchant_name="Merchant",
        name="Coffee",
        category=["Food and Drink"],
        personal_finance_category=None,
        pending=pending,
    )


def _make_item(db_session, plaid_account_id):
    user = User(email=f"{uuid.uuid4()}@example.com", hashed_password=hash_password("x"))
    db_session.add(user)
    db_session.flush()

    item = PlaidItem(
        user_id=user.id,
        plaid_item_id=f"item-{uuid.uuid4()}",
        access_token_encrypted=encrypt("access-sandbox-token"),
    )
    db_session.add(item)
    db_session.flush()

    account = Account(
        user_id=user.id,
        plaid_item_id=item.id,
        plaid_account_id=plaid_account_id,
        source="plaid",
        name="Checking",
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(item)
    return item, account


def test_sync_creates_transaction_and_resync_is_noop(db_session):
    item, account = _make_item(db_session, plaid_account_id="acc-1")

    added = _txn("txn-1", account.plaid_account_id, 12.50, pending=True)
    first_response = SimpleNamespace(
        added=[added], modified=[], removed=[], next_cursor="cursor-1", has_more=False
    )
    result = sync_transactions(db_session, FakePlaidClient([first_response]), item)
    assert result == {"added": 1, "modified": 0, "removed": 0}

    rows = db_session.query(Transaction).filter(Transaction.account_id == account.id).all()
    assert len(rows) == 1
    assert rows[0].plaid_transaction_id == "txn-1"
    assert rows[0].pending is True

    # Re-running a sync against unchanged data (Plaid returns an empty page
    # for the same cursor) must not move the row count — WIZ-5.
    empty_response = SimpleNamespace(
        added=[], modified=[], removed=[], next_cursor="cursor-1", has_more=False
    )
    result_2 = sync_transactions(db_session, FakePlaidClient([empty_response]), item)
    assert result_2 == {"added": 0, "modified": 0, "removed": 0}

    rows_after = db_session.query(Transaction).filter(Transaction.account_id == account.id).all()
    assert len(rows_after) == 1


def test_pending_transaction_updates_in_place_on_posting(db_session):
    item, account = _make_item(db_session, plaid_account_id="acc-2")

    pending_txn = _txn("txn-pending-1", account.plaid_account_id, 42.00, pending=True)
    first_response = SimpleNamespace(
        added=[pending_txn], modified=[], removed=[], next_cursor="c1", has_more=False
    )
    sync_transactions(db_session, FakePlaidClient([first_response]), item)

    # Plaid's real behavior when a pending charge posts: a "removed" for the
    # old pending transaction_id, plus an "added" for a new transaction_id
    # that references the old one via pending_transaction_id.
    posted_txn = _txn(
        "txn-posted-1",
        account.plaid_account_id,
        42.00,
        pending=False,
        pending_transaction_id="txn-pending-1",
    )
    removed = SimpleNamespace(transaction_id="txn-pending-1")
    second_response = SimpleNamespace(
        added=[posted_txn], modified=[], removed=[removed], next_cursor="c2", has_more=False
    )
    sync_transactions(db_session, FakePlaidClient([second_response]), item)

    rows = db_session.query(Transaction).filter(Transaction.account_id == account.id).all()
    assert len(rows) == 1, "pending->posted must update the existing row, never insert a second one"
    assert rows[0].plaid_transaction_id == "txn-posted-1"
    assert rows[0].pending is False
