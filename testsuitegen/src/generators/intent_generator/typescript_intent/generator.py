"""
TypeScript Intent Generator

Generates test intents for TypeScript function signatures.
Specialized for TypeScript-specific type system including generics, interfaces, and union types.
"""

from typing import List, Dict, Any, Optional


# TypeScript-specific intent definitions
TYPESCRIPT_INTENT_DEFINITIONS = {
    # Functional
    "HAPPY_PATH": {
        "category": "functional",
        "description": "Valid call with all correct arguments",
        "expected_status": 200,
    },
    # Structural
    "REQUIRED_ARG_MISSING": {
        "category": "structure",
        "description": "Required parameter is missing",
        "expected_status": 400,
    },
    "UNEXPECTED_ARGUMENT": {
        "category": "structure",
        "description": "Extra unexpected parameter passed",
        "expected_status": 400,
    },
    "OBJECT_MISSING_FIELD": {
        "category": "structure",
        "description": "Required property missing from object",
        "expected_status": 400,
    },
    "OBJECT_EXTRA_FIELD": {
        "category": "structure",
        "description": "Unexpected property in strict object",
        "expected_status": 400,
    },
    # Type Violations
    "TYPE_VIOLATION": {
        "category": "type",
        "description": "Wrong type for parameter",
        "expected_status": 400,
    },
    "NULL_NOT_ALLOWED": {
        "category": "type",
        "description": "Null passed to non-nullable parameter",
        "expected_status": 400,
    },
    "ARRAY_ITEM_TYPE_VIOLATION": {
        "category": "type",
        "description": "Array contains items of wrong type",
        "expected_status": 400,
    },
    "UNION_NO_MATCH": {
        "category": "type",
        "description": "Value matches no variant of union type",
        "expected_status": 400,
    },
    "GENERIC_TYPE_VIOLATION": {
        "category": "type",
        "description": "Value violates generic type constraint",
        "expected_status": 400,
    },
    "INTERFACE_MISSING_PROPERTY": {
        "category": "type",
        "description": "Object missing required interface property",
        "expected_status": 400,
    },
    # Constraints
    "BOUNDARY_MIN_MINUS_ONE": {
        "category": "constraint",
        "description": "Numeric value below minimum",
        "expected_status": 400,
    },
    "BOUNDARY_MAX_PLUS_ONE": {
        "category": "constraint",
        "description": "Numeric value above maximum",
        "expected_status": 400,
    },
    "STRING_TOO_SHORT": {
        "category": "constraint",
        "description": "String below minimum length",
        "expected_status": 400,
    },
    "STRING_TOO_LONG": {
        "category": "constraint",
        "description": "String exceeds maximum length",
        "expected_status": 400,
    },
    "PATTERN_MISMATCH": {
        "category": "constraint",
        "description": "String doesn't match required pattern",
        "expected_status": 400,
    },
    "ENUM_MISMATCH": {
        "category": "constraint",
        "description": "Value not in allowed enum options",
        "expected_status": 400,
    },
    # Robustness
    "EMPTY_STRING": {
        "category": "robustness",
        "description": "Empty string input",
        "expected_status": 400,
    },
    "WHITESPACE_ONLY": {
        "category": "robustness",
        "description": "String with only whitespace",
        "expected_status": 400,
    },
    "ZERO_VALUE": {
        "category": "robustness",
        "description": "Zero numeric value",
        "expected_status": 400,
    },
    "NEGATIVE_VALUE": {
        "category": "robustness",
        "description": "Negative numeric value",
        "expected_status": 400,
    },
    "EMPTY_COLLECTION": {
        "category": "robustness",
        "description": "Empty array or object",
        "expected_status": 400,
    },
    # Security
    "SQL_INJECTION": {
        "category": "security",
        "description": "SQL injection attempt",
        "expected_status": 400,
    },
    "XSS_INJECTION": {
        "category": "security",
        "description": "Cross-site scripting attempt",
        "expected_status": 400,
    },
    "PATH_TRAVERSAL": {
        "category": "security",
        "description": "Path traversal attempt",
        "expected_status": 400,
    },
    "COMMAND_INJECTION": {
        "category": "security",
        "description": "Command injection attempt",
        "expected_status": 400,
    },
}


