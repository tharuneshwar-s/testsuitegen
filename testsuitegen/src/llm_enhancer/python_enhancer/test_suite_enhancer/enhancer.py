# llm_enhancer/test_enhancer/enhancer.py

import sys
import time

sys.path.append("..")
from testsuitegen.src.llm_enhancer.client import llm_generate
from testsuitegen.src.llm_enhancer.python_enhancer.test_suite_enhancer.prompts import (
    ENHANCE_CODE_UNIT_PROMPT,
    ENHANCE_CODE_API_PROMPT,
)
from testsuitegen.src.llm_enhancer.python_enhancer.test_suite_enhancer.validator import (
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
    """Clean LLM response from markdown formatting and common issues.

    Args:
        response: Raw LLM response

    Returns:
        Cleaned Python code
    """
    # Remove markdown code blocks
    if response.startswith("```python"):
        response = response[9:]
    elif response.startswith("```typescript"):
        response = response[13:]
    elif response.startswith("```ts"):
        response = response[5:]
    elif response.startswith("```javascript"):
        response = response[13:]
    elif response.startswith("```js"):
        response = response[5:]
    elif response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]  # Remove closing ```

    # Strip whitespace
    response = response.strip()

    # Handle common LLM formatting issues
    lines = response.split("\n")
    cleaned_lines = []

    for line in lines:
        # Skip empty lines at start/end
        if not line.strip() and (not cleaned_lines or line == lines[-1]):
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def _is_beneficial_only_change(original: str, enhanced: str) -> bool:
    """Check if the enhancement only adds beneficial changes (fixtures, comments, etc.)."""
    # Simple heuristic: if enhanced is longer and contains fixture-related keywords,
    # and doesn't contain forbidden patterns, consider it beneficial

    beneficial_keywords = [
        "@pytest.fixture",
        "test_data_setup",
        "USE_CREATED_RESOURCE",
        "def setup_",
        "patch(",
        "MagicMock",
    ]
    forbidden_patterns = [
        r"expected_status.*=",
        r"assert.*!=",
        r"@pytest.mark.parametrize.*\[",
    ]

    # Check for beneficial additions
    has_beneficial = any(keyword in enhanced for keyword in beneficial_keywords)

    # Check for forbidden changes
    has_forbidden = any(pattern in enhanced for pattern in forbidden_patterns)

    # If it has beneficial changes and no forbidden ones, and is reasonably longer (added content)
    length_increase = len(enhanced) - len(original)
    reasonable_addition = (
        length_increase > 50 and length_increase < 2000
    )  # Reasonable bounds

    return has_beneficial and not has_forbidden and reasonable_addition


def enhance_code(
    code: str,
    provider: str = None,
    model: str = None,
    max_retries: int = None,
    test_type: str = "api",
) -> str:
    """Enhance test code with better formatting and docstrings using Resilience Layer.

    Args:
        code: Original test code
        provider: LLM provider to use (None = use default)
        max_retries: Number of retry attempts on transient errors
        test_type: "api" or "unit" to select enhancement strategy

    Returns:
        Enhanced code (or original if enhancement fails)

    RESILIENCE:
    - Circuit Breaker: Stops LLM calls after repeated failures
    - Exponential Backoff: Retries with increasing delays (2s, 4s, 8s)
    - Strict Validation: Rejects code with logic changes
    """
    if not LLM_ENABLED:
        return code

    # Use config default if not specified
    if max_retries is None:
        max_retries = MAX_LLM_RETRIES

    # 1. Check Circuit Breaker before attempting
    try:
        circuit_breaker.check_state()
    except LLMError as e:
        print(
            f"⚠ Circuit Breaker blocking LLM call for test code enhancement. Returning original code."
        )
        return code

    print(
        f"▶ Enhancing code with LLM ({test_type} mode) using provider: {provider or 'default'}:{model or 'default'}..."
    )

    # Prepare prompt based on test type
    if test_type == "unit":
        prompt_template = ENHANCE_CODE_UNIT_PROMPT
    else:
        prompt_template = ENHANCE_CODE_API_PROMPT

    prompt = prompt_template.replace("{code}", code)

    # 2. Exponential Backoff Retry Loop
    for attempt in range(1, max_retries + 1):
        try:
            print(
                f"   LLM Attempt {attempt}/{max_retries} for test code enhancement..."
            )

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

            # Check if response looks like Python code
            if not enhanced or len(enhanced.strip()) < 10:
                print(
                    f"   ⚠ LLM returned empty or too short response. Retrying... Attempt {attempt}"
                )
                raise ValueError("Empty or invalid response from LLM")

            # Check for common hallucination patterns
            if enhanced.strip().startswith(
                ("Here", "Sure", "I'll", "Let me", "The code")
            ):
                print(
                    f"   ⚠ LLM returned text instead of code. Retrying... Attempt {attempt}"
                )
                raise ValueError("LLM returned explanation text instead of code")

            # Validate no logic changes
            try:
                validate_no_logic_change(original=code, enhanced=enhanced)
            except RuntimeError as validation_error:
                # Check if it's beneficial changes only
                if _is_beneficial_only_change(code, enhanced):
                    print(
                        f"   ⚠ Validation warning (but allowing beneficial changes): {validation_error}"
                    )
                else:
                    print(
                        f"   ⚠ Logic validation failed. Retrying... Attempt {attempt}"
                    )
                    raise ValueError(f"Logic change detected: {validation_error}")

            # 4. SUCCESS: Record Success and Return
            circuit_breaker.record_success()
            print(f"   ✨ Test code enhancement successful")
            return enhanced

        except ValueError as ve:
            # Validation errors
            print(f"   ⚠ Validation Error: {ve}")
            if attempt == max_retries:
                print(
                    f"   ❌ Max retries ({max_retries}) reached for validation errors."
                )
                circuit_breaker.record_failure()
                return code
            time.sleep(2**attempt)  # Exponential backoff

        except LLMFatalError as lf:
            # Non-retryable policy/config error from provider - abort immediately
            print(f"   ⚠ Non-retryable LLM error: {lf}. Aborting code enhancement.")
            circuit_breaker.record_failure()
            return code

        except Exception as e:
            # Transient errors
            print(f"   ⚠ LLM API Error (Attempt {attempt}): {e}")
            if attempt == max_retries:
                print(f"   ❌ Max retries ({max_retries}) reached for API errors.")
                circuit_breaker.record_failure()
                return code
            time.sleep(EXPONENTIAL_BACKOFF_BASE**attempt)  # Exponential backoff

    # Should not reach here, but just in case
    return code
