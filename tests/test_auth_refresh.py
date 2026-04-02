from fastapi.testclient import TestClient

from app.main import app
from scripts.seed_data import seed

client = TestClient(app)


def test_refresh_token_flow():
    seed()

    login_response = client.post(
        "/auth/login",
        json={"email": "admin@finance.example.com", "password": "Admin@123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    refresh_response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert "access_token" in refreshed
    assert "refresh_token" in refreshed


def test_access_token_rejected_for_refresh_endpoint():
    seed()
    login_response = client.post(
        "/auth/login",
        json={"email": "admin@finance.example.com", "password": "Admin@123"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    response = client.post("/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401
