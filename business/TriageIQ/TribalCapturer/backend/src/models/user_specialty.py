"""
UserSpecialty association table for many-to-many relationship between users and specialties.
"""
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..database.connection import Base


class UserSpecialty(Base):
    """Association table linking users to specialties."""

    __tablename__ = "user_specialties"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    specialty_id = Column(UUID(as_uuid=True), ForeignKey("specialties.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    def __repr__(self):
        return f"<UserSpecialty(user_id={self.user_id}, specialty_id={self.specialty_id})>"
