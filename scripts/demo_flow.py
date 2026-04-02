import httpx

BASE_URL = "http://127.0.0.1:8001"


def login(email: str, password: str) -> str:
    response = httpx.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password}, timeout=10)
    response.raise_for_status()
    return response.json()["access_token"]


def main() -> None:
    admin_token = login("admin@finance.example.com", "Admin@123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    summary = httpx.get(f"{BASE_URL}/dashboard/summary", headers=headers, timeout=10)
    summary.raise_for_status()
    print("Summary:", summary.json())

    records = httpx.get(f"{BASE_URL}/records?limit=3", headers=headers, timeout=10)
    records.raise_for_status()
    print("Top records:", records.json())

    audits = httpx.get(f"{BASE_URL}/audits?limit=5", headers=headers, timeout=10)
    audits.raise_for_status()
    print("Recent audits:", audits.json())


if __name__ == "__main__":
    main()
