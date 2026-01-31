from typing import Any, Dict, List
import uuid


class OpenAPIMutator:
    """
    Handles all mutation logic for OpenAPI/HTTP payloads, headers, path parameters, and query parameters.
    This mutator is specifically designed for REST API testing based on OpenAPI specifications.
    """

    INVALID_TYPE = "__INVALID_TYPE__"

    def mutate_headers(self, headers: dict, intent_type: str, field: str):
        """Applies mutations to request headers."""
        if intent_type == "HEADER_MISSING":
            headers.pop(field, None)
        elif intent_type == "HEADER_INJECTION":
            headers[field] = "ValidValue\r\nSet-Cookie: evil=true"
        elif intent_type == "HEADER_ENUM_MISMATCH":
            headers[field] = "INVALID_HEADER_ENUM"

    def mutate_path_params(
        self, path_params: dict, intent_type: str, field: str, schema: dict, ir: dict
    ):
        """Applies mutations to URL path parameters."""
        if intent_type == "TYPE_VIOLATION":
            path_params[field] = self.INVALID_TYPE
        elif intent_type == "RESOURCE_NOT_FOUND":
            if schema.get("format") == "uuid":
                path_params[field] = str(uuid.uuid4())
            elif schema.get("type") == "integer":
                path_params[field] = 999999
            else:
                path_params[field] = "nonexistent_resource"
        elif intent_type == "FORMAT_INVALID_PATH_PARAM":
            path_params[field] = "not-a-valid-format"
        elif intent_type in [
            "BOUNDARY_MIN_MINUS_ONE",
            "BOUNDARY_MAX_PLUS_ONE",
            "BOUNDARY_MIN_LENGTH_MINUS_ONE",
            "BOUNDARY_MAX_LENGTH_PLUS_ONE",
            "PATTERN_MISMATCH",
            "SQL_INJECTION",
            "XSS_INJECTION",
        ]:
            val = self._calculate_boundary_value(intent_type, schema)
            if intent_type == "SQL_INJECTION":
                val = "' OR '1'='1"
            elif intent_type == "XSS_INJECTION":
                val = "<script>alert(1)</script>"
            elif intent_type == "PATTERN_MISMATCH":
                val = "!!!invalid!!!"
            path_params[field] = val

        # Ensure other path params (not the one we are testing) are valid
        self._fill_happy_path_params(path_params, ir, exclude=[field])

    def _fill_happy_path_params(
        self, path_params: dict, ir: dict, exclude: list = None
    ):
        """Fills all path parameters with valid values except those in exclude."""
        exclude = exclude or []
        for param in ir["inputs"].get("path", []):
            name = param["name"]
            if name in exclude:
                continue
            schema = param.get("schema", {})
            path_params[name] = self._valid_value(schema, name)

    def _valid_value(self, spec: dict, field_name: str = None) -> Any:
        """Generates a valid placeholder value based on schema type."""
        if not isinstance(spec, dict):
            return "__PLACEHOLDER_ANY__"

        t = spec.get("type", "string")
        if t == "string":
            if "enum" in spec:
                return spec["enum"][0]
            fmt = spec.get("format")
            if fmt == "uuid":
                return str(uuid.uuid4())
            return f"__PLACEHOLDER_STRING_{field_name}__"
        if t == "integer":
            return 1
        if t == "number":
            return 1.0
        if t == "boolean":
            return True
        if t == "array":
            return []
        if t == "object":
            return {}
        return "__PLACEHOLDER_ANY__"

    def mutate_query_params(
        self, payload: dict, intent_type: str, field: str, schema: dict
    ) -> bool:
        """Applies mutations to query parameters stored in the payload."""
        if intent_type == "REQUIRED_FIELD_MISSING":
            payload.pop(field, None)
            return True
        elif intent_type == "TYPE_VIOLATION":
            if self._should_skip_query_type_violation(schema):
                return False
            payload[field] = self.INVALID_TYPE
            return True
        return True

    def mutate_body(
        self, payload: dict, intent_type: str, target: str, field: str, schema: dict
    ):
        """Applies mutations to the JSON request body."""
        # Fallback: if field is missing, extract from target
        if not field and target:
            field = target.split(".")[-1].replace("[]", "")

        # Structural - Python Function Specific
        if intent_type == "REQUIRED_ARG_MISSING" and field:
            self._delete_field(payload, field)
        elif intent_type == "UNEXPECTED_ARGUMENT":
            payload["__unexpected_arg__"] = "unexpected_value"
        elif intent_type == "TOO_MANY_POS_ARGS":
            # Add extra positional arguments indicator
            payload["__extra_positional__"] = ["extra1", "extra2"]

        # Structural - General
        elif intent_type == "REQUIRED_FIELD_MISSING" and field:
            self._delete_field(payload, field)
        elif intent_type == "NULL_NOT_ALLOWED" and field:
            self._set_value(payload, target, field, None)
        elif intent_type == "TYPE_VIOLATION":
            self._apply_type_violation(payload, target, field)
        elif intent_type == "ADDITIONAL_PROPERTY_NOT_ALLOWED":
            payload["__extra__"] = "boom"

        # Type System
        elif intent_type == "ARRAY_ITEM_TYPE_VIOLATION":
            if field:
                # Determine the correct invalid type based on expected item type
                item_schema = schema.get("items", {})
                item_type = item_schema.get("type", "")

                # Use a value that actually violates the expected type
                if item_type == "string":
                    invalid_value = 12345  # Use integer to violate string
                elif item_type in ("integer", "number"):
                    invalid_value = "__INVALID_TYPE__"  # Use string to violate number
                elif item_type == "object":
                    invalid_value = "__INVALID_TYPE__"  # Use string to violate object
                elif item_type == "boolean":
                    invalid_value = "__INVALID_TYPE__"  # Use string to violate boolean
                else:
                    invalid_value = self.INVALID_TYPE  # Default fallback

                self._set_value(payload, target, field, [invalid_value])
        elif intent_type == "DICT_KEY_TYPE_VIOLATION":
            if field:
                # Create dict with invalid key type (represented as marker)
                self._set_value(
                    payload, target, field, {"__INVALID_KEY_TYPE__": "value"}
                )
        elif intent_type == "DICT_VALUE_TYPE_VIOLATION":
            if field:
                # Create dict with invalid value type
                self._set_value(payload, target, field, {"key": self.INVALID_TYPE})
        elif intent_type == "OBJECT_VALUE_TYPE_VIOLATION":
            if field:
                # Set object field to a non-object type (string)
                self._set_value(payload, target, field, self.INVALID_TYPE)
        elif intent_type == "ARRAY_ITEM_OBJECT_VALUE_TYPE_VIOLATION":
            if field:
                # Set array item's object field to wrong type
                self._set_value(
                    payload,
                    target,
                    field,
                    [{"__nested_type_violation__": self.INVALID_TYPE}],
                )
        elif intent_type == "NESTED_ARRAY_ITEM_TYPE_VIOLATION":
            if field:
                # Set nested array item to wrong type
                self._set_value(payload, target, field, [[self.INVALID_TYPE]])
        elif intent_type == "ARRAY_SHAPE_VIOLATION":
            if field:
                # Change array to non-array type
                self._set_value(payload, target, field, "not_an_array")

        # Boundaries & Constraints - Numeric
        elif intent_type in [
            "BOUNDARY_MIN_MINUS_ONE",
            "BOUNDARY_MAX_PLUS_ONE",
            "BOUNDARY_MIN_LENGTH_MINUS_ONE",
            "BOUNDARY_MAX_LENGTH_PLUS_ONE",
        ]:
            val = self._calculate_boundary_value(intent_type, schema)
            self._set_value(payload, target, field, val)

        # Boundaries & Constraints - Array Items
        elif intent_type == "BOUNDARY_MIN_ITEMS_MINUS_ONE":
            min_items = schema.get("minItems", 1)
            item_template = self._get_array_item_template(schema, target, payload)
            count = max(0, min_items - 1)
            self._set_value(
                payload, target, field, [item_template] * count if count > 0 else []
            )
        elif intent_type == "BOUNDARY_MAX_ITEMS_PLUS_ONE":
            max_items = schema.get("maxItems", 10)
            item_template = self._get_array_item_template(schema, target, payload)
            self._set_value(payload, target, field, [item_template] * (max_items + 1))

        elif intent_type == "ENUM_MISMATCH":
            self._set_value(payload, target, field, "INVALID_ENUM_VALUE")
        elif intent_type == "STRING_TOO_SHORT":
            self._set_value(payload, target, field, "")
        elif intent_type == "STRING_TOO_LONG":
            self._set_value(payload, target, field, "x" * 1000)
        elif intent_type == "PATTERN_MISMATCH":
            self._set_value(payload, target, field, "!!!invalid_pattern!!!")
        elif intent_type == "FORMAT_INVALID":
            self._set_value(payload, target, field, "invalid_format_value")
        elif intent_type == "NUMBER_TOO_SMALL":
            self._set_value(payload, target, field, -999999)
        elif intent_type == "NUMBER_TOO_LARGE":
            self._set_value(payload, target, field, 999999)
        elif intent_type == "NOT_MULTIPLE_OF":
            # Calculate a value that violates the multipleOf constraint
            multiple_of = schema.get("multipleOf", 1)
            if multiple_of and multiple_of > 0:
                # Generate a value that's not a multiple
                # For small multipleOf like 0.01, use a value with more decimal places
                if multiple_of < 1:
                    # e.g., multipleOf: 0.01 -> use 7.999 (not a multiple of 0.01)
                    invalid_val = 7.999
                else:
                    # e.g., multipleOf: 5 -> use 7 (not a multiple of 5)
                    invalid_val = multiple_of + 2
                self._set_value(payload, target, field, invalid_val)
            else:
                self._set_value(payload, target, field, 7)

        # Data Edge Cases
        elif intent_type == "EMPTY_STRING":
            self._set_value(payload, target, field, "")
        elif intent_type == "WHITESPACE_ONLY":
            self._set_value(payload, target, field, "   ")
        elif intent_type == "ZERO_VALUE":
            self._set_value(payload, target, field, 0)
        elif intent_type == "NEGATIVE_VALUE":
            self._set_value(payload, target, field, -1)
        elif intent_type == "EMPTY_COLLECTION":
            # Set to empty list or dict based on schema
            if schema.get("type") == "array":
                self._set_value(payload, target, field, [])
            else:
                self._set_value(payload, target, field, {})
        elif intent_type == "ARRAY_TOO_SHORT":
            self._set_value(payload, target, field, [])
        elif intent_type == "ARRAY_TOO_LONG":
            self._set_value(payload, target, field, [1] * 1000)
        elif intent_type == "ARRAY_NOT_UNIQUE":
            self._make_array_not_unique(payload, target)
        elif intent_type == "OBJECT_TOO_FEW_PROPERTIES":
            payload.clear()
        elif intent_type == "OBJECT_TOO_MANY_PROPERTIES":
            for i in range(100):
                payload[f"extra_{i}"] = i

        # Complex Objects
        elif intent_type == "OBJECT_MISSING_FIELD":
            if field:
                self._delete_field(payload, field)
        elif intent_type == "OBJECT_EXTRA_FIELD":
            if field and field in payload and isinstance(payload[field], dict):
                payload[field]["__unexpected_field__"] = "unexpected"
            else:
                payload["__unexpected_field__"] = "unexpected"

        # Security
        elif intent_type == "SQL_INJECTION":
            self._set_value(payload, target, field, "' OR '1'='1")
        elif intent_type == "XSS_INJECTION":
            self._set_value(payload, target, field, "<script>alert(1)</script>")
        elif intent_type == "PATH_TRAVERSAL":
            self._set_value(payload, target, field, "../../etc/passwd")
        elif intent_type == "COMMAND_INJECTION":
            self._set_value(payload, target, field, "; cat /etc/passwd")

        # Python Runtime Specifics
        elif intent_type == "MUTABLE_DEFAULT_TRAP":
            # Test mutable default by passing same list/dict reference indicator
            if field:
                self._set_value(
                    payload, target, field, {"__mutable_default_marker__": True}
                )

        # Polymorphism & Logic
        elif intent_type == "DISCRIMINATOR_VIOLATION":
            self._set_value(payload, target, field, "INVALID_DISCRIMINATOR_TYPE")
        elif intent_type in ["DEPENDENCY_VIOLATION", "CONDITIONAL_REQUIRED_MISSING"]:
            if field and "_requires_" in field:
                trigger, missing = field.split("_requires_")
                self._set_value(payload, target, trigger, "present")
                self._delete_field(payload, missing)

        elif intent_type == "UNION_NO_MATCH":
            self._apply_union_no_match(payload, target)

    # Helper methods
    def _set_value(self, payload: dict, target: str, field: str, value: Any):
        """Sets a value deep inside the payload based on target path."""
        if not field:
            return
        if field in payload:
            payload[field] = value
            return

        parts = target.split(".")
        try:
            body_idx = parts.index("body")
        except ValueError:
            return

        current = payload
        path_parts = parts[body_idx + 1 :]
        for part in path_parts[:-1]:
            part_clean = part.replace("[]", "").replace("*", "")
            if part_clean in current:
                current = current[part_clean]
                if isinstance(current, list) and len(current) > 0:
                    current = current[0]

        if isinstance(current, dict):
            current[field] = value

    def _delete_field(self, payload: dict, field: str):
        """Recursively deletes a field from the payload."""
        if field in payload:
            del payload[field]
            return
        for v in payload.values():
            if isinstance(v, dict):
                self._delete_field(v, field)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        self._delete_field(item, field)

    def _apply_type_violation(self, payload: dict, target: str, field: str):
        if field:
            self._set_value(payload, target, field, self.INVALID_TYPE)
        else:
            parent = self._get_target_field(target)
            if parent and parent in payload:
                payload[parent] = self.INVALID_TYPE

    def _apply_union_no_match(self, payload: dict, target: str):
        parent = self._get_target_field(target)
        if not parent:
            if "mode" in payload:
                payload["mode"] = "INVALID_VARIANT_XYZ"
            payload["__FORCE_UNION_MISMATCH__"] = True
            return
        if parent in payload and isinstance(payload[parent], dict):
            payload[parent]["__FORCE_UNION_MISMATCH__"] = True
            if "mode" in payload[parent]:
                payload[parent]["mode"] = "INVALID_VARIANT_XYZ"

    def _make_array_not_unique(self, payload: dict, target: str):
        parent = self._get_target_field(target)
        if parent in payload and isinstance(payload[parent], list):
            if len(payload[parent]) > 0:
                payload[parent].append(payload[parent][0])
            else:
                payload[parent] = [1, 1]

    def _calculate_boundary_value(self, intent_type: str, schema: dict) -> Any:
        if not schema:
            return "INVALID"
        stype = schema.get("type")
        if intent_type == "BOUNDARY_MIN_MINUS_ONE":
            mn = schema.get("minimum", 0)
            return (mn - 1) if stype == "integer" else (mn - 0.01)
        if intent_type == "BOUNDARY_MAX_PLUS_ONE":
            mx = schema.get("maximum", 100)
            return (mx + 1) if stype == "integer" else (mx + 0.01)
        if intent_type == "BOUNDARY_MIN_LENGTH_MINUS_ONE":
            return "x" * max(0, schema.get("minLength", 1) - 1)
        if intent_type == "BOUNDARY_MAX_LENGTH_PLUS_ONE":
            return "x" * (schema.get("maxLength", 10) + 1)
        return "INVALID"

    def _get_target_field(self, target: str):
        parts = target.split(".")
        if "body" in parts:
            idx = parts.index("body")
            if idx + 1 < len(parts):
                return parts[idx + 1].replace("[]", "").replace("*", "")
        return None

    def _should_skip_query_type_violation(self, schema: dict) -> bool:
        if schema.get("type") == "string" and not any(
            k in schema for k in ["minLength", "pattern", "enum"]
        ):
            return True
        return False

    def _get_array_item_template(self, schema: dict, target: str, payload: dict) -> Any:
        """Get a valid item template from existing payload or generate one."""
        field = self._get_target_field(target)
        if (
            field
            and field in payload
            and isinstance(payload[field], list)
            and len(payload[field]) > 0
        ):
            return payload[field][0]
        items_schema = schema.get("items", {})
        return self._valid_value(items_schema)
