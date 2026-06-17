# 11. Git Sync Policy

This document keeps Git operations explicit during AI-assisted work.

## Core Policy

- Do not run `git pull`, `git merge`, `git rebase`, `git push`, PR creation, or PR merge without human confirmation.
- Do not switch branches when the worktree has unrelated changes unless the human accepts the risk.
- Prefer creating workspace files with `scripts/start-workflow.sh --no-checkout` when local state is dirty.
- Record start sync, mid-phase sync, pre-merge sync, and PR status in workspace `sync.md`.

## Current Baseline

Baseline adoption began from branch `tj2` at commit `728fc6918691b8992a45c6c1df665ff25c9c0903`.

Untracked local files existed before adoption:

- `.codex-run/`
- `frontend/tsconfig.node.tsbuildinfo`
- `frontend/tsconfig.tsbuildinfo`

These were not modified as part of harness adoption.

## Phase Start

Before branch-changing work, ask the human which path to use:

- continue on the current branch and create workspace files only
- create/switch to a new branch
- stash/commit unrelated local work first
- cancel or defer

## Pre-Merge

Before completion or PR readiness:

1. Check worktree status.
2. Confirm how to sync with the base branch.
3. Run required verification.
4. Record the result or approved deferral in `sync.md`.

## Why Confirmation Matters

Git sync operations can mix unrelated changes, rewrite local history, or publish incomplete work. The harness records and validates state, but the human decides when branch and remote state should change.
