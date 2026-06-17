# 08. Development Workflow

This repository uses the collaboration harness in Existing Codebase Adoption mode first, then normal phase work for future changes.

## Adoption Mode

Current mode:

```text
baseline + next-change adoption
```

Do not create retroactive workspaces for old work. Keep the baseline report as evidence of the current project state, then create one workspace per future feature, fix, docs, test, chore, or hotfix branch.

## Standard Start

1. Read `AGENTS.md`.
2. Read `docs/00-layer-map.md`.
3. Choose Context Budget mode from `docs/15-context-budget-rule.md`.
4. Read only directly relevant Source of Truth and source/test files.
5. Create or open `docs/workflows/<type>/<short-kebab-name>/`.
6. Record scope, sync, quality, decisions, and next action in the workspace.
7. Implement only the accepted scope.
8. Run agreed verification.
9. Update docs only when behavior, contracts, operations, or verification paths changed.
10. Write or update the workspace report.

## Workspace Commands

Preview:

```bash
scripts/start-workflow.sh --dry-run feature example "Example feature"
```

Create files without switching branches:

```bash
scripts/start-workflow.sh --no-checkout feature example "Example feature"
```

Summarize:

```bash
scripts/status-workflow.sh docs/workflows/feature/example
```

Validate harness files:

```bash
scripts/validate-harness.sh
scripts/validate-harness.sh --strict
```

## Quality Gate

Use `docs/12-quality-gates.md`.

- Documentation-only changes: harness validation is usually enough.
- Backend behavior: run focused `pytest` or the full backend suite.
- Frontend behavior: run `npm run build` and browser/manual verification when UI changed.
- RAG/LLM/MCP/Realtime changes: run focused service tests and document any OpenAI-dependent checks or skips.

## Completion Criteria

- Scope completed or explicitly deferred.
- Base commit and sync status recorded.
- Tests/build/manual checks run or skipped with a reason.
- User-visible or contract changes reflected in Source of Truth docs.
- No secrets or generated caches added intentionally.
- Report records changed, verified, remaining risk, and next context.
