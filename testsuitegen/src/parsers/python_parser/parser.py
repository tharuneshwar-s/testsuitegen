import ast
import logging
import sys
import inspect
import textwrap

# Configure logging
logger = logging.getLogger(__name__)


class PythonParser:
    """
    Deterministic Parser for Python Source Code using AST.
    Converts Python source directly to TestSuiteGen IR.
    """

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.type_registry = {}  # Maps type name -> parsed type definition
        try:
            self.tree = ast.parse(source_code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax: {e}")

    def parse(self) -> dict:
        operations = []
        types = []

        # First pass: Parse all classes to build type registry
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                try:
                    type_def = self._parse_class(node)
                    if type_def:
                        types.append(type_def)
                        # Register the type for lookup during function parsing
                        self.type_registry[type_def["id"]] = type_def
                except Exception as e:
                    logger.warning(f"Skipping class '{node.name}': {e}")
                    continue

        # Second pass: Parse functions (can now resolve custom types via registry)
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    op = self._parse_function(node)
                    operations.append(op)
                except ValueError as e:
                    logger.warning(f"Skipping function '{node.name}': {e}")
                    continue

        return {"operations": operations, "types": types}

    def _parse_class(self, class_node) -> dict:
        """
        Parses a ClassDef into a Type Definition (Enum or Model).
        """
        class_name = class_node.name
        docstring = ast.get_docstring(class_node) or ""

        # Check Bases for Enum
        is_enum = any(
            self._get_name_from_node(base) == "Enum" for base in class_node.bases
        )

        # Check Decorators for Dataclasses
        decorators = []
        is_dataclass = False
        for dec in class_node.decorator_list:
            dec_name = ""
            if isinstance(dec, ast.Name):
                dec_name = dec.id
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                dec_name = dec.func.id

            if dec_name:
                decorators.append(f"@{dec_name}")
                if "dataclass" in dec_name:
                    is_dataclass = True

        if is_enum:
            values = []
            for item in class_node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            # Enum member: NAME = VALUE
                            member_name = target.id
                            # Try to get simple value
                            member_value = None
                            if isinstance(item.value, ast.Constant):
                                member_value = item.value.value
                            values.append({"name": member_name, "value": member_value})

            return {
                "id": class_name,
                "kind": "enum",
                "description": docstring,
                "values": values,
            }

        # Otherwise, treat as Model (Dataclass or Pydantic or TypedDict)
        properties = {}
        required = []

        for item in class_node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Field: name: type = default
                field_name = item.target.id
                field_schema = self._node_to_schema(item.annotation)
                properties[field_name] = field_schema

                # Check for default value
                if item.value is None:
                    # No default value -> required
                    # Check if type is Optional/Nullable
                    if not field_schema.get("nullable", False):
                        required.append(field_name)

        return {
            "id": class_name,
            "kind": "model",
            "description": docstring,
            "metadata": {"decorators": decorators, "is_dataclass": is_dataclass},
            "schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def _parse_function(self, func_node) -> dict:
        """
        Converts a single function AST node into an IR Operation.
        """
        function_name = func_node.name
        docstring = ast.get_docstring(func_node) or ""

        is_async = isinstance(func_node, ast.AsyncFunctionDef)

        # Extract Decorators
        decorators = []
        for dec in func_node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(f"@{dec.id}")
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                decorators.append(f"@{dec.func.id}")

        # Validate Strict Rules
        if func_node.args.vararg or func_node.args.kwarg:
            raise ValueError("Functions with *args or **kwargs are not supported.")

        # 2. Parse Arguments -> JSON Schema Properties
        properties = {}
        required = []

        # Calculate where defaults start
        num_args = len(func_node.args.args)
        num_defaults = len(func_node.args.defaults)
        first_default_index = num_args - num_defaults

        for i, arg in enumerate(func_node.args.args):
            if arg.arg in ["self", "cls"]:
                continue

            # Strict Mode: Require Type Hints
            if not arg.annotation:
                raise ValueError(f"Argument '{arg.arg}' is missing a type hint.")

            # --- CORE CHANGE: Direct AST to Schema Mapping ---
            schema = self._node_to_schema(arg.annotation)
            properties[arg.arg] = schema

            # Handle Optional/Nullable logic for 'required' list
            is_optional_type = schema.get("nullable", False)
            has_default = i >= first_default_index

            if not has_default and not is_optional_type:
                required.append(arg.arg)

        body_schema = {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

        # Parse Return Type
        return_schema = (
            self._node_to_schema(func_node.returns) if func_node.returns else {}
        )

        # 6. Construct IR
        return {
            "id": function_name,
            "kind": "function",
            "async": is_async,
            "description": docstring,
            "metadata": {"decorators": decorators},
            "inputs": {
                "path": [],
                "query": [],
                "headers": [],
                "body": {
                    "content_type": "application/json",
                    "required": True,
                    "schema": body_schema,
                },
            },
            "outputs": [
                {
                    "status": 200,
                    "content_type": "application/json",
                    "schema": return_schema,
                }
            ],
            "errors": [],  # Will be populated by LLM in Step 2
        }

    def _node_to_schema(self, node) -> dict:
        """
        Recursively converts an AST node into a JSON Schema dictionary.
        Handles Union, Optional, List, Dict, Tuple, Set, Literal, and more.
        """
        if node is None:
            return {}

        # 1. Basic Names (int, str, MyClass)
        if isinstance(node, ast.Name):
            return self._resolve_name(node.id)

        # 2. Attributes (typing.List, pydantic.BaseModel)
        if isinstance(node, ast.Attribute):
            return self._resolve_name(node.attr)

        # 3. Constants (Literal values)
        if isinstance(node, ast.Constant):
            return {"const": node.value}

        # 4. Subscripts (List[int], Union[A, B], Optional[T])
        if isinstance(node, ast.Subscript):
            container_name = self._get_name_from_node(node.value)

            # Unbox the slice
            if sys.version_info < (3, 9) and isinstance(node.slice, ast.Index):
                slice_node = node.slice.value
            else:
                slice_node = node.slice

            # --- List / Set / Iterable ---
            if container_name in [
                "List",
                "list",
                "Set",
                "set",
                "FrozenSet",
                "Iterable",
                "Sequence",
                "Deque",
            ]:
                item_schema = self._node_to_schema(slice_node)
                return {"type": "array", "items": item_schema}

            # --- Tuple ---
            if container_name in ["Tuple", "tuple"]:
                if isinstance(slice_node, ast.Tuple):
                    items_schemas = [
                        self._node_to_schema(elt) for elt in slice_node.elts
                    ]
                    return {
                        "type": "array",
                        "prefixItems": items_schemas,
                        "minItems": len(items_schemas),
                        "maxItems": len(items_schemas),
                    }
                else:
                    # Tuple[int] matches Tuple[int, ...] in some versions, or single item tuple
                    return {"type": "array", "items": self._node_to_schema(slice_node)}

            # --- Dict / Mapping ---
            if container_name in ["Dict", "dict", "Mapping", "MutableMapping"]:
                if isinstance(slice_node, ast.Tuple) and len(slice_node.elts) >= 2:
                    value_schema = self._node_to_schema(slice_node.elts[1])
                    return {"type": "object", "additionalProperties": value_schema}
                return {"type": "object", "additionalProperties": True}

            # --- Optional ---
            if container_name == "Optional":
                schema = self._node_to_schema(slice_node)
                schema["nullable"] = True
                return schema

            # --- Union ---
            if container_name == "Union":
                return self._handle_union_node(slice_node)

            # --- Literal ---
            if container_name == "Literal":
                return self._handle_literal_node(slice_node)

            # --- Type or ClassVar ---
            if container_name in ["Type", "ClassVar"]:
                return self._node_to_schema(slice_node)

            # --- Callable ---
            if container_name in ["Callable"]:
                return {"type": "object", "description": "Callable/Function"}

        # 5. Binary Operations (Python 3.10+ Union: int | str)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return self._handle_binop_union(node)

        return {"type": "object", "description": f"Complex/Unknown Type"}

    def _handle_literal_node(self, slice_node) -> dict:
        """Handles Literal['a', 'b', 1] -> enum schema."""
        values = []
        if isinstance(slice_node, ast.Tuple):
            for elt in slice_node.elts:
                if isinstance(elt, ast.Constant):
                    values.append(elt.value)
        elif isinstance(slice_node, ast.Constant):
            values.append(slice_node.value)

        if not values:
            return {}

        # Determine strict type if all match
        types = set(type(v) for v in values)
        schema_type = "string"
        if types == {int}:
            schema_type = "integer"
        elif types == {float}:
            schema_type = "number"
        elif types == {bool}:
            schema_type = "boolean"
        # Mixed types -> no 'type' field, just enum

        if len(types) == 1:
            return {"type": schema_type, "enum": values}
        return {"enum": values}

    def _resolve_name(self, name: str) -> dict:
        """Maps a type name to a schema."""

        name_lower = name.lower()
        if name_lower in ["int", "integer"]:
            return {"type": "integer"}
        if name_lower in ["float", "number"]:
            return {"type": "number"}
        if name_lower in ["str", "string"]:
            return {"type": "string"}
        if name_lower in ["bool", "boolean"]:
            return {"type": "boolean"}
        if name_lower == "none":
            return {"type": "null"}
        if name_lower in ["dict", "object"]:
            return {"type": "object"}
        if name_lower in ["list", "array"]:
            return {"type": "array"}
        if name_lower == "any":
            return {}

        # Check type registry for custom types (Enums, Models)
        if name in self.type_registry:
            type_def = self.type_registry[name]
            kind = type_def.get("kind", "model")

            if kind == "enum":
                # Return enum schema with string type and enum values
                values = type_def.get("values", [])
                enum_values = [v.get("value") or v.get("name") for v in values]
                return {
                    "type": "string",
                    "enum": enum_values,
                    "x-enum-type": name,  # Reference to original enum
                }
            else:
                # For models, return a $ref
                return {"$ref": f"#/types/{name}"}

        # Fallback for unknown types (likely imported from external modules)
        return {"type": "object", "description": f"Complex type: {name}"}

    def _handle_union_node(self, slice_node) -> dict:
        """Handles Union[A, B] content."""
        options = []

        # If multiple args, it's a Tuple
        if isinstance(slice_node, ast.Tuple):
            for elt in slice_node.elts:
                options.append(self._node_to_schema(elt))
        else:
            # Single arg Union (rare but valid)
            options.append(self._node_to_schema(slice_node))

        return self._finalize_union(options)

    def _handle_binop_union(self, node: ast.BinOp) -> dict:
        """Handles A | B | C recursively."""
        options = []

        def collect_options(n):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr):
                collect_options(n.left)
                collect_options(n.right)
            else:
                options.append(self._node_to_schema(n))

        collect_options(node)
        return self._finalize_union(options)

    def _finalize_union(self, options: list) -> dict:
        """
        Cleans up a list of schemas into a oneOf or nullable schema.
        e.g. [int, None] -> {type: integer, nullable: true}
        """
        non_null_options = [o for o in options if o.get("type") != "null"]
        has_null = len(non_null_options) < len(options)

        if len(non_null_options) == 1:
            schema = non_null_options[0]
            if has_null:
                schema["nullable"] = True
            return schema

        schema = {"oneOf": non_null_options}
        if has_null:
            schema["nullable"] = True
        return schema

    def _get_name_from_node(self, node) -> str:
        """Helper to get string name from Name or Attribute node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""
