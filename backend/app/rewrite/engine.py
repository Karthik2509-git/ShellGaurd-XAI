import logging
from typing import List, Optional
from pydantic import BaseModel, Field

from app.parser.metadata_extractor import CommandMetadata
from app.context.collector import SystemContext

logger = logging.getLogger("shellguard.rewrite")

class CommandRewriteOption(BaseModel):
    safe_command: str = Field(..., description="Transformed safe command")
    why_better_rationale: str = Field(..., description="Educational explanation of why this rewrite is superior")
    safety_gain: str = Field(..., description="Quantified safety benefit")
    backup_command_suggestion: Optional[str] = Field(default=None, description="Optional Backup First payload")

class AICommandRewriteEngine:
    """
    ✨ AI Command Rewrite Engine.
    Transforms dangerous commands into safe, production-grade Linux commands
    accompanied by educational 'Why Rewrite is Better' explanations and 1-click 'Backup First' payloads.
    """

    def generate_rewrites(self, metadata: CommandMetadata, context: SystemContext) -> List[CommandRewriteOption]:
        """
        Generates optimal safe command rewrites and Backup First recommendations.
        """
        base = metadata.base_command.lower()
        rewrites = []

        if base == "rm":
            targets_str = " ".join(metadata.targets) if metadata.targets else "*"
            rewrites.append(
                CommandRewriteOption(
                    safe_command=f"trash-put {targets_str}",
                    why_better_rationale="Files are moved safely to the desktop trash bin instead of being permanently unlinked from the filesystem index. Fully compatible with Linux Desktop Trash.",
                    safety_gain="100% Recoverable via trash-restore",
                    backup_command_suggestion=f"tar -czf backup_before_delete_{int(context.disk_usage_percent)}.tar.gz {targets_str}"
                )
            )
            rewrites.append(
                CommandRewriteOption(
                    safe_command=f"find {targets_str} -type f -mtime +30 -delete",
                    why_better_rationale="Targets only files older than 30 days, preserving recent working files and directory structures.",
                    safety_gain="Prevents accidental deletion of active project files"
                )
            )

        elif base in ["chmod", "chown"]:
            if "777" in metadata.clean_command:
                target_path = metadata.targets[0] if metadata.targets else "project/"
                rewrites.append(
                    CommandRewriteOption(
                        safe_command=f"chmod -R 755 {target_path} && find {target_path} -type f -exec chmod 644 {{}} +",
                        why_better_rationale="Applies secure standard Unix permissions: 755 for directories (executable bit needed for directory traversal) and 644 for files (prevents unauthorized execution of uploaded files).",
                        safety_gain="Enforces Principle of Least Privilege"
                    )
                )

        elif base in ["killall", "kill"]:
            target_svc = metadata.targets[0] if metadata.targets else "service"
            rewrites.append(
                CommandRewriteOption(
                    safe_command=f"systemctl reload {target_svc}",
                    why_better_rationale="Gracefully reloads application configuration without severing existing socket connections or destroying active worker threads.",
                    safety_gain="Zero Downtime Service Maintenance"
                )
            )

        elif base in ["curl", "wget"] and ("| bash" in metadata.clean_command or "| sh" in metadata.clean_command):
            rewrites.append(
                CommandRewriteOption(
                    safe_command="curl -sSL <URL> -o script.sh && bash -n script.sh",
                    why_better_rationale="Downloads script locally and performs a syntax dry-run check before executing unverified remote payloads.",
                    safety_gain="Prevents Arbitrary Remote Code Execution (RCE)"
                )
            )

        return rewrites

rewrite_engine = AICommandRewriteEngine()
