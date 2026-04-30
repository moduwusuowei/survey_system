"""Question schemas."""
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum


class QuestionType(str, Enum):
    """Question type enum."""
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    RATING = "rating"
    DATE = "date"
    TIME = "time"


class QuestionBase(BaseModel):
    """Question base schema."""
    survey_id: int
    question_text: str = Field(..., min_length=1, max_length=500)
    question_type: QuestionType
    required: bool = True
    options: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    default_value: Optional[str] = None
    
    @field_validator('question_type', mode='before')
    @classmethod
    def validate_question_type(cls, v):
        """Validate question type."""
        if isinstance(v, str):
            return v.lower()
        return v


class QuestionCreate(QuestionBase):
    """Question create schema."""
    pass


class QuestionUpdate(BaseModel):
    """Question update schema."""
    question_text: Optional[str] = Field(None, min_length=1, max_length=500)
    question_type: Optional[QuestionType] = None
    required: Optional[bool] = None
    options: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    default_value: Optional[str] = None


class QuestionResponse(QuestionBase):
    """Question response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    
    @model_validator(mode='before')
    @classmethod
    def validate_orm(cls, v):
        """Validate ORM object."""
        if hasattr(v, '__dict__'):
            # Handle ORM object
            obj = v
            return {
                "id": obj.id,
                "survey_id": obj.survey_id,
                "question_text": obj.title,
                "question_type": obj.type,
                "required": obj.is_required,
                "options": obj.config.get("options") if obj.config else None,
                "min_value": obj.config.get("min_value") if obj.config else None,
                "max_value": obj.config.get("max_value") if obj.config else None,
                "default_value": None,
                "created_at": obj.created_at,
                "updated_at": obj.updated_at
            }
        return v
