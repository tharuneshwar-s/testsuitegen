"""
Runtime Category - Python Runtime Traps

This module contains functions designed to test runtime-related intents:
- MUTABLE_DEFAULT_TRAP: Python's mutable default argument anti-pattern

This is a common Python gotcha where mutable default arguments
(like lists or dicts) are shared across function calls.

Recommended Intents:
- HAPPY_PATH
- MUTABLE_DEFAULT_TRAP
"""

from typing import List, Dict, Optional


def append_item_dangerous(item: str, items: List[str] = []) -> List[str]:
    """
    ANTI-PATTERN: Mutable default argument.

    Tests MUTABLE_DEFAULT_TRAP - this is the classic Python footgun.
    The default list is created once and shared across all calls.

    Args:
        item: Item to append.
        items: List to append to (DANGER: mutable default!).

    Returns:
        List with item appended.

    Example of the bug:
        >>> append_item_dangerous("a")
        ['a']
        >>> append_item_dangerous("b")  # Returns ['a', 'b'], not ['b']!
        ['a', 'b']
    """
    items.append(item)
    return items


def add_tag_dangerous(name: str, tags: List[str] = []) -> Dict[str, List[str]]:
    """
    ANTI-PATTERN: Mutable default argument with list.

    Tests MUTABLE_DEFAULT_TRAP with tags list.

    Args:
        name: Name of the entity.
        tags: Tags to associate (DANGER: mutable default!).

    Returns:
        Entity with tags.
    """
    tags.append(name)
    return {"name": name, "tags": tags}


def build_config_dangerous(
    key: str, value: str, base: Dict[str, str] = {}
) -> Dict[str, str]:
    """
    ANTI-PATTERN: Mutable default argument with dict.

    Tests MUTABLE_DEFAULT_TRAP with dictionary.

    Args:
        key: Config key to set.
        value: Config value to set.
        base: Base configuration (DANGER: mutable default!).

    Returns:
        Updated configuration.
    """
    base[key] = value
    return base


# --- Safe alternatives for comparison ---


def append_item_safe(item: str, items: Optional[List[str]] = None) -> List[str]:
    """
    SAFE: Correct way to handle mutable defaults.

    Uses None as default and creates new list inside function.

    Args:
        item: Item to append.
        items: Optional list to append to.

    Returns:
        List with item appended.
    """
    if items is None:
        items = []
    items.append(item)
    return items


def add_tag_safe(name: str, tags: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """
    SAFE: Correct way to handle mutable defaults.

    Args:
        name: Name of the entity.
        tags: Optional tags list.

    Returns:
        Entity with tags.
    """
    if tags is None:
        tags = []
    tags.append(name)
    return {"name": name, "tags": tags}


def build_config_safe(
    key: str, value: str, base: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    SAFE: Correct way to handle mutable defaults.

    Args:
        key: Config key to set.
        value: Config value to set.
        base: Optional base configuration.

    Returns:
        Updated configuration.
    """
    if base is None:
        base = {}
    base[key] = value
    return base
