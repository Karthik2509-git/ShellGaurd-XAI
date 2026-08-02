import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.services.llm_factory import llm_service

logger = logging.getLogger("shellguard.voice_nl")

class NLToCommandResult(BaseModel):
    natural_prompt: str
    generated_command: str
    explanation: str
    confidence: float

class VoiceNLShellEngine:
    """
    Voice / Natural Language Shell Translation Engine.
    Converts user requests ("Safely cleanup old docker build caches") into verified Linux commands.
    """

    NL_SYSTEM_PROMPT = """You are ShellGuard AI's Natural Language Shell Assistant.
Translate the user's natural language request into a precise, standard Linux shell command.

Respond strictly in JSON format:
{
  "generated_command": "docker builder prune -a -f",
  "explanation": "Clears unused build cache files from Docker builder engine",
  "confidence": 0.95
}"""

    async def translate_nl_to_command(self, prompt: str) -> NLToCommandResult:
        """
        Translates natural language string to shell command.
        """
        messages = [
            {"role": "system", "content": self.NL_SYSTEM_PROMPT},
            {"role": "user", "content": f"Translate to Linux shell command: {prompt}"}
        ]

        try:
            res = await llm_service.generate_completion(messages=messages, temperature=0.1)
            content = res.get("content", "")

            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(json_str)
            return NLToCommandResult(
                natural_prompt=prompt,
                generated_command=parsed.get("generated_command", "echo 'Could not translate prompt'"),
                explanation=parsed.get("explanation", "Natural language translation"),
                confidence=float(parsed.get("confidence", 0.8))
            )
        except Exception as e:
            logger.error(f"NL Translation error: {e}")
            return NLToCommandResult(
                natural_prompt=prompt,
                generated_command=f"echo 'Error translating prompt: {e}'",
                explanation="Failed to translate",
                confidence=0.0
            )

voice_nl_engine = VoiceNLShellEngine()
