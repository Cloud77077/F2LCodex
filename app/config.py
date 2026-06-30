from functools import lru_cache
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "F2LCodex"
    public_base_url: str = "http://localhost:8000"
    bot_token: str = ""
    bot_api_base_url: str | None = None
    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    storage_backend: str = "local"
    local_storage_path: str = "./data/files"
    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_bucket: str | None = None
    s3_region: str = "us-east-1"
    secret_key: str = Field(default="change-me-in-production")
    token_bytes: int = 32
    default_link_ttl_hours: int = 0
    max_file_size_bytes: int = 0
    use_x_accel_redirect: bool = False
    x_accel_prefix: str = "/protected/"
    webhook_path: str = "/telegram/webhook"
    admin_token: str | None = None

    @computed_field
    @property
    def webhook_url(self) -> str:
        return self.public_base_url.rstrip("/") + self.webhook_path

@lru_cache
def get_settings() -> Settings:
    return Settings()
