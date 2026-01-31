# TestSuiteGen Core Library

![Python](https://img.shields.io/badge/python-3.11+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Jinja2](https://img.shields.io/badge/jinja-3.0+-C63D14?style=for-the-badge&logo=jinja&logoColor=white)
![Tree-sitter](https://img.shields.io/badge/Tree%20Sitter-Parsing-43B02A?style=for-the-badge&logo=treesitter&logoColor=white)
![AST](https://img.shields.io/badge/Python%20AST-Parsing-306998?style=for-the-badge&logo=python&logoColor=white)
![Httpx](https://img.shields.io/badge/httpx-Async_HTTP-005571?style=for-the-badge)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)
![vLLM](https://img.shields.io/badge/vLLM-Supported-blue?style=for-the-badge)
![LM Studio](https://img.shields.io/badge/LM_Studio-Local-purple?style=for-the-badge)

The core logic engine for generating test suites. It handles parsing OpenAPI/Python/TypeScript specifications, generating Intermediate Representations (IR), discovering test intents, mutating payloads, and rendering test code with optional LLM enhancement.

## Installation

1.  Navigate to the directory:

    ```bash
    cd testsuitegen
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Folder Structure

```text
testsuitegen/
├── requirements.txt            # Project dependencies
├── src/                        # Source code
│   │
│   ├── parsers/                # STAGE 1: Source Code Parsers
│   │   ├── __init__.py
│   │   ├── validator.py        # Schema validation utilities
│   │   ├── openapi_parser/     # OpenAPI/Swagger parsing
│   │   │   ├── __init__.py
│   │   │   └── parser.py
│   │   ├── python_parser/      # Python AST parsing
│   │   │   ├── __init__.py
│   │   │   └── parser.py
│   │   └── typescript_parser/  # Tree-sitter TypeScript parsing
│   │       ├── __init__.py
│   │       └── parser.py
│   │
│   ├── generators/             # STAGES 2-4: Generation Logic
│   │   │
│   │   ├── ir_generator/       # STAGE 2: Intermediate Representation
│   │   │   ├── __init__.py
│   │   │   ├── builder.py      # IR construction from parsed specs
│   │   │   └── validator.py    # IR schema validation
│   │   │
│   │   ├── intent_generator/   # STAGE 3: Intent Discovery
│   │   │   ├── __init__.py
│   │   │   ├── generator.py    # Main intent strategy dispatcher
│   │   │   ├── openapi_intent/ # OpenAPI-specific intents
│   │   │   │   ├── enums.py    # Intent type definitions
│   │   │   │   └── generator.py
│   │   │   ├── python_intent/  # Python-specific intents
│   │   │   │   ├── enums.py
│   │   │   │   └── generator.py
│   │   │   └── typescript_intent/ # TypeScript-specific intents
│   │   │       ├── enums.py
│   │   │       └── generator.py
│   │   │
│   │   └── payloads_generator/ # STAGE 4: Payload Generation & Mutation
│   │       ├── __init__.py
│   │       ├── generator.py    # Base payload generator
│   │       ├── mutator.py      # Base mutation strategies
│   │       ├── openapi_mutator/
│   │       │   └── mutator.py  # OpenAPI-specific mutations
│   │       ├── python_mutator/
│   │       │   └── mutator.py  # Python-specific mutations
│   │       └── typescript_mutator/
│   │           └── mutator.py  # TypeScript-specific mutations
│   │
│   ├── testsuite/              # STAGE 5: Test Code Rendering (NEW PIPELINE)
│   │   ├── __init__.py
│   │   ├── generator.py        # Main test suite orchestrator
│   │   ├── templates.py        # Jinja2 templates (Pytest, Jest)
│   │   ├── analyzer.py         # Static resource dependency analysis
│   │   ├── planner.py          # Setup/teardown planning
│   │   └── compiler.py         # Fixture code compilation
│   │
│   ├── llm_enhancer/           # Optional AI Enhancement Layer
│   │   ├── __init__.py
│   │   ├── client.py           # Unified LLM client wrapper
│   │   ├── circuit_breaker.py  # Error resilience (failure threshold)
│   │   │
│   │   ├── providers/          # LLM Provider Integrations
│   │   │   ├── base.py         # Abstract base class
│   │   │   ├── factory.py      # Provider factory
│   │   │   ├── gemini.py       # Google Gemini
│   │   │   ├── groq.py         # Groq
│   │   │   ├── vllm.py         # vLLM (local/remote)
│   │   │   ├── lmstudio.py     # LM Studio (local)
│   │   │   ├── openrouter.py   # OpenRouter
│   │   │   └── airllm.py       # AirLLM
│   │   │
│   │   ├── payload_enhancer/   # Payload realism enhancement
│   │   │   ├── enhancer.py
│   │   │   ├── prompts.py
│   │   │   └── validator.py
│   │   │
│   │   ├── python_enhancer/    # Python test code polishing
│   │   │   ├── ir_enhancer/
│   │   │   └── test_suite_enhancer/
│   │   │       ├── enhancer.py
│   │   │       ├── prompts.py
│   │   │       └── validator.py # Payload integrity validation
│   │   │
│   │   └── typescript_enhancer/ # TypeScript test code polishing
│   │       ├── ir_enhancer/
│   │       └── test_suite_enhancer/
│   │           ├── enhancer.py
│   │           ├── prompts.py
│   │           └── validator.py # Payload integrity validation
│   │
│   ├── config/                 # Configuration
│   │   ├── __init__.py
│   │   └── settings.py         # Global settings, LLMProviders enum
│   │
│   ├── exceptions/             # Custom Exceptions
│   │   ├── __init__.py
│   │   └── exceptions.py       # LLMError, ParsingError, etc.
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── tree_sitter_loader.py # Tree-sitter grammar loading
│
└── sample_applications/        # Demo Applications for Testing
    ├── api_applications/       # OpenAPI samples
    │   ├── 4_fintech_api/
    │   └── 6_event_booking_api/
    ├── python_applications/    # Python function samples
    └── ts_applications/        # TypeScript function samples
```

## Stage 5: Test Rendering Components

The `testsuite/` module uses a deterministic sub-pipeline for API test generation:

| Component | File | Description |
|-----------|------|-------------|
| **Static Analyzer** | `analyzer.py` | Detects resource dependencies (e.g., GET needs created ID) |
| **Setup Planner** | `planner.py` | Plans resource creation order (POST before GET) |
| **Fixture Compiler** | `compiler.py` | Generates pytest fixtures / Jest beforeAll hooks |
| **Template Renderer** | `generator.py` | Renders Jinja2 templates with compiled fixtures |

## Environment Configuration

Create a `.env` file in the project root (or ensure these variables are available).

| Variable                            | Description                      | Required        | Example                    |
| :---------------------------------- | :------------------------------- | :-------------- | :------------------------- |
| `GEMINI_API_KEY`                    | API Key for Google Gemini        | If using Gemini | `AIza...`                  |
| `OPENAI_API_KEY`                    | API Key for OpenAI               | If using OpenAI | `sk-...`                   |
| `GROQ_API_KEY`                      | API Key for Groq                 | If using Groq   | `gsk_...`                  |
| `LMSTUDIO_BASE_URL`                 | Base URL for LM Studio (Local)   | If using Local  | `http://localhost:1234/v1` |
| `VLLM_BASE_URL`                     | Base URL for VLLM (Local/Remote) | If using VLLM   | `http://localhost:8000/v1` |
| `AIRLLM_MODEL_PATH`                 | Path/Name for AirLLM Model       | If using AirLLM | `Qwen/Qwen2.5-Coder-1.5B`  |
| `CIRCUIT_BREAKER_FAILURE_THRESHOLD` | Failures before blocking LLM     | No (Default: 5) | `5`                        |
| `MAX_LLM_RETRIES`                   | Max retry attempts for LLM       | No (Default: 3) | `3`                        |
| `EXPONENTIAL_BACKOFF_BASE`          | Base delay for retries (seconds) | No (Default: 2) | `2`                        |
| `DEFAULT_OUTPUT_DIR`                | Directory for artifacts          | No              | `artifacts`                |

## Settings Configuration

The file `src/config/settings.py` controls the application behavior. Key values you might want to adjust include:

- **`LLMProviders` (Enum)**: Defines available providers and their default models/parameters (temperature, max_tokens).
- **`DEFAULT_LLM_PROVIDER`**: Logic to select the best available provider (Preference: Local > Cloud).
- **`CIRCUIT_BREAKER_FAILURE_THRESHOLD`**: Controls how sensitive the system is to LLM failures.
- **`EXPONENTIAL_BACKOFF_BASE`**: Base seconds for retry delays (2s, 4s, 8s...).

## Adding a New LLM Provider

To add a new LLM provider (e.g., "Anthropic"):

1.  **Create Provider Class**:
    Add a new file `src/llm_enhancer/providers/anthropic.py`. Use `src/llm_enhancer/providers/base.py` as a base class.

    ```python
    from .base import BaseLLMProvider
    class AnthropicProvider(BaseLLMProvider):
        def generate(self, prompt: str, **kwargs) -> str:
            # Implement API call logic
            pass
    ```

2.  **Register in Factory**:
    Update `src/llm_enhancer/providers/factory.py` to include the new provider in `create_provider`.

3.  **Update Settings**:
    In `src/config/settings.py`:
    - Add `ANTHROPIC` to the `LLMProviders` Enum with default config (model, tokens).
    - Add it to `get_by_name()` method.

4.  **Environment Variable**:
    Add the necessary API key (e.g., `ANTHROPIC_API_KEY`) to your `.env` and `settings.py` loading logic.
