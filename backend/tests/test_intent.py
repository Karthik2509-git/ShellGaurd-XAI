import pytest
from app.parser.ast_parser import command_parser
from app.context.collector import context_collector
from app.intent.classifier import intent_engine, IntentCategory

@pytest.mark.anyio
async def test_intent_storage_cleanup():
    meta = command_parser.parse("rm -rf /var/log/*")
    ctx = context_collector.collect_context(targets=["/var/log/*"])
    res = await intent_engine.analyze_intent(meta, ctx)
    assert res.category == IntentCategory.STORAGE_CLEANUP
    assert res.confidence_score >= 0.8
    assert len(res.evidence) > 0

@pytest.mark.anyio
async def test_intent_permission_mod():
    meta = command_parser.parse("chmod -R 777 /etc")
    ctx = context_collector.collect_context(targets=["/etc"])
    res = await intent_engine.analyze_intent(meta, ctx)
    assert res.category == IntentCategory.PERMISSION_MODIFICATION
    assert res.intent_mismatch is True
    assert len(res.evidence) > 0

@pytest.mark.anyio
async def test_intent_process_term():
    meta = command_parser.parse("killall postgres")
    ctx = context_collector.collect_context(targets=["postgres"])
    res = await intent_engine.analyze_intent(meta, ctx)
    assert res.category == IntentCategory.PROCESS_TERMINATION
    assert len(res.evidence) > 0
