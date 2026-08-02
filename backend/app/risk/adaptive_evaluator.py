import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis
from app.runtime.rules import rule_engine
from app.runtime.policy import policy_engine

logger = logging.getLogger("shellguard.safety.engine")

class RiskVectorBreakdown(BaseModel):
    data_loss_risk: float = Field(..., description="Risk of permanent file/data destruction (0-100)")
    security_risk: float = Field(..., description="Privilege escalation or unauthorized exposure risk (0-100)")
    downtime_risk: float = Field(..., description="Risk of interrupting background system services (0-100)")
    recoverability_risk: float = Field(..., description="Unrecoverability score (0-100)")
    privacy_risk: float = Field(..., description="Risk of exposing sensitive credentials/keys (0-100)")

class AdaptiveRiskAssessment(BaseModel):
    overall_risk_score: int = Field(..., description="Final combined risk score between 0 and 100")
    threat_level: str = Field(..., description="SAFE (Green), CAUTION (Yellow), HIGH (Orange), or CRITICAL (Red)")
    system_trust_level: str = Field(default="Verified", description="System Trust: Verified, Trusted, Warning, Unverified, or Blocked")
    protection_mode: str = Field(default="Active", description="Protection Level: Passive, Active, or Strict")
    risk_confidence: float = Field(default=0.97, description="Analysis confidence rating e.g. 0.97 (97%)")
    failure_likelihood: str = Field(default="Low", description="Failure Likelihood: Low, Medium, High, or Very High")
    recovery_complexity: str = Field(default="Low", description="Recovery Complexity: Low, Medium, High, or Critical")
    vectors: RiskVectorBreakdown = Field(..., description="5-Category Risk Matrix")
    primary_risk_factors: List[str] = Field(default_factory=list, description="Key drivers of risk score")
    evidence: List[str] = Field(default_factory=list, description="Deterministic evidence checkmarks")
    interruption_reasons: List[str] = Field(default_factory=list, description="Explicit 'Why was I interrupted' checkmarks")
    requires_confirmation: bool = Field(..., description="Flag indicating if interactive confirmation is required")
    rule_decision: str = Field(default="PASS", description="Deterministic Rule Engine Decision: PASS, WARN, BLOCK")
    policy_action: str = Field(default="ALLOW", description="Policy Engine Action: ALLOW, WARN, BLOCK")
    affected_files_count: int = Field(default=0, description="Total estimated files affected")
    affected_size_mb: float = Field(default=0.0, description="Total size in MB affected")

