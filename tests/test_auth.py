def test_signup_success(client):
    res = client.post("/api/auth/signup", json={"email": "new@example.com", "password": "password123"})
    assert res.status_code == 201
    data = res.json()
    assert "token" in data
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["team_id"] is None


def test_signup_duplicate_email(client, registered_user):
    res = client.post("/api/auth/signup", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "EMAIL_TAKEN"


def test_signup_invalid_email(client):
    res = client.post("/api/auth/signup", json={"email": "not-an-email", "password": "password123"})
    assert res.status_code == 422


def test_signup_short_password(client):
    res = client.post("/api/auth/signup", json={"email": "x@example.com", "password": "short"})
    assert res.status_code == 422


def test_login_success(client, registered_user):
    res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "token" in res.json()


def test_login_wrong_password(client, registered_user):
    res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrongpass"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_email(client):
    res = client.post("/api/auth/login", json={"email": "unknown@example.com", "password": "password123"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_success(client, registered_user, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"


def test_me_no_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "TOKEN_EXPIRED"


def test_logout(client, auth_headers):
    res = client.post("/api/auth/logout", headers=auth_headers)
    assert res.status_code == 200
