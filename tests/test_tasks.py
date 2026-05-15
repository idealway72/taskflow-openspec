def test_create_task(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res = client.post(f"/api/teams/{team_id}/tasks", json={"title": "Test Task"}, headers=team_with_auth["headers"])
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "TODO"
    assert data["assignee_id"] is None


def test_create_task_invalid_title(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    res = client.post(f"/api/teams/{team_id}/tasks", json={"title": ""}, headers=team_with_auth["headers"])
    assert res.status_code == 422


def test_list_tasks(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    client.post(f"/api/teams/{team_id}/tasks", json={"title": "Task 1"}, headers=team_with_auth["headers"])
    client.post(f"/api/teams/{team_id}/tasks", json={"title": "Task 2"}, headers=team_with_auth["headers"])
    res = client.get(f"/api/teams/{team_id}/tasks", headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_task(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    created = client.post(f"/api/teams/{team_id}/tasks", json={"title": "Task"}, headers=team_with_auth["headers"]).json()
    res = client.get(f"/api/tasks/{created['id']}", headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_update_task(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    created = client.post(f"/api/teams/{team_id}/tasks", json={"title": "Old Title"}, headers=team_with_auth["headers"]).json()
    res = client.put(f"/api/tasks/{created['id']}", json={"title": "New Title"}, headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert res.json()["title"] == "New Title"


def test_update_task_status(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    created = client.post(f"/api/teams/{team_id}/tasks", json={"title": "Task"}, headers=team_with_auth["headers"]).json()
    res = client.patch(f"/api/tasks/{created['id']}/status", json={"status": "DOING"}, headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert res.json()["status"] == "DOING"


def test_update_task_invalid_status(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    created = client.post(f"/api/teams/{team_id}/tasks", json={"title": "Task"}, headers=team_with_auth["headers"]).json()
    res = client.patch(f"/api/tasks/{created['id']}/status", json={"status": "IN_PROGRESS"}, headers=team_with_auth["headers"])
    assert res.status_code == 422


def test_delete_task_by_creator(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    created = client.post(f"/api/teams/{team_id}/tasks", json={"title": "Task"}, headers=team_with_auth["headers"]).json()
    res = client.delete(f"/api/tasks/{created['id']}", headers=team_with_auth["headers"])
    assert res.status_code == 204


def test_delete_task_forbidden(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    invite_code = team_with_auth["team"]["invite_code"]
    created = client.post(f"/api/teams/{team_id}/tasks", json={"title": "Task"}, headers=team_with_auth["headers"]).json()
    res2 = client.post("/api/auth/signup", json={"email": "member@example.com", "password": "password123"})
    token2 = res2.json()["token"]
    client.post("/api/teams/join", json={"invite_code": invite_code}, headers={"Authorization": f"Bearer {token2}"})
    res = client.delete(f"/api/tasks/{created['id']}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_filter_my_tasks(client, team_with_auth):
    team_id = team_with_auth["team"]["id"]
    user_id = team_with_auth["user"]["user"]["id"]
    client.post(f"/api/teams/{team_id}/tasks", json={"title": "My Task", "assignee_id": user_id}, headers=team_with_auth["headers"])
    client.post(f"/api/teams/{team_id}/tasks", json={"title": "Unassigned"}, headers=team_with_auth["headers"])
    res = client.get(f"/api/teams/{team_id}/tasks?filter=me", headers=team_with_auth["headers"])
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["title"] == "My Task"
