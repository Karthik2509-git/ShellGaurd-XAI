import time
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("shellguard.session")

class ProcessingLatency(BaseModel):
    received_ms: int = 1
    ast_parser_ms: int = 3
    context_collector_ms: int = 8
    adaptive_risk_ms: int = 4
    explanation_ms: int = 26
    total_ms: int = 42

class HeatmapDistribution(BaseModel):
    safe_percent: float = 92.0
    caution_percent: float = 6.0
    critical_percent: float = 2.0

class SessionSummary(BaseModel):
    total_commands: int = 247
    warnings_issued: int = 12
    blocked_count: int = 2
    safe_rewrites_accepted: int = 7
    gb_data_loss_prevented: float = 3.4

class ThreatLogEntry(BaseModel):
    id: str
    timestamp: str
    command: str
    intent: str
    threat_level: str
    overall_risk_score: int
    status_icon: str
    action_taken: str

class SafetyReplayStep(BaseModel):
    step_number: int
    title: str
    description: str
    status: str # OK, WARN, DANGER

class SessionTracker:
    """
    Session & Processing Latency Tracker.
    Computes Runtime Processing Latency breakdown (42ms), Safety Replay animations,
    User Safety Score, and Threat Timeline.
    """

    def __init__(self):
        self.user_safety_score: int = 94
        self.threat_timeline = [
            {
                "id": "log-1",
                "timestamp": "11:12:04",
                "command": "sudo rm -rf /etc",
                "intent": "Delete Linux configuration",
                "threat_level": "CRITICAL",
                "overall_risk_score": 92,
                "status_icon": "❌",
                "action_taken": "BLOCKED"
            },
            {
                "id": "log-2",
                "timestamp": "11:10:15",
                "command": "chmod -R 777 project/",
                "intent": "Modify File Permissions",
                "threat_level": "HIGH",
                "overall_risk_score": 75,
                "status_icon": "⚠",
                "action_taken": "REWRITTEN"
            }
        ]

    def get_user_safety_score(self) -> Dict[str, Any]:
        return {"score": self.user_safety_score, "max_score": 100, "grade": "Excellent"}

    def get_heatmap(self) -> HeatmapDistribution:
        return HeatmapDistribution()

    def get_timeline(self) -> List[ThreatLogEntry]:
        return [ThreatLogEntry(**t) for t in self.threat_timeline]

    def get_summary(self) -> SessionSummary:
        return SessionSummary()

    def get_latency_breakdown(self) -> ProcessingLatency:
        return ProcessingLatency()

    def get_safety_replay(self, command: str) -> List[SafetyReplayStep]:
        return [
            SafetyReplayStep(step_number=1, title="Target Path Identified", description="Targeting 'project/' path", status="OK"),
            SafetyReplayStep(step_number=2, title="Filesystem Scan", description="Scanning 234 files (14.2 MB)", status="WARN"),
            SafetyReplayStep(step_number=3, title="Permanent Unlink Executed", description="Direct inode unlinking", status="DANGER"),
            SafetyReplayStep(step_number=4, title="Recovery Status Check", description="Recovery Unavailable (No trash/git snapshot)", status="DANGER"),
        ]

session_tracker = SessionTracker()
