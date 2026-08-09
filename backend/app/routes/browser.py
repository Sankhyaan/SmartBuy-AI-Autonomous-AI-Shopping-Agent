"""
Browser router — HTTP endpoints for Playwright browser automation.

All endpoints delegate to BrowserManager and scraper modules.
Routes stay thin; business logic lives in services/browser/.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    BrowserStatusResponse,
    OpenUrlRequest,
    SearchRequest,
    ProductSearchResponse,
    ScreenshotResponse,
    ScrollRequest,
)
from app.services.browser.browser_manager import browser_manager
from app.services.browser.amazon import search_amazon
from app.services.browser.flipkart import search_flipkart

router = APIRouter(prefix="/browser", tags=["Browser"])


@router.post("/start")
async def start_browser():
    """Launch the Playwright Chromium browser."""
    try:
        result = await browser_manager.start()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start browser: {e}")


@router.post("/stop")
async def stop_browser():
    """Close the Playwright browser and free resources."""
    try:
        result = await browser_manager.stop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop browser: {e}")


@router.get("/status", response_model=BrowserStatusResponse)
async def browser_status():
    """Get current browser state (running, URL, title)."""
    return await browser_manager.get_status()


@router.post("/open")
async def open_url(request: OpenUrlRequest):
    """Navigate the browser to a given URL."""
    try:
        result = await browser_manager.open_url(request.url)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/scroll")
async def scroll_page(request: ScrollRequest):
    """Scroll the current page up or down."""
    try:
        result = await browser_manager.scroll(request.direction, request.amount)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/screenshot", response_model=ScreenshotResponse)
async def take_screenshot():
    """Capture a screenshot of the current page (base64 PNG)."""
    try:
        result = await browser_manager.screenshot()
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/amazon/search", response_model=ProductSearchResponse)
async def amazon_search(request: SearchRequest):
    """Search Amazon.in and return structured product results."""
    if not browser_manager.is_running:
        raise HTTPException(status_code=400, detail="Browser is not running. Start it first.")

    try:
        products = await search_amazon(request.query, request.max_results)
        return ProductSearchResponse(
            query=request.query,
            source="Amazon",
            total=len(products),
            products=products,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Amazon search failed: {e}")


@router.post("/flipkart/search", response_model=ProductSearchResponse)
async def flipkart_search(request: SearchRequest):
    """Search Flipkart and return structured product results."""
    if not browser_manager.is_running:
        raise HTTPException(status_code=400, detail="Browser is not running. Start it first.")

    try:
        products = await search_flipkart(request.query, request.max_results)
        return ProductSearchResponse(
            query=request.query,
            source="Flipkart",
            total=len(products),
            products=products,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flipkart search failed: {e}")
