from testsuitegen.src.generators.intent_generator.openapi_intent.enums import (
    OpenAPISpecIntentType,
)


class IntentGenerator:
    """
    Intent generator.
    Generates test intents covering:
    - Headers, Path params, Query params, Body fields
    - Boundaries, Constraints, Security fuzzing
    - Polymorphism (discriminators), Logic dependencies
    """

    def __init__(self, ir: dict):
        self.ir = ir
        self.op_id = ir["id"]
        self.inputs = ir["inputs"]
        self.body = self.inputs.get("body")
        self.schema = self.body["schema"] if self.body else None

        self.OK = self._get_success_status()
        self.ERR = self._get_error_status()

        # Track required fields for determining expected status
        self.required_fields = (
            set(self.schema.get("required", [])) if self.schema else set()
        )

        self.intents = []

    def generate(self) -> list[dict]:
        """Main entry point - generates all intents and returns deduplicated list."""
        self._emit_happy_path()
        self._process_headers()
        self._process_path_params()
        self._process_query_params()

        if self.schema:
            self._process_body_schema()

        return self._deduplicate()

    # ========== STATUS CODE HELPERS ==========

    def _get_success_status(self) -> str:
        """Determine the success status code from outputs."""
        for output in self.ir.get("outputs", []):
            if output["status"] in range(200, 301):
                return str(output["status"])
        return "200"

    def _get_error_status(self) -> str:
        """Determine the error status code from errors."""
        for error in self.ir.get("errors", []):
            if error["status"] in range(400, 501):
                return str(error["status"])
        return "422"

    # ========== INTENT EMITTER ==========

    def _determine_expected_status(self, intent_type: str, location: str) -> str:
        """
        Intelligently derives expected HTTP status based on context.
        Uses the OpenAPI spec's defined error status for validation errors.

        Args:
            intent_type: The type of intent being generated
            location: Where the parameter is (path/query/header/body)

        Returns:
            Expected HTTP status code as string
        """
        # 1. Path Parameters -> 404 Not Found
        if location == "path":
            return "404"

        # 2. Auth/Headers -> 400 Bad Request
        if location == "header":
            return "400"

        return self.ERR

    def _is_security_test_applicable(self, prop: dict, field_name: str = None) -> bool:
        """
        Prevents Intent Explosion by filtering security tests.
        Only tests injection if the field is 'open' enough to accept malicious input.

        Args:
            prop: The property schema
            field_name: Optional field name to check if it's required

        Returns:
            True if security testing is applicable, False otherwise
        """
        # 1. Skip if Enum (Input strictly validated against a list)
        if "enum" in prop:
            return False

        # 2. Skip if UUID/Date (Strict format validation blocks injection)
        if prop.get("format") in ["uuid", "date", "date-time", "ipv4", "ipv6"]:
            return False

        # 3. Skip if very short maxLength (Injection payloads won't fit)
        # Typical SQLi is ~10-15 chars minimum to be useful
        if prop.get("maxLength", 100) < 10:
            return False

        # 4. Skip if strict pattern (Regex likely blocks injection)
        if "pattern" in prop:
            return False

        # 5. Skip required fields without explicit security hints
        # Required fields like "full_name", "title" etc. rarely have security validators
        # unless the description explicitly mentions security concerns
        if field_name and field_name in self.required_fields:
            description = prop.get("description", "").lower()
            # Only apply security tests if description hints at security concerns
            security_keywords = [
                "user input",
                "sanitize",
                "validate",
                "xss",
                "sql",
                "injection",
                "vulnerable",
            ]
            if not any(keyword in description for keyword in security_keywords):
                return False

        return True

    def _emit(
        self,
        intent: str,
        target: str,
        field: str = None,
        expected: str = None,
        notes: str = None,
    ) -> None:
        """Adds an intent to the list with intelligent status code determination."""
        # Determine location from target string
        location = "body"
        if ".path." in target:
            location = "path"
        elif ".query." in target:
            location = "query"
        elif ".headers." in target:
            location = "header"

        # Auto-calculate status if not provided
        if not expected:
            expected = self._determine_expected_status(intent, location)

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

    # ========== HAPPY PATH ==========

    def _emit_happy_path(self) -> None:
        """Emits happy path intent(s), with polymorphic variant support."""
        base = f"{self.op_id}.inputs.body" if self.body else f"{self.op_id}.inputs"

        # 1. Check Root Polymorphism
        if self.schema and "oneOf" in self.schema:
            # Generate a Happy Path for EACH variant
            for idx, variant in enumerate(self.schema["oneOf"]):
                self._emit(
                    OpenAPISpecIntentType.HAPPY_PATH.value,
                    base,
                    notes=f"Root Variant {idx}",
                    expected=self.OK,
                )
            return

        # 2. Check Nested Polymorphism
        if self.schema and "properties" in self.schema:
            for name, prop in self.schema["properties"].items():
                if "oneOf" in prop:
                    # Found nested polymorphism - generate variant for each option
                    for idx, variant in enumerate(prop["oneOf"]):
                        # Try to extract discriminator value for better naming
                        desc = f"Variant {idx}"
                        # If variant has a discriminator field with enum, use it
                        if "properties" in variant and "mode" in variant["properties"]:
                            mode_enum = variant["properties"]["mode"].get("enum", [])
                            if mode_enum:
                                desc = f"Variant: {mode_enum[0]}"

                        self._emit(
                            OpenAPISpecIntentType.HAPPY_PATH.value,
                            base,
                            notes=f"Nested {name} -> {desc}",
                            expected=self.OK,
                        )
                    return  # Stop after finding the first major polymorphic switch

        # 3. Fallback - Standard Happy Path
        self._emit(
            OpenAPISpecIntentType.HAPPY_PATH.value,
            base,
            expected=self.OK,
            notes="Standard Valid Request",
        )

    # ========== HEADER ANALYSIS ==========

    def _process_headers(self) -> None:
        """Processes header parameters for required, enum, and injection tests."""
        for header in self.inputs.get("headers", []):
            header_path = f"{self.op_id}.inputs.headers.{header['name']}"
            header_schema = header.get("schema", {})

            # Required header missing
            if header.get("required"):
                self._emit(
                    OpenAPISpecIntentType.HEADER_MISSING.value,
                    header_path,
                    field=header["name"],
                )

            # CRLF injection test - only for strings without enum constraints
            if header_schema.get("type") == "string" and "enum" not in header_schema:
                self._emit(
                    OpenAPISpecIntentType.HEADER_INJECTION.value,
                    header_path,
                    field=header["name"],
                )

            # Enum mismatch
            if "enum" in header_schema:
                self._emit(
                    OpenAPISpecIntentType.HEADER_ENUM_MISMATCH.value,
                    header_path,
                    field=header["name"],
                )

            # CRLF injection test
            self._emit(
                OpenAPISpecIntentType.HEADER_INJECTION.value,
                header_path,
                field=header["name"],
            )

            # Enum mismatch
            if "enum" in header_schema:
                self._emit(
                    OpenAPISpecIntentType.HEADER_ENUM_MISMATCH.value,
                    header_path,
                    field=header["name"],
                )

    # ========== PATH PARAMETER ANALYSIS ==========

    def _process_path_params(self) -> None:
        """Processes path parameters for type, boundary, pattern, and security tests."""
        for param in self.inputs.get("path", []):
            param_path = f"{self.op_id}.inputs.path.{param['name']}"
            param_schema = param.get("schema", {})

            # 1. Resource Not Found (Valid format, wrong ID) -> 404
            self._emit(
                OpenAPISpecIntentType.RESOURCE_NOT_FOUND.value,
                param_path,
                field=param["name"],
                expected="404",
                notes="Valid format, nonexistent resource",
            )

            # 2. Format Invalid (Invalid format) -> 400
            # Only if format is specified (uuid, int, etc.)
            if param_schema.get("format") or param_schema.get("type") in [
                "integer",
                "number",
            ]:
                self._emit(
                    OpenAPISpecIntentType.FORMAT_INVALID_PATH_PARAM.value,
                    param_path,
                    field=param["name"],
                    expected="400",
                    notes="Invalid format",
                )

            # String-specific constraints
            if param_schema.get("type") == "string":
                self._process_string_path_param(param_path, param["name"], param_schema)

            # Numeric-specific constraints
            if param_schema.get("type") in ["integer", "number"]:
                self._process_numeric_path_param(
                    param_path, param["name"], param_schema
                )

    def _process_string_path_param(self, path: str, name: str, schema: dict) -> None:
        """Processes string path parameter constraints."""
        # Pattern mismatch
        if "pattern" in schema:
            self._emit(
                OpenAPISpecIntentType.PATTERN_MISMATCH.value,
                path,
                field=name,
                notes=f"Pattern: {schema['pattern']}",
            )

        # Length boundaries
        if "minLength" in schema:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MIN_LENGTH_MINUS_ONE.value,
                path,
                field=name,
                notes=f"Len: {schema['minLength']}-1",
            )

        if "maxLength" in schema:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MAX_LENGTH_PLUS_ONE.value,
                path,
                field=name,
                notes=f"Len: {schema['maxLength']}+1",
            )

        # Security fuzzing (skip for UUIDs and dates)
        if schema.get("format") not in ["uuid", "date", "date-time"]:
            self._emit(OpenAPISpecIntentType.SQL_INJECTION.value, path, field=name)
            self._emit(OpenAPISpecIntentType.XSS_INJECTION.value, path, field=name)

    def _process_numeric_path_param(self, path: str, name: str, schema: dict) -> None:
        """Processes numeric path parameter constraints."""
        if "minimum" in schema:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MIN_MINUS_ONE.value,
                path,
                field=name,
                notes=f"Val: {schema['minimum']}-1",
            )

        if "maximum" in schema:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MAX_PLUS_ONE.value,
                path,
                field=name,
                notes=f"Val: {schema['maximum']}+1",
            )

    # ========== QUERY PARAMETER ANALYSIS ==========

    def _process_query_params(self) -> None:
        """Processes query parameters for required and type violations."""
        for param in self.inputs.get("query", []):
            param_path = f"{self.op_id}.inputs.query.{param['name']}"
            param_schema = param.get("schema", {})

            # Required field missing
            if param.get("required"):
                self._emit(
                    OpenAPISpecIntentType.REQUIRED_FIELD_MISSING.value,
                    param_path,
                    field=param["name"],
                )

            # Type violation - only for types where sending wrong type causes validation error
            # String fields accept any string, so TYPE_VIOLATION doesn't apply
            param_type = param_schema.get("type")
            if param_type in ["integer", "number", "boolean"] or "enum" in param_schema:
                self._emit(
                    OpenAPISpecIntentType.TYPE_VIOLATION.value,
                    param_path,
                    field=param["name"],
                )

    # ========== BODY SCHEMA ANALYSIS ==========

    def _process_body_schema(self) -> None:
        """Processes the request body schema for all constraints and validations."""
        base = f"{self.op_id}.inputs.body"

        # Required fields
        self._process_required_fields(base)

        # Schema dependencies
        self._process_schema_dependencies(base)

        # Property-level constraints (recursive)
        self._process_properties(self.schema.get("properties", {}), base)

        # Root-level constraints
        self._process_root_constraints(base)

    def _process_required_fields(self, base: str) -> None:
        """Emits intents for required field violations."""
        for required_field in self.schema.get("required", []):
            self._emit(
                OpenAPISpecIntentType.REQUIRED_FIELD_MISSING.value,
                f"{base}.{required_field}",
                field=required_field,
            )

    def _process_schema_dependencies(self, base: str) -> None:
        """Processes OpenAPI schema dependencies (field X requires field Y)."""
        dependencies = self.schema.get("dependencies", {})
        for field, deps in dependencies.items():
            if isinstance(deps, list):
                for dep in deps:
                    self._emit(
                        OpenAPISpecIntentType.DEPENDENCY_VIOLATION.value,
                        base,
                        field=f"{field}_requires_{dep}",
                        notes=f"Field {field} requires {dep}",
                    )

    def _process_conditional_dependencies(self, base: str) -> None:
        """Processes conditional dependencies (if field A exists, field B is required)."""
        # Support both OpenAPI 3.0 'dependencies' and 3.1 'dependentRequired'
        deps = self.schema.get("dependencies", {}) or self.schema.get(
            "dependentRequired", {}
        )

        for field, requirements in deps.items():
            if isinstance(requirements, list):
                for req_field in requirements:
                    self._emit(
                        OpenAPISpecIntentType.CONDITIONAL_REQUIRED_MISSING.value,
                        base,
                        field=f"{field}_requires_{req_field}",
                        notes=f"When {field} is present, {req_field} is required",
                    )

    def _process_root_constraints(self, base: str) -> None:
        """Processes root-level object constraints."""
        # Additional properties
        if self.schema.get("additionalProperties") is False:
            self._emit(
                OpenAPISpecIntentType.ADDITIONAL_PROPERTY_NOT_ALLOWED.value, base
            )

        # Min/max properties
        if "minProperties" in self.schema:
            self._emit(
                OpenAPISpecIntentType.OBJECT_TOO_FEW_PROPERTIES.value,
                base,
                notes=f"Min properties: {self.schema['minProperties']}",
            )

        if "maxProperties" in self.schema:
            self._emit(
                OpenAPISpecIntentType.OBJECT_TOO_MANY_PROPERTIES.value,
                base,
                notes=f"Max properties: {self.schema['maxProperties']}",
            )

    # ========== RECURSIVE PROPERTY ANALYSIS ==========

    def _process_properties(self, properties: dict, parent_path: str) -> None:
        """Recursively processes properties and their constraints."""
        for name, prop in properties.items():
            field_path = f"{parent_path}.{name}"

            # Common validations
            self._process_common_validations(field_path, name, prop)

            # Type-specific validations
            prop_type = prop.get("type")

            # Handle anyOf nullable patterns (e.g., anyOf: [{type: string}, {type: null}])
            if "anyOf" in prop and not prop_type:
                # Find the non-null type in the anyOf
                for variant in prop["anyOf"]:
                    if variant.get("type") == "string":
                        prop_type = "string"
                        # Merge constraints from the variant into prop for processing
                        merged_prop = {**prop, **variant}
                        self._process_string_field(field_path, name, merged_prop)
                        prop_type = None  # Don't process again below
                        break

            if prop_type == "string":
                self._process_string_field(field_path, name, prop)
            elif prop_type in ["integer", "number"]:
                self._process_numeric_field(field_path, name, prop)
            elif prop_type == "array":
                self._process_array_field(field_path, name, prop)
            elif prop_type == "object":
                self._process_object_field(field_path, name, prop)

    def _process_common_validations(
        self, field_path: str, name: str, prop: dict
    ) -> None:
        """Processes validations common to all field types."""
        # Nullability
        if prop.get("nullable") is False:
            self._emit(
                OpenAPISpecIntentType.NULL_NOT_ALLOWED.value, field_path, field=name
            )

        # Type violation - only for types where sending wrong type causes validation error
        # String fields accept any string, so TYPE_VIOLATION doesn't apply to them
        prop_type = prop.get("type")
        if prop_type in ["integer", "number", "boolean"] or "enum" in prop:
            self._emit(
                OpenAPISpecIntentType.TYPE_VIOLATION.value, field_path, field=name
            )

        # Union types
        if "oneOf" in prop:
            self._emit(
                OpenAPISpecIntentType.UNION_NO_MATCH.value, field_path, field=name
            )

        # Polymorphic discriminator
        if "oneOf" in prop or "anyOf" in prop:
            self._process_discriminator(field_path, prop)

    def _process_discriminator(self, field_path: str, prop: dict) -> None:
        """Processes polymorphic discriminator if present."""
        discriminator = prop.get("discriminator")
        if discriminator and "propertyName" in discriminator:
            disc_prop = discriminator["propertyName"]
            self._emit(
                OpenAPISpecIntentType.DISCRIMINATOR_VIOLATION.value,
                f"{field_path}.{disc_prop}",
                field=disc_prop,
                notes="Invalid discriminator value",
            )

    # ========== STRING FIELD PROCESSING ==========

    def _process_string_field(self, field_path: str, name: str, prop: dict) -> None:
        """Processes string-specific constraints and validations."""
        # Enum
        if "enum" in prop:
            self._emit(
                OpenAPISpecIntentType.ENUM_MISMATCH.value,
                field_path,
                field=name,
                notes=f"Value not in enum: {prop['enum']}",
            )

        # Length boundaries
        self._process_string_length_boundaries(field_path, name, prop)

        # Pattern
        if "pattern" in prop:
            self._emit(
                OpenAPISpecIntentType.PATTERN_MISMATCH.value,
                field_path,
                field=name,
                notes=f"Pattern: {prop['pattern']}",
            )

        # Format
        if "format" in prop:
            self._emit(
                OpenAPISpecIntentType.FORMAT_INVALID.value,
                field_path,
                field=name,
                notes=f"Format: {prop['format']}",
            )

        # Security fuzzing
        self._process_string_security_tests(field_path, name, prop)

    def _process_string_length_boundaries(
        self, field_path: str, name: str, prop: dict
    ) -> None:
        """Processes minLength and maxLength boundaries."""
        is_required = name in self.required_fields
        is_anyof = "anyOf" in prop
        has_pattern = "pattern" in prop
        has_maxlength_only = "maxLength" in prop and "minLength" not in prop

        # Check for pattern in anyOf variants
        if is_anyof:
            for variant in prop["anyOf"]:
                if "pattern" in variant:
                    has_pattern = True
                # Check if any variant has constraints we can use
                if "maxLength" in variant and "minLength" not in variant:
                    has_maxlength_only = True

        if "minLength" in prop:
            if prop["minLength"] > 0:
                self._emit(
                    OpenAPISpecIntentType.BOUNDARY_MIN_LENGTH_MINUS_ONE.value,
                    field_path,
                    field=name,
                    notes=f"Len: {prop['minLength']}-1",
                )
            else:
                # minLength=0 means empty string is valid
                self._emit(
                    OpenAPISpecIntentType.EMPTY_STRING.value,
                    field_path,
                    field=name,
                    expected=self.OK,
                )
        elif prop.get("nullable") is not False:
            # Determine expected status for EMPTY_STRING test
            if has_pattern:
                # Empty string won't match the pattern
                expected = self.ERR
                self._emit(
                    OpenAPISpecIntentType.EMPTY_STRING.value,
                    field_path,
                    field=name,
                    expected=expected,
                )
            elif is_anyof and not has_maxlength_only:
                # Skip EMPTY_STRING for anyOf fields without maxLength constraint
                # These have unpredictable behavior (might have custom validators)
                pass
            elif not is_required:
                # Skip EMPTY_STRING for optional fields without explicit minLength=0
                # Many APIs have custom validation that rejects empty strings even for
                # optional fields, making behavior unpredictable. Only test empty strings
                # when minLength=0 is explicitly set (handled above).
                pass
            else:
                self._emit(
                    OpenAPISpecIntentType.EMPTY_STRING.value,
                    field_path,
                    field=name,
                    expected=self.ERR,
                )

        if "maxLength" in prop:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MAX_LENGTH_PLUS_ONE.value,
                field_path,
                field=name,
                notes=f"Len: {prop['maxLength']}+1",
            )

    def _process_string_security_tests(
        self, field_path: str, name: str, prop: dict
    ) -> None:
        """Processes security fuzzing tests for strings with noise reduction."""
        # Use intelligent filter to avoid test explosion
        if self._is_security_test_applicable(prop, field_name=name):
            self._emit(
                OpenAPISpecIntentType.SQL_INJECTION.value, field_path, field=name
            )
            self._emit(
                OpenAPISpecIntentType.XSS_INJECTION.value, field_path, field=name
            )
            self._emit(
                OpenAPISpecIntentType.WHITESPACE_ONLY.value, field_path, field=name
            )

    # ========== NUMERIC FIELD PROCESSING ==========

    def _process_numeric_field(self, field_path: str, name: str, prop: dict) -> None:
        """Processes numeric-specific constraints (integer/number)."""
        # Minimum boundary
        if "minimum" in prop:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MIN_MINUS_ONE.value,
                field_path,
                field=name,
                notes=f"Boundary: {prop['minimum']} - 1",
            )

        # Maximum boundary
        if "maximum" in prop:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MAX_PLUS_ONE.value,
                field_path,
                field=name,
                notes=f"Boundary: {prop['maximum']} + 1",
            )

        # Multiple of
        if "multipleOf" in prop:
            self._emit(
                OpenAPISpecIntentType.NOT_MULTIPLE_OF.value,
                field_path,
                field=name,
                notes=f"Multiple of: {prop['multipleOf']}",
            )

    # ========== ARRAY FIELD PROCESSING ==========

    def _process_array_field(self, field_path: str, name: str, prop: dict) -> None:
        """Processes array-specific constraints and nested items."""
        # Array item type violation
        self._emit(OpenAPISpecIntentType.ARRAY_ITEM_TYPE_VIOLATION.value, field_path)

        # Item count boundaries
        if "minItems" in prop:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MIN_ITEMS_MINUS_ONE.value,
                field_path,
                field=name,
                notes=f"Items: {prop['minItems']}-1",
            )

        if "maxItems" in prop:
            self._emit(
                OpenAPISpecIntentType.BOUNDARY_MAX_ITEMS_PLUS_ONE.value,
                field_path,
                field=name,
                notes=f"Items: {prop['maxItems']}+1",
            )

        # Unique items
        if prop.get("uniqueItems"):
            self._emit(
                OpenAPISpecIntentType.ARRAY_NOT_UNIQUE.value,
                field_path,
                field=name,
                notes="Array must have unique items",
            )

        # Process array items
        self._process_array_items(field_path, prop.get("items", {}))

    def _process_array_items(self, field_path: str, items: dict) -> None:
        """Processes array item schemas recursively."""
        item_path = f"{field_path}[]"

        # Union in items
        if "oneOf" in items:
            self._emit(OpenAPISpecIntentType.UNION_NO_MATCH.value, item_path)

        # Object items
        if items.get("type") == "object":
            self._emit(
                OpenAPISpecIntentType.OBJECT_VALUE_TYPE_VIOLATION.value, item_path
            )

            # Recurse into object properties
            if "properties" in items:
                self._process_properties(items["properties"], item_path)

            # Nested arrays in object items
            for key, value in items.get("properties", {}).items():
                if value.get("type") == "array":
                    self._emit(
                        OpenAPISpecIntentType.ARRAY_ITEM_TYPE_VIOLATION.value,
                        f"{item_path}.{key}",
                    )
                    if "oneOf" in value.get("items", {}):
                        self._emit(
                            OpenAPISpecIntentType.UNION_NO_MATCH.value,
                            f"{item_path}.{key}[]",
                        )

    # ========== OBJECT FIELD PROCESSING ==========

    def _process_object_field(self, field_path: str, name: str, prop: dict) -> None:
        """Processes nested object properties and additionalProperties."""
        # Recurse into nested properties
        if "properties" in prop:
            self._process_properties(prop["properties"], field_path)

        # Additional properties
        if "additionalProperties" in prop:
            self._process_additional_properties(
                field_path, prop["additionalProperties"]
            )

    def _process_additional_properties(self, field_path: str, additional_props) -> None:
        """Processes additionalProperties schema."""
        # Only process if it's a schema (dict), not a boolean
        if not isinstance(additional_props, dict):
            return

        self._emit(OpenAPISpecIntentType.OBJECT_VALUE_TYPE_VIOLATION.value, field_path)

        # Union in additional properties
        if "oneOf" in additional_props:
            self._emit(OpenAPISpecIntentType.UNION_NO_MATCH.value, f"{field_path}.*")

        # Array in additional properties
        elif additional_props.get("type") == "array":
            self._emit(
                OpenAPISpecIntentType.ARRAY_ITEM_TYPE_VIOLATION.value, f"{field_path}.*"
            )

            # Object in array items
            ap_items = additional_props.get("items", {})
            if ap_items.get("type") == "object":
                self._emit(
                    OpenAPISpecIntentType.OBJECT_VALUE_TYPE_VIOLATION.value,
                    f"{field_path}.*[]",
                )

    # ========== DEDUPLICATION ==========

    def _deduplicate(self) -> list[dict]:
        """Removes duplicate intents based on (intent, target) combination."""
        seen = set()
        final = []

        for intent in self.intents:
            key = (intent["intent"], intent["target"])
            if key not in seen:
                seen.add(key)
                final.append(intent)

        return final


def generate_intents(ir: dict) -> list[dict]:
    """
    Main entry point for intent generation.
    Maintains backward compatibility with function-based API.
    """
    generator = IntentGenerator(ir)
    return generator.generate()
