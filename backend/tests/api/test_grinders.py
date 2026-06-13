GRINDER_PAYLOAD = {
    "brand": "Eureka",
    "model": "Mignon Specialita",
    "scale_type": "STEPLESS",
    "step_native": 0.1,
    "finer_is_lower": True,
    "snap": 0.1,
    "unit_label": "numbers",
}


def test_create_grinder(client):
    resp = client.post("/grinders", json=GRINDER_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["brand"] == "Eureka"
    assert data["model"] == "Mignon Specialita"
    assert data["scale_type"] == "STEPLESS"
    assert data["step_native"] == 0.1
    assert data["finer_is_lower"] is True
    assert data["snap"] == 0.1
    assert data["unit_label"] == "numbers"
    assert data["label"] is None
    assert data["min_native"] is None
    assert data["max_native"] is None
    assert "id" in data


def test_create_grinder_with_optional_fields(client):
    payload = {
        **GRINDER_PAYLOAD,
        "label": "My Grinder",
        "min_native": 0.0,
        "max_native": 10.0,
    }
    resp = client.post("/grinders", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["label"] == "My Grinder"
    assert data["min_native"] == 0.0
    assert data["max_native"] == 10.0


def test_list_grinders_empty(client):
    resp = client.get("/grinders")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_grinders_after_create(client):
    client.post("/grinders", json=GRINDER_PAYLOAD)
    resp = client.get("/grinders")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["scale_type"] == "STEPLESS"


def test_create_grinder_invalid_scale_type(client):
    payload = {**GRINDER_PAYLOAD, "scale_type": "INVALID"}
    resp = client.post("/grinders", json=payload)
    assert resp.status_code == 422
