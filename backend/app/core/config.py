"""Application configuration, loaded from environment variables / .env file."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "Trivium"
    ENVIRONMENT: str = "development"  # development | test | production
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./trivium.db"

    # --- Security / JWT ---
    SECRET_KEY: str = "dev-secret-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # --- CORS (comma-separated origins) ---
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173"

    # --- Rate limiting ---
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_LLM: str = "30/minute"
    RATE_LIMIT_ENABLED: bool = True

    # --- LLM provider abstraction ---
    LLM_PROVIDER: str = "mock"  # mock | openai | groq | anthropic | any litellm-compatible
    LLM_MODEL: str = ""
    LLM_API_KEY: str = ""
    LLM_TIMEOUT_SECONDS: int = 60

    # --- Learning science parameters ---
    # Diffuse-mode: minimum delay before a unit's FIRST review is ever surfaced.
    DIFFUSE_MODE_DELAY_HOURS: int = 12
    # Never schedule two reviews of the same unit closer than this.
    MIN_REVIEW_GAP_HOURS: int = 4
    # Max units per generated review session.
    REVIEW_SESSION_SIZE: int = 10

    # --- Extraction ---
    EXTRACTION_MIN_MESSAGES: int = 2
    FORMAT_RULE_VERSION: str = "v1.0"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
