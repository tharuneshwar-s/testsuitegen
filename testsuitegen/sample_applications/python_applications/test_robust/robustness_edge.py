"""
Robustness Category - Edge Case Tests

This module contains functions designed to test robustness-related intents:
- EMPTY_STRING: Empty string input
- WHITESPACE_ONLY: String with only whitespace
- ZERO_VALUE: Zero numeric input
- NEGATIVE_VALUE: Negative numeric input
- EMPTY_COLLECTION: Empty list or dict

Recommended Intents:
- HAPPY_PATH
- EMPTY_STRING
- WHITESPACE_ONLY
- ZERO_VALUE
- NEGATIVE_VALUE
- EMPTY_COLLECTION
"""

from typing import List, Dict, Optional


def process_name(name: str) -> str:
    """
    Processes a user's name.

    Tests EMPTY_STRING and WHITESPACE_ONLY edge cases.

    Args:
        name: User's name, should not be empty or whitespace.

    Returns:
        Formatted name.
    """
    if not name or not name.strip():
        raise ValueError("Name cannot be empty or whitespace only")
    return name.strip().title()


def process_description(text: str) -> str:
    """
    Processes a description text.

    Tests EMPTY_STRING and WHITESPACE_ONLY inputs.

    Args:
        text: Description text.

    Returns:
        Cleaned text.
    """
    cleaned = text.strip()
    if not cleaned:
        return "No description provided"
    return cleaned


def divide_numbers(dividend: int, divisor: int) -> float:
    """
    Divides two numbers.

    Tests ZERO_VALUE when divisor is zero.

    Args:
        dividend: The number to divide.
        divisor: The number to divide by, cannot be zero.

    Returns:
        Result of division.
    """
    if divisor == 0:
        raise ValueError("Cannot divide by zero")
    return dividend / divisor


def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculates discounted price.

    Tests ZERO_VALUE and NEGATIVE_VALUE for discount.

    Args:
        price: Original price.
        discount_percent: Discount percentage (0-100).

    Returns:
        Discounted price.
    """
    if discount_percent < 0:
        raise ValueError("Discount cannot be negative")
    return price * (1 - discount_percent / 100)


def process_quantity(quantity: int) -> str:
    """
    Processes a quantity value.

    Tests ZERO_VALUE and NEGATIVE_VALUE inputs.

    Args:
        quantity: Item quantity.

    Returns:
        Quantity status string.
    """
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if quantity == 0:
        return "out_of_stock"
    return f"in_stock_{quantity}"


def calculate_average(numbers: List[float]) -> float:
    """
    Calculates average of a list of numbers.

    Tests EMPTY_COLLECTION when list is empty.

    Args:
        numbers: List of numbers to average.

    Returns:
        Average value.
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)


def get_first_item(items: List[str]) -> str:
    """
    Gets the first item from a list.

    Tests EMPTY_COLLECTION when list is empty.

    Args:
        items: List of string items.

    Returns:
        First item.
    """
    if not items:
        raise ValueError("List cannot be empty")
    return items[0]


def merge_configs(config: Dict[str, str]) -> Dict[str, str]:
    """
    Merges configuration with defaults.

    Tests EMPTY_COLLECTION when dict is empty.

    Args:
        config: Configuration dictionary.

    Returns:
        Merged configuration.
    """
    defaults = {"timeout": "30", "retries": "3"}
    if not config:
        return defaults
    return {**defaults, **config}


def validate_tags(tags: List[str]) -> bool:
    """
    Validates a list of tags.

    Tests EMPTY_COLLECTION and items with EMPTY_STRING.

    Args:
        tags: List of tag strings.

    Returns:
        True if all tags are valid.
    """
    if not tags:
        raise ValueError("Tags list cannot be empty")
    for tag in tags:
        if not tag.strip():
            raise ValueError("Tags cannot be empty strings")
    return True
