import sys
import time

sys.path.append("..")
from testsuitegen.src.llm_enhancer.client import llm_generate
from testsuitegen.src.llm_enhancer.typescript_enhancer.test_suite_enhancer.prompts import (
    ENHANCE_CODE_UNIT_PROMPT,
    ENHANCE_CODE_API_PROMPT,
)
from testsuitegen.src.llm_enhancer.typescript_enhancer.test_suite_enhancer.validator import (
    validate_no_logic_change,
)
from testsuitegen.src.llm_enhancer.circuit_breaker import circuit_breaker
from testsuitegen.src.config.settings import (
    LLM_ENABLED,
    MAX_LLM_RETRIES,
    EXPONENTIAL_BACKOFF_BASE,
)
from testsuitegen.src.exceptions.exceptions import LLMError, LLMFatalError


def _clean_llm_response(response: str) -> str:
    """Clean LLM response from markdown formatting and common issues."""
    import re

    # Remove markdown code blocks (can appear anywhere)
    # Handle ```typescript ... ``` blocks
    response = re.sub(r"```(?:typescript|ts|javascript|js)?\s*", "", response)
    response = response.replace("```", "")

    # Strip whitespace
    response = response.strip()

    # Handle common LLM formatting issues - remove explanation text
    lines = response.split("\n")
    cleaned_lines = []
    in_code = False

    for line in lines:
        stripped = line.strip()

        # Skip markdown-style headers and explanations
        if stripped.startswith("**") or stripped.startswith("#"):
            continue
        # Skip lines that look like bullet points or explanations
        if stripped.startswith("- The ") or stripped.startswith("* The "):
            continue
        # Skip empty lines at start
        if not stripped and not cleaned_lines:
            continue
        # Detect code start - MUST start with valid TS file beginning
        if (
            stripped.startswith("//")
            or stripped.startswith("import ")
            or stripped.startswith("describe(")
            or stripped.startswith("export ")
        ):
            in_code = True
        # If we're in code or line looks like code, keep it
        if (
            in_code
            or stripped.startswith("const ")
            or stripped.startswith("let ")
            or stripped.startswith("}")
            or stripped.startswith("{")
        ):
            cleaned_lines.append(line)
            in_code = True
        elif not in_code:
            # Skip non-code lines before code starts
            continue
        else:
            cleaned_lines.append(line)

    result = "\n".join(cleaned_lines)

    # Final safety: if result doesn't look like TS code, return original
    if not ("describe(" in result or "export" in result):
        return response

    # CRITICAL: Validate the result starts with a valid TypeScript file beginning
    # This prevents corrupted partial code from being accepted
    result_stripped = result.strip()
    valid_starts = (
        "import ",  # Import statement
        "//",  # Comment
        "/*",  # Multi-line comment
        "export ",  # Export statement
        "describe(",  # Jest describe block
        "const ",  # Constant declaration at file level
    )
    if not result_stripped.startswith(valid_starts):
        # LLM returned partial/corrupted code - reject it
        return None  # Signal to caller that enhancement failed

    return result


def enhance_code(
    code: str,
    provider: str = None,
    model: str = None,
    max_retries: int = None,
    test_type: str = "api",
) -> str:
    """Enhance TypeScript test code."""
    if not LLM_ENABLED:
        return code

    # Use config default if not specified
    if max_retries is None:
        max_retries = MAX_LLM_RETRIES

    # 1. Check Circuit Breaker before attempting
    try:
        circuit_breaker.check_state()
    except LLMError as e:
        return code

    # Prepare prompt based on test type
    if test_type == "unit":
        prompt_template = ENHANCE_CODE_UNIT_PROMPT
    else:
        prompt_template = ENHANCE_CODE_API_PROMPT

    prompt = prompt_template.replace("{code}", code)

    # 2. Exponential Backoff Retry Loop
    for attempt in range(1, max_retries + 1):
        try:

            # Progressive Backoff Temperature: Increase temp by 0.1 for each retry to break loops
            base_temp = 0.01
            kwargs = {}
            if attempt > 1:
                kwargs["temperature"] = base_temp + 0.1 * (attempt - 1)

            # Call LLM
            raw_enhanced = llm_generate(
                prompt, provider=provider, model_override=model, **kwargs
            )

            # 3. STRICT VALIDATION - Clean and validate
            enhanced = _clean_llm_response(raw_enhanced)

            # Check if cleaning failed (returned None means corrupted code)
            if enhanced is None:
                continue
                # raise ValueError("LLM returned partial or corrupted code")

            # Check if response looks like code (length check)
            if not enhanced or len(enhanced.strip()) < 10:
                raise ValueError("Empty or invalid response from LLM")

            # Check for common hallucination patterns
            if enhanced.strip().startswith(
                ("Here", "Sure", "I'll", "Let me", "The code")
            ):
                raise ValueError("LLM returned explanation text instead of code")

            # CRITICAL: Check for forbidden patterns that corrupt the code
            forbidden_patterns = [
                "import axios",
                "from 'axios'",
                "require('axios')",
                "import fetch from",
                "require('node-fetch')",
                "Axios.RequestConfig",
                "```typescript",
                "```ts",
                "```javascript",
                "**Explanation**",
                "Here is",
                "Here's the",
            ]
            for pattern in forbidden_patterns:
                if pattern in enhanced:
                    raise ValueError(f"LLM added forbidden pattern: {pattern}")

            # Validate no logic changes
            try:
                validate_no_logic_change(original=code, enhanced=enhanced)
            except RuntimeError as validation_error:
                raise ValueError(f"Logic change detected: {validation_error}")

            # 4. SUCCESS: Record Success and Return
            circuit_breaker.record_success()
            return enhanced

        except ValueError as ve:
            # Validation errors
            if attempt == max_retries:
                circuit_breaker.record_failure()
                return code
            time.sleep(2**attempt)

        except LLMFatalError as lf:
            circuit_breaker.record_failure()
            return code

        except Exception as e:
            # Transient errors
            if attempt == max_retries:
                circuit_breaker.record_failure()
                return code
            time.sleep(EXPONENTIAL_BACKOFF_BASE**attempt)

    return code
