# 12. Quality Gates

Quality gates are the verification language for this project. They should be scaled to the risk of the change.

## Core Policy

- Use TDD for backend core logic, bug fixes, regression-prone behavior, API/schema contracts, RAG/agent orchestration, MCP behavior, and Realtime flows.
- Documentation-only and low-risk mechanical edits may skip TDD when the reason is recorded.
- A branch is not ready until agreed checks are run or skipped with a clear reason.

## Project Checks

Backend:

```bash
cd backend && pytest
```

Frontend:

```bash
cd frontend && npm install
cd frontend && npm run build
```

Harness:

```bash
scripts/validate-harness.sh
scripts/validate-harness.sh --strict
```

Full local smoke:

```bash
docker compose up --build
```

## When To Escalate Verification

- API route, schema, or database model changes: run focused tests and update interface/architecture docs as needed.
- RAG, embeddings, search, rerank, MCP, or agent changes: run focused service tests and record OpenAI-dependent limitations.
- Realtime voice changes: run service tests and manual browser/microphone verification when feasible.
- Frontend UI changes: run build and browser/manual verification.
- Data import/export changes: include migration, rollback, or private bundle handling notes.

## Workspace Evidence

Each future workspace should record:

- quality gate status
- TDD applies or skip reason
- commands run
- results
- skipped checks and reasons
- remaining risk
- deploy/publish gate if relevant

Allowed quality statuses:

- `draft`
- `planned`
- `passed`
- `passed-with-skips`
- `deferred`
