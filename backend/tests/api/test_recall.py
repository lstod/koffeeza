from app.enums import ReasonCode, Taste
from app.models import Shot


def _post_shot(db, bean, grinder, machine, *, reason_code=ReasonCode.TASTE_SOUR, **overrides):
    defaults = dict(
        user_id=bean.user_id,
        bean_id=bean.id,
        grinder_id=grinder.id,
        machine_id=machine.id,
        grind_setting_native="12",
        dose_g=18.0,
        yield_g=36.0,
        time_s=28.0,
        taste=Taste.BALANCED,
        reason_code=reason_code,
    )
    defaults.update(overrides)
    shot = Shot(**defaults)
    db.add(shot)
    db.commit()
    db.refresh(shot)
    return shot


class TestRecallGeneric:
    def test_no_prior_shots_returns_generic(self, client, create_bean, create_grinder, create_machine):
        bean = create_bean()
        grinder = create_grinder()
        machine = create_machine()

        resp = client.get("/recall", params={
            "bean_id": bean.id,
            "grinder_id": grinder.id,
            "machine_id": machine.id,
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["confidence_label"] == "GENERIC"
        assert data["source_tier"] == 5
        assert data["dose_g"] == 18.0
        assert data["yield_g"] == 36.0
        assert data["time_s"] == 28.0
        assert data["shot_id"] is None
        assert data["grind_setting_native"] is None


class TestRecallExact:
    def test_exact_combo_any_reason_returns_tier2(
        self, client, db, create_bean, create_grinder, create_machine
    ):
        bean = create_bean()
        grinder = create_grinder()
        machine = create_machine()
        shot = _post_shot(
            db, bean, grinder, machine,
            reason_code=ReasonCode.TASTE_SOUR,
            dose_g=19.0, yield_g=40.0, time_s=30.0, grind_setting_native="10",
        )

        resp = client.get("/recall", params={
            "bean_id": bean.id,
            "grinder_id": grinder.id,
            "machine_id": machine.id,
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["confidence_label"] == "EXACT"
        assert data["source_tier"] == 2
        assert data["shot_id"] == shot.id
        assert data["dose_g"] == 19.0
        assert data["yield_g"] == 40.0
        assert data["time_s"] == 30.0
        assert data["grind_setting_native"] == "10"

    def test_dialed_in_returns_tier1(
        self, client, db, create_bean, create_grinder, create_machine
    ):
        bean = create_bean()
        grinder = create_grinder()
        machine = create_machine()

        _post_shot(
            db, bean, grinder, machine,
            reason_code=ReasonCode.TASTE_SOUR,
            dose_g=19.0, yield_g=40.0, time_s=30.0,
        )
        dialed = _post_shot(
            db, bean, grinder, machine,
            reason_code=ReasonCode.DIALED_IN,
            dose_g=18.0, yield_g=36.0, time_s=27.0, grind_setting_native="11",
        )

        resp = client.get("/recall", params={
            "bean_id": bean.id,
            "grinder_id": grinder.id,
            "machine_id": machine.id,
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["confidence_label"] == "EXACT"
        assert data["source_tier"] == 1
        assert data["shot_id"] == dialed.id
        assert data["dose_g"] == 18.0
        assert data["yield_g"] == 36.0

    def test_tier1_preferred_over_tier2(
        self, client, db, create_bean, create_grinder, create_machine
    ):
        """Even if a non-dialed-in shot is more recent, tier 1 wins."""
        bean = create_bean()
        grinder = create_grinder()
        machine = create_machine()

        dialed = _post_shot(
            db, bean, grinder, machine,
            reason_code=ReasonCode.DIALED_IN,
            dose_g=18.0, yield_g=36.0, time_s=27.0,
        )
        _post_shot(
            db, bean, grinder, machine,
            reason_code=ReasonCode.TASTE_BITTER,
            dose_g=18.0, yield_g=38.0, time_s=29.0,
        )

        resp = client.get("/recall", params={
            "bean_id": bean.id,
            "grinder_id": grinder.id,
            "machine_id": machine.id,
        })

        data = resp.json()
        assert data["source_tier"] == 1
        assert data["shot_id"] == dialed.id


class TestRecallFallthrough:
    def test_different_grinder_falls_to_generic(
        self, client, db, create_bean, create_grinder, create_machine
    ):
        bean = create_bean()
        grinder1 = create_grinder(brand="Niche", model="Zero")
        grinder2 = create_grinder(brand="Baratza", model="Encore")
        machine = create_machine()

        _post_shot(db, bean, grinder1, machine, reason_code=ReasonCode.DIALED_IN)

        resp = client.get("/recall", params={
            "bean_id": bean.id,
            "grinder_id": grinder2.id,
            "machine_id": machine.id,
        })

        data = resp.json()
        assert data["confidence_label"] == "GENERIC"
        assert data["source_tier"] == 5

    def test_different_machine_falls_to_generic(
        self, client, db, create_bean, create_grinder, create_machine
    ):
        bean = create_bean()
        grinder = create_grinder()
        machine1 = create_machine(brand="Breville", model="Bambino Plus")
        machine2 = create_machine(brand="La Marzocco", model="Linea Mini")

        _post_shot(db, bean, grinder, machine1, reason_code=ReasonCode.DIALED_IN)

        resp = client.get("/recall", params={
            "bean_id": bean.id,
            "grinder_id": grinder.id,
            "machine_id": machine2.id,
        })

        data = resp.json()
        assert data["confidence_label"] == "GENERIC"
        assert data["source_tier"] == 5

    def test_different_bean_falls_to_generic(
        self, client, db, create_bean, create_grinder, create_machine
    ):
        bean1 = create_bean(brand="Onyx", product="Monarch")
        bean2 = create_bean(brand="Counter Culture", product="Big Trouble")
        grinder = create_grinder()
        machine = create_machine()

        _post_shot(db, bean1, grinder, machine, reason_code=ReasonCode.DIALED_IN)

        resp = client.get("/recall", params={
            "bean_id": bean2.id,
            "grinder_id": grinder.id,
            "machine_id": machine.id,
        })

        data = resp.json()
        assert data["confidence_label"] == "GENERIC"
        assert data["source_tier"] == 5


class TestRecallValidation:
    def test_invalid_bean_id_returns_404(self, client, create_grinder, create_machine):
        grinder = create_grinder()
        machine = create_machine()

        resp = client.get("/recall", params={
            "bean_id": 999,
            "grinder_id": grinder.id,
            "machine_id": machine.id,
        })
        assert resp.status_code == 404

    def test_invalid_grinder_id_returns_404(self, client, create_bean, create_machine):
        bean = create_bean()
        machine = create_machine()

        resp = client.get("/recall", params={
            "bean_id": bean.id,
            "grinder_id": 999,
            "machine_id": machine.id,
        })
        assert resp.status_code == 404

    def test_invalid_machine_id_returns_404(self, client, create_bean, create_grinder):
        bean = create_bean()
        grinder = create_grinder()

        resp = client.get("/recall", params={
            "bean_id": bean.id,
            "grinder_id": grinder.id,
            "machine_id": 999,
        })
        assert resp.status_code == 404
