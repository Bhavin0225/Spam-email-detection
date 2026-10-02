import pytest
from fastapi.testclient import TestClient
from app.database.collections import get_collection
from app.core.security import create_access_token
from app.database.crud import create_user
from app.core.security import hash_password

def test_analytics_api_permissions(client: TestClient, require_db):
    user_email = "regular_u@example.com"
    analyst_email = "analyst_u@example.com"
    
    get_collection("users").delete_many({"email": {"$in": [user_email, analyst_email]}})
    
    create_user(email=user_email, password_hash=hash_password("Pass123!"), role="user")
    create_user(email=analyst_email, password_hash=hash_password("Pass123!"), role="analyst")
    
    token_user = create_access_token(user_email, "user")
    token_analyst = create_access_token(analyst_email, "analyst")
    
    headers_user = {"Authorization": f"Bearer {token_user}"}
    headers_analyst = {"Authorization": f"Bearer {token_analyst}"}
    
    # 1. Unauthenticated request -> 401
    res_unauth = client.get("/analytics")
    assert res_unauth.status_code == 401
    
    # 2. Standard user -> 403 Forbidden
    res_user = client.get("/analytics", headers=headers_user)
    assert res_user.status_code == 403
    
    # 3. Analyst user -> 200
    res_analyst = client.get("/analytics", headers=headers_analyst)
    assert res_analyst.status_code == 200
    body = res_analyst.json()
    assert "total_scans" in body
    assert "spam_rate" in body
    assert "false_positive_rate" in body
    assert "predictions_over_time" in body
    assert "top_suspicious_domains" in body
