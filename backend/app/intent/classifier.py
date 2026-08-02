import logging
import json
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext
from app.services.llm_factory import llm_service

logger = logging.getLogger("shellguard.intent")

class IntentCategory(str, Enum):
    STORAGE_CLEANUP = "STORAGE_CLEANUP"
    PERMISSION_MODIFICATION = "PERMISSION_MODIFICATION"
    SYSTEM_ADMINISTRATION = "SYSTEM_ADMINISTRATION"
    PROCESS_TERMINATION = "PROCESS_TERMINATION"
    NETWORK_TRANSFER = "NETWORK_TRANSFER"
    PACKAGE_MANAGEMENT = "PACKAGE_MANAGEMENT"
    FILE_MANIPULATION = "FILE_MANIPULATION"
    UNKNOWN_INTENT = "UNKNOWN_INTENT"

class IntentAnalysis(BaseModel):
    user_intent: str = Field(..., description="High-level business intent inferred by AI")
    category: IntentCategory = Field(..., description="Categorized Linux operational intent")
    confidence_score: float = Field(..., description="AI confidence score between 0.0 and 1.0")
    predicted_side_effects: List[str] = Field(default_factory=list, description="Side effects")
    evidence: List[str] = Field(default_factory=list, description="Deterministic evidence checkmarks")
    intent_mismatch: bool = Field(default=False, description="Flag indicating mismatch")
    mismatch_explanation: Optional[str] = Field(default=None, description="Explanation of mismatch")

class MultiAgentIntentEngine:
    """
    Multi-Agent Intent Engine.
    Uses LLM reasoning with evidence-backed heuristic fallback.
    """

    async def analyze_intent(self, metadata: CommandMetadata, context: SystemContext) -> IntentAnalysis:
        """
        Analyzes command intent using LLM and evidence checkmarks.
        """
        prompt = f"""You are ShellGuard Intent Analysis Agent.
Analyze the following Linux command and return JSON with keys:
- "user_intent": High level goal
- "category": STORAGE_CLEANUP, PERMISSION_MODIFICATION, SYSTEM_ADMINISTRATION, PROCESS_TERMINATION, NETWORK_TRANSFER, FILE_MANIPULATION, UNKNOWN_INTENT
- "confidence_score": float 0-1
- "predicted_side_effects": list of strings
- "intent_mismatch": boolean
- "mismatch_explanation": string or null

Command: {metadata.clean_command}
Base Binary: {metadata.base_command}
Targets: {metadata.targets}
Root User: {context.is_root or metadata.is_sudo}
"""
        try:
            res = await llm_service.generate_completion([{"role": "user", "content": prompt}], temperature=0.0)
            raw_response = res.get("content", "")
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            data = json.loads(clean_json)

            category_str = data.get("category", "UNKNOWN_INTENT")
            try:
                cat_enum = IntentCategory(category_str)
            except ValueError:
                cat_enum = IntentCategory.UNKNOWN_INTENT

            evidence = [
                f"✓ Binary parser identified command '{metadata.base_command}'",
                f"✓ Execution environment: {'Root/Sudo' if metadata.is_sudo or context.is_root else 'Standard User'}"
            ]
            if metadata.targets:
                evidence.append(f"✓ Target path = {', '.join(metadata.targets)}")
            if metadata.is_recursive:
                evidence.append("✓ Recursive flag detected (-r/-R)")

            return IntentAnalysis(
                user_intent=data.get("user_intent", f"Execute {metadata.base_command}"),
                category=cat_enum,
                confidence_score=float(data.get("confidence_score", 0.95)),
                predicted_side_effects=data.get("predicted_side_effects", []),
                evidence=evidence,
                intent_mismatch=bool(data.get("intent_mismatch", False)),
                mismatch_explanation=data.get("mismatch_explanation")
            )
        except Exception as e:
            logger.warning(f"LLM Intent analysis error: {e}. Falling back to deterministic heuristics.")
            return self._heuristic_intent(metadata, context)

    def _heuristic_intent(self, metadata: CommandMetadata, context: SystemContext) -> IntentAnalysis:
        base = metadata.base_command.lower()
        if base == "rm":
            intent_str = "Permanent Storage Cleanup / File Deletion"
            cat_enum = IntentCategory.STORAGE_CLEANUP
            side_effects = ["Loss of unbacked files", "Potential directory index corruption"]
            mismatch = metadata.target_is_wildcard or any(t in ["/", "/*", "/etc"] for t in metadata.targets)
            mismatch_expl = "Command targets critical system directory beyond normal cleanup intent" if mismatch else None
        elif base in ["chmod", "chown"]:
            intent_str = "Modify File System Permissions & Access Ownership"
            cat_enum = IntentCategory.PERMISSION_MODIFICATION
            side_effects = ["Security isolation breach", "Unauthorized privilege exposure"]
            mismatch = "777" in metadata.clean_command
            mismatch_expl = "chmod 777 grants full world-writable permissions" if mismatch else None
        elif base in ["kill", "killall", "pkill"]:
            intent_str = "Terminate Active Processes"
            cat_enum = IntentCategory.PROCESS_TERMINATION
            side_effects = ["Unsaved process data loss", "Abrupt service disconnection"]
            mismatch = False
            mismatch_expl = None
        elif base in ["systemctl", "service"]:
            intent_str = "Manage System Service Configuration & State"
            cat_enum = IntentCategory.SYSTEM_ADMINISTRATION
            side_effects = ["Background service status change"]
            mismatch = False
            mismatch_expl = None
        else:
            intent_str = f"Execute system command '{base}'"
            cat_enum = IntentCategory.UNKNOWN_INTENT
            side_effects = []
            mismatch = False
            mismatch_expl = None

        evidence = [
            f"✓ Binary parser identified command '{metadata.base_command}'",
            f"✓ Target path matched {len(metadata.targets)} paths" if metadata.targets else "✓ No path target specified",
            f"✓ Execution environment: {'Root/Sudo' if metadata.is_sudo or context.is_root else 'Standard User'}"
        ]
        if metadata.is_recursive:
            evidence.append("✓ Recursive traversal flag detected (-r/-R)")

        return IntentAnalysis(
            user_intent=intent_str,
            category=cat_enum,
            confidence_score=0.96,
            predicted_side_effects=side_effects,
            evidence=evidence,
            intent_mismatch=mismatch,
            mismatch_explanation=mismatch_expl
        )

intent_engine = MultiAgentIntentEngine()
