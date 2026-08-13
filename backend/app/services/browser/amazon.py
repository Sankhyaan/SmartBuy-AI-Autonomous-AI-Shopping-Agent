"""
Amazon product search and extraction.

Uses Playwright to navigate Amazon.in search results,
scroll to load lazy images, and extract structured product data.
"""

import urllib.parse
from typing import List

from app.models.schemas import ProductItem
from app.services.browser.browser_manager import browser_manager
from app.services.browser.base_scraper import (
    smooth_scroll, safe_text, safe_attribute,
    format_rating_out_of_5, clean_rating_count, clean_bought_past_month,
    parse_count_numeric_value
)

AMAZON_SEARCH_URL = "https://www.amazon.in/s?k={query}"


async def search_amazon(query: str, max_results: int = 50) -> List[ProductItem]:
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
    await smooth_scroll(page, scrolls=6, distance=700)

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
            raw_rating = await safe_attribute(card, "span.a-icon-alt", "textContent")
            if not raw_rating:
                icon = await card.query_selector("span.a-icon-alt")
                if icon:
                    raw_rating = await icon.text_content()
                    raw_rating = raw_rating.strip() if raw_rating else None

            rating = format_rating_out_of_5(raw_rating)

            # Rating count (e.g. (13.3K) or 13,311 or 11,828)
            rc_candidates = []
            rating_count_selectors = [
                "a[href*='#customerReviews'] span",
                "a[href*='customerReviews']",
                "span.s-underline-text",
                "span.a-size-base.s-underline-text",
                "a.s-underline-text"
            ]
            for sel in rating_count_selectors:
                try:
                    sub_elems = await card.query_selector_all(sel)
                    for sub in sub_elems:
                        txt = await sub.text_content()
                        if txt:
                            cleaned_rc = clean_rating_count(txt)
                            if cleaned_rc:
                                rc_candidates.append(cleaned_rc)
                except Exception:
                    pass

            # Select candidate with the highest numeric review count (e.g. 13.3K over 13)
            rating_count = max(rc_candidates, key=parse_count_numeric_value) if rc_candidates else None

            # Bought in past month
            bought_past_month = clean_bought_past_month(card_full_text)

            # URL
            link = await safe_attribute(card, "h2 a.a-link-normal", "href")
            if not link:
                link = await safe_attribute(card, "a.a-link-normal", "href")
            if not link:
                link = await safe_attribute(card, "a[href*='/dp/']", "href")

            if link:
                product_url = f"https://www.amazon.in{link}" if link.startswith("/") else link
            else:
                product_url = f"https://www.amazon.in/s?k={urllib.parse.quote_plus(title)}"

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
                bought_past_month=bought_past_month,
            ))

        except Exception:
            # Skip any malformed card
            continue

    return products
