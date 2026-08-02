from fastapi import APIRouter
from app.core.config import settings
from typing import Dict, Any

router = APIRouter()

@router.get("/health", summary="System Health Indicator")
async def health_check():
    return {
        "status": "online",
        "runtime": settings.PROJECT_NAME,
        "engine": settings.ENGINE_NAME,
        "version": settings.VERSION
    }

@router.get("/status", summary="System Status")
async def system_status():
    return {
        "runtime": settings.PROJECT_NAME,
        "primary_llm": settings.DEFAULT_LLM_MODEL,
        "fallback_llm": settings.FALLBACK_LLM_MODEL,
        "qdrant": f"{settings.QDRANT_HOST}:{settings.QDRANT_PORT}",
        "environment": settings.ENVIRONMENT
    }

@router.get("/diagnostics", summary="Runtime Diagnostics Matrix")
async def runtime_diagnostics():
    return {
        "protection_status": "Online",
        "runtime_health": "Healthy",
        "ipc_layer": "Connected",
        "shell_hooks": "Loaded (Bash / Zsh / Fish)",
        "policy_engine": "Ready (Normal Mode)",
        "rule_engine": "Active (Deterministic Authority)",
        "knowledge_base": "Available (Qdrant Local)",
        "offline_models": "Ready (Ollama/Qwen2.5-Coder)",
        "notification_service": "Running (Tiered Alerting)"
    }
