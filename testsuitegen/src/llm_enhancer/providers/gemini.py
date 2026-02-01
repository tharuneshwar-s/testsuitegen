"""Google Gemini provider using official SDK."""

import time
from testsuitegen.src.llm_enhancer.providers.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.01,
        max_tokens: int = 8000,
        timeout: int = 90,
    ):
        """Initialize Gemini provider.

        Args:
            api_key: Google Gemini API key
            model: Model name (default: gemini-2.0-flash)
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
        """Lazy initialization of Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError(
                    "google-generativeai SDK not installed. Run: pip install google-generativeai"
                )
        return self._client

    def generate(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """Generate text using Gemini.

        Args:
            prompt: Input prompt
            max_retries: Maximum retry attempts

        Returns:
            Generated text
        """
        client = self._get_client()

        for attempt in range(max_retries):
            try:
                response = client.generate_content(
                    prompt,
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_tokens,
                    },
                )
                return response.text
            except Exception as e:
                error_msg = str(e).lower()
                # Retry on rate limits or server errors
                if attempt < max_retries - 1 and (
                    "503" in error_msg or "429" in error_msg or "rate" in error_msg
                ):
                    wait_time = 2**attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Gemini generation failed: {e}")

        raise Exception("Gemini generation failed after all retries")

    @property
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return bool(self.api_key)

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "gemini"
