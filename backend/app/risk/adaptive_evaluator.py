import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis

logger = logging.getLogger("shellguard.risk.adaptive")

class RiskVectorBreakdown(BaseModel):
    data_loss_risk: float = Field(..., description="Risk of permanent file/data destruction (0-100)")
    security_risk: float = Field(..., description="Privilege escalation or unauthorized exposure risk (0-100)")
    downtime_risk: float = Field(..., description="Risk of interrupting background system services (0-100)")
    recoverability_risk: float = Field(..., description="Unrecoverability score (0-100, higher means harder to recover)")
    privacy_risk: float = Field(..., description="Risk of exposing sensitive credentials/keys (0-100)")

class AdaptiveRiskAssessment(BaseModel):
    overall_risk_score: int = Field(..., description="Final combined risk score between 0 and 100")
    threat_level: str = Field(..., description="SAFE (Green), CAUTION (Yellow), HIGH (Orange), or CRITICAL (Red)")
    risk_confidence: float = Field(default=0.98, description="AI Risk Assessment confidence rating (e.g. 0.98)")
    vectors: RiskVectorBreakdown = Field(..., description="5-Category Risk Matrix")
    primary_risk_factors: List[str] = Field(default_factory=list, description="Key drivers of risk score")
    requires_confirmation: bool = Field(..., description="Flag indicating if interactive confirmation is required")
    adaptive_penalty_applied: bool = Field(default=False, description="Flag indicating if adaptive historical penalty was added")
    adaptive_reason: Optional[str] = Field(default=None, description="Explanation of adaptive score adjustment")
    affected_files_count: int = Field(default=0, description="Total estimated files affected")
    affected_size_mb: float = Field(default=0.0, description="Total size in MB affected")

