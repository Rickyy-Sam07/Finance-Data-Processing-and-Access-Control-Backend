from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def ensure_test_users() -> None:
    db = SessionLocal()
    try:
        users = db.query(User).count()
        if users == 0:
            from scripts.seed_data import seed

            db.close()
            seed()
    finally:
        if db.is_active:
            db.close()


def test_viewer_cannot_create_record():
    ensure_test_users()
    token = login("viewer@finance.example.com", "Viewer@123")
    response = client.post(
        "/records",
        json={
            "amount": 99.9,
            "type": "expense",
            "category": "misc",
            "record_date": "2026-03-01",
            "notes": "viewer should fail",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_analyst_can_read_dashboard_but_not_users():
    ensure_test_users()
    token = login("analyst@finance.example.com", "Analyst@123")

    dashboard_response = client.get("/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    assert dashboard_response.status_code == 200

    users_response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert users_response.status_code == 403
