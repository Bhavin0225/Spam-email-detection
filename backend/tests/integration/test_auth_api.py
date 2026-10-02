import pytest
from fastapi.testclient import TestClient
from app.database.collections import get_collection
from app.database.crud import create_user
from app.core.security import hash_password

def test_signup_flow_success(client: TestClient, require_db):
    """
    Verifies that a new user registration succeeds and stores the user in MongoDB.
    """
    email = "signup_test@example.com"
    payload = {
        "email": email,
        "password": "StrongPassword123!",
        "full_name": "Signup Test User"
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201
    
    body = response.json()
    assert "user_id" in body
    assert body["email"] == email
    assert body["role"] == "user"
    assert body["status"] == "active"
    
    # Confirm DB storage
    users_col = get_collection("users")
    db_user = users_col.find_one({"email": email})
    assert db_user is not None
    assert db_user["full_name"] == "Signup Test User"
    assert db_user["password_hash"] != "StrongPassword123!"

def test_signup_flow_duplicate_email(client: TestClient, require_db):
    """
    Verifies duplicate signup attempts return a 409 Conflict status.
    """
    email = "dup_test@example.com"
    # Create the user directly
    create_user(email=email, password_hash="hashed_pw", role="user")
    
    payload = {
        "email": email,
        "password": "OtherPassword123!",
        "full_name": "Duplicate User"
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"

def test_login_flow_success_and_audit(client: TestClient, require_db):
    """
    Verifies valid logins issue access and refresh tokens, and log the event.
    """
    email = "login_test@example.com"
    pwd = "HashedLogin123!"
    hashed_pwd = hash_password(pwd)
    create_user(email=email, password_hash=hashed_pwd, role="user")
    
    # login router expects urlencoded form data
    form_data = {
        "username": email,
        "password": pwd
    }
    response = client.post("/auth/login", data=form_data)
    assert response.status_code == 200
    
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    
    # Check that audit logs were written
    logs_col = get_collection("system_logs")
    log = logs_col.find_one({"event_type": "login", "details.path": "/auth/login"})
    assert log is not None
    assert log["severity"] == "info"

def test_login_flow_failure(client: TestClient, require_db):
    """
    Verifies failed credentials return generic 401 response error details.
    """
    form_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=form_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."

def test_refresh_token_success(client: TestClient, require_db):
    """
    Verifies using a valid refresh token yields new access and refresh tokens.
    """
    email = "refresh_test@example.com"
    pwd = "HashedRefresh123!"
    hashed_pwd = hash_password(pwd)
    create_user(email=email, password_hash=hashed_pwd, role="user")
    
    login_response = client.post("/auth/login", data={"username": email, "password": pwd})
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh
    refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    body = refresh_response.json()
    assert "access_token" in body
    assert "refresh_token" in body

def test_admin_route_permissions(client: TestClient, require_db):
    """
    Verifies that GET /admin/users rejects standard users with a 403 Forbidden,
    but grants access to administrators.
    """
    user_email = "regular_user@example.com"
    admin_email = "admin_user@example.com"
    pwd = "HashedPassword123!"
    
    create_user(email=user_email, password_hash=hash_password(pwd), role="user")
    create_user(email=admin_email, password_hash=hash_password(pwd), role="admin")
    
    # Authenticate standard user
    user_login = client.post("/auth/login", data={"username": user_email, "password": pwd}).json()
    user_headers = {"Authorization": f"Bearer {user_login['access_token']}"}
    
    # Authenticate admin user
    admin_login = client.post("/auth/login", data={"username": admin_email, "password": pwd}).json()
    admin_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}
    
    # Standard user check
    regular_response = client.get("/admin/users", headers=user_headers)
    assert regular_response.status_code == 403
    
    # Admin user check
    admin_response = client.get("/admin/users", headers=admin_headers)
    assert admin_response.status_code == 200
    assert len(admin_response.json()) >= 2
