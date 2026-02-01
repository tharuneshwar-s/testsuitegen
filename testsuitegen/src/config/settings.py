"""
Application-wide configuration settings.

This module loads environment variables and provides configuration
constants for all components of the Test Suite Generator.
"""

import os
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Import ProviderConfig from providers module
from testsuitegen.src.llm_enhancer.providers.config import ProviderConfig


env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class LLMProviders(Enum):
    """
    Enumeration of available LLM providers with their default configurations.

    Each provider includes:
    - Model selection
    - Temperature for deterministic output
    - Token limits
    - Timeout settings
    """

    GEMINI = ProviderConfig(
        name="gemini",
        model="gemini-2.0-flash",
        temperature=0.01,
        max_tokens=8000,
        timeout=90,
    )

    GROQ = ProviderConfig(
        name="groq",
        model="llama-3.3-70b-versatile",
        temperature=0.01,
        max_tokens=8000,
        timeout=90,
    )

    LMSTUDIO = ProviderConfig(
        name="lmstudio",
        model="meta-llama-3.1-8b-instruct",
        # model="versatile-llama-3-8b",
        temperature=0.001,
        max_tokens=4096 * 2,
        timeout=90,
        base_url="http://localhost:1234/v1",
    )
    VLLM = ProviderConfig(
        name="vllm",
        model="Qwen/Qwen2.5-Coder-1.5B-Instruct",
        temperature=0.01,
        max_tokens=8000,
        timeout=int(os.getenv("VLLM_TIMEOUT", "300")),
        base_url=os.getenv("VLLM_BASE_URL", ""),
    )
    AIRLLM = ProviderConfig(
        name="airllm",
        model="",
        temperature=0.01,
        max_tokens=8000,
        timeout=90,
    )

    @classmethod
    def get_by_name(cls, name: str) -> Optional["LLMProviders"]:
        """
        Get provider enum by name (case-insensitive).

        Args:
            name: Provider name string

        Returns:
            LLMProviders enum or None if not found
        """
        name = name.lower()
        for provider in cls:
            if provider.value.name == name:
                return provider
        return None

    @classmethod
    def get_available_providers(cls) -> list["LLMProviders"]:
        """
        Get list of all configured and available providers.

        Returns:
            List of LLMProviders that have valid API keys
        """
        return [p for p in cls if p.value.is_available]

    @classmethod
    def get_default_provider(cls) -> Optional["LLMProviders"]:
        """
        Get default provider based on availability and preference order.

        Preference: lmstudio > airllm > vllm > gemini > groq
        (Local models preferred over cloud for privacy/cost)

        Returns:
            First available provider in preference order, or None
        """
        preference_order = [
            cls.LMSTUDIO,
            cls.AIRLLM,
            cls.VLLM,
            cls.GEMINI,
            cls.GROQ,
        ]
        for provider in preference_order:
            if provider.value.is_available:
                return provider
        return None


# Default provider/model (mandatory LLM enabled by design)
DEFAULT_LLM_PROVIDER = LLMProviders.get_default_provider()
if DEFAULT_LLM_PROVIDER:
    DEFAULT_LLM_MODEL = DEFAULT_LLM_PROVIDER.value.model
else:
    DEFAULT_LLM_MODEL = None

# Global flag: Is LLM enhancement enabled? (any provider available)
LLM_ENABLED = len(LLMProviders.get_available_providers()) > 0


# ==============================================================================
# CIRCUIT BREAKER CONFIGURATION
# ==============================================================================

# Number of consecutive failures before circuit breaker trips
# This prevents cascading failures and saves API costs
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(
    os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")
)


# ==============================================================================
# RETRY CONFIGURATION
# ==============================================================================

# Maximum number of retry attempts for LLM calls
# Each retry uses exponential backoff
MAX_LLM_RETRIES = int(os.getenv("MAX_LLM_RETRIES", "3"))

# Base delay for exponential backoff (in seconds)
# Actual delays: base^1, base^2, base^3 (e.g., 2s, 4s, 8s)
EXPONENTIAL_BACKOFF_BASE = int(os.getenv("EXPONENTIAL_BACKOFF_BASE", "2"))


# ==============================================================================
# APPLICATION SETTINGS
# ==============================================================================

# Default output directory for generated artifacts
DEFAULT_OUTPUT_DIR = os.getenv("DEFAULT_OUTPUT_DIR", "artifacts")

# Default base URL for API testing
DEFAULT_BASE_URL = os.getenv("DEFAULT_BASE_URL", "http://localhost:8000")


# ==============================================================================
# CONFIGURATION SUMMARY (for debugging)
# ==============================================================================
