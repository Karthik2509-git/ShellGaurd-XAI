from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.context.collector import context_collector, SystemContext

router = APIRouter()

class ContextRequest(BaseModel):
    targets: List[str]
    cwd: Optional[str] = None

@router.post("/collect", response_model=SystemContext, summary="Collect System Telemetry & Impact Context")
async def collect_context(request: ContextRequest):
    """
    Collects live system telemetry, path file count, total size, 
    running service dependencies, Git state, and recoverability rating.
    """
    context = context_collector.collect_context(request.targets, request.cwd)
    return context
