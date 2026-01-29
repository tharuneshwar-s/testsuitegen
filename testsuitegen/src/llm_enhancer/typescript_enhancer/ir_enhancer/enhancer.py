# llm_enhancer/typescript_enhancer/ir_enhancer/enhancer.py

import json
import time
import logging

from testsuitegen.src.llm_enhancer.client import llm_generate
from testsuitegen.src.llm_enhancer.typescript_enhancer.ir_enhancer.prompts import (
    ENHANCE_IR_PROMPT_TS,
)
from testsuitegen.src.llm_enhancer.typescript_enhancer.ir_enhancer.validator import (
    validate_ir_enhancement_flexible,
)
from testsuitegen.src.config.settings import (
    LLM_ENABLED,
    MAX_LLM_RETRIES,
    EXPONENTIAL_BACKOFF_BASE,
)
from testsuitegen.src.llm_enhancer.circuit_breaker import circuit_breaker
from testsuitegen.src.exceptions.exceptions import LLMError

logger = logging.getLogger(__name__)


def enhance_ir_schema_ts(
    ir_operation: dict,
    source_code: str,
    types: list,
    provider: str = None,
    model: str = None,
    max_retries: int = None,
    **kwargs,
) -> dict:
    """
    Uses LLM to inject constraints into the IR based on TS code logic with Resilience Layer.
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
        logger.warning(
            f"      Circuit Breaker blocking LLM call for {operation_id}. Returning original IR."
        )
        return ir_operation

    schema = ir_operation["inputs"]["body"]["schema"]
    schema_json = json.dumps(schema, indent=2)
    types_json = json.dumps(types, indent=2) if types else "[]"

    # Prepare prompt with TS Template
    prompt = (
        ENHANCE_IR_PROMPT_TS.replace("{schema}", schema_json)
        .replace("{function_name}", operation_id)
        .replace("{code}", source_code)
        .replace("{types}", types_json)
    )

    # 2. Exponential Backoff Retry Loop
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"      LLM Attempt {attempt}/{max_retries} for {operation_id} (TS)..."
            )

            # kwargs = {"chat_template_kwargs": {"enable_thinking": False}}
            # kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}
            # kwargs["generate_cfg"] = ({"thought_in_content": False},)

            if attempt > 1:
                kwargs["temperature"] = 0.1 * attempt

            enhanced_text = llm_generate(
                prompt, provider=provider, model_override=model, **kwargs
            )

            # 3. STRICT JSON VALIDATION - Clean and validate
            enhanced_text = enhanced_text.strip()
            if enhanced_text.startswith("```json"):
                enhanced_text = enhanced_text[7:]
            elif enhanced_text.startswith("```"):
                enhanced_text = enhanced_text[3:]
            if enhanced_text.endswith("```"):
                enhanced_text = enhanced_text[:-3]
            enhanced_text = enhanced_text.strip()

            if not enhanced_text.startswith("{"):
                start = enhanced_text.find("{")
                end = enhanced_text.rfind("}")
                if start != -1 and end != -1:
                    enhanced_text = enhanced_text[start : end + 1]
                else:
                    logger.warning(
                        f"      LLM returned non-JSON response. Retrying... Attempt {attempt}"
                    )
                    raise ValueError("Response did not contain valid JSON object")

            try:
                enhanced_schema = json.loads(enhanced_text)
            except json.JSONDecodeError as e:
                # Attempt simple repair
                try:
                    import re

                    repaired_text = re.sub(
                        r'\\(?![/u"\\bfnrt])', r"\\\\", enhanced_text
                    )
                    enhanced_schema = json.loads(repaired_text)
                except Exception:
                    logger.warning(f"      Invalid JSON. Retrying... Attempt {attempt}")
                    if attempt <= max_retries:
                        kwargs["temperature"] = 0.1 * attempt
                        prompt += f"\n\nInvalid JSON returned: {e}"
                        continue
                    raise ValueError(f"Invalid JSON returned: {e}")

            # Validate structure (Reuse python validator as structure rules are same)
            if not validate_ir_enhancement_flexible(schema, enhanced_schema):
                logger.warning(
                    f"      Structure validation failed. Retrying... Attempt {attempt}"
                )
                raise ValueError("LLM changed schema structure")

            # 4. SUCCESS: Apply enhancements
            if "metadata" in enhanced_schema:
                ir_operation["metadata"] = enhanced_schema.pop("metadata")

            ir_operation["inputs"]["body"]["schema"] = enhanced_schema

            circuit_breaker.record_success()
            logger.info(f"      Schema enhanced successfully (TS)")
            return ir_operation

        except ValueError as ve:
            logger.warning(f"      Validation Error: {ve}")
            if attempt == max_retries:
                circuit_breaker.record_failure()
                return ir_operation
            time.sleep(EXPONENTIAL_BACKOFF_BASE**attempt)

        except Exception as e:
            logger.error(f"      LLM API Error (Attempt {attempt}): {e}")
            if attempt == max_retries:
                circuit_breaker.record_failure()
                return ir_operation
            time.sleep(EXPONENTIAL_BACKOFF_BASE**attempt)

    return ir_operation
