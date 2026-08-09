"""
BrowserManager — Singleton Playwright lifecycle manager.

Handles:
- Launching/closing Chromium via async Playwright
- Page navigation, scrolling, clicking
- Screenshots as base64
- Status reporting

Designed as a singleton so LangGraph nodes and MCP tools can call it
directly in future phases without going through HTTP.
"""

import asyncio
import base64
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from app.config.settings import settings
from app.services.browser.base_scraper import USER_AGENT, configure_anti_detection


class BrowserManager:
    """Async singleton managing a single Playwright Chromium instance."""

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    # ── Lifecycle ─────────────────────────────────────────────

    async def start(self) -> dict:
        """Launch Chromium and open a blank page."""
        if self._browser and self._browser.is_connected():
            return {"status": "Browser already running"}

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=settings.browser_headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        self._context = await self._browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 768},
        )
        self._page = await self._context.new_page()
        await configure_anti_detection(self._page)
        return {"status": "Browser started"}

    async def stop(self) -> dict:
        """Close browser and clean up Playwright resources."""
        if not self._browser:
            return {"status": "Browser is not running"}

        try:
            if self._browser.is_connected():
                await self._browser.close()
        except Exception:
            pass

        try:
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass

        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None
        return {"status": "Browser stopped"}

    # ── Status ────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        return self._browser is not None and self._browser.is_connected()

    async def get_status(self) -> dict:
        """Return current browser state."""
        if not self.is_running or not self._page:
            return {"is_running": False, "current_url": None, "title": None}

        try:
            url = self._page.url
            title = await self._page.title()
        except Exception:
            url = None
            title = None

        return {"is_running": True, "current_url": url, "title": title}

    # ── Page helpers ──────────────────────────────────────────

    def _ensure_page(self) -> Page:
        """Raise if browser is not started or page is closed."""
        if not self.is_running or not self._page:
            raise RuntimeError("Browser is not running. Call /browser/start first.")
        return self._page

    async def open_url(self, url: str, wait_until: str = "domcontentloaded") -> dict:
        """Navigate to a URL."""
        page = self._ensure_page()
        try:
            await page.goto(url, wait_until=wait_until, timeout=30000)
        except Exception as e:
            raise RuntimeError(f"Failed to open URL: {e}")
        return {"url": page.url, "title": await page.title()}

    async def scroll(self, direction: str = "down", amount: int = 500) -> dict:
        """Scroll the page up or down."""
        page = self._ensure_page()
        pixels = amount if direction == "down" else -amount
        await page.evaluate(f"window.scrollBy(0, {pixels})")
        await asyncio.sleep(0.3)
        return {"scrolled": direction, "pixels": abs(amount)}

    async def click(self, selector: str) -> dict:
        """Click an element by CSS selector."""
        page = self._ensure_page()
        try:
            await page.click(selector, timeout=10000)
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            raise RuntimeError(f"Click failed on '{selector}': {e}")
        return {"clicked": selector, "url": page.url}

    async def screenshot(self) -> dict:
        """Take a full-page screenshot and return it as base64 PNG."""
        page = self._ensure_page()
        try:
            img_bytes = await page.screenshot(type="png", full_page=False)
            b64 = base64.b64encode(img_bytes).decode("utf-8")
        except Exception as e:
            raise RuntimeError(f"Screenshot failed: {e}")
        return {"image_base64": b64, "current_url": page.url}

    async def get_page(self) -> Page:
        """Expose the raw page for scrapers to use directly."""
        return self._ensure_page()


# Module-level singleton
browser_manager = BrowserManager()
