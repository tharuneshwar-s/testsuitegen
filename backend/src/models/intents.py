from typing import List, Optional
from pydantic import BaseModel, Field


class IntentMetadata(BaseModel):
    """Metadata for a test intent."""

    id: str = Field(..., description="Unique intent ID.")
    category: Optional[str] = Field(None, description="Intent category.")
    description: str = Field(..., description="Human-readable description.")
    default_selected: bool = Field(
        default=False, description="Default selection state."
    )


class MetadataResponse(BaseModel):
    """Response containing available intents."""

    intents: List[IntentMetadata]
    categories: List[str] = Field(
        default_factory=list, description="Unique categories."
    )
    total_count: int
