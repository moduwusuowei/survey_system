"""Tests for authentication endpoints."""
import pytest
from sqlalchemy.orm import Session

from app.models.user import User


@pytest.fixture
def test_user(db: Session):
    """Create test user."""
    # First, check if user already exists to avoid UNIQUE constraint error
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        return existing_user
    
    # Create a new user with a valid pbkdf2_sha256 hash for "testpassword123"
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


def test_register(client, db: Session):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password1234"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "Registration successful"
    assert "access_token" in data["data"]


def test_login(client, test_user: User):
    """Test user login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "Login successful"
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401


def test_refresh_token(client, test_user: User):
    """Test refresh token."""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    refresh_token = login_response.json()["data"]["refresh_token"]
    
    # Test refresh token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    print("Refresh token response:", refresh_response.json())
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert data["code"] == 200
    assert data["message"] == "Token refreshed"
    assert "access_token" in data["data"]
