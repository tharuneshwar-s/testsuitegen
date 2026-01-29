from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CustomPayload(BaseModel):
    """User-defined custom test payload."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    intent_type: Optional[str] = Field(default=None, description="Mapped intent type.")
    payload: Dict[str, Any] = Field(..., description="Raw JSON payload.")
