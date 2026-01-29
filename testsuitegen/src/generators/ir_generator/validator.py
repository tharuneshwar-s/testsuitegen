# validator.py
# This file will contain functions to validate IR against the schema.

import json
from jsonschema import validate, ValidationError as JsonSchemaValidationError
from pathlib import Path
from testsuitegen.src.exceptions.exceptions import ValidationError


SCHEMA_PATH = Path(__file__).parent / "schema.json"


def validate_ir(ir: dict) -> bool:
    """
    Validate IR data using the schema defined in schema.json.

    Raises:
        ValidationError: If the IR structure is invalid.
    """
    schema = json.loads(SCHEMA_PATH.read_text())
    try:
        validate(instance=ir, schema=schema)
    except JsonSchemaValidationError as e:

        error_path = " -> ".join([str(p) for p in e.path]) if e.path else "Root"
        raise ValidationError(
            f"IR Structure Invalid at [{error_path}]",
            (
                f"{e.message}\n   Expected: {e.schema.get('type', 'object')}"
                if hasattr(e, "schema")
                else e.message
            ),
        )
        
    return True
