"""
API routes for knowledge entry operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from ...database import get_db
from ...models.user import User, UserRole
from ...api.dependencies import get_current_user, require_role
from ...api.schemas.knowledge import (
    KnowledgeEntryCreate,
    KnowledgeEntryUpdate,
    KnowledgeEntryDetail,
    KnowledgeEntryList,
    SearchResults,
    BatchKnowledgeEntryCreate,
    BatchKnowledgeEntryResponse
)
from ...services import knowledge_service
from ...services.pdf_service import generate_single_entry_pdf, generate_bulk_entries_pdf
from ...models.knowledge_entry import EntryStatus

router = APIRouter()


@router.post(
    "/",
    response_model=KnowledgeEntryDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new knowledge entry"
)
async def create_entry(
    entry_data: KnowledgeEntryCreate,
    current_user: User = Depends(require_role(UserRole.MA)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new knowledge entry (MA role only).

    **User Story 1**: As an MA, I want to submit tribal knowledge entries.

    Args:
        entry_data: Knowledge entry data
        current_user: Authenticated MA user
        db: Database session

    Returns:
        KnowledgeEntryDetail: Created entry details
    """
    return await knowledge_service.create_knowledge_entry(db, entry_data, current_user)


@router.post(
    "/batch",
    response_model=BatchKnowledgeEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple knowledge entries atomically"
)
async def create_entries_batch(
    batch_data: BatchKnowledgeEntryCreate,
    current_user: User = Depends(require_role(UserRole.MA)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple knowledge entries in a single atomic transaction (MA role only).

    **Batch Submission**: Submit 1-50 entries at once. All entries are created or none are created.

    **Use Case**: MA captures multiple knowledge entries during a shift and submits them together.

    Args:
        batch_data: Batch of knowledge entry data (1-50 entries)
        current_user: Authenticated MA user
        db: Database session

    Returns:
        BatchKnowledgeEntryResponse: Created entries and summary

    Raises:
        HTTPException: 400 if any entry fails validation or creation
    """
    try:
        created_entries = await knowledge_service.create_knowledge_entries_batch(
            db, batch_data.entries, current_user
        )

        return BatchKnowledgeEntryResponse(
            total_submitted=len(batch_data.entries),
            total_created=len(created_entries),
            entries=created_entries,
            message=f"Successfully created {len(created_entries)} knowledge entries"
        )
    except Exception as e:
        # Return 400 with error details
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch creation failed: {str(e)}"
        )


@router.get(
    "/my-entries",
    response_model=KnowledgeEntryList,
    summary="Get current user's knowledge entries"
)
async def get_my_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[EntryStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(require_role(UserRole.MA)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of current user's knowledge entries.

    **User Story 1**: As an MA, I want to view my submitted entries.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)
        status: Optional filter by entry status (draft or published)
        current_user: Authenticated MA user
        db: Database session

    Returns:
        KnowledgeEntryList: Paginated list of entries
    """
    return await knowledge_service.get_user_knowledge_entries(
        db, current_user.id, page, page_size, status
    )


@router.get(
    "/",
    response_model=KnowledgeEntryList,
    summary="Get all published knowledge entries"
)
async def get_all_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    facility: Optional[str] = Query(None, description="Filter by facility"),
    specialty: Optional[str] = Query(None, description="Filter by specialty service"),
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of all published knowledge entries (Creator role only).

    **User Story 2**: As a Creator, I want to view all tribal knowledge entries.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)
        facility: Optional filter by facility name (partial match)
        specialty: Optional filter by specialty service (partial match)
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        KnowledgeEntryList: Paginated list of published entries
    """
    return await knowledge_service.get_all_knowledge_entries(
        db, page, page_size, facility, specialty
    )


@router.get(
    "/{entry_id}",
    response_model=KnowledgeEntryDetail,
    summary="Get a specific knowledge entry"
)
async def get_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific knowledge entry.

    **User Stories 1 & 2**: View entry details.

    Args:
        entry_id: UUID of the entry
        current_user: Authenticated user (any role)
        db: Database session

    Returns:
        KnowledgeEntryDetail: Entry details

    Raises:
        HTTPException: 404 if entry not found
    """
    entry = await knowledge_service.get_knowledge_entry(db, entry_id)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found"
        )

    # MAs can only view their own entries, Creators can view all published entries
    if current_user.role == UserRole.MA and entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own entries"
        )

    if current_user.role == UserRole.CREATOR and entry.status != EntryStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creators can only view published entries"
        )

    return entry


