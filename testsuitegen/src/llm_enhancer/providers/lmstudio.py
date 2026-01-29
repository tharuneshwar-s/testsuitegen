"""LM Studio provider using OpenAI-compatible SDK."""

import time
from testsuitegen.src.llm_enhancer.providers.base import BaseLLMProvider


class LMStudioProvider(BaseLLMProvider):
    """LM Studio local LLM provider (OpenAI-compatible)."""

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: str = "local-model",
        api_key: str = "not-needed",
        temperature: float = 0.01,
        max_tokens: int = 8000,
        timeout: int = 90,
    ):
        """Initialize LM Studio provider.

        Args:
            base_url: LM Studio server URL (default: http://localhost:1234/v1)
            model: Model identifier (use server's loaded model name)
            api_key: API key (not needed for local LM Studio)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout
        """
        super().__init__(
            model=model, temperature=temperature, max_tokens=max_tokens, timeout=timeout
        )
        self.base_url = base_url
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client for LM Studio."""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)
            except ImportError:
                raise ImportError("openai SDK not installed. Run: pip install openai")
        return self._client

    def generate(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """Generate text using LM Studio.

        Args:
            prompt: Input prompt
            max_retries: Maximum retry attempts
            **kwargs: Extra arguments for the client (e.g. response_format)

        Returns:
            Generated text
        """
        client = self._get_client()

        # Extract extra params for OpenAI client (e.g. response_format)
        extra_params = {
            k: v
            for k, v in kwargs.items()
            if k
            in ["response_format", "functions", "function_call", "tools", "tool_choice"]
        }

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                    **extra_params,
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = str(e).lower()
                # Retry on connection errors or server errors
                if attempt < max_retries - 1 and (
                    "connection" in error_msg
                    or "timeout" in error_msg
                    or "503" in error_msg
                ):
                    wait_time = 2**attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise Exception(f"LM Studio generation failed: {e}")

        raise Exception("LM Studio generation failed after all retries")

    @property
    def is_available(self) -> bool:
        """Check if LM Studio is available.

        Note: We assume availability if base_url is set.
        Actual server availability is checked on first request.
        """
        return bool(self.base_url)

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "lmstudio"
