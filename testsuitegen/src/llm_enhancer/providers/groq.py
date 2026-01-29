"""Groq provider using official SDK."""

import time
from typing import Optional
from testsuitegen.src.llm_enhancer.providers.base import BaseLLMProvider


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.01,
        max_tokens: int = 8000,
        timeout: int = 90,
    ):
        """Initialize Groq provider.

        Args:
            api_key: Groq API key
            model: Model name (default: llama-3.3-70b-versatile)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout
        """
        super().__init__(
            model=model, temperature=temperature, max_tokens=max_tokens, timeout=timeout
        )
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy initialization of Groq client."""
        if self._client is None:
            try:
                from groq import Groq

                self._client = Groq(api_key=self.api_key)
            except ImportError:
                raise ImportError("groq SDK not installed. Run: pip install groq")
        return self._client

    def generate(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """Generate text using Groq.

        Args:
            prompt: Input prompt
            max_retries: Maximum retry attempts

        Returns:
            Generated text
        """
        client = self._get_client()

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = str(e).lower()
                # Retry on rate limits or server errors
                if attempt < max_retries - 1 and (
                    "503" in error_msg or "429" in error_msg or "rate" in error_msg
                ):
                    wait_time = 2**attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Groq generation failed: {e}")

        raise Exception("Groq generation failed after all retries")

    @property
    def is_available(self) -> bool:
        """Check if Groq is available."""
        return bool(self.api_key)

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "groq"
