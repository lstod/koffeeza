import pytest


@pytest.fixture
def setup_entities(create_bean, create_grinder, create_machine):
    bean = create_bean(brand="Onyx", product="Monarch")
    grinder = create_grinder(
        brand="Niche",
        model="Zero",
        scale_type="STEPLESS",
        step_native=8.0,
        finer_is_lower=True,
        snap=5.0,
        unit_label="°",
    )
    machine = create_machine(brand="Breville", model="Bambino Plus")
    return bean, grinder, machine


def _shot_payload(bean_id, grinder_id, machine_id, **overrides):
    data = {
        "bean_id": bean_id,
        "grinder_id": grinder_id,
        "machine_id": machine_id,
        "grind_setting_native": "20",
        "dose_g": 18.0,
        "yield_g": 36.0,
        "time_s": 28.0,
        "taste": "BALANCED",
    }
    data.update(overrides)
    return data


def test_post_shot_success(client, setup_entities):
    bean, grinder, machine = setup_entities
    payload = _shot_payload(bean.id, grinder.id, machine.id)

    resp = client.post("/shots", json=payload)

    assert resp.status_code == 201
    body = resp.json()
    assert "shot" in body
    assert "direction" in body
    assert "magnitude_normalized" in body
    assert "confidence" in body
    assert "instruction" in body
    assert "rationale" in body
    assert body["shot"]["reason_code"] == "DIALED_IN"
    assert body["direction"] is None
    assert body["magnitude_normalized"] == 0.0
    assert body["confidence"] == "HIGH"


def test_post_shot_invalid_bean(client, setup_entities):
    _, grinder, machine = setup_entities
    payload = _shot_payload(9999, grinder.id, machine.id)

    resp = client.post("/shots", json=payload)
    assert resp.status_code == 404
    assert "Bean" in resp.json()["detail"]


def test_post_shot_invalid_grinder(client, setup_entities):
    bean, _, machine = setup_entities
    payload = _shot_payload(bean.id, 9999, machine.id)

    resp = client.post("/shots", json=payload)
    assert resp.status_code == 404
    assert "Grinder" in resp.json()["detail"]


def test_post_shot_invalid_machine(client, setup_entities):
    bean, grinder, _ = setup_entities
    payload = _shot_payload(bean.id, grinder.id, 9999)

    resp = client.post("/shots", json=payload)
    assert resp.status_code == 404
    assert "Machine" in resp.json()["detail"]


def test_get_shots_empty(client):
    resp = client.get("/shots")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_shots_ordered_desc(client, setup_entities):
    bean, grinder, machine = setup_entities
    client.post("/shots", json=_shot_payload(bean.id, grinder.id, machine.id, time_s=28.0))
    client.post("/shots", json=_shot_payload(bean.id, grinder.id, machine.id, time_s=30.0))

    resp = client.get("/shots")
    assert resp.status_code == 200
    shots = resp.json()
    assert len(shots) == 2
    assert shots[0]["id"] > shots[1]["id"]


def test_get_shots_filter_by_bean(client, setup_entities, create_bean):
    bean1, grinder, machine = setup_entities
    bean2 = create_bean(brand="Counter Culture", product="Apollo")

    client.post("/shots", json=_shot_payload(bean1.id, grinder.id, machine.id))
    client.post("/shots", json=_shot_payload(bean2.id, grinder.id, machine.id))

    resp = client.get(f"/shots?bean_id={bean1.id}")
    assert resp.status_code == 200
    shots = resp.json()
    assert len(shots) == 1
    assert shots[0]["bean_id"] == bean1.id


def test_end_to_end_fast_shot(client, setup_entities):
    """Fast shot (18s) should trigger FLOW_TOO_FAST with FINER direction."""
    bean, grinder, machine = setup_entities
    payload = _shot_payload(
        bean.id,
        grinder.id,
        machine.id,
        time_s=18.0,
        taste="SOUR",
    )

    resp = client.post("/shots", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["shot"]["reason_code"] == "FLOW_TOO_FAST"
    assert body["direction"] == "FINER"
    assert body["magnitude_normalized"] == 2.5
    assert body["confidence"] == "HIGH"
    assert "finer" in body["rationale"].lower()
    assert body["instruction"]  # non-empty instruction text


def test_end_to_end_slow_shot(client, setup_entities):
    """Very slow shot (45s) should trigger FLOW_TOO_SLOW with COARSER direction."""
    bean, grinder, machine = setup_entities
    payload = _shot_payload(
        bean.id,
        grinder.id,
        machine.id,
        time_s=45.0,
        taste="BITTER",
    )

    resp = client.post("/shots", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["shot"]["reason_code"] == "FLOW_TOO_SLOW"
    assert body["direction"] == "COARSER"
    assert body["confidence"] == "HIGH"


def test_end_to_end_taste_sour(client, setup_entities):
    """In-window sour shot should trigger TASTE_SOUR with FINER direction."""
    bean, grinder, machine = setup_entities
    payload = _shot_payload(
        bean.id,
        grinder.id,
        machine.id,
        time_s=28.0,
        taste="SOUR",
    )

    resp = client.post("/shots", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["shot"]["reason_code"] == "TASTE_SOUR"
    assert body["direction"] == "FINER"
    assert "sour" in body["rationale"].lower()
