# AGENTS.md

AI agents working in this repository must preserve the current application behavior and use the collaboration harness as an operating layer, not as a reason to rewrite the project.

## Project

**조선왕조실록 AI 게시판** - 조선왕조실록 XML 원문을 PostgreSQL/pgvector에 저장하고, RAG와 OpenAI 기반 초벌 요약/해석, 댓글 토론, AI 토론 도우미, Realtime 음성 토론을 제공하는 FastAPI + React 웹 애플리케이션.

## Source Of Truth

0. Layer Map: `docs/00-layer-map.md`
1. Requirements / external summary: `README.md`
2. Product planning: `docs/01-product-planning.md`
3. Architecture: `docs/02-architecture.md`
4. Interface reference: `docs/03-interface-reference.md`
5. Development operations: `docs/04-development-guide.md`
6. Workflow: `docs/08-development-workflow.md`
7. Git sync policy: `docs/11-git-sync-policy.md`
8. Quality gates: `docs/12-quality-gates.md`
9. Context budget rule: `docs/15-context-budget-rule.md`
10. Existing codebase adoption: `docs/16-existing-codebase-adoption.md`
11. Branch workspaces: `docs/workflows/`
12. Evidence reports: `docs/reports/`

Missing acceptance, regression, and manual-verification documents should be recorded as gaps until they are intentionally created. Do not silently treat missing harness documents as complete.

## Tech Stack

- Frontend: React, Vite, lucide-react
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL, pgvector
- AI: OpenAI API, embeddings, RAG, MCP article lookup, Realtime API
- Local orchestration: Docker Compose

## Work Rules

1. Use Existing Codebase Adoption for this repository: record the current state as baseline evidence, then manage future changes with branch workspaces.
2. Do not create retroactive workspaces for completed historical work.
3. Keep runtime code changes scoped to the user request. Harness adoption alone should not alter app behavior.
4. Read `docs/00-layer-map.md` before deciding which project documents are relevant.
5. Start with Lite Read for small work, Escalate Read for contracts/data/security/quality/sync risk, and Audit Read for baseline adoption or whole-project review.
6. Use `scripts/start-workflow.sh --no-checkout` when the worktree has unrelated local changes.
7. Do not pull, merge, rebase, push, create PRs, or deploy without explicit human confirmation.
8. Use TDD or focused regression tests for core logic, bug fixes, and integration contracts.
9. Record verification evidence in workspace `quality.md` and summarize it in `report.md`.
10. Do not commit secrets, API keys, real credentials, private data bundles, or generated caches.

## Current Commands

```bash
docker compose up --build
cd backend && pytest
cd frontend && npm install
cd frontend && npm run build
scripts/validate-harness.sh
```

## Avoid

- Replacing existing README or architecture docs during harness adoption.
- Expanding documentation work beyond what the current change needs.
- Treating generated files such as `.pytest_cache`, `__pycache__`, `tsconfig*.tsbuildinfo`, or `.codex-run/` as source artifacts.
- Running destructive database, Git, deploy, or private bundle operations without a clear user request.
