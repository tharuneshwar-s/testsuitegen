# llm_enhancer/test_enhancer/validator.py

import ast


def validate_no_logic_change(original: str, enhanced: str):
    """Validate that LLM only made safe enhancements, not harmful logic changes."""

    # Check for obviously harmful changes by comparing key patterns
    harmful_patterns = [
        r"expected_status.*[^=]=[^=]",  # API tests: expected statuses
        r"expected_result.*[^=]=[^=]",  # Unit tests: expected return values
        r"expected_value.*[^=]=[^=]",  # Unit tests: expected values
        r"assert.*!=",  # Changing assertions to not-equal
        r"assert.*status_code.*[^2]..",  # Changing status code assertions
        r"@pytest.mark.parametrize.*\[.*\]",  # Modifying parametrize decorators
        r'id=.*[^"]',  # Changing test IDs
    ]

    for pattern in harmful_patterns:
        orig_count = len([line for line in original.split("\n") if pattern in line])
        enhanced_count = len([line for line in enhanced.split("\n") if pattern in line])

        if orig_count != enhanced_count:
            raise RuntimeError(
                f"LLM modified test logic (pattern: {pattern}) — enhancement rejected"
            )

    # Validate test_data_setup fixture structure for API tests
    # if "def test_data_setup" in original:
    #     # Check that the fixture still yields a dict with "created_resources" key
    #     if 'yield {"created_resources": created_resources}' not in enhanced:
    #         raise RuntimeError(
    #             "LLM modified test_data_setup fixture structure — enhancement rejected. "
    #             "Fixture must yield {'created_resources': created_resources}"
    #         )

    # Allow enhancements that add fixtures, comments, or formatting
    return True
