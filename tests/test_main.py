from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "tasks-api"}


def test_create_and_list_task():
    resp = client.post("/tasks", json={"title": "Test task"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Test task"
    assert body["done"] is False
    task_id = body["id"]

    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert any(t["id"] == task_id for t in resp.json())


def test_get_task():
    created = client.post("/tasks", json={"title": "Fetch me", "priority": "low"}).json()
    resp = client.get(f"/tasks/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Fetch me"
    assert resp.json()["priority"] == "low"


def test_get_task_not_found():
    resp = client.get("/tasks/9999")
    assert resp.status_code == 404


def test_update_task():
    created = client.post("/tasks", json={"title": "Original"}).json()
    resp = client.patch(f"/tasks/{created['id']}", json={"title": "Updated", "done": True})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"
    assert resp.json()["done"] is True


def test_update_task_not_found():
    resp = client.patch("/tasks/9999", json={"title": "x"})
    assert resp.status_code == 404


def test_delete_task():
    created = client.post("/tasks", json={"title": "To delete"}).json()
    resp = client.delete(f"/tasks/{created['id']}")
    assert resp.status_code == 204
    resp = client.get(f"/tasks/{created['id']}")
    assert resp.status_code == 404


def test_delete_task_not_found():
    resp = client.delete("/tasks/9999")
    assert resp.status_code == 404


def test_list_reflects_updates_after_cache_invalidation():
    created = client.post("/tasks", json={"title": "Cache check", "priority": "high"}).json()
    first_list = client.get("/tasks").json()
    assert any(t["id"] == created["id"] and t["priority"] == "high" for t in first_list)

    client.patch(f"/tasks/{created['id']}", json={"title": "Cache check", "priority": "low"})
    second_list = client.get("/tasks").json()
    assert any(t["id"] == created["id"] and t["priority"] == "low" for t in second_list)
