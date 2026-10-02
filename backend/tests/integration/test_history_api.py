import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.database.collections import get_collection
from app.core.security import create_access_token
from app.database.crud import create_user
from app.core.security import hash_password

def test_history_api_pagination_and_filters(client: TestClient, require_db):
    user_email = "history_u@example.com"
    get_collection("users").delete_many({"email": user_email})
    u = create_user(email=user_email, password_hash=hash_password("Pass123!"), role="user")
    user_id = u["user_id"]
    
    token = create_access_token(user_email, "user")
    headers = {"Authorization": f"Bearer {token}"}
    
    predictions_col = get_collection("predictions")
    emails_col = get_collection("emails")
    
    predictions_col.delete_many({})
    emails_col.delete_many({})
    
    emails_col.insert_many([
        {"email_id": "e-1", "subject": "Hello 1", "body_text": "Body 1", "sender": "s@s.com", "sender_domain": "s.com", "content_hash": "h1"},
        {"email_id": "e-2", "subject": "Hello 2", "body_text": "Body 2", "sender": "s@s.com", "sender_domain": "s.com", "content_hash": "h2"}
    ])
    
    now = datetime.now(timezone.utc)
    predictions_col.insert_many([
        {
            "prediction_id": "p-1",
            "email_id": "e-1",
            "model_version": "v1.0.0",
            "prediction_label": "suspicious",
            "confidence": 0.95,
            "risk_level": "high",
            "user_id": user_id,
            "created_at": now - timedelta(hours=1)
        },
        {
            "prediction_id": "p-2",
            "email_id": "e-2",
            "model_version": "v1.0.0",
            "prediction_label": "legitimate",
            "confidence": 0.15,
            "risk_level": "low",
            "user_id": user_id,
            "created_at": now
        }
    ])
    
    # 2. Query history -> returns both, sorted DESC by created_at
    response = client.get("/history", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["prediction_id"] == "p-2"
    assert body[0]["email"]["subject"] == "Hello 2"
    
    # 3. Query history with limit=1 -> returns p-2
    response = client.get("/history?limit=1", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["prediction_id"] == "p-2"
    
    # 4. Query with filter risk_level=high -> returns p-1
    response = client.get("/history?risk_level=high", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["prediction_id"] == "p-1"
