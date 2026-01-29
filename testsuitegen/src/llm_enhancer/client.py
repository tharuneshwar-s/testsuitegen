# llm_enhancer/client.py

from typing import Optional
from testsuitegen.src.config.settings import LLMProviders
from testsuitegen.src.llm_enhancer.providers.config import ProviderConfig
from testsuitegen.src.llm_enhancer.providers.factory import (
    ProviderFactory,
    BaseLLMProvider,
)


# Global provider cache to avoid recreating providers
_provider_cache = {}


def _clone_config_with_model(
    base_config: ProviderConfig, model_override: str
) -> ProviderConfig:
    return ProviderConfig(
        name=base_config.name,
        model=model_override or base_config.model,
        temperature=base_config.temperature,
        max_tokens=base_config.max_tokens,
        timeout=base_config.timeout,
        base_url=base_config.base_url,
    )


def _get_provider(
    provider_enum: LLMProviders, model_override: str = None
) -> BaseLLMProvider:
    """Get or create a provider instance keyed by provider name and model."""

    provider_name = provider_enum.value.name
    cache_key = f"{provider_name}:{model_override or provider_enum.value.model}"

    if cache_key not in _provider_cache:
        config = (
            _clone_config_with_model(provider_enum.value, model_override)
            if model_override
            else provider_enum.value
        )

        _provider_cache[cache_key] = ProviderFactory.create_provider(
            provider_config=config
        )

    return _provider_cache[cache_key]


def llm_generate(
    prompt: str,
    provider: Optional[str] = None,
    model_override: Optional[str] = None,
    max_retries: int = 3,
    **kwargs,
) -> str:
    """Generate text using the selected LLM provider.

    Args:
        prompt: Input prompt
        provider: Provider name to use (None = use default provider)
        max_retries: Maximum retry attempts
        **kwargs: Additional provider-specific arguments (e.g., response_format)

    Returns:
        Generated text

    Raises:
        ValueError: If provider is unknown or not configured
        Exception: If generation fails
    """
    # Resolve provider
    if provider:
        provider_enum = LLMProviders.get_by_name(provider)
        if not provider_enum:
            raise ValueError(f"Unknown provider: {provider}")
    else:
        provider_enum = LLMProviders.get_default_provider()

    if not provider_enum:
        raise ValueError("No LLM provider configured")

    if not provider_enum.value.is_available:
        raise ValueError(
            f"Provider '{provider_enum.value.name}' is not properly configured"
        )

    provider_instance = _get_provider(provider_enum, model_override=model_override)
    return provider_instance.generate(prompt, max_retries=max_retries, **kwargs)
