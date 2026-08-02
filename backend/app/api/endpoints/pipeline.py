from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.evaluator import risk_engine
from app.explainability.generator import explainability_engine, ExplanationReport
from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis
from app.risk.evaluator import RiskAssessment

router = APIRouter()

class PipelineRequest(BaseModel):
    command: str
    cwd: str = None

class PipelineResponse(BaseModel):
    metadata: CommandMetadata
    context: SystemContext
    intent: IntentAnalysis
    risk: RiskAssessment
    explanation: ExplanationReport

@router.post("/evaluate", response_model=PipelineResponse, summary="End-to-End ShellGuard AI Pipeline Evaluation")
async def evaluate_pipeline(request: PipelineRequest):
    """
    Executes complete ShellGuard AI security pipeline:
    Command ➔ AST Parser ➔ OS Context Telemetry ➔ Multi-Agent Intent ➔ 5-Vector Risk Engine ➔ Explainability Generator.
    """
    if not request.command or not request.command.strip():
        raise HTTPException(status_code=400, detail="Command string cannot be empty")

    # 1. AST Parser & Anti-Evasion
    metadata = command_parser.parse(request.command)

    # 2. Live OS Context Telemetry
    context = context_collector.collect_context(metadata.targets, request.cwd)

    # 3. Multi-Agent AI Intent Reasoning
    intent = await intent_engine.analyze_intent(metadata, context)

    # 4. Dynamic 5-Vector Risk Assessment
    risk = risk_engine.assess_risk(metadata, context, intent)

    # 5. Explainable Rationale & Safe Alternatives
    explanation = await explainability_engine.generate_explanation(metadata, context, intent, risk)

    return PipelineResponse(
        metadata=metadata,
        context=context,
        intent=intent,
        risk=risk,
        explanation=explanation
    )
