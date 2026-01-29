import logging

from backend.src.exceptions import IRBuildError
from testsuitegen.src.generators.ir_generator.builder import build_ir
from testsuitegen.src.generators.ir_generator.validator import validate_ir

from testsuitegen.src.llm_enhancer.python_enhancer.ir_enhancer.enhancer import (
    enhance_ir_schema,
)
from testsuitegen.src.llm_enhancer.typescript_enhancer.ir_enhancer.enhancer import (
    enhance_ir_schema_ts,
)
from testsuitegen.src.utils.code_extractor import extract_relevant_context

logger = logging.getLogger(__name__)


def _build_ir(
    parsed_data: dict,
    spec_json: str,
    source_type: str = "openapi",
    provider: str = None,
    model: str = None,
):
    """Build and validate the intermediate representation."""
    try:
        operations = parsed_data.get("operations", [])
        types = parsed_data.get("types", [])
        metadata = {
            k: v for k, v in parsed_data.items() if k not in ["operations", "types"]
        }

        # Enhance IR with LLM if source is Python
        if source_type == "python":
            logger.info("Enhancing IR schema with LLM for Python source...")
            enhanced_operations = []
            for op in operations:
                try:
                    # Pass filtered source code (function + types) for context
                    context_code = extract_relevant_context(
                        spec_json, op.get("id"), language="python"
                    )
                    enhanced_op = enhance_ir_schema(
                        op, context_code, provider=provider, model=model, types=types
                    )
                    enhanced_operations.append(enhanced_op)
                except Exception as e:
                    logger.warning(f"Failed to enhance operation {op.get('id')}: {e}")
                    enhanced_operations.append(op)
            operations = enhanced_operations

        # Enhance IR with LLM if source is TypeScript
        elif source_type == "typescript":
            logger.info("Enhancing IR schema with LLM for TypeScript source...")
            enhanced_operations = []
            for op in operations:
                try:
                    # Pass filtered source code (function + types) for context
                    context_code = extract_relevant_context(
                        spec_json, op.get("id"), language="typescript"
                    )
                    enhanced_op = enhance_ir_schema_ts(
                        op, context_code, provider=provider, model=model, types=types
                    )
                    enhanced_operations.append(enhanced_op)
                except Exception as e:
                    logger.warning(
                        f"Failed to enhance operation {op.get('id')} (TS): {e}"
                    )
                    enhanced_operations.append(op)
            operations = enhanced_operations

        ir = build_ir(
            source_type=source_type,
            source_name="uploaded_spec",
            source_payload=spec_json,
            operations=operations,
            types=types,
            metadata=metadata,
        )
        is_valid = validate_ir(ir)
        if not is_valid:
            raise IRBuildError("IR validation failed")
        return ir
    except Exception as exc:
        logger.exception("Failed to build IR")
        raise IRBuildError(str(exc)) from exc
