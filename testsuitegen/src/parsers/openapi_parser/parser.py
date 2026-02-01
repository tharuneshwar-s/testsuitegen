import yaml


class Parser:

    __current_spec = None  # for $ref resolution
    HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options", "head"}

    def __init__(self, raw_spec: str) -> None:
        self._spec = yaml.safe_load(raw_spec)
        self.__current_spec = self._spec
        self._operations = []

    def parse(self):

        operation_data = {
            "title": self._spec.get("info", {}).get("title", "API"),
            "version": self._spec.get("info", {}).get("version", "1.0.0"),
        }

        if self._spec.get("info", {}).get("description") != "":
            operation_data["description"] = self._spec.get("info", {}).get(
                "description", ""
            )

        paths = self._spec.get("paths", {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() not in self.HTTP_METHODS:
                    continue

                operation_id = operation.get(
                    "operationId",
                    f"{method}_{path}".replace("/", "_")
                    .replace("{", "")
                    .replace("}", ""),
                )

                self._operations.append(
                    {
                        "id": operation_id,
                        "kind": "http",
                        "method": method.upper(),
                        "path": path,
                        "inputs": self.__parse_inputs(operation),
                        "outputs": self.__parse_outputs(operation),
                        "errors": self.__parse_errors(operation),
                    }
                )

        operation_data["operations"] = self._operations

        return operation_data

    def __parse_inputs(self, operation: dict) -> dict:

        parameters = operation.get("parameters", [])

        path_params = []
        query_params = []
        header_params = []

        for parameter in parameters:
            # Get schema and normalize it to resolve $ref and extract other properties
            raw_schema = parameter.get("schema", {"type": "object"})
            normalized_schema = self.__normalize_schema(raw_schema)

            params = {
                "name": parameter.get("name"),
                "required": parameter.get("required", False),
                "schema": normalized_schema,
            }

            location = parameter.get("in")
            if location == "path":
                path_params.append(params)
            elif location == "query":
                query_params.append(params)
            elif location == "header":
                header_params.append(params)

        body = self.__parse_request_body(operation.get("requestBody"))

        return {
            "path": path_params,
            "query": query_params,
            "headers": header_params,
            "body": body,
        }

    def __parse_outputs(self, operation: dict) -> dict:

        outputs = []

        for status, resp in operation.get("responses", {}).items():

            if not status.isdigit():
                continue

            code = int(status)
            if code >= 500:
                continue

            content = resp.get("content", {})
            json_body = content.get("application/json", {})

            if json_body:
                outputs.append(
                    {
                        "status": code,
                        "description": resp.get("description", ""),
                        "content_type": "application/json",
                        "schema": self.__normalize_schema(json_body.get("schema", {})),
                    }
                )
            else:
                outputs.append(
                    {
                        "status": code,
                        "description": resp.get("description", ""),
                        "content_type": None,
                        "schema": None,
                    }
                )

        return outputs

    def __parse_errors(self, operation: dict) -> list:
        errors = []

        for status, resp in operation.get("responses", {}).items():

            if not status.isdigit():
                continue

            code = int(status)
            if code < 400 or code >= 500:
                continue

            content = resp.get("content", {})
            json_body = content.get("application/json", {})

            if json_body:
                errors.append(
                    {
                        "status": code,
                        "description": resp.get("description", "http_error"),
                        "schema": self.__normalize_schema(json_body.get("schema", {})),
                        "content_type": "application/json",
                    }
                )
            else:
                errors.append(
                    {
                        "status": code,
                        "description": resp.get("description", ""),
                        "schema": None,
                        "content_type": None,
                    }
                )

        return errors

    def __normalize_schema(self, schema: dict) -> dict:

        if not isinstance(schema, dict):
            return {"type": "object", "nullable": False}

        # Keep original reference for preserving constraint keywords
        original_schema = dict(schema)
        schema = dict(schema)

        if "$ref" in schema:
            ref_path = schema["$ref"]
            resolved = (
                self._resolve_ref(ref_path, self.__current_spec)
                if self.__current_spec
                else {}
            )
            # Merge resolved schema with any additional properties in the original schema
            schema.pop("$ref")
            resolved = dict(resolved)
            resolved.update(schema)
            schema = resolved

        # Default nullable
        schema["nullable"] = schema.get("nullable", False)

        # Normalize properties
        if "properties" in schema:
            schema["properties"] = {
                k: self.__normalize_schema(v) for k, v in schema["properties"].items()
            }

        # Normalize array items
        if "items" in schema:
            schema["items"] = self.__normalize_schema(schema["items"])

        # Normalize allOf (merge all schemas into one)
        if "allOf" in schema:
            merged = {}
            for sub_schema in schema["allOf"]:
                normalized_sub = self.__normalize_schema(sub_schema)
                # Merge properties
                if "properties" in normalized_sub:
                    if "properties" not in merged:
                        merged["properties"] = {}
                    merged["properties"].update(normalized_sub["properties"])
                # Merge required fields
                if "required" in normalized_sub:
                    if "required" not in merged:
                        merged["required"] = []
                    merged["required"].extend(normalized_sub["required"])
                # Merge other fields (type, etc.)
                for key, value in normalized_sub.items():
                    if key not in ["properties", "required", "allOf"]:
                        merged[key] = value
            # Remove allOf and replace with merged schema
            schema.pop("allOf")
            schema.update(merged)
            # Deduplicate required fields
            if "required" in schema:
                schema["required"] = list(set(schema["required"]))

        # Normalize anyOf
        if "anyOf" in schema:
            non_null = [s for s in schema["anyOf"] if s.get("type") != "null"]
            has_null = len(non_null) != len(schema["anyOf"])

            if len(non_null) == 1:
                merged = self.__normalize_schema(non_null[0])
                merged["nullable"] = has_null
                return merged

            return {
                "oneOf": [self.__normalize_schema(s) for s in non_null],
                "nullable": has_null,
            }
        # Normalize unions
        if "oneOf" in schema:
            schema["oneOf"] = [self.__normalize_schema(s) for s in schema["oneOf"]]

        # Normalize not (negation schema)
        if "not" in schema:
            schema["not"] = self.__normalize_schema(schema["not"])

        # Normalize discriminator mapping (resolve $ref in mapping values)
        if "discriminator" in schema and isinstance(schema["discriminator"], dict):
            discriminator = schema["discriminator"]
            if "mapping" in discriminator and isinstance(
                discriminator["mapping"], dict
            ):
                resolved_mapping = {}
                for key, ref_path in discriminator["mapping"].items():
                    if isinstance(ref_path, str) and ref_path.startswith("#/"):
                        # Resolve the reference and normalize the schema
                        resolved = (
                            self._resolve_ref(ref_path, self.__current_spec)
                            if self.__current_spec
                            else {}
                        )
                        resolved_mapping[key] = self.__normalize_schema(resolved)
                    else:
                        resolved_mapping[key] = ref_path
                discriminator["mapping"] = resolved_mapping

        # Normalize additionalProperties
        if "additionalProperties" in schema:
            if isinstance(schema["additionalProperties"], dict):
                schema["additionalProperties"] = self.__normalize_schema(
                    schema["additionalProperties"]
                )

        if "oneOf" in schema:
            schema.pop("type", None)
            return schema

        # Default type only for non-unions
        schema.setdefault("type", "object")

        # PRESERVE all OpenAPI constraint keywords
        # These are critical for test intent generation and payload validation
        preserved_keys = [
            # Enums and defaults
            "enum",
            "default",
            "example",
            # String constraints
            "minLength",
            "maxLength",
            "pattern",
            "format",
            # Numeric constraints
            "minimum",
            "maximum",
            "exclusiveMinimum",
            "exclusiveMaximum",
            "multipleOf",
            # Array constraints
            "minItems",
            "maxItems",
            "uniqueItems",
            # Object constraints
            "minProperties",
            "maxProperties",
            "required",
            # Access modifiers
            "readOnly",
            "writeOnly",
            # Metadata
            "deprecated",
            "title",
            "description",
            # Conditional logic (OpenAPI 3.0/3.1)
            "dependencies",
            "dependentRequired",
            "dependentSchemas",
        ]

        # Preserve these keywords from original schema if they exist
        for key in preserved_keys:
            if key in original_schema and key not in schema:
                schema[key] = original_schema[key]

        return schema

    def _resolve_ref(self, ref: str, spec: dict) -> dict:
        """
        Resolve a JSON reference like '#/components/schemas/UserCreate'
        """
        if not ref.startswith("#/"):
            return {}

        parts = ref[2:].split("/")  # Remove '#/' and split
        current = spec

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part, {})
            else:
                return {}

        return current if isinstance(current, dict) else {}

    def __parse_request_body(self, request_body: dict | None) -> dict:
        if not request_body:
            return {}

        content = request_body.get("content", {})

        json_body = content.get("application/json")
        if not json_body:
            return {}

        schema = self.__normalize_schema(json_body.get("schema", {}))

        return {
            "content_type": "application/json",
            "required": request_body.get("required", False),
            "schema": schema,
        }


if __name__ == "__main__":

    import json

    filepath = [
        # "input_parser/openapi_parser/examples/openapi_easy.yaml",
        # "input_parser/openapi_parser/examples/openapi_medium.yaml",
        # "input_parser/openapi_parser/examples/openapi_hard.yaml",
        "test.yaml"
    ]
