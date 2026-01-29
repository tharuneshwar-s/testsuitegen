"""
Constraints Category - Boundary and Validation Tests

Recommended Intents:
- HAPPY_PATH
- ENUM_MISMATCH
- BOUNDARY_MIN_MINUS_ONE
- BOUNDARY_MAX_PLUS_ONE
- NEGATIVE_VALUE
- ZERO_VALUE
- NOT_MULTIPLE_OF
"""

from typing import Dict
from enum import Enum


class Priority(Enum):
    """Priority levels for tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(Enum):
    """Status values for items."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def validate_age(age: int) -> bool:
    """Validates age is between 0 and 150."""
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age cannot exceed 150")
    return True


def validate_quantity(quantity: int) -> bool:
    """Validates quantity is between 1 and 100."""
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")
    if quantity > 100:
        raise ValueError("Quantity cannot exceed 100")
    return True


def validate_percentage(value: float) -> bool:
    """Validates percentage is between 0.0 and 100.0."""
    if value < 0.0:
        raise ValueError("Percentage cannot be negative")
    if value > 100.0:
        raise ValueError("Percentage cannot exceed 100")
    return True


def validate_username(username: str) -> bool:
    """Validates username length is between 3 and 20."""
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    if len(username) > 20:
        raise ValueError("Username cannot exceed 20 characters")
    return True


def validate_password(password: str) -> bool:
    """Validates password length is between 8 and 128."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(password) > 128:
        raise ValueError("Password cannot exceed 128 characters")
    return True


def validate_email_pattern(email: str) -> bool:
    """Validates email format."""
    if "@" not in email or "." not in email:
        raise ValueError("Invalid email format")
    return True


def validate_phone_pattern(phone: str) -> bool:
    """Validates phone number contains digits/dashes/spaces only."""
    cleaned = phone.replace("-", "").replace(" ", "")
    if not cleaned.isdigit():
        raise ValueError("Phone must contain only digits and dashes")
    return True


def set_priority(task_id: str, priority: Priority) -> Dict[str, str]:
    """
    Sets task priority using Priority enum.

    Args:
        task_id: The task identifier.
        priority: Priority enum member.

    Returns:
        Updated task info.
    """
    if not isinstance(priority, Priority):
        raise ValueError(f"Priority must be a Priority enum value: {list(Priority)}")

    return {"task_id": task_id, "priority": priority.value}


def set_status(task_id: str, status: Status) -> Dict[str, str]:
    """
    Sets task status using Status enum.

    Args:
        task_id: The task identifier.
        status: Status enum member.

    Returns:
        Updated task information.
    """
    if not isinstance(status, Status):
        raise ValueError(f"Status must be a Status enum value: {list(Status)}")

    return {"task_id": task_id, "status": status.value}


def allocate_items(count: int) -> int:
    """Allocates items in batches of 5."""
    if count % 5 != 0:
        raise ValueError("Count must be a multiple of 5")
    return count // 5
