from fastapi import APIRouter
from pydantic import BaseModel
from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis
from app.risk.evaluator import risk_engine, RiskAssessment

router = APIRouter()

class RiskRequest(BaseModel):
    metadata: CommandMetadata
    context: SystemContext
    intent: IntentAnalysis

@router.post("/assess", response_model=RiskAssessment, summary="Compute Dynamic 5-Vector Risk Assessment")
async def assess_risk(request: RiskRequest):
    """
    Computes 0-100 dynamic risk score, vector breakdowns (Data Loss, System Stability, 
    Security Escalation, Service Downtime, Recoverability), and confirmation requirement.
    """
    assessment = risk_engine.assess_risk(request.metadata, request.context, request.intent)
    return assessment
