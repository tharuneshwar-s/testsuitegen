"""
Functional Category - Basic Happy Path Tests

This module contains functions designed to test the HAPPY_PATH intent,
which verifies that functions work correctly with valid inputs.

Recommended Intents:
- HAPPY_PATH
- BOUNDARY_MIN_MINUS_ONE
- BOUNDARY_MAX_PLUS_ONE
"""

from typing import List, Dict, Optional


def greet_user(name: str) -> str:
    """
    Returns a personalized greeting for the user.

    Args:
        name: The user's name to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"


def calculate_sum(a: int, b: int) -> int:
    """
    Calculates the sum of two integers.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        The sum of a and b.
    """
    return a + b


def get_user_info(user_id: str, include_email: bool = True) -> Dict[str, str]:
    """
    Retrieves user information from the database.

    Args:
        user_id: The unique user identifier.
        include_email: Whether to include email in the response.

    Returns:
        A dictionary containing user information.
    """
    result = {"id": user_id, "name": "John Doe"}
    if include_email:
        result["email"] = "john@example.com"
    return result


def process_items(items: List[str], prefix: str = "") -> List[str]:
    """
    Processes a list of items by adding an optional prefix.

    Args:
        items: List of items to process.
        prefix: Optional prefix to add to each item.

    Returns:
        List of processed items.
    """
    return [f"{prefix}{item}" for item in items]


def validate_age(age: int) -> bool:
    """
    Validates that the age is within acceptable range (0-150).

    Args:
        age: The age to validate.

    Returns:
        True if age is valid, False otherwise.
    """
    return 0 <= age <= 150
