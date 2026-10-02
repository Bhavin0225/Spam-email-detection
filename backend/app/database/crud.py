import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.database.collections import get_collection
from app.utils.logger import logger

def get_user_by_email(email: str) -> Optional[dict]:
    """
    Retrieves a user document from MongoDB by email address.
    """
    users_col = get_collection("users")
    return users_col.find_one({"email": email.lower()})

def get_user_by_id(user_id: str) -> Optional[dict]:
    """
    Retrieves a user document from MongoDB by user_id.
    """
    users_col = get_collection("users")
    return users_col.find_one({"user_id": user_id})

def create_user(email: str, password_hash: str, full_name: Optional[str] = None, role: str = "user") -> dict:
    """
    Creates and stores a new user record in the users collection.
    """
    users_col = get_collection("users")
    now = datetime.now(timezone.utc)
    user_document = {
        "user_id": str(uuid.uuid4()),
        "email": email.lower(),
        "password_hash": password_hash,
        "full_name": full_name,
        "role": role,
        "status": "active",
        "auth_provider": "local",
        "email_verified": False,
        "mfa_enabled": False,
        "last_login_at": None,
        "created_at": now,
        "updated_at": now
    }
    users_col.insert_one(user_document)
    return user_document

def update_user_last_login(user_id: str) -> None:
    """
    Updates the last_login_at and updated_at timestamps for a user.
    """
    users_col = get_collection("users")
    now = datetime.now(timezone.utc)
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"last_login_at": now, "updated_at": now}}
    )

def get_all_users() -> List[dict]:
    """
    Retrieves all user documents from the collection.
    """
    users_col = get_collection("users")
    return list(users_col.find({}))

def write_audit_log(
    event_type: str,
    details: dict,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    severity: str = "info",
    request_id: Optional[str] = None
) -> dict:
    """
    Writes a new audit record to the system_logs collection.
    Wrapped defensively so that database write issues here do not abort request routing.
    """
    try:
        logs_col = get_collection("system_logs")
        log_document = {
            "log_id": str(uuid.uuid4()),
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc),
            "severity": severity,
            "request_id": request_id
        }
        logs_col.insert_one(log_document)
        return log_document
    except Exception as e:
        logger.error(f"Failed to write system audit log document: {str(e)}")
        return {}
