import pytest
from unittest.mock import patch, MagicMock
from app.services.email_providers import imap_connector


@patch("imaplib.IMAP4_SSL")
def test_fetch_emails_imap_success(mock_imap):
    # Mock IMAP connection instance
    mock_instance = MagicMock()
    mock_imap.return_value = mock_instance
    
    mock_instance.login.return_value = ("OK", [b"Logged in"])
    mock_instance.select.return_value = ("OK", [b"10"])
    mock_instance.search.return_value = ("OK", [b"1 2 3"])
    
    # Mock FETCH response
    raw_email = (
        b"From: sender@test.com\r\n"
        b"Subject: IMAP Test\r\n"
        b"Date: Sun, 08 Jun 2026 00:00:00 +0000\r\n"
        b"Authentication-Results: mx.google.com; spf=pass; dkim=pass; dmarc=pass\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n\r\n"
        b"Hello IMAP World"
    )
    mock_instance.fetch.return_value = ("OK", [(b"1", raw_email)])
    
    emails = imap_connector.fetch_emails(
        host="imap.test.com",
        port=993,
        email_address="user@test.com",
        password="app-password",
        limit=1
    )
    
    assert len(emails) == 1
    assert emails[0]["subject"] == "IMAP Test"
    assert emails[0]["sender"] == "sender@test.com"
    assert emails[0]["body"] == "Hello IMAP World"
    assert emails[0]["headers"]["spf"] == "pass"
    assert emails[0]["headers"]["dkim"] == "pass"
    assert emails[0]["headers"]["dmarc"] == "pass"
    assert emails[0]["source"] == "imap"


@patch("imaplib.IMAP4_SSL")
def test_fetch_emails_imap_auth_failed(mock_imap):
    mock_instance = MagicMock()
    mock_imap.return_value = mock_instance
    
    import imaplib
    mock_instance.login.side_effect = imaplib.IMAP4.error("Invalid credentials")
    
    with pytest.raises(ValueError) as exc:
        imap_connector.fetch_emails(
            host="imap.test.com",
            port=993,
            email_address="user@test.com",
            password="wrong-password",
            limit=1
        )
    assert "IMAP authentication failed" in str(exc.value)
