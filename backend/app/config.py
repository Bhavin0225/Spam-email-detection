import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # MongoDB Atlas
    MONGODB_URI: str = Field(..., description="MongoDB Atlas connection URI")
    MONGODB_DATABASE: str = Field("phishing_detection_db", description="Target database name")

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(..., description="Secret key for signing access tokens")
    JWT_REFRESH_SECRET_KEY: str = Field(..., description="Secret key for signing refresh tokens")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, description="Access token TTL in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, description="Refresh token TTL in days")

    # ML Configuration
    DECISION_THRESHOLD: float = Field(0.65, description="Minimum probability for suspicious label")
    ACTIVE_MODEL_VERSION: str = Field("v1.0.0", description="Active model version tag")

    # Monitoring
    SENTRY_DSN: str = Field("", description="Sentry project DSN for error monitoring")

    # Google OAuth2 (Gmail API)
    GOOGLE_CLIENT_ID: str = Field("", description="Google OAuth2 client ID for Gmail integration")
    GOOGLE_CLIENT_SECRET: str = Field("", description="Google OAuth2 client secret")
    GOOGLE_REDIRECT_URI: str = Field("http://localhost:3000/inbox/gmail/callback", description="OAuth2 redirect URI")

    # Inbox Scanner
    INBOX_SCAN_LIMIT_MAX: int = Field(200, description="Maximum number of emails to fetch per inbox scan")

    # Server Configuration
    CORS_ORIGINS: Union[str, List[str]] = Field("http://localhost:3000", description="Allowed CORS origins")
    LOG_LEVEL: str = Field("INFO", description="Log level")

    model_config = SettingsConfigDict(
        # Allow reading from a .env file if it exists, but don't fail if it doesn't
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v.strip():
                return []
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

# Instantiate a settings instance.
# To avoid ValidationError when running tests or scripts where environment variables
# are not explicitly set, we will only instantiate settings directly when importing,
# but allow instantiation overrides if necessary.
try:
    settings = Settings()
except Exception:
    # If instantiation fails due to missing required env vars, we check if we are in testing
    if "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("ENV") == "testing":
        # Provide dummy values for testing if they aren't configured
        settings = Settings(
            MONGODB_URI="mongodb://localhost:27017",
            JWT_SECRET_KEY="dummy-jwt-secret-key-minimum-256-bits-long-random-string-pytest",
            JWT_REFRESH_SECRET_KEY="dummy-jwt-refresh-secret-key-minimum-256-bits-long-random-string-pytest"
        )
    else:
        raise
