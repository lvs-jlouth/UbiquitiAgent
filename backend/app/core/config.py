"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings loaded from environment / .env file."""

    APP_NAME: str = "UniFi AI Operations Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ubiquitiagent"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # UniFi
    UNIFI_HOST: str = ""
    UNIFI_PORT: int = 443
    UNIFI_USERNAME: str = ""
    UNIFI_PASSWORD: str = ""
    UNIFI_SITE: str = "default"
    UNIFI_VERIFY_SSL: bool = False

    # Operating Mode: read_only, approval_required, authorized_change
    OPERATING_MODE: str = "read_only"

    # Scheduler
    TELEMETRY_INTERVAL_SECONDS: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Rate limiting
    AGENT_RATE_LIMIT_PER_MINUTE: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)


settings = Settings()
