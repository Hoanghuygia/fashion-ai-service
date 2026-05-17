from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Style Engine AI"
    app_env: str = "local"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+psycopg://style_engine:style_engine@localhost:5432/style_engine"
    )
    redis_url: str = "redis://localhost:6379/0"

    storage_provider: str = "s3"
    s3_endpoint: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket: str = "style-engine"
    s3_region: str = "us-east-1"
    s3_use_ssl: bool = False
    s3_path_style: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
