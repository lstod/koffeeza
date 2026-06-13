from app.enums import Taste


class TestGetPreferences:
    def test_get_default_returns_nulls(self, client):
        resp = client.get("/preferences")
        assert resp.status_code == 200
        data = resp.json()
        assert data["grinder_id"] is None
        assert data["machine_id"] is None

    def test_get_is_idempotent(self, client):
        client.get("/preferences")
        resp = client.get("/preferences")
        assert resp.status_code == 200


class TestPutPreferences:
    def test_put_then_get(self, client, create_grinder, create_machine):
        grinder = create_grinder()
        machine = create_machine()

        resp = client.put("/preferences", json={
            "grinder_id": grinder.id,
            "machine_id": machine.id,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["grinder_id"] == grinder.id
        assert data["machine_id"] == machine.id

        resp = client.get("/preferences")
        data = resp.json()
        assert data["grinder_id"] == grinder.id
        assert data["machine_id"] == machine.id

    def test_partial_update_preserves_other_field(self, client, create_grinder, create_machine):
        grinder = create_grinder()
        machine = create_machine()

        client.put("/preferences", json={
            "grinder_id": grinder.id,
            "machine_id": machine.id,
        })

        grinder2 = create_grinder(brand="Niche", model="Zero")
        client.put("/preferences", json={"grinder_id": grinder2.id})

        data = client.get("/preferences").json()
        assert data["grinder_id"] == grinder2.id
        assert data["machine_id"] == machine.id


class TestShotAutoUpdatesPreferences:
    def test_post_shot_updates_preferences(
        self, client, create_bean, create_grinder, create_machine
    ):
        bean = create_bean()
        grinder = create_grinder()
        machine = create_machine()

        resp = client.post("/shots", json={
            "bean_id": bean.id,
            "grinder_id": grinder.id,
            "machine_id": machine.id,
            "grind_setting_native": "12",
            "dose_g": 18.0,
            "yield_g": 36.0,
            "time_s": 28.0,
            "taste": Taste.BALANCED,
        })
        assert resp.status_code == 201

        pref = client.get("/preferences").json()
        assert pref["grinder_id"] == grinder.id
        assert pref["machine_id"] == machine.id

    def test_post_shot_overwrites_previous_preferences(
        self, client, create_bean, create_grinder, create_machine
    ):
        bean = create_bean()
        grinder1 = create_grinder(brand="Niche", model="Zero")
        grinder2 = create_grinder(brand="Baratza", model="Encore")
        machine = create_machine()

        client.post("/shots", json={
            "bean_id": bean.id,
            "grinder_id": grinder1.id,
            "machine_id": machine.id,
            "grind_setting_native": "12",
            "dose_g": 18.0,
            "yield_g": 36.0,
            "time_s": 28.0,
            "taste": Taste.BALANCED,
        })

        client.post("/shots", json={
            "bean_id": bean.id,
            "grinder_id": grinder2.id,
            "machine_id": machine.id,
            "grind_setting_native": "15",
            "dose_g": 18.0,
            "yield_g": 36.0,
            "time_s": 25.0,
            "taste": Taste.SOUR,
        })

        pref = client.get("/preferences").json()
        assert pref["grinder_id"] == grinder2.id
        assert pref["machine_id"] == machine.id
