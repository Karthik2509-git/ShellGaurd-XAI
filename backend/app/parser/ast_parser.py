import re
import logging
try:
    import bashlex
    HAVE_BASHLEX = True
except ImportError:
    bashlex = None
    HAVE_BASHLEX = False
from typing import List, Dict, Any, Optional
from app.parser.anti_evasion import anti_evasion_engine
from app.parser.metadata_extractor import CommandMetadata

logger = logging.getLogger("shellguard.parser.ast")

class CommandASTParser:
    """
    Robust Linux Command AST Parser combining bashlex syntax trees 
    with Anti-Evasion de-obfuscation and fallback parsing.
    """

    CRITICAL_TARGETS = {"/", "/*", "/boot", "/boot/*", "/etc", "/etc/*", "/var", "/var/*", "/usr", "/usr/*", "~", "~/*"}

    def parse(self, raw_command: str) -> CommandMetadata:
        """
        Parses raw command into clean CommandMetadata AST structure.
        """
        if not raw_command or not raw_command.strip():
            return CommandMetadata(
                raw_command="",
                clean_command="",
                base_command=""
            )

        # 1. Anti-Evasion & De-obfuscation
        clean_cmd, is_obfuscated, evasion_type = anti_evasion_engine.inspect_and_clean(raw_command)

        tokens: List[str] = []
        is_sudo = False
        subshell_calls: List[str] = []

        # Check for sudo privilege escalation
        working_cmd = clean_cmd
        if working_cmd.startswith("sudo "):
            is_sudo = True
            working_cmd = working_cmd[5:].strip()

        # 2. Bashlex AST Parsing
        if HAVE_BASHLEX:
            try:
                parts = bashlex.parse(working_cmd)
                tokens = self._extract_tokens_from_ast(parts, working_cmd)
            except Exception as e:
                logger.debug(f"bashlex parse fallback for '{working_cmd}': {e}")
                tokens = working_cmd.split()
        else:
            tokens = working_cmd.split()

        if not tokens:
            tokens = working_cmd.split()

        base_command = tokens[0] if tokens else ""
        flags: List[str] = []
        targets: List[str] = []
        pipe_commands: List[str] = []
        has_redirection = ">" in working_cmd or ">>" in working_cmd

        # Check for pipeline commands (|)
        if "|" in working_cmd:
            pipe_parts = [p.strip() for p in working_cmd.split("|")]
            pipe_commands = pipe_parts[1:]

        is_recursive = False
        is_force = False
        target_is_wildcard = False

        for token in tokens[1:]:
            if token.startswith("-"):
                flags.append(token)
                if "r" in token or "R" in token or token == "--recursive":
                    is_recursive = True
                if "f" in token or token == "--force":
                    is_force = True
            else:
                targets.append(token)
                if token in self.CRITICAL_TARGETS or token.endswith("*") or token == "/" or token == "/*":
                    target_is_wildcard = True

        # Extract subshell expressions $(...)
        subshell_matches = re.findall(r'\$\([^\)]+\)|`[^`]+`', raw_command)
        if subshell_matches:
            subshell_calls = subshell_matches

        return CommandMetadata(
            raw_command=raw_command,
            clean_command=clean_cmd,
            base_command=base_command,
            flags=flags,
            targets=targets,
            is_recursive=is_recursive,
            is_force=is_force,
            is_sudo=is_sudo,
            is_obfuscated=is_obfuscated,
            obfuscation_type=evasion_type,
            has_redirection=has_redirection,
            pipe_commands=pipe_commands,
            target_is_wildcard=target_is_wildcard,
            subshell_calls=subshell_calls
        )

    def _extract_tokens_from_ast(self, ast_nodes: Any, original_str: str) -> List[str]:
        """
        Traverses bashlex AST nodes to extract command tokens.
        """
        tokens = []
        for node in ast_nodes:
            if hasattr(node, "parts"):
                for subpart in node.parts:
                    if hasattr(subpart, "word"):
                        tokens.append(subpart.word)
                    elif hasattr(subpart, "pos"):
                        start, end = subpart.pos
                        tokens.append(original_str[start:end])
        return tokens if tokens else original_str.split()

command_parser = CommandASTParser()
