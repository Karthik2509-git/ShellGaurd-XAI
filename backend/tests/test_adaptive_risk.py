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
from app.runtime.rules import rule_engine

@pytest.mark.anyio
async def test_rule_engine_authority():
    meta = command_parser.parse("sudo rm -rf /")
    decision, violations = rule_engine.evaluate_rules(meta, is_root=True)
    assert decision == "BLOCK"
    assert len(violations) > 0

@pytest.mark.anyio
async def test_adaptive_risk_evaluator_evidence():
    meta = command_parser.parse("sudo rm -rf /etc")
    ctx = context_collector.collect_context(targets=["/etc"])
    intent = await intent_engine.analyze_intent(meta, ctx)

    assessment = adaptive_risk_engine.assess_risk(meta, ctx, intent)
    assert assessment.threat_level == "CRITICAL"
    assert assessment.rule_decision == "BLOCK"
    assert len(assessment.evidence) > 0
    assert len(assessment.interruption_reasons) > 0
    assert assessment.failure_likelihood == "Very High"
    assert assessment.recovery_complexity == "Critical"

@pytest.mark.anyio
async def test_impact_report_and_digital_twin():
    meta = command_parser.parse("sudo rm -rf /var/log/*")
    ctx = context_collector.collect_context(targets=["/var/log/*"])
    intent = await intent_engine.analyze_intent(meta, ctx)
    risk = adaptive_risk_engine.assess_risk(meta, ctx, intent)

    report, tree, twin = impact_report_generator.generate_report(meta, ctx, intent, risk)
    assert report.failure_likelihood in ["High", "Very High"]
    assert twin.virtual_execution_status == "SIMULATED_DESTRUCTION"
    assert len(tree) >= 3

@pytest.mark.anyio
async def test_command_rewrite_evidence_checkmarks():
    meta = command_parser.parse("rm -rf notes.txt")
    ctx = context_collector.collect_context(targets=["notes.txt"])

    rewrites = rewrite_engine.generate_rewrites(meta, ctx)
    assert len(rewrites) > 0
    assert "trash-put" in rewrites[0].safe_command
    assert len(rewrites[0].evidence_checkmarks) > 0
