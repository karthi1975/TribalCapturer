"""
API routes for user management operations (Creator only).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from ...database import get_db
from ...models.user import User, UserRole
from ...api.dependencies import require_role
from ...api.schemas.user_management import (
    UserCreateByCreator,
    UserUpdateByCreator,
    UserPasswordReset,
    UserAssignments,
    UserDetailWithAssignments,
    UserListResponse,
    UserAssignmentResponse
)
from ...services import user_management_service


router = APIRouter()


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="Get all users (Creator only)"
)
async def get_users(
    page: int = 1,
    page_size: int = 20,
    role: Optional[UserRole] = None,
    active_only: Optional[bool] = True,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of users with their facility and specialty assignments.

    **Creator only**

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        role: Filter by role (optional)
        active_only: Filter by active status (None for all, True for active, False for inactive)
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        UserListResponse: List of users with assignments and pagination info
    """
    users, total = await user_management_service.get_all_users(
        db,
        page=page,
        page_size=page_size,
        role_filter=role,
        active_filter=active_only
    )

    return UserListResponse(
        users=[UserDetailWithAssignments.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post(
    "/users",
    response_model=UserDetailWithAssignments,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user (Creator only)"
)
async def create_user(
    user_data: UserCreateByCreator,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user with optional facility/specialty assignments.

    **Creator only**

    For MA users, facility_ids and specialty_ids can be provided for initial assignment.
    For Creator users, assignments are ignored.

    Args:
        user_data: User creation data
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        UserDetailWithAssignments: Created user with assignments

    Raises:
        HTTPException: 409 if username (email) already exists
        HTTPException: 400 if password requirements not met
    """
    try:
        user = await user_management_service.create_user(
            db,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role,
            facility_ids=user_data.facility_ids if user_data.role == UserRole.MA else [],
            specialty_ids=user_data.specialty_ids if user_data.role == UserRole.MA else [],
            created_by_user_id=current_user.id
        )
        return UserDetailWithAssignments.model_validate(user)
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        raise


@router.get(
    "/users/{user_id}",
    response_model=UserDetailWithAssignments,
    summary="Get user details (Creator only)"
)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user details with facility and specialty assignments.

    **Creator only**

    Args:
        user_id: User UUID
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        UserDetailWithAssignments: User details with assignments

    Raises:
        HTTPException: 404 if user not found
    """
    user = await user_management_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserDetailWithAssignments.model_validate(user)


@router.put(
    "/users/{user_id}",
    response_model=UserDetailWithAssignments,
    summary="Update user details (Creator only)"
)
async def update_user(
    user_id: UUID,
    update_data: UserUpdateByCreator,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user details (name and active status).

    **Creator only**

    Args:
        user_id: User UUID
        update_data: Fields to update
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        UserDetailWithAssignments: Updated user details

    Raises:
        HTTPException: 404 if user not found
    """
    user = await user_management_service.update_user(
        db,
        user_id=user_id,
        full_name=update_data.full_name,
        is_active=update_data.is_active
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserDetailWithAssignments.model_validate(user)


@router.post(
    "/users/{user_id}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Activate user account (Creator only)"
)
async def activate_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Activate a user account.

    **Creator only**

    Args:
        user_id: User UUID
        current_user: Authenticated Creator user
        db: Database session

    Raises:
        HTTPException: 404 if user not found
    """
    success = await user_management_service.activate_user(db, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post(
    "/users/{user_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate user account (Creator only)"
)
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a user account.

    **Creator only**

    Deactivated users cannot log in.

    Args:
        user_id: User UUID
        current_user: Authenticated Creator user
        db: Database session

    Raises:
        HTTPException: 404 if user not found
    """
    success = await user_management_service.deactivate_user(db, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post(
    "/users/{user_id}/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset user password (Creator only)"
)
async def reset_password(
    user_id: UUID,
    password_data: UserPasswordReset,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset a user's password.

    **Creator only**

    Args:
        user_id: User UUID
        password_data: New password
        current_user: Authenticated Creator user
        db: Database session

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 400 if password requirements not met
    """
    success = await user_management_service.reset_user_password(
        db,
        user_id=user_id,
        new_password=password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.put(
    "/users/{user_id}/assignments",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update user assignments (Creator only)"
)
async def update_assignments(
    user_id: UUID,
    assignments: UserAssignments,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's facility and specialty assignments.

    **Creator only**

    Replaces all existing assignments with the provided ones.

    Args:
        user_id: User UUID
        assignments: New facility and specialty assignments
        current_user: Authenticated Creator user
        db: Database session

    Raises:
        HTTPException: 404 if user not found
    """
    # Update facility assignments
    facilities_success = await user_management_service.assign_facilities(
        db,
        user_id=user_id,
        facility_ids=assignments.facility_ids,
        assigned_by_user_id=current_user.id
    )

    # Update specialty assignments
    specialties_success = await user_management_service.assign_specialties(
        db,
        user_id=user_id,
        specialty_ids=assignments.specialty_ids,
        assigned_by_user_id=current_user.id
    )

    if not (facilities_success and specialties_success):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.get(
    "/users/{user_id}/assignments",
    response_model=UserAssignmentResponse,
    summary="Get user assignments (Creator only)"
)
async def get_assignments(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current facility and specialty assignments.

    **Creator only**

    Args:
        user_id: User UUID
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        UserAssignmentResponse: User's facility and specialty assignments

    Raises:
        HTTPException: 404 if user not found
    """
    result = await user_management_service.get_user_assignments(db, user_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    facilities, specialties = result

    from ...api.schemas.facility import FacilityInfo
    from ...api.schemas.specialty import SpecialtyInfo

    return UserAssignmentResponse(
        facilities=[FacilityInfo.model_validate(f) for f in facilities],
        specialties=[SpecialtyInfo.model_validate(s) for s in specialties]
    )
