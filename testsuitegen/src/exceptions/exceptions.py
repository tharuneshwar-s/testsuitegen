"""Custom Exception Classes for TestSuiteGen."""


class TestGenError(Exception):
    """Base class for all testsuitegen exceptions."""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        msg = f"Error: {self.message}"
        if self.details:
            msg += f"\n   Details: {self.details}"
        return msg


class FileError(TestGenError):
    """Raised when the input file cannot be accessed or is invalid."""

    pass


class InvalidSpecError(TestGenError):
    """Raised when the specification (OpenAPI/Python) is structurally invalid."""

    pass


class ValidationError(TestGenError):
    """Raised when the Intermediate Representation (IR) fails validation."""

    pass


class LLMError(TestGenError):
    """Raised when LLM operations fail."""

    pass


class LLMFatalError(LLMError):
    """Raised when an LLM error is non-retryable (e.g., policy or configuration).

    Use this to signal that retries will not help and enhancement should fallback
    immediately to non-LLM behavior.
    """

    pass


class ParsingError(TestGenError):
    """Raised when parsing operations fail."""

    pass
