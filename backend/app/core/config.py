import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ShellGuard Runtime"
    ENGINE_NAME: str = "ShellGuard AI Engine"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # AI Model Defaults & Router
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    FALLBACK_LLM_MODEL: str = "ollama/qwen2.5-coder:7b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Vector DB (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # Adaptive Risk & Persona Settings
    DEFAULT_PERSONA: str = "Professional"  # "Beginner" or "Professional"
    DEFAULT_RISK_THRESHOLD: int = 65
    FORCE_INTERCEPT: bool = True
    PRIVACY_FIRST_LOCAL_ONLY: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
