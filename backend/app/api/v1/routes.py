"""API v1 routes."""
from fastapi import APIRouter

from app.api.v1 import health, auth, questionnaires, questions, roles, answers, analytics

router = APIRouter()

# Include endpoints
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(questionnaires.router, prefix="/questionnaires", tags=["questionnaires"])
router.include_router(questions.router, prefix="/questions", tags=["questions"])
router.include_router(answers.router, prefix="/responses", tags=["responses"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(roles.router, prefix="/roles", tags=["roles"])
