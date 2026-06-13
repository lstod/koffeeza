import pytest
from fastapi.testclient import TestClient

from app.auth import create_token, get_current_user
from app.database import get_db
from app.main import app
from app.models.user import User


class TestUserCRUD:
    def test_create_user_no_pin(self, raw_client):
        resp = raw_client.post("/users", json={"name": "Alice"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["user"]["name"] == "Alice"
        assert data["user"]["has_pin"] is False
        assert "token" in data

    def test_create_user_with_pin(self, raw_client):
        resp = raw_client.post("/users", json={"name": "Bob", "pin": "1234"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["user"]["has_pin"] is True

    def test_create_duplicate_name(self, raw_client):
        raw_client.post("/users", json={"name": "Alice"})
        resp = raw_client.post("/users", json={"name": "Alice"})
        assert resp.status_code == 409

    def test_list_users(self, raw_client):
        raw_client.post("/users", json={"name": "Alice"})
        raw_client.post("/users", json={"name": "Bob"})
        resp = raw_client.get("/users")
        assert resp.status_code == 200
        names = [u["name"] for u in resp.json()]
        assert "Alice" in names
        assert "Bob" in names

    def test_list_users_does_not_expose_pin(self, raw_client):
        raw_client.post("/users", json={"name": "Alice", "pin": "9999"})
        resp = raw_client.get("/users")
        user = resp.json()[0]
        assert "pin_hash" not in user
        assert "pin" not in user
        assert user["has_pin"] is True


class TestLogin:
    def test_login_no_pin_user(self, raw_client):
        create_resp = raw_client.post("/users", json={"name": "Alice"})
        user_id = create_resp.json()["user"]["id"]

        resp = raw_client.post(f"/users/{user_id}/login", json={})
        assert resp.status_code == 200
        assert resp.json()["user"]["name"] == "Alice"
        assert "token" in resp.json()

    def test_login_with_correct_pin(self, raw_client):
        create_resp = raw_client.post("/users", json={"name": "Bob", "pin": "5678"})
        user_id = create_resp.json()["user"]["id"]

        resp = raw_client.post(f"/users/{user_id}/login", json={"pin": "5678"})
        assert resp.status_code == 200

    def test_login_with_wrong_pin(self, raw_client):
        create_resp = raw_client.post("/users", json={"name": "Bob", "pin": "5678"})
        user_id = create_resp.json()["user"]["id"]

        resp = raw_client.post(f"/users/{user_id}/login", json={"pin": "0000"})
        assert resp.status_code == 401

    def test_login_missing_pin_for_pin_user(self, raw_client):
        create_resp = raw_client.post("/users", json={"name": "Bob", "pin": "5678"})
        user_id = create_resp.json()["user"]["id"]

        resp = raw_client.post(f"/users/{user_id}/login", json={})
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, raw_client):
        resp = raw_client.post("/users/9999/login", json={})
        assert resp.status_code == 404


class TestAuthRequired:
    def test_beans_requires_auth(self, raw_client):
        resp = raw_client.get("/beans")
        assert resp.status_code in (401, 403)

    def test_shots_requires_auth(self, raw_client):
        resp = raw_client.get("/shots")
        assert resp.status_code in (401, 403)

    def test_preferences_requires_auth(self, raw_client):
        resp = raw_client.get("/preferences")
        assert resp.status_code in (401, 403)

    def test_valid_token_grants_access(self, raw_client, db):
        user = User(name="TokenUser")
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_token(user.id)
        resp = raw_client.get("/beans", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200


class TestDataIsolation:
    @pytest.fixture
    def two_user_clients(self, db):
        user_a = User(name="Alice")
        user_b = User(name="Bob")
        db.add(user_a)
        db.add(user_b)
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)

        def _override_get_db():
            try:
                yield db
            finally:
                pass

        def _override_user_a():
            return user_a

        def _override_user_b():
            return user_b

        app.dependency_overrides[get_db] = _override_get_db

        app.dependency_overrides[get_current_user] = _override_user_a
        client_a = TestClient(app)

        app.dependency_overrides[get_current_user] = _override_user_b
        client_b = TestClient(app)

        yield client_a, client_b, user_a, user_b, _override_user_a, _override_user_b

        app.dependency_overrides.clear()

    def test_beans_are_isolated(self, two_user_clients):
        client_a, client_b, _, _, set_a, set_b = two_user_clients

        app.dependency_overrides[get_current_user] = set_a
        client_a.post("/beans", json={"brand": "Onyx", "product": "Monarch"})

        app.dependency_overrides[get_current_user] = set_b
        client_b.post("/beans", json={"brand": "Counter Culture", "product": "Hologram"})

        app.dependency_overrides[get_current_user] = set_a
        alice_beans = client_a.get("/beans").json()
        assert len(alice_beans) == 1
        assert alice_beans[0]["brand"] == "Onyx"

        app.dependency_overrides[get_current_user] = set_b
        bob_beans = client_b.get("/beans").json()
        assert len(bob_beans) == 1
        assert bob_beans[0]["brand"] == "Counter Culture"

    def test_shots_are_isolated(self, two_user_clients):
        client_a, client_b, _, _, set_a, set_b = two_user_clients

        app.dependency_overrides[get_current_user] = set_a
        client_a.post("/beans", json={"brand": "Onyx", "product": "Monarch"})
        client_a.post("/grinders", json={
            "brand": "Niche", "model": "Zero", "scale_type": "STEPLESS",
            "step_native": 1.0, "finer_is_lower": True, "snap": 0.5, "unit_label": "num",
        })
        client_a.post("/machines", json={"brand": "Breville", "model": "Bambino"})

        beans_a = client_a.get("/beans").json()
        grinders_a = client_a.get("/grinders").json()
        machines_a = client_a.get("/machines").json()

        client_a.post("/shots", json={
            "bean_id": beans_a[0]["id"],
            "grinder_id": grinders_a[0]["id"],
            "machine_id": machines_a[0]["id"],
            "grind_setting_native": "20",
            "dose_g": 18.0, "yield_g": 36.0, "time_s": 28.0,
            "taste": "BALANCED",
        })

        app.dependency_overrides[get_current_user] = set_b
        bob_shots = client_b.get("/shots").json()
        assert len(bob_shots) == 0
