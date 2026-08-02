import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.evaluator import risk_engine

BENCHMARK_COMMANDS = [
    "sudo rm -rf /",
    "rm -rf /var/log/*",
    "chmod -R 777 /etc",
    "killall postgres",
    "systemctl stop sshd",
    "echo c3VkbyBybSAtcmYgLw== | base64 -d | sh",
    "trash-put notes.txt",
    "ls -la /tmp",
    "git status",
    "docker image prune -a -f"
]

def test_ast_parser_benchmark():
    start = time.time()
    for cmd in BENCHMARK_COMMANDS * 10:  # 100 iterations
        meta = command_parser.parse(cmd)
        assert meta.base_command != ""
    elapsed = time.time() - start
    avg_ms = (elapsed / 100.0) * 1000.0
    print(f"\n[BENCHMARK] AST Parser Average Throughput: {avg_ms:.2f} ms / command")
    assert avg_ms < 15.0  # Must be faster than 15ms per command

@pytest.mark.anyio
async def test_full_pipeline_benchmark():
    start = time.time()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/pipeline/evaluate", json={"command": "sudo rm -rf /var/log/*"})
        assert res.status_code == 200
        assert res.json()["risk"]["overall_risk_score"] >= 80
    elapsed_ms = (time.time() - start) * 1000.0
    print(f"\n[BENCHMARK] End-to-End Pipeline Latency: {elapsed_ms:.2f} ms")
