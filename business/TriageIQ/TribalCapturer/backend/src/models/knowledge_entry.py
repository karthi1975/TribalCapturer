"""
KnowledgeEntry model representing tribal knowledge submissions.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database.connection import Base


class EntryStatus(str, enum.Enum):
    """Knowledge entry status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"


class KnowledgeType(str, enum.Enum):
    """Knowledge entry type/category for AI routing."""
    DIAGNOSIS_SPECIALTY = "diagnosis_specialty"  # Diagnosis → Specialty Referral
    PROVIDER_PREFERENCE = "provider_preference"  # Provider-specific preferences
    CONTINUITY_CARE = "continuity_care"  # Continuity of care rules
    PRE_VISIT_REQUIREMENT = "pre_visit_requirement"  # Pre-appointment requirements
    SCHEDULING_WORKFLOW = "scheduling_workflow"  # Scheduling workflow tips
    GENERAL_KNOWLEDGE = "general_knowledge"  # General tribal knowledge


class KnowledgeEntry(Base):
    """KnowledgeEntry model for storing tribal knowledge."""

    __tablename__ = "knowledge_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    ma_name = Column(String(255), nullable=False)  # Denormalized for audit trail

    # NEW: Foreign key relationships (migration will populate these)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="RESTRICT"), nullable=True, index=True)
    specialty_id = Column(UUID(as_uuid=True), ForeignKey("specialties.id", ondelete="RESTRICT"), nullable=True, index=True)

    # OLD: Keep for migration compatibility (will be removed in future migration)
    facility = Column(String(255), nullable=False, index=True)
    specialty_service = Column(String(255), nullable=False, index=True)

    # NEW: Provider and knowledge categorization
    provider_name = Column(String(255), nullable=True, index=True)  # Optional: specific provider
    knowledge_type = Column(
        SQLEnum(KnowledgeType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default="general_knowledge",
        index=True
    )
    is_continuity_care = Column(Boolean, nullable=False, default=False)  # Continuity of care flag

    knowledge_description = Column(Text, nullable=False)
    status = Column(SQLEnum(EntryStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default="published", index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    # Relationships
    facility_rel = relationship("Facility", back_populates="knowledge_entries")
    specialty_rel = relationship("Specialty", back_populates="knowledge_entries")

    def __repr__(self):
        return f"<KnowledgeEntry(id={self.id}, ma_name={self.ma_name}, facility={self.facility})>"
