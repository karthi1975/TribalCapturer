"""
User model representing system users (MAs and Creators).
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database.connection import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    MA = "MA"
    CREATOR = "Creator"


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    assigned_facilities = relationship("Facility", secondary="user_facilities", back_populates="assigned_users")
    assigned_specialties = relationship("Specialty", secondary="user_specialties", back_populates="assigned_users")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
