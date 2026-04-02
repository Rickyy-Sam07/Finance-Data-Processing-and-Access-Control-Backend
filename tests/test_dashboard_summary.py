from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def login(email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def ensure_seed() -> None:
    from scripts.seed_data import seed

    seed()


def test_summary_has_expected_fields():
    ensure_seed()
    token = login("analyst@finance.example.com", "Analyst@123")
    response = client.get("/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert "total_income" in body
    assert "total_expenses" in body
    assert "net_balance" in body
    assert "category_totals" in body
    assert "monthly_trends" in body
