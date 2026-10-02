import pytest
import jwt
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

def test_password_hashing_and_verification():
    """
    Verifies that hash_password creates non-reversible bcrypt hashes,
    and verify_password correctly validates matches.
    """
    plain = "SecurityPassword123"
    hashed = hash_password(plain)
    
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("different-pass", hashed) is False

def test_access_token_generation_and_decode():
    """
    Verifies that issued access tokens contain standard claims.
    """
    email = "user@example.com"
    role = "analyst"
    
    token = create_access_token(email, role)
    claims = decode_token(token)
    
    assert claims["sub"] == email
    assert claims["role"] == role
    assert claims["type"] == "access"
    assert "exp" in claims

def test_refresh_token_generation_and_decode():
    """
    Verifies that issued refresh tokens use the refresh key secret.
    """
    email = "user@example.com"
    
    token = create_refresh_token(email)
    claims = decode_token(token, verify_refresh=True)
    
    assert claims["sub"] == email
    assert claims["type"] == "refresh"

def test_jwt_expired_signature_detection(monkeypatch):
    """
    Verifies that decoding an expired token raises ExpiredSignatureError.
    """
    from app.config import settings
    # Override settings TTL dynamically to simulate immediate expiration
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", -5)
    
    expired_token = create_access_token("user@example.com", "user")
    
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(expired_token)
