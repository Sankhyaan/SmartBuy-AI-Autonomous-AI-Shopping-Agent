"""
Base Scraper Utilities

Shared helper functions for Playwright browser automation:
- Anti-detection headers / viewport setup
- Smooth scrolling to trigger lazy loading
- Safe string extraction with fallback defaults
"""

import asyncio
from typing import Optional
from playwright.async_api import Page, ElementHandle

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


async def configure_anti_detection(page: Page) -> None:
    """Apply realistic user-agent and headers to reduce bot detection."""
    await page.set_extra_http_headers({
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    })


async def smooth_scroll(page: Page, scrolls: int = 6, distance: int = 700) -> None:
    """Scroll down incrementally to trigger lazy-loaded images and products."""
    for _ in range(scrolls):
        await page.evaluate(f"window.scrollBy(0, {distance})")
        await asyncio.sleep(0.4)


def format_rating_out_of_5(raw_rating: Optional[str]) -> Optional[str]:
    """Standardize rating string to 'X.X out of 5 stars' format for all platforms."""
    if not raw_rating or raw_rating == "N/A":
        return None
    import re
    match = re.search(r"([0-5](?:\.[0-9])?)", raw_rating)
    if match:
        val = match.group(1)
        if "." not in val:
            val = f"{val}.0"
        return f"{val} out of 5 stars"
    return None


def clean_rating_count(raw_count: Optional[str]) -> Optional[str]:
    """
    Clean and strip parentheses/words from rating count.
    Supports Indian numbering format (e.g. '33,365', '2,25,115'), Western (e.g. '225,115'), and abbreviations ('4.3K').
    Handles 'based on 33,365 ratings by Verified Buyers'.
    Rejects unit prices like '₹63.97 / 100g' or decimal floats.
    """
    if not raw_count:
        return None
    
    raw_lower = raw_count.lower().strip()
    
    # Reject unit prices or non-review text containing currency symbols or per-unit indicators
    if "₹" in raw_lower or "$" in raw_lower or "/" in raw_lower or "100g" in raw_lower or "per " in raw_lower:
        return None
        
    import re
    # Explicitly match "based on 33,365 ratings" or "33,365 ratings" pattern
    ratings_pattern_match = re.search(r"(?:based\s+on\s+)?([0-9][0-9,]*[0-9]|[0-9]+)\s*ratings", raw_count, re.IGNORECASE)
    if ratings_pattern_match:
        return ratings_pattern_match.group(1).strip()

    # Extract numbers inside parentheses first if present e.g. "(33,365)" -> "33,365"
    paren_match = re.search(r"\(([0-9,]+(?:\.[0-9]+)?[KMBkmb]?)\)", raw_count)
    if paren_match:
        cleaned = paren_match.group(1).strip()
    else:
        cleaned = re.sub(r"(?i)\b(based|on|ratings|rating|reviews|verified|buyers)\b", "", raw_count)
        cleaned = cleaned.replace("(", "").replace(")", "").strip()
    
    match = re.search(r"([0-9][0-9,]*[0-9]|[0-9]+(?:\.[0-9])?[KMBkmb]|[0-9]+)", cleaned)
    if match:
        val = match.group(1).strip().upper()
        if "." in val and not any(char in val for char in ["K", "M", "B"]):
            return None
        return val
    return None


def parse_count_numeric_value(count_str: Optional[str]) -> float:
    """Convert cleaned count string ('13,311', '2,25,115', '4.3K') into numeric float value for max comparison."""
    if not count_str:
        return 0.0
    s = count_str.upper().replace(",", "").strip()
    if s.endswith("K"):
        try:
            return float(s[:-1]) * 1000.0
        except ValueError:
            return 0.0
    elif s.endswith("M"):
        try:
            return float(s[:-1]) * 1000000.0
        except ValueError:
            return 0.0
    elif s.endswith("B"):
        try:
            return float(s[:-1]) * 1000000000.0
        except ValueError:
            return 0.0
    else:
        try:
            return float(s)
        except ValueError:
            return 0.0


def clean_bought_past_month(raw_text: Optional[str]) -> Optional[str]:
    """Extract and standardize 'X+ bought in past month' pattern."""
    if not raw_text:
        return None
    import re
    match = re.search(r"([0-9KMBkmb\+]+\+?\s*bought in\s*(?:the\s*)?past\s*(?:month|30 days)?)", raw_text, re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        return re.sub(r"([0-9]+)([kmb])", lambda m: m.group(1) + m.group(2).upper(), val, flags=re.IGNORECASE)
    return None


async def safe_text(element: ElementHandle, selector: str, fallback: Optional[str] = None) -> Optional[str]:
    """Safely extract text content from a sub-element with an optional fallback default."""
    try:
        sub = await element.query_selector(selector)
        if sub:
            text = await sub.text_content()
            return text.strip() if text and text.strip() else fallback
    except Exception:
        pass
    return fallback


async def safe_attribute(element: ElementHandle, selector: str, attribute: str, fallback: Optional[str] = None) -> Optional[str]:
    """Safely extract an attribute value (e.g. href, src) from a sub-element with an optional fallback."""
    try:
        sub = await element.query_selector(selector)
        if sub:
            val = await sub.get_attribute(attribute)
            return val.strip() if val and val.strip() else fallback
    except Exception:
        pass
    return fallback
