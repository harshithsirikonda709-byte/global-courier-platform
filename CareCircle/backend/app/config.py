import json
from functools import lru_cache
from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./carecircle.db"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""
    supabase_jwt_algorithm: Literal["ES256", "RS256", "HS256", "AUTO"] = "ES256"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]
    admin_user_ids: list[str] = []
    environment: str = "development"

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        return value

    @field_validator("admin_user_ids", mode="before")
    @classmethod
    def assemble_admin_user_ids(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return [str(user_id).strip() for user_id in parsed if str(user_id).strip()]
                except json.JSONDecodeError:
                    pass
            return [user_id.strip() for user_id in stripped.split(",") if user_id.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(user_id).strip() for user_id in value if str(user_id).strip()]
        return value

    @field_validator("supabase_jwt_algorithm", mode="before")
    @classmethod
    def normalize_algorithm(cls, value: Any) -> str:
        if isinstance(value, str):
            upper = value.strip().upper()
            if upper in ("ES256", "RS256", "HS256", "AUTO"):
                return upper
        return value

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
