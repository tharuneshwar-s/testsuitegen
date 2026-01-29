"""vLLM provider using OpenAI-compatible SDK."""

import time
from testsuitegen.src.llm_enhancer.providers.base import BaseLLMProvider
from testsuitegen.src.exceptions.exceptions import LLMFatalError


class VLLMProvider(BaseLLMProvider):
    """vLLM provider (OpenAI-compatible)."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "not-needed",
        temperature: float = 0.01,
        max_tokens: int = 8000,
        timeout: int = 90,
    ):
        """Initialize vLLM provider.

        Args:
            base_url: vLLM server URL
            model: Model identifier
            api_key: API key (usually ignored by vLLM, but passed for compatibility)
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
        """Lazy initialization of OpenAI client for vLLM."""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)
            except ImportError:
                raise ImportError("openai SDK not installed. Run: pip install openai")
        return self._client

    def generate(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """Generate text using vLLM.

        Args:
            prompt: Input prompt
            max_retries: Maximum retry attempts
            **kwargs: Extra arguments for the client

        Returns:
            Generated text
        """
        client = self._get_client()

        # Extract extra params for OpenAI client
        extra_params = {
            k: v
            for k, v in kwargs.items()
            if k
            in [
                "response_format",
                "functions",
                "function_call",
                "tools",
                "tool_choice",
                "extra_body",
            ]
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
                # Retry on connection errors or transient server errors
                if attempt < max_retries - 1 and (
                    "connection" in error_msg
                    or "timeout" in error_msg
                    or "503" in error_msg
                    or "502" in error_msg
                ):
                    wait_time = 2**attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                # Treat other errors (including 404 / bad route) as fatal
                raise LLMFatalError(f"vLLM generation failed: {e}")

        raise LLMFatalError("vLLM generation failed after all retries")

    @property
    def is_available(self) -> bool:
        """Check if vLLM is available.

        Assumes availability if base_url is configured.
        """
        return bool(self.base_url)

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "vllm"
