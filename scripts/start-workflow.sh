#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/start-workflow.sh [--dry-run] [--no-checkout] [--allow-dirty] <type> <short-kebab-name> "<title>"

Examples:
  scripts/start-workflow.sh feature task-board "Task board MVP"
  scripts/start-workflow.sh --dry-run docs workflow-automation "Workflow automation"
  scripts/start-workflow.sh --no-checkout fix invalid-task-title "Invalid task title handling"

Allowed types:
  feature, fix, docs, test, chore, hotfix
USAGE
}

dry_run=0
checkout=1
allow_dirty=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      dry_run=1
      shift
      ;;
    --no-checkout)
      checkout=0
      shift
      ;;
    --allow-dirty)
      allow_dirty=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -ne 3 ]]; then
  usage
  exit 1
fi

branch_type="$1"
branch_slug="$2"
title="$3"
branch_name="${branch_type}/${branch_slug}"
workspace_dir="docs/workflows/${branch_type}/${branch_slug}"
main_branch="main"

case "$branch_type" in
  feature|fix|docs|test|chore|hotfix) ;;
  *)
    echo "Invalid branch type: ${branch_type}" >&2
    usage
    exit 1
    ;;
esac

if [[ ! "$branch_slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "Invalid branch slug: ${branch_slug}" >&2
  echo "Use lowercase kebab-case, for example: task-board or workflow-automation" >&2
  exit 1
fi

if [[ "$title" =~ [[:cntrl:]] ]]; then
  echo "Invalid title: control characters are not allowed" >&2
  exit 1
fi

echo "Branch: ${branch_name}"
echo "Workspace: ${workspace_dir}"
echo "Title: ${title}"

if [[ "$dry_run" -eq 1 ]]; then
  echo "Dry run only. No branch or files created."
  exit 0
fi

if [[ "$checkout" -eq 1 ]] && ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Cannot create or switch branches outside a Git worktree." >&2
  echo "Use --no-checkout to generate workflow files without Git branch operations." >&2
  exit 1
fi

if [[ "$checkout" -eq 1 ]] && [[ "$allow_dirty" -ne 1 ]] && ! git diff --quiet; then
  echo "Refusing to switch branches with unstaged changes." >&2
  echo "Commit, stash, or rerun with --no-checkout / --allow-dirty." >&2
  exit 1
fi

if [[ "$checkout" -eq 1 ]] && [[ "$allow_dirty" -ne 1 ]] && [[ -n "$(git status --porcelain --untracked-files=normal)" ]]; then
  echo "Refusing to switch branches with uncommitted or untracked changes." >&2
  echo "Commit, stash, or rerun with --no-checkout / --allow-dirty." >&2
  exit 1
fi

if [[ "$checkout" -eq 1 ]]; then
  if git rev-parse --verify --quiet "$branch_name" >/dev/null; then
    git switch "$branch_name"
  else
    git switch -c "$branch_name"
  fi
fi

mkdir -p "$workspace_dir"

current_branch="not a git worktree"
base_commit="unavailable"
sync_result="Git sync not performed by start-workflow.sh; record approved pull/merge/rebase results here."

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  current_branch="$(git branch --show-current 2>/dev/null || echo detached)"
  base_commit="$(git rev-parse --short HEAD 2>/dev/null || echo unborn)"
  sync_result="Workspace created from ${current_branch} at ${base_commit}; no pull/merge/rebase was run automatically."
fi

if [[ ! -f "${workspace_dir}/plan.md" ]]; then
  cat > "${workspace_dir}/plan.md" <<EOF_PLAN
# ${title} Plan

## Branch

- Branch: \`${branch_name}\`
- Workspace: \`${workspace_dir}\`
- Created: $(date +%Y-%m-%d)

## Goal

- 

## Scope

- 

## Out Of Scope

- 

## Source Of Truth Context

- \`AGENTS.md\`
- \`docs/00-layer-map.md\`
- \`docs/04-development-guide.md\`
- \`docs/08-development-workflow.md\`
- \`docs/12-quality-gates.md\`
- \`docs/15-context-budget-rule.md\`

## Implementation Prompt

\`\`\`text
@AGENTS.md @docs/00-layer-map.md @docs/04-development-guide.md @docs/08-development-workflow.md @docs/12-quality-gates.md @docs/15-context-budget-rule.md

Implement only the work described in this branch workspace.
Start with Lite Read and escalate only when risk signals require more context.
Use TDD when the branch changes core logic, regression risk, integration contracts, or bug fixes.
For high-impact choices, record options and the accepted decision in \`decisions.md\` before implementation.
Do not expand scope without updating this plan.
\`\`\`

## Verification Prompt

\`\`\`text
@AGENTS.md @docs/00-layer-map.md @docs/04-development-guide.md @docs/12-quality-gates.md

Verify the branch work and record evidence in \`quality.md\` and this workspace report. If the change needs acceptance, regression, or manual verification docs that do not exist yet, record that gap and propose the smallest useful doc update.
\`\`\`

## Completion Criteria

- [ ] Scope completed
- [ ] TDD status recorded
- [ ] Acceptance checked
- [ ] Regression/failure scenario checked
- [ ] Manual verification recorded
- [ ] CI/check commands recorded
- [ ] Report updated
EOF_PLAN
fi

if [[ ! -f "${workspace_dir}/notes.md" ]]; then
  cat > "${workspace_dir}/notes.md" <<EOF_NOTES
# ${title} Notes

## Running Notes

- 

## Decisions

- 

## Open Questions

- 

## Links / Evidence

- 
EOF_NOTES
fi

if [[ ! -f "${workspace_dir}/report.md" ]]; then
  cat > "${workspace_dir}/report.md" <<EOF_REPORT
# ${title} Report

## Short Report

- Type: ${branch_type}
- Branch/work location: \`${branch_name}\`, \`${workspace_dir}\`
- Date: $(date +%Y-%m-%d)
- Workspace state: draft
- Context Budget mode: Lite Read
- Primary context read:
- Escalated context read:
- Context omitted intentionally:
- Changed:
- Verified:
- Remaining:
- Next context:
- Risk:
EOF_REPORT
fi

if [[ ! -f "${workspace_dir}/quality.md" ]]; then
  cat > "${workspace_dir}/quality.md" <<EOF_QUALITY
# ${title} Quality Gates

Use this file to record TDD and CI/CD evidence for this branch.

- Quality gate status: draft

## TDD Plan

- Applies: TBD
- Reason:
- Failing test first:
- Expected failure command/result:
- Pass command/result:
- Refactor notes:

## Branch Checks

| Check | Command | Result | Evidence |
| --- | --- | --- | --- |
| lint |  |  |  |
| unit/focused test |  |  |  |
| integration/contract test |  |  |  |
| build/typecheck |  |  |  |
| harness validation | \`scripts/validate-harness.sh\` |  |  |
| strict harness validation | \`scripts/validate-harness.sh --strict\` |  |  |

## CI/CD Gate

- CI required: TBD
- CI result:
- Deploy/publish required: no
- Deployment confirmation:
- Rollback/smoke notes:

## Skipped Checks

| Check | Reason | Human Confirmed |
| --- | --- | --- |
|  |  |  |
EOF_QUALITY
fi

if [[ ! -f "${workspace_dir}/decisions.md" ]]; then
  cat > "${workspace_dir}/decisions.md" <<EOF_DECISIONS
# ${title} Decisions

Use this file to record high-impact choices and their outcomes.
For high-impact choices, compare options, record the selected option, and include revisit or rollback conditions.

- Decision status: none

## Decision Option Briefs

- 

## Accepted Decisions

| Decision | Selected Option | Reason | Confirmed By / At |
| --- | --- | --- | --- |
|  |  |  |  |

## Deferred Decisions

| Decision | Deferred Reason | Revisit Trigger | Target Branch / Phase |
| --- | --- | --- | --- |
|  |  |  |  |

## Revisit / Rollback Conditions

| Decision | Condition | Action |
| --- | --- | --- |
|  |  |  |
EOF_DECISIONS
fi

echo "Created or confirmed workflow files:"
echo "- ${workspace_dir}/plan.md"
echo "- ${workspace_dir}/notes.md"
if [[ ! -f "${workspace_dir}/shared-docs.md" ]]; then
  cat > "${workspace_dir}/shared-docs.md" <<EOF_SHARED
# ${title} Shared Document Patch Proposals

Use this file when branch work needs changes to shared Source of Truth documents.
Integration branches should read this file before merging branch work.

## Proposed Source Of Truth Changes

| File | Proposed Change | Reason | Merge Risk |
| --- | --- | --- | --- |
| \`README.md\` |  |  |  |
| \`docs/02-architecture.md\` |  |  |  |
| \`docs/04-development-guide.md\` |  |  |  |
| \`docs/12-quality-gates.md\` |  |  |  |
| New acceptance/regression/manual verification doc if needed |  |  |  |

## Integration Notes

- 

## Conflicts To Resolve

- 
EOF_SHARED
fi

if [[ ! -f "${workspace_dir}/sources.md" ]]; then
  cat > "${workspace_dir}/sources.md" <<EOF_SOURCES
# ${title} Source Branches

Use this file when this branch depends on or integrates other branch workspaces.

## Source Branch Workspaces

- 

## Required Source Files

For each source branch, read:

- \`plan.md\`
- \`shared-docs.md\`
- \`report.md\`
- \`quality.md\`
- \`decisions.md\`
- \`confirmations.md\`
- \`sync.md\`

## Source Branch Base Records

Record the Git point that each source branch was read from.

| Source Branch | Workspace | Base Commit | Read At | Notes |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Integration Notes

- 
EOF_SOURCES
fi

if [[ ! -f "${workspace_dir}/confirmations.md" ]]; then
  cat > "${workspace_dir}/confirmations.md" <<EOF_CONFIRM
# ${title} Human Confirmation Gates

Use this file to record when AI should stop and ask for human confirmation.

## Scope Confirm

- Status: pending
- Ask human to confirm:
  - branch/workspace
  - included scope
  - excluded scope
  - impacted Source of Truth docs
- Human response:

## Contract Confirm

- Status: pending
- Ask human to confirm:
  - data model changes
  - interface/API/CLI/UI contract changes
  - external dependencies
  - shared Source of Truth changes
- Human response:

## Scope Change Confirm

- Status: not needed
- Ask human when:
  - work expands beyond \`plan.md\`
  - a feature should move to another branch
  - implementation reveals a new product decision
- Human response:

## Verification Confirm

- Status: pending
- Ask human to confirm:
  - test/build/smoke commands
  - TDD evidence or skip reason
  - CI/check commands
  - manual verification path
  - completion criteria
- Human response:

## Quality Gate Confirm

- Status: pending
- Ask human to confirm:
  - TDD applies or is intentionally skipped
  - required branch checks and CI gates
  - skipped checks and reasons
  - deploy/publish gate if relevant
- Human response:

## Git Sync Confirm

- Status: pending
- Ask human to confirm:
  - start sync command/result before implementation
  - mid-phase upstream change action
  - pre-merge sync command/result before completion
- Human response:

## Sync Conflict Confirm

- Status: not needed
- Ask human when:
  - main changed during the Phase
  - shared Source of Truth docs conflict with this branch
  - merge/rebase/pull/push/PR action is needed
- Human response:

## Completion Confirm

- Status: pending
- Ask human to confirm:
  - changed summary
  - verification result
  - remaining risk
  - next task context
- Human response:

## Integration Conflict Confirm

- Status: not needed
- Ask human when:
  - this branch integrates multiple source branches
  - shared data model or interface conflicts exist
  - acceptance/regression/manual verification paths conflict
- Human response:
EOF_CONFIRM
fi

if [[ ! -f "${workspace_dir}/next-actions.md" ]]; then
  cat > "${workspace_dir}/next-actions.md" <<EOF_NEXT
# ${title} Next Action Menu

Use this file to guide the human through the next collaboration choice.

## Current State

- State: workspace created
- Summary: branch workspace exists, but scope still needs human confirmation.

## Recommended Next Action

- Ask for Scope Confirm.
- Reason: implementation should not start until branch/workspace, included scope, excluded scope, and impacted docs are clear.

## Options

1. Confirm scope and continue to Contract Confirm.
2. Revise scope before implementation.
3. Split part of the work into another branch.
4. Pause this workspace.

## Waiting On Human

- Please choose one option or give a natural language instruction.

## Last User Choice

- 

## Next AI Action

- If option 1 is chosen, update \`confirmations.md\`, then draft or confirm shared contracts.
- If option 2 is chosen, update \`plan.md\` and \`shared-docs.md\`.
- If option 3 is chosen, create another workspace with \`scripts/start-workflow.sh\`.
- If option 4 is chosen, record the pause reason in \`notes.md\`.
EOF_NEXT
fi

if [[ ! -f "${workspace_dir}/sync.md" ]]; then
  cat > "${workspace_dir}/sync.md" <<EOF_SYNC
# ${title} Git Sync

Use this file to record main synchronization and integration readiness.
Do not run pull, merge, rebase, push, or PR actions without human confirmation.

## Start Sync

- main branch: ${main_branch}
- current branch: ${current_branch}
- base commit: ${base_commit}
- pulled at:
- command:
- result: ${sync_result}

## Mid-Phase Sync Checks

| Checked At | Upstream Changes | Impacted Source of Truth | Action |
| --- | --- | --- | --- |
|  |  |  |  |

## Pre-Merge Sync

- main commit:
- conflicts:
- validation:
- result:
- deferral reason:

## Push / PR

- pushed branch:
- PR link:
- merge status:
EOF_SYNC
fi

echo "- ${workspace_dir}/report.md"
echo "- ${workspace_dir}/quality.md"
echo "- ${workspace_dir}/decisions.md"
echo "- ${workspace_dir}/shared-docs.md"
echo "- ${workspace_dir}/sources.md"
echo "- ${workspace_dir}/confirmations.md"
echo "- ${workspace_dir}/next-actions.md"
echo "- ${workspace_dir}/sync.md"
