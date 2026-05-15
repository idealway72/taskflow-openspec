def test_create_team(client, registered_user, auth_headers):
    res = client.post("/api/teams", json={"name": "My Team"}, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "My Team"
    assert len(data["invite_code"]) == 9
    import re
    assert re.match(r"^[A-Z]{4}-[0-9]{4}$", data["invite_code"])


def test_create_team_invalid_name(client, auth_headers):
    res = client.post("/api/teams", json={"name": ""}, headers=auth_headers)
    assert res.status_code == 422


def test_join_team(client, team_with_auth):
    invite_code = team_with_auth["team"]["invite_code"]
    res2 = client.post("/api/auth/signup", json={"email": "member@example.com", "password": "password123"})
    token2 = res2.json()["token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    res = client.post("/api/teams/join", json={"invite_code": invite_code}, headers=headers2)
    assert res.status_code == 200
    assert res.json()["team"]["name"] == "Test Team"


def test_join_team_already_in_team(client, team_with_auth):
    invite_code = team_with_auth["team"]["invite_code"]
    res = client.post("/api/teams/join", json={"invite_code": invite_code}, headers=team_with_auth["headers"])
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "ALREADY_IN_TEAM"


def test_join_team_not_found(client, registered_user, auth_headers):
    res = client.post("/api/teams/join", json={"invite_code": "XXXX-9999"}, headers=auth_headers)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_join_team_invalid_code_format(client, registered_user, auth_headers):
    res = client.post("/api/teams/join", json={"invite_code": "abcd1234"}, headers=auth_headers)
    assert res.status_code == 422


def test_get_team(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res = client.get(f"/api/teams/{team_id}", headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert res.json()["id"] == team_id


def test_get_team_forbidden(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res2 = client.post("/api/auth/signup", json={"email": "other@example.com", "password": "password123"})
    token2 = res2.json()["token"]
    res = client.get(f"/api/teams/{team_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_get_members(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res = client.get(f"/api/teams/{team_id}/members", headers=team_with_auth["headers"])
    assert res.status_code == 200
    members = res.json()
    assert len(members) == 1
    assert members[0]["is_owner"] is True


def test_leave_team_owner_cannot_leave(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res = client.delete(f"/api/teams/{team_id}/leave", headers=team_with_auth["headers"])
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "OWNER_CANNOT_LEAVE"
