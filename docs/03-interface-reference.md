# 03. Interface Reference

This is the baseline interface reference for the existing codebase. It records known interface surfaces at a summary level. Expand it before API, schema, protocol, or UI contract-heavy work.

## Frontend / Backend Boundary

Frontend runs on Vite and calls the FastAPI backend using `VITE_API_BASE_URL`.

Default local endpoints:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

## Known API Areas

From current docs and code structure, the backend exposes these functional areas:

- auth: register and login
- posts: create, list, detail, update title, delete
- comments: create and list comments for posts
- search/list filters: pagination, keyword search, tag filter
- AI discussion stream: post-context AI discussion over SSE
- Realtime voice discussion: session, message, and WebRTC support endpoints

Before changing route paths, payloads, response shapes, auth behavior, streaming format, or Realtime protocol behavior, inspect `backend/app/main.py` and `backend/app/schemas.py` and update this document with the exact contract.

## Data Contract Areas

Primary schemas and models live in:

- `backend/app/schemas.py`
- `backend/app/models.py`

Important persisted entities:

- user
- post
- comment
- annals article
- annals chunk
- voice session
- voice message

## AI / Tool Interfaces

- Embeddings use OpenAI embedding settings from environment.
- LLM summary, interpretation, discussion, rerank, and routing behavior lives under `backend/app/services/llm.py` and related service modules.
- MCP article lookup is exposed by `backend/app/mcp_server.py` and consumed by `backend/app/services/mcp_client.py`.
- Realtime voice flow uses OpenAI Realtime API and WebRTC.

## Environment Interface

Key environment variables:

- `DATABASE_URL`
- `ANNALS_XML_DIR`
- `ANNALS_PRIVATE_BUNDLE_ZIP`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_EMBEDDING_DIMENSIONS`
- `OPENAI_REALTIME_MODEL`
- `OPENAI_REALTIME_VOICE`
- `VITE_API_BASE_URL`

## Interface Change Rule

When a change affects an interface:

1. Identify the route/schema/protocol/data boundary.
2. Add or update focused tests.
3. Update this document with the exact changed contract.
4. Update `docs/02-architecture.md` if the system flow changes.
