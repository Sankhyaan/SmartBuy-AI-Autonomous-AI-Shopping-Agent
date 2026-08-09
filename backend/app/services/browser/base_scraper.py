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


async def smooth_scroll(page: Page, scrolls: int = 3, distance: int = 600) -> None:
    """Scroll down incrementally to trigger lazy-loaded images and products."""
    for _ in range(scrolls):
        await page.evaluate(f"window.scrollBy(0, {distance})")
        await asyncio.sleep(0.5)


async def safe_text(element: ElementHandle, selector: str) -> Optional[str]:
    """Safely extract text content from a sub-element."""
    try:
        sub = await element.query_selector(selector)
        if sub:
            text = await sub.text_content()
            return text.strip() if text else None
    except Exception:
        pass
    return None


async def safe_attribute(element: ElementHandle, selector: str, attribute: str) -> Optional[str]:
    """Safely extract an attribute value (e.g. href, src) from a sub-element."""
    try:
        sub = await element.query_selector(selector)
        if sub:
            val = await sub.get_attribute(attribute)
            return val.strip() if val else None
    except Exception:
        pass
    return None
