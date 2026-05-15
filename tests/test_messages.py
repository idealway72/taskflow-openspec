def test_send_message(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res = client.post(f"/api/teams/{team_id}/messages", json={"content": "Hello!"}, headers=team_with_auth["headers"])
    assert res.status_code == 201
    data = res.json()
    assert data["content"] == "Hello!"
    assert data["user_email"] == "test@example.com"


def test_send_message_too_long(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res = client.post(f"/api/teams/{team_id}/messages", json={"content": "x" * 1001}, headers=team_with_auth["headers"])
    assert res.status_code == 422


def test_send_message_empty(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res = client.post(f"/api/teams/{team_id}/messages", json={"content": ""}, headers=team_with_auth["headers"])
    assert res.status_code == 422


def test_list_messages(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    client.post(f"/api/teams/{team_id}/messages", json={"content": "msg1"}, headers=team_with_auth["headers"])
    client.post(f"/api/teams/{team_id}/messages", json={"content": "msg2"}, headers=team_with_auth["headers"])
    res = client.get(f"/api/teams/{team_id}/messages", headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_messages_since(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    client.post(f"/api/teams/{team_id}/messages", json={"content": "old"}, headers=team_with_auth["headers"])
    msgs = client.get(f"/api/teams/{team_id}/messages", headers=team_with_auth["headers"]).json()
    since = msgs[-1]["created_at"]
    client.post(f"/api/teams/{team_id}/messages", json={"content": "new"}, headers=team_with_auth["headers"])
    res = client.get(f"/api/teams/{team_id}/messages?since={since}", headers=team_with_auth["headers"])
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["content"] == "new"


def test_delete_own_message(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    msg = client.post(f"/api/teams/{team_id}/messages", json={"content": "bye"}, headers=team_with_auth["headers"]).json()
    res = client.delete(f"/api/messages/{msg['id']}", headers=team_with_auth["headers"])
    assert res.status_code == 204


def test_delete_other_message_forbidden(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    invite_code = team_with_auth["team"]["invite_code"]
    msg = client.post(f"/api/teams/{team_id}/messages", json={"content": "owner msg"}, headers=team_with_auth["headers"]).json()
    res2 = client.post("/api/auth/signup", json={"email": "member@example.com", "password": "password123"})
    token2 = res2.json()["token"]
    client.post("/api/teams/join", json={"invite_code": invite_code}, headers={"Authorization": f"Bearer {token2}"})
    res = client.delete(f"/api/messages/{msg['id']}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "NOT_OWNER"
