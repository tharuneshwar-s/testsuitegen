"""
TypeScript Intent Type Definitions

Defines all test intent types for TypeScript function testing.
These intents are specifically designed for TypeScript type system validation.
"""

from enum import Enum


class TypeScriptIntentType(str, Enum):
    # --- 1. Functional (Happy Path) ---
    HAPPY_PATH = "HAPPY_PATH"

    # --- 2. Structural (The Contract) ---
    REQUIRED_ARG_MISSING = "REQUIRED_ARG_MISSING"
    UNEXPECTED_ARGUMENT = "UNEXPECTED_ARGUMENT"
    OBJECT_MISSING_FIELD = "OBJECT_MISSING_FIELD"
    OBJECT_EXTRA_FIELD = "OBJECT_EXTRA_FIELD"

    # --- 3. Type System (Static Typing) ---
    TYPE_VIOLATION = "TYPE_VIOLATION"
    NULL_NOT_ALLOWED = "NULL_NOT_ALLOWED"
    ARRAY_ITEM_TYPE_VIOLATION = "ARRAY_ITEM_TYPE_VIOLATION"
    UNION_NO_MATCH = "UNION_NO_MATCH"
    GENERIC_TYPE_VIOLATION = "GENERIC_TYPE_VIOLATION"
    INTERFACE_MISSING_PROPERTY = "INTERFACE_MISSING_PROPERTY"

    # --- 4. Constraints & Boundaries ---
    BOUNDARY_MIN_MINUS_ONE = "BOUNDARY_MIN_MINUS_ONE"
    BOUNDARY_MAX_PLUS_ONE = "BOUNDARY_MAX_PLUS_ONE"
    STRING_TOO_SHORT = "STRING_TOO_SHORT"
    STRING_TOO_LONG = "STRING_TOO_LONG"
    PATTERN_MISMATCH = "PATTERN_MISMATCH"
    ENUM_MISMATCH = "ENUM_MISMATCH"

    # --- 5. Data Edge Cases (Robustness) ---
    EMPTY_STRING = "EMPTY_STRING"
    WHITESPACE_ONLY = "WHITESPACE_ONLY"
    ZERO_VALUE = "ZERO_VALUE"
    NEGATIVE_VALUE = "NEGATIVE_VALUE"
    EMPTY_COLLECTION = "EMPTY_COLLECTION"

    # --- 6. Security Fuzzing ---
    SQL_INJECTION = "SQL_INJECTION"
    XSS_INJECTION = "XSS_INJECTION"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    COMMAND_INJECTION = "COMMAND_INJECTION"


# Intents grouped by category
INTENTS_BY_CATEGORY = {
    "Functional": [
        TypeScriptIntentType.HAPPY_PATH.value,
    ],
    "Structure": [
        TypeScriptIntentType.REQUIRED_ARG_MISSING.value,
        TypeScriptIntentType.UNEXPECTED_ARGUMENT.value,
        TypeScriptIntentType.OBJECT_MISSING_FIELD.value,
        TypeScriptIntentType.OBJECT_EXTRA_FIELD.value,
    ],
    "Type": [
        TypeScriptIntentType.TYPE_VIOLATION.value,
        TypeScriptIntentType.NULL_NOT_ALLOWED.value,
        TypeScriptIntentType.ARRAY_ITEM_TYPE_VIOLATION.value,
        TypeScriptIntentType.UNION_NO_MATCH.value,
        TypeScriptIntentType.GENERIC_TYPE_VIOLATION.value,
        TypeScriptIntentType.INTERFACE_MISSING_PROPERTY.value,
    ],
    "Constraints": [
        TypeScriptIntentType.BOUNDARY_MIN_MINUS_ONE.value,
        TypeScriptIntentType.BOUNDARY_MAX_PLUS_ONE.value,
        TypeScriptIntentType.STRING_TOO_SHORT.value,
        TypeScriptIntentType.STRING_TOO_LONG.value,
        TypeScriptIntentType.PATTERN_MISMATCH.value,
        TypeScriptIntentType.ENUM_MISMATCH.value,
    ],
    "Robustness": [
        TypeScriptIntentType.EMPTY_STRING.value,
        TypeScriptIntentType.WHITESPACE_ONLY.value,
        TypeScriptIntentType.ZERO_VALUE.value,
        TypeScriptIntentType.NEGATIVE_VALUE.value,
        TypeScriptIntentType.EMPTY_COLLECTION.value,
    ],
    "Security": [
        TypeScriptIntentType.SQL_INJECTION.value,
        TypeScriptIntentType.XSS_INJECTION.value,
        TypeScriptIntentType.PATH_TRAVERSAL.value,
        TypeScriptIntentType.COMMAND_INJECTION.value,
    ],
}

# Flattened list and reverse map for quick lookup
ALL_TYPESCRIPT_INTENTS = [i for cat in INTENTS_BY_CATEGORY.values() for i in cat]
INTENT_TO_CATEGORY = {
    intent: cat for cat, lst in INTENTS_BY_CATEGORY.items() for intent in lst
}
