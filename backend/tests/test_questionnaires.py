"""Tests for questionnaire endpoints."""
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


def test_create_survey(client: TestClient, auth_headers):
    """Test create survey."""
    response = client.post(
        "/api/v1/questionnaires/",
        json={
            "title": "New Survey",
            "description": "New survey description",
            "status": "draft",
            "is_public": True
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Survey"
    assert data["description"] == "New survey description"


def test_get_surveys(client: TestClient, auth_headers, test_survey: Survey):
    """Test get surveys."""
    response = client.get("/api/v1/questionnaires/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_get_survey(client: TestClient, auth_headers, test_survey: Survey):
    """Test get single survey."""
    response = client.get(f"/api/v1/questionnaires/{test_survey.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_survey.id
    assert data["title"] == test_survey.title


def test_update_survey(client: TestClient, auth_headers, test_survey: Survey):
    """Test update survey."""
    response = client.put(
        f"/api/v1/questionnaires/{test_survey.id}",
        json={
            "title": "Updated Survey",
            "description": "Updated survey description"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Survey"
    assert data["description"] == "Updated survey description"


def test_delete_survey(client: TestClient, auth_headers, test_survey: Survey):
    """Test delete survey."""
    response = client.delete(f"/api/v1/questionnaires/{test_survey.id}", headers=auth_headers)
    
    assert response.status_code == 204


def test_get_public_survey(client: TestClient, test_survey: Survey, db: Session):
    """Test get public survey."""
    # Update survey to published and public
    survey = db.query(Survey).filter(Survey.id == test_survey.id).first()
    survey.status = "published"
    survey.is_public = True
    db.commit()
    
    response = client.get(f"/api/v1/questionnaires/public/{test_survey.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_survey.title