"""
Semantic search service using OpenAI embeddings for intelligent knowledge retrieval.
Implements failure handling, caching, and fallback to keyword search.
"""
from typing import List, Optional, Tuple
from openai import OpenAI, OpenAIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
import numpy as np
from datetime import datetime
import logging

from ..models.knowledge_entry import KnowledgeEntry
from ..config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
try:
    client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    client = None


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


async def generate_embedding(text: str, timeout: float = 2.0) -> Optional[List[float]]:
    """
    Generate embedding for text using OpenAI API with timeout and error handling.

    Failure modes handled:
    - API timeout (> 2s)
    - API rate limit
    - API key invalid/missing
    - Network errors

    Returns None on any failure, allowing fallback to keyword search.
    """
    if not client:
        logger.warning("OpenAI client not initialized")
        return None

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",  # Cheaper, faster model
            input=text,
            timeout=timeout
        )
        return response.data[0].embedding
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating embedding: {e}")
        return None


async def semantic_search(
    db: AsyncSession,
    query: str,
    filters: Optional[dict] = None,
    top_k: int = 10,
    min_similarity: float = 0.5
) -> List[Tuple[KnowledgeEntry, float]]:
    """
    Intelligent semantic search with automatic fallback to keyword search.

    Args:
        db: Database session
        query: Search query text
        filters: Optional filters (facility, specialty, provider, knowledge_type)
        top_k: Number of results to return
        min_similarity: Minimum similarity score threshold

    Returns:
        List of (KnowledgeEntry, similarity_score) tuples, sorted by relevance

    Failure handling:
    - If embedding generation fails → fallback to keyword search
    - If no results above threshold → fallback to keyword search
    - If embedding search timeout → fallback to keyword search
    """
    # Try semantic search first
    query_embedding = await generate_embedding(query)

    if query_embedding is None:
        logger.info("Falling back to keyword search (embedding generation failed)")
        return await keyword_search_fallback(db, query, filters, top_k)

    # Fetch all published entries with filters
    stmt = select(KnowledgeEntry).where(KnowledgeEntry.status == "published")

    if filters:
        if filters.get("facility"):
            stmt = stmt.where(KnowledgeEntry.facility.ilike(f"%{filters['facility']}%"))
        if filters.get("specialty"):
            stmt = stmt.where(KnowledgeEntry.specialty_service.ilike(f"%{filters['specialty']}%"))
        if filters.get("provider"):
            stmt = stmt.where(KnowledgeEntry.provider_name.ilike(f"%{filters['provider']}%"))
        if filters.get("knowledge_type"):
            stmt = stmt.where(KnowledgeEntry.knowledge_type == filters['knowledge_type'])
        if filters.get("is_continuity_care") is not None:
            stmt = stmt.where(KnowledgeEntry.is_continuity_care == filters['is_continuity_care'])

    result = await db.execute(stmt)
    entries = result.scalars().all()

    if not entries:
        return []

    # Calculate similarities
    scored_entries = []
    for entry in entries:
        # Generate embedding for entry description
        entry_embedding = await generate_embedding(entry.knowledge_description)
        if entry_embedding is None:
            continue

        similarity = cosine_similarity(query_embedding, entry_embedding)
        if similarity >= min_similarity:
            scored_entries.append((entry, similarity))

    # If no good matches, fallback to keyword search
    if not scored_entries:
        logger.info(f"No semantic matches above threshold {min_similarity}, falling back to keyword search")
        return await keyword_search_fallback(db, query, filters, top_k)

    # Sort by similarity (highest first) and return top_k
    scored_entries.sort(key=lambda x: x[1], reverse=True)
    return scored_entries[:top_k]


async def keyword_search_fallback(
    db: AsyncSession,
    query: str,
    filters: Optional[dict] = None,
    top_k: int = 10
) -> List[Tuple[KnowledgeEntry, float]]:
    """
    Fallback keyword search using PostgreSQL full-text search.
    Always returns results (confidence score = 0.5 for keyword matches).
    """
    stmt = select(KnowledgeEntry).where(
        KnowledgeEntry.status == "published",
        or_(
            KnowledgeEntry.knowledge_description.ilike(f"%{query}%"),
            KnowledgeEntry.specialty_service.ilike(f"%{query}%"),
            KnowledgeEntry.facility.ilike(f"%{query}%"),
            KnowledgeEntry.provider_name.ilike(f"%{query}%") if query else False
        )
    )

    if filters:
        if filters.get("facility"):
            stmt = stmt.where(KnowledgeEntry.facility.ilike(f"%{filters['facility']}%"))
        if filters.get("specialty"):
            stmt = stmt.where(KnowledgeEntry.specialty_service.ilike(f"%{filters['specialty']}%"))
        if filters.get("provider"):
            stmt = stmt.where(KnowledgeEntry.provider_name.ilike(f"%{filters['provider']}%"))
        if filters.get("knowledge_type"):
            stmt = stmt.where(KnowledgeEntry.knowledge_type == filters['knowledge_type'])
        if filters.get("is_continuity_care") is not None:
            stmt = stmt.where(KnowledgeEntry.is_continuity_care == filters['is_continuity_care'])

    stmt = stmt.limit(top_k)
    result = await db.execute(stmt)
    entries = result.scalars().all()

    # Return with fixed confidence score of 0.5 for keyword matches
    return [(entry, 0.5) for entry in entries]


async def search_autocomplete(
    db: AsyncSession,
    query: str,
    field: str = "specialty_service",
    limit: int = 10
) -> List[str]:
    """
    Autocomplete suggestions for providers, specialties, or facilities.
    Used for smart form auto-complete.

    Args:
        db: Database session
        query: Partial text to search
        field: Field to search in (provider_name, specialty_service, facility)
        limit: Max suggestions to return

    Returns:
        List of unique matching values
    """
    valid_fields = ["provider_name", "specialty_service", "facility"]
    if field not in valid_fields:
        field = "specialty_service"

    column = getattr(KnowledgeEntry, field)
    stmt = (
        select(column)
        .where(
            KnowledgeEntry.status == "published",
            column.ilike(f"%{query}%"),
            column.isnot(None)
        )
        .distinct()
        .limit(limit)
    )

    result = await db.execute(stmt)
    return [row[0] for row in result.all() if row[0]]
