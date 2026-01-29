import tree_sitter_typescript
import tree_sitter_python
from tree_sitter import Language, Parser


def get_parser(language_name: str) -> Parser:
    """
    Returns a configured Tree-Sitter parser for the specified language.
    """
    if language_name == "typescript":
        language = Language(tree_sitter_typescript.language_typescript())
    elif language_name == "python":
        language = Language(tree_sitter_python.language())
    else:
        raise ValueError(f"Unsupported language for tree-sitter: {language_name}")

    parser = Parser(language)
    return parser
