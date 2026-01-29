from testsuitegen.src.generators.intent_generator.python_intent.enums import (
    PythonIntentType,
)


class PythonIntentGenerator:
    """
    Generates test intents for Python functions based on their IR schema.
    """

    def __init__(self, ir_operation: dict):
        self.op = ir_operation
        self.op_id = ir_operation["id"]
        # In Python IR, arguments are mapped to inputs.body.schema
        self.body = ir_operation["inputs"].get("body", {})
        self.schema = self.body.get("schema", {})
        self.intents = []

    def generate(self) -> list[dict]:
        if not self.schema:
            return []

        # 1. Happy Path
        self._emit_happy_path()

        # 2. Argument Analysis
        properties = self.schema.get("properties", {})
        self._process_arguments(properties, parent_path="body")

        # 3. Structural Limits
        if self.schema.get("additionalProperties") is False:
            self._emit(PythonIntentType.UNEXPECTED_ARGUMENT, "body", expected="400")

        return self.intents

    def _emit(self, intent, target, field=None, expected="422", notes=None):
        """
        Emits an intent.
        Note on 'expected':
        - 200: Success / Return Value
        - 400: TypeError (Structural/Missing args)
        - 422: ValueError (Constraint violation)
        """
        self.intents.append(
            {
                "operation_id": self.op_id,
                "intent": intent,
                "target": target,
                "expected": expected,
                **({"field": field} if field else {}),
                **({"notes": notes} if notes else {}),
            }
        )

    def _emit_happy_path(self):
        self._emit(
            PythonIntentType.HAPPY_PATH, "body", expected="200", notes="Valid arguments"
        )

    def _process_arguments(self, properties: dict, parent_path: str):
        required_fields = self.schema.get("required", [])

        for name, prop in properties.items():
            field_path = f"{parent_path}.{name}"

            # --- 1. Structural Checks ---
            if name in required_fields:
                self._emit(
                    PythonIntentType.REQUIRED_ARG_MISSING,
                    field_path,
                    field=name,
                    expected="400",
                )

            # --- 2. Type Checks ---
            # TYPE_VIOLATION only applies to types where sending wrong type causes error
            # String fields accept any string, so TYPE_VIOLATION doesn't apply
            prop_type = prop.get("type")
            if prop_type in ["integer", "number", "boolean"] or "enum" in prop:
                self._emit(
                    PythonIntentType.TYPE_VIOLATION,
                    field_path,
                    field=name,
                    expected="400",
                )

            if not prop.get("nullable", False):
                self._emit(
                    PythonIntentType.NULL_NOT_ALLOWED,
                    field_path,
                    field=name,
                    expected="400",
                )

            # --- 3. Numeric Constraints ---
            if prop.get("type") in ["integer", "number"]:
                if "minimum" in prop:
                    self._emit(
                        PythonIntentType.BOUNDARY_MIN_MINUS_ONE, field_path, field=name
                    )
                    # Also test negative if min is 0 or positive
                    if prop["minimum"] >= 0:
                        self._emit(
                            PythonIntentType.NEGATIVE_VALUE, field_path, field=name
                        )

                if "maximum" in prop:
                    self._emit(
                        PythonIntentType.BOUNDARY_MAX_PLUS_ONE, field_path, field=name
                    )

                if "multipleOf" in prop:
                    self._emit(PythonIntentType.NOT_MULTIPLE_OF, field_path, field=name)

                # Edge case: Zero
                
                if prop.get("minimum", 0) > 0 or prop.get("exclusiveMinimum", False):
                    self._emit(PythonIntentType.ZERO_VALUE, field_path, field=name)

            # --- 4. String Constraints ---
            if prop.get("type") == "string":
                # Check explicitly for enum list OR x-enum-type marker
                if "enum" in prop or "x-enum-type" in prop:
                    self._emit(PythonIntentType.ENUM_MISMATCH, field_path, field=name)

                if "minLength" in prop:
                    self._emit(
                        PythonIntentType.STRING_TOO_SHORT, field_path, field=name
                    )
                    self._emit(PythonIntentType.EMPTY_STRING, field_path, field=name)

                if "maxLength" in prop:
                    self._emit(PythonIntentType.STRING_TOO_LONG, field_path, field=name)

                if "pattern" in prop:
                    self._emit(
                        PythonIntentType.PATTERN_MISMATCH, field_path, field=name
                    )

                # Security Fuzzing (Skip if strict format/enum exists)
                if (
                    not prop.get("enum")
                    and "x-enum-type" not in prop
                    and prop.get("format")
                    not in [
                        "uuid",
                        "date",
                        "date-time",
                    ]
                ):
                    self._emit(PythonIntentType.SQL_INJECTION, field_path, field=name)
                    self._emit(PythonIntentType.XSS_INJECTION, field_path, field=name)
                    self._emit(PythonIntentType.WHITESPACE_ONLY, field_path, field=name)

            # --- 5. Collections (Arrays) ---
            if prop.get("type") == "array":
                self._emit(
                    PythonIntentType.ARRAY_ITEM_TYPE_VIOLATION, field_path, field=name
                )

                # Empty collection check
                if prop.get("minItems", 0) > 0:
                    self._emit(
                        PythonIntentType.EMPTY_COLLECTION, field_path, field=name
                    )

            # --- 6. Complex Objects (Recursion) ---
            if prop.get("type") == "object":
                if "properties" in prop:
                    # Recurse for nested objects
                    self._process_arguments(prop["properties"], field_path)

                # Check for extra fields if strict
                if prop.get("additionalProperties") is False:
                    self._emit(
                        PythonIntentType.OBJECT_EXTRA_FIELD, field_path, field=name
                    )
