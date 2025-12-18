"""
Pydantic schemas for User-related requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from ...models.user import UserRole


class UserLogin(BaseModel):
    """Login request schema."""
    username: EmailStr
    password: str = Field(..., min_length=12)


class UserCreate(BaseModel):
    """User creation schema."""
    username: EmailStr
    password: str = Field(..., min_length=12)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: UserRole


class UserInfo(BaseModel):
    """User information response schema."""
    id: UUID
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response schema."""
    user: UserInfo
    message: str = "Login successful"


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """JWT token payload data."""
    user_id: UUID
    username: str
    role: UserRole
