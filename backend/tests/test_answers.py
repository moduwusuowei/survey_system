"""Tests for answer endpoints."""
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.survey import Survey
from app.models.question import Question
from app.models.response import Response, Answer
from app.models.user import User


@pytest.fixture
def auth_headers(client: TestClient, test_user: User):
    """Get authentication headers."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "test123456"
        }
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_user(db: Session):
    """Create test user."""
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        return existing_user
    
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="$pbkdf2-sha256$29000$J9vK7hRc7eOT4w3rIvrI7Q$G9q0t8eB6Pz27e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_survey(db: Session, test_user: User):
    """Create test survey."""
    survey = Survey(
        title="Test Survey",
        description="Test survey description",
        status="published",
        is_public=True,
        creator_id=test_user.id
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


@pytest.fixture
def test_question(db: Session, test_survey: Survey):
    """Create test question."""
    question = Question(
        survey_id=test_survey.id,
        type="multiple_choice",
        title="What is your favorite color?",
        is_required=True,
        order_index=1
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def test_submit_response(client: TestClient, test_survey: Survey, test_question: Question):
    """Test submit survey response."""
    # Survey is already created by the fixture, no need to update
    response = client.post(
        "/api/v1/responses/",
        json={
            "survey_id": test_survey.id,
            "answers": [
                {
                    "question_id": test_question.id,
                    "text_answer": "Red"
                }
            ]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["survey_id"] == test_survey.id


def test_get_responses(client: TestClient, test_survey: Survey, test_question: Question, auth_headers):
    """Test get survey responses."""
    # First submit a response
    client.post(
        "/api/v1/responses/",
        json={
            "survey_id": test_survey.id,
            "answers": [
                {
                    "question_id": test_question.id,
                    "text_answer": "Red"
                }
            ]
        }
    )
    
    # Get responses
    response = client.get(f"/api/v1/responses/survey/{test_survey.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_analytics(client: TestClient, test_survey: Survey, test_question: Question, auth_headers):
    """Test get survey analytics."""
    # First submit a response
    client.post(
        "/api/v1/responses/",
        json={
            "survey_id": test_survey.id,
            "answers": [
                {
                    "question_id": test_question.id,
                    "text_answer": "Red"
                }
            ]
        }
    )
    
    # Get IP statistics
    response = client.get(f"/api/v1/responses/ip-stats/{test_survey.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total_responses" in data
    assert "unique_ips" in data
    assert "ip_details" in data