"""Answers API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, UTC

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.response import Response, Answer
from app.models.survey import Survey
from app.models.user import User
from app.schemas.response import ResponseCreate, ResponseResponse, AnswerCreate

router = APIRouter()


def get_client_ip(request: Request):
    """Get client IP from request headers."""
    # Check for forwarded IP (when behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection
    if request.client:
        return request.client.host
    
    return "未知"


@router.post("/", response_model=ResponseResponse, status_code=status.HTTP_201_CREATED)
async def create_response(response: ResponseCreate, request: Request, db: Session = Depends(get_db)):
    """Create a new survey response."""
    # Check if the survey exists and is public
    survey = db.query(Survey).filter(Survey.id == response.survey_id, Survey.status == "published", Survey.is_public == True).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found or not public"
        )
    
    # Create response with auto-detected IP
    db_response = Response(
        survey_id=response.survey_id,
        respondent_email=response.respondent_email,
        ip_address=get_client_ip(request),
        user_agent=response.user_agent,
        started_at=datetime.now(UTC),
        is_complete=False
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    
    # Create answers
    for answer_data in response.answers:
        db_answer = Answer(
            response_id=db_response.id,
            question_id=answer_data.question_id,
            text_answer=answer_data.text_answer,
            rating_value=answer_data.rating_value
        )
        db.add(db_answer)
    
    db.commit()
    db.refresh(db_response)
    
    # Update response as complete
    db_response.completed_at = datetime.now(UTC)
    db_response.is_complete = True
    # Calculate duration - ensure both times are timezone-aware
    if db_response.completed_at and db_response.started_at:
        # If started_at is naive, make it aware
        if db_response.started_at.tzinfo is None:
            from datetime import timezone
            db_response.started_at = db_response.started_at.replace(tzinfo=timezone.utc)
        # If completed_at is naive, make it aware
        if db_response.completed_at.tzinfo is None:
            from datetime import timezone
            db_response.completed_at = db_response.completed_at.replace(tzinfo=timezone.utc)
        db_response.duration_seconds = int((db_response.completed_at - db_response.started_at).total_seconds())
    db.commit()
    db.refresh(db_response)
    
    return db_response


@router.get("/survey/{survey_id}", response_model=List[ResponseResponse])
async def get_survey_responses(survey_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get all responses for a survey."""
    # Check if the survey exists and belongs to the current user
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.creator_id == current_user.id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # Get responses
    responses = db.query(Response).filter(Response.survey_id == survey_id, Response.is_complete == True).all()
    return responses


@router.get("/count/{survey_id}")
async def get_survey_response_count(survey_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get the number of responses for a survey."""
    # Check if the survey exists and belongs to the current user
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.creator_id == current_user.id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # Get response count
    count = db.query(Response).filter(Response.survey_id == survey_id, Response.is_complete == True).count()
    return {"count": count}


@router.get("/total/count")
async def get_total_response_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get the total number of responses for all surveys of the current user."""
    # Get all surveys of the current user
    surveys = db.query(Survey).filter(Survey.creator_id == current_user.id).all()
    survey_ids = [survey.id for survey in surveys]
    
    # Get total response count
    count = db.query(Response).filter(Response.survey_id.in_(survey_ids), Response.is_complete == True).count()
    return {"count": count}


@router.get("/ip-stats/{survey_id}")
async def get_survey_ip_stats(survey_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get IP statistics for a survey."""
    # Check if the survey exists and belongs to the current user
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.creator_id == current_user.id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # Get all responses with IP addresses
    responses = db.query(Response).filter(
        Response.survey_id == survey_id, 
        Response.is_complete == True
    ).all()
    
    # Calculate IP statistics
    ip_counts = {}
    for response in responses:
        ip = response.ip_address or "未知"
        if ip in ip_counts:
            ip_counts[ip] += 1
        else:
            ip_counts[ip] = 1
    
    # Build IP details list
    ip_details = [
        {"ip": ip, "count": count}
        for ip, count in ip_counts.items()
    ]
    # Sort by count descending
    ip_details.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "total_responses": len(responses),
        "unique_ips": len(ip_counts),
        "ip_details": ip_details
    }


@router.get("/time-stats/{survey_id}")
async def get_survey_time_stats(survey_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get time-based statistics for a survey."""
    # Check if the survey exists and belongs to the current user
    survey = db.query(Survey).filter(Survey.id == survey_id, Survey.creator_id == current_user.id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # Get all completed responses
    responses = db.query(Response).filter(
        Response.survey_id == survey_id, 
        Response.is_complete == True
    ).order_by(Response.created_at).all()
    
    if not responses:
        return {
            "hourly_stats": [],
            "daily_stats": []
        }
    
    # Hourly statistics (group by hour)
    hourly_counts = {}
    for response in responses:
        hour_key = response.created_at.strftime("%H:00")
        if hour_key in hourly_counts:
            hourly_counts[hour_key] += 1
        else:
            hourly_counts[hour_key] = 1
    
    hourly_stats = [
        {"hour": hour, "count": count}
        for hour, count in sorted(hourly_counts.items())
    ]
    
    # Daily statistics (group by date)
    daily_counts = {}
    for response in responses:
        date_key = response.created_at.strftime("%Y-%m-%d")
        if date_key in daily_counts:
            daily_counts[date_key] += 1
        else:
            daily_counts[date_key] = 1
    
    daily_stats = [
        {"date": date, "count": count}
        for date, count in sorted(daily_counts.items())
    ]
    
    return {
        "hourly_stats": hourly_stats,
        "daily_stats": daily_stats
    }