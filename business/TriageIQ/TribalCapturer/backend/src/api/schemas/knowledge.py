"""
Pydantic schemas for KnowledgeEntry-related requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from ...models.knowledge_entry import EntryStatus, KnowledgeType


class KnowledgeEntryCreate(BaseModel):
    """Knowledge entry creation schema."""
    facility: str = Field(..., min_length=1, max_length=255)
    specialty_service: str = Field(..., min_length=1, max_length=255)
    provider_name: Optional[str] = Field(None, max_length=255, description="Optional: Specific provider this knowledge applies to")
    knowledge_type: KnowledgeType = Field(KnowledgeType.GENERAL_KNOWLEDGE, description="Category of knowledge for AI routing")
    is_continuity_care: bool = Field(False, description="Is this about continuity of care (seeing same provider)?")
    knowledge_description: str = Field(..., min_length=10)
    status: EntryStatus = EntryStatus.PUBLISHED


class KnowledgeEntryUpdate(BaseModel):
    """Knowledge entry update schema."""
    facility: Optional[str] = Field(None, min_length=1, max_length=255)
    specialty_service: Optional[str] = Field(None, min_length=1, max_length=255)
    provider_name: Optional[str] = Field(None, max_length=255)
    knowledge_type: Optional[KnowledgeType] = None
    is_continuity_care: Optional[bool] = None
    knowledge_description: Optional[str] = Field(None, min_length=10)
    status: Optional[EntryStatus] = None


class KnowledgeEntrySummary(BaseModel):
    """Knowledge entry summary for list views."""
    id: UUID
    ma_name: str
    facility: str
    specialty_service: str
    provider_name: Optional[str] = None
    knowledge_type: KnowledgeType
    is_continuity_care: bool
    status: EntryStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeEntryDetail(BaseModel):
    """Knowledge entry detail response."""
    id: UUID
    user_id: UUID
    ma_name: str
    facility: str
    specialty_service: str
    provider_name: Optional[str] = None
    knowledge_type: KnowledgeType
    is_continuity_care: bool
    knowledge_description: str
    status: EntryStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Pagination(BaseModel):
    """Pagination metadata."""
    page: int
    page_size: int
    total_items: int
    total_pages: int


class KnowledgeEntryList(BaseModel):
    """Paginated list of knowledge entries."""
    entries: List[KnowledgeEntrySummary]
    pagination: Pagination


class SearchResult(BaseModel):
    """Search result with highlighted snippet."""
    id: UUID
    ma_name: str
    facility: str
    specialty_service: str
    created_at: datetime
    highlighted_snippet: str

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    """Search results response."""
    results: List[SearchResult]
    pagination: Pagination
