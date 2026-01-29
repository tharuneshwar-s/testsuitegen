import logging

from backend.src.exceptions import SpecParsingError
from testsuitegen.src.parsers.openapi_parser.parser import Parser as OpenAPIParser
from testsuitegen.src.parsers.python_parser.parser import PythonParser
from testsuitegen.src.parsers.typescript_parser.parser import TypeScriptParser

logger = logging.getLogger(__name__)


def _parse_spec(spec_content: str, source_type: str = "openapi"):
    """Parse raw spec content into operations and metadata."""
    if not spec_content or not isinstance(spec_content, str):
        raise SpecParsingError("spec_content must be a non-empty string")

    try:
        source_type = (source_type or "openapi").lower()

        if source_type == "python":
            logger.info("Parsing Python spec")
            parser = PythonParser(spec_content)
        elif source_type == "typescript":
            logger.info("Parsing TypeScript spec")
            parser = TypeScriptParser(spec_content)
        elif source_type == "openapi":
            logger.info("Parsing OpenAPI spec")
            parser = OpenAPIParser(spec_content)
        else:
            raise SpecParsingError(
                f"Unsupported source type: {source_type}. Supported types: 'openapi', 'python', 'typescript'"
            )

        parsed_data = parser.parse()

        if not parsed_data:
            raise SpecParsingError(
                f"Parser returned empty result for {source_type} spec"
            )

        logger.info("Spec parsing successful for source_type=%s", source_type)
        return parsed_data
    except SpecParsingError:
        raise
    except Exception as exc:  # noqa: B902
        logger.exception("Failed to parse spec with source_type=%s", source_type)
        raise SpecParsingError(f"Spec parsing failed: {str(exc)}") from exc
