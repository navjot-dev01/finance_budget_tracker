import re
from datetime import datetime

def is_valid_amount(amount_str: str) -> bool:
    """Checks if the amount is a valid positive number greater than 0."""
    try:
        amount = float(amount_str)
        return amount > 0
    except ValueError:
        return False

def is_valid_date(date_str: str) -> bool:
    """Checks if the date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_not_empty(value_str: str) -> bool:
    """Checks if a string is not empty or just whitespace."""
    if not value_str:
        return False
    return len(value_str.strip()) > 0
