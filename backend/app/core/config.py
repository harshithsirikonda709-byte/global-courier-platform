import json
from functools import lru_cache
from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""
    supabase_jwt_algorithm: Literal["ES256", "RS256", "HS256", "AUTO"] = "ES256"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]
    environment: str = "development"

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed if str(origin).strip()]
                except Exception:
                    pass
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        if isinstance(v, (list, tuple, set)):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return v

    @field_validator("supabase_jwt_algorithm", mode="before")
    @classmethod
    def normalize_algorithm(cls, v: Any) -> str:
        if isinstance(v, str):
            upper = v.strip().upper()
            if upper in ("ES256", "RS256", "HS256", "AUTO"):
                return upper
        return v

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
