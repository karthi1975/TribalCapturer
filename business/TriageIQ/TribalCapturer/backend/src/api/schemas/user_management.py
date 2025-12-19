"""
Pydantic schemas for User Management API endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ...models.user import UserRole
from .facility import FacilityInfo
from .specialty import SpecialtyInfo


class UserCreateByCreator(BaseModel):
    """Schema for creating a new user by Creator."""
    username: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=12, description="Password (minimum 12 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    role: UserRole = Field(..., description="User role (MA or Creator)")
    facility_ids: List[UUID] = Field(default=[], description="Facility UUIDs to assign (for MA users)")
    specialty_ids: List[UUID] = Field(default=[], description="Specialty UUIDs to assign (for MA users)")


class UserUpdateByCreator(BaseModel):
    """Schema for updating a user by Creator."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's full name")
    is_active: Optional[bool] = Field(None, description="Active status")


class UserPasswordReset(BaseModel):
    """Schema for resetting user password."""
    new_password: str = Field(..., min_length=12, description="New password (minimum 12 characters)")


class UserAssignments(BaseModel):
    """Schema for updating user assignments."""
    facility_ids: List[UUID] = Field(..., description="Facility UUIDs to assign")
    specialty_ids: List[UUID] = Field(..., description="Specialty UUIDs to assign")


class UserDetailWithAssignments(BaseModel):
    """Schema for user details with facility and specialty assignments."""
    id: UUID
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    assigned_facilities: List[FacilityInfo] = []
    assigned_specialties: List[SpecialtyInfo] = []

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: List[UserDetailWithAssignments]
    total: int
    page: int
    page_size: int


class UserAssignmentResponse(BaseModel):
    """Schema for user assignment details."""
    facilities: List[FacilityInfo]
    specialties: List[SpecialtyInfo]
