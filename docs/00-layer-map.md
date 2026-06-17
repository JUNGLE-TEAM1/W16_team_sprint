# 00. Layer Map

This document maps the collaboration harness layers to the current project files. It is a routing guide for change propagation, not a command to edit every document for every change.

## Layer Mapping

| Layer | Role | Current Files |
| --- | --- | --- |
| Requirements | Product purpose, user problem, current feature list | `README.md` |
| Product | Product scope, non-goals, success criteria | `docs/01-product-planning.md` |
| Architecture | System boundaries, data flow, components, deployment shape | `docs/02-architecture.md` |
| Interface | API, schema, protocol, UI contract references | `docs/03-interface-reference.md` |
| Development Operations | run, test, branch, environment, migration, secret rules | `docs/04-development-guide.md` |
| Acceptance | golden paths and acceptance checklist | Gap: create `docs/05-acceptance-scenarios-and-checklist.md` before larger feature phases |
| Regression | regression guards, failure scenarios, rollback concerns | Gap: create `docs/06-regression-and-failure-scenarios.md` before risky fixes/features |
| Manual Verification | step-by-step human verification playbooks | Gap: create `docs/07-manual-verification-playbook.md` or `docs/manual-verification/` when manual QA paths are needed |
| Workflow | phase/workspace process and completion criteria | `docs/08-development-workflow.md` |
| Git Sync Policy | branch freshness, PR, and Git safety rules | `docs/11-git-sync-policy.md` |
| Quality Gates | TDD, local checks, CI/CD evidence rules | `docs/12-quality-gates.md` |
| Context Budget Rule | Lite/Escalate/Audit read modes | `docs/15-context-budget-rule.md` |
| Existing Codebase Adoption | baseline + next-change adoption mode | `docs/16-existing-codebase-adoption.md` |
| Branch Workspaces | branch-specific working state | `docs/workflows/` |
| Evidence | baseline, phase, hotfix reports | `docs/reports/` |
| External Summary | concise project summary | `README.md` |

## Change Propagation Paths

| Change Type | Start Here | Then Check |
| --- | --- | --- |
| Requirements or feature scope | `README.md` or future product doc | Architecture, interface, acceptance, regression, workflow |
| Architecture or data flow | `docs/02-architecture.md` | Interface, acceptance, regression, manual verification |
| API/schema/protocol/UI contract | Interface doc if present, otherwise code + architecture | Tests, acceptance, regression |
| Backend behavior | relevant `backend/app/` module | backend tests, architecture/interface docs if contracts changed |
| Frontend behavior | `frontend/src/main.jsx`, `frontend/src/styles.css` | build, manual verification, architecture if flow changed |
| RAG/LLM/MCP behavior | `backend/app/services/`, `backend/app/mcp_server.py` | tests, architecture, quality gates |
| Development operations | `docker-compose.yml`, Dockerfiles, requirements/package files | development guide, quality gates |
| Harness/workflow change | harness docs/scripts | baseline or phase report |

## Context Loading Paths

- Small fix: `AGENTS.md`, this file, directly relevant source/test files.
- Feature or integration work: add `README.md`, `docs/02-architecture.md`, and a branch workspace.
- API/data/security/AI workflow changes: Escalate Read to related models, schemas, services, tests, and docs.
- Harness adoption or whole-project status: Audit Read using repo structure, README, architecture, package/build/test config, and selected key modules.

## Baseline Note

This repository already had meaningful code, docs, Docker setup, and tests before the harness was added. Current code and existing docs are baseline evidence until a future change intentionally updates Source of Truth documents.
