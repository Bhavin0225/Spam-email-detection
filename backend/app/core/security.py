from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.config import settings

def hash_password(password: str) -> str:
    """
    Hashes a clear text password using bcrypt with a random salt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches a stored bcrypt hash.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def create_access_token(subject: str, role: str) -> str:
    """
    Generates a JWT access token containing subject, role, type claims, and 30-minute expiry.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": now
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(subject: str) -> str:
    """
    Generates a JWT refresh token containing subject, type claims, and 7-day expiry.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
        "iat": now
    }
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET_KEY, algorithm="HS256")

def decode_token(token: str, verify_refresh: bool = False) -> dict:
    """
    Decodes and validates a JWT token using HS256 algorithm.
    Throws jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure.
    """
    secret = settings.JWT_REFRESH_SECRET_KEY if verify_refresh else settings.JWT_SECRET_KEY
    return jwt.decode(token, secret, algorithms=["HS256"])