class SafetyEngine:
    """
    ⚡ ShellGuard Safety Engine.
    Combines adaptive scoring, OS context telemetry, evidence checkmarks,
    Policy Engine directives, and Rule Engine authority to determine overall system safety and trust level.
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

    def assess_safety(
        self, 
        metadata: CommandMetadata, 
        context: SystemContext, 
        intent: IntentAnalysis,
        command_history_count: int = 0
    ) -> AdaptiveRiskAssessment:
        """
        Computes Safety Engine assessment following pipeline order:
        Evidence ➔ Context ➔ Policy Engine ➔ Rule Engine ➔ Safety Engine
        """
        # 1. Policy Engine Evaluation (Context-Before-Rules)
        policy_action, policy_directives = policy_engine.evaluate_policies(metadata, context)

        # 2. Deterministic Rule Engine Evaluation
        rule_decision, rule_violations = rule_engine.evaluate_rules(metadata, context.is_root)

        dl = 0.0
        sec = 0.0
        dt = 0.0
        rec = 100.0 - (context.recoverability_score * 100.0)
        priv = 0.0

        risk_factors = []
        evidence_list = []
        interruption_reasons = []

        base = metadata.base_command.lower()

        # Evidence Gathering
        if metadata.is_recursive:
            evidence_list.append("✓ Recursive traversal flag (-r/-R)")
            interruption_reasons.append("✓ Recursive folder deletion active")

        if metadata.is_force:
            evidence_list.append("✓ Force flag (-f) bypassing interactive prompts")
            interruption_reasons.append("✓ Forced deletion bypassing safety confirmation")

        if metadata.is_sudo or context.is_root:
            evidence_list.append("✓ Execution under Root/Sudo privileges")
            interruption_reasons.append("✓ Elevated Root privileges active")

        # System Trust Level Classification
        if base in ["git", "ls", "pwd", "trash-put", "cat", "echo"]:
            trust_level = "Verified"
        elif base in ["chmod", "chown"] and "777" not in metadata.clean_command:
            trust_level = "Trusted"
        elif base in ["chmod", "chown"] or metadata.is_force:
            trust_level = "Warning"
        elif "curl" in base and "| bash" in metadata.clean_command:
            trust_level = "Unverified"
        else:
            trust_level = "Verified"

        # Risk Vector Calculations
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
                evidence_list.append("✓ Global permissive permission mask (777)")
                interruption_reasons.append("✓ Global read/write/execute permissions grant")

        elif base in ["kill", "killall", "pkill"]:
            dt += 70.0
            risk_factors.append(f"Abrupt process termination ({metadata.clean_command})")

        elif base in ["systemctl", "service"]:
            dt += 50.0
            if "stop" in metadata.clean_command or "disable" in metadata.clean_command:
                dt += 30.0
                risk_factors.append("System service shutdown/disable")

        elif base in ["curl", "wget"] and ("| bash" in metadata.clean_command or "| sh" in metadata.clean_command):
            sec += 85.0
            priv += 75.0
            risk_factors.append("Piping unverified remote web script directly into shell execution")
            evidence_list.append("✓ Remote code execution pipe (| bash)")
            interruption_reasons.append("✓ Remote unverified shell code pipe")

        # Target Path Context Inspection
        for t in metadata.targets:
            evidence_list.append(f"✓ Target path = {t}")
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
                    interruption_reasons.append(f"✓ Critical OS system directory '{crit_path}' targeted")

        if context.recoverability_score < 0.2:
            interruption_reasons.append("✓ Recovery impossible (no git backup or trash bin)")

        dl_c = min(100.0, max(0.0, dl))
        sec_c = min(100.0, max(0.0, sec))
        dt_c = min(100.0, max(0.0, dt))
        rec_c = min(100.0, max(0.0, rec))
        priv_c = min(100.0, max(0.0, priv))

        if max(dl_c, sec_c, dt_c, priv_c) == 0:
            overall = 0
        else:
            max_vec = max(dl_c, sec_c, dt_c, rec_c, priv_c)
            avg_vec = (dl_c + sec_c + dt_c + rec_c + priv_c) / 5.0
            overall = int(round(max_vec * 0.6 + avg_vec * 0.4))

        if rule_decision == "BLOCK" or policy_action == "BLOCK":
            overall = max(overall, 85)
            threat_level = "CRITICAL"
            trust_level = "Blocked"
        elif rule_decision == "WARN" or policy_action == "WARN":
            overall = max(overall, 55)
            threat_level = "HIGH" if overall >= 60 else "CAUTION"
            trust_level = "Warning" if trust_level != "Blocked" else "Blocked"
        else:
            if overall >= 80:
                threat_level = "CRITICAL"
            elif overall >= 60:
                threat_level = "HIGH"
            elif overall >= 30:
                threat_level = "CAUTION"
            else:
                threat_level = "SAFE"

        if overall >= 80:
            fail_like = "Very High"
            rec_comp = "Critical"
        elif overall >= 60:
            fail_like = "High"
            rec_comp = "High"
        elif overall >= 30:
            fail_like = "Medium"
            rec_comp = "Medium"
        else:
            fail_like = "Low"
            rec_comp = "Low"

        total_files = sum(t.file_count for t in context.target_telemetry)
        total_mb = sum(t.total_size_mb for t in context.target_telemetry)

        return AdaptiveRiskAssessment(
            overall_risk_score=overall,
            threat_level=threat_level,
            system_trust_level=trust_level,
            protection_mode="Active",
            risk_confidence=0.97,
            failure_likelihood=fail_like,
            recovery_complexity=rec_comp,
            vectors=RiskVectorBreakdown(
                data_loss_risk=round(dl_c, 1),
                security_risk=round(sec_c, 1),
                downtime_risk=round(dt_c, 1),
                recoverability_risk=round(rec_c, 1),
                privacy_risk=round(priv_c, 1)
            ),
            primary_risk_factors=list(set(risk_factors)),
            evidence=list(set(evidence_list)),
            interruption_reasons=list(set(interruption_reasons)),
            requires_confirmation=(overall >= 50 or rule_decision in ["WARN", "BLOCK"]),
            rule_decision=rule_decision,
            policy_action=policy_action,
            affected_files_count=total_files,
            affected_size_mb=round(total_mb, 2)
        )

    assess_risk = assess_safety

safety_engine = SafetyEngine()
adaptive_risk_engine = safety_engine
