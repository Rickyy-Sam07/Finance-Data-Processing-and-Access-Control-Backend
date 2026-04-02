from datetime import date, timedelta
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.database import SessionLocal
from app.db_migrations import run_migrations
from app.core.security import get_password_hash
from app.models.financial_record import FinancialRecord
from app.models.user import User


def seed() -> None:
    run_migrations()
    db = SessionLocal()
    try:
        seeded_users = [
            ("admin@finance.example.com", "System Admin", "Admin@123", "admin"),
            ("analyst@finance.example.com", "Data Analyst", "Analyst@123", "analyst"),
            ("viewer@finance.example.com", "Read-Only Viewer", "Viewer@123", "viewer"),
        ]

        resolved_admin: User | None = None
        for email, full_name, password, role in seeded_users:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    full_name=full_name,
                    password_hash=get_password_hash(password),
                    role=role,
                    is_active=True,
                )
                db.add(user)
            else:
                user.full_name = full_name
                user.password_hash = get_password_hash(password)
                user.role = role
                user.is_active = True
                db.add(user)

            if role == "admin":
                resolved_admin = user

        db.commit()
        if not resolved_admin:
            raise RuntimeError("Admin user could not be initialized")
        db.refresh(resolved_admin)

        today = date.today()
        sample_records = [
            FinancialRecord(amount=5500, type="income", category="salary", record_date=today - timedelta(days=28), notes="monthly salary", created_by=resolved_admin.id),
            FinancialRecord(amount=1200, type="income", category="freelance", record_date=today - timedelta(days=18), notes="api consulting", created_by=resolved_admin.id),
            FinancialRecord(amount=800, type="expense", category="rent", record_date=today - timedelta(days=25), notes="office rent", created_by=resolved_admin.id),
            FinancialRecord(amount=220, type="expense", category="utilities", record_date=today - timedelta(days=11), notes="internet + electricity", created_by=resolved_admin.id),
            FinancialRecord(amount=340, type="expense", category="tools", record_date=today - timedelta(days=5), notes="cloud tools", created_by=resolved_admin.id),
        ]
        if db.query(FinancialRecord).count() == 0:
            db.add_all(sample_records)
            db.commit()
        print("Seed complete")
        print("Admin: admin@finance.example.com / Admin@123")
        print("Analyst: analyst@finance.example.com / Analyst@123")
        print("Viewer: viewer@finance.example.com / Viewer@123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
