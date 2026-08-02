import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.evaluator import risk_engine

@pytest.mark.anyio
async def test_risk_evaluator_rm_rf_etc():
    meta = command_parser.parse("sudo rm -rf /etc")
    ctx = context_collector.collect_context(targets=["/etc"])
    intent = await intent_engine.analyze_intent(meta, ctx)
    
    assessment = risk_engine.assess_risk(meta, ctx, intent)
    assert assessment.overall_risk_score >= 80
    assert assessment.risk_level == "CRITICAL"
    assert assessment.requires_confirmation is True
    assert assessment.vectors.system_stability_risk >= 80.0

@pytest.mark.anyio
async def test_risk_evaluator_low_risk_ls():
    meta = command_parser.parse("ls -la /tmp")
    ctx = context_collector.collect_context(targets=["/tmp"])
    intent = await intent_engine.analyze_intent(meta, ctx)
    
    assessment = risk_engine.assess_risk(meta, ctx, intent)
    assert assessment.overall_risk_score < 35
    assert assessment.risk_level == "LOW"
    assert assessment.requires_confirmation is False

@pytest.mark.anyio
async def test_risk_api_endpoint():
    meta = command_parser.parse("chmod 777 /var/www")
    ctx = context_collector.collect_context(targets=["/var/www"])
    intent = await intent_engine.analyze_intent(meta, ctx)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/risk/assess", 
            json={
                "metadata": meta.model_dump(), 
                "context": ctx.model_dump(), 
                "intent": intent.model_dump()
            }
        )
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk_score"] > 50
    assert "vectors" in data
