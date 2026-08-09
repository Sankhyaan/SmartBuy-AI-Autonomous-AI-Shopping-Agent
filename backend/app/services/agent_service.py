"""
AgentService — the core business logic layer.

Phase 1: Returns a stub reply.
Phase 2: This class will be wired to a LangGraph stateful agent graph,
         Playwright browser sessions, and MCP tool calls.
Phase 3: Adds RAG (Google/Web Search) and PostgreSQL session persistence.
"""


class AgentService:
    """
    Orchestrates agent behaviour.
    All AI logic will live here — routes stay thin.
    """

    def __init__(self):
        # Phase 2: initialise LangGraph graph here
        # Phase 3: initialise DB session, vector store here
        pass

    async def process_message(self, message: str) -> str:
        """
        Process a user message and return the agent reply.

        Args:
            message: The raw user input string.

        Returns:
            A string reply from the agent.
        """
        # TODO (Phase 2): Replace with LangGraph agent invocation
        return "Coming Soon"


# Module-level singleton — avoids re-instantiation on every request
agent_service = AgentService()
