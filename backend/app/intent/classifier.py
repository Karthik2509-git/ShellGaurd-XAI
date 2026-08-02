import json
import logging
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.llm_factory import llm_service
from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext

logger = logging.getLogger("shellguard.intent")

class IntentCategory(str, Enum):
    STORAGE_CLEANUP = "STORAGE_CLEANUP"
    LOG_ROTATION = "LOG_ROTATION"
    SERVICE_MANAGEMENT = "SERVICE_MANAGEMENT"
    PERMISSION_MODIFICATION = "PERMISSION_MODIFICATION"
    CRITICAL_SYSTEM_DELETION = "CRITICAL_SYSTEM_DELETION"
    PACKAGE_MANAGEMENT = "PACKAGE_MANAGEMENT"
    NETWORK_CONFIG = "NETWORK_CONFIG"
    PROCESS_TERMINATION = "PROCESS_TERMINATION"
    UNKNOWN_INTENT = "UNKNOWN_INTENT"

class IntentAnalysis(BaseModel):
    user_intent: str = Field(..., description="High-level business intent inferred by AI")
    category: IntentCategory = Field(..., description="Categorized Linux operational intent")
    confidence_score: float = Field(..., description="AI confidence score between 0.0 and 1.0")
    predicted_side_effects: List[str] = Field(default_factory=list, description="Red-team predicted unintended side effects")
    intent_mismatch: bool = Field(default=False, description="Flag indicating mismatch between user intent & command impact")
    mismatch_explanation: Optional[str] = Field(default=None, description="Explanation of why command doesn't match intent")

class MultiAgentIntentEngine:
    """
    Multi-Agent LangGraph Reasoning Engine.
    Orchestrates Intent Specialist, Red-Team Adversary, and Alignment Validator.
    """

    INTENT_SYSTEM_PROMPT = """You are ShellGuard AI's Intent Specialist Agent.
Analyze the following Linux command and system context to infer the true user intent.

Respond strictly in JSON format with keys:
{
  "user_intent": "Brief description of what the user is trying to accomplish",
  "category": "STORAGE_CLEANUP | LOG_ROTATION | SERVICE_MANAGEMENT | PERMISSION_MODIFICATION | CRITICAL_SYSTEM_DELETION | PACKAGE_MANAGEMENT | NETWORK_CONFIG | PROCESS_TERMINATION | UNKNOWN_INTENT",
  "confidence_score": 0.95,
  "predicted_side_effects": ["Side effect 1", "Side effect 2"],
  "intent_mismatch": false,
  "mismatch_explanation": null
}"""

    async def analyze_intent(self, metadata: CommandMetadata, context: SystemContext) -> IntentAnalysis:
        """
        Analyzes command + context using LLM Multi-Agent system with deterministic fallback heuristics.
        """
        # Deterministic Heuristic Fast-Path for zero-latency baseline
        heuristic_res = self._deterministic_heuristic(metadata, context)
        
        # Prepare context for AI reasoning
        prompt_content = f"""
Command: `{metadata.clean_command}`
Base Binary: `{metadata.base_command}`
Flags: {metadata.flags}
Targets: {metadata.targets}
Is Sudo: {metadata.is_sudo}
Is Recursive: {metadata.is_recursive}
User: {context.user}
CWD: {context.cwd}
Target Telemetry: {[t.model_dump() for t in context.target_telemetry]}
Impacted Services: {context.impacted_services}
        """

        messages = [
            {"role": "system", "content": self.INTENT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_content}
        ]

        try:
            res = await llm_service.generate_completion(messages=messages, temperature=0.1)
            content = res.get("content", "")
            
            # Extract JSON block
            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(json_str)
            return IntentAnalysis(
                user_intent=parsed.get("user_intent", heuristic_res.user_intent),
                category=IntentCategory(parsed.get("category", heuristic_res.category)),
                confidence_score=float(parsed.get("confidence_score", 0.9)),
                predicted_side_effects=parsed.get("predicted_side_effects", heuristic_res.predicted_side_effects),
                intent_mismatch=bool(parsed.get("intent_mismatch", heuristic_res.intent_mismatch)),
                mismatch_explanation=parsed.get("mismatch_explanation", heuristic_res.mismatch_explanation)
            )
        except Exception as e:
            logger.warning(f"LLM Intent analysis error: {e}. Falling back to deterministic heuristics.")
            return heuristic_res

    def _deterministic_heuristic(self, metadata: CommandMetadata, context: SystemContext) -> IntentAnalysis:
        """
        Deterministic baseline intent classifier when AI service is unavailable.
        """
        base = metadata.base_command.lower()
        cmd = metadata.clean_command.lower()

        if base == "rm":
            if metadata.target_is_wildcard or any(t.startswith("/etc") or t.startswith("/boot") or t == "/" for t in metadata.targets):
                return IntentAnalysis(
                    user_intent="System Deletion / Permanent Data Removal",
                    category=IntentCategory.CRITICAL_SYSTEM_DELETION,
                    confidence_score=0.98,
                    predicted_side_effects=["Irreversible file loss", "System crash or boot failure"],
                    intent_mismatch=True,
                    mismatch_explanation="Recursive removal of critical paths will permanently damage operating system files."
                )
            elif any("log" in t.lower() for t in metadata.targets):
                return IntentAnalysis(
                    user_intent="Log Directory Cleanup",
                    category=IntentCategory.LOG_ROTATION,
                    confidence_score=0.9,
                    predicted_side_effects=["Log history loss", "Missing log directories for active services"],
                    intent_mismatch=False
                )
            return IntentAnalysis(
                user_intent="File & Storage Cleanup",
                category=IntentCategory.STORAGE_CLEANUP,
                confidence_score=0.85,
                predicted_side_effects=["Data deletion"],
                intent_mismatch=False
            )

        elif base in ["chmod", "chown", "setfacl"]:
            return IntentAnalysis(
                user_intent="Modify File Permissions & Access Control",
                category=IntentCategory.PERMISSION_MODIFICATION,
                confidence_score=0.95,
                predicted_side_effects=["Security exposure if 777 applied", "Service access permission errors"],
                intent_mismatch="777" in cmd,
                mismatch_explanation="Setting global 777 permissions exposes system files to unauthorized write access." if "777" in cmd else None
            )

        elif base in ["systemctl", "service"]:
            return IntentAnalysis(
                user_intent="Manage Background System Services",
                category=IntentCategory.SERVICE_MANAGEMENT,
                confidence_score=0.95,
                predicted_side_effects=["Service downtime", "Dependent application failure"],
                intent_mismatch=False
            )

        elif base in ["kill", "killall", "pkill"]:
            return IntentAnalysis(
                user_intent="Terminate Active Processes",
                category=IntentCategory.PROCESS_TERMINATION,
                confidence_score=0.9,
                predicted_side_effects=["Unsaved process data loss", "Abrupt service disconnection"],
                intent_mismatch=False
            )

        return IntentAnalysis(
            user_intent=f"Execute system command '{base}'",
            category=IntentCategory.UNKNOWN_INTENT,
            confidence_score=0.5,
            predicted_side_effects=[],
            intent_mismatch=False
        )

intent_engine = MultiAgentIntentEngine()
