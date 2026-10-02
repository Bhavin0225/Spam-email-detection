import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.services.inbox_scan_service import inbox_scan_service, encrypt_token, decrypt_token
from app.database.collections import get_collection


def test_token_encryption_decryption():
    orig_token = "my-oauth-access-token-12345"
    enc = encrypt_token(orig_token)
    assert enc != orig_token
    dec = decrypt_token(enc)
    assert dec == orig_token


@patch("app.services.email_providers.gmail_connector.fetch_emails")
@patch("app.services.inbox_scan_service.InboxScanServiceClass._get_valid_gmail_token")
@patch("app.services.prediction_service.prediction_service.predict_and_store")
def test_start_gmail_scan(mock_predict, mock_get_token, mock_fetch, require_db):
    mock_get_token.return_value = "valid_token"
    
    mock_fetch.return_value = [
        {
            "subject": "Spam Alert",
            "body": "Win a million dollars",
            "sender": "spammer@spam.com",
            "headers": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
            "date_sent": datetime.now(timezone.utc),
            "attachments": [],
            "source": "gmail"
        }
    ]
    
    mock_predict.return_value = {
        "prediction_label": "suspicious",
        "confidence": 0.99,
        "risk_level": "high",
        "prediction_id": "pred_123"
    }

    # Ensure collection is clean
    get_collection("inbox_scans").delete_many({"user_id": "user_123"})

    report = inbox_scan_service.start_gmail_scan("user_123", limit=1)
    
    assert report.total_scanned == 1
    assert report.spam_count == 1
    assert report.legitimate_count == 0
    assert report.high_risk_count == 1
    assert len(report.results) == 1
    assert report.results[0].subject == "Spam Alert"
    assert report.results[0].prediction_label == "suspicious"
    assert report.provider == "gmail"

    # Verify scan is stored in history
    history = inbox_scan_service.get_user_scan_history("user_123")
    assert len(history) == 1
    assert history[0].scan_id == report.scan_id
    assert history[0].provider == "gmail"
    assert history[0].total_scanned == 1


@patch("app.services.email_providers.imap_connector.fetch_emails")
@patch("app.services.prediction_service.prediction_service.predict_and_store")
def test_start_imap_scan(mock_predict, mock_fetch, require_db):
    mock_fetch.return_value = [
        {
            "subject": "Legitimate Subject",
            "body": "Hello, how are you?",
            "sender": "friend@gmail.com",
            "headers": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
            "date_sent": datetime.now(timezone.utc),
            "attachments": [],
            "source": "imap"
        }
    ]
    
    mock_predict.return_value = {
        "prediction_label": "legitimate",
        "confidence": 0.05,
        "risk_level": "low",
        "prediction_id": "pred_456"
    }

    # Ensure collection is clean
    get_collection("inbox_scans").delete_many({"user_id": "user_123"})

    report = inbox_scan_service.start_imap_scan(
        "user_123",
        {"host": "imap.test.com", "port": 993, "email": "test@test.com", "password": "pass"},
        limit=1
    )
    
    assert report.total_scanned == 1
    assert report.spam_count == 0
    assert report.legitimate_count == 1
    assert report.high_risk_count == 0
    assert report.provider == "imap"
