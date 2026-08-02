import logging
from typing import List, Tuple
from enum import Enum
from pydantic import BaseModel
from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext

logger = logging.getLogger("shellguard.runtime.policy")

class RuntimeMode(str, Enum):
    LEARNING = "LEARNING"      # Warn only, teach, never block
    NORMAL = "NORMAL text"       # Warn, allow override
    STRICT = "STRICT"          # Block critical operations unless explicitly confirmed
    ENTERPRISE = "ENTERPRISE"  # Policy-driven, strict audit logging

class PolicyEngine:
    """
    🛡️ Declarative OS Security Policy Engine.
    Evaluates system security policies based on active Runtime Mode (Learning, Normal, Strict, Enterprise).
    Executes BEFORE the Rule Engine.
    """

    def __init__(self, mode: RuntimeMode = RuntimeMode.NORMAL):
        self.active_mode = mode

    def evaluate_policies(self, metadata: CommandMetadata, context: SystemContext) -> Tuple[str, List[str]]:
        """
        Evaluates declarative policies against metadata and system context.
        Returns: (Policy Action: "ALLOW" | "WARN" | "BLOCK", Violated Policy Directives)
        """
        policy_warnings = []
        base = metadata.base_command.lower()

        # Policy #1: Never block cleanup inside user Downloads or Tmp directory
        for target in metadata.targets:
            if target.startswith("/tmp") or target.startswith("/home/user/Downloads"):
                return "ALLOW", ["Policy #201: Unrestricted cleanup allowed in temp/downloads directory"]

        # Policy #2: Strict Protection on Root & System Directories
        for target in metadata.targets:
            if target in ["/", "/*", "/etc", "/boot"]:
                if metadata.is_recursive or metadata.is_force:
                    policy_warnings.append(f"Policy #202: Protected OS root path '{target}' modification target")
                    if self.active_mode in [RuntimeMode.STRICT, RuntimeMode.ENTERPRISE, RuntimeMode.NORMAL]:
                        return "BLOCK", policy_warnings

        # Policy #3: Permissive Permission Policy
        if base == "chmod" and "777" in metadata.clean_command:
            policy_warnings.append("Policy #203: Global permissive permissions grant (chmod 777)")
            if self.active_mode == RuntimeMode.LEARNING:
                return "WARN", policy_warnings
            return "WARN", policy_warnings

        if policy_warnings:
            return "WARN", policy_warnings

        return "ALLOW", ["Standard operational policy pass"]

policy_engine = PolicyEngine()
