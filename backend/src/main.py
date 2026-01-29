"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.src.config import (
    CORS_ORIGINS,
    UPLOAD_DIR,
    ARTIFACT_DIR,
    LOG_DIR,
    BACKEND_HOST,
    BACKEND_PORT,
)
from backend.src.monitoring.logging import LogLevels, configure_logging
from backend.src.rate_limiter import limiter
from backend.src.routes.jobs.controller import router as jobs_router
from backend.src.routes.intents.controller import router as intents_router

configure_logging(LogLevels.info)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TestSuiteGen API",
    description="Backend for the Deterministic Test Suite Generator.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("Starting TestSuiteGen Backend...")
    logger.info("Upload Directory: %s", UPLOAD_DIR)
    logger.info("Artifact Directory: %s", ARTIFACT_DIR)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    yield

    # Shutdown
    logger.info("Shutting down TestSuiteGen Backend...")


app.router.lifespan_context = lifespan

app.include_router(jobs_router, prefix="/api/v1")
app.include_router(intents_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Welcome to TestSuiteGen Backend API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/health")
def health_check():
    """Health check endpoint for load balancer probes."""
    return {"status": "healthy", "service": "testsuitegen-backend", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Server starting at http://%s:%s", BACKEND_HOST, BACKEND_PORT)

    uvicorn.run(
        "main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True, log_level="info"
    )
