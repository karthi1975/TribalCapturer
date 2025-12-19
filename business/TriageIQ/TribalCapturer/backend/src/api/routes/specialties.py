"""
API routes for specialty management operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from ...database import get_db
from ...models.user import User, UserRole
from ...api.dependencies import get_current_user, require_role
from ...api.schemas.specialty import (
    SpecialtyCreate,
    SpecialtyUpdate,
    SpecialtyInfo,
    SpecialtyWithCounts,
    SpecialtyListResponse
)
from ...services import specialty_service


router = APIRouter()


@router.get(
    "/",
    response_model=SpecialtyListResponse,
    summary="Get all specialties"
)
async def get_specialties(
    page: int = 1,
    page_size: int = 50,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of specialties.

    Accessible by any authenticated user (both MA and Creator).

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        active_only: Filter for active specialties only
        current_user: Authenticated user
        db: Database session

    Returns:
        SpecialtyListResponse: List of specialties with pagination info
    """
    specialties, total = await specialty_service.get_all_specialties(
        db, page=page, page_size=page_size, active_only=active_only
    )

    return SpecialtyListResponse(
        specialties=[SpecialtyInfo.model_validate(s) for s in specialties],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post(
    "/",
    response_model=SpecialtyInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Create specialty (Creator only)"
)
async def create_specialty(
    specialty_data: SpecialtyCreate,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new specialty.

    **Creator only**

    Args:
        specialty_data: Specialty creation data
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        SpecialtyInfo: Created specialty information

    Raises:
        HTTPException: 409 if specialty with same name already exists
    """
    try:
        specialty = await specialty_service.create_specialty(
            db,
            name=specialty_data.name,
            code=specialty_data.code,
            created_by_user_id=current_user.id
        )
        return SpecialtyInfo.model_validate(specialty)
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Specialty with this name already exists"
            )
        raise


@router.get(
    "/my-specialties",
    response_model=list[SpecialtyInfo],
    summary="Get specialties assigned to current MA user"
)
async def get_my_specialties(
    current_user: User = Depends(require_role(UserRole.MA)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active specialties assigned to the current MA user.

    **MA only** - Used for populating the MA's specialty dropdown.

    Args:
        current_user: Authenticated MA user
        db: Database session

    Returns:
        List[SpecialtyInfo]: List of assigned specialties
    """
    specialties = await specialty_service.get_specialties_for_user(db, current_user.id)
    return [SpecialtyInfo.model_validate(s) for s in specialties]


@router.get(
    "/{specialty_id}",
    response_model=SpecialtyWithCounts,
    summary="Get specialty details"
)
async def get_specialty(
    specialty_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specialty details with assignment and entry counts.

    Args:
        specialty_id: Specialty UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        SpecialtyWithCounts: Specialty information with counts

    Raises:
        HTTPException: 404 if specialty not found
    """
    specialty = await specialty_service.get_specialty_by_id(db, specialty_id)

    if not specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialty not found"
        )

    # Get counts
    assigned_user_count = await specialty_service.get_specialty_assignment_count(db, specialty_id)
    knowledge_entry_count = await specialty_service.get_specialty_entry_count(db, specialty_id)

    specialty_info = SpecialtyInfo.model_validate(specialty)

    return SpecialtyWithCounts(
        **specialty_info.model_dump(),
        assigned_user_count=assigned_user_count,
        knowledge_entry_count=knowledge_entry_count
    )


@router.put(
    "/{specialty_id}",
    response_model=SpecialtyInfo,
    summary="Update specialty (Creator only)"
)
async def update_specialty(
    specialty_id: UUID,
    update_data: SpecialtyUpdate,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update specialty details.

    **Creator only**

    Args:
        specialty_id: Specialty UUID
        update_data: Fields to update
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        SpecialtyInfo: Updated specialty information

    Raises:
        HTTPException: 404 if specialty not found
        HTTPException: 409 if new name conflicts with existing specialty
    """
    try:
        specialty = await specialty_service.update_specialty(
            db,
            specialty_id=specialty_id,
            name=update_data.name,
            code=update_data.code,
            is_active=update_data.is_active
        )

        if not specialty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Specialty not found"
            )

        return SpecialtyInfo.model_validate(specialty)
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Specialty with this name already exists"
            )
        raise


@router.delete(
    "/{specialty_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate specialty (Creator only)"
)
async def deactivate_specialty(
    specialty_id: UUID,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a specialty (soft delete).

    **Creator only**

    Args:
        specialty_id: Specialty UUID
        current_user: Authenticated Creator user
        db: Database session

    Raises:
        HTTPException: 404 if specialty not found
    """
    success = await specialty_service.deactivate_specialty(db, specialty_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialty not found"
        )
