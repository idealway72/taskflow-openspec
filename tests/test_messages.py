def test_send_message(client, team_with_auth):
    """메시지 전송 성공 — 내용 전송 → 201 + user_email 포함"""
    team_id = team_with_auth["team"]["id"]
    res = client.post(f"/api/teams/{team_id}/messages", json={"content": "Hello!"}, headers=team_with_auth["headers"])
    assert res.status_code == 201
    data = res.json()
    assert data["content"] == "Hello!"
    assert data["user_email"] == "test@example.com"


def test_send_message_too_long(client, team_with_auth):
    """메시지 전송 실패 — 1000자 초과 → 422 VALIDATION_ERROR"""
    team_id = team_with_auth["team"]["id"]
    res = client.post(f"/api/teams/{team_id}/messages", json={"content": "x" * 1001}, headers=team_with_auth["headers"])
    assert res.status_code == 422


def test_send_message_empty(client, team_with_auth):
    """메시지 전송 실패 — 빈 내용 → 422 VALIDATION_ERROR"""
    team_id = team_with_auth["team"]["id"]
    res = client.post(f"/api/teams/{team_id}/messages", json={"content": ""}, headers=team_with_auth["headers"])
    assert res.status_code == 422


def test_list_messages(client, team_with_auth):
    """메시지 목록 조회 — 2건 전송 후 조회 → 2건 반환"""
    team_id = team_with_auth["team"]["id"]
    client.post(f"/api/teams/{team_id}/messages", json={"content": "msg1"}, headers=team_with_auth["headers"])
    client.post(f"/api/teams/{team_id}/messages", json={"content": "msg2"}, headers=team_with_auth["headers"])
    res = client.get(f"/api/teams/{team_id}/messages", headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_messages_since(client, team_with_auth):
    """메시지 증분 조회(since=) — 기준 시각 이후 메시지만 반환"""
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
    """메시지 삭제 성공 — 본인 메시지 삭제 → 204"""
    team_id = team_with_auth["team"]["id"]
    msg = client.post(f"/api/teams/{team_id}/messages", json={"content": "bye"}, headers=team_with_auth["headers"]).json()
    res = client.delete(f"/api/messages/{msg['id']}", headers=team_with_auth["headers"])
    assert res.status_code == 204


def test_delete_other_message_forbidden(client, team_with_auth):
    """메시지 삭제 실패 — 타인 메시지 삭제 시도(owner 포함) → 403 NOT_OWNER"""
    team_id = team_with_auth["team"]["id"]
    invite_code = team_with_auth["team"]["invite_code"]
    msg = client.post(f"/api/teams/{team_id}/messages", json={"content": "owner msg"}, headers=team_with_auth["headers"]).json()
    res2 = client.post("/api/auth/signup", json={"email": "member@example.com", "password": "password123"})
    token2 = res2.json()["token"]
    client.post("/api/teams/join", json={"invite_code": invite_code}, headers={"Authorization": f"Bearer {token2}"})
    res = client.delete(f"/api/messages/{msg['id']}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "NOT_OWNER"
