"""Response model for survey answers."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from app.core.database import Base


class Response(Base):
    """Survey response model."""
    
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    respondent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    respondent_email = Column(String(255))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    is_complete = Column(Boolean, default=False)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    survey = relationship("Survey", back_populates="responses")
    respondent = relationship("User", back_populates="responses")
    answers = relationship("Answer", back_populates="response", cascade="all, delete-orphan")


class Answer(Base):
    """Answer model for individual question responses."""
    
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_ids = Column(Integer, nullable=True)
    text_answer = Column(Text)
    rating_value = Column(Integer)
    matrix_answers = Column(Text)  # JSON string
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    response = relationship("Response", back_populates="answers")
    question = relationship("Question", back_populates="answers")
