import logging

from backend.src.exceptions import IntentGenerationError
from testsuitegen.src.generators.intent_generator.generator import generate_intents

logger = logging.getLogger(__name__)


def _get_intents(ir):
    """Generate intents from all operations in the IR."""
    intents = []
    for op in ir.get("operations", []):
        intents.extend(generate_intents(op))
    return intents


def _prepare_intents(ir, all_intents, job_requests):
    """Filter and augment intents based on job configuration."""
    target_intents = job_requests.get("target_intents", [])
    if target_intents:
        filtered_intents = [
            intent for intent in all_intents if intent["intent"] in target_intents
        ]
        has_happy = any(intent["intent"] == "HAPPY_PATH" for intent in filtered_intents)
        if not has_happy:
            happy = next((i for i in all_intents if i["intent"] == "HAPPY_PATH"), None)
            if happy:
                filtered_intents.append(happy)
        working = filtered_intents
    else:
        working = list(all_intents)

    custom_payloads = job_requests.get("custom_payloads", [])
    if custom_payloads:
        for idx, custom in enumerate(custom_payloads):
            op_id = ir["operations"][0]["id"] if ir.get("operations") else "op_0"
            working.append(
                {
                    "intent": f"CUSTOM_CASE_{idx}",
                    "operation_id": op_id,
                    "target": "inputs.body",
                    "payload": custom.get("payload", {}),
                    "expected": custom.get("expected", 200),
                }
            )

    return working


def _generate_intents(ir, job_requests):
    """Generate and prepare test intents from the IR."""
    try:
        all_intents = _get_intents(ir)
        working_intents = _prepare_intents(ir, all_intents, job_requests)
        return working_intents
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to generate intents")
        raise IntentGenerationError(str(exc)) from exc
