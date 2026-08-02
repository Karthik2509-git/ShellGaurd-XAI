import logging
from typing import Dict, Any, Optional, List
import litellm
from app.core.config import settings

logger = logging.getLogger("shellguard.llm")

class LLMFactory:
    """
    Multi-LLM Router providing high availability with automatic fallback 
    from cloud LLMs (OpenAI/Claude) to local SLMs (Ollama/Qwen).
    """

    def __init__(self):
        self.primary_model = settings.DEFAULT_LLM_MODEL
        self.fallback_model = settings.FALLBACK_LLM_MODEL
        litellm.drop_params = True

    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.2,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute completion with failover strategy.
        """
        try:
            # Attempt Primary Model
            logger.info(f"Invoking primary LLM: {self.primary_model}")
            kwargs = {
                "model": self.primary_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if response_format:
                kwargs["response_format"] = response_format
                
            response = await litellm.acompletion(**kwargs)
            return {
                "content": response.choices[0].message.content,
                "model_used": self.primary_model,
                "status": "success"
            }
        except Exception as primary_error:
            logger.warning(
                f"Primary LLM ({self.primary_model}) failed: {primary_error}. "
                f"Failing over to fallback model: {self.fallback_model}"
            )
            try:
                # Fallback to local / secondary model
                fallback_kwargs = {
                    "model": self.fallback_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "api_base": settings.OLLAMA_BASE_URL if "ollama" in self.fallback_model else None
                }
                response = await litellm.acompletion(**fallback_kwargs)
                return {
                    "content": response.choices[0].message.content,
                    "model_used": self.fallback_model,
                    "status": "fallback_success"
                }
            except Exception as fallback_error:
                logger.error(f"Fallback LLM ({self.fallback_model}) failed: {fallback_error}")
                # Mock offline safety rule response if all LLMs are unreachable
                return {
                    "content": "AI Service offline. Standard deterministic safety rules enforced.",
                    "model_used": "deterministic_offline_guard",
                    "status": "offline_fallback"
                }

llm_service = LLMFactory()
