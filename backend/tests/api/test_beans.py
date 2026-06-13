def test_create_bean(client):
    resp = client.post("/beans", json={"brand": "Onyx", "product": "Monarch"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["brand"] == "Onyx"
    assert data["product"] == "Monarch"
    assert data["notes"] is None
    assert "id" in data


def test_create_bean_with_notes(client):
    resp = client.post(
        "/beans", json={"brand": "Onyx", "product": "Monarch", "notes": "Fruity"}
    )
    assert resp.status_code == 201
    assert resp.json()["notes"] == "Fruity"


def test_list_beans_empty(client):
    resp = client.get("/beans")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_beans_after_create(client):
    client.post("/beans", json={"brand": "Onyx", "product": "Monarch"})
    client.post("/beans", json={"brand": "Counter Culture", "product": "Hologram"})
    resp = client.get("/beans")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_create_bean_missing_field(client):
    resp = client.post("/beans", json={"brand": "Onyx"})
    assert resp.status_code == 422
