from fastapi.testclient import TestClient

from app.core.rate_limit import reset_rate_limits
from app.main import app

client = TestClient(app)


def test_login_rate_limit_for_invalid_attempts():
    reset_rate_limits()
    last_status = None
    for _ in range(60):
        response = client.post(
            "/auth/login",
            json={"email": "invalid@finance.example.com", "password": "wrongpassword"},
        )
        last_status = response.status_code
        if last_status == 429:
            break

    assert last_status == 429
    reset_rate_limits()
