from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRole(str, Enum):
    USER = "user"
    ANALYST = "analyst"
    ML_ENGINEER = "ml_engineer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"

class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="Unique email address for registration")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type prefix")

class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid refresh token")

class UserResponse(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User's email address")
    role: UserRole = Field(..., description="Assigned RBAC role")
    status: UserStatus = Field(..., description="User account status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Account last update timestamp")
