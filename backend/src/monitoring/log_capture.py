from typing import TextIO
from backend.src.database.store import _add_log


class StreamCapture(TextIO):
    """Captures stdout and writes to both store and original stream."""

    def __init__(self, job_id: str, original_stdout):
        self.job_id = job_id
        self.original_stdout = original_stdout

    def _determine_log_type(self, text: str) -> str:
        """Determine log type based on message content."""
        text_lower = text.strip().lower()
        
        # Error indicators
        if any(indicator in text_lower for indicator in ['❌', 'error', 'failed', 'exception', 'traceback']):
            return 'error'
        
        # Debug indicators
        if any(indicator in text_lower for indicator in ['debug', '→', 'extracted', 'saved', 'uploaded']):
            return 'debug'
        
        # Info indicators (step progress, completion)
        if any(indicator in text_lower for indicator in ['▶', '✓', '✨', 'step', 'completed', 'generated', 'pipeline']):
            return 'info'
        
        # Default to debug for misc output
        return 'debug'

    def write(self, text: str):
        """Write to log store and original stdout."""
        # Skip empty lines or whitespace-only
        if text.strip():
            log_type = self._determine_log_type(text)
            _add_log(self.job_id, text, log_type)
        self.original_stdout.write(text)

    def flush(self):
        """Flush the original stdout."""
        self.original_stdout.flush()
