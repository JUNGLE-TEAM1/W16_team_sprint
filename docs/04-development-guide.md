# 04. Development Guide

This document records project-specific development operations for the 조선왕조실록 AI 게시판.

## Run Commands

```bash
docker compose up --build
```

The compose stack starts:

- PostgreSQL + pgvector on `localhost:5432`
- FastAPI backend on `localhost:8000`
- Vite frontend on `localhost:5173`

Required runtime environment:

- `OPENAI_API_KEY` for AI features
- optional `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`, `OPENAI_EMBEDDING_DIMENSIONS`, `OPENAI_REALTIME_MODEL`, `OPENAI_REALTIME_VOICE`

## Local Checks

```bash
cd backend && pytest
cd frontend && npm install
cd frontend && npm run build
scripts/validate-harness.sh
```

Use focused backend tests when changing a service, route, parser, MCP client, Realtime orchestration, or query filtering behavior.

## Branch Strategy

Recommended branch types:

- `feature/[short-kebab-name]`
- `fix/[short-kebab-name]`
- `docs/[short-kebab-name]`
- `test/[short-kebab-name]`
- `chore/[short-kebab-name]`
- `hotfix/[short-kebab-name]`

Create a matching workspace with:

```bash
scripts/start-workflow.sh --no-checkout feature short-name "Human readable title"
```

Use `--no-checkout` when there are unrelated local changes. Use branch-changing options only after the human confirms the Git sync decision.

## Git Sync Rules

`docs/11-git-sync-policy.md` is the Source of Truth for pull, merge, rebase, push, and PR safety.

- Do not run pull, merge, rebase, push, PR creation, or deploy commands without human confirmation.
- Record base commit and sync status in workspace `sync.md`.
- Prefer PR-based integration when remote collaboration is involved.

## Test Strategy

- Backend unit/integration tests live in `backend/tests/`.
- Frontend build validation is `npm run build`.
- Docker smoke validation is `docker compose up --build` followed by checking frontend/backend availability.
- TDD is expected for core logic, bug fixes, RAG/agent behavior, API contracts, and regression-prone work.
- Documentation-only harness edits can skip TDD when the skip reason is recorded.

## Secret And Data Rules

- Do not commit real API keys, private credentials, or production secrets.
- Treat `data/annals_private_bundle.zip` and private XML/data bundles as sensitive project data.
- Do not alter seed/import/export data flows without a clear migration or rollback note.

## Generated Files To Avoid

Do not treat these as source changes unless the user specifically asks:

- `.codex-run/`
- `.pytest_cache/`
- `__pycache__/`
- `frontend/tsconfig*.tsbuildinfo`
- local database volumes or build artifacts
