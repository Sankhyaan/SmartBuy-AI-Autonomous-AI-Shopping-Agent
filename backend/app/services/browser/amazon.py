"""
Amazon product search and extraction.

Uses Playwright to navigate Amazon.in search results,
scroll to load lazy images, and extract structured product data.
"""

import urllib.parse
from typing import List

from app.models.schemas import ProductItem
from app.services.browser.browser_manager import browser_manager
from app.services.browser.base_scraper import smooth_scroll, safe_text, safe_attribute

AMAZON_SEARCH_URL = "https://www.amazon.in/s?k={query}"


async def search_amazon(query: str, max_results: int = 10) -> List[ProductItem]:
    """
    Search Amazon.in for a query and return structured product results.

    Args:
        query: Search term (e.g. "wireless headphones").
        max_results: Cap on number of products to return.

    Returns:
        A list of ProductItem dicts extracted from search results.
    """
    page = await browser_manager.get_page()

    encoded = urllib.parse.quote_plus(query)
    url = AMAZON_SEARCH_URL.format(query=encoded)

    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await smooth_scroll(page, scrolls=4, distance=700)

    products: List[ProductItem] = []

    # Main search result cards
    cards = await page.query_selector_all(
        "div[data-component-type='s-search-result']"
    )

    for card in cards[:max_results]:
        try:
            # Title
            title = await safe_text(card, "h2 span")
            if not title:
                continue

            # Price — try whole price element first, then fallback
            price = await safe_text(card, "span.a-price > span.a-offscreen")
            if not price:
                price = await safe_text(card, "span.a-price-whole")
                if price:
                    fraction = await safe_text(card, "span.a-price-fraction") or ""
                    price = f"₹{price}.{fraction}"
                else:
                    price = "N/A"

            # Rating
            rating = await safe_attribute(card, "span.a-icon-alt", "textContent")
            if not rating:
                icon = await card.query_selector("span.a-icon-alt")
                if icon:
                    rating = await icon.text_content()
                    rating = rating.strip() if rating else None

            # Rating count
            rating_count = await safe_text(card, "span.a-size-base.s-underline-text")
            if not rating_count:
                rating_count = await safe_text(card, "a > span.a-size-base")

            # URL
            link = await safe_attribute(card, "h2 a.a-link-normal", "href")
            product_url = f"https://www.amazon.in{link}" if link and link.startswith("/") else link or ""

            # Image
            image_url = await safe_attribute(card, "img.s-image", "src")

            products.append(ProductItem(
                title=title,
                price=price,
                rating=rating,
                rating_count=rating_count,
                url=product_url,
                image_url=image_url,
                source="Amazon",
            ))

        except Exception:
            # Skip any malformed card
            continue

    return products
