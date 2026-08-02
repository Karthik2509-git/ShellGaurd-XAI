import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.adaptive_evaluator import adaptive_risk_engine
from app.explainability.impact_report import impact_report_generator
from app.rewrite.engine import rewrite_engine
from app.session.tracker import session_tracker

@pytest.mark.anyio
async def test_adaptive_risk_evaluator_rm_rf():
    meta = command_parser.parse("sudo rm -rf /etc")
    ctx = context_collector.collect_context(targets=["/etc"])
    intent = await intent_engine.analyze_intent(meta, ctx)

    assessment = adaptive_risk_engine.assess_risk(meta, ctx, intent)
    assert assessment.threat_level == "CRITICAL"
    assert assessment.overall_risk_score >= 80
    assert assessment.risk_confidence == 0.98
    assert assessment.vectors.data_loss_risk >= 80.0

@pytest.mark.anyio
async def test_ai_impact_report_generator():
    meta = command_parser.parse("sudo rm -rf /var/log/*")
    ctx = context_collector.collect_context(targets=["/var/log/*"])
    intent = await intent_engine.analyze_intent(meta, ctx)
    risk = adaptive_risk_engine.assess_risk(meta, ctx, intent)

    report, tree = impact_report_generator.generate_report(meta, ctx, intent, risk)
    assert report.failure_probability >= 0.7
    assert len(tree) >= 3
    assert tree[-1].status in ["BLOCK", "WARN"]

@pytest.mark.anyio
async def test_ai_command_rewrite_engine():
    meta = command_parser.parse("chmod -R 777 project/")
    ctx = context_collector.collect_context(targets=["project/"])

    rewrites = rewrite_engine.generate_rewrites(meta, ctx)
    assert len(rewrites) > 0
    assert "755" in rewrites[0].safe_command
    assert rewrites[0].why_better_rationale != ""

@pytest.mark.anyio
async def test_session_tracker_and_timeline():
    entry = session_tracker.record_command(
        command="sudo rm -rf /boot",
        intent="Delete boot partition",
        threat_level="CRITICAL",
        overall_risk_score=95,
        action="BLOCKED"
    )
    assert entry.threat_level == "CRITICAL"
    assert entry.status_icon == "❌"
    
    score_data = session_tracker.get_user_safety_score()
    assert "score" in score_data
