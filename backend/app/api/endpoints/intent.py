from fastapi import APIRouter
from pydantic import BaseModel
from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import intent_engine, IntentAnalysis

router = APIRouter()

class IntentRequest(BaseModel):
    metadata: CommandMetadata
    context: SystemContext

@router.post("/analyze", response_model=IntentAnalysis, summary="Multi-Agent AI Intent Reasoning")
async def analyze_intent(request: IntentRequest):
    """
    Analyzes true operational intent, predicts side effects, 
    and checks intent-vs-impact alignment using Multi-Agent AI.
    """
    analysis = await intent_engine.analyze_intent(request.metadata, request.context)
    return analysis