class AdaptiveRiskEngine:
    """
    Adaptive Risk Engine.
    Dynamically adjusts risk using command history, CWD, git status, user privilege, 
    project type, and command frequency while enforcing a 4-tier threat hierarchy.
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
        intent: IntentAnalysis,
        command_history_count: int = 0
    ) -> AdaptiveRiskAssessment:
        """
        Computes dynamic Adaptive Risk Assessment across 5 risk categories and 4 threat levels.
        """
        dl = 0.0
        sec = 0.0
        dt = 0.0
        rec = 100.0 - (context.recoverability_score * 100.0)
        priv = 0.0

        risk_factors = []
        adaptive_applied = False
        adaptive_reason = None

        base = metadata.base_command.lower()

        # 1. Base Binary Analysis
        if base == "rm":
            dl += 40.0
            if metadata.is_recursive:
                dl += 30.0
                risk_factors.append("Recursive folder deletion (-r/-R)")
            if metadata.is_force:
                dl += 15.0
                risk_factors.append("Forced deletion bypass (-f)")

        elif base in ["chmod", "chown"]:
            sec += 50.0
            if "777" in metadata.clean_command:
                sec += 40.0
                risk_factors.append("Global read/write/execute permissions (chmod 777)")
            if metadata.is_recursive:
                sec += 20.0

        elif base in ["kill", "killall", "pkill"]:
            dt += 70.0
            risk_factors.append(f"Abrupt process termination ({metadata.clean_command})")

        elif base in ["systemctl", "service"]:
            dt += 50.0
            if "stop" in metadata.clean_command or "disable" in metadata.clean_command:
                dt += 30.0
                risk_factors.append("System service shutdown/disable")

        elif base in ["mkfs", "dd", "fdisk", "parted"]:
            dl = 100.0
            sec = 90.0
            risk_factors.append("Direct disk formatting / partition modification")

        elif base in ["curl", "wget"] and ("| bash" in metadata.clean_command or "| sh" in metadata.clean_command):
            sec += 85.0
            priv += 75.0
            risk_factors.append("Piping unverified remote web script directly into shell execution")

        # 2. Privacy Vector (e.g. inspecting .ssh, .aws, .env, id_rsa)
        for t in metadata.targets:
            if any(p in t for p in [".ssh", "id_rsa", ".aws", ".env", "credentials", "shadow"]):
                priv += 80.0
                sec += 40.0
                risk_factors.append(f"Accessing sensitive credential/privacy path: {t}")

        # 3. Critical Path Target Check
        for t in metadata.targets:
            for crit_path, score in self.CRITICAL_PATH_SCORES.items():
                is_match = False
                if crit_path in ["/", "/*"]:
                    if t in ["/", "/*"]:
                        is_match = True
                elif t == crit_path or t.startswith(crit_path + "/"):
                    is_match = True

                if is_match:
                    dl = max(dl, float(score))
                    sec = max(sec, float(score))
                    risk_factors.append(f"Targeting critical OS system path: {crit_path}")

        # 4. Privilege Escalation (Sudo / Root)
        if metadata.is_sudo or context.is_root:
            sec += 30.0
            risk_factors.append("Execution with Root / Sudo privileges")

        # 5. Obfuscation Penalty
        if metadata.is_obfuscated:
            sec += 50.0
            risk_factors.append(f"Detected anti-evasion obfuscation ({metadata.obfuscation_type})")

        # 6. Service Downtime Impact
        if context.impacted_services:
            dt += 35.0
            risk_factors.append(f"Impacts background services: {', '.join(context.impacted_services)}")

        # 7. Adaptive Anomaly Penalty (frequency & environment context)
        if not context.git_repo_detected and base in ["rm", "chmod"] and metadata.is_recursive:
            dl += 15.0
            adaptive_applied = True
            adaptive_reason = "Executed outside version-controlled repository"

        if command_history_count > 3:  # Rapid succession of risky commands
            sec += 15.0
            adaptive_applied = True
            adaptive_reason = adaptive_reason or "High frequency of elevated risk operations in session"

        # Clamp all vectors 0-100
        dl_c = min(100.0, max(0.0, dl))
        sec_c = min(100.0, max(0.0, sec))
        dt_c = min(100.0, max(0.0, dt))
        rec_c = min(100.0, max(0.0, rec))
        priv_c = min(100.0, max(0.0, priv))

        # Overall Risk Score Calculation
        if max(dl_c, sec_c, dt_c, priv_c) == 0:
            overall = 0
        else:
            max_vec = max(dl_c, sec_c, dt_c, rec_c, priv_c)
            avg_vec = (dl_c + sec_c + dt_c + rec_c + priv_c) / 5.0
            overall = int(round(max_vec * 0.6 + avg_vec * 0.4))

        # 4-Tier Threat Hierarchy: SAFE, CAUTION, HIGH, CRITICAL
        if overall >= 80:
            threat_level = "CRITICAL"
        elif overall >= 60:
            threat_level = "HIGH"
        elif overall >= 30:
            threat_level = "CAUTION"
        else:
            threat_level = "SAFE"

        # Calculate affected files and size
        total_files = sum(t.file_count for t in context.target_telemetry)
        total_mb = sum(t.total_size_mb for t in context.target_telemetry)

        return AdaptiveRiskAssessment(
            overall_risk_score=overall,
            threat_level=threat_level,
            risk_confidence=0.98,
            vectors=RiskVectorBreakdown(
                data_loss_risk=round(dl_c, 1),
                security_risk=round(sec_c, 1),
                downtime_risk=round(dt_c, 1),
                recoverability_risk=round(rec_c, 1),
                privacy_risk=round(priv_c, 1)
            ),
            primary_risk_factors=list(set(risk_factors)),
            requires_confirmation=(overall >= 50),
            adaptive_penalty_applied=adaptive_applied,
            adaptive_reason=adaptive_reason,
            affected_files_count=total_files,
            affected_size_mb=round(total_mb, 2)
        )

adaptive_risk_engine = AdaptiveRiskEngine()
