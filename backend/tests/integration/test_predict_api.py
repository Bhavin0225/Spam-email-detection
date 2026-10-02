import pytest
from fastapi.testclient import TestClient
from app.database.collections import get_collection
from app.core.security import create_access_token
from app.database.crud import create_user
from app.core.security import hash_password

def test_predict_endpoint_success_and_db_persistence(client: TestClient, require_db):
    email = "predict_test@example.com"
    # Ensure database is clean of users to avoid conflict
    get_collection("users").delete_many({"email": email})
    create_user(email=email, password_hash=hash_password("Password123!"), role="user")
    token = create_access_token(email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "subject": "Urgent Invoice Payment",
        "body": "Dear customer, pay your invoice at http://suspicious-link.net immediately!",
        "sender": "billing@scam.com"
    }
    
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "prediction_id" in body
    assert "email_id" in body
    assert body["prediction_label"] in ("suspicious", "legitimate")
    assert "confidence" in body
    assert body["risk_level"] in ("high", "medium", "low")
    assert body["model_version"] == "v1.0.0"
    
    # Assert DB records
    emails_col = get_collection("emails")
    predictions_col = get_collection("predictions")
    
    email_doc = emails_col.find_one({"email_id": body["email_id"]})
    assert email_doc is not None
    assert email_doc["subject"] == payload["subject"]
    assert email_doc["body_text"] == payload["body"]
    
    pred_doc = predictions_col.find_one({"prediction_id": body["prediction_id"]})
    assert pred_doc is not None
    assert pred_doc["prediction_label"] == body["prediction_label"]
    assert pred_doc["user_id"] is not None

def test_predict_endpoint_unauthorized(client: TestClient, require_db):
    payload = {
        "subject": "Urgent Invoice Payment",
        "body": "Dear customer, pay your invoice at http://suspicious-link.net immediately!",
        "sender": "billing@scam.com"
    }
    # No auth header -> 401
    response = client.post("/predict", json=payload)
    assert response.status_code == 401

def test_predict_endpoint_rate_limit(client: TestClient, require_db):
    email = "rate_limit_test@example.com"
    get_collection("users").delete_many({"email": email})
    create_user(email=email, password_hash=hash_password("Password123!"), role="user")
    token = create_access_token(email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "subject": "Limiter Check",
        "body": "Check limit",
        "sender": "limiter@check.com"
    }
    
    # Make 11 requests, 11th should return 429
    responses = []
    for _ in range(11):
        responses.append(client.post("/predict", json=payload, headers=headers))
        
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes
