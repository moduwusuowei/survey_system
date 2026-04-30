"""Authentication schemas."""
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Register request schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_verified: bool


class TokenData(BaseModel):
    """Token data schema."""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class TokenResponse(BaseModel):
    """Token response schema."""
    code: int
    message: str
    data: TokenData


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str
