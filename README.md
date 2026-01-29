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

## Project Structure

```text
.
├── backend/                # FastAPI Orchestration Service
│   ├── src/
│   │   ├── core/           # Generation pipeline & orchestrators
│   │   ├── routes/         # API endpoints (Jobs, Intents)
│   │   └── database/       # Job state management (Supabase)
│   └── .env.example        # Backend config template
├── frontend/               # Next.js Dashboard UI
│   ├── app/                # App Router (Dashboard implementation)
│   ├── components/         # Reactive UI (Pipeline monitoring, Monaco editor)
│   └── lib/                # API client & utilities
└── testsuitegen/           # Core Python Logic (Parsing & Generation)
    └── src/
        ├── generators/     # Intent extraction & IR construction
        ├── llm_enhancer/   # Multi-provider AI logic (Gemini, Groq, local)
        └── testsuite/      # Jinja2 rendering templates
```

- **[Frontend](frontend/README.md)**: Real-time dashboard for managing generation jobs, streaming logs, and reviewing generated artifacts.
- **[Backend](backend/README.md)**: RESTful API that coordinates between the user interface and the core generator.
- **[TestSuiteGen Core](testsuitegen/README.md)**: The heart of the platform, containing the parsers, IR builders, and LLM enhancers.

## Key Features

- **Multi-Source Ingestion**: Generate tests from OpenAPI/Swagger definitions, Python source code (AST-based), or TypeScript files.
- **AI-Enhanced Payloads**: Leverages state-of-the-art LLMs (Gemini, Groq, local Llama) to generate context-aware, realistic validation data beyond simple random values.
- **Intent Discovery**: Automatically identifies application intent, identifying critical paths, authentication requirements, and data constraints.
- **Polyglot Test Generation**: Renders production-ready test code in multiple frameworks including **Pytest** and **Jest**.
- **Real-time Pipeline**: Track generation progress step-by-step through a modern, reactive interface with live status updates.
- **Resilience & Reliability**: Built-in **Circuit Breaker** patterns and exponential backoff to handle LLM API rate limits and failures gracefully.
- **Artifact Management**: Integrated storage via Supabase for generated test suites and execution reports.

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
- [ ] **Coverage Analysis**: Fine-tuned feedback loops to generate tests targeting specific missing coverage gaps.
- [ ] **Custom Templates**: Expanded support for more languages and custom user-defined test templates.
