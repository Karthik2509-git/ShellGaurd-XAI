import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.context.collector import context_collector

def test_context_collector_basic():
    ctx = context_collector.collect_context(targets=["/etc", "/var/log"], cwd=os.getcwd())
    assert ctx.user != ""
    assert len(ctx.target_telemetry) == 2
    
    etc_telemetry = next(t for t in ctx.target_telemetry if t.path == "/etc")
    assert etc_telemetry.is_critical_path is True
    assert etc_telemetry.criticality_reason is not None

def test_context_collector_nonexistent_target():
    ctx = context_collector.collect_context(targets=["/non_existent_path_xyz_123"])
    assert len(ctx.target_telemetry) == 1
    assert ctx.target_telemetry[0].exists is False

@pytest.mark.anyio
async def test_context_api_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/context/collect", json={"targets": ["/etc"]})
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert len(data["target_telemetry"]) == 1
    assert data["target_telemetry"][0]["is_critical_path"] is True
