"""Pre-parsing validation logic for input files."""

import json
import ast
from pathlib import Path
from typing import Union

from testsuitegen.src.exceptions.exceptions import InvalidSpecError, FileError


def validate_input_spec(file_path: Union[str, Path]):
    """
    Performs structural validation on OpenAPI or Python files.

    Args:
        file_path: Path to the specification file.

    Raises:
        FileError: If file doesn't exist or extension is wrong.
        InvalidSpecError: If the file structure is malformed.
    """
    path = Path(file_path)

    # 1. File Existence & Type Check
    if not path.exists():
        raise FileError(
            f"File not found: {file_path}", "Please check the path and try again."
        )

    suffix = path.suffix.lower()
    if suffix not in [".json", ".yaml", ".yml", ".py"]:
        raise FileError(
            f"Unsupported file format: {suffix}",
            "Supported formats are: .json, .yaml, .yml, .py",
        )

    # 2. Read content safely
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        raise FileError(f"Could not read file: {file_path}", str(e))

    # 3. Validate Structure based on type
    if suffix == ".py":
        _validate_python_structure(path, content)
    else:
        _validate_openapi_structure(path, content, suffix)


def _validate_openapi_structure(path: Path, content: str, suffix: str):
    """Validates OpenAPI YAML/JSON structure."""
    try:
        if suffix == ".json":
            data = json.loads(content)
        else:
            # Basic YAML import (assuming pyyaml is installed)
            import yaml

            data = yaml.safe_load(content)
    except json.JSONDecodeError as e:
        raise InvalidSpecError(
            f"Invalid JSON syntax in {path.name}",
            f"Line {e.lineno}, Column {e.colno}: {e.msg}",
        )
    except Exception as e:
        # Handle YAML errors or other parsing issues
        if "yaml" in str(type(e).__module__):
            # YAML error
            problem_mark = e.problem_mark if hasattr(e, "problem_mark") else None
            location = (
                f"Line {problem_mark.line}" if problem_mark else "Unknown location"
            )
            problem_desc = str(e.problem) if hasattr(e, "problem") else "Syntax error"
            raise InvalidSpecError(
                f"Invalid YAML syntax in {path.name}", f"{location}: {problem_desc}"
            )
        raise InvalidSpecError(f"Failed to parse OpenAPI file", str(e))

    # Structural Checks (Deep enough to catch basic issues, fast enough to run instantly)
    if not isinstance(data, dict):
        raise InvalidSpecError(
            "Root element must be an object (dictionary)",
            "The file provided is likely a list or raw value.",
        )

    # Check for OpenAPI version (v3.x or v2.0)
    if "openapi" not in data and "swagger" not in data:
        raise InvalidSpecError(
            "Missing 'openapi' or 'swagger' key at root level",
            "This file does not appear to be a valid OpenAPI specification.",
        )

    # Check for paths
    if "paths" not in data:
        raise InvalidSpecError(
            "Missing 'paths' key at root level",
            "An OpenAPI spec must define paths/endpoints to generate tests.",
        )


def _validate_python_structure(path: Path, content: str):
    """Validates Python syntax using AST."""
    try:
        ast.parse(content, filename=str(path))
    except SyntaxError as e:
        raise InvalidSpecError(
            f"Python syntax error in {path.name}", f"Line {e.lineno}: {e.msg}"
        )