@router.put(
    "/{entry_id}",
    response_model=KnowledgeEntryDetail,
    summary="Update a knowledge entry"
)
async def update_entry(
    entry_id: UUID,
    entry_data: KnowledgeEntryUpdate,
    current_user: User = Depends(require_role(UserRole.MA)),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a knowledge entry (MA can only update their own entries).

    **User Story 4**: As an MA, I want to edit my knowledge entries.

    Args:
        entry_id: UUID of the entry to update
        entry_data: Updated entry data
        current_user: Authenticated MA user
        db: Database session

    Returns:
        KnowledgeEntryDetail: Updated entry details

    Raises:
        HTTPException: 404 if entry not found or not owned by user
    """
    entry = await knowledge_service.update_knowledge_entry(
        db, entry_id, entry_data, current_user.id
    )

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found or you don't have permission to update it"
        )

    return entry


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a knowledge entry"
)
async def delete_entry(
    entry_id: UUID,
    current_user: User = Depends(require_role(UserRole.MA)),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a knowledge entry (MA can only delete their own entries).

    **User Story 4**: As an MA, I want to delete my knowledge entries.

    Args:
        entry_id: UUID of the entry to delete
        current_user: Authenticated MA user
        db: Database session

    Raises:
        HTTPException: 404 if entry not found or not owned by user
    """
    deleted = await knowledge_service.delete_knowledge_entry(
        db, entry_id, current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge entry not found or you don't have permission to delete it"
        )


@router.get(
    "/search/",
    response_model=SearchResults,
    summary="Search knowledge entries"
)
async def search_entries(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Full-text search of knowledge entries (Creator role only).

    **User Story 3**: As a Creator, I want to search tribal knowledge.

    Args:
        q: Search query text
        page: Page number (1-indexed)
        page_size: Number of items per page (max 100)
        current_user: Authenticated Creator user
        db: Database session

    Returns:
        SearchResults: Paginated search results with highlighted snippets
    """
    return await knowledge_service.search_knowledge_entries(db, q, page, page_size)


@router.get(
    "/smart-search/",
    summary="Intelligent semantic search with auto-fallback"
)
async def intelligent_search(
    q: str = Query(..., min_length=1, description="Search query"),
    facility: Optional[str] = Query(None, description="Filter by facility"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    knowledge_type: Optional[str] = Query(None, description="Filter by knowledge type"),
    continuity_care_only: Optional[bool] = Query(None, description="Show only continuity of care entries"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🧠 Intelligent semantic search using OpenAI embeddings with automatic fallback to keyword search.

    **Features:**
    - Semantic similarity matching (understands context, not just keywords)
    - Auto-fallback to keyword search if AI fails (robust)
    - Filters by facility, specialty, provider, knowledge type
    - Returns relevance scores (1.0 = perfect match, 0.5 = keyword match)

    **Failure Handling:**
    - OpenAI API timeout → Falls back to keyword search
    - No API key → Falls back to keyword search
    - No high-confidence matches → Falls back to keyword search

    Args:
        q: Search query (e.g., "Crohn's disease scheduling")
        facility: Optional facility filter
        specialty: Optional specialty filter
        provider: Optional provider filter
        knowledge_type: Optional knowledge type filter
        continuity_care_only: If true, only show continuity of care entries
        top_k: Number of results to return (max 50)

    Returns:
        List of knowledge entries with relevance scores
    """
    from ...services.semantic_search_service import semantic_search

    filters = {}
    if facility:
        filters["facility"] = facility
    if specialty:
        filters["specialty"] = specialty
    if provider:
        filters["provider"] = provider
    if knowledge_type:
        filters["knowledge_type"] = knowledge_type
    if continuity_care_only is not None:
        filters["is_continuity_care"] = continuity_care_only

    results = await semantic_search(db, q, filters, top_k)

    return {
        "query": q,
        "results": [
            {
                "entry": {
                    "id": str(entry.id),
                    "ma_name": entry.ma_name,
                    "facility": entry.facility,
                    "specialty_service": entry.specialty_service,
                    "provider_name": entry.provider_name,
                    "knowledge_type": entry.knowledge_type.value,
                    "is_continuity_care": entry.is_continuity_care,
                    "knowledge_description": entry.knowledge_description,
                    "created_at": entry.created_at.isoformat(),
                },
                "relevance_score": score,
                "match_type": "semantic" if score > 0.5 else "keyword"
            }
            for entry, score in results
        ],
        "total_results": len(results)
    }


@router.get(
    "/autocomplete/{field}",
    summary="Autocomplete for providers, specialties, facilities"
)
async def autocomplete(
    field: str,
    q: str = Query(..., min_length=1, description="Partial text to search"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🔍 Smart autocomplete for form fields.

    Helps MAs quickly find providers, specialties, or facilities as they type.

    Args:
        field: Field to search (provider_name, specialty_service, facility)
        q: Partial text (e.g., "card" → "Cardiology", "Dr. Smith")
        limit: Max suggestions

    Returns:
        List of unique matching values
    """
    from ...services.semantic_search_service import search_autocomplete

    suggestions = await search_autocomplete(db, q, field, limit)
    return {
        "field": field,
        "query": q,
        "suggestions": suggestions
    }


@router.get(
    "/checklist/",
    summary="Get pre-appointment checklist for AI scheduling"
)
async def get_appointment_checklist(
    specialty: str = Query(..., description="Specialty service"),
    provider: Optional[str] = Query(None, description="Provider name"),
    diagnosis: Optional[str] = Query(None, description="Patient diagnosis/condition"),
    facility: Optional[str] = Query(None, description="Facility"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    📋 AI-Powered Pre-Appointment Checklist Generator

    Extracts structured requirements from tribal knowledge for appointment preparation.

    **Use Case:** AI scheduling system calls this to know what needs to be done before appointment.

    **Example:**
    - Scheduling cardiology follow-up → Returns: "Get BNP labs 48hrs before", "NPO after midnight", etc.
    - Scheduling with Dr. Smith → Returns: "Dr. Smith prefers afternoon slots for complex cases"

    Args:
        specialty: Required specialty (e.g., "Cardiology")
        provider: Optional provider name (e.g., "Dr. Smith")
        diagnosis: Optional diagnosis (e.g., "Heart failure")
        facility: Optional facility filter

    Returns:
        Structured checklist with requirements categorized by type
    """
    from ...services.checklist_service import get_checklist_for_appointment

    checklist = await get_checklist_for_appointment(
        db, specialty, provider, diagnosis, facility
    )
    return checklist


@router.get(
    "/checklist/by-diagnosis/",
    summary="Get scheduling guidance by diagnosis for AI"
)
async def get_diagnosis_guidance(
    diagnosis: str = Query(..., min_length=2, description="Diagnosis or condition"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🩺 Diagnosis-Based Scheduling Guidance for AI

    AI asks: "Patient has Crohn's disease - what do I do?"
    System returns: "Schedule Rheumatologist, check if GI consult done first", etc.

    **Extracted from Tribal Knowledge:**
    - Which specialty to schedule
    - Pre-requisites
    - Urgency
    - Provider preferences

    Args:
        diagnosis: Diagnosis/condition (e.g., "Crohn's disease", "new MI")
        limit: Max results

    Returns:
        List of scheduling guidance with confidence scores
    """
    from ...services.checklist_service import search_requirements_by_diagnosis

    guidance = await search_requirements_by_diagnosis(db, diagnosis, limit)
    return {
        "diagnosis": diagnosis,
        "guidance": guidance,
        "total_results": len(guidance)
    }


@router.get(
    "/{entry_id}/export-pdf",
    summary="Export single knowledge entry as PDF",
    response_class=StreamingResponse
)
async def export_entry_pdf(
    entry_id: UUID,
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a single knowledge entry as a professionally formatted PDF.

    **Creator Role Only**: Only published entries can be exported.

    Returns:
        StreamingResponse with PDF file

    Headers:
        Content-Type: application/pdf
        Content-Disposition: attachment; filename="knowledge_entry_{id}.pdf"

    Raises:
        HTTPException 404: Entry not found
        HTTPException 403: User does not have permission to access this entry
        HTTPException 500: PDF generation failed
    """
    # Fetch entry
    entry = await knowledge_service.get_knowledge_entry(db, entry_id)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge entry with ID {entry_id} not found"
        )

    # Check if entry is published (Creators can only access published entries)
    if entry.status != EntryStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only published entries can be exported"
        )

    # Generate PDF
    try:
        pdf_buffer = generate_single_entry_pdf(entry)

        # Create filename
        filename = f"knowledge_entry_{entry_id}.pdf"

        # Return as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.post(
    "/export-pdf-bulk",
    summary="Export multiple knowledge entries as single PDF",
    response_class=StreamingResponse
)
async def export_entries_bulk_pdf(
    entry_ids: List[UUID] = Body(..., max_length=1000, embed=True),
    current_user: User = Depends(require_role(UserRole.CREATOR)),
    db: AsyncSession = Depends(get_db)
):
    """
    Download multiple knowledge entries as a single PDF (one entry per page).

    **Creator Role Only**: Only published entries can be exported.

    **Limit**: Maximum 1000 entries per request.

    Request Body:
        {
            "entry_ids": ["uuid1", "uuid2", ...]
        }

    Returns:
        StreamingResponse with PDF file

    Headers:
        Content-Type: application/pdf
        Content-Disposition: attachment; filename="knowledge_entries_{timestamp}.pdf"

    Raises:
        HTTPException 400: Empty entry list or too many entries
        HTTPException 403: User does not have permission
        HTTPException 500: PDF generation failed
    """
    # Validate entry count
    if not entry_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Entry IDs list cannot be empty"
        )

    if len(entry_ids) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot export more than 1000 entries at once"
        )

    # Fetch all entries
    from sqlalchemy import select
    from ...models.knowledge_entry import KnowledgeEntry

    query = select(KnowledgeEntry).where(
        KnowledgeEntry.id.in_(entry_ids),
        KnowledgeEntry.status == EntryStatus.PUBLISHED  # Only published entries
    ).order_by(KnowledgeEntry.created_at.desc())

    result = await db.execute(query)
    entries = result.scalars().all()

    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published entries found with the provided IDs"
        )

    # Generate PDF
    try:
        pdf_buffer = generate_bulk_entries_pdf(list(entries))

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"knowledge_entries_{timestamp}.pdf"

        # Return as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )
