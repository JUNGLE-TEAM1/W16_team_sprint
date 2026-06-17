# Baseline Existing Codebase Adoption Report

- Type: docs
- Date: 2026-06-17
- Branch/work location: `tj2`
- Workspace state: complete
- Context Budget mode: Audit Read

## Project

- Name: 조선왕조실록 AI 게시판
- Purpose: 조선왕조실록 원문 기반 RAG 검색, AI 초벌 요약/해석, 게시판 토론, AI 토론 도우미, Realtime 음성 토론을 제공하는 웹 애플리케이션.

## Baseline

- Base commit: `728fc6918691b8992a45c6c1df665ff25c9c0903`
- Existing branch: `tj2`
- Pre-existing untracked files observed:
  - `.codex-run/`
  - `frontend/tsconfig.node.tsbuildinfo`
  - `frontend/tsconfig.tsbuildinfo`

These pre-existing untracked files were not changed by harness adoption.

## Current Run / Build / Test Commands

```bash
docker compose up --build
cd backend && pytest
cd frontend && npm install
cd frontend && npm run build
scripts/validate-harness.sh
```

## Existing CI / CD / PR / Branch Rules

- CI configuration: none found under `.github/` during baseline scan.
- CD/deploy policy: not defined in existing docs.
- PR policy: not defined in existing docs.
- Branch policy: current repository branch observed as `tj2`; future branch guidance is now recorded in `docs/04-development-guide.md` and `docs/11-git-sync-policy.md`.

## Key Directories And Modules

- `frontend/`: React + Vite UI.
- `frontend/src/main.jsx`: main application and UI flow.
- `frontend/src/styles.css`: frontend styling.
- `backend/app/main.py`: FastAPI routes and application assembly.
- `backend/app/models.py`: SQLAlchemy models.
- `backend/app/schemas.py`: Pydantic schemas.
- `backend/app/services/`: search, embeddings, LLM, MCP client, agent workflow, Realtime orchestration, XML parsing, chunking, query filters.
- `backend/app/mcp_server.py`: MCP article lookup server.
- `backend/scripts/`: annals seed/import/export/private bundle helpers.
- `backend/tests/`: focused tests for search, MCP client, query filters, XML parser, LLM rerank, discussion stream, Realtime session/orchestrator.
- `data/`: private bundle and data README.
- `docs/02-architecture.md`: canonical harness architecture Source of Truth.
- `docker-compose.yml`: local Postgres/backend/frontend stack.

## Existing Docs Mapped

- `README.md` -> requirements, external summary, current feature inventory.
- `docs/01-product-planning.md` -> baseline product scope summarized from existing README and architecture docs.
- `docs/02-architecture.md` -> architecture, deployment, frontend/backend/data/AI flow.
- `docs/03-interface-reference.md` -> baseline interface surface summary.
- `data/README.md` -> data/private bundle context.

## Known Risks

- OpenAI-dependent behavior may require live credentials and can be difficult to fully verify in local automated tests.
- Realtime voice flows need browser/microphone and network verification beyond unit tests.
- CI is absent, so branch readiness currently depends on local commands.
- Interface, acceptance, regression, and manual verification docs are not yet separated from README/architecture/source tests.
- Private data bundle handling should remain careful to avoid committing sensitive or derived private material unintentionally.

## Missing Or Stale Docs

- `docs/05-acceptance-scenarios-and-checklist.md`: not present.
- `docs/06-regression-and-failure-scenarios.md`: not present.
- `docs/07-manual-verification-playbook.md`: not present.
- CI/PR template docs: not present.

These are gaps, not blockers for baseline adoption.

## Intentionally Not Backfilled

- No retroactive workspaces were created for existing features.
- Existing architecture content was moved into `docs/02-architecture.md` so the harness flow has one canonical architecture path.
- Runtime application code was not changed.
- CI/CD files were not invented during baseline adoption.
- Historical feature decisions were not reconstructed.

## Next-Change Adoption Plan

For the next real change:

1. Create a branch workspace with `scripts/start-workflow.sh --no-checkout <type> <slug> "<title>"`.
2. Start with Lite Read: `AGENTS.md`, `docs/00-layer-map.md`, workspace status, and directly relevant source/test/docs.
3. Escalate only for API/schema/data/security/AI/quality/Git-sync risk.
4. Record TDD/check commands in workspace `quality.md`.
5. Update Source of Truth docs only when behavior, contracts, operations, or verification paths change.
6. Summarize completion in workspace `report.md`.

## Verification

Baseline verification target:

```bash
scripts/validate-harness.sh
```

## Final Judgment

- Done: minimal collaboration harness applied for an existing codebase.
- Remaining risk: future high-risk work should add interface, acceptance, regression, and manual verification docs as needed rather than all at once.
