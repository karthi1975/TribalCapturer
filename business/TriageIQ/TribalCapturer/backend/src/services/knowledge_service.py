"""
Service layer for knowledge entry operations.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from fastapi import HTTPException, status
from ..models.knowledge_entry import KnowledgeEntry, EntryStatus
from ..models.user import User, UserRole
from ..models.user_facility import UserFacility
from ..models.user_specialty import UserSpecialty
from ..models.facility import Facility
from ..models.specialty import Specialty
from ..api.schemas.knowledge import (
    KnowledgeEntryCreate,
    KnowledgeEntryUpdate,
    KnowledgeEntryDetail,
    KnowledgeEntrySummary,
    KnowledgeEntryList,
    Pagination,
    SearchResult,
    SearchResults,
    BatchKnowledgeEntryCreate,
    BatchKnowledgeEntryResponse
)


async def _validate_ma_assignment(
    db: AsyncSession,
    user: User,
    facility_text: str,
    specialty_text: str
) -> tuple[Optional[UUID], Optional[UUID]]:
    """
    Validate that MA user has access to facility and specialty.
    Returns facility_id and specialty_id if valid.

    For Creator users, just looks up the IDs without validation.

    Args:
        db: Database session
        user: User making the request
        facility_text: Facility name
        specialty_text: Specialty name

    Returns:
        Tuple of (facility_id, specialty_id)

    Raises:
        HTTPException: If MA user lacks access or if facility/specialty not found
    """
    # Look up facility by name
    facility_result = await db.execute(
        select(Facility).where(Facility.name == facility_text)
    )
    facility = facility_result.scalar_one_or_none()

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Facility '{facility_text}' not found"
        )

    # Look up specialty by name
    specialty_result = await db.execute(
        select(Specialty).where(Specialty.name == specialty_text)
    )
    specialty = specialty_result.scalar_one_or_none()

    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Specialty '{specialty_text}' not found"
        )

    # For MA users, validate assignments
    if user.role == UserRole.MA:
        # Check facility assignment
        facility_check = await db.execute(
            select(UserFacility).where(
                UserFacility.user_id == user.id,
                UserFacility.facility_id == facility.id
            )
        )
        if not facility_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not assigned to facility '{facility_text}'"
            )

        # Check specialty assignment
        specialty_check = await db.execute(
            select(UserSpecialty).where(
                UserSpecialty.user_id == user.id,
                UserSpecialty.specialty_id == specialty.id
            )
        )
        if not specialty_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not assigned to specialty '{specialty_text}'"
            )

    return facility.id, specialty.id


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

    Raises:
        HTTPException: If MA user lacks access to facility/specialty
    """
    # Validate MA assignment and get facility/specialty IDs
    facility_id, specialty_id = await _validate_ma_assignment(
        db, user, entry_data.facility, entry_data.specialty_service
    )

    entry = KnowledgeEntry(
        user_id=user.id,
        ma_name=user.full_name,
        # Old fields (for backwards compatibility during migration)
        facility=entry_data.facility,
        specialty_service=entry_data.specialty_service,
        # New foreign key fields
        facility_id=facility_id,
        specialty_id=specialty_id,
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


async def create_knowledge_entries_batch(
    db: AsyncSession,
    entries_data: List[KnowledgeEntryCreate],
    user: User
) -> List[KnowledgeEntryDetail]:
    """
    Create multiple knowledge entries atomically in a single transaction.

    All entries are created or none are created (all-or-nothing).

    Args:
        db: Database session
        entries_data: List of knowledge entry data
        user: The authenticated user creating the entries

    Returns:
        List[KnowledgeEntryDetail]: Created entry details

    Raises:
        Exception: If any entry fails validation or creation
        HTTPException: If MA user lacks access to any facility/specialty
    """
    created_entries = []

    try:
        # Create all entries within the existing transaction
        for entry_data in entries_data:
            # Validate MA assignment and get facility/specialty IDs
            facility_id, specialty_id = await _validate_ma_assignment(
                db, user, entry_data.facility, entry_data.specialty_service
            )

            entry = KnowledgeEntry(
                user_id=user.id,
                ma_name=user.full_name,
                # Old fields (for backwards compatibility during migration)
                facility=entry_data.facility,
                specialty_service=entry_data.specialty_service,
                # New foreign key fields
                facility_id=facility_id,
                specialty_id=specialty_id,
                provider_name=entry_data.provider_name,
                knowledge_type=entry_data.knowledge_type.value if isinstance(entry_data.knowledge_type, object) else entry_data.knowledge_type,
                is_continuity_care=entry_data.is_continuity_care,
                knowledge_description=entry_data.knowledge_description,
                status=entry_data.status.value if isinstance(entry_data.status, object) else entry_data.status
            )
            db.add(entry)
            created_entries.append(entry)

        # Commit all at once (atomic)
        await db.commit()

        # Refresh all entries to get database-generated values
        for entry in created_entries:
            await db.refresh(entry)

        return [KnowledgeEntryDetail.model_validate(e) for e in created_entries]

    except Exception as e:
        # Rollback is handled by get_db() dependency
        raise e


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
