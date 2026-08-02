import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.anyio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/system/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["version"] == "1.0.0-rc2"
    assert "build_number" in data

@pytest.mark.anyio
async def test_status_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/system/status")
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == "1.0.0-rc2"

@pytest.mark.anyio
async def test_dynamic_diagnostics_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/system/diagnostics")
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == "1.0.0-rc2"
    assert "shell_hooks" in data
    assert "Loaded" in data["shell_hooks"] or "⚠" in data["shell_hooks"]
