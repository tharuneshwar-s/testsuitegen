import uuid
from copy import deepcopy
from typing import List, Any, Optional

# Import all mutators
from testsuitegen.src.generators.payloads_generator.openapi_mutator.mutator import (
    OpenAPIMutator,
)
from testsuitegen.src.generators.payloads_generator.python_mutator.mutator import (
    PythonMutator,
)
from testsuitegen.src.generators.payloads_generator.typescript_mutator.mutator import (
    TypeScriptMutator,
)




def get_mutator_for_kind(kind: str):
    """
    Factory function to get the appropriate mutator based on IR operation kind.
    
    Args:
        kind: The kind of operation ('http', 'function', 'typescript_function')
        
    Returns:
        An instance of the appropriate mutator class
    """
    if kind == "function":
        return PythonMutator()
    elif kind == "typescript_function":
        return TypeScriptMutator()
    else:  # Default to OpenAPI for 'http' and unknown kinds
        return OpenAPIMutator()


class PayloadGenerator:
    """
    Payload Generator.
    Converts IR and Intents into concrete test cases using a mutation-based approach.
    Supports 'Golden Record' optimization to maintain high-fidelity data across tests.
    Uses the appropriate mutator based on the source type (OpenAPI, Python, TypeScript).
    """

    def __init__(self, ir: dict, base_payload_override: Optional[dict] = None):
        self.ir = ir
        self.base_path_params = self._build_path_params()
        self.base_headers = self._build_valid_headers()
        
        # Select the appropriate mutator based on IR kind
        kind = ir.get("kind", "http")
        self.mutator = get_mutator_for_kind(kind)

        # Initialize the base payload (Golden Record)
        if base_payload_override:
            self.base_payload = deepcopy(base_payload_override)
            body_schema = self.ir["inputs"].get("body", {}).get("schema", {})
            self._recursive_sanitize(self.base_payload, body_schema)
        else:
            self.base_payload = self._build_valid_payload()

    def generate(self, intents: List[dict]) -> List[dict]:
        """
        Iterates through intents and applies mutations
        to the base Golden Record.
        """
        results = []

        for intent in intents:
            # Step 1: Start every test case with a clean copy of the Golden Record
            payload = deepcopy(self.base_payload)
            path_params = deepcopy(self.base_path_params)
            headers = deepcopy(self.base_headers)

            intent_type = intent["intent"]
            target = intent["target"]
            field = intent.get("field")
            field_schema = self._get_schema_for_field(target)

            # Step 2: Handle Happy Path
            if intent_type == "HAPPY_PATH":
                self._handle_happy_path(payload, path_params)
                results.append(self._wrap(intent, payload, path_params, headers))
                continue

            # Step 3: Handle Header Mutations
            if "inputs.headers" in target:
                self.mutator.mutate_headers(headers, intent_type, field)
                results.append(self._wrap(intent, payload, path_params, headers))
                continue

            # Step 4: Handle Path Parameter Mutations
            if "inputs.path" in target:
                self.mutator.mutate_path_params(
                    path_params, intent_type, field, field_schema, self.ir
                )
                results.append(self._wrap(intent, payload, path_params, headers))
                continue

            # Step 5: Handle Query Parameter Mutations
            if "inputs.query" in target:
                if self.mutator.mutate_query_params(
                    payload, intent_type, field, field_schema
                ):
                    results.append(self._wrap(intent, payload, path_params, headers))
                continue

            # Step 6: Handle Body Mutations (The bulk of the logic)
            self.mutator.mutate_body(payload, intent_type, target, field, field_schema)

            # Step 7: Wrap and append the result
            results.append(self._wrap(intent, payload, path_params, headers))

        # Step 8: Return all generated results
        return results

    def _wrap(
        self,
        intent: dict,
        payload: dict,
        path_params: dict = None,
        headers: dict = None,
    ):
        expected_status = int(intent["expected"])
        result = {
            "operation_id": intent["operation_id"],
            "intent": intent["intent"],
            "expected_status": expected_status,
            "payload": payload,
            "response": self._generate_mock_response(expected_status),
        }
        if path_params:
            result["path_params"] = path_params
        if headers:
            result["headers"] = headers
        return result

    def _generate_mock_response(self, status_code: int) -> dict:
        """Generate a mock response based on the operation's output schemas."""
        outputs = self.ir.get("outputs", [])
        
        # Find matching output schema for the expected status code
        matching_output = None
        for output in outputs:
            if output.get("status") == status_code:
                matching_output = output
                break
        
        # If no exact match, try to find a 2xx response for happy path
        if not matching_output and 200 <= status_code < 300:
            for output in outputs:
                if 200 <= output.get("status", 0) < 300:
                    matching_output = output
                    break
        
        if not matching_output or not matching_output.get("schema"):
            return {"status": status_code, "body": None}
        
        schema = matching_output["schema"]
        mock_body = self._generate_value_from_schema(schema)
        
        return {
            "status": status_code,
            "content_type": matching_output.get("content_type", "application/json"),
            "body": mock_body,
        }

    def _generate_value_from_schema(self, schema: dict) -> Any:
        """Recursively generate mock data from a schema."""
        if not isinstance(schema, dict):
            return None
        
        # Handle oneOf/anyOf by picking first option
        if "oneOf" in schema:
            return self._generate_value_from_schema(schema["oneOf"][0])
        if "anyOf" in schema:
            return self._generate_value_from_schema(schema["anyOf"][0])
        
        schema_type = schema.get("type", "object")
        
        # Use example if provided
        if "example" in schema:
            return schema["example"]
        
        # Use default if provided
        if "default" in schema:
            return schema["default"]
        
        # Use enum first value if provided
        if "enum" in schema:
            return schema["enum"][0]
        
        if schema_type == "object":
            result = {}
            properties = schema.get("properties", {})
            for prop_name, prop_schema in properties.items():
                result[prop_name] = self._generate_value_from_schema(prop_schema)
            return result
        
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            return [self._generate_value_from_schema(items_schema)]
        
        elif schema_type == "string":
            fmt = schema.get("format")
            if fmt == "uuid":
                return "550e8400-e29b-41d4-a716-446655440000"
            elif fmt == "date-time":
                return "2024-01-15T10:30:00Z"
            elif fmt == "date":
                return "2024-01-15"
            elif fmt == "email":
                return "user@example.com"
            elif fmt == "uri":
                return "https://example.com/resource"
            return "sample_string"
        
        elif schema_type == "integer":
            return 1
        
        elif schema_type == "number":
            return 1.0
        
        elif schema_type == "boolean":
            return True
        
        return None

    def _handle_happy_path(self, payload: dict, path_params: dict):
        """Ensure required query and path params are valid."""
        for query_param in self.ir["inputs"].get("query", []):
            if query_param.get("required", False):
                name = query_param["name"]
                if name not in payload:
                    payload[name] = self._valid_value(
                        query_param.get("schema", {}), name
                    )

        self._fill_happy_path_params(path_params)

    def _recursive_sanitize(self, data: Any, schema: dict):
        """Remove invalid fields based on schema."""
        if not isinstance(data, dict) or not schema:
            return
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}).keys())
            for k in list(data.keys()):
                if k not in allowed:
                    del data[k]
        for k, v in data.items():
            if k in schema.get("properties", {}):
                self._recursive_sanitize(v, schema["properties"][k])

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
        if intent_type == "BOUNDARY_MIN_LENGTH_MINUS_ONE":
            return "x" * max(0, schema.get("minLength", 1) - 1)
        if intent_type == "BOUNDARY_MAX_LENGTH_PLUS_ONE":
            return "x" * (schema.get("maxLength", 10) + 1)
        return "INVALID"

    def _get_schema_for_field(self, target: str) -> dict:
        """Retrieve schema for a specific field in the target."""
        parts = target.split(".")
        current = self.ir["inputs"]
        if "body" in parts:
            current = current.get("body", {}).get("schema", {})
            for part in parts[parts.index("body") + 1 :]:
                if not part or part in ["[]", "*"]:
                    continue
                if "properties" in current:
                    current = current["properties"].get(part, {})
                elif "items" in current:
                    current = current["items"]
                    if "properties" in current:
                        current = current["properties"].get(part, {})
        return current if isinstance(current, dict) else {}

    def _valid_value(self, spec: dict, field_name: str = None) -> Any:
        """Generate a valid value based on the schema."""
        if not isinstance(spec, dict):
            return "__PLACEHOLDER_ANY__"
        if "oneOf" in spec:
            return self._valid_value(spec["oneOf"][0], field_name)
        if "anyOf" in spec:
            return self._valid_value(spec["anyOf"][0], field_name)

        t = spec.get("type")
        if t == "string":
            if "enum" in spec:
                return spec["enum"][0]
            fmt = spec.get("format")
            if fmt == "uuid":
                return f"__PLACEHOLDER_UUID_{field_name}__"
            if fmt == "date-time":
                return f"__PLACEHOLDER_DATETIME_{field_name}__"
            return f"__PLACEHOLDER_STRING_{field_name}__"
        if t == "integer":
            # Respect minimum/maximum constraints
            min_val = spec.get("minimum", spec.get("exclusiveMinimum"))
            if min_val is not None:
                # For exclusiveMinimum, add 1
                if "exclusiveMinimum" in spec:
                    return int(min_val) + 1
                return int(min_val)
            return 1
        if t == "number":
            # Respect minimum/maximum constraints
            min_val = spec.get("minimum", spec.get("exclusiveMinimum"))
            if min_val is not None:
                # For exclusiveMinimum, add a small delta
                if "exclusiveMinimum" in spec:
                    return float(min_val) + 0.01
                return float(min_val)
            return 1.0
        if t == "boolean":
            return True
        if t == "array":
            return [self._valid_value(spec.get("items", {}), field_name)]
        if t == "object":
            # Recursively generate valid values for object properties
            properties = spec.get("properties", {})
            if properties:
                result = {}
                for prop_name, prop_schema in properties.items():
                    result[prop_name] = self._valid_value(prop_schema, prop_name)
                return result
            return {}
        return "__PLACEHOLDER_ANY__"

    def _invalid_value(self, spec: dict) -> Any:
        """Generate an invalid value for the schema."""
        t = spec.get("type", "string")
        if t == "integer":
            return "not_an_int"
        if t == "boolean":
            return "not_a_bool"
        return 12345

    def _should_skip_query_type_violation(self, schema: dict) -> bool:
        """Check if query type violation should be skipped."""
        if schema.get("type") == "string" and not any(
            k in schema for k in ["minLength", "pattern", "enum"]
        ):
            return True
        return False

    def _fill_happy_path_params(self, path_params: dict, exclude: List[str] = None):
        """Fill valid values for path parameters."""
        exclude = exclude or []
        for param in self.ir["inputs"].get("path", []):
            name = param["name"]
            if name in exclude:
                continue
            schema = param.get("schema", {})
            if schema.get("format") == "uuid":
                path_params[name] = str(uuid.uuid4())
            elif schema.get("type") == "integer":
                path_params[name] = 1
            else:
                path_params[name] = "test_val"

    def _build_valid_payload(self) -> dict:
        """Build a valid payload based on the schema."""
        payload = {}
        body = self.ir["inputs"].get("body", {})
        if body and body.get("schema"):
            for f, s in body["schema"].get("properties", {}).items():
                payload[f] = self._valid_value(s, f)
        return payload

    def _build_path_params(self) -> dict:
        """Build default path parameters."""
        return {p["name"]: None for p in self.ir["inputs"].get("path", [])}

    def _build_valid_headers(self) -> dict:
        """Build valid headers based on the schema."""
        return {
            h["name"]: self._valid_value(h.get("schema", {}), h["name"])
            for h in self.ir["inputs"].get("headers", [])
        }

    def _get_target_field(self, target: str):
        """Extract the target field from the path."""
        parts = target.split(".")
        if "body" in parts:
            idx = parts.index("body")
            if idx + 1 < len(parts):
                return parts[idx + 1].replace("[]", "").replace("*", "")
        return None


def generate_payloads(
    ir: dict, intents: list, base_payload_override: dict = None
) -> list:
    """Functional wrapper for the PayloadGenerator class."""
    generator = PayloadGenerator(ir, base_payload_override)
    return generator.generate(intents)
