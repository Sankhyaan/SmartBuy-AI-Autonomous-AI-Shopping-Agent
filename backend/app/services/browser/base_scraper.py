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
    """Clean and strip parentheses/words from rating count e.g. '(1,234)' -> '1,234', '(41.9K)' -> '41.9K'."""
    if not raw_count:
        return None
    import re
    cleaned = raw_count.replace("(", "").replace(")", "").strip()
    match = re.search(r"([0-9,]+(?:\.[0-9]+)?[KMBkmb]?)", cleaned)
    if match:
        return match.group(1).upper()
    return cleaned if cleaned else None


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
