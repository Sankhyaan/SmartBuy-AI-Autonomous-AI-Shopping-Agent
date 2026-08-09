"""
Flipkart product search and extraction.

Uses Playwright to navigate Flipkart search results,
scroll to load lazy images, and extract structured product data.
"""

import urllib.parse
from typing import List

from app.models.schemas import ProductItem
from app.services.browser.browser_manager import browser_manager
from app.services.browser.base_scraper import smooth_scroll, safe_text, safe_attribute

FLIPKART_SEARCH_URL = "https://www.flipkart.com/search?q={query}"


async def search_flipkart(query: str, max_results: int = 10) -> List[ProductItem]:
    """
    Search Flipkart for a query and return structured product results.

    Args:
        query: Search term.
        max_results: Cap on number of products to return.

    Returns:
        A list of ProductItem dicts extracted from search results.
    """
    page = await browser_manager.get_page()

    encoded = urllib.parse.quote_plus(query)
    url = FLIPKART_SEARCH_URL.format(query=encoded)

    await page.goto(url, wait_until="domcontentloaded", timeout=30000)

    # Close the login popup if it appears
    try:
        close_btn = await page.query_selector("button._2KpZ6l._2doB4z")
        if close_btn:
            await close_btn.click()
    except Exception:
        pass

    await smooth_scroll(page, scrolls=4, distance=700)

    products: List[ProductItem] = []

    # Use JS evaluation to robustly extract products based on text layout, ignoring fragile CSS classes
    products_data = await page.evaluate(f'''(max_results) => {{
        const links = Array.from(document.querySelectorAll('a[href*="/p/"]'));
        
        const containers = [];
        const seen = new Set();
        
        for (const a of links) {{
            let current = a;
            let foundContainer = a;
            // Traverse up to find a container that holds both the product image and text
            for(let i=0; i<6; i++) {{
                if(!current || current.tagName === 'BODY') break;
                if(current.querySelector('img') && current.innerText.length > 20) {{
                    foundContainer = current;
                    break;
                }}
                current = current.parentElement;
            }}
            
            if (!seen.has(foundContainer)) {{
                seen.add(foundContainer);
                containers.push({{ container: foundContainer, href: a.href }});
            }}
        }}

        return containers.slice(0, max_results).map(item => {{
            const c = item.container;
            const texts = c.innerText.split('\\n').map(t => t.trim()).filter(t => t.length > 0);
            
            // Title is usually one of the longest strings
            const title = texts.find(t => t.length > 15) || texts[0] || '';
            
            // Price usually has ₹. If multiple prices are smashed together, extract the first one
            let price = 'N/A';
            const priceStr = texts.find(t => t.includes('₹'));
            if (priceStr) {{
                const match = priceStr.match(/₹[0-9,]+/);
                price = match ? match[0] : priceStr;
            }}
            
            // Rating usually has ★ or matches a pattern like 3.9(11,828)
            let rating = '';
            let ratingCount = '';
            
            // Try to find a combined rating line like "3.9(11,828)" or "4.5★"
            const ratingLine = texts.find(t => t.match(/^[0-9](\.[0-9])?\([0-9,]+\)$/) || t.includes('★'));
            
            if (ratingLine) {{
                // If it matches 3.9(11,828)
                const match = ratingLine.match(/^([0-9](\.[0-9])?)\(([0-9,]+)\)$/);
                if (match) {{
                    rating = match[1];
                    ratingCount = match[3];
                }} else {{
                    // It has a star, so it might just be the rating
                    rating = ratingLine.replace('★', '').trim();
                }}
            }}
            
            // If ratingCount wasn't found in the combined line, try finding it standalone "(11,828)"
            if (!ratingCount) {{
                const ratingCountLine = texts.find(t => t.startsWith('(') && t.endsWith(')') && /[0-9]/.test(t));
                if (ratingCountLine) {{
                    ratingCount = ratingCountLine.replace(/[()]/g, '');
                }}
            }}
            
            // Image might be inside or nearby
            const img = c.querySelector('img');
            const image_url = img ? img.src : '';
            
            return {{
                url: item.href,
                title: title,
                price: price,
                rating: rating,
                rating_count: ratingCount,
                image_url: image_url
            }};
        }});
    }}''', max_results)
    
    for item in products_data:
        if not item.get('title'):
            continue
            
        products.append(ProductItem(
            title=item.get('title'),
            price=item.get('price'),
            rating=item.get('rating'),
            rating_count=item.get('rating_count'),
            url=item.get('url'),
            image_url=item.get('image_url'),
            source="Flipkart",
        ))

    return products
