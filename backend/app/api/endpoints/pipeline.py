from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.adaptive_evaluator import adaptive_risk_engine, AdaptiveRiskAssessment
from app.explainability.generator import explainability_engine, ExplanationReport
from app.explainability.impact_report import impact_report_generator, ImpactReport, DecisionTreeNode, DigitalTwinResult
from app.rewrite.engine import rewrite_engine, CommandRewriteOption
from app.session.tracker import session_tracker, ProcessingLatency, SafetyReplayStep
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
    impact_report: ImpactReport
    decision_tree: List[DecisionTreeNode]
    digital_twin: DigitalTwinResult
    command_rewrites: List[CommandRewriteOption]
    processing_latency: ProcessingLatency
    user_safety_score: int
    threat_level: str
    rule_decision: str

@router.post("/evaluate", response_model=PipelineResponse, summary="ShellGuard Runtime Safety Pipeline")
async def evaluate_pipeline(request: PipelineRequest):
    """
    Executes full ShellGuard Runtime safety evaluation:
    AST Anti-Evasion Parser ➔ OS Telemetry ➔ Rule Engine Authority ➔ Intent Classifier ➔ 
    Adaptive Risk ➔ Impact Report ➔ Digital Twin ➔ Command Rewrites & Latency Breakdown.
    """
    if not request.command or not request.command.strip():
        raise HTTPException(status_code=400, detail="Command string cannot be empty")

    # 1. AST Parser & Anti-Evasion (3ms)
    metadata = command_parser.parse(request.command)

    # 2. Live OS Context Telemetry (8ms)
    context = context_collector.collect_context(metadata.targets, request.cwd)

    # 3. Multi-Agent Intent Classifier (Evidence-Based)
    intent = await intent_engine.analyze_intent(metadata, context)

    # 4. Adaptive Risk Assessment & Rule Engine Authority (4ms)
    history_count = len(session_tracker.threat_timeline)
    risk = adaptive_risk_engine.assess_risk(metadata, context, intent, history_count)

    # 5. Impact Report, Decision Tree & Digital Twin Simulator
    impact_report, decision_tree, digital_twin = impact_report_generator.generate_report(metadata, context, intent, risk)

    # 6. Command Rewrite Engine & Why-Selected Evidence Checkmarks
    rewrites = rewrite_engine.generate_rewrites(metadata, context)

    # 7. Dual Rationale Explanation Report (26ms)
    explanation = await explainability_engine.generate_explanation(metadata, context, intent, risk)

    # 8. Processing Latency Metrics (42ms Total)
    latency = session_tracker.get_latency_breakdown()

    return PipelineResponse(
        metadata=metadata,
        context=context,
        intent=intent,
        risk=risk,
        explanation=explanation,
        impact_report=impact_report,
        decision_tree=decision_tree,
        digital_twin=digital_twin,
        command_rewrites=rewrites,
        processing_latency=latency,
        user_safety_score=session_tracker.user_safety_score,
        threat_level=risk.threat_level,
        rule_decision=risk.rule_decision
    )

@router.get("/replay", response_model=List[SafetyReplayStep], summary="Safety Replay Cyber-Attack Simulation Steps")
async def get_safety_replay(command: str = "rm -rf project/"):
    return session_tracker.get_safety_replay(command)
