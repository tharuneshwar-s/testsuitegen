from testsuitegen.src.generators.intent_generator.python_intent.generator import (
    PythonIntentGenerator,
)
from testsuitegen.src.generators.intent_generator.openapi_intent.generator import (
    IntentGenerator as OpenAPIIntentGenerator,
)
from testsuitegen.src.generators.intent_generator.typescript_intent.generator import (
    TypeScriptIntentGenerator,
)


def generate_intents(ir_operation: dict) -> list[dict]:
    """
    Main dispatcher for intent generation.
    Routes to appropriate generator based on operation kind.

    Args:
        ir_operation: The IR operation dict with 'kind' field

    Returns:
        List of intent dictionaries
    """
    kind = ir_operation.get("kind", "http")

    # Dispatch based on kind
    if kind == "function":
        generator = PythonIntentGenerator(ir_operation)
        return generator.generate()

    elif kind == "typescript_function":
        generator = TypeScriptIntentGenerator(ir_operation)
        return generator.generate()

    else:
        generator = OpenAPIIntentGenerator(ir_operation)
        return generator.generate()
