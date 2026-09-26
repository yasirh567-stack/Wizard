from app.models.account import Account
from app.models.transaction import Transaction


def _auth_headers(client, email="demo@example.com"):
    client.post("/auth/register", json={"email": email, "password": "hunter22"})
    login = client.post("/auth/login", data={"username": email, "password": "hunter22"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_load_demo_data_creates_accounts_and_12_months_of_history(client, db_session):
    headers = _auth_headers(client)

    response = client.post("/demo/load", headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["accounts_created"] == 3
    assert body["transactions_created"] > 0

    accounts = db_session.query(Account).all()
    assert len(accounts) == 3
    assert all(account.source == "demo" for account in accounts)

    transactions = db_session.query(Transaction).all()
    assert len(transactions) == body["transactions_created"]

    span_days = (max(t.date for t in transactions) - min(t.date for t in transactions)).days
    assert span_days >= 365


def test_reloading_demo_data_replaces_rather_than_duplicates(client):
    headers = _auth_headers(client, email="demo2@example.com")

    client.post("/demo/load", headers=headers)
    second = client.post("/demo/load", headers=headers)
    assert second.status_code == 201
    assert second.json()["accounts_created"] == 3

    accounts_response = client.get("/accounts", headers=headers)
    assert len(accounts_response.json()) == 3


def test_demo_load_requires_auth(client):
    response = client.post("/demo/load")
    assert response.status_code == 401
