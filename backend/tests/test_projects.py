"""Project CRUD + cross-user isolation."""
API = "/api/v1"


def test_project_crud(client, user):
    created = client.post(f"{API}/projects", json={"name": "My SaaS"}, headers=user["headers"])
    assert created.status_code == 201
    pid = created.json()["id"]

    listed = client.get(f"{API}/projects", headers=user["headers"])
    assert any(p["id"] == pid for p in listed.json())

    got = client.get(f"{API}/projects/{pid}", headers=user["headers"])
    assert got.status_code == 200 and got.json()["name"] == "My SaaS"

    renamed = client.patch(f"{API}/projects/{pid}", json={"name": "My SaaS v2"}, headers=user["headers"])
    assert renamed.status_code == 200 and renamed.json()["name"] == "My SaaS v2"

    deleted = client.delete(f"{API}/projects/{pid}", headers=user["headers"])
    assert deleted.status_code == 204
    assert client.get(f"{API}/projects/{pid}", headers=user["headers"]).status_code == 404
    assert all(p["id"] != pid for p in client.get(f"{API}/projects", headers=user["headers"]).json())


def test_cross_user_isolation_returns_404(client, user, other_user):
    pid = client.post(f"{API}/projects", json={"name": "Private"}, headers=user["headers"]).json()["id"]
    # Another user must get 404 (not 403 — existence must not leak) on every verb.
    assert client.get(f"{API}/projects/{pid}", headers=other_user["headers"]).status_code == 404
    assert client.patch(f"{API}/projects/{pid}", json={"name": "Hacked"}, headers=other_user["headers"]).status_code == 404
    assert client.delete(f"{API}/projects/{pid}", headers=other_user["headers"]).status_code == 404
    # And the owner's data is untouched.
    assert client.get(f"{API}/projects/{pid}", headers=user["headers"]).json()["name"] == "Private"


def test_validation_and_injection_safety(client, user):
    assert client.post(f"{API}/projects", json={"name": ""}, headers=user["headers"]).status_code == 422
    assert client.post(f"{API}/projects", json={"name": "x" * 300}, headers=user["headers"]).status_code == 422
    # SQL-injection-shaped input is stored as inert text.
    inj = "'; DROP TABLE projects; --"
    created = client.post(f"{API}/projects", json={"name": inj}, headers=user["headers"])
    assert created.status_code == 201
    assert client.get(f"{API}/projects/{created.json()['id']}", headers=user["headers"]).json()["name"] == inj
