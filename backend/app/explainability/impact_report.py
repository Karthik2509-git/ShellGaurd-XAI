import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis
from app.risk.adaptive_evaluator import AdaptiveRiskAssessment

logger = logging.getLogger("shellguard.explainability.impact")

class ComponentImpactScore(BaseModel):
    filesystem: int = Field(..., description="Filesystem impact percentage 0-100")
    security: int = Field(..., description="Security exposure impact percentage 0-100")
    networking: int = Field(..., description="Networking & Sockets impact percentage 0-100")
    boot: int = Field(..., description="Kernel & Boot integrity impact percentage 0-100")

class AIImpactReport(BaseModel):
    intent_summary: str = Field(..., description="High-level operational goal")
    failure_probability: float = Field(..., description="Probability of system failure (e.g. 0.98 for 98%)")
    estimated_files: int = Field(..., description="Total estimated files affected")
    critical_services: List[str] = Field(default_factory=list, description="Names of impacted critical services")
    recovery_difficulty: str = Field(..., description="None, Low, Medium, High, or Very High")
    estimated_repair_time: str = Field(..., description="e.g. '0 mins', '5-15 mins', '2-6 hours'")
    affected_components: ComponentImpactScore = Field(..., description="Component progress bar scores")

class DecisionTreeNode(BaseModel):
    step: str
    decision: str
    status: str  # PASS, WARN, BLOCK

class ImpactReportGenerator:
    """
    AI Impact Report Generator & AI Decision Tree Builder.
    Produces comprehensive technical impact data and step-by-step decision trees.
    """

    def generate_report(
        self, 
        metadata: CommandMetadata, 
        context: SystemContext, 
        intent: IntentAnalysis, 
        risk: AdaptiveRiskAssessment
    ) -> tuple[AIImpactReport, List[DecisionTreeNode]]:
        """
        Generates AI Impact Report and AI Decision Tree.
        """
        score = risk.overall_risk_score

        # Failure probability estimation
        fail_prob = min(0.99, max(0.01, round(score / 100.0, 2)))

        # Recovery difficulty & repair time estimation
        if score >= 80:
            diff = "Very High"
            repair_time = "2–6 hours"
        elif score >= 60:
            diff = "High"
            repair_time = "30–60 mins"
        elif score >= 30:
            diff = "Medium"
            repair_time = "5–15 mins"
        else:
            diff = "None"
            repair_time = "0 mins"

        # Component Progress Bar Scores
        fs_score = int(min(100, risk.vectors.data_loss_risk))
        sec_score = int(min(100, risk.vectors.security_risk))
        net_score = int(min(100, risk.vectors.downtime_risk))
        boot_score = 90 if any("boot" in t or "etc" in t or t == "/" for t in metadata.targets) else 10

        impact_report = AIImpactReport(
            intent_summary=intent.user_intent,
            failure_probability=fail_prob,
            estimated_files=risk.vectors.data_loss_risk > 0 and sum(t.file_count for t in context.target_telemetry) or 1,
            critical_services=context.impacted_services,
            recovery_difficulty=diff,
            estimated_repair_time=repair_time,
            affected_components=ComponentImpactScore(
                filesystem=fs_score,
                security=sec_score,
                networking=net_score,
                boot=boot_score
            )
        )

        # Build AI Decision Tree
        tree_nodes = []
        tree_nodes.append(DecisionTreeNode(step="Command AST Parse", decision=f"Binary: {metadata.base_command}", status="PASS"))

        if metadata.is_recursive:
            tree_nodes.append(DecisionTreeNode(step="Recursive Check", decision="Flag: -r/-R active", status="WARN"))

        if metadata.target_is_wildcard or any(t.startswith("/etc") or t == "/" for t in metadata.targets):
            tree_nodes.append(DecisionTreeNode(step="Critical Path Check", decision=f"Target: {', '.join(metadata.targets)}", status="BLOCK" if score >= 80 else "WARN"))

        if metadata.is_sudo or context.is_root:
            tree_nodes.append(DecisionTreeNode(step="Privilege Check", decision="Root/Sudo execution", status="WARN"))

        if context.recoverability_score < 0.2:
            tree_nodes.append(DecisionTreeNode(step="Recoverability Check", decision="No trash/git backup found", status="WARN"))

        final_status = "BLOCK" if risk.requires_confirmation else "PASS"
        tree_nodes.append(DecisionTreeNode(step="Final Decision", decision=f"Score: {score} ({risk.threat_level})", status=final_status))

        return impact_report, tree_nodes

impact_report_generator = ImpactReportGenerator()
