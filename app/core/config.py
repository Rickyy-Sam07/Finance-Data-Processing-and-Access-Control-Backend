from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Finance Data Processing API"
    environment: str = "development"
    app_port: int = 8001
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'finance.db').as_posix()}"
    auto_run_migrations: bool = True
    auth_rate_limit_requests: int = 20
    auth_rate_limit_window_seconds: int = 60
    enable_event_driven_pipeline: bool = True
    kafka_bootstrap_servers: str = ""
    kafka_topic: str = "finance.domain.events"
    jwt_secret_key: str = "replace-with-a-long-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    refresh_token_expire_minutes: int = 10080

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
