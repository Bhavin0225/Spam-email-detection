import pytest
from unittest.mock import patch, MagicMock
from app.services.email_providers import gmail_connector


def test_get_auth_url():
    auth_url = gmail_connector.get_auth_url("http://test-redirect")
    assert "client_id" in auth_url
    assert "redirect_uri=http://test-redirect" in auth_url
    assert "scope=" in auth_url


@patch("requests.post")
def test_exchange_code_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "mock_access",
        "refresh_token": "mock_refresh",
        "expires_in": 3600
    }
    mock_post.return_value = mock_response

    res = gmail_connector.exchange_code("mock_auth_code", "http://test-redirect")
    assert res["access_token"] == "mock_access"
    assert res["refresh_token"] == "mock_refresh"
    assert res["expires_in"] == 3600


@patch("requests.post")
def test_exchange_code_failure(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    with pytest.raises(ValueError):
        gmail_connector.exchange_code("bad_code")


@patch("requests.get")
def test_fetch_emails(mock_get):
    # Mocking list response
    mock_list_response = MagicMock()
    mock_list_response.status_code = 200
    mock_list_response.json.return_value = {
        "messages": [
            {"id": "msg123", "threadId": "thread123"}
        ]
    }
    
    # Mocking message get response
    mock_msg_response = MagicMock()
    mock_msg_response.status_code = 200
    mock_msg_response.json.return_value = {
        "id": "msg123",
        "internalDate": "1717800000000",  # epoch ms
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "sender@test.com"},
                {"name": "Date", "value": "Sun, 08 Jun 2026 00:00:00 GMT"},
                {"name": "Authentication-Results", "value": "mx.google.com; spf=pass dkim=pass dmarc=pass"}
            ],
            "mimeType": "text/plain",
            "body": {
                "data": "SGVsbG8gV29ybGQ="  # "Hello World" in base64
            }
        }
    }

    mock_get.side_effect = [mock_list_response, mock_msg_response]

    emails = gmail_connector.fetch_emails("mock_token", limit=1)
    assert len(emails) == 1
    assert emails[0]["subject"] == "Test Subject"
    assert emails[0]["sender"] == "sender@test.com"
    assert emails[0]["body"] == "Hello World"
    assert emails[0]["headers"]["spf"] == "pass"
    assert emails[0]["headers"]["dkim"] == "pass"
    assert emails[0]["headers"]["dmarc"] == "pass"
    assert emails[0]["source"] == "gmail"
