"""
Service layer for knowledge entry operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from ..models.knowledge_entry import KnowledgeEntry, EntryStatus
from ..models.user import User
from ..api.schemas.knowledge import (
    KnowledgeEntryCreate,
    KnowledgeEntryUpdate,
    KnowledgeEntryDetail,
    KnowledgeEntrySummary,
    KnowledgeEntryList,
    Pagination,
    SearchResult,
    SearchResults
)


async def create_knowledge_entry(
    db: AsyncSession,
    entry_data: KnowledgeEntryCreate,
    user: User
) -> KnowledgeEntryDetail:
    """
    Create a new knowledge entry.

    Args:
        db: Database session
        entry_data: Knowledge entry data
        user: The authenticated user creating the entry

    Returns:
        KnowledgeEntryDetail: Created entry details
    """
    entry = KnowledgeEntry(
        user_id=user.id,
        ma_name=user.full_name,
        facility=entry_data.facility,
        specialty_service=entry_data.specialty_service,
        provider_name=entry_data.provider_name,
        knowledge_type=entry_data.knowledge_type.value if isinstance(entry_data.knowledge_type, object) else entry_data.knowledge_type,
        is_continuity_care=entry_data.is_continuity_care,
        knowledge_description=entry_data.knowledge_description,
        status=entry_data.status.value if isinstance(entry_data.status, object) else entry_data.status
    )

    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    return KnowledgeEntryDetail.model_validate(entry)


async def get_knowledge_entry(
    db: AsyncSession,
    entry_id: UUID
) -> Optional[KnowledgeEntryDetail]:
    """
    Get a knowledge entry by ID.

    Args:
        db: Database session
        entry_id: UUID of the entry

    Returns:
        Optional[KnowledgeEntryDetail]: Entry details or None if not found
    """
    result = await db.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if entry:
        return KnowledgeEntryDetail.model_validate(entry)
    return None


async def get_user_knowledge_entries(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[EntryStatus] = None
) -> KnowledgeEntryList:
    """
    Get paginated knowledge entries for a specific user.

    Args:
        db: Database session
        user_id: UUID of the user
        page: Page number (1-indexed)
        page_size: Number of items per page
        status_filter: Optional filter by entry status

    Returns:
        KnowledgeEntryList: Paginated list of entries
    """
    # Build query
    query = select(KnowledgeEntry).where(KnowledgeEntry.user_id == user_id)

    if status_filter:
        query = query.where(KnowledgeEntry.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_items = count_result.scalar()

    # Get paginated entries
    offset = (page - 1) * page_size
    query = query.order_by(desc(KnowledgeEntry.created_at)).limit(page_size).offset(offset)

    result = await db.execute(query)
    entries = result.scalars().all()

    # Calculate pagination metadata
    total_pages = (total_items + page_size - 1) // page_size

    return KnowledgeEntryList(
        entries=[KnowledgeEntrySummary.model_validate(e) for e in entries],
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages
        )
    )


async def get_all_knowledge_entries(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    facility_filter: Optional[str] = None,
    specialty_filter: Optional[str] = None
) -> KnowledgeEntryList:
    """
    Get paginated list of all published knowledge entries (for Creator role).

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        facility_filter: Optional filter by facility
        specialty_filter: Optional filter by specialty service

    Returns:
        KnowledgeEntryList: Paginated list of entries
    """
    # Build query - only published entries
    query = select(KnowledgeEntry).where(KnowledgeEntry.status == "published")

    if facility_filter:
        query = query.where(KnowledgeEntry.facility.ilike(f"%{facility_filter}%"))

    if specialty_filter:
        query = query.where(KnowledgeEntry.specialty_service.ilike(f"%{specialty_filter}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total_items = count_result.scalar()

    # Get paginated entries
    offset = (page - 1) * page_size
    query = query.order_by(desc(KnowledgeEntry.created_at)).limit(page_size).offset(offset)

    result = await db.execute(query)
    entries = result.scalars().all()

    # Calculate pagination metadata
    total_pages = (total_items + page_size - 1) // page_size

    return KnowledgeEntryList(
        entries=[KnowledgeEntrySummary.model_validate(e) for e in entries],
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages
        )
    )


async def update_knowledge_entry(
    db: AsyncSession,
    entry_id: UUID,
    entry_data: KnowledgeEntryUpdate,
    user_id: UUID
) -> Optional[KnowledgeEntryDetail]:
    """
    Update a knowledge entry (only if owned by user).

    Args:
        db: Database session
        entry_id: UUID of the entry to update
        entry_data: Updated entry data
        user_id: UUID of the user making the update

    Returns:
        Optional[KnowledgeEntryDetail]: Updated entry or None if not found/unauthorized
    """
    result = await db.execute(
        select(KnowledgeEntry).where(
            KnowledgeEntry.id == entry_id,
            KnowledgeEntry.user_id == user_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        return None

    # Update fields if provided
    if entry_data.facility is not None:
        entry.facility = entry_data.facility
    if entry_data.specialty_service is not None:
        entry.specialty_service = entry_data.specialty_service
    if entry_data.provider_name is not None:
        entry.provider_name = entry_data.provider_name
    if entry_data.knowledge_type is not None:
        entry.knowledge_type = entry_data.knowledge_type.value if isinstance(entry_data.knowledge_type, object) else entry_data.knowledge_type
    if entry_data.is_continuity_care is not None:
        entry.is_continuity_care = entry_data.is_continuity_care
    if entry_data.knowledge_description is not None:
        entry.knowledge_description = entry_data.knowledge_description
    if entry_data.status is not None:
        entry.status = entry_data.status.value if isinstance(entry_data.status, object) else entry_data.status

    await db.commit()
    await db.refresh(entry)

    return KnowledgeEntryDetail.model_validate(entry)


async def delete_knowledge_entry(
    db: AsyncSession,
    entry_id: UUID,
    user_id: UUID
) -> bool:
    """
    Delete a knowledge entry (only if owned by user).

    Args:
        db: Database session
        entry_id: UUID of the entry to delete
        user_id: UUID of the user making the deletion

    Returns:
        bool: True if deleted, False if not found/unauthorized
    """
    result = await db.execute(
        select(KnowledgeEntry).where(
            KnowledgeEntry.id == entry_id,
            KnowledgeEntry.user_id == user_id
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        return False

    await db.delete(entry)
    await db.commit()

    return True


async def search_knowledge_entries(
    db: AsyncSession,
    query_text: str,
    page: int = 1,
    page_size: int = 20
) -> SearchResults:
    """
    Full-text search of knowledge entries.

    Args:
        db: Database session
        query_text: Search query text
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        SearchResults: Paginated search results with highlighted snippets
    """
    # PostgreSQL full-text search query
    search_query = select(KnowledgeEntry).where(
        KnowledgeEntry.status == "published",
        func.to_tsvector('english', KnowledgeEntry.knowledge_description).op('@@')(
            func.plainto_tsquery('english', query_text)
        )
    )

    # Get total count
    count_query = select(func.count()).select_from(search_query.subquery())
    count_result = await db.execute(count_query)
    total_items = count_result.scalar()

    # Get paginated results
    offset = (page - 1) * page_size
    search_query = search_query.order_by(desc(KnowledgeEntry.created_at)).limit(page_size).offset(offset)

    result = await db.execute(search_query)
    entries = result.scalars().all()

    # Calculate pagination metadata
    total_pages = (total_items + page_size - 1) // page_size

    # Create search results with snippets
    search_results = []
    for entry in entries:
        # Extract snippet (first 200 chars for now; can be enhanced with ts_headline)
        snippet = entry.knowledge_description[:200]
        if len(entry.knowledge_description) > 200:
            snippet += "..."

        search_results.append(SearchResult(
            id=entry.id,
            ma_name=entry.ma_name,
            facility=entry.facility,
            specialty_service=entry.specialty_service,
            created_at=entry.created_at,
            highlighted_snippet=snippet
        ))

    return SearchResults(
        results=search_results,
        pagination=Pagination(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages
        )
    )
