"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import HealthCheck, Response

router = APIRouter()


@router.get("/", response_model=Response[HealthCheck])
async def health_check(db: Session = Depends(get_db)) -> Response[HealthCheck]:
    """Check application health."""
    # Test database connection
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    health_data = HealthCheck(
        status="healthy",
        version=settings.VERSION,
        database=db_status
    )

    return Response(data=health_data)


@router.get("/ping")
async def ping() -> dict:
    """Simple ping endpoint."""
    return {"message": "pong"}