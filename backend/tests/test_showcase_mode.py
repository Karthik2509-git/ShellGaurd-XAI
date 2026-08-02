import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.runtime.showcase_mode import showcase_engine

def test_showcase_mode_scenarios():
    scenarios = showcase_engine.get_scenarios()
    assert len(scenarios) == 5
    assert scenarios[0].command == "ls -la /tmp"
    assert scenarios[3].expected_threat_level == "CRITICAL"

@pytest.mark.anyio
async def test_diagnostics_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/system/diagnostics")
    assert res.status_code == 200
    data = res.json()
    assert data["protection_status"] == "Online"
    assert data["runtime_health"] == "Healthy"
    assert "ipc_layer" in data
