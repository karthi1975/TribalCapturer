"""
Specialty model representing medical specialties.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database.connection import Base


class Specialty(Base):
    """Specialty model for medical specialties."""

    __tablename__ = "specialties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    code = Column(String(50), nullable=True, unique=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    assigned_users = relationship("User", secondary="user_specialties", back_populates="assigned_specialties")
    knowledge_entries = relationship("KnowledgeEntry", back_populates="specialty")

    def __repr__(self):
        return f"<Specialty(id={self.id}, name={self.name}, is_active={self.is_active})>"
