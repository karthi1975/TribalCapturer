"""
Pydantic schemas for Facility API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class FacilityCreate(BaseModel):
    """Schema for creating a new facility."""
    name: str = Field(..., min_length=1, max_length=255, description="Facility name")
    code: Optional[str] = Field(None, max_length=50, description="Optional facility code")


class FacilityUpdate(BaseModel):
    """Schema for updating a facility."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Facility name")
    code: Optional[str] = Field(None, max_length=50, description="Facility code")
    is_active: Optional[bool] = Field(None, description="Active status")


class FacilityInfo(BaseModel):
    """Schema for facility information."""
    id: UUID
    name: str
    code: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FacilityWithCounts(FacilityInfo):
    """Schema for facility with assignment and entry counts."""
    assigned_user_count: int = Field(0, description="Number of users assigned to this facility")
    knowledge_entry_count: int = Field(0, description="Number of knowledge entries for this facility")


class FacilityListResponse(BaseModel):
    """Schema for paginated facility list response."""
    facilities: list[FacilityInfo]
    total: int
    page: int
    page_size: int
