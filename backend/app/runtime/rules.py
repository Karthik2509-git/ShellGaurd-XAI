import logging
from typing import List, Tuple
from app.parser.metadata_extractor import CommandMetadata

logger = logging.getLogger("shellguard.runtime.rules")

class DeterministicRuleEngine:
    """
    🔒 Deterministic Security Rule Engine.
    Acts as the FINAL DECISION AUTHORITY in ShellGuard Runtime.
    Rule Engine decides whether an operation is PASS, WARN, or BLOCK.
    Adaptive Risk & Explainability AI explain the rationale and coach the user.
    """

    CRITICAL_TARGET_PATHS = ["/", "/*", "/boot", "/etc", "/usr", "/var/log"]

    def evaluate_rules(self, metadata: CommandMetadata, is_root: bool) -> Tuple[str, List[str]]:
        """
        Evaluates deterministic security rules.
        Returns: (Decision: "PASS" | "WARN" | "BLOCK", Rule Violations List)
        """
        violations = []
        base = metadata.base_command.lower()

        # Rule 1: Root Path Recursive Destruction
        for target in metadata.targets:
            if target in ["/", "/*"] and metadata.is_recursive and (metadata.is_sudo or is_root):
                violations.append("Rule #101: Root filesystem recursive destruction attempt")
                return "BLOCK", violations

        # Rule 2: Critical OS Directory Alteration with Sudo
        for target in metadata.targets:
            if any(target == cp or target.startswith(cp + "/") for cp in self.CRITICAL_TARGET_PATHS):
                if metadata.is_recursive or metadata.is_force:
                    violations.append(f"Rule #102: Recursive/forced modification of critical system directory '{target}'")
                    return "BLOCK", violations
                elif metadata.is_sudo or is_root:
                    violations.append(f"Rule #103: Root execution targeting OS path '{target}'")

        # Rule 3: Obfuscated Remote Execution Pipe
        if metadata.is_obfuscated or ("curl" in base and "| bash" in metadata.clean_command):
            violations.append("Rule #104: Obfuscated or remote shell code execution pipe")
            return "BLOCK", violations

        # Rule 4: Global Permissive Permission Grant
        if base == "chmod" and "777" in metadata.clean_command and metadata.is_recursive:
            violations.append("Rule #105: Global recursive 777 permission grant")
            return "WARN", violations

        if violations:
            return "WARN", violations

        return "PASS", ["Standard user shell command"]

rule_engine = DeterministicRuleEngine()
