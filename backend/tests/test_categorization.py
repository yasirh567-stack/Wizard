"""WIZ-7 (auto-categorization), WIZ-8 (confidence + manual override), and
WIZ-9 (correction propagation), plus the held-out precision/recall check
ROADMAP.md's Phase 2 exit criteria calls for explicitly ("measured against
a held-out labeled set, not eyeballed").
"""

from datetime import date

from app.core.security import hash_password
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.services.categorization import categorize_transaction
from app.services.category_taxonomy import UNCATEGORIZED


def _auth_headers(client, email="cat@example.com"):
    client.post("/auth/register", json={"email": email, "password": "hunter22"})
    login = client.post("/auth/login", data={"username": email, "password": "hunter22"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_user(db_session, email):
    user = User(email=email, hashed_password=hash_password("x"))
    db_session.add(user)
    db_session.flush()
    return user


def _categorize(db_session, user, merchant_name, name="Purchase"):
    txn = Transaction(
        account_id=None,
        date=date(2026, 1, 1),
        amount=10,
        merchant_name=merchant_name,
        name=name,
        pending=False,
    )
    categorize_transaction(db_session, txn, user.id)
    category = db_session.get(Category, txn.category_id)
    return category.name, txn.category_confidence, txn.category_source


# Deliberately different literal strings than the demo-seed/keyword-rule
# source data — a genuinely held-out check of whether the rule-seeded
# categorizer generalizes, not a replay of its own seed data.
HELD_OUT_LABELED_SET = [
    ("Whole Foods Market #204", "Groceries"),
    ("Trader Joe's #512", "Groceries"),
    ("Safeway Pharmacy", "Groceries"),
    ("Costco Wholesale Corp", "Groceries"),
    ("Chipotle Mexican Grill", "Restaurants"),
    ("Sweetgreen Union Square", "Restaurants"),
    ("Downtown Thai Kitchen Takeout", "Restaurants"),
    ("Shell Gas Station #4521", "Gas"),
    ("Chevron Fuel Stop", "Gas"),
    ("Amazon Marketplace", "Shopping"),
    ("Target.com Order", "Shopping"),
    ("Best Buy Online Order", "Shopping"),
    ("Netflix.com Subscription", "Entertainment"),
    ("Spotify USA Inc", "Entertainment"),
    ("Comcast Xfinity Internet", "Internet and Cable"),
    ("Verizon Fios Phone Bill", "Phone"),
    ("Anytime Fitness Downtown", "Gyms and Fitness Centers"),
    ("ACME Landlord Rent Co", "Rent and Utilities"),
    ("ACME Corp Payroll Services", "Income"),
    ("Internal Transfer to Savings", "Transfer"),
    ("Joe's Local Pizza Truck", UNCATEGORIZED),
    ("Unknown Vendor LLC", UNCATEGORIZED),
    ("Random Merchant 123", UNCATEGORIZED),
    ("Mystery Charge Co", UNCATEGORIZED),
]


def test_categorization_precision_and_recall_on_held_out_set(db_session):
    user = _make_user(db_session, "holdout@example.com")

    results = []
    for merchant_name, expected in HELD_OUT_LABELED_SET:
        actual, _confidence, _source = _categorize(db_session, user, merchant_name)
        results.append((merchant_name, expected, actual))

    predicted_positive = [r for r in results if r[2] != UNCATEGORIZED]
    correct_positive = [r for r in predicted_positive if r[2] == r[1]]
    precision = len(correct_positive) / len(predicted_positive) if predicted_positive else 0.0

    expected_positive = [r for r in results if r[1] != UNCATEGORIZED]
    recalled = [r for r in expected_positive if r[2] == r[1]]
    recall = len(recalled) / len(expected_positive) if expected_positive else 0.0

    mismatches = [r for r in results if r[2] != r[1]]
    assert precision >= 0.9, f"precision {precision:.2f} below threshold; mismatches: {mismatches}"
    assert recall >= 0.8, f"recall {recall:.2f} below threshold; mismatches: {mismatches}"


def test_known_merchant_categorized_with_high_confidence(db_session):
    user = _make_user(db_session, "known@example.com")
    category, confidence, source = _categorize(db_session, user, "Netflix")
    assert category == "Entertainment"
    assert source == "rule"
    assert confidence > 0.5


def test_unknown_merchant_falls_back_to_uncategorized_not_null(db_session):
    user = _make_user(db_session, "unknown@example.com")
    category, confidence, source = _categorize(db_session, user, "Totally Unrecognizable Vendor Co")
    assert category == UNCATEGORIZED
    assert source == "uncategorized"
    assert confidence < 0.5


def test_demo_data_lands_categorized(client, db_session):
    headers = _auth_headers(client, email="demo-cat@example.com")
    client.post("/demo/load", headers=headers)

    transactions = db_session.query(Transaction).all()
    assert len(transactions) > 0
    assert all(t.category_id is not None for t in transactions)
    assert all(t.category_confidence is not None for t in transactions)


def test_manual_correction_is_a_single_call_applied_immediately(client, db_session):
    headers = _auth_headers(client, email="correct@example.com")
    files = {"file": ("t.csv", "date,amount,name,merchant_name\n2026-01-05,9.99,Mystery charge,Weird Co\n", "text/csv")}
    upload = client.post("/transactions/csv-upload", headers=headers, files=files)
    transaction_id = db_session.query(Transaction).filter(Transaction.merchant_name == "Weird Co").one().id

    groceries = db_session.query(Category).filter(Category.name == "Groceries").one()

    response = client.patch(
        f"/transactions/{transaction_id}/category",
        headers=headers,
        json={"category_id": str(groceries.id)},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category_id"] == str(groceries.id)
    assert body["category_source"] == "manual"
    assert body["category_confidence"] == 1.0


def test_correction_propagates_to_future_transactions_same_merchant(client, db_session):
    headers = _auth_headers(client, email="propagate@example.com")

    first_csv = {
        "file": (
            "t.csv",
            "date,amount,name,merchant_name\n2026-01-05,9.99,Charge one,Weird Co\n",
            "text/csv",
        )
    }
    client.post("/transactions/csv-upload", headers=headers, files=first_csv)
    first_txn = db_session.query(Transaction).filter(Transaction.merchant_name == "Weird Co").one()

    groceries = db_session.query(Category).filter(Category.name == "Groceries").one()
    client.patch(
        f"/transactions/{first_txn.id}/category",
        headers=headers,
        json={"category_id": str(groceries.id)},
    )

    second_csv = {
        "file": (
            "t.csv",
            "date,amount,name,merchant_name\n2026-02-05,12.50,Charge two,Weird Co\n",
            "text/csv",
        )
    }
    client.post(
        "/transactions/csv-upload",
        headers=headers,
        files=second_csv,
        data={"account_id": str(first_txn.account_id)},
    )

    second_txn = (
        db_session.query(Transaction)
        .filter(Transaction.merchant_name == "Weird Co", Transaction.id != first_txn.id)
        .one()
    )
    assert str(second_txn.category_id) == str(groceries.id)
    assert second_txn.category_source == "manual"


def test_correction_does_not_leak_across_users(client, db_session):
    headers_a = _auth_headers(client, email="usera@example.com")
    headers_b = _auth_headers(client, email="userb@example.com")

    csv_content = "date,amount,name,merchant_name\n2026-01-05,9.99,Charge,Weird Co\n"
    client.post(
        "/transactions/csv-upload",
        headers=headers_a,
        files={"file": ("t.csv", csv_content, "text/csv")},
    )
    txn_a = db_session.query(Transaction).filter(Transaction.merchant_name == "Weird Co").one()
    groceries = db_session.query(Category).filter(Category.name == "Groceries").one()
    client.patch(
        f"/transactions/{txn_a.id}/category",
        headers=headers_a,
        json={"category_id": str(groceries.id)},
    )

    client.post(
        "/transactions/csv-upload",
        headers=headers_b,
        files={"file": ("t.csv", csv_content, "text/csv")},
    )
    txn_b = (
        db_session.query(Transaction)
        .filter(Transaction.merchant_name == "Weird Co", Transaction.id != txn_a.id)
        .one()
    )
    assert str(txn_b.category_id) != str(groceries.id)
    assert txn_b.category_source == "uncategorized"
