import pytest
import time
import asyncio
import statistics
import psutil
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine, IntentAnalysis, IntentCategory
from app.risk.adaptive_evaluator import safety_engine
from app.runtime.rules import rule_engine

# Timer resolution precision threshold
TIMER_RESOLUTION_MS = 0.01

@pytest.mark.anyio
async def test_cold_vs_warm_stage_profiling_benchmark():
    """
    Performs explicit 50-iteration statistical profiling across each stage
    and full pipeline orchestration to produce mathematically reconcilable metrics.
    """
    cmd = "sudo rm -rf /etc"
    
    # -------------------------------------------------------------
    # STAGE 1: AST Parsing
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    meta_cold = command_parser.parse(cmd)
    ast_cold_ms = (time.perf_counter() - t0) * 1000.0

    ast_warm = []
    for _ in range(50):
        ts = time.perf_counter()
        _ = command_parser.parse(cmd)
        ast_warm.append((time.perf_counter() - ts) * 1000.0)

    ast_warm_med = statistics.median(ast_warm)
    ast_warm_p95 = sorted(ast_warm)[int(0.95 * len(ast_warm))]

    # -------------------------------------------------------------
    # STAGE 2: Context Telemetry Collection
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    ctx_cold = context_collector.collect_context(targets=["/etc"])
    ctx_cold_ms = (time.perf_counter() - t0) * 1000.0

    ctx_warm = []
    for _ in range(50):
        ts = time.perf_counter()
        _ = context_collector.collect_context(targets=["/etc"])
        ctx_warm.append((time.perf_counter() - ts) * 1000.0)

    ctx_warm_med = statistics.median(ctx_warm)
    ctx_warm_p95 = sorted(ctx_warm)[int(0.95 * len(ctx_warm))]

    # -------------------------------------------------------------
    # STAGE 3: Deterministic Rule Engine
    # -------------------------------------------------------------
    t0 = time.perf_counter()
    dec_cold, viol_cold = rule_engine.evaluate_rules(meta_cold, is_root=True)
    rule_cold_ms = (time.perf_counter() - t0) * 1000.0

    rule_warm = []
    for _ in range(50):
        ts = time.perf_counter()
        _ = rule_engine.evaluate_rules(meta_cold, is_root=True)
        rule_warm.append((time.perf_counter() - ts) * 1000.0)

    rule_warm_med = statistics.median(rule_warm)
    rule_warm_p95 = sorted(rule_warm)[int(0.95 * len(rule_warm))]

    # -------------------------------------------------------------
    # STAGE 4: Safety Engine Evaluation
    # -------------------------------------------------------------
    intent_obj = IntentAnalysis(
        user_intent="System directory recursive removal",
        category=IntentCategory.SYSTEM_ADMINISTRATION,
        confidence_score=0.98,
        predicted_side_effects=["Permanent OS file removal"],
        evidence=["sudo privilege", "recursive flag -r"]
    )
    
    t0 = time.perf_counter()
    safety_cold = safety_engine.assess_safety(meta_cold, ctx_cold, intent_obj)
    safety_cold_ms = (time.perf_counter() - t0) * 1000.0

    safety_warm = []
    for _ in range(50):
        ts = time.perf_counter()
        _ = safety_engine.assess_safety(meta_cold, ctx_cold, intent_obj)
        safety_warm.append((time.perf_counter() - ts) * 1000.0)

    safety_warm_med = statistics.median(safety_warm)
    safety_warm_p95 = sorted(safety_warm)[int(0.95 * len(safety_warm))]

    # -------------------------------------------------------------
    # STAGE 5: Decision Orchestration & Fast-API Handler Overhead
    # -------------------------------------------------------------
    orch_warm = []
    for _ in range(50):
        ts = time.perf_counter()
        # Simulated orchestration: dict packaging + payload validation
        _ = {
            "command": cmd,
            "decision": dec_cold,
            "violations": viol_cold,
            "safety": safety_cold.model_dump(),
            "context": ctx_cold.model_dump()
        }
        orch_warm.append((time.perf_counter() - ts) * 1000.0)

    orch_warm_med = statistics.median(orch_warm)
    orch_warm_p95 = sorted(orch_warm)[int(0.95 * len(orch_warm))]

    # -------------------------------------------------------------
    # STAGE 6: Full Pipeline Interception — Deterministic Test Provider (50 reps)
    # -------------------------------------------------------------
    pipeline_warm = []
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Cold pipeline run
        t0 = time.perf_counter()
        res_cold = await ac.post("/api/v1/pipeline/evaluate", json={"command": "sudo rm -rf /etc"})
        pipeline_cold_ms = (time.perf_counter() - t0) * 1000.0
        assert res_cold.status_code == 200

        for _ in range(50):
            ts = time.perf_counter()
            res = await ac.post("/api/v1/pipeline/evaluate", json={"command": "sudo rm -rf /etc"})
            pipeline_warm.append((time.perf_counter() - ts) * 1000.0)
            assert res.status_code == 200

    pipeline_warm_med = statistics.median(pipeline_warm)
    pipeline_warm_p95 = sorted(pipeline_warm)[int(0.95 * len(pipeline_warm))]

    # Print mathematical reconciliation summary for audit logs
    sum_stages_med = ast_warm_med + ctx_warm_med + rule_warm_med + safety_warm_med + orch_warm_med
    print(f"\n--- GATE 3 MATHEMATICAL RECONCILIATION ---")
    print(f"AST Warm Median: {ast_warm_med:.3f} ms")
    print(f"Ctx Warm Median: {ctx_warm_med:.3f} ms")
    print(f"Rule Warm Median: {rule_warm_med:.3f} ms")
    print(f"Safety Warm Median: {safety_warm_med:.3f} ms")
    print(f"Orchestration Warm Median: {orch_warm_med:.3f} ms")
    print(f"Sum of Stage Medians: {sum_stages_med:.3f} ms")
    print(f"Full Pipeline — Deterministic Test Provider Median: {pipeline_warm_med:.3f} ms")

    assert ast_warm_med < 5.0
    assert rule_warm_med < 2.0
    assert pipeline_warm_med < 100.0

