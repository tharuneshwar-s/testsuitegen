"""
Structure Category - Argument Structure Tests

This module contains functions designed to test structure-related intents:
- REQUIRED_ARG_MISSING: Missing required arguments
- UNEXPECTED_ARGUMENT: Extra unexpected arguments
- TOO_MANY_POS_ARGS: Too many positional arguments
- OBJECT_MISSING_FIELD: Missing required fields in objects
- OBJECT_EXTRA_FIELD: Extra unexpected fields in objects

Recommended Intents:
- HAPPY_PATH
- REQUIRED_ARG_MISSING
- TOO_MANY_POS_ARGS
- UNEXPECTED_ARGUMENT
- OBJECT_MISSING_FIELD
- OBJECT_EXTRA_FIELD
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class UserProfile:
    """User profile with required and optional fields."""
    username: str
    email: str
    age: int


def register_user(username: str, email: str, password: str) -> Dict[str, str]:
    """
    Registers a new user with all required fields.
    
    Tests REQUIRED_ARG_MISSING when any argument is omitted.
    
    Args:
        username: Required username.
        email: Required email address.
        password: Required password.
        
    Returns:
        Registration confirmation.
    """
    return {
        "status": "registered",
        "username": username,
        "email": email
    }


def create_order(
    customer_id: str,
    product_id: str,
    quantity: int,
    shipping_address: str
) -> Dict[str, str]:
    """
    Creates an order with multiple required arguments.
    
    Tests REQUIRED_ARG_MISSING and TOO_MANY_POS_ARGS.
    
    Args:
        customer_id: The customer identifier.
        product_id: The product identifier.
        quantity: Number of items to order.
        shipping_address: Delivery address.
        
    Returns:
        Order confirmation.
    """
    return {
        "order_id": "ORD-12345",
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": str(quantity),
        "status": "created"
    }


def update_profile(profile: Dict[str, str]) -> Dict[str, str]:
    """
    Updates a user profile from a dictionary.
    
    Tests OBJECT_MISSING_FIELD and OBJECT_EXTRA_FIELD.
    
    Args:
        profile: Dictionary with 'name', 'email', 'bio' fields.
        
    Returns:
        Updated profile.
    """
    required_fields = ["name", "email"]
    for field in required_fields:
        if field not in profile:
            raise ValueError(f"Missing required field: {field}")
    return {**profile, "updated": "true"}


def configure_settings(
    theme: str,
    language: str,
    notifications: bool,
    timezone: str
) -> Dict[str, str]:
    """
    Configures application settings with multiple parameters.
    
    Tests argument structure with many required parameters.
    
    Args:
        theme: UI theme name.
        language: Preferred language code.
        notifications: Whether to enable notifications.
        timezone: User's timezone.
        
    Returns:
        Settings confirmation.
    """
    return {
        "theme": theme,
        "language": language,
        "notifications": str(notifications),
        "timezone": timezone,
        "applied": "true"
    }
