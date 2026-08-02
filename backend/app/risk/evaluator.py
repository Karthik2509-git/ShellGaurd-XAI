import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis, IntentCategory

logger = logging.getLogger("shellguard.risk")

class RiskVectorBreakdown(BaseModel):
    data_loss_risk: float = Field(..., description="Risk of permanent file/data destruction (0-100)")
    system_stability_risk: float = Field(..., description="Risk of OS crash or boot failure (0-100)")
    security_escalation_risk: float = Field(..., description="Privilege escalation or unauthorized access risk (0-100)")
    service_downtime_risk: float = Field(..., description="Risk of crashing active system services (0-100)")
    recoverability_rating: float = Field(..., description="Rating of availability of backups/trash (0-100, lower means worse recoverability)")

class RiskAssessment(BaseModel):
    overall_risk_score: int = Field(..., description="Final combined risk score between 0 and 100")
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    vectors: RiskVectorBreakdown = Field(..., description="5-Vector risk breakdown")
    primary_risk_factors: List[str] = Field(default_factory=list, description="Key factors driving high risk score")
    requires_confirmation: bool = Field(..., description="Flag indicating if interactive Y/N confirmation is required")
    affected_files_count: int = Field(default=0, description="Total estimated files affected")
    affected_size_mb: float = Field(default=0.0, description="Total size in MB affected")

class RiskEngine:
    """
    Dynamic 5-Vector Risk Assessment Engine.
    Combines deterministic security rules with live OS context & AI intent telemetry.
    """

    CRITICAL_PATH_SCORES = {
        "/": 100,
        "/*": 100,
        "/boot": 95,
        "/etc": 90,
        "/var": 85,
        "/usr": 80,
        "/home": 75
    }

    def assess_risk(
        self, 
        metadata: CommandMetadata, 
        context: SystemContext, 
        intent: IntentAnalysis
    ) -> RiskAssessment:
        """
        Calculates dynamic Risk Assessment based on metadata, context, and intent.
        """
        data_loss = 0.0
        system_stability = 0.0
        security_escalation = 0.0
        service_downtime = 0.0
        recoverability = 100.0 - (context.recoverability_score * 100.0)  # High score = hard to recover

        risk_factors = []

        # 1. Base Binary Risk
        base = metadata.base_command.lower()
        if base == "rm":
            data_loss += 40.0
            if metadata.is_recursive:
                data_loss += 30.0
                risk_factors.append("Recursive folder deletion (-r/-R)")
            if metadata.is_force:
                data_loss += 15.0
                risk_factors.append("Forced deletion bypass (-f)")

        elif base in ["chmod", "chown"]:
            security_escalation += 50.0
            if "777" in metadata.clean_command:
                security_escalation += 40.0
                risk_factors.append("Global read/write/execute permissions (chmod 777)")
            if metadata.is_recursive:
                security_escalation += 20.0

        elif base in ["kill", "killall", "pkill"]:
            service_downtime += 70.0
            risk_factors.append(f"Abrupt process termination ({metadata.clean_command})")

        elif base in ["systemctl", "service"]:
            service_downtime += 50.0
            if "stop" in metadata.clean_command or "disable" in metadata.clean_command:
                service_downtime += 30.0
                risk_factors.append("System service shutdown/disable")

        elif base in ["mkfs", "dd", "fdisk", "parted"]:
            data_loss = 100.0
            system_stability = 90.0
            risk_factors.append("Direct disk formatting / partition modification")

        # 2. Critical Target Path Penalty
        for t in metadata.targets:
            for crit_path, score in self.CRITICAL_PATH_SCORES.items():
                is_match = False
                if crit_path in ["/", "/*"]:
                    if t in ["/", "/*"]:
                        is_match = True
                elif t == crit_path or t.startswith(crit_path + "/") or t.startswith(crit_path):
                    is_match = True

                if is_match:
                    system_stability = max(system_stability, float(score))
                    data_loss = max(data_loss, float(score))
                    risk_factors.append(f"Targeting critical system path: {crit_path}")

        # 3. Privilege Escalation (Sudo / Root)
        if metadata.is_sudo or context.is_root:
            security_escalation += 30.0
            system_stability += 15.0
            risk_factors.append("Execution with Root / Sudo privileges")

        # 4. Obfuscation Penalty
        if metadata.is_obfuscated:
            security_escalation += 50.0
            risk_factors.append(f"Detected evasion attempt ({metadata.obfuscation_type})")

        # 5. Service Impact Penalty
        if context.impacted_services:
            service_downtime += 30.0
            risk_factors.append(f"Impacts active system services: {', '.join(context.impacted_services)}")

        # 6. Intent Mismatch Penalty
        if intent.intent_mismatch:
            data_loss += 25.0
            risk_factors.append("High Intent Mismatch (Command impact exceeds user intent)")

        # Clamp all vector scores between 0 and 100
        dl = min(100.0, max(0.0, data_loss))
        ss = min(100.0, max(0.0, system_stability))
        se = min(100.0, max(0.0, security_escalation))
        sd = min(100.0, max(0.0, service_downtime))
        rec = min(100.0, max(0.0, recoverability))

        # If no operational risk vectors are triggered (e.g. read-only commands like ls, cat, pwd), overall risk is 0
        if max(dl, ss, se, sd) == 0:
            overall = 0
        else:
            max_vec = max(dl, ss, se, sd, rec)
            avg_vec = (dl + ss + se + sd + rec) / 5.0
            overall = int(round(max_vec * 0.6 + avg_vec * 0.4))

        # Risk Level Categorization
        if overall >= 80:
            level = "CRITICAL"
        elif overall >= 60:
            level = "HIGH"
        elif overall >= 35:
            level = "MEDIUM"
        else:
            level = "LOW"

        # Calculate affected files and size
        total_files = sum(t.file_count for t in context.target_telemetry)
        total_mb = sum(t.total_size_mb for t in context.target_telemetry)

        return RiskAssessment(
            overall_risk_score=overall,
            risk_level=level,
            vectors=RiskVectorBreakdown(
                data_loss_risk=round(dl, 1),
                system_stability_risk=round(ss, 1),
                security_escalation_risk=round(se, 1),
                service_downtime_risk=round(sd, 1),
                recoverability_rating=round(rec, 1)
            ),
            primary_risk_factors=list(set(risk_factors)),
            requires_confirmation=(overall >= 50),
            affected_files_count=total_files,
            affected_size_mb=round(total_mb, 2)
        )

risk_engine = RiskEngine()
