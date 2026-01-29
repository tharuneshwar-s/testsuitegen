import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from supabase import create_client, Client
from backend.src.models.jobs import JobStatus, JobRequest
from backend.src.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def create_job(job_request: JobRequest) -> str:
    """Create a new job and return its ID."""
    job_id = str(uuid4())

    try:
        supabase.table("jobs").insert(
            {
                "id": job_id,
                "status": JobStatus.PENDING.value,
                "source_type": job_request.source_type,
                "base_url": str(job_request.base_url),
                "progress": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).execute()

        # Convert Pydantic model to JSON-safe dict
        request_data = json.loads(job_request.json())

        supabase.table("job_requests").insert(
            {
                "job_id": job_id,
                "spec_data": (
                    job_request.spec_data
                    if isinstance(job_request.spec_data, str)
                    else ""
                ),
                "request_payload": request_data,
            }
        ).execute()

        logger.info("Job created: %s", job_id)
        return job_id
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to create job in Supabase")
        raise


async def get_job(job_id: str) -> Optional[Dict]:
    """Retrieve job data with logs and artifacts."""
    try:
        job_response = supabase.table("jobs").select("*").eq("id", job_id).execute()
        if not job_response.data:
            return None

        job = job_response.data[0]

        logs_response = (
            supabase.table("job_logs")
            .select("message, log_type, created_at")
            .eq("job_id", job_id)
            .order("created_at")
            .execute()
        )
        logs = (
            [{"message": log["message"], "log_type": log.get("log_type", "info"), "created_at": log["created_at"]} for log in logs_response.data] if logs_response.data else []
        )

        artifacts_response = (
            supabase.table("job_artifacts")
            .select("artifact_path")
            .eq("job_id", job_id)
            .execute()
        )
        artifacts = (
            [art["artifact_path"] for art in artifacts_response.data]
            if artifacts_response.data
            else []
        )

        return {
            "status": job["status"],
            "created_at": job["created_at"],
            "progress": job["progress"],
            "logs": logs,
            "artifacts": artifacts,
            "error_message": job.get("error_message"),
        }
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to retrieve job from Supabase")
        return None


async def update_status(job_id: str, status: JobStatus):
    """Update job status."""
    try:
        supabase.table("jobs").update(
            {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", job_id).execute()

        _add_log(job_id, f"System: Job status changed to {status.value}")
        logger.debug("Job status updated: %s -> %s", job_id, status.value)
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to update job status")


async def append_log(job_id: str, log_message: str, log_type: str = "info"):
    """Append a log message to the job."""
    _add_log(job_id, log_message, log_type)


def _add_log(job_id: str, log_message: str, log_type: str = "info"):
    """Add log entry to database."""
    try:
        supabase.table("job_logs").insert(
            {
                "job_id": job_id,
                "message": log_message,
                "log_type": log_type,
                "created_at": datetime.utcnow().isoformat(),
            }
        ).execute()
    except Exception as exc:  # noqa: B902
        logger.warning("Failed to add log for job %s: %s", job_id, exc)


async def add_artifact(job_id: str, artifact_path: str):
    """Register a generated artifact to the job."""
    try:
        supabase.table("job_artifacts").insert(
            {
                "job_id": job_id,
                "artifact_path": artifact_path,
                "created_at": datetime.utcnow().isoformat(),
            }
        ).execute()
        logger.debug("Artifact added: %s -> %s", job_id, artifact_path)
    except Exception as exc:  # noqa: B902
        logger.warning("Failed to add artifact for job %s: %s", job_id, exc)


async def set_progress(job_id: str, percent: int):
    """Update job progress percentage."""
    try:
        supabase.table("jobs").update(
            {
                "progress": percent,
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", job_id).execute()
        logger.debug("Job progress updated: %s -> %d%%", job_id, percent)
    except Exception as exc:  # noqa: B902
        logger.warning("Failed to set progress for job %s: %s", job_id, exc)


async def mark_failed(job_id: str, error: str):
    """Mark job as failed with error message."""
    try:
        supabase.table("jobs").update(
            {
                "status": JobStatus.FAILED.value,
                "error_message": error,
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", job_id).execute()

        _add_log(job_id, f"System: Job FAILED - {error}")
        logger.error("Job marked as failed: %s - %s", job_id, error)
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to mark job as failed")


async def mark_completed(job_id: str):
    """Mark job as successfully completed."""
    try:
        supabase.table("jobs").update(
            {
                "status": JobStatus.COMPLETED.value,
                "progress": 100,
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", job_id).execute()

        _add_log(job_id, "System: Job COMPLETED successfully.")
        logger.info("Job completed: %s", job_id)
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to mark job as completed")


async def save_endpoints(job_id: str, endpoints: List[dict]):
    """Save extracted API endpoints for the job."""
    try:
        supabase.table("jobs").update(
            {
                "endpoints": endpoints,
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).eq("id", job_id).execute()
        logger.debug("Saved %d endpoints for job %s", len(endpoints), job_id)
    except Exception as exc:  # noqa: B902
        logger.warning("Failed to save endpoints for job %s: %s", job_id, exc)


async def get_endpoints(job_id: str) -> List[dict]:
    """Get endpoints for a job."""
    try:
        response = supabase.table("jobs").select("endpoints").eq("id", job_id).execute()
        if response.data and response.data[0].get("endpoints"):
            return response.data[0]["endpoints"]
        return []
    except Exception as exc:  # noqa: B902
        logger.warning("Failed to get endpoints for job %s: %s", job_id, exc)
        return []
