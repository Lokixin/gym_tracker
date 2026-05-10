import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://admin:admin@postgres/workouts"
    )
    strengthlog_cookie: str | None = os.getenv("STRENGTHLOG_COOKIE")

    @property
    def psycopg_url(self) -> str:
        return self.database_url.replace("postgresql+psycopg://", "postgresql://")


settings = Settings()
