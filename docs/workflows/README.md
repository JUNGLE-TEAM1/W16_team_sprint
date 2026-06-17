# Branch Workspaces

This folder stores future branch-specific collaboration state.

The shared process lives in `docs/08-development-workflow.md`.

## Naming

```text
docs/workflows/<branch-type>/<short-kebab-name>/
```

Examples:

- `docs/workflows/feature/tag-filter/`
- `docs/workflows/fix/realtime-session-timeout/`
- `docs/workflows/docs/interface-reference/`

## Generated Files

Use:

```bash
scripts/start-workflow.sh --no-checkout feature tag-filter "Tag filter refinement"
```

Each workspace contains:

- `plan.md`
- `notes.md`
- `report.md`
- `quality.md`
- `decisions.md`
- `shared-docs.md`
- `sources.md`
- `confirmations.md`
- `next-actions.md`
- `sync.md`

## Status

```bash
scripts/status-workflow.sh docs/workflows/feature/tag-filter
```

The status output is a summary entry point. It does not replace reading Source of Truth files when behavior, contract, data, or quality risk is involved.