class TypeScriptIntentGenerator:
    """
    Generates test intents for TypeScript function operations.
    """

    def __init__(self, operation: dict):
        self.operation = operation
        self.op_id = operation.get("id", "unknown_op")
        self.inputs = operation.get("inputs", {})
        self.body_schema = self.inputs.get("body", {}).get("schema", {})
        self.properties = self.body_schema.get("properties", {})
        self.required = self.body_schema.get("required", [])

    def generate(self) -> List[dict]:
        """Generate all applicable intents for this TypeScript operation."""
        intents = []

        # Always generate HAPPY_PATH
        intents.append(self._create_intent("HAPPY_PATH", "inputs.body", None))

        # Generate intents for each parameter
        for param_name, param_schema in self.properties.items():
            target = f"inputs.body.{param_name}"
            param_intents = self._generate_param_intents(
                param_name, param_schema, target
            )
            intents.extend(param_intents)

        return intents

    def _create_intent(
        self, intent_type: str, target: str, field: Optional[str], **kwargs
    ) -> dict:
        """Create a standardized intent dict."""
        intent_def = TYPESCRIPT_INTENT_DEFINITIONS.get(intent_type, {})

        intent = {
            "intent": intent_type,
            "operation_id": self.op_id,
            "target": target,
            "field": field,
            "category": intent_def.get("category", "unknown"),
            "description": intent_def.get("description", ""),
            "expected": str(intent_def.get("expected_status", 400)),
        }
        intent.update(kwargs)
        return intent

    def _generate_param_intents(
        self, param_name: str, schema: dict, target: str
    ) -> List[dict]:
        """Generate intents applicable to a specific parameter."""
        intents = []
        param_type = schema.get("type", "")
        is_required = param_name in self.required
        is_nullable = schema.get("nullable", False)

        # Structural intents
        if is_required:
            intents.append(
                self._create_intent("REQUIRED_ARG_MISSING", target, param_name)
            )

        # Type violations
        if param_type:
            intents.append(self._create_intent("TYPE_VIOLATION", target, param_name))

        if not is_nullable:
            intents.append(self._create_intent("NULL_NOT_ALLOWED", target, param_name))

        # Array-specific
        if param_type == "array":
            intents.append(
                self._create_intent("ARRAY_ITEM_TYPE_VIOLATION", target, param_name)
            )
            intents.append(self._create_intent("EMPTY_COLLECTION", target, param_name))

        # Object-specific
        if param_type == "object":
            intents.append(
                self._create_intent("OBJECT_MISSING_FIELD", target, param_name)
            )
            intents.append(
                self._create_intent("OBJECT_EXTRA_FIELD", target, param_name)
            )
            intents.append(
                self._create_intent("INTERFACE_MISSING_PROPERTY", target, param_name)
            )

        # Union types
        if "oneOf" in schema or "anyOf" in schema:
            intents.append(self._create_intent("UNION_NO_MATCH", target, param_name))

        # Numeric constraints
        if param_type in ("number", "integer"):
            if "minimum" in schema:
                intents.append(
                    self._create_intent("BOUNDARY_MIN_MINUS_ONE", target, param_name)
                )
            if "maximum" in schema:
                intents.append(
                    self._create_intent("BOUNDARY_MAX_PLUS_ONE", target, param_name)
                )
            intents.append(self._create_intent("ZERO_VALUE", target, param_name))
            intents.append(self._create_intent("NEGATIVE_VALUE", target, param_name))

        # String constraints
        if param_type == "string":
            if "minLength" in schema:
                intents.append(
                    self._create_intent("STRING_TOO_SHORT", target, param_name)
                )
            if "maxLength" in schema:
                intents.append(
                    self._create_intent("STRING_TOO_LONG", target, param_name)
                )
            if "pattern" in schema:
                intents.append(
                    self._create_intent("PATTERN_MISMATCH", target, param_name)
                )
            if "enum" in schema:
                intents.append(self._create_intent("ENUM_MISMATCH", target, param_name))

            # Robustness
            intents.append(self._create_intent("EMPTY_STRING", target, param_name))
            intents.append(self._create_intent("WHITESPACE_ONLY", target, param_name))

            # Security
            intents.append(self._create_intent("SQL_INJECTION", target, param_name))
            intents.append(self._create_intent("XSS_INJECTION", target, param_name))
            intents.append(self._create_intent("PATH_TRAVERSAL", target, param_name))
            intents.append(self._create_intent("COMMAND_INJECTION", target, param_name))

        return intents


def get_typescript_intent_definitions() -> dict:
    """Return all TypeScript intent definitions."""
    return TYPESCRIPT_INTENT_DEFINITIONS.copy()
