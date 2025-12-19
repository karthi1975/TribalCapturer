"""
Pydantic schemas for Specialty API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class SpecialtyCreate(BaseModel):
    """Schema for creating a new specialty."""
    name: str = Field(..., min_length=1, max_length=255, description="Specialty name")
    code: Optional[str] = Field(None, max_length=50, description="Optional specialty code")


class SpecialtyUpdate(BaseModel):
    """Schema for updating a specialty."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Specialty name")
    code: Optional[str] = Field(None, max_length=50, description="Specialty code")
    is_active: Optional[bool] = Field(None, description="Active status")


class SpecialtyInfo(BaseModel):
    """Schema for specialty information."""
    id: UUID
    name: str
    code: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SpecialtyWithCounts(SpecialtyInfo):
    """Schema for specialty with assignment and entry counts."""
    assigned_user_count: int = Field(0, description="Number of users assigned to this specialty")
    knowledge_entry_count: int = Field(0, description="Number of knowledge entries for this specialty")


class SpecialtyListResponse(BaseModel):
    """Schema for paginated specialty list response."""
    specialties: list[SpecialtyInfo]
    total: int
    page: int
    page_size: int
