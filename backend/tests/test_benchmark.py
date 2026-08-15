import pytest
import time
import asyncio
import statistics
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine
from app.risk.adaptive_evaluator import safety_engine
from app.runtime.rules import rule_engine

@pytest.mark.anyio
async def test_cold_vs_warm_ast_parsing_benchmark():
    """Measures Cold vs Warm AST parsing latency across 50 repetitions."""
    # Cold Run
    t0 = time.perf_counter()
    meta_cold = command_parser.parse("sudo rm -rf /var/log/*")
    cold_latency_ms = (time.perf_counter() - t0) * 1000.0

    # Warm Runs (50 iterations)
    warm_latencies = []
    for _ in range(50):
        t_start = time.perf_counter()
        meta_warm = command_parser.parse("sudo rm -rf /var/log/*")
        warm_latencies.append((time.perf_counter() - t_start) * 1000.0)

    median_warm = statistics.median(warm_latencies)
    p95_warm = sorted(warm_latencies)[int(0.95 * len(warm_latencies))]

    assert meta_cold.clean_command == "sudo rm -rf /var/log/*"
    assert median_warm < 5.0  # Warm AST parsing must be sub-5ms

@pytest.mark.anyio
async def test_command_class_benchmarks():
    """Benchmarks AST parsing + Rule Evaluation across command risk classes."""
    classes = {
        "SAFE": "ls -la /tmp",
        "CAUTION": "rm notes.txt",
        "HIGH": "chmod -R 777 project/",
        "CRITICAL": "sudo rm -rf /etc"
    }

    results = {}
    for cls_name, cmd in classes.items():
        t0 = time.perf_counter()
        meta = command_parser.parse(cmd)
        rule_engine.evaluate_rules(meta, is_root=meta.is_sudo)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        results[cls_name] = elapsed_ms
        assert elapsed_ms < 15.0  # Must evaluate under 15ms

@pytest.mark.anyio
async def test_degraded_mode_fallback_benchmark():
    """Verifies deterministic fallback performance when LLM is bypassed."""
    meta = command_parser.parse("sudo rm -rf /etc")
    t0 = time.perf_counter()
    decision, violations = rule_engine.evaluate_rules(meta, is_root=True)
    fallback_latency_ms = (time.perf_counter() - t0) * 1000.0

    assert decision == "BLOCK"
    assert fallback_latency_ms < 15.0  # Deterministic rule evaluation under 15ms

@pytest.mark.anyio
async def test_concurrency_scaling_benchmark():
    """Benchmarks 10 concurrent requests submitting diagnostic evaluations."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        t0 = time.perf_counter()
        tasks = [ac.get("/api/v1/system/health") for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        total_ms = (time.perf_counter() - t0) * 1000.0

        for res in responses:
            assert res.status_code == 200
        assert total_ms < 2000.0  # 10 concurrent requests under 2.0s total
