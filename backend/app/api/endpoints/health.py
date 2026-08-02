from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health", summary="Service Health Check")
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@router.get("/status", summary="System Components Status")
async def system_status():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "primary_llm": settings.DEFAULT_LLM_MODEL,
        "fallback_llm": settings.FALLBACK_LLM_MODEL,
        "qdrant_host": f"{settings.QDRANT_HOST}:{settings.QDRANT_PORT}",
        "redis_host": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        "force_intercept": settings.FORCE_INTERCEPT
    }
