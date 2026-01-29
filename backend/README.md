# TestSuiteGen Backend

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-DB-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-Server-20232A?style=for-the-badge)
![SlowAPI](https://img.shields.io/badge/SlowAPI-Rate_Limit-blue?style=for-the-badge)

The backend service for TestSuiteGen, providing the RESTful API and orchestration engine for the test generation pipeline. It bridges the frontend interface with the core logic library.

## Setup & Installation

1.  **Navigate to the backend directory:**

    ```bash
    cd backend
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

Start the application using Uvicorn with hot-reloading:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Structure

```text
backend/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Environment variables and global settings
│   ├── exceptions.py           # API-specific exception handlers
│   ├── rate_limiter.py         # Request rate limiting logic
│   ├── core/                   # Business Logic & Orchestration
│   │   ├── intents.py          # Intent analysis orchestration
│   │   ├── intermediate_request.py # IR processing
│   │   ├── parsing.py          # Specification parsing wrappers
│   │   ├── payloads.py         # Payload enhancement logic
│   │   └── pipeline.py         # Main generation pipeline coordination
│   ├── database/               # Data Persistence
│   │   └── store.py            # Job state and status management
│   ├── models/                 # Pydantic Schemas
│   │   ├── intents.py          # Schema for test intents
│   │   ├── jobs.py             # Schema for generation jobs
│   │   ├── llms.py             # LLM configuration models
│   │   └── payloads.py         # Payload data models
│   ├── monitoring/             # Logging and telemetry
│   │   ├── log_capture.py      # Real-time log capture
│   │   └── logging.py          # Logger configuration
│   └── routes/                 # API Endpoint Definitions
│       ├── intents/
│       │   └── controller.py   # Intent extraction endpoints
│       └── jobs/
│           ├── controller.py   # Job management endpoints
│           └── service.py      # Job-related business logic
├── requirements.txt            # Main dependencies
├── requirements-dev.txt        # Development dependencies
└── .env.example                # Configuration template
```

## Environment Variables

The backend requires the following configuration in a `.env` file:

| Variable                  | Description                      | Example                                       |
| :------------------------ | :------------------------------- | :-------------------------------------------- |
| `SUPABASE_URL`            | Your Supabase instance URL       | `your_url`                                    |
| `SUPABASE_KEY`            | Supabase Service Role/Anon Key   | `your_key`                                    |
| `SUPABASE_STORAGE_BUCKET` | Bucket name for artifacts        | `your_bucket`                                 |
| `ENVIRONMENT`             | Deployment environment           | `development`                                 |
| `BACKEND_HOST`            | Host to run the server on        | `0.0.0.0`                                     |
| `BACKEND_PORT`            | Port to run the server on        | `8000`                                        |
| `CORS_ORIGINS`            | Allowed CORS origins (comma-sep) | `http://localhost:3000,http://localhost:3001` |


## Core Responsibilities

- **Spec Parsing**: Converts various API spec formats into standard representations.
- **Pipeline Orchestration**: Manages the sequential steps of intent discovery, IR generation, and code enhancement.
- **Progress Tracking**: Reports real-time status updates back to the frontend through Supabase/Websockets.
- **Artifact Hosting**: Manages storage and retrieval of generated test suites.
