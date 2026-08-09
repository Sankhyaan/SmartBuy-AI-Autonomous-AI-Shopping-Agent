# Project Architecture

## Phase 1 — Foundation

```
User (Browser)
    │
    ▼
React SPA (Vite + Tailwind)
    │  POST /chat
    ▼
FastAPI Backend
    │
    ├─ routes/chat.py      ← HTTP layer
    ├─ services/agent_service.py  ← Business logic (stub)
    └─ models/schemas.py   ← Pydantic contracts
```

## Phase 2 — Agent Core (Planned)

Adds:
- **LangGraph** stateful agent loop inside `agent_service.py`
- **MCP** (Model Context Protocol) tool calls
- **Playwright** browser automation (browser panel becomes live)
- Agent reasoning stream → displayed in Reasoning Panel

## Phase 3 — Intelligence Layer (Planned)

Adds:
- **RAG** using Google/Web Search for product research
- **PostgreSQL** for session history, product cache, user preferences
- Full agentic shopping loop: search → compare → recommend → buy

---

## Key Design Decisions

### Scalable Service Layer
`agent_service.py` is a class stub in Phase 1. In Phase 2 it becomes
the LangGraph orchestrator — zero changes required to routes or schemas.

### Environment-Driven Config
All URLs, origins, and secrets live in `.env` files.
`pydantic-settings` validates and exposes them — easy to extend.

### CORS Pre-configured
CORS origins are set from env so moving from dev → staging → prod
requires only `.env` changes, not code changes.

### Pydantic Contracts First
`schemas.py` defines request/response shapes before logic exists.
This enforces clean API contracts from day one.
