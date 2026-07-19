"""Application configuration using pydantic-settings."""
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings loaded from environment / .env file."""

    APP_NAME: str = "UniFi AI Operations Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database – supply DATABASE_URL directly OR individual components
    DB_USER: str = "ubiquiti"
    DB_PASSWORD: str = "ubiquiti"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ubiquitiagent"
    # Override the entire URL at once if preferred (e.g. in tests or Docker)
    DATABASE_URL: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_database_url(self) -> str:
        """Return DATABASE_URL if set, otherwise build from components."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

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
