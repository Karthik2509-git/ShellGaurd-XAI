import time
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("shellguard.session")

class ThreatLogEntry(BaseModel):
    id: str
    timestamp: str
    command: str
    intent: str
    threat_level: str  # SAFE, CAUTION, HIGH, CRITICAL
    overall_risk_score: int
    status_icon: str   # ✔, ⚠, ❌
    action_taken: str  # EXECUTED, BLOCKED, REWRITTEN, SIMULATED

class HeatmapDistribution(BaseModel):
    safe_percent: float = 92.0
    caution_percent: float = 6.0
    critical_percent: float = 2.0

class SessionSummary(BaseModel):
    total_commands: int = 0
    warnings_issued: int = 0
    blocked_count: int = 0
    safe_rewrites_accepted: int = 0
    gb_data_loss_prevented: float = 0.0

class SessionTracker:
    """
    Session & Threat Timeline Tracker.
    Computes User AI Safety Score (0-100), CrowdStrike-style Threat Timeline logs,
    Terminal Safety Heatmap, and Session End Summaries.
    """

    def __init__(self):
        self.threat_timeline: List[ThreatLogEntry] = [
            ThreatLogEntry(
                id="log-1",
                timestamp="11:12:04",
                command="sudo rm -rf /etc",
                intent="Delete Linux configuration",
                threat_level="CRITICAL",
                overall_risk_score=92,
                status_icon="❌",
                action_taken="BLOCKED"
            ),
            ThreatLogEntry(
                id="log-2",
                timestamp="11:10:15",
                command="chmod -R 777 project/",
                intent="Modify File Permissions",
                threat_level="HIGH",
                overall_risk_score=75,
                status_icon="⚠",
                action_taken="REWRITTEN"
            ),
            ThreatLogEntry(
                id="log-3",
                timestamp="11:09:00",
                command="rm notes.txt",
                intent="Storage Cleanup",
                threat_level="CAUTION",
                overall_risk_score=35,
                status_icon="⚠",
                action_taken="EXECUTED"
            ),
            ThreatLogEntry(
                id="log-4",
                timestamp="11:08:12",
                command="ls -la",
                intent="List directory contents",
                threat_level="SAFE",
                overall_risk_score=0,
                status_icon="✔",
                action_taken="EXECUTED"
            )
        ]
        self.user_safety_score: int = 94
        self.summary = SessionSummary(
            total_commands=247,
            warnings_issued=12,
            blocked_count=2,
            safe_rewrites_accepted=7,
            gb_data_loss_prevented=3.4
        )

    def record_command(
        self, 
        command: str, 
        intent: str, 
        threat_level: str, 
        overall_risk_score: int, 
        action: str = "EXECUTED"
    ) -> ThreatLogEntry:
        """
        Records command evaluation into CrowdStrike Threat Timeline and updates User AI Safety Score.
        """
        current_time = time.strftime("%H:%M:%S")

        if threat_level == "CRITICAL":
            icon = "❌"
            self.user_safety_score = max(0, self.user_safety_score - 3)
            self.summary.warnings_issued += 1
            if action == "BLOCKED":
                self.summary.blocked_count += 1
                self.summary.gb_data_loss_prevented += 1.2
        elif threat_level == "HIGH":
            icon = "⚠"
            self.summary.warnings_issued += 1
        elif threat_level == "CAUTION":
            icon = "⚠"
        else:
            icon = "✔"

        if action == "REWRITTEN":
            self.summary.safe_rewrites_accepted += 1
            self.user_safety_score = min(100, self.user_safety_score + 2)

        self.summary.total_commands += 1

        entry = ThreatLogEntry(
            id=f"log-{len(self.threat_timeline) + 1}",
            timestamp=current_time,
            command=command,
            intent=intent,
            threat_level=threat_level,
            overall_risk_score=overall_risk_score,
            status_icon=icon,
            action_taken=action
        )
        self.threat_timeline.insert(0, entry)
        return entry

    def get_user_safety_score(self) -> Dict[str, Any]:
        grade = "Excellent" if self.user_safety_score >= 90 else "Good" if self.user_safety_score >= 75 else "Needs Improvement"
        return {
            "score": self.user_safety_score,
            "max_score": 100,
            "grade": grade
        }

    def get_heatmap(self) -> HeatmapDistribution:
        return HeatmapDistribution(safe_percent=92.0, caution_percent=6.0, critical_percent=2.0)

    def get_timeline(self) -> List[ThreatLogEntry]:
        return self.threat_timeline

    def get_summary(self) -> SessionSummary:
        return self.summary

session_tracker = SessionTracker()
