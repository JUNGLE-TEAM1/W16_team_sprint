# 15. Context Budget Rule

Context Budget controls how much project context an AI agent should load before acting.

## Lite Read

Use for small, ordinary feature, fix, docs, test, or status work.

Read:

- `AGENTS.md`
- `docs/00-layer-map.md`
- current workspace status when a workspace exists
- 1-3 directly relevant source, test, or Source of Truth files

## Escalate Read

Escalate when the work affects:

- API, schema, data model, auth, permissions, privacy, or secrets
- RAG, LLM, MCP, Realtime, or external-service behavior
- acceptance, regression, or manual verification paths
- Git sync, PR readiness, integration, or merge risk
- TDD, CI, build, deploy, migration, smoke, or rollback gates
- conflicts between code, README, architecture, and reports

Read only the extra files required by the risk.

## Audit Read

Use for:

- Existing Codebase Adoption
- whole-project review
- broad risk analysis
- migration planning
- harness evaluation

For this project, Bounded Audit Read starts with repo structure, `README.md`, `docs/02-architecture.md`, `docker-compose.yml`, backend requirements/tests, frontend package/build config, and key source directories by summary.

## Reporting Rule

Workspace reports and baseline reports should record:

- Context Budget mode
- primary context read
- escalated context read
- context intentionally omitted
