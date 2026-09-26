def _auth_headers(client, email="csv@example.com"):
    client.post("/auth/register", json={"email": email, "password": "hunter22"})
    login = client.post("/auth/login", data={"username": email, "password": "hunter22"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_csv_upload_imports_valid_rows_and_reports_bad_ones_individually(client):
    headers = _auth_headers(client)

    csv_content = (
        "date,amount,name,merchant_name,category\n"
        "2026-01-05,42.50,Coffee shop,Blue Bottle,Restaurants\n"
        "not-a-date,10.00,Bad date row,,\n"
        "2026-01-06,not-a-number,Bad amount row,,\n"
        "2026-01-07,15.00,,,\n"
        "2026-01-08,99.99,Groceries,Whole Foods,Groceries\n"
    )
    files = {"file": ("transactions.csv", csv_content, "text/csv")}
    response = client.post(
        "/transactions/csv-upload", headers=headers, files=files, data={"account_name": "My Bank"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["imported"] == 2
    assert body["skipped"] == 3
    assert {e["row"] for e in body["errors"]} == {3, 4, 5}
    # one bad row per failure category, and the rest of the file still landed
    assert not any("Bad amount row" in e["reason"] for e in body["errors"])

    transactions_response = client.get("/transactions", headers=headers)
    assert len(transactions_response.json()) == 2


def test_csv_upload_missing_required_column_is_rejected(client):
    headers = _auth_headers(client, email="csv2@example.com")
    csv_content = "foo,bar\n1,2\n"
    files = {"file": ("bad.csv", csv_content, "text/csv")}

    response = client.post("/transactions/csv-upload", headers=headers, files=files)

    assert response.status_code == 400


def test_csv_reupload_of_same_rows_is_deduped(client):
    headers = _auth_headers(client, email="csv3@example.com")
    csv_content = "date,amount,name\n2026-02-01,20.00,Gas station\n"

    first = client.post(
        "/transactions/csv-upload",
        headers=headers,
        files={"file": ("transactions.csv", csv_content, "text/csv")},
    )
    account_id = first.json()["account_id"]

    second = client.post(
        "/transactions/csv-upload",
        headers=headers,
        files={"file": ("transactions.csv", csv_content, "text/csv")},
        data={"account_id": account_id},
    )
    assert second.status_code == 201

    transactions_response = client.get("/transactions", headers=headers)
    assert len(transactions_response.json()) == 1


def test_csv_upload_requires_auth(client):
    files = {"file": ("transactions.csv", "date,amount,name\n", "text/csv")}
    response = client.post("/transactions/csv-upload", files=files)
    assert response.status_code == 401
