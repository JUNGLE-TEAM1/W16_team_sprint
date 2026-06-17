# 16. Existing Codebase Adoption

This repository already had meaningful code, tests, Docker configuration, and documentation before the collaboration harness was added.

## Strategy

Use:

```text
baseline + next-change adoption
```

First record the current project state as baseline evidence. Then use normal branch workspaces for future changes.

## Rules

- Do not rewrite existing project structure to fit the harness.
- Do not create retroactive workspaces for old features.
- Existing code and docs are baseline evidence until a future change updates Source of Truth.
- Mark missing docs as gaps rather than pretending they are complete.
- Preserve existing README and architecture docs.
- Add only the minimal harness documents and scripts needed to guide future work.

## Minimal Adoption Set

- `AGENTS.md`
- `docs/00-layer-map.md`
- `docs/04-development-guide.md`
- `docs/08-development-workflow.md`
- `docs/11-git-sync-policy.md`
- `docs/12-quality-gates.md`
- `docs/15-context-budget-rule.md`
- `docs/16-existing-codebase-adoption.md`
- `docs/workflows/README.md`
- `docs/reports/_template.md`
- `scripts/start-workflow.sh`
- `scripts/status-workflow.sh`
- `scripts/validate-harness.sh`

## Baseline Report Requirements

The baseline report should record:

- project name
- current base commit
- current run, build, and test commands
- existing CI/CD/PR/branch rules
- key directories and modules
- known risks
- missing or stale docs
- what was intentionally not backfilled
- recommended next-change workflow

## Exit Criteria

- Baseline report exists.
- Layer Map connects current docs/code to harness layers.
- Run/test/build commands are recorded.
- Existing Git/CI policy is recorded or explicitly absent.
- Missing docs are marked as gaps.
- Future changes can start with `scripts/start-workflow.sh --no-checkout`.
