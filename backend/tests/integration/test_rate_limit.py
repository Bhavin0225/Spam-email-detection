import pytest
from fastapi.testclient import TestClient

def test_rate_limiting_trigger_auth_login(client: TestClient, require_db):
    """
    Simulates high frequency logins and verifies that slowapi successfully triggers a
    429 Too Many Requests response after exceeding the limit threshold.
    """
    form_data = {
        "username": "rate_limit_test@example.com",
        "password": "some-random-password-value"
    }

    status_codes = []
    # Send 12 rapid login requests (limit is 10/minute)
    for _ in range(12):
        response = client.post("/auth/login", data=form_data)
        status_codes.append(response.status_code)

    # Assert that at least one request was rate limited and returned HTTP 429
    assert 429 in status_codes
    # The final requests must be blocked with a 429 status code
    assert status_codes[-1] == 429
    
    # Assert JSON response matches ErrorResponse schema custom message
    last_response = client.post("/auth/login", data=form_data)
    assert last_response.status_code == 429
    assert "detail" in last_response.json()
    assert "Too many requests" in last_response.json()["detail"]
