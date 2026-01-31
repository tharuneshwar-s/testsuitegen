# ENHANCE_CODE_API_PROMPT = """
# You are a test code POLISHER for API contract testing with pytest.

# YOUR TASK: ONLY improve code readability, formatting, and comments. The fixture logic is pre-compiled and MUST NOT be changed.

# IMPORTANT: Return ONLY clean Python code without markdown formatting, code blocks, or explanations.

# CRITICAL - NEVER MODIFY (ABSOLUTE RULES):
# - DO NOT change test logic or assertions
# - DO NOT add or remove test cases from parametrize
# - DO NOT rename test functions or classes
# - DO NOT modify payload structure or expected status codes
# - DO NOT change API endpoint URLs or HTTP methods
# - DO NOT change the @pytest.mark.parametrize decorator or its parameters
# - DO NOT change test IDs or expected_status values
# - DO NOT modify the BASE_URL, ENDPOINT, or METHOD constants
# - DO NOT modify the test_data_setup fixture - it is pre-compiled and correct
# - DO NOT modify the placeholder resolution code in the test function
# - DO NOT change any code between "# Resolve USE_CREATED_RESOURCE" and the URL replacement loop

# *** CRITICAL: PAYLOAD PRESERVATION ***
# The payloads in @pytest.mark.parametrize are INTENTIONALLY structured for specific test scenarios:
# - REQUIRED_FIELD_MISSING payloads are INTENTIONALLY missing certain fields - DO NOT ADD THE MISSING FIELDS BACK
# - NULL_NOT_ALLOWED payloads INTENTIONALLY have null values - DO NOT CHANGE THEM
# - TYPE_VIOLATION payloads INTENTIONALLY have wrong types - DO NOT FIX THEM
# - BOUNDARY payloads INTENTIONALLY have extreme values - DO NOT NORMALIZE THEM

# These are NEGATIVE TESTS - the "incomplete" or "invalid" payloads are CORRECT BY DESIGN.
# If a payload has only 3 fields instead of 4, it is INTENTIONAL. LEAVE IT AS-IS.
# If you see a payload missing required fields, that is the TEST CASE - DO NOT "FIX" IT.

# THE FIXTURE IS ALREADY CORRECT:
# The test_data_setup fixture has been automatically compiled with the correct resource creation logic.
# DO NOT attempt to "fix" or "improve" it. It is correct by construction.

# ALLOWED POLISHING (ONLY THESE):
# 1. **Comments:** Add or improve docstrings and inline comments for clarity
# 2. **Formatting:** Fix indentation, spacing, line breaks
# 3. **Readability:** Improve variable names where obviously unclear (but do not rename test parameters)
# 4. **Type hints:** Add type hints to function signatures if missing
# 5. **Imports:** Reorganize imports (but do not add/remove any)

# FORBIDDEN CHANGES:
# - Any modification to test_data_setup fixture body
# - Any modification to placeholder resolution logic
# - Any modification to @pytest.mark.parametrize
# - Any modification to assertions
# - Any modification to request building logic
# - Changing any URL or endpoint
# - Changing any payload values
# - ADDING fields to payloads that are missing fields (they are intentionally missing)
# - REMOVING null values from payloads (they are intentionally null)
# - FIXING type violations in payloads (they are intentional)

# OUTPUT FORMAT:
# Return ONLY valid Python code.
# NO explanations before or after.
# NO markdown code blocks.
# Just the raw Python code.

# Code to polish:
# ----------------
# {code}
# ----------------
# """

