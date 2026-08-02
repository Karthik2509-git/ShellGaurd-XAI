import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.evaluator import risk_engine
from app.explainability.generator import explainability_engine

@pytest.mark.anyio
async def test_explainability_generator():
    meta = command_parser.parse("sudo rm -rf /etc")
    ctx = context_collector.collect_context(targets=["/etc"])
    intent = await intent_engine.analyze_intent(meta, ctx)
    risk = risk_engine.assess_risk(meta, ctx, intent)

    report = await explainability_engine.generate_explanation(meta, ctx, intent, risk)
    assert report.technical_rationale != ""
    assert report.eli5_rationale != ""
    assert len(report.why_dangerous_bullets) > 0
    assert len(report.safe_alternatives) > 0
    assert report.safe_alternatives[0].command != ""

@pytest.mark.anyio
async def test_pipeline_evaluate_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/pipeline/evaluate",
            json={"command": "chmod -R 777 /var/www"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["base_command"] == "chmod"
    assert data["risk"]["overall_risk_score"] > 50
    assert "technical_rationale" in data["explanation"]
    assert len(data["explanation"]["safe_alternatives"]) > 0
