from fastapi import APIRouter
from pydantic import BaseModel
from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis
from app.risk.evaluator import RiskAssessment
from app.explainability.generator import explainability_engine, ExplanationReport

router = APIRouter()

class ExplainRequest(BaseModel):
    metadata: CommandMetadata
    context: SystemContext
    intent: IntentAnalysis
    risk: RiskAssessment

@router.post("/generate", response_model=ExplanationReport, summary="Generate Explainable Rationale & Safe Alternatives")
async def generate_explanation(request: ExplainRequest):
    """
    Generates Technical Rationale, ELI5 Summary, why-dangerous bullet points, 
    safe command alternatives, and undo/remediation playbook.
    """
    report = await explainability_engine.generate_explanation(
        request.metadata, request.context, request.intent, request.risk
    )
    return report
