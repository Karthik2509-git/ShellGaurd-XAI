from fastapi import APIRouter
from app.session.tracker import session_tracker, HeatmapDistribution, SessionSummary, ThreatLogEntry
from app.runtime.os_events import os_event_monitor, OSEvent
from typing import List, Dict, Any

router = APIRouter()

@router.get("/timeline", response_model=List[ThreatLogEntry], summary="CrowdStrike-Style Threat Timeline Audit Log")
async def get_threat_timeline():
    return session_tracker.get_timeline()

@router.get("/user_safety_score", summary="User AI Safety Score (0-100)")
async def get_user_safety_score():
    return session_tracker.get_user_safety_score()

@router.get("/heatmap", response_model=HeatmapDistribution, summary="Terminal Safety Heatmap")
async def get_heatmap():
    return session_tracker.get_heatmap()

@router.get("/summary", response_model=SessionSummary, summary="Session End Summary Metrics")
async def get_session_summary():
    return session_tracker.get_summary()

@router.get("/os_events", response_model=List[OSEvent], summary="OS System Event Awareness Log")
async def get_os_events():
    return os_event_monitor.get_recent_events()
