from http import HTTPStatus


class BackendError(Exception):
    """Base exception with HTTP status code."""

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    message: str = "Internal server error"

    def __init__(self, message: str | None = None, status_code: int | None = None):
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class SpecDecodeError(BackendError):
    """Raised when spec data cannot be decoded."""

    status_code = HTTPStatus.BAD_REQUEST
    message = "Unable to decode spec data"


class SpecParsingError(BackendError):
    """Raised when specification parsing fails."""

    status_code = HTTPStatus.BAD_REQUEST
    message = "Failed to parse specification"


class IRBuildError(BackendError):
    """Raised when IR generation fails."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = "Failed to build intermediate representation"


class IntentGenerationError(BackendError):
    """Raised when intent generation fails."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = "Failed to generate intents"


class PayloadGenerationError(BackendError):
    """Raised when payload generation fails."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = "Failed to generate payloads"


class JobCreationError(BackendError):
    """Raised when job creation fails."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = "Failed to create job"


class JobNotFoundError(BackendError):
    """Raised when a job is not found."""

    status_code = HTTPStatus.NOT_FOUND
    message = "Job not found"
