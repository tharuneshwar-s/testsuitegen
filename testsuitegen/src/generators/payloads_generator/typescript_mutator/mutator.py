"""
TypeScript Function Mutator

Handles all mutation logic for TypeScript function parameters.
This mutator is specifically designed for TypeScript function testing
based on type annotations, interfaces, and generics.
"""

from typing import Any, Dict, List, Optional
from copy import deepcopy


class TypeScriptMutator:
    """
    Handles all mutation logic for TypeScript function parameters.
    Generates mutated argument sets for testing TypeScript functions.
    """

    INVALID_TYPE = "__INVALID_TYPE__"

    # --- Interface compatibility with OpenAPIMutator ---
    def mutate_body(
        self, payload: dict, intent_type: str, target: str, field: str, schema: dict
    ):
        """Alias for mutate_args to maintain interface compatibility."""
        return self.mutate_args(payload, intent_type, target, field, schema)

    def mutate_headers(self, headers: dict, intent_type: str, field: str):
        """No-op for TypeScript functions (no HTTP headers)."""
        pass

    def mutate_path_params(
        self, path_params: dict, intent_type: str, field: str, schema: dict, ir: dict
    ):
        """No-op for TypeScript functions (no URL path params)."""
        pass

    def mutate_query_params(
        self, payload: dict, intent_type: str, field: str, schema: dict
    ) -> bool:
        """No-op for TypeScript functions (no query params)."""
        return True

    # --- TypeScript-specific mutation logic ---
    def mutate_args(
        self,
        args: dict,
        intent_type: str,
        target: str,
        field: str,
        schema: dict,
    ) -> dict:
        """
        Applies mutations to TypeScript function parameters.
        
        Args:
            args: Dictionary of parameter name -> value
            intent_type: The type of mutation to apply
            target: The target path (e.g., "body.param_name")
            field: The specific field/parameter to mutate
            schema: The schema for the field being mutated
            
        Returns:
            The mutated arguments dictionary
        """
        # Fallback: if field is missing, extract from target
        if not field and target:
            field = target.split(".")[-1].replace("[]", "")

        # --- 1. Structural Mutations ---
        if intent_type == "REQUIRED_ARG_MISSING" and field:
            # Remove a required parameter
            args.pop(field, None)

        elif intent_type == "UNEXPECTED_ARGUMENT":
            # Add an unexpected parameter
            args["__unexpected_param__"] = "unexpected_value"

        elif intent_type == "TOO_MANY_POS_ARGS":
            # Marker to indicate too many arguments
            args["__extra_positional__"] = ["extra_arg_1", "extra_arg_2"]

        # --- 2. Type Violations ---
        elif intent_type == "TYPE_VIOLATION" and field:
            # Set parameter to wrong type
            self._set_invalid_type(args, field, schema)

        elif intent_type == "NULL_NOT_ALLOWED" and field:
            # Set parameter to null when not allowed (undefined in TS context)
            args[field] = None

        elif intent_type == "ARRAY_ITEM_TYPE_VIOLATION" and field:
            # Array with wrong item type
            item_schema = schema.get("items", {})
            item_type = item_schema.get("type", "")
            if item_type == "string":
                args[field] = [12345]  # number instead of string
            elif item_type in ("integer", "number"):
                args[field] = ["wrong_type"]  # string instead of number
            else:
                args[field] = [self.INVALID_TYPE]

        elif intent_type == "UNION_NO_MATCH" and field:
            # Value that doesn't match any union type
            args[field] = {"__INVALID_UNION_VARIANT__": True}

        # --- 3. TypeScript-Specific Types ---
        elif intent_type == "GENERIC_TYPE_VIOLATION" and field:
            # Violate a generic type constraint
            args[field] = {"__GENERIC_VIOLATION__": True}

        elif intent_type == "INTERFACE_MISSING_PROPERTY" and field:
            # Remove a required property from an interface
            if field in args and isinstance(args[field], dict):
                if args[field]:
                    first_key = next(iter(args[field]))
                    del args[field][first_key]

        elif intent_type == "READONLY_MUTATION" and field:
            # Marker to test readonly property mutation
            args[field] = {"__READONLY_MUTATION__": True}

        # --- 4. Constraint Violations ---
        elif intent_type == "BOUNDARY_MIN_MINUS_ONE" and field:
            val = self._calculate_boundary_value(intent_type, schema)
            args[field] = val

        elif intent_type == "BOUNDARY_MAX_PLUS_ONE" and field:
            val = self._calculate_boundary_value(intent_type, schema)
            args[field] = val

        elif intent_type == "STRING_TOO_SHORT" and field:
            min_len = schema.get("minLength", 1)
            args[field] = "x" * max(0, min_len - 1)

        elif intent_type == "STRING_TOO_LONG" and field:
            max_len = schema.get("maxLength", 100)
            args[field] = "x" * (max_len + 100)

        elif intent_type == "PATTERN_MISMATCH" and field:
            args[field] = "!!!invalid_pattern!!!"

        elif intent_type == "ENUM_MISMATCH" and field:
            args[field] = "INVALID_ENUM_VALUE"

        # --- 5. Data Edge Cases ---
        elif intent_type == "EMPTY_STRING" and field:
            args[field] = ""

        elif intent_type == "WHITESPACE_ONLY" and field:
            args[field] = "   "

        elif intent_type == "ZERO_VALUE" and field:
            args[field] = 0

        elif intent_type == "NEGATIVE_VALUE" and field:
            args[field] = -1

        elif intent_type == "EMPTY_COLLECTION" and field:
            if schema.get("type") == "array":
                args[field] = []
            else:
                args[field] = {}

        # --- 6. Complex Objects ---
        elif intent_type == "OBJECT_MISSING_FIELD" and field:
            if field in args and isinstance(args[field], dict):
                if args[field]:
                    first_key = next(iter(args[field]))
                    del args[field][first_key]

        elif intent_type == "OBJECT_EXTRA_FIELD" and field:
            if field in args and isinstance(args[field], dict):
                args[field]["__unexpected_field__"] = "unexpected"
            else:
                args["__unexpected_field__"] = "unexpected"

        # --- 7. Security Fuzzing ---
        elif intent_type == "SQL_INJECTION" and field:
            args[field] = "' OR '1'='1"

        elif intent_type == "XSS_INJECTION" and field:
            args[field] = "<script>alert(1)</script>"

        elif intent_type == "PATH_TRAVERSAL" and field:
            args[field] = "../../etc/passwd"

        elif intent_type == "COMMAND_INJECTION" and field:
            args[field] = "; cat /etc/passwd"

        return args

    def _set_invalid_type(self, args: dict, field: str, schema: dict):
        """Sets an invalid type value based on what type is expected."""
        expected_type = schema.get("type", "string")
        
        if expected_type == "integer" or expected_type == "number":
            args[field] = "not_a_number"
        elif expected_type == "string":
            args[field] = 12345  # number instead of string
        elif expected_type == "boolean":
            args[field] = "not_a_boolean"
        elif expected_type == "array":
            args[field] = "not_an_array"
        elif expected_type == "object":
            args[field] = "not_an_object"
        else:
            args[field] = self.INVALID_TYPE

    def _calculate_boundary_value(self, intent_type: str, schema: dict) -> Any:
        """Calculate boundary values for schema constraints."""
        if not schema:
            return "INVALID"
        
        stype = schema.get("type")
        
        if intent_type == "BOUNDARY_MIN_MINUS_ONE":
            mn = schema.get("minimum", 0)
            return (mn - 1) if stype == "integer" else (mn - 0.01)
        
        if intent_type == "BOUNDARY_MAX_PLUS_ONE":
            mx = schema.get("maximum", 100)
            return (mx + 1) if stype == "integer" else (mx + 0.01)
        
        return "INVALID"
