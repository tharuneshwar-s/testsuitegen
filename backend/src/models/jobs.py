from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Union
from fastapi import UploadFile

from backend.src.models.llms import LLMConfig
from backend.src.models.payloads import CustomPayload


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobRequest(BaseModel):
    """Request model for creating a test generation job."""

    spec_data: Union[str, UploadFile] = Field(
        ...,
        description="Base64 encoded spec or UploadFile.",
    )

    source_type: str = Field(
        default="openapi",
        description="Source type: 'openapi', 'python', or 'typescript'.",
    )

    framework: str = Field(
        default="pytest",
        description="Test framework: 'pytest' (Python/API) or 'jest' (TypeScript).",
    )

    base_url: HttpUrl = Field(
        default="http://localhost:8000",
        description="Base URL for generated tests.",
    )
    llm_config: LLMConfig = Field(
        default_factory=LLMConfig, description="LLM enhancement settings."
    )

    target_intents: Optional[List[str]] = Field(
        default_factory=list,
        description="Specific intent IDs to generate.",
    )

    custom_payloads: List[CustomPayload] = Field(
        default_factory=list,
        description="User-defined custom payloads.",
    )


class JobResponse(BaseModel):
    """Response after creating a job."""

    job_id: str
    status: JobStatus
    estimated_time_sec: int = Field(
        default=60, description="Estimated time in seconds."
    )


class JobStatusResponse(BaseModel):
    """Response for job status polling."""

    job_id: str
    status: JobStatus
    created_at: str
    logs_count: int = 0
    progress: int = 0
    artifacts: List[str] = Field(
        default_factory=list, description="Generated file paths."
    )
    error_message: Optional[str] = None
