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
    evidence_checkmarks: List[str] = Field(default_factory=list, description="Why this rewrite was selected checkmarks")
    backup_command_suggestion: Optional[str] = Field(default=None, description="Optional Backup First payload")

class CommandRewriteEngine:
    """
    Command Rewrite Engine.
    Transforms dangerous commands into safe, production-grade Linux commands
    accompanied by 'Why Selected' evidence checkmarks and 'Backup First' payloads.
    """

    def generate_rewrites(self, metadata: CommandMetadata, context: SystemContext) -> List[CommandRewriteOption]:
        """
        Generates optimal safe command rewrites and evidence checkmarks.
        """
        base = metadata.base_command.lower()
        rewrites = []

        if base == "rm":
            targets_str = " ".join(metadata.targets) if metadata.targets else "*"
            rewrites.append(
                CommandRewriteOption(
                    safe_command=f"trash-put {targets_str}",
                    why_better_rationale="Files are moved safely to the desktop trash bin instead of being permanently unlinked from the filesystem index.",
                    safety_gain="100% Recoverable via trash-restore",
                    evidence_checkmarks=[
                        "✓ Fully recoverable",
                        "✓ Linux Desktop Trash compatible",
                        "✓ Preserves file inode metadata",
                        "✓ Reversible action"
                    ],
                    backup_command_suggestion=f"tar -czf backup_before_delete_{int(context.disk_usage_percent)}.tar.gz {targets_str}"
                )
            )

        elif base in ["chmod", "chown"]:
            if "777" in metadata.clean_command:
                target_path = metadata.targets[0] if metadata.targets else "project/"
                rewrites.append(
                    CommandRewriteOption(
                        safe_command=f"chmod -R 755 {target_path} && find {target_path} -type f -exec chmod 644 {{}} +",
                        why_better_rationale="Applies secure standard Unix permissions: 755 for directories and 644 for files.",
                        safety_gain="Enforces Principle of Least Privilege",
                        evidence_checkmarks=[
                            "✓ Standard POSIX permissions",
                            "✓ Prevents arbitrary script execution",
                            "✓ Maintains directory traversal capability"
                        ]
                    )
                )

        return rewrites

rewrite_engine = CommandRewriteEngine()
