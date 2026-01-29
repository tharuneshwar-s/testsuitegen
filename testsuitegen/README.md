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

The core logic engine for generating test suites. It handles parsing OpenAPI/Python specifications, generating Intermediate Representations (IR), enhancing payloads via LLMs, and rendering test code.

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
│   ├── config/
│   │   ├── settings.py         # Global settings & Enums (LLMProviders, API Keys)
│   │   └── __init__.py
│   ├── exceptions/
│   │   ├── exceptions.py       # Custom error classes (LLMError, ParsingError)
│   │   └── __init__.py
│   ├── generators/             # Core Generation Logic
│   │   ├── intent_generator/   # 1. Intent Analysis
│   │   │   ├── openapi_intent/ # OpenAPI specific strategies
│   │   │   │   ├── enums.py
│   │   │   │   └── generator.py
│   │   │   ├── python_intent/  # Python specific strategies
│   │   │   │   ├── enums.py
│   │   │   │   └── generator.py
│   │   │   ├── typescript_intent/ # TypeScript specific strategies
│   │   │   │   ├── enums.py
│   │   │   │   └── generator.py
│   │   │   └── generator.py    # Main Intent Strategy
│   │   ├── ir_generator/       # 2. Intermediate Representation
│   │   │   ├── builder.py      # IR Construction logic
│   │   │   └── validator.py    # Schema validation
│   │   └── payloads_generator/ # 3. Payload Generation
│   │       ├── openapi_mutator/
│   │       │   └── mutator.py
│   │       ├── python_mutator/
│   │       │   └── mutator.py
│   │       ├── typescript_mutator/
│   │       │   └── mutator.py
│   │       ├── generator.py
│   │       └── mutator.py      # Base mutator logic
│   ├── llm_enhancer/           # AI Enhancement Layer
│   │   ├── payload_enhancer/   # Data realism enhancement
│   │   │   ├── enhancer.py
│   │   │   ├── prompts.py
│   │   │   └── validator.py
│   │   ├── providers/          # LLM Integration
│   │   │   ├── airllm.py
│   │   │   ├── base.py
│   │   │   ├── config.py
│   │   │   ├── factory.py
│   │   │   ├── gemini.py
│   │   │   ├── groq.py
│   │   │   ├── lmstudio.py
│   │   │   ├── openrouter.py
│   │   │   └── vllm.py
│   │   ├── python_enhancer/    # Python Code Enhancement
│   │   │   ├── ir_enhancer/
│   │   │   │   ├── enhancer.py
│   │   │   │   └── prompts.py
│   │   │   └── test_suite_enhancer/
│   │   │       └── enhancer.py
│   │   ├── typescript_enhancer/# TypeScript Code Enhancement
│   │   │   ├── ir_enhancer/
│   │   │   │   └── enhancer.py
│   │   │   └── test_suite_enhancer/
│   │   │       └── enhancer.py
│   │   ├── circuit_breaker.py  # Error resilience
│   │   └── client.py           # Unified client wrapper
│   └── testsuite/              # 4. Final Code Rendering
│       ├── generator.py        # Orchestrates template rendering
│       └── templates.py        # Jinja2 templates (Pytest, Jest)
└── __init__.py
```

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
