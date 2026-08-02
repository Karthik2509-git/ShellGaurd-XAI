from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.adaptive_evaluator import adaptive_risk_engine, AdaptiveRiskAssessment
from app.explainability.generator import explainability_engine, ExplanationReport
from app.explainability.impact_report import impact_report_generator, AIImpactReport, DecisionTreeNode
from app.rewrite.engine import rewrite_engine, CommandRewriteOption
from app.session.tracker import session_tracker
from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis

router = APIRouter()

class PipelineRequest(BaseModel):
    command: str
    cwd: Optional[str] = None

class PipelineResponse(BaseModel):
    metadata: CommandMetadata
    context: SystemContext
    intent: IntentAnalysis
    risk: AdaptiveRiskAssessment
    explanation: ExplanationReport
    ai_impact_report: AIImpactReport
    decision_tree: List[DecisionTreeNode]
    ai_command_rewrites: List[CommandRewriteOption]
    user_safety_score: int
    threat_level: str

@router.post("/evaluate", response_model=PipelineResponse, summary="End-to-End ShellGuard Runtime Evaluation")
async def evaluate_pipeline(request: PipelineRequest):
    """
    Executes full ShellGuard Runtime safety evaluation:
    AST Anti-Evasion Parser ➔ OS Context Telemetry ➔ Multi-Agent Intent ➔ Adaptive 5-Category Risk Engine ➔ 
    AI Impact Report ➔ AI Decision Tree ➔ ✨ AI Command Rewrites & Why-Better Rationales.
    """
    if not request.command or not request.command.strip():
        raise HTTPException(status_code=400, detail="Command string cannot be empty")

    # 1. AST Parser & Anti-Evasion
    metadata = command_parser.parse(request.command)

    # 2. Live OS Context Telemetry
    context = context_collector.collect_context(metadata.targets, request.cwd)

    # 3. Multi-Agent Intent Classifier
    intent = await intent_engine.analyze_intent(metadata, context)

    # 4. Adaptive Risk Assessment (5 Categories & 4 Threat Tiers)
    history_count = len(session_tracker.threat_timeline)
    risk = adaptive_risk_engine.assess_risk(metadata, context, intent, history_count)

    # 5. AI Impact Report & Decision Tree Generator
    impact_report, decision_tree = impact_report_generator.generate_report(metadata, context, intent, risk)

    # 6. ✨ AI Command Rewrite Engine & "Backup First" Generator
    rewrites = rewrite_engine.generate_rewrites(metadata, context)

    # 7. Dual Rationale Explanation Report
    explanation = await explainability_engine.generate_explanation(metadata, context, intent, risk)

    # Record in Session Threat Timeline
    session_tracker.record_command(
        command=metadata.clean_command,
        intent=intent.user_intent,
        threat_level=risk.threat_level,
        overall_risk_score=risk.overall_risk_score,
        action="BLOCKED" if risk.requires_confirmation else "EXECUTED"
    )

    return PipelineResponse(
        metadata=metadata,
        context=context,
        intent=intent,
        risk=risk,
        explanation=explanation,
        ai_impact_report=impact_report,
        decision_tree=decision_tree,
        ai_command_rewrites=rewrites,
        user_safety_score=session_tracker.user_safety_score,
        threat_level=risk.threat_level
    )
