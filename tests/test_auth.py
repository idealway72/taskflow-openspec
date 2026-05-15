def test_signup_success(client):
    """회원가입 성공 — 정상 이메일+비밀번호로 201 + JWT 반환"""
    res = client.post("/api/auth/signup", json={"email": "new@example.com", "password": "password123"})
    assert res.status_code == 201
    data = res.json()
    assert "token" in data
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["team_id"] is None


def test_signup_duplicate_email(client, registered_user):
    """회원가입 실패 — 중복 이메일 → 409 EMAIL_TAKEN"""
    res = client.post("/api/auth/signup", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "EMAIL_TAKEN"


def test_signup_invalid_email(client):
    """회원가입 실패 — 이메일 형식 오류 → 422 VALIDATION_ERROR"""
    res = client.post("/api/auth/signup", json={"email": "not-an-email", "password": "password123"})
    assert res.status_code == 422


def test_signup_short_password(client):
    """회원가입 실패 — 비밀번호 8자 미만 → 422 VALIDATION_ERROR"""
    res = client.post("/api/auth/signup", json={"email": "x@example.com", "password": "short"})
    assert res.status_code == 422


def test_login_success(client, registered_user):
    """로그인 성공 — 올바른 자격증명 → 200 + JWT"""
    res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "token" in res.json()


def test_login_wrong_password(client, registered_user):
    """로그인 실패 — 틀린 비밀번호 → 401 INVALID_CREDENTIALS"""
    res = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrongpass"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_email(client):
    """로그인 실패 — 존재하지 않는 이메일 → 401 INVALID_CREDENTIALS"""
    res = client.post("/api/auth/login", json={"email": "unknown@example.com", "password": "password123"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_success(client, registered_user, auth_headers):
    """현재 사용자 조회 — 유효한 JWT → 200 + 사용자 정보"""
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"


def test_me_no_token(client):
    """현재 사용자 조회 실패 — 토큰 없음 → 401 TOKEN_EXPIRED"""
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "TOKEN_EXPIRED"


def test_logout(client, auth_headers):
    """로그아웃 — stateless 처리 → 200 반환"""
    res = client.post("/api/auth/logout", headers=auth_headers)
    assert res.status_code == 200
