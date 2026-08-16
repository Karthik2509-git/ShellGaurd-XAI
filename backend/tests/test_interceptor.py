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

@pytest.mark.anyio
async def test_cli_backend_offline_deterministic_fallback():
    """Verifies CLI blocks catastrophic commands via local RuleEngine when backend is offline."""
    from app.interceptor.shellguard_cli import ShellGuardCLI
    offline_cli = ShellGuardCLI(backend_url="http://invalid-localhost:99999")
    decision = await offline_cli.evaluate_and_prompt("sudo rm -rf /etc")
    assert decision == "ABORT"

    safe_decision = await offline_cli.evaluate_and_prompt("ls -la /tmp")
    assert safe_decision == "EXECUTE"

def test_shellguard_runtime_imports():
    """Verifies that mandatory ShellGuard dependencies can be imported in runtime."""
    import httpx
    import fastapi
    import uvicorn
    import bashlex
    import pydantic
    assert httpx.__version__ is not None

@pytest.mark.anyio
async def test_reentrancy_guard_bypass():
    """Verifies internal ShellGuard commands immediately return EXECUTE without recursion."""
    decision = await shellguard_cli.evaluate_and_prompt("python3 -m app.interceptor.shellguard_cli 'ls'")
    assert decision == "EXECUTE"

def test_python_resolution_dependency_guard():
    """Verifies python interpreter resolution validates importability of mandatory dependencies."""
    import sys
    import subprocess
    cmd = [sys.executable, "-c", "import httpx, fastapi, pydantic, bashlex; print('OK')"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "OK" in res.stdout

@pytest.mark.anyio
async def test_online_backend_block_decision_enforcement(monkeypatch):
    """Verifies that an online backend decision of BLOCK returns ABORT without calling input()."""
    from app.interceptor.shellguard_cli import ShellGuardCLI
    import httpx

    mock_payload = {
        "risk": {
            "overall_risk_score": 85,
            "threat_level": "CRITICAL",
            "system_trust_level": "Blocked",
            "requires_confirmation": True,
            "rule_decision": "BLOCK",
            "policy_action": "BLOCK",
            "primary_risk_factors": ["Modification of /etc"],
            "vectors": {
                "data_loss_risk": 90,
                "security_risk": 85,
                "downtime_risk": 80,
                "recoverability_risk": 95,
                "privacy_risk": 20
            }
        },
        "explanation": {"eli5_summary": "Dangerous command!"}
    }

    class MockResponse:
        status_code = 200
        def json(self):
            return mock_payload

    class MockAsyncClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, json, timeout):
            return MockResponse()

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    input_called = False
    def mock_input(prompt=""):
        nonlocal input_called
        input_called = True
        return "y"

    monkeypatch.setattr("builtins.input", mock_input)

    cli = ShellGuardCLI(backend_url="http://mock-daemon:8000")
    decision = await cli.evaluate_and_prompt("sudo rm -rf /etc")

    assert decision == "ABORT"
    assert not input_called, "input() must NEVER be called when backend returns BLOCK"

@pytest.mark.anyio
async def test_online_backend_policy_action_block_enforcement(monkeypatch):
    """Verifies that policy_action='BLOCK' returns ABORT without prompting."""
    from app.interceptor.shellguard_cli import ShellGuardCLI
    import httpx

    mock_payload = {
        "risk": {
            "overall_risk_score": 90,
            "threat_level": "CRITICAL",
            "requires_confirmation": True,
            "rule_decision": "PASS",
            "policy_action": "BLOCK",
            "primary_risk_factors": ["Policy Violation"],
            "vectors": {
                "data_loss_risk": 90,
                "security_risk": 85,
                "downtime_risk": 80,
                "recoverability_risk": 95,
                "privacy_risk": 20
            }
        },
        "explanation": {"eli5_summary": "Policy blocked operation"}
    }

    class MockResponse:
        status_code = 200
        def json(self):
            return mock_payload

    class MockAsyncClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, url, json, timeout):
            return MockResponse()

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    input_called = False
    def mock_input(prompt=""):
        nonlocal input_called
        input_called = True
        return "y"

    monkeypatch.setattr("builtins.input", mock_input)

    cli = ShellGuardCLI(backend_url="http://mock-daemon:8000")
    decision = await cli.evaluate_and_prompt("rm -rf /")

    assert decision == "ABORT"
    assert not input_called
