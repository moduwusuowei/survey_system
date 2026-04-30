"""Question model."""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON, Enum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime, UTC

from app.core.database import Base


class QuestionType(str, PyEnum):
    """Question type enum."""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    DROPDOWN = "dropdown"
    RATING = "rating"
    MATRIX_SINGLE = "matrix_single"
    MATRIX_MULTIPLE = "matrix_multiple"


class Question(Base):
    """Question model."""
    
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    type = Column(Enum(QuestionType), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    is_required = Column(Boolean, default=False)
    order_index = Column(Integer, nullable=False)
    config = Column(JSON, default=dict)
    logic_rules = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    survey = relationship("Survey", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="question")


class Option(Base):
    """Option model for questions."""
    
    __tablename__ = "options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)
    score = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    question = relationship("Question", back_populates="options")
