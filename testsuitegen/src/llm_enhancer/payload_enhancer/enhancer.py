# llm_enhancer/payload_enhancer/enhancer.py

import json
import time

from testsuitegen.src.llm_enhancer.client import llm_generate
from testsuitegen.src.llm_enhancer.payload_enhancer.prompts import (
    ENHANCE_PAYLOAD_PROMPT,
)
from testsuitegen.src.llm_enhancer.payload_enhancer.validator import (
    validate_payload_structure,
)
from testsuitegen.src.llm_enhancer.circuit_breaker import circuit_breaker
from testsuitegen.src.config.settings import MAX_LLM_RETRIES, EXPONENTIAL_BACKOFF_BASE
from testsuitegen.src.exceptions.exceptions import LLMError, LLMFatalError


def enhance_payload(
    payload: dict,
    operation_id: str = None,
    intent: str = "HAPPY_PATH",
    schema_info: str = None,
    provider: str = None,
    model: str = None,
    max_retries: int = None,
    **kwargs,
) -> dict:
    """Enhance payload with realistic values using LLM with Resilience Layer.

    Args:
        payload: Original payload dictionary
        operation_id: API operation identifier
        intent: Test intent type
        schema_info: Additional schema context
        provider: LLM provider to use (None = use default)
        max_retries: Number of retry attempts on transient errors

    Returns:
        Enhanced payload (or original if enhancement fails)

    RULES:
    - Only enhances HAPPY_PATH intents (and optionally VALID_BOUNDARY, VALID_ENUM)
    - Does NOT add, remove, or rename keys
    - Does NOT change data types
    - Does NOT change array sizes
    - Falls back to original payload if structure changes

    RESILIENCE:
    - Circuit Breaker: Stops LLM calls after repeated failures
    - Exponential Backoff: Retries with increasing delays (2s, 4s, 8s)
    - Strict JSON Validation: Rejects non-JSON responses
    """

    # Only enhance valid/happy path intents
    if intent not in ["HAPPY_PATH", "VALID_BOUNDARY", "VALID_ENUM"]:
        return payload

    # Use config default if not specified
    if max_retries is None:
        max_retries = MAX_LLM_RETRIES

    # 1. Check Circuit Breaker before attempting
    try:
        circuit_breaker.check_state()
    except LLMError as e:
        return payload

    # Build schema context if available
    schema_context = ""
    if schema_info:
        schema_context = f"\nSchema Context:\n{schema_info}"

    prompt = (
        ENHANCE_PAYLOAD_PROMPT.replace("{operation_id}", operation_id or "unknown")
        .replace("{intent}", intent)
        .replace("{schema_info}", schema_context)
        .replace("{payload}", json.dumps(payload, indent=2))
    )

    # 2. Exponential Backoff Retry Loop
    for attempt in range(1, max_retries + 1):
        try:

            # Progressive Backoff Temperature: Increase temp by 0.1 for each retry to break loops
            base_temp = 0.01
            if attempt > 1:
                kwargs["temperature"] = base_temp + 0.1 * (attempt - 1)
            # Call LLM
            enhanced_text = llm_generate(
                prompt, provider=provider, model_override=model, **kwargs
            )

            # 3. STRICT JSON VALIDATION - Check for non-JSON headers (Hallucination)
            enhanced_text = enhanced_text.strip()

            # Remove markdown code blocks if present
            if enhanced_text.startswith("```json"):
                enhanced_text = enhanced_text[7:]  # Remove ```json
            elif enhanced_text.startswith("```"):
                enhanced_text = enhanced_text[3:]  # Remove ```

            if enhanced_text.endswith("```"):
                enhanced_text = enhanced_text[:-3]  # Remove closing ```

            enhanced_text = enhanced_text.strip()

            # Check if response starts with valid JSON
            if not enhanced_text.startswith(("{", "[")):
                raise ValueError("Response did not start with JSON object/array")

            # Parse JSON
            try:
                enhanced = json.loads(enhanced_text)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON returned: {e}")

            # Handle case where enhanced is an array of objects with a 'payload' key
            if (
                isinstance(enhanced, list)
                and len(enhanced) > 0
                and isinstance(payload, dict)
            ):
                first_item = enhanced[0]
                if isinstance(first_item, dict) and "payload" in first_item:
                    enhanced = first_item["payload"]

            # Validate structure
            if not validate_payload_structure(payload, enhanced):
                raise ValueError(f"Structure changed for operation {operation_id}")

            # Check if placeholders were actually replaced
            enhanced_str = json.dumps(enhanced)
            if "__PLACEHOLDER_" in enhanced_str:
                raise ValueError("Placeholders not replaced")

            # 4. SUCCESS: Record Success and Return
            circuit_breaker.record_success()
            return enhanced

        except ValueError as ve:
            # Validation errors (JSON, structure, placeholders)
            if attempt == max_retries:
                circuit_breaker.record_failure()
                return payload
            time.sleep(2**attempt)  # Exponential backoff: 2s, 4s, 8s

        except LLMFatalError as lf:
            # Non-retryable policy/config error from provider - abort immediately
            circuit_breaker.record_failure()
            return payload

        except Exception as e:
            # Transient network/API errors
            if attempt == max_retries:
                circuit_breaker.record_failure()
                return payload
            time.sleep(EXPONENTIAL_BACKOFF_BASE**attempt)  # Exponential backoff

    # Should not reach here, but just in case
    return payload