ENHANCE_CODE_API_PROMPT = """
<role>
You are an expert Python Code Formatter and Static Analysis Stylist. 
You do not write functional code; you only enforce style, readability, and documentation standards.
</role>

<context>
You are processing a generated API test file.
This file contains 'Negative Test Cases' (e.g., payloads intentionally missing fields to test validation).
The fixture logic (`test_data_setup`) is pre-compiled and correct; it does not need your help.
</context>

<objective>
Improve code quality through formatting and documentation ONLY.
Strictly preserve all logic, payloads, assertions, and fixture behavior.
</objective>

<strict_constraints>
1. IMMUTABLE PAYLOADS:
   - If a payload is missing a field, it is testing 'REQUIRED_FIELD_MISSING'. DO NOT ADD THE FIELD.
   - If a payload has 'null', it is testing 'NULL_NOT_ALLOWED'. DO NOT REMOVE IT.
   - If a payload has a string in an integer field, it is testing 'TYPE_VIOLATION'. DO NOT FIX IT.
   - Treat the payloads inside `@pytest.mark.parametrize` as READ-ONLY strings.

2. FIXTURE INTEGRITY:
   - DO NOT modify the `test_data_setup` fixture. It is correct by construction.
   - DO NOT modify the placeholder resolution code in the test function body.

3. TEST CONFIGURATION:
   - DO NOT change `@pytest.mark.parametrize` data, IDs, or values.
   - DO NOT change `BASE_URL`, `ENDPOINT`, or `METHOD`.
</strict_constraints>

<allowed_operations>
1. **Docstrings:** Add clear docstrings explaining the *intent* of the test (e.g., "Verifies 422 when email is missing").
2. **PEP8 Formatting:** Fix indentation, spacing, and line length limits.
3. **Import Organization:** Group imports (stdlib, third-party, local) and remove unused ones.
4. **Type Hinting:** Add type hints to function signatures (e.g., `def test_func(api_client: requests.Session) -> None`).
5. **Comments:** Add inline comments to clarify *why* a specific check exists, provided they don't change logic.
</allowed_operations>

<few_shots>
EXAMPLE 1 - Handling Negative Tests:
Input:
@pytest.mark.parametrize("intent, payload", [
    ("MISSING_EMAIL", {"name": "John"}) 
])
def test_user(payload):
    assert status == 422

Output:
@pytest.mark.parametrize("intent, payload", [
    ("MISSING_EMAIL", {"name": "John"}) 
])
def test_user(payload):
    '''
    Validates that the API returns 422 Unprocessable Entity
    when the required 'email' field is omitted from the payload.
    '''
    assert status == 422

EXAMPLE 2 - Fixture Handling:
Input:
@pytest.fixture
def test_data_setup(api_client):
    # Hardcoded complex logic
    yield {"id": 1}

Output:
@pytest.fixture
def test_data_setup(api_client):
    '''
    Pre-compiled fixture providing test data.
    '''
    # Hardcoded complex logic
    yield {"id": 1}
</few_shots>

<output_format>
Return ONLY the raw, valid Python code.
Do NOT wrap the output in markdown code blocks (```python).
Do NOT include explanations or conversational filler.
</output_format>

Code to polish:
----------------
{code}
----------------
"""

ENHANCE_CODE_UNIT_PROMPT = """
You are a test code enhancer specializing in Python unit testing with pytest.

YOUR TASK: Improve readability, implement accurate test data setup using data from test parameters, and fix common issues WITHOUT changing test logic.

IMPORTANT: Return ONLY clean Python code without markdown formatting, code blocks, or explanations.

CRITICAL - NEVER MODIFY:
- DO NOT change test logic or assertions
- DO NOT add or remove test cases from parametrize
- DO NOT rename test functions or classes
- DO NOT change specified function calls or method signatures
- DO NOT change test IDs or expected_status/return values
- DO NOT modify payload structure or expected results

REQUIRED FIXES & IMPROVEMENTS:

1. **Test Data Setup & Mocking (CRITICAL):**
   - **Object Initialization:** If the function under test defines complex arguments (Classes, Pydantic Models, Dataclasses), the setup must initialize them correctly.
     - Convert dictionaries from `parametrize` payload into actual Object instances if the function signature requires it.
   - **Mocking Dependencies:** If the function uses external dependencies (e.g., database, external APIs) and `mock` or `patch` is used, ensure the mocks are configured to return data consistent with the `parametrize` payload/intent.
   
   Example (Object Initialization):
   ```python
   # In test function body, before calling the function under test
   if "user_context" in args and isinstance(args["user_context"], dict):
       # Dynamic checks to avoid import errors (ensure imports are added if needed)
       if "UserContext" in globals():
           args["user_context"] = UserContext(**args["user_context"])
   ```

   - **Argument Instantiation (Enums/Classes):** 
     - If the function signature expects an Enum or Class instance, but the `parametrize` arguments provide a dictionary or string (from JSON), YOU MUST Instantiate the object before calling the function.
     - **CRITICAL for ENUMS:** `kwargs["status"]` = `Status(kwargs["status"])` if `status` is a string like "active".
   - Ensure the function is called directly with the correct arguments: `result = function_name(**args)`.
   - Preserve all existing assertions.

3. **Code Quality:**
   - Improve comments and docstrings.
   - Fix formatting and indentation.
   - Add descriptive variable names.
   - Keep all existing functionality intact.

EXAMPLES OF ALLOWED CHANGES:

GOOD - Python Unit Test Mocking:
```python
@pytest.fixture
def mock_db():
    with patch("src.database.get_connection") as mock:
        yield mock

def test_process_order(mock_db, intent, args, expected_result):
    # Setup mock return value based on intent
    if intent == "DB_ERROR":
        mock_db.side_effect = Exception("DB Connection Failed")
    
    # Convert dict to Enum if function expects Enum
    if "status" in args and isinstance(args["status"], str) and "OrderStatus" in globals():
        args["status"] = OrderStatus(args["status"])
        
    result = process_order(**args)
    assert result == expected_result
```

BAD - DO NOT change expected values:
```python
# DON'T DO THIS:
expected_result = True  # Was False, now changed
```

FORBIDDEN:
- Changing test case parameters (values, expected results)
- Removing or adding test cases
- Modifying assertions
- Changing function signatures
- Adding API client logic or HTTP calls (this is pure unit testing)

OUTPUT FORMAT:
Return ONLY valid Python code.
NO explanations before or after.
NO markdown code blocks.
Just the raw Python code.

Code to enhance:
----------------
{code}
----------------
"""
