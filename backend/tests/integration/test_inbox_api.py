import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from app.database.collections import get_collection
from app.core.security import create_access_token
from app.database.crud import create_user
from app.core.security import hash_password


def test_inbox_api_unauthorized(client: TestClient):
    # Without Authorization header, endpoints should return 401
    response = client.get("/inbox/gmail/auth-url")
    assert response.status_code == 401


@patch("app.services.email_providers.gmail_connector.get_auth_url")
def test_get_gmail_auth_url(mock_get_url, client: TestClient, require_db):
    user_email = "inbox_user@example.com"
    get_collection("users").delete_many({"email": user_email})
    create_user(email=user_email, password_hash=hash_password("Pass123!"), role="user")
    
    token = create_access_token(user_email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_get_url.return_value = "https://mock-google-auth-url"
    
    response = client.get("/inbox/gmail/auth-url?redirect_uri=http://localhost:3000", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"auth_url": "https://mock-google-auth-url"}
    mock_get_url.assert_called_once_with("http://localhost:3000")


@patch("app.services.email_providers.gmail_connector.exchange_code")
@patch("app.services.inbox_scan_service.inbox_scan_service.save_gmail_tokens")
def test_gmail_callback(mock_save, mock_exchange, client: TestClient, require_db):
    user_email = "inbox_user@example.com"
    token = create_access_token(user_email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_exchange.return_value = {"access_token": "acc", "refresh_token": "ref", "expires_in": 3600}
    mock_save.return_value = "user@gmail.com"
    
    response = client.post(
        "/inbox/gmail/callback",
        json={"code": "auth_code_123", "redirect_uri": "http://localhost:3000"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success", "email": "user@gmail.com"}


@patch("app.services.inbox_scan_service.inbox_scan_service.get_gmail_status")
def test_gmail_status(mock_status, client: TestClient, require_db):
    user_email = "inbox_user@example.com"
    token = create_access_token(user_email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_status.return_value = {
        "connected": True,
        "email": "user@gmail.com",
        "connected_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.get("/inbox/gmail/status", headers=headers)
    assert response.status_code == 200
    assert response.json()["connected"] is True
    assert response.json()["email"] == "user@gmail.com"


@patch("app.services.inbox_scan_service.inbox_scan_service.disconnect_gmail")
def test_gmail_disconnect(mock_disconnect, client: TestClient, require_db):
    user_email = "inbox_user@example.com"
    token = create_access_token(user_email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_disconnect.return_value = True
    
    response = client.delete("/inbox/gmail/disconnect", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Gmail disconnected successfully."}


@patch("app.services.inbox_scan_service.inbox_scan_service.start_gmail_scan")
def test_gmail_scan(mock_scan, client: TestClient, require_db):
    user_email = "inbox_user@example.com"
    token = create_access_token(user_email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_scan.return_value = {
        "scan_id": "scan-123",
        "provider": "gmail",
        "total_scanned": 1,
        "spam_count": 0,
        "legitimate_count": 1,
        "high_risk_count": 0,
        "scan_duration_seconds": 1.25,
        "results": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/inbox/gmail/scan", json={"limit": 50}, headers=headers)
    assert response.status_code == 200
    assert response.json()["scan_id"] == "scan-123"
    assert response.json()["total_scanned"] == 1


@patch("app.services.inbox_scan_service.inbox_scan_service.start_imap_scan")
def test_imap_scan(mock_scan, client: TestClient, require_db):
    user_email = "inbox_user@example.com"
    token = create_access_token(user_email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_scan.return_value = {
        "scan_id": "scan-456",
        "provider": "imap",
        "total_scanned": 1,
        "spam_count": 1,
        "legitimate_count": 0,
        "high_risk_count": 1,
        "scan_duration_seconds": 2.1,
        "results": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post(
        "/inbox/imap/scan",
        json={
            "host": "imap.test.com",
            "port": 993,
            "email": "my-email@test.com",
            "password": "app-password",
            "limit": 10
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["scan_id"] == "scan-456"
    assert response.json()["spam_count"] == 1