@pytest.mark.anyio
async def test_command_class_benchmarks():
    """
    Benchmarks Decision-Path Latency (AST + Rules) and Complete Interception Latency (Full Endpoint)
    across command risk classes (50 repetitions each).
    """
    classes = {
        "SAFE": "ls -la /tmp",
        "CAUTION": "rm notes.txt",
        "HIGH": "chmod -R 777 project/",
        "CRITICAL": "sudo rm -rf /etc"
    }

    decision_path_results = {}
    full_pipeline_results = {}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for cls_name, cmd in classes.items():
            # 1. Decision-Path Latency (AST Parsing + Deterministic Rule Evaluation)
            dec_latencies = []
            for _ in range(50):
                t0 = time.perf_counter()
                meta = command_parser.parse(cmd)
                rule_engine.evaluate_rules(meta, is_root=meta.is_sudo)
                dec_latencies.append((time.perf_counter() - t0) * 1000.0)
            med_dec_ms = statistics.median(dec_latencies)
            decision_path_results[cls_name] = max(med_dec_ms, TIMER_RESOLUTION_MS) if med_dec_ms < TIMER_RESOLUTION_MS else med_dec_ms

            # 2. Complete Interception Latency (Full Pipeline HTTP Endpoint)
            pipe_latencies = []
            for _ in range(50):
                t0 = time.perf_counter()
                res = await ac.post("/api/v1/pipeline/evaluate", json={"command": cmd})
                pipe_latencies.append((time.perf_counter() - t0) * 1000.0)
                assert res.status_code == 200
            full_pipeline_results[cls_name] = statistics.median(pipe_latencies)

            assert med_dec_ms < 15.0
            assert full_pipeline_results[cls_name] < 100.0

    print(f"\n--- COMMAND CLASS BENCHMARK RESULTS (50 reps) ---")
    print("Class     | Decision-Path Latency (AST+Rules) | Complete Interception Latency (Full Endpoint)")
    for cls_name in classes.keys():
        d_val = decision_path_results[cls_name]
        d_disp = f"< {TIMER_RESOLUTION_MS} ms" if d_val == TIMER_RESOLUTION_MS else f"{d_val:.3f} ms"
        p_val = full_pipeline_results[cls_name]
        print(f"{cls_name:<9} | {d_disp:<33} | {p_val:.3f} ms")

@pytest.mark.anyio
async def test_degraded_mode_fallback_benchmark():
    """Verifies deterministic fallback performance when LLM is bypassed (50 reps)."""
    meta = command_parser.parse("sudo rm -rf /etc")
    latencies = []
    for _ in range(50):
        t0 = time.perf_counter()
        decision, violations = rule_engine.evaluate_rules(meta, is_root=True)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    med_ms = statistics.median(latencies)
    assert decision == "BLOCK"
    assert med_ms < 2.0  # Deterministic rule evaluation under 2.0ms

@pytest.mark.anyio
async def test_concurrency_scaling_benchmark():
    """
    Benchmarks 1, 5, 10, 20 concurrent HTTP health check requests
    and records memory/CPU footprint from psutil.
    """
    process = psutil.Process()
    mem_before_mb = process.memory_info().rss / (1024 * 1024)

    concurrency_levels = [1, 5, 10, 20]
    results = {}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for n in concurrency_levels:
            t0 = time.perf_counter()
            tasks = [ac.post("/api/v1/pipeline/evaluate", json={"command": "sudo rm -rf /etc"}) for _ in range(n)]
            responses = await asyncio.gather(*tasks)
            total_duration_ms = (time.perf_counter() - t0) * 1000.0

            for res in responses:
                assert res.status_code == 200
            
            throughput_req_sec = (n / (total_duration_ms / 1000.0)) if total_duration_ms > 0 else 0
            results[n] = {
                "total_duration_ms": total_duration_ms,
                "avg_latency_per_req_ms": total_duration_ms / n,
                "throughput_req_sec": throughput_req_sec
            }

    mem_after_mb = process.memory_info().rss / (1024 * 1024)
    cpu_percent = process.cpu_percent(interval=None)

    print(f"\n--- CONCURRENCY & RESOURCE RESULTS ---")
    print(f"Memory Before: {mem_before_mb:.2f} MB, Memory After: {mem_after_mb:.2f} MB")
    print(f"CPU Utilization: {cpu_percent:.2f}%")
    for n, data in results.items():
        print(f"{n} Terminals: Total={data['total_duration_ms']:.2f}ms, Avg/Req={data['avg_latency_per_req_ms']:.2f}ms, Throughput={data['throughput_req_sec']:.1f} req/s")
