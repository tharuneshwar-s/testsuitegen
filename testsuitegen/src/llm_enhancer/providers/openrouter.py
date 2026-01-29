"""OpenRouter provider using OpenAI SDK (OpenAI-compatible API)."""

import time
from typing import Optional
from testsuitegen.src.llm_enhancer.providers.base import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter LLM provider using native SDK."""

    def __init__(
        self,
        api_key: str,
        model: str = "meta-llama/llama-3.1-8b-instruct:free",
        temperature: float = 0.01,
        max_tokens: int = 8000,
        timeout: int = 90,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        """Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key (get from openrouter.ai/settings/keys)
            model: Model identifier (e.g., 'meta-llama/llama-3.1-8b-instruct:free',
                   'nvidia/nemotron-3-nano-30b-a3b:free', 'qwen/qwen3-next-80b-a3b-instruct:free')
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout
            base_url: OpenRouter API base URL
        """
        super().__init__(
            model=model, temperature=temperature, max_tokens=max_tokens, timeout=timeout
        )
        self.api_key = api_key
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client for OpenRouter."""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                )
            except ImportError:
                raise ImportError("openai SDK not installed. Run: pip install openai")
        return self._client

    def generate(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """Generate text using OpenRouter.

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
                # Retry on rate limits, connection errors, or server errors
                if attempt < max_retries - 1 and (
                    "rate" in error_msg
                    or "429" in error_msg
                    or "503" in error_msg
                    or "connection" in error_msg
                    or "timeout" in error_msg
                ):
                    wait_time = 2**attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise Exception(f"OpenRouter generation failed: {e}")

        raise Exception("OpenRouter generation failed after all retries")

    @property
    def is_available(self) -> bool:
        """Check if OpenRouter is available."""
        return bool(self.api_key)

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "openrouter"
