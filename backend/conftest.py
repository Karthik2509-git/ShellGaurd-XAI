import pytest
import json
from app.services.llm_factory import llm_service

class DeterministicTestLLMProvider:
    """
    ⚡ Test-Only Deterministic LLM Provider for ShellGuard Runtime.
    Guarantees 100% offline execution without accessing OpenAI, Ollama, Qdrant, or network sockets.
    Provides realistic, schema-compliant JSON responses for Intent Analysis & Explainability Generator.
    """

    async def mock_generate_completion(
        self,
        messages,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        response_format = None
    ):
        prompt_text = ""
        for m in messages:
            prompt_text += m.get("content", "") + "\n"

        prompt_lower = prompt_text.lower()

        # -------------------------------------------------------------
        # Intent Analysis Prompt Handling
        # -------------------------------------------------------------
        if "shellguard intent analysis agent" in prompt_lower or "user_intent" in prompt_lower:
            if "chmod" in prompt_lower:
                category = "PERMISSION_MODIFICATION"
                user_intent = "Modify File System Permissions & Access Ownership"
                mismatch = "777" in prompt_lower
                mismatch_expl = "chmod 777 grants full world-writable permissions" if mismatch else None
                side_effects = ["Security isolation breach", "Unauthorized privilege exposure"]
            elif "kill" in prompt_lower or "killall" in prompt_lower or "pkill" in prompt_lower:
                category = "PROCESS_TERMINATION"
                user_intent = "Terminate Active Processes"
                mismatch = False
                mismatch_expl = None
                side_effects = ["Unsaved process data loss", "Abrupt service disconnection"]
            elif "systemctl" in prompt_lower or "service" in prompt_lower:
                category = "SYSTEM_ADMINISTRATION"
                user_intent = "Manage System Service Configuration & State"
                mismatch = False
                mismatch_expl = None
                side_effects = ["Background service status change"]
            elif "rm" in prompt_lower:
                category = "STORAGE_CLEANUP"
                user_intent = "Permanent Storage Cleanup / File Deletion"
                mismatch = any(t in prompt_lower for t in ["/etc", "/boot", "/var", " / ", " /*"])
                mismatch_expl = "Command targets critical system directory beyond normal cleanup intent" if mismatch else None
                side_effects = ["Loss of unbacked files"]
            elif "ls" in prompt_lower or "cat" in prompt_lower or "pwd" in prompt_lower or "cd" in prompt_lower:
                category = "FILE_MANIPULATION"
                user_intent = "Directory Listing / Read-Only Inspection"
                mismatch = False
                mismatch_expl = None
                side_effects = []
            else:
                category = "FILE_MANIPULATION"
                user_intent = "General Linux File Operation"
                mismatch = False
                mismatch_expl = None
                side_effects = []

            payload = {
                "user_intent": user_intent,
                "category": category,
                "confidence_score": 0.96,
                "predicted_side_effects": side_effects,
                "intent_mismatch": mismatch,
                "mismatch_explanation": mismatch_expl
            }

            return {
                "content": json.dumps(payload),
                "model_used": "deterministic_test_provider",
                "status": "success"
            }

        # -------------------------------------------------------------
        # Explainability Generator Prompt Handling
        # -------------------------------------------------------------
        payload = {
            "technical_rationale": "Command received risk score analysis. Affects system files and potential background services.",
            "eli5_rationale": "Warning! Running this command will permanently affect target files and services.",
            "why_dangerous_bullets": [
                "Executes elevated privilege operational command",
                "Potential unrecoverable file system modifications"
            ],
            "safe_alternatives": [
                {
                    "command": "trash-put /tmp/demo",
                    "explanation": "Moves files safely to user trash directory instead of permanent unlinking.",
                    "safety_gain": "100% Recoverable via trash-restore"
                }
            ],
            "undo_playbook": "Restore from Timeshift snapshot or check git stash."
        }

        return {
            "content": json.dumps(payload),
            "model_used": "deterministic_test_provider",
            "status": "success"
        }

@pytest.fixture(autouse=True)
def enable_deterministic_test_llm_provider(monkeypatch):
    """
    Autouse fixture that installs the DeterministicTestLLMProvider across all backend pytest runs.
    Guarantees sub-second offline test execution with zero external socket connectivity.
    """
    provider = DeterministicTestLLMProvider()
    monkeypatch.setattr(llm_service, "generate_completion", provider.mock_generate_completion)
