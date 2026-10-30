from fastapi import APIRouter
from app.db.database import engine
from app.core.config import settings

router = APIRouter()

@router.get("/health")
def check_health():
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "database": engine.dialect.name,
        "llm_configured": bool(settings.LLM_API_KEY)
    }

