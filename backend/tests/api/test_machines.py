def test_create_machine(client):
    resp = client.post("/machines", json={"brand": "Breville", "model": "Bambino Plus"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["brand"] == "Breville"
    assert data["model"] == "Bambino Plus"
    assert data["label"] is None
    assert data["notes"] is None
    assert "id" in data


def test_create_machine_with_optional_fields(client):
    resp = client.post(
        "/machines",
        json={
            "brand": "La Marzocco",
            "model": "Linea Mini",
            "label": "Office",
            "notes": "Plumbed in",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["label"] == "Office"
    assert data["notes"] == "Plumbed in"


def test_list_machines_empty(client):
    resp = client.get("/machines")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_machines_after_create(client):
    client.post("/machines", json={"brand": "Breville", "model": "Bambino Plus"})
    resp = client.get("/machines")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_create_machine_missing_field(client):
    resp = client.post("/machines", json={"brand": "Breville"})
    assert resp.status_code == 422
