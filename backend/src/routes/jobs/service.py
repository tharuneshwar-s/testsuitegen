import asyncio
import logging
from typing import Set

from backend.src.core.pipeline import execute_job
from backend.src.database import store
from backend.src.exceptions import JobCreationError, JobNotFoundError
from backend.src.models.jobs import JobRequest, JobResponse

logger = logging.getLogger(__name__)

_background_tasks: Set[asyncio.Task] = set()


def _create_background_task(coro):
    """Create and track a background task."""
    task = asyncio.create_task(coro)
    _background_tasks.add(task)

    def _on_task_done(t):
        _background_tasks.discard(t)
        if t.exception() is not None:
            logger.exception("Background task failed", exc_info=t.exception())

    task.add_done_callback(_on_task_done)
    return task


async def create_job_(job: JobRequest):
    """Create a job and start background processing."""
    try:
        job_id = await store.create_job(job)
        _create_background_task(execute_job(job_id, job.dict()))
        return job_id
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to create job")
        raise JobCreationError(str(exc)) from exc


async def get_job_status_data(job_id: str) -> JobResponse:
    """Retrieve job status data."""
    job_data = await store.get_job(job_id)
    if not job_data:
        raise JobNotFoundError()
    return job_data
