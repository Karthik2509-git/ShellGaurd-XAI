import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.llm_factory import llm_service
from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.intent.classifier import IntentAnalysis
from app.risk.evaluator import RiskAssessment

logger = logging.getLogger("shellguard.explainability")

class SafeAlternative(BaseModel):
    command: str = Field(..., description="Recommended safe command replacement")
    explanation: str = Field(..., description="Why this alternative is safer")
    safety_gain: str = Field(..., description="Quantified safety benefit (e.g. Preserves undo support)")

class ExplanationReport(BaseModel):
    technical_rationale: str = Field(..., description="Detailed technical breakdown of risk and consequences")
    eli5_rationale: str = Field(..., description="Simple, 1-sentence Explain-Like-I'm-5 explanation")
    why_dangerous_bullets: List[str] = Field(default_factory=list, description="Key bullet points outlining system damage")
    safe_alternatives: List[SafeAlternative] = Field(default_factory=list, description="Suggested safer command alternatives")
    undo_playbook: Optional[str] = Field(default=None, description="Steps or commands to recover/undo if executed")

class ExplainabilityEngine:
    """
    Explainable AI Engine.
    Translates complex OS risk scores into human-readable technical rationale,
    ELI5 summaries, bulleted damage points, and smart safer alternatives.
    """

    EXPLAIN_SYSTEM_PROMPT = """You are ShellGuard AI's Explainable Risk & Remediation Generator.
Analyze the provided Linux command, system context, intent analysis, and 5-vector risk score.

Generate a comprehensive explanation and safe alternative commands.
Respond strictly in JSON format matching this schema:
{
  "technical_rationale": "Detailed technical analysis explaining why the command poses risk to files, services, or kernel stability",
  "eli5_rationale": "Simple Explain-Like-I'm-5 summary in one plain sentence",
  "why_dangerous_bullets": [
    "Deletes 1,420 files recursively across /etc",
    "Stops active PostgreSQL database service",
    "Irreversible data loss without trash recovery"
  ],
  "safe_alternatives": [
    {
      "command": "trash-put /var/log/*",
      "explanation": "Moves files to system trash bin instead of permanent deletion",
      "safety_gain": "100% Recoverable via trash-restore"
    }
  ],
  "undo_playbook": "If executed accidentally, restore from Timeshift snapshot or check git stash."
}"""

    async def generate_explanation(
        self, 
        metadata: CommandMetadata, 
        context: SystemContext, 
        intent: IntentAnalysis,
        risk: RiskAssessment
    ) -> ExplanationReport:
        """
        Generates dual rationale (Technical + ELI5) and safer alternatives.
        """
        heuristic_report = self._deterministic_fallback(metadata, context, intent, risk)

        prompt_content = f"""
Command: `{metadata.clean_command}`
Base Binary: `{metadata.base_command}`
Flags: {metadata.flags}
Targets: {metadata.targets}
User Intent: {intent.user_intent}
Intent Category: {intent.category}
Overall Risk Score: {risk.overall_risk_score}/100 ({risk.threat_level})
Risk Vectors: Data Loss: {risk.vectors.data_loss_risk}, Security: {risk.vectors.security_risk}, Service Downtime: {risk.vectors.downtime_risk}
Affected Files: {risk.affected_files_count} files ({risk.affected_size_mb} MB)
Impacted Services: {context.impacted_services}
Primary Risk Factors: {risk.primary_risk_factors}
        """

        messages = [
            {"role": "system", "content": self.EXPLAIN_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_content}
        ]

        try:
            res = await llm_service.generate_completion(messages=messages, temperature=0.2)
            content = res.get("content", "")

            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(json_str)
            alternatives = [
                SafeAlternative(
                    command=a.get("command", ""),
                    explanation=a.get("explanation", ""),
                    safety_gain=a.get("safety_gain", "Safer execution")
                )
                for a in parsed.get("safe_alternatives", [])
            ]

            return ExplanationReport(
                technical_rationale=parsed.get("technical_rationale", heuristic_report.technical_rationale),
                eli5_rationale=parsed.get("eli5_rationale", heuristic_report.eli5_rationale),
                why_dangerous_bullets=parsed.get("why_dangerous_bullets", heuristic_report.why_dangerous_bullets),
                safe_alternatives=alternatives if alternatives else heuristic_report.safe_alternatives,
                undo_playbook=parsed.get("undo_playbook", heuristic_report.undo_playbook)
            )
        except Exception as e:
            logger.warning(f"LLM Explainability generation failed: {e}. Using deterministic fallback.")
            return heuristic_report

    def _deterministic_fallback(
        self, 
        metadata: CommandMetadata, 
        context: SystemContext, 
        intent: IntentAnalysis,
        risk: RiskAssessment
    ) -> ExplanationReport:
        """
        Deterministic explanation generator when AI is offline.
        """
        base = metadata.base_command.lower()
        bullets = risk.primary_risk_factors.copy()
        if not bullets:
            bullets = [f"Executes potentially impactful operational command '{base}'"]

        alternatives = []
        if base == "rm":
            alternatives.append(
                SafeAlternative(
                    command=f"trash-put {' '.join(metadata.targets)}" if metadata.targets else "trash-put *",
                    explanation="Moves items safely to the user's trash directory instead of unrecoverable unlinking.",
                    safety_gain="100% Recoverable using trash-restore"
                )
            )
            alternatives.append(
                SafeAlternative(
                    command=f"rm -ri {' '.join(metadata.targets)}" if metadata.targets else "rm -ri *",
                    explanation="Prompts for interactive confirmation before deleting each individual file.",
                    safety_gain="Prevents accidental batch deletion"
                )
            )
        elif base in ["chmod", "chown"]:
            if "777" in metadata.clean_command:
                clean_target = " ".join(metadata.targets) if metadata.targets else "path"
                alternatives.append(
                    SafeAlternative(
                        command=f"chmod 755 {clean_target}",
                        explanation="Grants owner full read/write/execute rights while restricting public write access.",
                        safety_gain="Prevents security vulnerability exploitation"
                    )
                )
        elif base in ["killall", "kill"]:
            alternatives.append(
                SafeAlternative(
                    command=f"systemctl reload {' '.join(metadata.targets)}" if metadata.targets else "systemctl reload <service>",
                    explanation="Gracefully reloads application configuration without severing active connections.",
                    safety_gain="Zero downtime process management"
                )
            )

        tech = f"The command '{metadata.clean_command}' received a Risk Score of {risk.overall_risk_score}/100 ({risk.threat_level}). "
        if risk.affected_files_count > 0:
            tech += f"It affects approximately {risk.affected_files_count} files ({risk.affected_size_mb} MB). "
        if context.impacted_services:
            tech += f"It directly impacts background services: {', '.join(context.impacted_services)}. "

        eli5 = f"Warning! Running this will permanently affect {risk.affected_files_count} files and might stop your computer's background programs."

        return ExplanationReport(
            technical_rationale=tech,
            eli5_rationale=eli5,
            why_dangerous_bullets=bullets,
            safe_alternatives=alternatives,
            undo_playbook="Use git checkout / git restore if in a Git repo, or check trash-cli if configured."
        )

explainability_engine = ExplainabilityEngine()
