from enum import Enum


class OpenAPISpecIntentType(str, Enum):
    # General intent types
    HAPPY_PATH = "HAPPY_PATH"

    # Field-related violations
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    NULL_NOT_ALLOWED = "NULL_NOT_ALLOWED"
    TYPE_VIOLATION = "TYPE_VIOLATION"
    # Path Parameter Semantics (404 vs 400)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"  # Valid format, wrong ID -> 404
    FORMAT_INVALID_PATH_PARAM = "FORMAT_INVALID_PATH_PARAM"  # Invalid format -> 400
    # Array-related violations
    ARRAY_ITEM_TYPE_VIOLATION = "ARRAY_ITEM_TYPE_VIOLATION"
    ARRAY_SHAPE_VIOLATION = "ARRAY_SHAPE_VIOLATION"
    NESTED_ARRAY_ITEM_TYPE_VIOLATION = "NESTED_ARRAY_ITEM_TYPE_VIOLATION"

    # Union-related violations
    UNION_NO_MATCH = "UNION_NO_MATCH"

    # Property-related violations
    ADDITIONAL_PROPERTY_NOT_ALLOWED = "ADDITIONAL_PROPERTY_NOT_ALLOWED"
    OBJECT_VALUE_TYPE_VIOLATION = "OBJECT_VALUE_TYPE_VIOLATION"
    ARRAY_ITEM_OBJECT_VALUE_TYPE_VIOLATION = "ARRAY_ITEM_OBJECT_VALUE_TYPE_VIOLATION"

    # String constraint violations
    ENUM_MISMATCH = "ENUM_MISMATCH"
    STRING_TOO_SHORT = "STRING_TOO_SHORT"
    STRING_TOO_LONG = "STRING_TOO_LONG"
    PATTERN_MISMATCH = "PATTERN_MISMATCH"
    FORMAT_INVALID = "FORMAT_INVALID"

    # Numeric constraint violations
    NUMBER_TOO_SMALL = "NUMBER_TOO_SMALL"
    NUMBER_TOO_LARGE = "NUMBER_TOO_LARGE"
    NOT_MULTIPLE_OF = "NOT_MULTIPLE_OF"

    # Array constraint violations
    ARRAY_TOO_SHORT = "ARRAY_TOO_SHORT"
    ARRAY_TOO_LONG = "ARRAY_TOO_LONG"
    ARRAY_NOT_UNIQUE = "ARRAY_NOT_UNIQUE"

    # Object constraint violations
    OBJECT_TOO_FEW_PROPERTIES = "OBJECT_TOO_FEW_PROPERTIES"
    OBJECT_TOO_MANY_PROPERTIES = "OBJECT_TOO_MANY_PROPERTIES"

    # Precise Boundaries (Off-by-one)
    BOUNDARY_MIN_MINUS_ONE = "BOUNDARY_MIN_MINUS_ONE"  # e.g., min=10, send 9
    BOUNDARY_MAX_PLUS_ONE = "BOUNDARY_MAX_PLUS_ONE"  # e.g., max=10, send 11
    BOUNDARY_MIN_LENGTH_MINUS_ONE = "BOUNDARY_MIN_LENGTH_MINUS_ONE"
    BOUNDARY_MAX_LENGTH_PLUS_ONE = "BOUNDARY_MAX_LENGTH_PLUS_ONE"
    BOUNDARY_MIN_ITEMS_MINUS_ONE = "BOUNDARY_MIN_ITEMS_MINUS_ONE"
    BOUNDARY_MAX_ITEMS_PLUS_ONE = "BOUNDARY_MAX_ITEMS_PLUS_ONE"

    # Data Edge Cases
    EMPTY_STRING = "EMPTY_STRING"  # "" (Different from NULL)
    WHITESPACE_ONLY = "WHITESPACE_ONLY"  # "   "

    # Security Fuzzing
    SQL_INJECTION = "SQL_INJECTION"
    XSS_INJECTION = "XSS_INJECTION"
    COMMAND_INJECTION = "COMMAND_INJECTION"

    # Polymorphism & Logic Dependencies
    DISCRIMINATOR_VIOLATION = "DISCRIMINATOR_VIOLATION"  # Invalid discriminator value
    DEPENDENCY_VIOLATION = "DEPENDENCY_VIOLATION"  # Missing dependent field
    CONDITIONAL_REQUIRED_MISSING = "CONDITIONAL_REQUIRED_MISSING"  # Conditional logic: if A=1, B required but missing

    # Header Fuzzing
    HEADER_MISSING = "HEADER_MISSING"
    HEADER_ENUM_MISMATCH = "HEADER_ENUM_MISMATCH"
    HEADER_INJECTION = "HEADER_INJECTION"  # CRLF Injection


# ----- New: intents grouped by category -----
INTENTS_BY_CATEGORY = {
    "Functional": [
        OpenAPISpecIntentType.HAPPY_PATH.value,
    ],
    "Structure": [
        OpenAPISpecIntentType.REQUIRED_FIELD_MISSING.value,
        OpenAPISpecIntentType.NULL_NOT_ALLOWED.value,
        OpenAPISpecIntentType.TYPE_VIOLATION.value,
        OpenAPISpecIntentType.RESOURCE_NOT_FOUND.value,
        OpenAPISpecIntentType.FORMAT_INVALID_PATH_PARAM.value,
        OpenAPISpecIntentType.ADDITIONAL_PROPERTY_NOT_ALLOWED.value,
        OpenAPISpecIntentType.OBJECT_VALUE_TYPE_VIOLATION.value,
    ],
    "Constraints": [
        OpenAPISpecIntentType.ENUM_MISMATCH.value,
        OpenAPISpecIntentType.STRING_TOO_SHORT.value,
        OpenAPISpecIntentType.STRING_TOO_LONG.value,
        OpenAPISpecIntentType.PATTERN_MISMATCH.value,
        OpenAPISpecIntentType.NUMBER_TOO_SMALL.value,
        OpenAPISpecIntentType.NUMBER_TOO_LARGE.value,
        OpenAPISpecIntentType.NOT_MULTIPLE_OF.value,
        OpenAPISpecIntentType.BOUNDARY_MIN_MINUS_ONE.value,
        OpenAPISpecIntentType.BOUNDARY_MAX_PLUS_ONE.value,
    ],
    "Array": [
        OpenAPISpecIntentType.ARRAY_ITEM_TYPE_VIOLATION.value,
        OpenAPISpecIntentType.ARRAY_SHAPE_VIOLATION.value,
        OpenAPISpecIntentType.ARRAY_TOO_SHORT.value,
        OpenAPISpecIntentType.ARRAY_TOO_LONG.value,
        OpenAPISpecIntentType.ARRAY_NOT_UNIQUE.value,
    ],
    "Security": [
        OpenAPISpecIntentType.SQL_INJECTION.value,
        OpenAPISpecIntentType.XSS_INJECTION.value,
        OpenAPISpecIntentType.COMMAND_INJECTION.value,
        OpenAPISpecIntentType.HEADER_INJECTION.value,
    ],
}

# Flattened list and reverse map for quick lookup
ALL_OPENAPI_INTENTS = [i for cat in INTENTS_BY_CATEGORY.values() for i in cat]
INTENT_TO_CATEGORY = {
    intent: cat for cat, lst in INTENTS_BY_CATEGORY.items() for intent in lst
}
