"""
Chat router — HTTP interface for the agent.

Keeps routes thin: validation is done by Pydantic, logic lives in AgentService.
"""

import time
from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse
from app.services.agent_service import agent_service

router = APIRouter()

@router.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint — confirms the backend is running."""
    return HealthResponse(status="Shopping Agent Backend Running")


@router.get("/health", tags=["Health"])
async def detailed_health():
    """Detailed health check endpoint returning system status and timestamp."""
    return {
        "status": "healthy",
        "version": "0.2.0",
        "timestamp": time.time(),
        "services": ["fastapi", "playwright"]
    }


@router.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat(request: ChatRequest):
    """
    Accept a user message and return the agent reply.

    Phase 1: Returns a stub reply.
    Phase 2: Streams LangGraph agent responses.
    """
    reply = await agent_service.process_message(request.message)
    return ChatResponse(reply=reply)
