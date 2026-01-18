from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    GEMINI_API_KEY: str
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    GOOGLE_MAPS_API_KEY: str
    GOOGLE_PLACES_API_KEY: str

    # Configuration
    PLAID_ENV: str = "sandbox"
    DATABASE_URL: str = "sqlite+aiosqlite:///./loan_assessment.db"
    CORS_ORIGINS: str = "http://localhost:3000"

    # Security
    ENCRYPTION_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


_settings = None


def get_settings() -> Settings:
    """Get or create the global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Global settings instance - use get_settings() for lazy initialization
# For direct usage, instantiate when imported (will fail if env vars not set)
try:
    settings = Settings()
except Exception:
    # Allow import to succeed even if settings can't be created (e.g., during tests)
    settings = None  # type: ignore
