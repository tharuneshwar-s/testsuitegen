"""LLM configuration models."""

from typing import Optional
from pydantic import BaseModel, Field


class EnhancementConfig(BaseModel):
    """LLM configuration for an enhancement step."""

    provider: str = "lmstudio"
    model: Optional[str] = Field(default=None, description="Model override.")


class LLMConfig(BaseModel):
    """LLM configuration for payload and test enhancement."""

    payload_enhancement: EnhancementConfig = Field(
        default_factory=EnhancementConfig,
        description="Config for payload enrichment.",
    )
    test_enhancement: EnhancementConfig = Field(
        default_factory=EnhancementConfig,
        description="Config for test polishing.",
    )
