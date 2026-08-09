"""
Uvicorn entry point.

Run with: python run.py
"""

import sys
import asyncio
import uvicorn

if __name__ == "__main__":
    # On Windows, async Playwright subprocesses require the ProactorEventLoop.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,          # Disable reload to avoid loop policy reset on spawn
        loop="asyncio",        # Force uvicorn to use standard loop policy
        log_level="info",
    )
