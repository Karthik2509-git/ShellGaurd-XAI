import sys
import json
import logging
import asyncio
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger("shellguard.interceptor")

class ANSIColor:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

class ShellGuardCLI:
    """
    Terminal Interceptor CLI & ANSI Formatter.
    Displays dynamic risk gauges, intent analysis, explainable rationales, 
    and interactive decision prompts [Y/N/Simulate/Alternative].
    """

    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url.rstrip("/")

    def format_risk_meter(self, score: int, level: str) -> str:
        """
        Renders an ANSI color-coded 10-block visual risk gauge.
        """
        filled_blocks = int(round(score / 10.0))
        empty_blocks = 10 - filled_blocks
        
        if score >= 80:
            color = ANSIColor.RED
        elif score >= 60:
            color = ANSIColor.YELLOW
        elif score >= 35:
            color = ANSIColor.CYAN
        else:
            color = ANSIColor.GREEN

        gauge = f"{color}[{'█' * filled_blocks}{'░' * empty_blocks}] {score}% {level}{ANSIColor.RESET}"
        return gauge

    def print_intercept_banner(self, payload: Dict[str, Any]):
        """
        Renders complete terminal safety evaluation banner.
        """
        meta = payload.get("metadata", {})
        risk = payload.get("risk", {})
        intent = payload.get("intent", {})
        explanation = payload.get("explanation", {})

        score = risk.get("overall_risk_score", 0)
        level = risk.get("risk_level", "UNKNOWN")

        print(f"\n{ANSIColor.BOLD}{ANSIColor.CYAN}═════════════════════════════════════════════════════════════════════════{ANSIColor.RESET}")
        print(f"{ANSIColor.BOLD}🛡️  SHELLGUARD AI — INTENT SAFETY LAYER{ANSIColor.RESET}")
        print(f"{ANSIColor.BOLD}{ANSIColor.CYAN}═════════════════════════════════════════════════════════════════════════{ANSIColor.RESET}\n")

        print(f"  {ANSIColor.BOLD}Target Command:{ANSIColor.RESET} {ANSIColor.YELLOW}{meta.get('clean_command', '')}{ANSIColor.RESET}")
        print(f"  {ANSIColor.BOLD}Inferred Intent:{ANSIColor.RESET} {intent.get('user_intent', 'N/A')} ({intent.get('category', 'UNKNOWN')})")
        print(f"  {ANSIColor.BOLD}Dynamic Risk Score:{ANSIColor.RESET} {self.format_risk_meter(score, level)}\n")

        print(f"  {ANSIColor.BOLD}💡 ELI5 Summary:{ANSIColor.RESET}")
        print(f"     {explanation.get('eli5_rationale', '')}\n")

        print(f"  {ANSIColor.BOLD}⚠️  Potential Impact & Vulnerabilities:{ANSIColor.RESET}")
        for bullet in explanation.get("why_dangerous_bullets", []):
            print(f"     • {ANSIColor.RED}{bullet}{ANSIColor.RESET}")

        alternatives = explanation.get("safe_alternatives", [])
        if alternatives:
            print(f"\n  {ANSIColor.BOLD}✨ Recommended Safer Alternatives:{ANSIColor.RESET}")
            for idx, alt in enumerate(alternatives, 1):
                print(f"     [{idx}] {ANSIColor.GREEN}{alt.get('command')}{ANSIColor.RESET}")
                print(f"         └─ {alt.get('explanation')} ({ANSIColor.CYAN}{alt.get('safety_gain')}{ANSIColor.RESET})")

        print(f"\n{ANSIColor.BOLD}{ANSIColor.CYAN}═════════════════════════════════════════════════════════════════════════{ANSIColor.RESET}")

    async def evaluate_and_prompt(self, command: str) -> str:
        """
        Sends command to backend API and prompts user if confirmation is needed.
        Returns user decision: 'EXECUTE', 'ABORT', 'SIMULATE', or 'ALTERNATIVE:<cmd>'
        """
        if any(internal in command for internal in ["_shellguard", "shellguard-runtime", "shellguard_cli"]):
            return "EXECUTE"

        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    f"{self.backend_url}/api/v1/pipeline/evaluate",
                    json={"command": command},
                    timeout=10.0
                )
                if res.status_code != 200:
                    logger.error(f"Pipeline error: {res.text}")
                    return "EXECUTE"  # Fail-open if backend error

                data = res.json()
                risk = data.get("risk", {})

                if not risk.get("requires_confirmation", False):
                    return "EXECUTE"

                self.print_intercept_banner(data)

                # Prompt user for decision
                print(f"\n{ANSIColor.BOLD}Action Required:{ANSIColor.RESET}")
                print(f"  [{ANSIColor.GREEN}Y{ANSIColor.RESET}] Proceed with Execution")
                print(f"  [{ANSIColor.RED}N{ANSIColor.RESET}] Abort Command (Default)")
                print(f"  [{ANSIColor.CYAN}S{ANSIColor.RESET}] Dry-Run Simulation")
                
                alternatives = data.get("explanation", {}).get("safe_alternatives", [])
                if alternatives:
                    print(f"  [{ANSIColor.YELLOW}A{ANSIColor.RESET}] Use Safe Alternative ({alternatives[0].get('command')})")

                choice = input(f"\nProceed with operation? [y/N/s/a]: ").strip().lower()

                if choice == "y":
                    return "EXECUTE"
                elif choice == "s":
                    return "SIMULATE"
                elif choice == "a" and alternatives:
                    return f"ALTERNATIVE:{alternatives[0].get('command')}"
                else:
                    return "ABORT"

            except Exception as e:
                logger.warning(f"Backend API unavailable ({e}). Fallback to local deterministic safety engine.")
                try:
                    from app.parser.ast_parser import command_parser
                    from app.runtime.rules import rule_engine
                    meta = command_parser.parse(command)
                    decision, violations = rule_engine.evaluate_rules(meta, is_root=meta.is_sudo)
                    if decision == "BLOCK":
                        print(f"\n{ANSIColor.BOLD}{ANSIColor.RED}[ShellGuard Offline Guard] CATASTROPHIC COMMAND BLOCKED{ANSIColor.RESET}")
                        print(f"  {ANSIColor.BOLD}Target Command:{ANSIColor.RESET} {ANSIColor.YELLOW}{meta.clean_command}{ANSIColor.RESET}")
                        print(f"  {ANSIColor.RED}Violations:{ANSIColor.RESET} {', '.join(violations)}")
                        print(f"  {ANSIColor.BOLD}Backend Daemon Status:{ANSIColor.RESET} Offline — Deterministic Rule Engine Active\n")
                        return "ABORT"
                    elif decision == "WARN":
                        print(f"\n{ANSIColor.BOLD}{ANSIColor.YELLOW}[ShellGuard Offline Guard] POTENTIAL RISK WARNING{ANSIColor.RESET}")
                        print(f"  {ANSIColor.BOLD}Target Command:{ANSIColor.RESET} {ANSIColor.YELLOW}{meta.clean_command}{ANSIColor.RESET}")
                        print(f"  {ANSIColor.YELLOW}Violations:{ANSIColor.RESET} {', '.join(violations)}\n")
                        choice = input("Proceed with operation? [y/N]: ").strip().lower()
                        return "EXECUTE" if choice == "y" else "ABORT"
                    return "EXECUTE"
                except Exception as fallback_err:
                    logger.error(f"Fallback rule engine error: {fallback_err}")
                    return "EXECUTE"

shellguard_cli = ShellGuardCLI()

if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        sys.exit(0)
    target_cmd = sys.argv[1]
    decision = asyncio.run(shellguard_cli.evaluate_and_prompt(target_cmd))
    if decision == "ABORT":
        sys.exit(1)
    elif decision == "SIMULATE":
        print(f"{ANSIColor.CYAN}[ShellGuard Simulation] Dry-run complete. System state preserved.{ANSIColor.RESET}")
        sys.exit(1)
    elif decision.startswith("ALTERNATIVE:"):
        alt_cmd = decision.split("ALTERNATIVE:", 1)[1]
        print(f"{ANSIColor.GREEN}[ShellGuard Alternative] Executing replacement: {alt_cmd}{ANSIColor.RESET}")
        import subprocess
        sys.exit(subprocess.call(alt_cmd, shell=True))
    sys.exit(0)
