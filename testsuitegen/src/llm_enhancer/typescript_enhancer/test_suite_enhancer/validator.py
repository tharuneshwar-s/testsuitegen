def validate_no_logic_change(original: str, enhanced: str):
    """Validate that LLM only made safe enhancements, not harmful logic changes."""

    # TypeScript specific harmful patterns
    harmful_patterns = [
        r"expectedStatus.*:",  # Changed expected status in JSON object
        r"expectedResult.*:",  # Changed expected result
        r"expect\(.*\.toBe\(",  # Changed assertions
        r"describe\(",  # Should not remove/change describe blocks essentially
        r"const BASE_URL",  # Constants
        r"const ENDPOINT",
        r"const METHOD",
    ]

    for pattern in harmful_patterns:
        orig_count = len([line for line in original.split("\n") if pattern in line])
        enhanced_count = len([line for line in enhanced.split("\n") if pattern in line])

        if orig_count != enhanced_count:
            # For Jest/TS, exact line validation is tricky due to formatting changes (e.g. object keys).
            # But critical logic like 'expectedStatus: 200' should appear same number of times.
            raise RuntimeError(
                f"LLM modified test logic (pattern: {pattern}) — enhancement rejected"
            )

    # Allow enhancements that add fixtures, comments, or formatting
    return True
