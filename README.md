# TestSuiteGen

### Core Stack & Frameworks

![Python](https://img.shields.io/badge/python-3.11+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Next.js](https://img.shields.io/badge/next.js-v15-000000?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-v5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwind-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-DB-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)

### AI & Parsing Engine

![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)
![Tree-sitter](https://img.shields.io/badge/Tree%20Sitter-Parsing-43B02A?style=for-the-badge&logo=treesitter&logoColor=white)
![Python AST](https://img.shields.io/badge/Python%20AST-Parsing-306998?style=for-the-badge&logo=python&logoColor=white)
![vLLM](https://img.shields.io/badge/vLLM-Supported-blue?style=for-the-badge)
![LM Studio](https://img.shields.io/badge/LM_Studio-Local-purple?style=for-the-badge)

### Utilities & Tools

![Monaco Editor](https://img.shields.io/badge/Monaco_Editor-IDE-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Jinja2](https://img.shields.io/badge/jinja-3.0+-C63D14?style=for-the-badge&logo=jinja&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-Server-20232A?style=for-the-badge)
![SlowAPI](https://img.shields.io/badge/SlowAPI-Rate_Limit-blue?style=for-the-badge)
![Httpx](https://img.shields.io/badge/httpx-Async_HTTP-005571?style=for-the-badge)

**TestSuiteGen** is an AI-powered automated test generation platform. It ingests API specifications (OpenAPI, Swagger) or source code (Python, TypeScript), understands the logic using LLMs (Gemini, Llama, etc.), and generates comprehensive test suites (Pytest, Jest) with realistic payloads and edge cases.

## Architecture: Deterministic 5-Stage Pipeline

TestSuiteGen uses a **deterministic pipeline** that ensures consistent, reproducible test generation:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    TESTSUITEGEN PIPELINE                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │   STAGE 1    │     │   STAGE 2    │     │   STAGE 3    │     │   STAGE 4    │     │   STAGE 5    │
     │   PARSING    │────▶│   IR BUILD   │────▶│    INTENT    │────▶│   PAYLOAD    │────▶│  TESTSUITE   │
     │              │     │              │     │  DISCOVERY   │     │  GENERATION  │     │  RENDERING   │
     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
            │                    │                    │                    │                    │
            ▼                    ▼                    ▼                    ▼                    ▼
     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │  OpenAPI     │     │  Unified IR  │     │  Test Intent │     │   Mutated    │     │  Pytest/Jest │
     │  Python AST  │     │  Operations  │     │   Catalog    │     │   Payloads   │     │  Test Files  │
     │  TypeScript  │     │  Schemas     │     │              │     │              │     │              │
     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### Pipeline Stages

| Stage | Component | Description | Key Files |
|-------|-----------|-------------|-----------|
| **1. Parsing** | `parsers/` | Parse source into normalized AST/Schema | `openapi_parser/`, `python_parser/`, `typescript_parser/` |
| **2. IR Build** | `generators/ir_generator/` | Build unified Intermediate Representation | `builder.py`, `validator.py` |
| **3. Intent Discovery** | `generators/intent_generator/` | Identify testable scenarios per operation | `openapi_intent/`, `python_intent/`, `typescript_intent/` |
| **4. Payload Generation** | `generators/payloads_generator/` | Generate valid payloads, then mutate per intent | `generator.py`, `mutator.py` |
| **5. Test Rendering** | `testsuite/` | Render Jinja2 templates + optional LLM polish | `generator.py`, `templates.py`, `analyzer.py`, `planner.py`, `compiler.py` |

### Stage 5: Test Rendering Sub-Pipeline

The test rendering stage uses a **deterministic sub-pipeline** for API tests:

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        TESTSUITE RENDERING SUB-PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐         │
│  │   Static     │   │    Setup     │   │   Fixture    │   │   Template   │         │
│  │  Analyzer    │──▶│   Planner    │──▶│   Compiler   │──▶│   Renderer   │         │
│  │              │   │              │   │              │   │              │         │
│  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘         │
│        │                  │                  │                  │                  │
│        ▼                  ▼                  ▼                  ▼                  │
│  Detect resource    Plan resource      Generate pytest    Render final           │
│  dependencies       creation order     fixtures/Jest      test file              │
│  (GET needs ID)     (POST before GET)  beforeAll hooks                           │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼ (Optional)
                              ┌──────────────────┐
                              │   LLM Polisher   │
                              │  (Docs & Style)  │
                              └──────────────────┘
```

## Project Structure

```text
.
├── backend/                    # FastAPI Orchestration Service
│   ├── src/
│   │   ├── main.py             # Application entry point
│   │   ├── config.py           # Environment & settings
│   │   ├── core/               # Pipeline orchestration
│   │   │   ├── pipeline.py     # Main generation coordinator
│   │   │   ├── parsing.py      # Spec parsing wrappers
│   │   │   ├── intents.py      # Intent generation
│   │   │   └── payloads.py     # Payload processing
│   │   ├── routes/             # API endpoints
│   │   │   ├── jobs/           # Job management
│   │   │   └── intents/        # Intent extraction
│   │   ├── models/             # Pydantic schemas
│   │   ├── database/           # Supabase integration
│   │   └── monitoring/         # Logging & telemetry
│   └── requirements.txt
│
├── frontend/                   # Next.js Dashboard UI
│   ├── app/                    # App Router pages
│   ├── components/             # React components
│   │   ├── EditorPanel.tsx     # Monaco code editor
│   │   ├── PipelineStatus.tsx  # Generation progress
│   │   ├── LogViewer.tsx       # Real-time logs
│   │   └── ArtifactsTabs.tsx   # Generated files viewer
│   └── lib/                    # API client & utilities
│
└── testsuitegen/               # Core Python Library
    └── src/
        ├── parsers/            # Source Code Parsers
        │   ├── openapi_parser/ # OpenAPI/Swagger
        │   ├── python_parser/  # Python AST
        │   └── typescript_parser/ # Tree-sitter TS
        │
        ├── generators/         # Generation Logic
        │   ├── ir_generator/   # IR construction
        │   ├── intent_generator/ # Intent discovery
        │   │   ├── openapi_intent/
        │   │   ├── python_intent/
        │   │   └── typescript_intent/
        │   └── payloads_generator/ # Payload mutation
        │       ├── openapi_mutator/
        │       ├── python_mutator/
        │       └── typescript_mutator/
        │
        ├── testsuite/          # Test Rendering (NEW PIPELINE)
        │   ├── generator.py    # Main orchestrator
        │   ├── templates.py    # Jinja2 templates
        │   ├── analyzer.py     # Static analysis
        │   ├── planner.py      # Setup planning
        │   └── compiler.py     # Fixture compilation
        │
        └── llm_enhancer/       # AI Enhancement Layer
            ├── providers/      # LLM integrations
            │   ├── gemini.py
            │   ├── groq.py
            │   ├── vllm.py
            │   └── lmstudio.py
            ├── python_enhancer/
            ├── typescript_enhancer/
            ├── payload_enhancer/
            └── circuit_breaker.py
```

- **[Frontend](frontend/README.md)**: Real-time dashboard for managing generation jobs, streaming logs, and reviewing generated artifacts.
- **[Backend](backend/README.md)**: RESTful API that coordinates between the user interface and the core generator.
- **[TestSuiteGen Core](testsuitegen/README.md)**: The heart of the platform, containing the parsers, IR builders, and LLM enhancers.

## Key Features

- **Multi-Source Ingestion**: Generate tests from OpenAPI/Swagger definitions, Python source code (AST-based), or TypeScript files (Tree-sitter).
- **Deterministic Pipeline**: 5-stage pipeline ensures consistent, reproducible test generation without LLM randomness in core logic.
- **Intent Discovery**: Automatically identifies test scenarios including `HAPPY_PATH`, `REQUIRED_FIELD_MISSING`, `TYPE_VIOLATION`, `BOUNDARY_*`, `PATTERN_MISMATCH`, and more.
- **Smart Fixture Generation**: Static analyzer detects resource dependencies, planner orders creation, compiler generates pytest fixtures/Jest hooks.
- **AI-Enhanced Documentation**: Optional LLM polisher improves test readability while preserving payload integrity.
- **Polyglot Test Generation**: Renders production-ready test code in **Pytest** and **Jest** frameworks.
- **Real-time Pipeline**: Track generation progress step-by-step through a modern, reactive interface.
- **Resilience & Reliability**: Built-in **Circuit Breaker** patterns and exponential backoff for LLM API handling.
- **Artifact Management**: Integrated storage via Supabase for generated test suites.

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Supabase Project

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-org/testsuitegen.git
    cd testsuitegen
    ```

2.  **Environment Configuration:**
    Create `.env` files in both `backend/` and `frontend/` folders. Refer to the `.env.example` files in each directory for required variables.

3.  **Launch the Platform:**
    Detailed setup steps for each component can be found in their respective READMEs:
    - [Backend Setup Guide](backend/README.md)
    - [Frontend Setup Guide](frontend/README.md)
    - [Core Library Details](testsuitegen/README.md)

## Future Roadmap

- [ ] **MCP Server Integration**: Generate test suites directly from your IDE using the Model Context Protocol.
- [ ] **Export Options**: Support for exporting generated tests to Postman Collections, Bruno, and Insomnia.
- [ ] **Continuous Integration**: GitHub Actions and GitLab CI integrations for automated test suite updates.
- [ ] **Custom Templates**: Expanded support for more languages and custom user-defined test templates.
