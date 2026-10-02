from fastapi import HTTPException, status

class AuthError(HTTPException):
    """
    Exception raised when authentication fails (HTTP 401).
    """
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class ForbiddenError(HTTPException):
    """
    Exception raised when authorization/RBAC checks fail (HTTP 403).
    """
    def __init__(self, detail: str = "Not enough permissions to access this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class UserConflictError(HTTPException):
    """
    Exception raised when trying to register a user that already exists (HTTP 409).
    """
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
