# llm_enhancer/ir_enhancer/enhancer.py

import json
import time

from testsuitegen.src.llm_enhancer.client import llm_generate
from testsuitegen.src.llm_enhancer.python_enhancer.ir_enhancer.prompts import (
    ENHANCE_IR_PROMPT,
)
from testsuitegen.src.llm_enhancer.python_enhancer.ir_enhancer.validator import (
    validate_ir_enhancement_flexible,
)
from testsuitegen.src.config.settings import (
    LLM_ENABLED,
    MAX_LLM_RETRIES,
    EXPONENTIAL_BACKOFF_BASE,
)
from testsuitegen.src.llm_enhancer.circuit_breaker import circuit_breaker
from testsuitegen.src.exceptions.exceptions import LLMError


def _strip_invalid_enum_markers(schema: dict, valid_types: set) -> dict:
    """
    Recursively remove x-enum-type markers that reference non-existent types.

    This fixes LLM hallucination where it invents types like 'Username', 'Password'
    that don't actually exist in the source code.
    """
    if not isinstance(schema, dict):
        return schema

    # Remove invalid x-enum-type at this level
    if "x-enum-type" in schema:
        if schema["x-enum-type"] not in valid_types:
            del schema["x-enum-type"]

    # Recurse into properties
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            _strip_invalid_enum_markers(prop_schema, valid_types)

    # Recurse into items (for arrays)
    if "items" in schema and isinstance(schema["items"], dict):
        _strip_invalid_enum_markers(schema["items"], valid_types)

    # Recurse into oneOf/anyOf
    for variant_key in ("oneOf", "anyOf"):
        if variant_key in schema:
            for variant in schema[variant_key]:
                _strip_invalid_enum_markers(variant, valid_types)

    return schema


def enhance_ir_schema(
    ir_operation: dict,
    source_code: str,
    types: list,
    provider: str = None,
    model: str = None,
    max_retries: int = None,
) -> dict:
    """
    Uses LLM to inject constraints into the IR based on code logic with Resilience Layer.

    Args:
        ir_operation: The single operation dictionary from the IR
        source_code: The full python source code (or specific function text)
        provider: LLM provider to use
        model: Specific model to use (overrides provider default)
        max_retries: Number of retry attempts on transient errors
    """
    if not LLM_ENABLED:
        return ir_operation

    # Check if schema exists
    if (
        "body" not in ir_operation["inputs"]
        or "schema" not in ir_operation["inputs"]["body"]
    ):
        return ir_operation

    operation_id = ir_operation.get("id", "unknown_function")

    # Use config default if not specified
    if max_retries is None:
        max_retries = MAX_LLM_RETRIES

    # 1. Check Circuit Breaker before attempting
    try:
        circuit_breaker.check_state()
    except LLMError as e:
        print(
            f"      ⚠ Circuit Breaker blocking LLM call for {operation_id}. Returning original IR."
        )
        return ir_operation

    schema = ir_operation["inputs"]["body"]["schema"]
    schema_json = json.dumps(schema, indent=2)
    types_json = json.dumps(types, indent=2) if types else "[]"

    # Prepare prompt
    prompt = (
        ENHANCE_IR_PROMPT.replace("{schema}", schema_json)
        .replace("{function_name}", operation_id)
        .replace("{code}", source_code)
        .replace("{types}", types_json)
    )

    # 2. Exponential Backoff Retry Loop
    for attempt in range(1, max_retries + 1):
        try:
            print(f"      LLM Attempt {attempt}/{max_retries} for {operation_id}...")

            kwargs = {"chat_template_kwargs": {"enable_thinking": False}}
            kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}

            # Progressive Backoff Temperature: Increase temp by 0.1 for each retry to break loops
            # Attempt 1: Default (0.01)
            # Attempt 2: 0.11
            # Attempt 3: 0.21 ...
            base_temp = 0.01
            if attempt > 1:
                kwargs["temperature"] = base_temp + 0.1 * (attempt - 1)

            kwargs["generate_cfg"] = (
                {
                    # Add: When the response content is `<think>this is the thought</think>this is the answer;
                    # Do not add: When the response has been separated by reasoning_content and content.
                    "thought_in_content": False,
                },
            )

            enhanced_text = llm_generate(
                prompt, provider=provider, model_override=model, **kwargs
            )

            # 3. STRICT JSON VALIDATION - Clean and validate
            enhanced_text = enhanced_text.strip()

            # Remove markdown code blocks
            if enhanced_text.startswith("```json"):
                enhanced_text = enhanced_text[7:]
            elif enhanced_text.startswith("```"):
                enhanced_text = enhanced_text[3:]

            if enhanced_text.endswith("```"):
                enhanced_text = enhanced_text[:-3]

            enhanced_text = enhanced_text.strip()

            # Check for valid JSON start
            if not enhanced_text.startswith("{"):
                # Try to find JSON object
                start = enhanced_text.find("{")
                end = enhanced_text.rfind("}")
                if start != -1 and end != -1:
                    enhanced_text = enhanced_text[start : end + 1]
                else:
                    print(
                        f"      ⚠ LLM returned non-JSON response. Retrying... Attempt {attempt}"
                    )
                    raise ValueError("Response did not contain valid JSON object")

            # Parse JSON
            try:
                enhanced_schema = json.loads(enhanced_text)
            except json.JSONDecodeError as e:
                try:
                    import re

                    repaired_text = re.sub(
                        r'\\(?![/u"\\bfnrt])', r"\\\\", enhanced_text
                    )
                    enhanced_schema = json.loads(repaired_text)
                    print(
                        f"      ✨ JSON repaired successfully (fixed invalid escapes)"
                    )
                except Exception as repair_error:
                    print(
                        f"      ⚠ LLM returned invalid JSON: {e}. Repair failed: {repair_error}. Retrying... Attempt {attempt}"
                    )
                    raise ValueError(f"Invalid JSON returned: {e}")

            # Validate structure using FLEXIBLE validator
            if not validate_ir_enhancement_flexible(schema, enhanced_schema):
                print(
                    f"      ⚠ Structure validation failed. Retrying... Attempt {attempt}"
                )
                raise ValueError("LLM changed schema structure")

            # 4.5 Strip invalid x-enum-type markers (LLM hallucination fix)
            # Build set of valid type names from the types list passed in
            valid_type_names = {t.get("id") for t in types if t.get("id")}
            _strip_invalid_enum_markers(enhanced_schema, valid_type_names)

            # 4. SUCCESS: Apply enhancements
            # Extract metadata if provided by LLM
            if "metadata" in enhanced_schema:
                ir_operation["metadata"] = enhanced_schema.pop("metadata")

            # Update Schema
            ir_operation["inputs"]["body"]["schema"] = enhanced_schema

            circuit_breaker.record_success()
            print(f"      ✨ Schema enhanced successfully with type resolution")
            return ir_operation

        except ValueError as ve:
            # Validation errors
            print(f"      ⚠ Validation Error: {ve}")
            if attempt == max_retries:
                print(
                    f"      ❌ Max retries ({max_retries}) reached for validation errors."
                )
                circuit_breaker.record_failure()
                return ir_operation
            time.sleep(EXPONENTIAL_BACKOFF_BASE**attempt)  # Exponential backoff

        except Exception as e:
            # Transient errors
            print(f"      ⚠ LLM API Error (Attempt {attempt}): {e}")
            if attempt == max_retries:
                print(f"      ❌ Max retries ({max_retries}) reached for API errors.")
                circuit_breaker.record_failure()
                return ir_operation
            time.sleep(EXPONENTIAL_BACKOFF_BASE**attempt)  # Exponential backoff

    return ir_operation
