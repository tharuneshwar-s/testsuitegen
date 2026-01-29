from enum import Enum


class PythonIntentType(str, Enum):
    # --- 1. Structural (The Contract) ---
    HAPPY_PATH = "HAPPY_PATH"
    REQUIRED_ARG_MISSING = "REQUIRED_ARG_MISSING"
    UNEXPECTED_ARGUMENT = "UNEXPECTED_ARGUMENT"
    TOO_MANY_POS_ARGS = "TOO_MANY_POS_ARGS"

    # --- 2. Type System (Static Typing) ---
    TYPE_VIOLATION = "TYPE_VIOLATION"
    NULL_NOT_ALLOWED = "NULL_NOT_ALLOWED"
    ARRAY_ITEM_TYPE_VIOLATION = "ARRAY_ITEM_TYPE_VIOLATION"
    DICT_KEY_TYPE_VIOLATION = "DICT_KEY_TYPE_VIOLATION"
    DICT_VALUE_TYPE_VIOLATION = "DICT_VALUE_TYPE_VIOLATION"
    UNION_NO_MATCH = "UNION_NO_MATCH"

    # --- 3. Constraints & Boundaries (The Logic) ---
    BOUNDARY_MIN_MINUS_ONE = "BOUNDARY_MIN_MINUS_ONE"
    BOUNDARY_MAX_PLUS_ONE = "BOUNDARY_MAX_PLUS_ONE"
    STRING_TOO_SHORT = "STRING_TOO_SHORT"
    STRING_TOO_LONG = "STRING_TOO_LONG"
    PATTERN_MISMATCH = "PATTERN_MISMATCH"
    ENUM_MISMATCH = "ENUM_MISMATCH"
    NOT_MULTIPLE_OF = "NOT_MULTIPLE_OF"

    # --- 4. Data Edge Cases (Robustness) ---
    EMPTY_STRING = "EMPTY_STRING"
    WHITESPACE_ONLY = "WHITESPACE_ONLY"
    ZERO_VALUE = "ZERO_VALUE"
    NEGATIVE_VALUE = "NEGATIVE_VALUE"
    EMPTY_COLLECTION = "EMPTY_COLLECTION"

    # --- 5. Complex Objects ---
    OBJECT_MISSING_FIELD = "OBJECT_MISSING_FIELD"
    OBJECT_EXTRA_FIELD = "OBJECT_EXTRA_FIELD"

    # --- 6. Security Fuzzing ---
    SQL_INJECTION = "SQL_INJECTION"
    XSS_INJECTION = "XSS_INJECTION"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    COMMAND_INJECTION = "COMMAND_INJECTION"

    # --- 7. Python Runtime Specifics ---
    MUTABLE_DEFAULT_TRAP = "MUTABLE_DEFAULT_TRAP"


# ----- New: intents grouped by category -----
INTENTS_BY_CATEGORY = {
    "Functional": [
        PythonIntentType.HAPPY_PATH.value,
    ],
    "Structure": [
        PythonIntentType.REQUIRED_ARG_MISSING.value,
        PythonIntentType.UNEXPECTED_ARGUMENT.value,
        PythonIntentType.TOO_MANY_POS_ARGS.value,
        PythonIntentType.OBJECT_MISSING_FIELD.value,
        PythonIntentType.OBJECT_EXTRA_FIELD.value,
    ],
    "Type": [
        PythonIntentType.TYPE_VIOLATION.value,
        PythonIntentType.NULL_NOT_ALLOWED.value,
        PythonIntentType.ARRAY_ITEM_TYPE_VIOLATION.value,
        PythonIntentType.DICT_KEY_TYPE_VIOLATION.value,
        PythonIntentType.DICT_VALUE_TYPE_VIOLATION.value,
        PythonIntentType.UNION_NO_MATCH.value,
    ],
    "Constraints": [
        PythonIntentType.BOUNDARY_MIN_MINUS_ONE.value,
        PythonIntentType.BOUNDARY_MAX_PLUS_ONE.value,
        PythonIntentType.STRING_TOO_SHORT.value,
        PythonIntentType.STRING_TOO_LONG.value,
        PythonIntentType.PATTERN_MISMATCH.value,
        PythonIntentType.ENUM_MISMATCH.value,
        PythonIntentType.NOT_MULTIPLE_OF.value,
    ],
    "Robustness": [
        PythonIntentType.EMPTY_STRING.value,
        PythonIntentType.WHITESPACE_ONLY.value,
        PythonIntentType.ZERO_VALUE.value,
        PythonIntentType.NEGATIVE_VALUE.value,
        PythonIntentType.EMPTY_COLLECTION.value,
    ],
    "Security": [
        PythonIntentType.SQL_INJECTION.value,
        PythonIntentType.XSS_INJECTION.value,
        PythonIntentType.PATH_TRAVERSAL.value,
        PythonIntentType.COMMAND_INJECTION.value,
    ],
    "Runtime": [
        PythonIntentType.MUTABLE_DEFAULT_TRAP.value,
    ],
}

# Flattened list and reverse map for quick lookup
ALL_PYTHON_INTENTS = [i for cat in INTENTS_BY_CATEGORY.values() for i in cat]
INTENT_TO_CATEGORY = {
    intent: cat for cat, lst in INTENTS_BY_CATEGORY.items() for intent in lst
}
