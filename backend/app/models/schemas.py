"""
Pydantic schemas for all API request and response contracts.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message to the agent")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Agent reply")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Backend health status")


# ── Browser & Product Automation Schemas ──────────────────────────────────────

class ProductItem(BaseModel):
    title: str = Field(..., description="Product title")
    price: str = Field("N/A", description="Product price string")
    rating: Optional[str] = Field(None, description="Product rating e.g. 4.5 out of 5 stars")
    rating_count: Optional[str] = Field(None, description="Number of ratings e.g. 1,234 ratings")
    url: str = Field(..., description="Direct link to product page")
    image_url: Optional[str] = Field(None, description="Thumbnail image URL")
    source: str = Field(..., description="Platform e.g. Amazon, Flipkart")


class ProductSearchResponse(BaseModel):
    query: str = Field(..., description="Search query string")
    source: str = Field(..., description="Search engine/store used")
    total: int = Field(..., description="Number of products returned")
    products: List[ProductItem] = Field([], description="List of extracted products")


class BrowserStatusResponse(BaseModel):
    is_running: bool = Field(..., description="Whether the Playwright browser is active")
    current_url: Optional[str] = Field(None, description="Currently loaded page URL")
    title: Optional[str] = Field(None, description="Currently loaded page title")


class OpenUrlRequest(BaseModel):
    url: str = Field(..., description="URL to navigate to")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search term e.g. wireless headphones")
    max_results: int = Field(10, ge=1, le=30, description="Max products to return")


class ScreenshotResponse(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded PNG image data")
    current_url: str = Field(..., description="URL at the time of screenshot")


class ScrollRequest(BaseModel):
    direction: str = Field("down", description="Scroll direction: 'up' or 'down'")
    amount: int = Field(500, description="Pixels to scroll")
