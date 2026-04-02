from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy import text

from app.core.database import engine


LEGACY_BASELINE_REVISION = "20260401_0001"


def run_migrations() -> None:
    project_root = Path(__file__).resolve().parents[1]
    alembic_ini = project_root / "alembic.ini"
    if not alembic_ini.exists():
        return

    cfg = Config(str(alembic_ini))
    cfg.set_main_option("script_location", str(project_root / "alembic"))

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    has_business_tables = bool({"users", "financial_records", "audit_logs"}.intersection(table_names))
    has_alembic_version = "alembic_version" in table_names

    empty_alembic_version = False
    if has_alembic_version:
        with engine.connect() as conn:
            version_row = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).fetchone()
            empty_alembic_version = version_row is None

    if has_business_tables and (not has_alembic_version or empty_alembic_version):
        command.stamp(cfg, LEGACY_BASELINE_REVISION)

    command.upgrade(cfg, "head")
