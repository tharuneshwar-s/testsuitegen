"""
Type Category - Type Validation Tests

This module contains functions designed to test type-related intents:
- TYPE_VIOLATION: Wrong type for an argument
- NULL_NOT_ALLOWED: None passed where not allowed
- ARRAY_ITEM_TYPE_VIOLATION: Wrong type in list items
- DICT_KEY_TYPE_VIOLATION: Wrong key type in dict
- DICT_VALUE_TYPE_VIOLATION: Wrong value type in dict
- UNION_NO_MATCH: Value doesn't match any union variant

Recommended Intents:
- HAPPY_PATH
- TYPE_VIOLATION
- NULL_NOT_ALLOWED
- ARRAY_ITEM_TYPE_VIOLATION
- DICT_KEY_TYPE_VIOLATION
- DICT_VALUE_TYPE_VIOLATION
- UNION_NO_MATCH
"""

from typing import List, Dict, Optional, Union


def process_number(value: int) -> int:
    """
    Processes an integer value.
    
    Tests TYPE_VIOLATION when a non-integer is passed.
    
    Args:
        value: Must be an integer.
        
    Returns:
        The processed value.
    """
    return value * 2


def process_string(text: str) -> str:
    """
    Processes a string value.
    
    Tests TYPE_VIOLATION when a non-string is passed.
    
    Args:
        text: Must be a string.
        
    Returns:
        The processed string.
    """
    return text.upper()


def process_boolean(flag: bool) -> str:
    """
    Processes a boolean value.
    
    Tests TYPE_VIOLATION when a non-boolean is passed.
    
    Args:
        flag: Must be a boolean.
        
    Returns:
        String representation.
    """
    return "enabled" if flag else "disabled"


def process_list_of_strings(items: List[str]) -> int:
    """
    Counts items in a list of strings.
    
    Tests ARRAY_ITEM_TYPE_VIOLATION when list contains non-strings.
    
    Args:
        items: List of strings only.
        
    Returns:
        Count of items.
    """
    return len(items)


def process_list_of_numbers(numbers: List[int]) -> int:
    """
    Sums a list of integers.
    
    Tests ARRAY_ITEM_TYPE_VIOLATION when list contains non-integers.
    
    Args:
        numbers: List of integers only.
        
    Returns:
        Sum of all numbers.
    """
    return sum(numbers)


def process_dict_string_keys(data: Dict[str, int]) -> int:
    """
    Sums values in a dict with string keys.
    
    Tests DICT_KEY_TYPE_VIOLATION and DICT_VALUE_TYPE_VIOLATION.
    
    Args:
        data: Dictionary with string keys and integer values.
        
    Returns:
        Sum of all values.
    """
    return sum(data.values())


def process_union_type(value: Union[str, int]) -> str:
    """
    Processes a value that can be string or int.
    
    Tests UNION_NO_MATCH when value is neither string nor int.
    
    Args:
        value: Either a string or an integer.
        
    Returns:
        String representation of the value.
    """
    return str(value)


def require_non_null(name: str, age: int) -> Dict[str, str]:
    """
    Requires non-null values for both arguments.
    
    Tests NULL_NOT_ALLOWED when None is passed.
    
    Args:
        name: Required non-null string.
        age: Required non-null integer.
        
    Returns:
        User info dictionary.
    """
    return {"name": name, "age": str(age)}


def process_optional(value: Optional[str] = None) -> str:
    """
    Processes an optional string value.
    
    This should NOT trigger NULL_NOT_ALLOWED since Optional allows None.
    
    Args:
        value: Optional string that can be None.
        
    Returns:
        The value or a default.
    """
    return value or "default"
