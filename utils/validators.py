"""Input validation utilities for the Hospital PDF Manager application."""

import re
from typing import Tuple


def validate_hospital_number(number: str) -> Tuple[bool, str]:
    """
    Validate hospital number input.

    Args:
        number: The hospital number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Strip whitespace
    number = number.strip()

    # Check if empty
    if not number:
        return False, "Hospital number is required"

    # Check max length
    if len(number) > 20:
        return False, "Hospital number cannot exceed 20 characters"

    # Check if it contains only alphanumeric characters and hyphens
    if not re.match(r"^[a-zA-Z0-9\-]+$", number):
        return False, "Hospital number can only contain letters, numbers, and hyphens"

    return True, ""
