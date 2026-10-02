import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.database.collections import get_collection
from app.core.security import create_access_token
from app.database.crud import create_user
from app.core.security import hash_password

def test_feedback_api_flows(client: TestClient, require_db):
    user_a = "user_a@example.com"
    user_b = "user_b@example.com"
    
    get_collection("users").delete_many({"email": {"$in": [user_a, user_b]}})
    
    ua = create_user(email=user_a, password_hash=hash_password("Pass123!"), role="user")
    ub = create_user(email=user_b, password_hash=hash_password("Pass123!"), role="user")
    
    token_a = create_access_token(user_a, "user")
    token_b = create_access_token(user_b, "user")
    
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # 1. Create prediction record owned by user_a
    predictions_col = get_collection("predictions")
    predictions_col.delete_many({})
    predictions_col.insert_one({
        "prediction_id": "pred-a",
        "email_id": "email-1",
        "prediction_label": "suspicious",
        "confidence": 0.90,
        "risk_level": "high",
        "user_id": ua["user_id"],
        "created_at": datetime.now(timezone.utc)
    })
    
    # 2. Submit feedback from owner (user_a) -> 200
    payload = {
        "prediction_id": "pred-a",
        "was_correct": False,
        "correct_label": "legitimate",
        "comment": "False positive check"
    }
    response = client.post("/feedback", json=payload, headers=headers_a)
    assert response.status_code == 200
    assert response.json()["was_correct"] is False
    assert response.json()["correct_label"] == "legitimate"
    
    # 3. Submit feedback from non-owner (user_b) -> 403 Forbidden
    response = client.post("/feedback", json=payload, headers=headers_b)
    assert response.status_code == 403
    
    # 4. Submit feedback for missing prediction -> 404 Not Found
    payload_fake = {
        "prediction_id": "pred-nonexistent",
        "was_correct": True,
        "correct_label": ""
    }
    response = client.post("/feedback", json=payload_fake, headers=headers_a)
    assert response.status_code == 404
