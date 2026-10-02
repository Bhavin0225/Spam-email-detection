from app.config import Settings

def test_settings_load_defaults(monkeypatch):
    """
    Verifies that default settings values are correctly populated when optional env variables are omitted.
    """
    monkeypatch.delenv("MONGODB_DATABASE", raising=False)
    settings = Settings(
        MONGODB_URI="mongodb://test-uri:27017",
        JWT_SECRET_KEY="test-secret-key-with-enough-bits-minimum-256-bits-long",
        JWT_REFRESH_SECRET_KEY="test-refresh-secret-key-with-enough-bits-minimum-256-bits-long",
        _env_file=None
    )
    assert settings.MONGODB_DATABASE == "phishing_detection_db"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert settings.DECISION_THRESHOLD == 0.65
    assert settings.ACTIVE_MODEL_VERSION == "v1.0.0"
    assert settings.LOG_LEVEL == "INFO"

def test_settings_custom_values_and_parsing():
    """
    Verifies custom settings input and CORS string list parsing.
    """
    settings = Settings(
        MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net",
        MONGODB_DATABASE="custom_phishing_db",
        JWT_SECRET_KEY="custom-jwt-key-minimum-256-bits-long-value",
        JWT_REFRESH_SECRET_KEY="custom-refresh-key-minimum-256-bits-long-value",
        ACCESS_TOKEN_EXPIRE_MINUTES=45,
        REFRESH_TOKEN_EXPIRE_DAYS=14,
        DECISION_THRESHOLD=0.75,
        ACTIVE_MODEL_VERSION="v2.0.0",
        CORS_ORIGINS="http://localhost:3000, https://spamapp.io",
        LOG_LEVEL="DEBUG",
        _env_file=None
    )
    assert settings.MONGODB_DATABASE == "custom_phishing_db"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 45
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 14
    assert settings.DECISION_THRESHOLD == 0.75
    assert settings.ACTIVE_MODEL_VERSION == "v2.0.0"
    assert settings.CORS_ORIGINS == ["http://localhost:3000", "https://spamapp.io"]
    assert settings.LOG_LEVEL == "DEBUG"
