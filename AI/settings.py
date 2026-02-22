# AI/settings.py
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Which LLM to use: 'openai' | 'ollama' | 'mock'
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")

    # --- OpenAI ---
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # --- Ollama ---
    # Allow overriding model and server location without code changes
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # --- Timeouts & generation ---
    # Read timeout (server processing). First run of a model can take a while.
    timeout_seconds: int = int(os.getenv("AI_TIMEOUT", "300"))          # was 20
    # Connect timeout (just establishing TCP)
    timeout_connect_seconds: int = int(os.getenv("AI_CONNECT_TIMEOUT", "10"))
    max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "400"))
    language: str = os.getenv("AI_LANG", "en")

settings = Settings()
