from fastapi.testclient import TestClient

from app.main import app
from scripts.seed_data import seed

client = TestClient(app)


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_records_pagination_and_validation_errors():
    seed()
    analyst_token = login("analyst@finance.example.com", "Analyst@123")

    response = client.get("/records?skip=0&limit=2", headers={"Authorization": f"Bearer {analyst_token}"})
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert body["limit"] == 2

    invalid_response = client.get("/records?limit=999", headers={"Authorization": f"Bearer {analyst_token}"})
    assert invalid_response.status_code == 422


def test_records_search_and_soft_delete_restore():
    seed()
    admin_token = login("admin@finance.example.com", "Admin@123")
    analyst_token = login("analyst@finance.example.com", "Analyst@123")

    create_response = client.post(
        "/records",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "amount": 77.0,
            "type": "expense",
            "category": "searchable",
            "record_date": "2026-03-20",
            "notes": "invoice keyword zeta",
        },
    )
    assert create_response.status_code == 201
    record_id = create_response.json()["id"]

    search_response = client.get("/records?q=zeta", headers={"Authorization": f"Bearer {analyst_token}"})
    assert search_response.status_code == 200
    assert any(item["id"] == record_id for item in search_response.json()["items"])

    delete_response = client.delete(f"/records/{record_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert delete_response.status_code == 204

    after_delete = client.get("/records?q=zeta", headers={"Authorization": f"Bearer {analyst_token}"})
    assert after_delete.status_code == 200
    assert all(item["id"] != record_id for item in after_delete.json()["items"])

    restore_response = client.post(f"/records/{record_id}/restore", headers={"Authorization": f"Bearer {admin_token}"})
    assert restore_response.status_code == 200

    after_restore = client.get("/records?q=zeta", headers={"Authorization": f"Bearer {analyst_token}"})
    assert after_restore.status_code == 200
    assert any(item["id"] == record_id for item in after_restore.json()["items"])


def test_audit_logs_admin_only():
    seed()
    admin_token = login("admin@finance.example.com", "Admin@123")
    analyst_token = login("analyst@finance.example.com", "Analyst@123")

    create_response = client.post(
        "/records",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "amount": 123.45,
            "type": "expense",
            "category": "qa",
            "record_date": "2026-03-15",
            "notes": "audit test",
        },
    )
    assert create_response.status_code == 201

    admin_audits = client.get("/audits?limit=20", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_audits.status_code == 200
    payload = admin_audits.json()
    assert payload["total"] >= 1
    assert any(item["action"] == "record_created" for item in payload["items"])

    analyst_audits = client.get("/audits", headers={"Authorization": f"Bearer {analyst_token}"})
    assert analyst_audits.status_code == 403


def test_domain_events_outbox_admin_only():
    seed()
    admin_token = login("admin@finance.example.com", "Admin@123")
    analyst_token = login("analyst@finance.example.com", "Analyst@123")

    create_response = client.post(
        "/records",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "amount": 66.0,
            "type": "income",
            "category": "events",
            "record_date": "2026-03-22",
            "notes": "event outbox test",
        },
    )
    assert create_response.status_code == 201

    admin_events = client.get("/events?limit=20", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_events.status_code == 200
    payload = admin_events.json()
    assert payload["total"] >= 1
    assert any(item["event_type"] == "record.created" for item in payload["items"])

    analyst_events = client.get("/events", headers={"Authorization": f"Bearer {analyst_token}"})
    assert analyst_events.status_code == 403
