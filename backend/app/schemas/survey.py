"""Survey schemas."""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class SurveyStatus(str, Enum):
    """Survey status enum."""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"


class SurveyBase(BaseModel):
    """Survey base schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: SurveyStatus = SurveyStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_public: bool = True


class SurveyCreate(SurveyBase):
    """Survey create schema."""
    questions: Optional[List[Dict[str, Any]]] = None


class SurveyUpdate(BaseModel):
    """Survey update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[SurveyStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_public: Optional[bool] = None
    questions: Optional[List[Dict[str, Any]]] = None


class SurveyResponse(SurveyBase):
    """Survey response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    creator_id: int
