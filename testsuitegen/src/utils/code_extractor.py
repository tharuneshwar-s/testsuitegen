import ast
import logging
from testsuitegen.src.utils.tree_sitter_loader import get_parser

logger = logging.getLogger(__name__)


def extract_relevant_context(
    source_code: str, target_function_name: str, language: str = "python"
) -> str:
    """
    Extracts the target function code and all potential type definitions (Classes, Enums, Interfaces)
    from the source code to provide a focused context for the LLM.

    Args:
        source_code: Full source code.
        target_function_name: Name of the function to extract.
        language: "python" or "typescript".

    Returns:
        A string containing relevant definitions and the target function.
        Returns original source_code if extraction fails or function is not found.
    """
    if language == "python":
        return _extract_python_context(source_code, target_function_name)
    elif language == "typescript":
        return _extract_typescript_context(source_code, target_function_name)
    else:
        logger.warning(
            f"Unsupported language {language} for context extraction. Returning full source."
        )
        return source_code


def _extract_python_context(source_code: str, target_function_name: str) -> str:
    try:
        tree = ast.parse(source_code)
        relevant_nodes = []
        target_found = False
        source_lines = source_code.splitlines(keepends=True)

        for node in tree.body:
            # 1. Keep all Class Definitions (potential types/enums)
            if isinstance(node, ast.ClassDef):
                relevant_nodes.append(node)
            # 2. Keep the Target Function
            elif (
                isinstance(node, ast.FunctionDef) and node.name == target_function_name
            ):
                relevant_nodes.append(node)
                target_found = True
            # 3. Keep Assignments (potential Type Aliases or Constants)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                relevant_nodes.append(node)
            # 4. Keep Imports
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                relevant_nodes.append(node)

        if not target_found:
            logger.warning(
                f"Target function '{target_function_name}' not found in Python source. Returning full source."
            )
            return source_code

        extracted_code = []
        for node in relevant_nodes:
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                start = node.lineno - 1
                end = node.end_lineno
                extracted_code.append("".join(source_lines[start:end]))

        return "\n\n".join(extracted_code)

    except Exception as e:
        logger.error(f"Error parsing Python source: {e}")
        return source_code


def _extract_typescript_context(source_code: str, target_function_name: str) -> str:
    try:
        parser = get_parser("typescript")
        tree = parser.parse(bytes(source_code, "utf8"))
        root = tree.root_node

        def node_text(node):
            return source_code[node.start_byte : node.end_byte]

        nodes_to_keep = []
        target_found = False

        # Top-level pass: pick imports, types, classes, enums, top-level functions, exports
        for child in root.children:
            t = child.type

            # Keep imports, interfaces, type aliases, classes, enums
            if t in (
                "import_statement",
                "interface_declaration",
                "type_alias_declaration",
                "class_declaration",
                "enum_declaration",
            ):
                nodes_to_keep.append(child)

            # Top-level function
            elif t == "function_declaration":
                # find identifier child
                id_node = next(
                    (c for c in child.children if c.type == "identifier"), None
                )
                if id_node and node_text(id_node) == target_function_name:
                    nodes_to_keep.append(child)
                    target_found = True

            # exported declarations: could be "export_statement" with a declaration child
            elif t == "export_statement":
                # keep exported types/classes/etc for context
                for named in child.named_children:
                    if named.type in (
                        "interface_declaration",
                        "class_declaration",
                        "enum_declaration",
                        "type_alias_declaration",
                        "function_declaration",
                    ):
                        # if it's a function, check name; otherwise keep it for context
                        if named.type == "function_declaration":
                            id_node = next(
                                (c for c in named.children if c.type == "identifier"),
                                None,
                            )
                            if id_node and node_text(id_node) == target_function_name:
                                nodes_to_keep.append(
                                    child
                                )  # include the whole export_statement
                                target_found = True
                            else:
                                # keep other exported functions/types for context
                                nodes_to_keep.append(named)
                        else:
                            nodes_to_keep.append(named)

        # Second pass: search for the function as a method inside classes; if found, include the class
        for child in root.children:
            if child.type == "class_declaration":
                # class body typically is a child named 'class_body' or has method_definition nodes inside
                for member in child.named_children:
                    # method definition types may vary between grammars: 'method_definition', 'public_field_definition', etc.
                    if member.type in (
                        "method_definition",
                        "function",
                        "method_signature",
                    ):
                        # method name can be 'property_identifier' or 'identifier' or similar
                        name_node = next(
                            (
                                c
                                for c in member.children
                                if c.type in ("property_identifier", "identifier")
                            ),
                            None,
                        )
                        if name_node and node_text(name_node) == target_function_name:
                            nodes_to_keep.append(child)
                            target_found = True
                            break
                if target_found:
                    # no need to search other classes once found (optional)
                    pass

        if not target_found:
            logger.warning(
                f"Target function '{target_function_name}' not found in TS source. Returning full source."
            )
            return source_code

        # Deduplicate by (start_byte, end_byte) and sort by position
        seen_ranges = set()
        unique_nodes = []
        for n in nodes_to_keep:
            key = (n.start_byte, n.end_byte)
            if key not in seen_ranges:
                seen_ranges.add(key)
                unique_nodes.append(n)

        unique_nodes.sort(key=lambda n: n.start_byte)

        # Extract text parts
        extracted_parts = [node_text(n) for n in unique_nodes]

        return "\n\n".join(extracted_parts)

    except Exception as e:
        logger.error(f"Error parsing TypeScript source: {e}")
        return source_code
