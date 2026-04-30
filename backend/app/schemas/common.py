"""Common response schemas."""
from datetime import datetime, UTC
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ResponseBase(BaseModel):
    """Base response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    code: int = 200
    message: str = "success"
    timestamp: datetime = datetime.now(UTC)


class Response(ResponseBase, Generic[T]):
    """Generic response schema with data."""
    data: Optional[T] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    page_size: int = 20


class PaginationInfo(BaseModel):
    """Pagination information."""
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(ResponseBase, Generic[T]):
    """Paginated response schema."""
    data: list[T]
    pagination: PaginationInfo


class ErrorResponse(ResponseBase):
    """Error response schema."""
    code: int = 400
    message: str = "error"
    errors: Optional[list[dict]] = None


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str