from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(validation_alias="APP_NAME")
    app_env: str = Field(validation_alias="APP_ENV")
    debug: bool = Field(validation_alias="DEBUG")
    app_description: str = Field(
        default="AI microservice for wardrobe analysis, outfit generation, and image processing.",
        validation_alias="APP_DESCRIPTION",
    )
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    docs_url: str | None = Field(default="/docs", validation_alias="DOCS_URL")
    redoc_url: str | None = Field(default="/redoc", validation_alias="REDOC_URL")
    openapi_url: str | None = Field(default="/openapi.json", validation_alias="OPENAPI_URL")

    cors_allowed_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        validation_alias="CORS_ALLOWED_ORIGINS",
    )
    cors_allow_credentials: bool = Field(default=True, validation_alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list[str] = Field(default=["*"], validation_alias="CORS_ALLOW_METHODS")
    cors_allow_headers: list[str] = Field(default=["*"], validation_alias="CORS_ALLOW_HEADERS")

    rate_limit_enabled: bool = Field(default=True, validation_alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, validation_alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, validation_alias="RATE_LIMIT_WINDOW_SECONDS")

    internal_api_key: str = Field(validation_alias="INTERNAL_API_KEY")

    database_url: str = Field(validation_alias="DATABASE_URL")
    redis_url: str = Field(validation_alias="REDIS_URL")

    storage_provider: str = Field(validation_alias="STORAGE_PROVIDER")
    s3_endpoint: str = Field(validation_alias="S3_ENDPOINT")
    s3_access_key: str = Field(validation_alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(validation_alias="S3_SECRET_KEY")
    s3_bucket: str = Field(validation_alias="S3_BUCKET")
    s3_region: str = Field(validation_alias="S3_REGION")
    s3_use_ssl: bool = Field(validation_alias="S3_USE_SSL")
    s3_path_style: bool = Field(validation_alias="S3_PATH_STYLE")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Priority high -> low. Real OS/container env vars must win over a local
        # committed-by-mistake `.env`, so env_settings comes before dotenv_settings.
        return init_settings, env_settings, dotenv_settings, file_secret_settings


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
