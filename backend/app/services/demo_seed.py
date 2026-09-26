"""WIZ-3: synthetic transaction history so the product is explorable with
zero external calls (no Plaid sandbox credentials needed).
"""

import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.services.content_hash import compute_content_hash

MONTHS_OF_HISTORY = 13

_RECURRING_CHECKING_BILLS = [
    # (merchant, name, category, amount, day_of_month)
    ("Landlord LLC", "Rent Payment", "Rent and Utilities", Decimal("1450.00"), 1),
    ("Comcast", "Internet Bill", "Internet and Cable", Decimal("60.00"), 3),
    ("Verizon Wireless", "Phone Bill", "Phone", Decimal("45.00"), 5),
    ("Anytime Fitness", "Gym Membership", "Gyms and Fitness Centers", Decimal("30.00"), 8),
]

_RECURRING_CARD_SUBSCRIPTIONS = [
    ("Netflix", "Netflix Subscription", "Entertainment", Decimal("15.49"), 10),
    ("Spotify", "Spotify Premium", "Entertainment", Decimal("10.99"), 14),
]

_DISCRETIONARY_CATEGORIES = {
    "Groceries": (["Trader Joe's", "Whole Foods", "Safeway", "Costco"], (25, 140)),
    "Restaurants": (["Chipotle", "Sweetgreen", "Local Diner", "Thai Kitchen"], (10, 60)),
    "Gas": (["Shell", "Chevron", "76"], (30, 70)),
    "Shopping": (["Amazon", "Target", "Best Buy"], (15, 200)),
}


def _month_starts(start: date, end: date):
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        yield cursor
        cursor = date(cursor.year + 1, 1, 1) if cursor.month == 12 else date(cursor.year, cursor.month + 1, 1)


def _day_in_month(month_start: date, day: int) -> date | None:
    try:
        return date(month_start.year, month_start.month, day)
    except ValueError:
        return None


def _add_transaction(
    db: Session,
    account: Account,
    txn_date: date,
    amount: Decimal,
    merchant_name: str | None,
    name: str,
    category: str | None,
) -> None:
    content_hash = compute_content_hash(account.id, txn_date, amount, merchant_name)
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


def generate_demo_data(db: Session, user: User) -> dict[str, int]:
    # Reloading demo data replaces the previous set rather than piling on
    # top of it — cascade delete takes the old transactions with it.
    existing_demo_accounts = db.scalars(
        select(Account).where(Account.user_id == user.id, Account.source == "demo")
    ).all()
    for account in existing_demo_accounts:
        db.delete(account)
    db.flush()

    rng = random.Random()

    checking = Account(
        user_id=user.id,
        source="demo",
        name="Demo Checking",
        official_name="Demo Checking Account",
        type="depository",
        subtype="checking",
        mask="1111",
    )
    savings = Account(
        user_id=user.id,
        source="demo",
        name="Demo Savings",
        official_name="Demo Savings Account",
        type="depository",
        subtype="savings",
        mask="2222",
    )
    credit_card = Account(
        user_id=user.id,
        source="demo",
        name="Demo Credit Card",
        official_name="Demo Rewards Card",
        type="credit",
        subtype="credit card",
        mask="3333",
    )
    db.add_all([checking, savings, credit_card])
    db.flush()

    today = date.today()
    start = today - timedelta(days=30 * MONTHS_OF_HISTORY)
    transactions_created = 0

    # Biweekly paycheck into checking. Plaid convention: negative = money in.
    payday = start
    while payday <= today:
        _add_transaction(
            db, checking, payday, Decimal("-2100.00"), "Employer Inc", "Payroll Deposit", "Income"
        )
        transactions_created += 1
        payday += timedelta(days=14)

    for month_start in _month_starts(start, today):
        for merchant, name, category, amount, day in _RECURRING_CHECKING_BILLS:
            txn_date = _day_in_month(month_start, day)
            if txn_date and start <= txn_date <= today:
                _add_transaction(db, checking, txn_date, amount, merchant, name, category)
                transactions_created += 1

        for merchant, name, category, amount, day in _RECURRING_CARD_SUBSCRIPTIONS:
            txn_date = _day_in_month(month_start, day)
            if txn_date and start <= txn_date <= today:
                _add_transaction(db, credit_card, txn_date, amount, merchant, name, category)
                transactions_created += 1

        transfer_date = _day_in_month(month_start, 20)
        if transfer_date and start <= transfer_date <= today:
            _add_transaction(
                db, savings, transfer_date, Decimal("-200.00"), "Internal Transfer",
                "Transfer from Checking", "Transfer",
            )
            transactions_created += 1

    # Discretionary card spend, roughly 3 times a week.
    current = start
    while current <= today:
        if rng.random() < 3 / 7:
            category = rng.choice(list(_DISCRETIONARY_CATEGORIES.keys()))
            merchants, (low, high) = _DISCRETIONARY_CATEGORIES[category]
            merchant = rng.choice(merchants)
            amount = Decimal(str(round(rng.uniform(low, high), 2)))
            _add_transaction(db, credit_card, current, amount, merchant, f"{merchant} purchase", category)
            transactions_created += 1
        current += timedelta(days=1)

    db.commit()

    return {"accounts_created": 3, "transactions_created": transactions_created}
