"""Tests for question endpoints."""
import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.survey import Survey
from app.models.question import Question
from app.models.user import User


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
        status="draft",
        is_public=True,
        creator_id=test_user.id
    )
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


@pytest.fixture
def auth_headers(client: TestClient, test_user: User):
    """Get authentication headers."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_question(client: TestClient, auth_headers, test_survey: Survey):
    """Test create question."""
    response = client.post(
        "/api/v1/questions/",
        json={
            "survey_id": test_survey.id,
            "question_type": "multiple_choice",
            "question_text": "What is your favorite color?",
            "options": ["Red", "Green", "Blue"],
            "required": True
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["question_text"] == "What is your favorite color?"
    assert data["question_type"] == "multiple_choice"


def test_get_questions(client: TestClient, auth_headers, test_survey: Survey):
    """Test get questions for a survey."""
    # First create a question
    client.post(
        "/api/v1/questions/",
        json={
            "survey_id": test_survey.id,
            "question_type": "multiple_choice",
            "question_text": "What is your favorite color?",
            "options": ["Red", "Green", "Blue"],
            "required": True
        },
        headers=auth_headers
    )
    
    # Get questions
    response = client.get(f"/api/v1/questions/survey/{test_survey.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_update_question(client: TestClient, auth_headers, test_survey: Survey):
    """Test update question."""
    # Create a question
    create_response = client.post(
        "/api/v1/questions/",
        json={
            "survey_id": test_survey.id,
            "question_type": "multiple_choice",
            "question_text": "What is your favorite color?",
            "options": ["Red", "Green", "Blue"],
            "required": True
        },
        headers=auth_headers
    )
    
    question_id = create_response.json()["id"]
    
    # Update the question
    response = client.put(
        f"/api/v1/questions/{question_id}",
        json={
            "question_text": "What is your favorite color? (Updated)",
            "options": ["Red", "Green", "Blue", "Yellow"]
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question_text"] == "What is your favorite color? (Updated)"


def test_delete_question(client: TestClient, auth_headers, test_survey: Survey):
    """Test delete question."""
    # Create a question
    create_response = client.post(
        "/api/v1/questions/",
        json={
            "survey_id": test_survey.id,
            "question_type": "multiple_choice",
            "question_text": "What is your favorite color?",
            "options": ["Red", "Green", "Blue"],
            "required": True
        },
        headers=auth_headers
    )
    
    question_id = create_response.json()["id"]
    
    # Delete the question
    response = client.delete(f"/api/v1/questions/{question_id}", headers=auth_headers)
    
    assert response.status_code == 204