def test_create_team(client, registered_user, auth_headers):
    """팀 생성 성공 — 팀명 입력 → 201 + 초대코드(AAAA-9999 형식) 발급"""
    res = client.post("/api/teams", json={"name": "My Team"}, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "My Team"
    assert len(data["invite_code"]) == 9
    import re
    assert re.match(r"^[A-Z]{4}-[0-9]{4}$", data["invite_code"])


def test_create_team_invalid_name(client, auth_headers):
    """팀 생성 실패 — 빈 팀명 → 422 VALIDATION_ERROR"""
    res = client.post("/api/teams", json={"name": ""}, headers=auth_headers)
    assert res.status_code == 422


def test_join_team(client, team_with_auth):
    """초대코드 합류 성공 — 유효한 코드로 → 200 + 팀 정보"""
    invite_code = team_with_auth["team"]["invite_code"]
    res2 = client.post("/api/auth/signup", json={"email": "member@example.com", "password": "password123"})
    token2 = res2.json()["token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    res = client.post("/api/teams/join", json={"invite_code": invite_code}, headers=headers2)
    assert res.status_code == 200
    assert res.json()["team"]["name"] == "Test Team"


def test_join_team_already_in_team(client, team_with_auth):
    """초대코드 합류 실패 — 이미 팀 소속 → 409 ALREADY_IN_TEAM"""
    invite_code = team_with_auth["team"]["invite_code"]
    res = client.post("/api/teams/join", json={"invite_code": invite_code}, headers=team_with_auth["headers"])
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "ALREADY_IN_TEAM"


def test_join_team_not_found(client, registered_user, auth_headers):
    """초대코드 합류 실패 — 존재하지 않는 코드 → 404 NOT_FOUND"""
    res = client.post("/api/teams/join", json={"invite_code": "XXXX-9999"}, headers=auth_headers)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_join_team_invalid_code_format(client, registered_user, auth_headers):
    """초대코드 합류 실패 — 형식 오류(소문자 등) → 422 VALIDATION_ERROR"""
    res = client.post("/api/teams/join", json={"invite_code": "abcd1234"}, headers=auth_headers)
    assert res.status_code == 422


def test_get_team(client, team_with_auth):
    """팀 정보 조회 성공 — 팀 멤버 → 200 + 팀 정보"""
    team_id = team_with_auth["team"]["id"]
    res = client.get(f"/api/teams/{team_id}", headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert res.json()["id"] == team_id


def test_get_team_forbidden(client, team_with_auth):
    """팀 정보 조회 실패 — 비멤버 접근 → 403 FORBIDDEN"""
    team_id = team_with_auth["team"]["id"]
    res2 = client.post("/api/auth/signup", json={"email": "other@example.com", "password": "password123"})
    token2 = res2.json()["token"]
    res = client.get(f"/api/teams/{team_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_get_members(client, team_with_auth):
    """팀 멤버 목록 조회 성공 — owner 표시 포함"""
    team_id = team_with_auth["team"]["id"]
    res = client.get(f"/api/teams/{team_id}/members", headers=team_with_auth["headers"])
    assert res.status_code == 200
    members = res.json()
    assert len(members) == 1
    assert members[0]["is_owner"] is True


def test_leave_team_owner_cannot_leave(client, team_with_auth):
    """팀 탈퇴 실패 — owner는 팀을 떠날 수 없음 → 400 OWNER_CANNOT_LEAVE"""
    team_id = team_with_auth["team"]["id"]
    res = client.delete(f"/api/teams/{team_id}/leave", headers=team_with_auth["headers"])
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "OWNER_CANNOT_LEAVE"


def test_regenerate_invite_code_owner(client, team_with_auth):
    """초대코드 재발급 성공 — owner가 재발급 → 200 + 새 코드(기존 코드와 다름)"""
    team_id = team_with_auth["team"]["id"]
    old_code = team_with_auth["team"]["invite_code"]
    res = client.post(f"/api/teams/{team_id}/invite-code", headers=team_with_auth["headers"])
    assert res.status_code == 200
    new_code = res.json()["invite_code"]
    assert new_code != old_code
    import re
    assert re.match(r"^[A-Z]{4}-[0-9]{4}$", new_code)


def test_regenerate_invite_code_member_forbidden(client, team_with_auth):
    """초대코드 재발급 실패 — 일반 멤버 시도 → 403 FORBIDDEN"""
    team_id = team_with_auth["team"]["id"]
    invite_code = team_with_auth["team"]["invite_code"]
    res2 = client.post("/api/auth/signup", json={"email": "member2@example.com", "password": "password123"})
    token2 = res2.json()["token"]
    client.post("/api/teams/join", json={"invite_code": invite_code}, headers={"Authorization": f"Bearer {token2}"})
    res = client.post(f"/api/teams/{team_id}/invite-code", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_regenerate_invite_code_old_code_invalid(client, team_with_auth):
    """초대코드 재발급 후 구 코드 무효화 — 구 코드로 합류 시도 → 404 NOT_FOUND"""
    team_id = team_with_auth["team"]["id"]
    old_code = team_with_auth["team"]["invite_code"]
    client.post(f"/api/teams/{team_id}/invite-code", headers=team_with_auth["headers"])
    res3 = client.post("/api/auth/signup", json={"email": "newmember@example.com", "password": "password123"})
    token3 = res3.json()["token"]
    res = client.post("/api/teams/join", json={"invite_code": old_code}, headers={"Authorization": f"Bearer {token3}"})
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"
