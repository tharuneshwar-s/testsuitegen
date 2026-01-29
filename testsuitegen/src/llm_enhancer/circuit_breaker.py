from testsuitegen.src.exceptions.exceptions import LLMError
from testsuitegen.src.config.settings import CIRCUIT_BREAKER_FAILURE_THRESHOLD


class LLMCircuitBreaker:
    """
    Prevents cascading failures by stopping LLM calls after N consecutive failures.
    """

    def __init__(self, failure_threshold: int = None):
        self.failure_threshold = failure_threshold or CIRCUIT_BREAKER_FAILURE_THRESHOLD
        self.consecutive_failures = 0
        self.is_open = False  # Circuit is OPEN (blocking) or CLOSED (allowing)

    def record_success(self):
        self.consecutive_failures = 0
        self.is_open = False
        print("Circuit Breaker: Success recorded. Circuit is CLOSED.")

    def record_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.is_open = True
            print(
                f"Circuit Breaker TRIPPED: {self.consecutive_failures} consecutive failures. "
                "Stopping LLM calls for this session."
            )
            raise LLMError(
                f"Circuit Breaker Tripped: LLM failed {self.consecutive_failures} times consecutively."
            )

    def check_state(self):
        if self.is_open:
            raise LLMError(
                "Circuit Breaker is OPEN. Blocking LLM call to save resources."
            )


circuit_breaker = LLMCircuitBreaker()
