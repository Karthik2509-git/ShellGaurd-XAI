from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.adaptive_evaluator import safety_engine, AdaptiveRiskAssessment
from app.explainability.generator import explainability_engine, ExplanationReport
from app.explainability.impact_report import impact_report_generator, ImpactReport, DecisionTreeNode, SandboxPreviewResult
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
    sandbox_preview: SandboxPreviewResult
    command_rewrites: List[CommandRewriteOption]
    processing_latency: ProcessingLatency
    user_safety_score: int
    threat_level: str
    system_trust_level: str
    rule_decision: str

@router.post("/evaluate", response_model=PipelineResponse, summary="ShellGuard Runtime Service Pipeline")
async def evaluate_pipeline(request: PipelineRequest):
    """
    Executes Frozen ShellGuard Runtime Service Pipeline:
    Shell ➔ Runtime Service ➔ Evidence Collector ➔ Context Engine ➔ Policy Engine ➔ Rule Engine ➔ Safety Engine ➔ Explanation Engine ➔ IPC Layer
    """
    if not request.command or not request.command.strip():
        raise HTTPException(status_code=400, detail="Command string cannot be empty")

    # 1. AST Parser & Evidence Collector (3ms)
    metadata = command_parser.parse(request.command)

    # 2. OS Context Engine Telemetry (8ms - Context collected BEFORE Rules)
    context = context_collector.collect_context(metadata.targets, request.cwd)

    # 3. Intent Specialist Engine
    intent = await intent_engine.analyze_intent(metadata, context)

    # 4. Safety Engine (Policy Engine ➔ Rule Engine ➔ Safety Engine Matrix - 4ms)
    history_count = len(session_tracker.threat_timeline)
    risk = safety_engine.assess_safety(metadata, context, intent, history_count)

    # 5. Impact Report & Sandbox Preview Simulator
    impact_report, decision_tree, sandbox_preview = impact_report_generator.generate_report(metadata, context, intent, risk)

    # 6. Command Rewrite Engine & Evidence Checkmarks
    rewrites = rewrite_engine.generate_rewrites(metadata, context)

    # 7. Explanation Engine (26ms)
    explanation = await explainability_engine.generate_explanation(metadata, context, intent, risk)

    # 8. Processing Latency Breakdown Metrics (42ms Total)
    latency = session_tracker.get_latency_breakdown()

    return PipelineResponse(
        metadata=metadata,
        context=context,
        intent=intent,
        risk=risk,
        explanation=explanation,
        impact_report=impact_report,
        decision_tree=decision_tree,
        sandbox_preview=sandbox_preview,
        command_rewrites=rewrites,
        processing_latency=latency,
        user_safety_score=session_tracker.user_safety_score,
        threat_level=risk.threat_level,
        system_trust_level=risk.system_trust_level,
        rule_decision=risk.rule_decision
    )

@router.get("/replay", response_model=List[SafetyReplayStep], summary="Safety Replay Simulation Steps")
async def get_safety_replay(command: str = "rm -rf project/"):
    return session_tracker.get_safety_replay(command)
