import json
import logging

from backend.src.exceptions import PayloadGenerationError
from testsuitegen.src.config.settings import DEFAULT_LLM_MODEL, DEFAULT_LLM_PROVIDER
from testsuitegen.src.generators.payloads_generator.generator import PayloadGenerator
from testsuitegen.src.llm_enhancer.payload_enhancer.enhancer import enhance_payload

logger = logging.getLogger(__name__)


def __generate_golden_payload(op, happy_intent):
    """Generate a base payload for the happy path intent."""
    raw_result = PayloadGenerator(op).generate([happy_intent])[0]
    return raw_result.get("payload", {})


def __enhance_payload(
    raw_payload, schema_str, llm_provider, llm_model, op_id, intent="HAPPY_PATH"
):
    """Enhance payload using LLM for realistic test data."""
    logger.info("Enhancing payload for %s with %s:%s", op_id, llm_provider, llm_model)
    return enhance_payload(
        payload=raw_payload,
        operation_id=op_id,
        schema_info=schema_str,
        provider=llm_provider,
        model=llm_model,
        intent=intent,
    )


def _generate_payloads(ir, working_intents_all, llm_cfg):
    """Generate and enhance payloads for all operations."""
    try:
        # Use dynamic default provider
        default_provider = DEFAULT_LLM_PROVIDER
        if hasattr(DEFAULT_LLM_PROVIDER, "value"):
            default_provider = DEFAULT_LLM_PROVIDER.value.name

        llm_provider = (llm_cfg.get("provider") or default_provider).lower()
        llm_model = llm_cfg.get("model") or DEFAULT_LLM_MODEL

        final_payloads = []
        enhanced_payloads = []

        for op in ir.get("operations", []):
            op_id = op["id"]
            op_intents = [
                i for i in working_intents_all if i.get("operation_id") == op_id
            ]
            if not op_intents:
                continue

            happy_intent = next(
                (i for i in op_intents if i["intent"] == "HAPPY_PATH"), None
            )

            if not happy_intent:
                fallback_happy = next(
                    (
                        i
                        for i in working_intents_all
                        if i.get("operation_id") == op_id
                        and i["intent"] == "HAPPY_PATH"
                    ),
                    None,
                )
                if fallback_happy:
                    op_intents.append(fallback_happy)
                    happy_intent = fallback_happy

            golden_payload = None
            if happy_intent:
                raw_payload = __generate_golden_payload(op, happy_intent)

                body_schema = op.get("inputs", {}).get("body", {}).get("schema", {})

                if body_schema:
                    schema_str = json.dumps(body_schema, indent=2)
                    try:
                        golden_payload = __enhance_payload(
                            raw_payload,
                            schema_str,
                            llm_provider,
                            llm_model,
                            op_id,
                            intent="HAPPY_PATH",
                        )
                        enhanced_payloads.append(
                            {
                                "operation_id": op_id,
                                "payload": golden_payload,
                            }
                        )
                        logger.info("Payload enhancement for %s completed", op_id)
                    except Exception as exc:  # noqa: B902
                        logger.error(
                            "Payload enhancement failed for %s: %s",
                            op_id,
                            exc,
                            exc_info=True,
                        )
                        golden_payload = raw_payload
                else:
                    golden_payload = raw_payload

                happy_intent["payload"] = golden_payload
            else:
                generator = PayloadGenerator(op)
                golden_payload = generator.base_payload

            generator = PayloadGenerator(op, base_payload_override=golden_payload)
            generated_cases = generator.generate(op_intents)
            final_payloads.extend(generated_cases)

        return final_payloads, enhanced_payloads
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to generate payloads")
        raise PayloadGenerationError(str(exc)) from exc
