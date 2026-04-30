"""Survey model."""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime, UTC

from app.core.database import Base


class SurveyStatus(str, PyEnum):
    """Survey status enum."""
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Survey(Base):
    """Survey model."""
    
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(SurveyStatus), default=SurveyStatus.DRAFT, nullable=False)
    is_public = Column(Boolean, default=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    max_responses = Column(Integer)
    allow_multiple = Column(Boolean, default=False)
    share_token = Column(String(100), unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    creator = relationship("User", back_populates="surveys")
    questions = relationship("Question", back_populates="survey", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="survey", cascade="all, delete-orphan")
