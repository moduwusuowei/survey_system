"""Questionnaire/ Survey API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, UTC

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.survey import Survey
from app.models.question import Question
from app.models.user import User
from app.schemas.survey import SurveyCreate, SurveyUpdate, SurveyResponse
from app.schemas.question import QuestionResponse
from app.api.v1.answers import router as answers_router

router = APIRouter()


@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(survey: SurveyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create a new survey."""
    # Extract questions from survey data
    questions_data = survey.questions or []
    # Remove questions from survey data since it's not a field in Survey model
    survey_data = survey.model_dump()
    survey_data.pop("questions", None)
    survey_data["creator_id"] = current_user.id
    
    # Create survey
    db_survey = Survey(**survey_data)
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    
    # Create questions
    for i, question_data in enumerate(questions_data):
        question = Question(
            survey_id=db_survey.id,
            order_index=i,
            type=question_data.get("question_type"),
            title=question_data.get("question_text"),
            is_required=question_data.get("required", False),
            config={
                "options": question_data.get("options"),
                "min_value": question_data.get("min_value"),
                "max_value": question_data.get("max_value")
            }
        )
        db.add(question)
    
    db.commit()
    return db_survey


@router.get("/", response_model=List[SurveyResponse])
async def get_surveys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get all surveys for current user."""
    surveys = db.query(Survey).filter(Survey.creator_id == current_user.id).offset(skip).limit(limit).all()
    return surveys


@router.get("/{survey_id}", response_model=SurveyResponse)
async def get_survey(survey_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get a survey by ID."""
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.creator_id == current_user.id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    return survey


@router.put("/{survey_id}", response_model=SurveyResponse)
async def update_survey(survey_id: int, survey: SurveyUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Update a survey."""
    db_survey = db.query(Survey).filter(Survey.id == survey_id, Survey.creator_id == current_user.id).first()
    if not db_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # Remove questions from survey data since we don't want to delete/recreate questions
    update_data = survey.model_dump(exclude_unset=True)
    update_data.pop("questions", None)
    
    # Update survey fields
    for field, value in update_data.items():
        setattr(db_survey, field, value)
    
    db.commit()
    db.refresh(db_survey)
    return db_survey


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(survey_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete a survey."""
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.creator_id == current_user.id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # Delete associated questions
    db.query(Question).filter(Question.survey_id == survey_id).delete()
    
    db.delete(survey)
    db.commit()
    return None


@router.get("/public/{survey_id}", response_model=SurveyResponse)
async def get_public_survey(survey_id: int, db: Session = Depends(get_db)):
    """Get a public survey by ID (no authentication required)."""
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.status == "published", Survey.is_public == True).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found or not public"
        )
    
    now = datetime.now(UTC)
    
    if survey.start_date and now < survey.start_date:
        return JSONResponse(
            status_code=403,
            content={
                "detail": "not_started",
                "message": f"问卷还未开始，将于 {survey.start_date.strftime('%Y-%m-%d %H:%M')} 开始"
            }
        )
    
    if survey.end_date and now > survey.end_date:
        return JSONResponse(
            status_code=403,
            content={
                "detail": "expired",
                "message": "问卷已过期，感谢您的关注"
            }
        )
    
    return survey
