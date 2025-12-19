"""
User management service for Creator role to manage MA users and assignments.
"""
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from ..models.user import User, UserRole
from ..models.facility import Facility
from ..models.specialty import Specialty
from ..models.user_facility import UserFacility
from ..models.user_specialty import UserSpecialty
from ..services.auth_service import hash_password


async def get_all_users(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    role_filter: Optional[UserRole] = None,
    active_filter: Optional[bool] = True
) -> Tuple[List[User], int]:
    """
    Get paginated list of users with their assignments.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        role_filter: Filter by role (optional)
        active_filter: Filter by active status (None for all, True for active, False for inactive)

    Returns:
        Tuple of (users list with assignments, total count)
    """
    # Build base query
    query = select(User).options(
        selectinload(User.assigned_facilities),
        selectinload(User.assigned_specialties)
    )

    if role_filter:
        query = query.where(User.role == role_filter)

    if active_filter is not None:
        query = query.where(User.is_active == active_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_count_result = await db.execute(count_query)
    total_count = total_count_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    return users, total_count


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Get user by ID with assignments.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        User with assignments if found, None otherwise
    """
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.assigned_facilities),
            selectinload(User.assigned_specialties)
        )
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    full_name: str,
    role: UserRole,
    facility_ids: List[UUID] = [],
    specialty_ids: List[UUID] = [],
    created_by_user_id: Optional[UUID] = None
) -> User:
    """
    Create a new user with optional facility/specialty assignments.

    Args:
        db: Database session
        username: User email
        password: Plain text password (will be hashed)
        full_name: User's full name
        role: User role (MA or Creator)
        facility_ids: List of facility UUIDs to assign (for MA users)
        specialty_ids: List of specialty UUIDs to assign (for MA users)
        created_by_user_id: UUID of creator

    Returns:
        Created User
    """
    # Hash password
    password_hash = hash_password(password)

    # Create user
    user = User(
        username=username,
        password_hash=password_hash,
        full_name=full_name,
        role=role,
        is_active=True
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Assign facilities and specialties for MA users
    if role == UserRole.MA and (facility_ids or specialty_ids):
        await assign_facilities(db, user.id, facility_ids, created_by_user_id)
        await assign_specialties(db, user.id, specialty_ids, created_by_user_id)
        await db.refresh(user)

    return user


async def update_user(
    db: AsyncSession,
    user_id: UUID,
    full_name: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[User]:
    """
    Update user details.

    Args:
        db: Database session
        user_id: User UUID
        full_name: New full name (optional)
        is_active: New active status (optional)

    Returns:
        Updated User if found, None otherwise
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        return None

    if full_name is not None:
        user.full_name = full_name
    if is_active is not None:
        user.is_active = is_active

    await db.commit()
    await db.refresh(user)

    return user


async def activate_user(db: AsyncSession, user_id: UUID) -> bool:
    """
    Activate user account.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        True if activated, False if not found
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        return False

    user.is_active = True
    await db.commit()

    return True


async def deactivate_user(db: AsyncSession, user_id: UUID) -> bool:
    """
    Deactivate user account.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        True if deactivated, False if not found
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        return False

    user.is_active = False
    await db.commit()

    return True


async def reset_user_password(
    db: AsyncSession,
    user_id: UUID,
    new_password: str
) -> bool:
    """
    Reset user password.

    Args:
        db: Database session
        user_id: User UUID
        new_password: Plain text new password (will be hashed)

    Returns:
        True if password reset, False if user not found
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        return False

    user.password_hash = hash_password(new_password)
    await db.commit()

    return True


async def assign_facilities(
    db: AsyncSession,
    user_id: UUID,
    facility_ids: List[UUID],
    assigned_by_user_id: Optional[UUID] = None
) -> bool:
    """
    Assign facilities to MA user (replaces existing assignments).

    Args:
        db: Database session
        user_id: User UUID
        facility_ids: List of facility UUIDs
        assigned_by_user_id: UUID of assigner

    Returns:
        True if successful, False if user not found
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        return False

    # Remove existing assignments
    await db.execute(
        delete(UserFacility).where(UserFacility.user_id == user_id)
    )

    # Create new assignments
    for facility_id in facility_ids:
        assignment = UserFacility(
            user_id=user_id,
            facility_id=facility_id,
            assigned_by=assigned_by_user_id
        )
        db.add(assignment)

    await db.commit()
    return True


async def assign_specialties(
    db: AsyncSession,
    user_id: UUID,
    specialty_ids: List[UUID],
    assigned_by_user_id: Optional[UUID] = None
) -> bool:
    """
    Assign specialties to MA user (replaces existing assignments).

    Args:
        db: Database session
        user_id: User UUID
        specialty_ids: List of specialty UUIDs
        assigned_by_user_id: UUID of assigner

    Returns:
        True if successful, False if user not found
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        return False

    # Remove existing assignments
    await db.execute(
        delete(UserSpecialty).where(UserSpecialty.user_id == user_id)
    )

    # Create new assignments
    for specialty_id in specialty_ids:
        assignment = UserSpecialty(
            user_id=user_id,
            specialty_id=specialty_id,
            assigned_by=assigned_by_user_id
        )
        db.add(assignment)

    await db.commit()
    return True


async def get_user_assignments(
    db: AsyncSession,
    user_id: UUID
) -> Optional[Tuple[List[Facility], List[Specialty]]]:
    """
    Get user's facility and specialty assignments.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        Tuple of (facilities, specialties) if user found, None otherwise
    """
    user = await get_user_by_id(db, user_id)

    if not user:
        return None

    return user.assigned_facilities, user.assigned_specialties


async def remove_facility_assignment(
    db: AsyncSession,
    user_id: UUID,
    facility_id: UUID
) -> bool:
    """
    Remove specific facility assignment from user.

    Args:
        db: Database session
        user_id: User UUID
        facility_id: Facility UUID

    Returns:
        True if removed, False if not found
    """
    result = await db.execute(
        delete(UserFacility).where(
            UserFacility.user_id == user_id,
            UserFacility.facility_id == facility_id
        )
    )
    await db.commit()

    return result.rowcount > 0


async def remove_specialty_assignment(
    db: AsyncSession,
    user_id: UUID,
    specialty_id: UUID
) -> bool:
    """
    Remove specific specialty assignment from user.

    Args:
        db: Database session
        user_id: User UUID
        specialty_id: Specialty UUID

    Returns:
        True if removed, False if not found
    """
    result = await db.execute(
        delete(UserSpecialty).where(
            UserSpecialty.user_id == user_id,
            UserSpecialty.specialty_id == specialty_id
        )
    )
    await db.commit()

    return result.rowcount > 0
