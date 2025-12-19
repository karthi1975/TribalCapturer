"""
API routes for facility management operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from ...database import get_db
from ...models.user import User, UserRole
from ...api.dependencies import get_current_user, require_role
from ...api.schemas.facility import (
    FacilityCreate,
    FacilityUpdate,
    FacilityInfo,
    FacilityWithCounts,
    FacilityListResponse
)
from ...services import facility_service


router = APIRouter()


@router.get(
    "/",
    response_model=FacilityListResponse,
    summary="Get all facilities"
)
async def get_facilities(
    page: int = 1,
    page_size: int = 50,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of facilities.

    Accessible by any authenticated user (both MA and Creator).

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        active_only: Filter for active facilities only
        current_user: Authenticated user
        db: Database session

    Returns:
        FacilityListResponse: List of facilities with pagination info
    """
    facilities, total = await facility_service.get_all_facilities(
        db, page=page, page_size=page_size, active_only=active_only
    )

    return FacilityListResponse(
        facilities=[FacilityInfo.model_validate(f) for f in facilities],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post(
    "/",
    response_model=FacilityInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Create facility (Creator only)"
)
async def create_facility(
    facility_data: FacilityCreate,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new facility.

    **Creator only**

    Args:
        facility_data: Facility creation data
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        FacilityInfo: Created facility information

    Raises:
        HTTPException: 409 if facility with same name already exists
    """
    try:
        facility = await facility_service.create_facility(
            db,
            name=facility_data.name,
            code=facility_data.code,
            created_by_user_id=current_user.id
        )
        return FacilityInfo.model_validate(facility)
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Facility with this name already exists"
            )
        raise


@router.get(
    "/my-facilities",
    response_model=list[FacilityInfo],
    summary="Get facilities assigned to current MA user"
)
async def get_my_facilities(
    current_user: User = Depends(require_role(UserRole.MA)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active facilities assigned to the current MA user.

    **MA only** - Used for populating the MA's facility dropdown.

    Args:
        current_user: Authenticated MA user
        db: Database session

    Returns:
        List[FacilityInfo]: List of assigned facilities
    """
    facilities = await facility_service.get_facilities_for_user(db, current_user.id)
    return [FacilityInfo.model_validate(f) for f in facilities]


@router.get(
    "/{facility_id}",
    response_model=FacilityWithCounts,
    summary="Get facility details"
)
async def get_facility(
    facility_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get facility details with assignment and entry counts.

    Args:
        facility_id: Facility UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        FacilityWithCounts: Facility information with counts

    Raises:
        HTTPException: 404 if facility not found
    """
    facility = await facility_service.get_facility_by_id(db, facility_id)

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )

    # Get counts
    assigned_user_count = await facility_service.get_facility_assignment_count(db, facility_id)
    knowledge_entry_count = await facility_service.get_facility_entry_count(db, facility_id)

    facility_info = FacilityInfo.model_validate(facility)

    return FacilityWithCounts(
        **facility_info.model_dump(),
        assigned_user_count=assigned_user_count,
        knowledge_entry_count=knowledge_entry_count
    )


@router.put(
    "/{facility_id}",
    response_model=FacilityInfo,
    summary="Update facility (Creator only)"
)
async def update_facility(
    facility_id: UUID,
    update_data: FacilityUpdate,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update facility details.

    **Creator only**

    Args:
        facility_id: Facility UUID
        update_data: Fields to update
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        FacilityInfo: Updated facility information

    Raises:
        HTTPException: 404 if facility not found
        HTTPException: 409 if new name conflicts with existing facility
    """
    try:
        facility = await facility_service.update_facility(
            db,
            facility_id=facility_id,
            name=update_data.name,
            code=update_data.code,
            is_active=update_data.is_active
        )

        if not facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Facility not found"
            )

        return FacilityInfo.model_validate(facility)
    except Exception as e:
        if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Facility with this name already exists"
            )
        raise


@router.delete(
    "/{facility_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate facility (Creator only)"
)
async def deactivate_facility(
    facility_id: UUID,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a facility (soft delete).

    **Creator only**

    Args:
        facility_id: Facility UUID
        current_user: Authenticated Creator user
        db: Database session

    Raises:
        HTTPException: 404 if facility not found
    """
    success = await facility_service.deactivate_facility(db, facility_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
