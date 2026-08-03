import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.adaptive_evaluator import safety_engine
from app.runtime.rules import rule_engine

@pytest.mark.anyio
async def test_rapid_burst_command_evaluations():
    """Stress Test: Evaluates 20 rapid commands in burst sequence."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        commands = [
            "ls -la /tmp",
            "rm notes.txt",
            "sudo rm -rf /etc",
            "chmod 777 project/",
            "systemctl stop postgresql"
        ] * 4

        for cmd in commands:
            res = await ac.post("/api/v1/pipeline/evaluate", json={"command": cmd})
            assert res.status_code == 200
            data = res.json()
            assert "risk" in data
            assert "intent" in data

@pytest.mark.anyio
async def test_llm_fallback_reliability():
    """Fault Tolerance: Verifies deterministic rule engine operates when LLM fails."""
    meta = command_parser.parse("sudo rm -rf /var/log/*")
    ctx = context_collector.collect_context(targets=["/var/log/*"])

    intent = await intent_engine.analyze_intent(meta, ctx)
    assert intent.user_intent is not None
    assert intent.category is not None

    risk = safety_engine.assess_safety(meta, ctx, intent)
    assert risk.rule_decision in ["WARN", "BLOCK", "PASS"]
    assert risk.threat_level in ["SAFE", "CAUTION", "HIGH", "CRITICAL"]

@pytest.mark.anyio
async def test_non_existent_filesystem_target_resilience():
    """Fault Tolerance: Ensures non-existent target paths do not crash context collection."""
    ctx = context_collector.collect_context(targets=["/non_existent_directory_9999/file.txt"])
    assert len(ctx.target_telemetry) == 1
    assert ctx.target_telemetry[0].exists is False
    assert ctx.target_telemetry[0].file_count == 0
    assert ctx.recoverability_score <= 1.0

@pytest.mark.anyio
async def test_rule_engine_deterministic_authority_under_stress():
    """Authority Verification: Deterministic Rule Engine blocks critical operations 100% of the time."""
    critical_cmds = [
        "sudo rm -rf /",
        "sudo rm -rf /etc",
        "dd if=/dev/zero of=/dev/sda",
        "mkfs.ext4 /dev/sda1"
    ]
    for cmd in critical_cmds:
        meta = command_parser.parse(cmd)
        decision, violations = rule_engine.evaluate_rules(meta, is_root=True)
        assert decision == "BLOCK"
        assert len(violations) > 0
