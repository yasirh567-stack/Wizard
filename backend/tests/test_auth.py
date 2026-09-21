def test_register_and_login(client):
    register_response = client.post(
        "/auth/register", json={"email": "user@example.com", "password": "hunter22"}
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "user@example.com"
    assert "password" not in register_response.json()

    login_response = client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "hunter22"},
    )
    assert login_response.status_code == 200
    body = login_response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_duplicate_email_rejected(client):
    client.post("/auth/register", json={"email": "dupe@example.com", "password": "hunter22"})
    second = client.post("/auth/register", json={"email": "dupe@example.com", "password": "other123"})
    assert second.status_code == 400


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json={"email": "user2@example.com", "password": "hunter22"})
    response = client.post(
        "/auth/login", data={"username": "user2@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/accounts")
    assert response.status_code == 401


def test_protected_route_rejects_invalid_token(client):
    response = client.get("/accounts", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_protected_route_accepts_valid_token(client):
    client.post("/auth/register", json={"email": "user3@example.com", "password": "hunter22"})
    login_response = client.post(
        "/auth/login", data={"username": "user3@example.com", "password": "hunter22"}
    )
    token = login_response.json()["access_token"]

    response = client.get("/accounts", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []
