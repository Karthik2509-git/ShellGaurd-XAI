import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.interceptor.shellguard_cli import shellguard_cli
from app.interceptor.voice_nl_shell import voice_nl_engine

def test_cli_risk_meter_formatting():
    gauge_critical = shellguard_cli.format_risk_meter(85, "CRITICAL")
    assert "85%" in gauge_critical
    assert "CRITICAL" in gauge_critical

    gauge_low = shellguard_cli.format_risk_meter(10, "LOW")
    assert "10%" in gauge_low

@pytest.mark.anyio
async def test_voice_nl_translation():
    res = await voice_nl_engine.translate_nl_to_command("Safely delete docker build cache")
    assert res.natural_prompt == "Safely delete docker build cache"
    assert res.generated_command != ""

@pytest.mark.anyio
async def test_nl_api_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/interceptor/nl_translate", json={"prompt": "Remove temporary logs"})
    assert response.status_code == 200
    data = response.json()
    assert "generated_command" in data
