from typing import List
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.core.exceptions import AuthError, ForbiddenError
from app.core.security import decode_token
from app.database.crud import get_user_by_email

# oauth2_scheme parses authorization bearer headers and integrates with Swagger login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodes the Bearer token, asserts active status, and returns the current user document.
    """
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        token_type = payload.get("type")
        if not email or token_type != "access":
            raise AuthError("Invalid token claims.")
    except jwt.ExpiredSignatureError:
        raise AuthError("Access token signature has expired.")
    except jwt.InvalidTokenError:
        raise AuthError("Access token is invalid.")

    user = get_user_by_email(email)
    if not user:
        raise AuthError("User not found.")

    if user.get("status") != "active":
        raise AuthError("User account has been disabled or is pending approval.")

    return user

class RoleChecker:
    """
    Dependency helper that enforces RBAC role permission checks.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in self.allowed_roles:
            raise ForbiddenError("You do not have required role permissions to perform this action.")
        return current_user

# Pre-defined role hierarchical permission sets
ALL_ROLES = ["user", "analyst", "ml_engineer", "admin", "super_admin"]
ANALYST_OR_ABOVE = ["analyst", "ml_engineer", "admin", "super_admin"]
ML_ENGINEER_OR_ABOVE = ["ml_engineer", "admin", "super_admin"]
ADMIN_OR_ABOVE = ["admin", "super_admin"]
SUPER_ADMIN_ONLY = ["super_admin"]

require_user = RoleChecker(ALL_ROLES)
require_analyst = RoleChecker(ANALYST_OR_ABOVE)
require_ml_engineer = RoleChecker(ML_ENGINEER_OR_ABOVE)
require_admin = RoleChecker(ADMIN_OR_ABOVE)
require_super_admin = RoleChecker(SUPER_ADMIN_ONLY)
