import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine, IntentCategory

@pytest.mark.anyio
async def test_intent_analysis_critical_deletion():
    meta = command_parser.parse("sudo rm -rf /etc")
    ctx = context_collector.collect_context(targets=["/etc"])
    analysis = await intent_engine.analyze_intent(meta, ctx)
    
    assert analysis.category == IntentCategory.CRITICAL_SYSTEM_DELETION
    assert len(analysis.predicted_side_effects) > 0

@pytest.mark.anyio
async def test_intent_analysis_chmod():
    meta = command_parser.parse("chmod -R 777 /var/www")
    ctx = context_collector.collect_context(targets=["/var/www"])
    analysis = await intent_engine.analyze_intent(meta, ctx)
    
    assert analysis.category == IntentCategory.PERMISSION_MODIFICATION
    assert analysis.intent_mismatch is True

@pytest.mark.anyio
async def test_intent_api_endpoint():
    meta = command_parser.parse("systemctl stop postgresql")
    ctx = context_collector.collect_context(targets=["/var/lib/postgresql"])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/intent/analyze", 
            json={"metadata": meta.model_dump(), "context": ctx.model_dump()}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "SERVICE_MANAGEMENT"
