"""
Facility management service for CRUD operations on facilities.
"""
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload

from ..models.facility import Facility
from ..models.user_facility import UserFacility


async def get_all_facilities(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    active_only: bool = True
) -> Tuple[List[Facility], int]:
    """
    Get paginated list of facilities.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        active_only: Filter for active facilities only

    Returns:
        Tuple of (facilities list, total count)
    """
    # Build base query
    query = select(Facility)

    if active_only:
        query = query.where(Facility.is_active == True)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_count_result = await db.execute(count_query)
    total_count = total_count_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Facility.name)

    result = await db.execute(query)
    facilities = result.scalars().all()

    return facilities, total_count


async def get_facility_by_id(db: AsyncSession, facility_id: UUID) -> Optional[Facility]:
    """
    Get facility by ID.

    Args:
        db: Database session
        facility_id: Facility UUID

    Returns:
        Facility if found, None otherwise
    """
    result = await db.execute(
        select(Facility).where(Facility.id == facility_id)
    )
    return result.scalar_one_or_none()


async def create_facility(
    db: AsyncSession,
    name: str,
    code: Optional[str] = None,
    created_by_user_id: Optional[UUID] = None
) -> Facility:
    """
    Create a new facility.

    Args:
        db: Database session
        name: Facility name
        code: Optional facility code
        created_by_user_id: UUID of creator

    Returns:
        Created Facility
    """
    facility = Facility(
        name=name,
        code=code,
        is_active=True,
        created_by=created_by_user_id
    )

    db.add(facility)
    await db.commit()
    await db.refresh(facility)

    return facility


async def update_facility(
    db: AsyncSession,
    facility_id: UUID,
    name: Optional[str] = None,
    code: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[Facility]:
    """
    Update facility details.

    Args:
        db: Database session
        facility_id: Facility UUID
        name: New name (optional)
        code: New code (optional)
        is_active: New active status (optional)

    Returns:
        Updated Facility if found, None otherwise
    """
    facility = await get_facility_by_id(db, facility_id)

    if not facility:
        return None

    if name is not None:
        facility.name = name
    if code is not None:
        facility.code = code
    if is_active is not None:
        facility.is_active = is_active

    await db.commit()
    await db.refresh(facility)

    return facility


async def deactivate_facility(db: AsyncSession, facility_id: UUID) -> bool:
    """
    Deactivate a facility (soft delete).

    Args:
        db: Database session
        facility_id: Facility UUID

    Returns:
        True if deactivated, False if not found
    """
    facility = await get_facility_by_id(db, facility_id)

    if not facility:
        return False

    facility.is_active = False
    await db.commit()

    return True


async def get_facilities_for_user(db: AsyncSession, user_id: UUID) -> List[Facility]:
    """
    Get all active facilities assigned to a specific user (for MA dropdown).

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        List of assigned facilities
    """
    result = await db.execute(
        select(Facility)
        .join(UserFacility, UserFacility.facility_id == Facility.id)
        .where(
            UserFacility.user_id == user_id,
            Facility.is_active == True
        )
        .order_by(Facility.name)
    )
    return result.scalars().all()


async def get_all_active_facilities(db: AsyncSession) -> List[Facility]:
    """
    Get all active facilities (for Creator assignment UI).

    Args:
        db: Database session

    Returns:
        List of all active facilities
    """
    result = await db.execute(
        select(Facility)
        .where(Facility.is_active == True)
        .order_by(Facility.name)
    )
    return result.scalars().all()


async def get_facility_assignment_count(db: AsyncSession, facility_id: UUID) -> int:
    """
    Get count of users assigned to a facility.

    Args:
        db: Database session
        facility_id: Facility UUID

    Returns:
        Count of assigned users
    """
    result = await db.execute(
        select(func.count(UserFacility.user_id))
        .where(UserFacility.facility_id == facility_id)
    )
    return result.scalar() or 0


async def get_facility_entry_count(db: AsyncSession, facility_id: UUID) -> int:
    """
    Get count of knowledge entries for a facility.

    Args:
        db: Database session
        facility_id: Facility UUID

    Returns:
        Count of knowledge entries
    """
    from ..models.knowledge_entry import KnowledgeEntry

    result = await db.execute(
        select(func.count(KnowledgeEntry.id))
        .where(KnowledgeEntry.facility_id == facility_id)
    )
    return result.scalar() or 0
