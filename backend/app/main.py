"""
FastAPI application factory.

Configures middleware (CORS) and registers all route modules.
Add new routers here as the project scales across phases.
"""

import sys
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure Windows uses ProactorEventLoop for subprocesses inside the active loop
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
    yield
    # Clean up browser if left running
    try:
        from app.services.browser.browser_manager import browser_manager
        if browser_manager.is_running:
            await browser_manager.stop()
    except Exception:
        pass

from app.config.settings import settings
from app.routes.chat import router as chat_router
from app.routes.browser import router as browser_router

app = FastAPI(
    title="Shopping Agent API",
    description="Autonomous AI Shopping Agent — Phase 2 Browser Automation",
    version="0.2.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Origins are read from .env so switching environments requires no code changes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response




@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error": str(exc)},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(browser_router)
