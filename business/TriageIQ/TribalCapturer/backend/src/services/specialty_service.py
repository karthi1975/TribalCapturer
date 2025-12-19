"""
Specialty management service for CRUD operations on specialties.
"""
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload

from ..models.specialty import Specialty
from ..models.user_specialty import UserSpecialty


async def get_all_specialties(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    active_only: bool = True
) -> Tuple[List[Specialty], int]:
    """
    Get paginated list of specialties.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        active_only: Filter for active specialties only

    Returns:
        Tuple of (specialties list, total count)
    """
    # Build base query
    query = select(Specialty)

    if active_only:
        query = query.where(Specialty.is_active == True)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_count_result = await db.execute(count_query)
    total_count = total_count_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Specialty.name)

    result = await db.execute(query)
    specialties = result.scalars().all()

    return specialties, total_count


async def get_specialty_by_id(db: AsyncSession, specialty_id: UUID) -> Optional[Specialty]:
    """
    Get specialty by ID.

    Args:
        db: Database session
        specialty_id: Specialty UUID

    Returns:
        Specialty if found, None otherwise
    """
    result = await db.execute(
        select(Specialty).where(Specialty.id == specialty_id)
    )
    return result.scalar_one_or_none()


async def create_specialty(
    db: AsyncSession,
    name: str,
    code: Optional[str] = None,
    created_by_user_id: Optional[UUID] = None
) -> Specialty:
    """
    Create a new specialty.

    Args:
        db: Database session
        name: Specialty name
        code: Optional specialty code
        created_by_user_id: UUID of creator

    Returns:
        Created Specialty
    """
    specialty = Specialty(
        name=name,
        code=code,
        is_active=True,
        created_by=created_by_user_id
    )

    db.add(specialty)
    await db.commit()
    await db.refresh(specialty)

    return specialty


async def update_specialty(
    db: AsyncSession,
    specialty_id: UUID,
    name: Optional[str] = None,
    code: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[Specialty]:
    """
    Update specialty details.

    Args:
        db: Database session
        specialty_id: Specialty UUID
        name: New name (optional)
        code: New code (optional)
        is_active: New active status (optional)

    Returns:
        Updated Specialty if found, None otherwise
    """
    specialty = await get_specialty_by_id(db, specialty_id)

    if not specialty:
        return None

    if name is not None:
        specialty.name = name
    if code is not None:
        specialty.code = code
    if is_active is not None:
        specialty.is_active = is_active

    await db.commit()
    await db.refresh(specialty)

    return specialty


async def deactivate_specialty(db: AsyncSession, specialty_id: UUID) -> bool:
    """
    Deactivate a specialty (soft delete).

    Args:
        db: Database session
        specialty_id: Specialty UUID

    Returns:
        True if deactivated, False if not found
    """
    specialty = await get_specialty_by_id(db, specialty_id)

    if not specialty:
        return False

    specialty.is_active = False
    await db.commit()

    return True


async def get_specialties_for_user(db: AsyncSession, user_id: UUID) -> List[Specialty]:
    """
    Get all active specialties assigned to a specific user (for MA dropdown).

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        List of assigned specialties
    """
    result = await db.execute(
        select(Specialty)
        .join(UserSpecialty, UserSpecialty.specialty_id == Specialty.id)
        .where(
            UserSpecialty.user_id == user_id,
            Specialty.is_active == True
        )
        .order_by(Specialty.name)
    )
    return result.scalars().all()


async def get_all_active_specialties(db: AsyncSession) -> List[Specialty]:
    """
    Get all active specialties (for Creator assignment UI).

    Args:
        db: Database session

    Returns:
        List of all active specialties
    """
    result = await db.execute(
        select(Specialty)
        .where(Specialty.is_active == True)
        .order_by(Specialty.name)
    )
    return result.scalars().all()


async def get_specialty_assignment_count(db: AsyncSession, specialty_id: UUID) -> int:
    """
    Get count of users assigned to a specialty.

    Args:
        db: Database session
        specialty_id: Specialty UUID

    Returns:
        Count of assigned users
    """
    result = await db.execute(
        select(func.count(UserSpecialty.user_id))
        .where(UserSpecialty.specialty_id == specialty_id)
    )
    return result.scalar() or 0


async def get_specialty_entry_count(db: AsyncSession, specialty_id: UUID) -> int:
    """
    Get count of knowledge entries for a specialty.

    Args:
        db: Database session
        specialty_id: Specialty UUID

    Returns:
        Count of knowledge entries
    """
    from ..models.knowledge_entry import KnowledgeEntry

    result = await db.execute(
        select(func.count(KnowledgeEntry.id))
        .where(KnowledgeEntry.specialty_id == specialty_id)
    )
    return result.scalar() or 0
