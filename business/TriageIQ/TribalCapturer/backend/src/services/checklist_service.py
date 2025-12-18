"""
Pre-appointment checklist service - extracts requirements from tribal knowledge for AI scheduling.

This service intelligently surfaces pre-visit requirements based on:
- Specialty
- Provider
- Diagnosis/symptoms
- Knowledge type categorization
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import logging

from ..models.knowledge_entry import KnowledgeEntry, KnowledgeType

logger = logging.getLogger(__name__)


async def get_checklist_for_appointment(
    db: AsyncSession,
    specialty: str,
    provider_name: Optional[str] = None,
    diagnosis: Optional[str] = None,
    facility: Optional[str] = None
) -> Dict[str, any]:
    """
    Generate pre-appointment checklist by extracting requirements from tribal knowledge.

    AI can call this to get structured requirements for appointment preparation.

    Args:
        db: Database session
        specialty: Specialty service (e.g., "Cardiology")
        provider_name: Optional specific provider
        diagnosis: Optional diagnosis/condition
        facility: Optional facility filter

    Returns:
        Structured checklist with requirements categorized by type

    Example Response:
    {
        "specialty": "Cardiology",
        "provider": "Dr. Smith",
        "requirements": [
            {
                "type": "lab",
                "description": "BNP levels (must be within 48 hours)",
                "source": "Sarah J., 3/15/2024",
                "priority": "required"
            },
            {
                "type": "patient_prep",
                "description": "NPO after midnight",
                "source": "Michael C., 2/20/2024",
                "priority": "required"
            },
            {
                "type": "continuity",
                "description": "Check if patient has seen cardiologist before - prefer same provider",
                "source": "Emma R., 1/10/2024",
                "priority": "recommended"
            }
        ],
        "provider_preferences": [
            "Dr. Smith prefers afternoon slots for complex cases",
            "Dr. Smith reviews charts in AM - schedule new patients after 1PM"
        ],
        "total_requirements": 3
    }
    """

    # Build query for relevant knowledge entries
    query = select(KnowledgeEntry).where(
        KnowledgeEntry.status == "published",
        KnowledgeEntry.specialty_service.ilike(f"%{specialty}%"),
        or_(
            KnowledgeEntry.knowledge_type == KnowledgeType.PRE_VISIT_REQUIREMENT.value,
            KnowledgeEntry.knowledge_type == KnowledgeType.PROVIDER_PREFERENCE.value,
            KnowledgeEntry.knowledge_type == KnowledgeType.CONTINUITY_CARE.value,
        )
    )

    # Add optional filters
    if provider_name:
        query = query.where(
            or_(
                KnowledgeEntry.provider_name.ilike(f"%{provider_name}%"),
                KnowledgeEntry.provider_name.is_(None)  # Also include general knowledge
            )
        )

    if facility:
        query = query.where(KnowledgeEntry.facility.ilike(f"%{facility}%"))

    result = await db.execute(query)
    entries = result.scalars().all()

    # Structure the requirements
    requirements = []
    provider_preferences = []

    for entry in entries:
        if entry.knowledge_type == KnowledgeType.PRE_VISIT_REQUIREMENT.value:
            # Extract lab/imaging/prep requirements
            req = _parse_requirement(entry)
            if req:
                requirements.append(req)

        elif entry.knowledge_type == KnowledgeType.PROVIDER_PREFERENCE.value:
            # Provider-specific preferences
            provider_preferences.append({
                "preference": entry.knowledge_description[:200],
                "provider": entry.provider_name or "General",
                "source": f"{entry.ma_name}, {entry.created_at.strftime('%m/%d/%Y')}"
            })

        elif entry.knowledge_type == KnowledgeType.CONTINUITY_CARE.value:
            # Continuity of care requirements
            requirements.append({
                "type": "continuity",
                "description": entry.knowledge_description[:200],
                "source": f"{entry.ma_name}, {entry.created_at.strftime('%m/%d/%Y')}",
                "priority": "recommended",
                "is_continuity_care": True
            })

    return {
        "specialty": specialty,
        "provider": provider_name,
        "facility": facility,
        "requirements": requirements,
        "provider_preferences": provider_preferences,
        "total_requirements": len(requirements),
        "total_preferences": len(provider_preferences)
    }


def _parse_requirement(entry: KnowledgeEntry) -> Optional[Dict]:
    """
    Parse a knowledge entry to extract structured requirement.
    Uses simple keyword matching - can be enhanced with NLP/LLM later.
    """
    description = entry.knowledge_description.lower()

    # Determine requirement type by keywords
    req_type = "general"
    if any(word in description for word in ["lab", "labs", "blood work", "bnp", "ekg", "ecg"]):
        req_type = "lab"
    elif any(word in description for word in ["npo", "fasting", "empty stomach", "preparation"]):
        req_type = "patient_prep"
    elif any(word in description for word in ["imaging", "x-ray", "mri", "ct scan", "ultrasound"]):
        req_type = "imaging"
    elif any(word in description for word in ["authorization", "referral", "pre-auth", "insurance"]):
        req_type = "authorization"

    # Determine priority
    priority = "recommended"
    if any(word in description for word in ["must", "required", "always", "critical", "necessary"]):
        priority = "required"

    return {
        "type": req_type,
        "description": entry.knowledge_description[:300],  # Limit length
        "source": f"{entry.ma_name}, {entry.created_at.strftime('%m/%d/%Y')}",
        "priority": priority,
        "full_entry_id": str(entry.id)
    }


async def search_requirements_by_diagnosis(
    db: AsyncSession,
    diagnosis: str,
    limit: int = 10
) -> List[Dict]:
    """
    Search for scheduling requirements by diagnosis/condition.
    Uses semantic search if available, falls back to keyword search.

    This enables AI to answer: "What do I need to do when scheduling a patient with Crohn's disease?"

    Args:
        db: Database session
        diagnosis: Diagnosis or condition (e.g., "Crohn's disease", "heart failure")
        limit: Max results

    Returns:
        List of relevant requirements with context
    """
    # Try semantic search first if OpenAI is available
    try:
        from .semantic_search_service import semantic_search

        results = await semantic_search(
            db,
            query=diagnosis,
            filters={"knowledge_type": KnowledgeType.DIAGNOSIS_SPECIALTY.value},
            top_k=limit
        )

        return [
            {
                "diagnosis": diagnosis,
                "recommended_specialty": entry.specialty_service,
                "facility": entry.facility,
                "provider": entry.provider_name,
                "guidance": entry.knowledge_description,
                "confidence": score,
                "source": f"{entry.ma_name}, {entry.created_at.strftime('%m/%d/%Y')}"
            }
            for entry, score in results
        ]
    except Exception as e:
        logger.error(f"Semantic search failed, using keyword search: {e}")

        # Fallback to keyword search
        query = select(KnowledgeEntry).where(
            KnowledgeEntry.status == "published",
            KnowledgeEntry.knowledge_description.ilike(f"%{diagnosis}%"),
            KnowledgeEntry.knowledge_type == KnowledgeType.DIAGNOSIS_SPECIALTY.value
        ).limit(limit)

        result = await db.execute(query)
        entries = result.scalars().all()

        return [
            {
                "diagnosis": diagnosis,
                "recommended_specialty": entry.specialty_service,
                "facility": entry.facility,
                "provider": entry.provider_name,
                "guidance": entry.knowledge_description,
                "confidence": 0.5,  # Keyword match
                "source": f"{entry.ma_name}, {entry.created_at.strftime('%m/%d/%Y')}"
            }
            for entry in entries
        ]
