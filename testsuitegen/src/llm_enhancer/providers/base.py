"""Base provider interface for LLM providers."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.01,
        max_tokens: int = 8000,
        timeout: int = 90,
    ):
        """Initialize the provider with common settings.

        Args:
            model: Model name to use (provider-specific)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    @abstractmethod
    def generate(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """Generate text from the LLM.

        Args:
            prompt: The input prompt
            max_retries: Maximum number of retry attempts for transient errors

        Returns:
            Generated text response

        Raises:
            Exception: If generation fails after all retries
        """
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured and available.

        Returns:
            True if provider can be used, False otherwise
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this provider.

        Returns:
            Provider name (e.g., "gemini", "groq", "lmstudio")
        """
        pass
