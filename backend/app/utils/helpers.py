"""
Utility functions for string formatting, price cleaning, and logging.
"""

import re
import logging
from typing import Optional


def setup_logger(name: str = "shopping_agent") -> logging.Logger:
    """Configure and return a standard logger for application services."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def clean_price_string(raw_price: Optional[str]) -> str:
    """
    Extract clean price string in rupees from raw text.
    Handles smashed strings like '₹12,999₹15,00015% off'.
    """
    if not raw_price or raw_price == "N/A":
        return "N/A"
    
    match = re.search(r"₹\s*[0-9,]+(?:\.[0-9]{2})?", raw_price)
    if match:
        return match.group(0).replace(" ", "")
    return raw_price.strip()


def format_currency(amount: float, symbol: str = "₹") -> str:
    """Format a numerical amount into INR currency string format (e.g. ₹12,999.00)."""
    try:
        return f"{symbol}{amount:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"
