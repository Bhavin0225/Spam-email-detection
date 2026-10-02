from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from app.core.exceptions import AuthError, UserConflictError
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.database.crud import get_user_by_email, create_user, update_user_last_login
from app.schemas.auth import SignupRequest, TokenResponse, TokenRefreshRequest, UserResponse
from app.middleware.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Signup",
    description="Registers a new user account with default role 'user' and hashes their password. Rate limited to 10 requests per minute."
)
@limiter.limit("10/minute")
def signup(request: Request, body: SignupRequest):
    # Verify user email uniqueness
    existing_user = get_user_by_email(body.email)
    if existing_user:
        raise UserConflictError()

    # Hash user password and insert
    hashed_pwd = hash_password(body.password)
    user = create_user(
        email=body.email,
        password_hash=hashed_pwd,
        full_name=body.full_name,
        role="user"
    )
    return user

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticates credentials and returns a Bearer access token and refresh token. Rate limited to 10 requests per minute."
)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # Get user by email (username parameter in OAuth2 form)
    user = get_user_by_email(form_data.username)
    if not user:
        raise AuthError("Invalid email or password.")

    # Validate bcrypt hash match
    if not verify_password(form_data.password, user["password_hash"]):
        raise AuthError("Invalid email or password.")

    if user.get("status") != "active":
        raise AuthError("User account is disabled or pending approval.")

    # Update last login timestamp
    update_user_last_login(user["user_id"])

    # Issue tokens
    access = create_access_token(user["email"], user["role"])
    refresh = create_refresh_token(user["email"])

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer"
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Token Refresh",
    description="Validates a refresh token and generates a new pair of access and refresh tokens."
)
def refresh_token(body: TokenRefreshRequest):
    try:
        # Decode and assert token type is 'refresh'
        payload = decode_token(body.refresh_token, verify_refresh=True)
        email = payload.get("sub")
        token_type = payload.get("type")
        if not email or token_type != "refresh":
            raise AuthError("Invalid refresh token claims.")
    except jwt.ExpiredSignatureError:
        raise AuthError("Refresh token has expired.")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid refresh token.")

    # Verify user existence and active status
    user = get_user_by_email(email)
    if not user:
        raise AuthError("User not found.")

    if user.get("status") != "active":
        raise AuthError("User account has been deactivated.")

    # Issue new token pair
    access = create_access_token(user["email"], user["role"])
    refresh = create_refresh_token(user["email"])

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer"
    )
