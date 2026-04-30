"""Response schemas."""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class AnswerCreate(BaseModel):
    """Answer create schema."""
    question_id: int
    text_answer: Optional[str] = None
    rating_value: Optional[int] = None


class AnswerResponse(BaseModel):
    """Answer response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    question_id: int
    text_answer: Optional[str] = None
    rating_value: Optional[int] = None
    created_at: datetime


class ResponseCreate(BaseModel):
    """Response create schema."""
    survey_id: int
    respondent_email: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    answers: List[AnswerCreate]


class ResponseResponse(BaseModel):
    """Response response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    survey_id: int
    respondent_email: Optional[str] = None
    is_complete: bool
    duration_seconds: Optional[int] = None
    created_at: datetime
    answers: List[AnswerResponse]