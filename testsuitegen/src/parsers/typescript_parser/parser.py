"""
TypeScript Source Code Parser using Tree-Sitter

Parses TypeScript source code (.ts files) into TestSuiteGen IR format.
Uses tree-sitter for robust AST parsing, extracting signatures and type info.
"""

import logging
from typing import Optional
from ...utils.tree_sitter_loader import get_parser

logger = logging.getLogger(__name__)


class TypeScriptParser:
    """
    Tree-Sitter Parser for TypeScript Source Code.
    """

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.parser = get_parser("typescript")

    def parse(self) -> dict:
        """Parse TypeScript source code and return IR-compatible operations."""
        tree = self.parser.parse(bytes(self.source_code, "utf8"))
        root_node = tree.root_node

        operations = []

        # Traverse for function definitions
        # We look for: function_declaration, arrow_function, method_definition
        for node in self._traverse_tree(root_node):
            if node.type in ["function_declaration", "method_definition"]:
                op = self._parse_node(node)
                if op:
                    operations.append(op)
            elif node.type == "lexical_declaration":
                # Handle const foo = () => {}
                for child in node.children:
                    if child.type == "variable_declarator":
                        name_node = child.child_by_field_name("name")
                        value_node = child.child_by_field_name("value")
                        if value_node and value_node.type == "arrow_function":
                            op = self._parse_arrow_function(name_node, value_node)
                            if op:
                                operations.append(op)

        return {"operations": operations}

    def _traverse_tree(self, node):
        """Pre-order traversal."""
        yield node
        for child in node.children:
            yield from self._traverse_tree(child)

    def _get_text(self, node) -> str:
        """Get source text for a node."""
        if not node:
            return ""
        return self.source_code[node.start_byte : node.end_byte]

    def _parse_node(self, node) -> Optional[dict]:
        """Parse standard function entries."""
        name_node = node.child_by_field_name("name")
        if not name_node:
            return None

        func_name = self._get_text(name_node)

        # Check async
        is_async = False
        for child in node.children:
            if child.type == "async":
                is_async = True
                break

        # Parameters
        params_node = node.child_by_field_name("parameters")
        properties, required = self._parse_parameters(params_node)

        # Return Type
        return_type_node = node.child_by_field_name(
            "return_type"
        )  # This is type_annotation
        # In tree-sitter typescript:
        # return_type field exists for call_signature, but sometimes it captures `: Type`
        # actually node.child_by_field_name("type") might match the return type annotation

        return_schema = {}
        if node.child_by_field_name("type"):
            # The : Type part
            return_annotation = node.child_by_field_name("type")
            # It wraps the actual type
            if return_annotation.children:
                # Usually [0] is :, [1] is the type
                real_type = return_annotation.children[-1]
                return_schema = self._node_to_schema(real_type)
        elif return_type_node:
            # Some nodes use return_type field
            real_type = (
                return_type_node.children[-1]
                if return_type_node.children
                else return_type_node
            )
            return_schema = self._node_to_schema(real_type)

        # Get docstring (comments before the node)
        description = self._get_docstring(node)

        # Build Body Schema
        body_schema = {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

        return {
            "id": func_name,
            "kind": "typescript_function",
            "async": is_async,
            "description": description or f"TypeScript function: {func_name}",
            "metadata": {},
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
            "errors": [],
        }

    def _parse_arrow_function(self, name_node, arrow_node) -> dict:
        """Parse arrow functions explicitly."""
        func_name = self._get_text(name_node)

        is_async = False
        # Check children for 'async' keyword
        for child in arrow_node.children:
            if child.type == "async":
                is_async = True

        params_node = arrow_node.child_by_field_name("parameters")
        properties, required = self._parse_parameters(params_node)

        return_schema = {}
        # return_type field
        rt_node = arrow_node.child_by_field_name("return_type")
        if rt_node:
            real_type = rt_node.children[-1]
            return_schema = self._node_to_schema(real_type)

        # Docstring - usually attached to the variable declaration statement
        # We need to look up parent -> parent (lexical decl) -> prev sibling
        parent = arrow_node.parent  # variable_declarator
        grandparent = parent.parent  # lexical_declaration
        description = self._get_docstring(grandparent)

        body_schema = {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

        return {
            "id": func_name,
            "kind": "typescript_function",
            "async": is_async,
            "description": description or f"TypeScript arrow function: {func_name}",
            "metadata": {},
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
            "errors": [],
        }

    def _parse_parameters(self, params_node):
        """Returns (properties, required_list)"""
        properties = {}
        required = []

        if not params_node:
            return properties, required

        for child in params_node.children:
            if child.type in ["required_parameter", "optional_parameter"]:
                name_node = child.child_by_field_name(
                    "pattern"
                )  # 'pattern' holds identifier
                if not name_node:
                    continue

                param_name = self._get_text(name_node)

                # Check optional
                is_optional = child.type == "optional_parameter"

                # Type annotation
                type_node = child.child_by_field_name("type")
                schema = {}
                if type_node:
                    # type_node is usually type_annotation -> children[1] is usage
                    if type_node.children:
                        real_type = type_node.children[-1]
                        schema = self._node_to_schema(real_type)

                properties[param_name] = schema
                if not is_optional:
                    required.append(param_name)

        return properties, required

    def _node_to_schema(self, type_node) -> dict:
        """Map TS type nodes to JSON schema"""
        if not type_node:
            return {}

        kind = type_node.type
        text = self._get_text(type_node)

        if kind == "predefined_type":
            if text == "string":
                return {"type": "string"}
            if text == "number":
                return {"type": "number"}
            if text == "boolean":
                return {"type": "boolean"}
            if text == "any":
                return {}
            if text == "void":
                return {"type": "null"}

        if kind == "type_reference":
            # e.g. Promise<T> or Array<T> or User
            name_node = type_node.child_by_field_name("name")
            name = self._get_text(name_node)

            if name == "Array":
                args = type_node.child_by_field_name("type_arguments")
                if args and args.children:
                    # filtering checking children for type nodes
                    # standard struct: <, type, >
                    sub_types = [
                        c for c in args.children if c.type not in ["<", ">", ","]
                    ]
                    if sub_types:
                        return {
                            "type": "array",
                            "items": self._node_to_schema(sub_types[0]),
                        }

            if name == "Promise":
                args = type_node.child_by_field_name("type_arguments")
                if args and args.children:
                    sub_types = [
                        c for c in args.children if c.type not in ["<", ">", ","]
                    ]
                    if sub_types:
                        return self._node_to_schema(sub_types[0])

            # Fallback for named refs
            return {"type": "object", "description": f"Ref: {name}"}

        if kind == "array_type":
            # T[]
            elem = type_node.children[0]
            return {"type": "array", "items": self._node_to_schema(elem)}

        if kind == "union_type":
            # A | B
            # children: type, |, type
            options = []
            for child in type_node.children:
                if child.type == "|":
                    continue
                options.append(self._node_to_schema(child))

            # Filter nulls
            non_null = [o for o in options if o.get("type") != "null"]
            has_null = len(non_null) < len(options)

            if len(non_null) == 1:
                s = non_null[0]
                if has_null:
                    s["nullable"] = True
                return s

            s = {"oneOf": non_null}
            if has_null:
                s["nullable"] = True
            return s

        if kind == "object_type":
            # { name: string }
            props = {}
            # Iterate members
            for child in type_node.children:
                if child.type in ["property_signature", "property_signature"]:
                    pname = self._get_text(child.child_by_field_name("name"))
                    ptype = child.child_by_field_name("type")
                    if ptype and ptype.children:
                        pschema = self._node_to_schema(ptype.children[-1])
                        props[pname] = pschema
            return {"type": "object", "properties": props}

        if kind == "tuple_type":
            # [string, number]
            items = []
            for child in type_node.children:
                if child.type in ["[", "]", ","]:
                    continue
                items.append(self._node_to_schema(child))
            return {
                "type": "array",
                "prefixItems": items,
                "minItems": len(items),
                "maxItems": len(items),
            }

        if kind == "literal_type":
            # "foo" or 123
            text = self._get_text(type_node)
            # Strip quotes
            if text.startswith("'") or text.startswith('"'):
                return {"const": text[1:-1]}
            # Try number
            try:
                if "." in text:
                    return {"const": float(text)}
                return {"const": int(text)}
            except:
                return {"const": text}

        return {"type": "object", "description": f"TS Type: {kind}"}

    def _get_docstring(self, node) -> str:
        """Extract comments immediately preceding the node."""
        if not node:
            return ""

        # Look at previous siblings
        # Tree-sitter includes comments as nodes if enabled, or we scan raw source.
        # But commonly they are 'comment' nodes in the tree.

        # We search backward from node
        prev = node.prev_sibling
        comments = []
        while prev:
            if prev.type == "comment":
                text = self._get_text(prev)
                # Clean up // or /* */
                cleaned = text.strip()
                if cleaned.startswith("//"):
                    cleaned = cleaned[2:].strip()
                elif cleaned.startswith("/*"):
                    cleaned = cleaned[2:-2].strip()
                comments.insert(0, cleaned)
                prev = prev.prev_sibling
            elif prev.type in ["export", "async"]:
                # Skip modifiers to find comments before them
                prev = prev.prev_sibling
            elif str(prev.type).strip() == "":
                # Whitespace/Text nodes?
                prev = prev.prev_sibling
            else:
                break

        return "\n".join(comments)


if __name__ == "__main__":
    import json

    code = """
    /**
     * Greets the user.
     * @param name Name of user
     */
    export function greet(name: string): string { 
        return "Hi" 
    }
    
    // Process items
    const process = (items: number[]): void => {}
    """
