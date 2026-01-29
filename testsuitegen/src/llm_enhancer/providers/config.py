"""
Provider configuration module.

Contains the ProviderConfig dataclass used by all LLM providers.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderConfig:
    """
    Configuration for a single LLM provider.

    Attributes:
        name: Provider identifier (e.g., 'gemini', 'groq')
        model: Model name/identifier for the provider
        temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
        max_tokens: Maximum tokens in response
        timeout: Request timeout in seconds
        base_url: Optional base URL for self-hosted providers
    """

    name: str
    model: str
    temperature: float
    max_tokens: int
    timeout: int
    base_url: Optional[str] = None

    def get_api_key(self) -> Optional[str]:
        """
        Retrieve API key from environment variables.

        Returns:
            API key string if configured, None otherwise
        """
        if self.name == "gemini":
            return os.getenv("GEMINI_API_KEY")
        elif self.name == "groq":
            return os.getenv("GROQ_API_KEY")
        elif self.name == "lmstudio":
            return os.getenv("LMSTUDIO_BASE_URL")
        elif self.name == "vllm":
            # For vLLM, we treat the base_url (if hardcoded) as the 'key' for availability
            return self.base_url or os.getenv("VLLM_BASE_URL")
        elif self.name == "airllm":
            return os.getenv("AIRLLM_MODEL_PATH")
        return None

    @property
    def is_available(self) -> bool:
        """
        Check if provider is properly configured and available.

        Returns:
            True if API key/configuration is present, False otherwise
        """
        key = self.get_api_key()
        return (key is not None and len(key) > 0) or (
            self.base_url is not None and len(self.base_url) > 0
        )
