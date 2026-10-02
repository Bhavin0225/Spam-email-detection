import pytest
from app.core.exceptions import ForbiddenError
from app.core.permissions import RoleChecker

def test_role_checker_passes_when_authorized():
    """
    Verifies that the RoleChecker allows requests when the user's role is in the allowed list.
    """
    checker = RoleChecker(["admin", "super_admin"])
    user_payload = {"email": "admin@example.com", "role": "admin"}
    
    result = checker(current_user=user_payload)
    assert result == user_payload

def test_role_checker_raises_forbidden_unauthorized():
    """
    Verifies that the RoleChecker blocks requests by throwing ForbiddenError when role claims match exclusions.
    """
    checker = RoleChecker(["admin", "super_admin"])
    user_payload = {"email": "user@example.com", "role": "user"}
    
    with pytest.raises(ForbiddenError) as exc_info:
        checker(current_user=user_payload)
        
    assert exc_info.value.status_code == 403
    assert "You do not have required role permissions" in exc_info.value.detail
