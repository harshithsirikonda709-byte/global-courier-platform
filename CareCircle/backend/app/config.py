from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./carecircle.db"
    jwt_secret: str = "development-only-change-before-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
