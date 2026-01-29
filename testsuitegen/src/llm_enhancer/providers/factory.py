"""Provider factory for creating LLM provider instances."""

from testsuitegen.src.llm_enhancer.providers.base import BaseLLMProvider
from testsuitegen.src.llm_enhancer.providers.gemini import GeminiProvider
from testsuitegen.src.llm_enhancer.providers.groq import GroqProvider
from testsuitegen.src.llm_enhancer.providers.lmstudio import LMStudioProvider
from testsuitegen.src.llm_enhancer.providers.vllm import VLLMProvider
from testsuitegen.src.llm_enhancer.providers.airllm import AirLLMProvider
from testsuitegen.src.llm_enhancer.providers.config import ProviderConfig


class ProviderFactory:
    """Factory for creating and managing LLM providers."""

    @staticmethod
    def create_provider(provider_config: ProviderConfig) -> BaseLLMProvider:
        """Create an LLM provider instance from ProviderConfig.

        Args:
            provider_config: Provider configuration from enum

        Returns:
            Configured provider instance

        Raises:
            ValueError: If provider_type is unknown or not configured
        """
        provider_name = provider_config.name.lower()
        api_key = provider_config.get_api_key()

        if provider_name == "gemini":
            if not api_key:
                raise ValueError("Gemini provider requires GEMINI_API_KEY in .env")
            return GeminiProvider(
                api_key=api_key,
                model=provider_config.model,
                temperature=provider_config.temperature,
                max_tokens=provider_config.max_tokens,
                timeout=provider_config.timeout,
            )

        elif provider_name == "groq":
            if not api_key:
                raise ValueError("Groq provider requires GROQ_API_KEY in .env")
            return GroqProvider(
                api_key=api_key,
                model=provider_config.model,
                temperature=provider_config.temperature,
                max_tokens=provider_config.max_tokens,
                timeout=provider_config.timeout,
            )

        elif provider_name == "lmstudio":
            if not api_key:
                raise ValueError("LM Studio requires LMSTUDIO_BASE_URL in .env")
            return LMStudioProvider(
                base_url=provider_config.base_url or api_key,
                model=provider_config.model,
                api_key="not-needed",
                temperature=provider_config.temperature,
                max_tokens=provider_config.max_tokens,
                timeout=provider_config.timeout,
            )

        elif provider_name == "vllm":
            # vLLM setup (base_url from config or env)
            return VLLMProvider(
                base_url=provider_config.base_url
                or api_key,  # Use base_url from config
                model=provider_config.model,
                api_key="not-needed",  # vLLM typically doesn't check keys
                temperature=provider_config.temperature,
                max_tokens=provider_config.max_tokens,
                timeout=provider_config.timeout,
            )

        elif provider_name == "airllm":
            if not api_key:
                raise ValueError("AirLLM requires AIRLLM_MODEL_PATH in .env")
            return AirLLMProvider(
                model_path=api_key,
                model=provider_config.model,
                temperature=provider_config.temperature,
                max_tokens=provider_config.max_tokens,
                timeout=provider_config.timeout,
            )

        else:
            raise ValueError(
                f"Unknown provider: {provider_name}. Supported: gemini, groq, lmstudio, vllm, airllm"
            )
