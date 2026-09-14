from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://safraos:safraos_local_dev@localhost:5473/safraos"
    redis_url: str = "redis://localhost:6383/0"
