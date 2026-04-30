"""Questions API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.question import Question
from app.models.survey import Survey
from app.models.user import User
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse

router = APIRouter()


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Create a new question."""
    # Check if the survey exists and belongs to the current user
    survey = db.query(Survey).filter(Survey.id == question.survey_id, Survey.creator_id == current_user.id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # Create question with correct field mapping
    question_data = question.model_dump()
    # Get current max order index for the survey
    max_order = db.query(Question).filter(Question.survey_id == question_data["survey_id"]).count()
    db_question = Question(
        survey_id=question_data["survey_id"],
        type=question_data["question_type"],
        title=question_data["question_text"],
        is_required=question_data["required"],
        order_index=max_order + 1,
        config={
            "options": question_data.get("options"),
            "min_value": question_data.get("min_value"),
            "max_value": question_data.get("max_value")
        }
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.get("/survey/{survey_id}", response_model=List[QuestionResponse])
async def get_questions_by_survey(survey_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get all questions for a survey."""
    # Check if the survey exists and belongs to the current user
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.creator_id == current_user.id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    questions = db.query(Question).filter(Question.survey_id == survey_id).order_by(Question.order_index).all()
    return questions


@router.get("/public/survey/{survey_id}", response_model=List[QuestionResponse])
async def get_public_questions_by_survey(survey_id: int, db: Session = Depends(get_db)):
    """Get all questions for a public survey (no authentication required)."""
    # Check if the survey exists and is public
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.status == "published", Survey.is_public == True).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found or not public"
        )
    
    questions = db.query(Question).filter(Question.survey_id == survey_id).order_by(Question.order_index).all()
    return questions


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get a question by ID."""
    question = db.query(Question).join(Survey).filter(Question.id == question_id, Survey.creator_id == current_user.id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question: QuestionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Update a question."""
    # Check if the question exists and belongs to the current user
    db_question = db.query(Question).join(Survey).filter(Question.id == question_id, Survey.creator_id == current_user.id).first()
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # If survey_id is being updated, check if the new survey exists and belongs to the current user
    update_data = question.model_dump(exclude_unset=True)
    if "survey_id" in update_data:
        survey = db.query(Survey).filter(Survey.id == update_data["survey_id"], Survey.creator_id == current_user.id).first()
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
    
    if "question_text" in update_data:
        db_question.title = update_data.pop("question_text")
    
    if "question_type" in update_data:
        db_question.type = update_data.pop("question_type")
    
    if "required" in update_data:
        db_question.is_required = update_data.pop("required")
    
    # Update config fields
    if any(key in update_data for key in ["options", "min_value", "max_value"]):
        if not db_question.config:
            db_question.config = {}
        
        if "options" in update_data:
            db_question.config["options"] = update_data.pop("options")
        
        if "min_value" in update_data:
            db_question.config["min_value"] = update_data.pop("min_value")
        
        if "max_value" in update_data:
            db_question.config["max_value"] = update_data.pop("max_value")
    
    # Update remaining fields
    for field, value in update_data.items():
        setattr(db_question, field, value)
    
    db.commit()
    db.refresh(db_question)
    return db_question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete a question."""
    question = db.query(Question).join(Survey).filter(Question.id == question_id, Survey.creator_id == current_user.id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    db.delete(question)
    db.commit()
    return None
