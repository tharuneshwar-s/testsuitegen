from fastapi import APIRouter, HTTPException, Request

from backend.src.config import RATE_LIMIT_JOB_CREATION
from backend.src.exceptions import BackendError, JobNotFoundError
from backend.src.models.jobs import (
    JobRequest,
    JobResponse,
    JobStatusResponse,
    JobStatus,
)
from backend.src.rate_limiter import limiter
from backend.src.routes.jobs.service import (
    create_job_,
    get_job_status_data,
)
from backend.src.database.store import supabase


router = APIRouter()


@router.post("/jobs", response_model=JobResponse, status_code=202)
@limiter.limit(RATE_LIMIT_JOB_CREATION)
async def create_job(request: Request, job: JobRequest):
    """Create a new test generation job."""
    try:
        job_id = await create_job_(job)
        return JobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            estimated_time_sec=60,
        )
    except BackendError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get current job status."""
    try:
        job_data = await get_job_status_data(job_id)
        return JobStatusResponse(
            job_id=job_id,
            status=job_data["status"],
            created_at=job_data["created_at"],
            logs_count=len(job_data.get("logs", [])),
            progress=job_data.get("progress", 0),
            artifacts=job_data.get("artifacts", []),
            error_message=job_data.get("error_message"),
        )
    except JobNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.delete("/jobs/{job_id}", status_code=204)
async def delete_job(job_id: str):
    """Delete a job and all related data."""
    try:
        # Delete from jobs table - cascade will handle related tables
        result = supabase.table("jobs").delete().eq("id", job_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Job not found")

        return None
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete job: {str(exc)}"
        ) from exc
