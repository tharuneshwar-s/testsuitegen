"""Application configuration and environment settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "testsuitegen-artifacts")

# Server
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

# CORS
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Rate Limiting
RATE_LIMIT_JOB_CREATION = os.getenv("RATE_LIMIT_JOB_CREATION", "5/minute")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# File Paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "tmp" / "uploads"
ARTIFACT_DIR = BASE_DIR / "tmp" / "artifacts"
LOG_DIR = BASE_DIR / "logs"
