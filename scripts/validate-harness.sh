#!/usr/bin/env bash
set -euo pipefail

failures=0
strict=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --strict)
      strict=1
      shift
      ;;
    --integration)
      strict=1
      shift
      ;;
    -h|--help)
      cat <<'USAGE'
Usage:
  scripts/validate-harness.sh [--strict] [--integration]

Default validation checks the minimal Existing Codebase Adoption harness files.
Strict validation also checks workspace structure and basic status fields when workspaces exist.
USAGE
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

fail() {
  echo "FAIL: $*" >&2
  failures=$((failures + 1))
}

require_file() {
  local file="$1"
  [[ -f "$file" ]] || fail "Missing file: ${file}"
}

field_value() {
  local file="$1"
  local label="$2"
  awk -v label="$label" '
    index($0, label) == 1 {
      value=$0
      sub(label "[ \t]*", "", value)
      gsub(/^[ \t]+|[ \t]+$/, "", value)
      print value
      exit
    }
  ' "$file"
}

require_file "AGENTS.md"
require_file "README.md"
require_file "docs/00-layer-map.md"
require_file "docs/01-product-planning.md"
require_file "docs/02-architecture.md"
require_file "docs/03-interface-reference.md"
require_file "docs/04-development-guide.md"
require_file "docs/08-development-workflow.md"
require_file "docs/11-git-sync-policy.md"
require_file "docs/12-quality-gates.md"
require_file "docs/15-context-budget-rule.md"
require_file "docs/16-existing-codebase-adoption.md"
require_file "docs/workflows/README.md"
require_file "docs/reports/README.md"
require_file "docs/reports/_template.md"
require_file "docs/reports/baseline-existing-codebase-adoption.md"
require_file "scripts/start-workflow.sh"
require_file "scripts/status-workflow.sh"

if [[ ! -x "scripts/start-workflow.sh" ]]; then
  fail "scripts/start-workflow.sh is not executable"
fi

if [[ ! -x "scripts/status-workflow.sh" ]]; then
  fail "scripts/status-workflow.sh is not executable"
fi

if ! rg -q "baseline \\+ next-change adoption" docs/16-existing-codebase-adoption.md docs/08-development-workflow.md; then
  fail "Existing Codebase Adoption strategy is not recorded"
fi

if ! rg -q "docs/02-architecture.md" docs/00-layer-map.md AGENTS.md; then
  fail "Canonical architecture doc is not mapped"
fi

while IFS= read -r -d '' dir; do
  require_file "${dir}/plan.md"
  require_file "${dir}/notes.md"
  require_file "${dir}/report.md"
  require_file "${dir}/quality.md"
  require_file "${dir}/decisions.md"
  require_file "${dir}/shared-docs.md"
  require_file "${dir}/sources.md"
  require_file "${dir}/confirmations.md"
  require_file "${dir}/next-actions.md"
  require_file "${dir}/sync.md"

  if [[ "$strict" -eq 1 ]]; then
    state="$(field_value "${dir}/report.md" "- Workspace state:")"
    q_status="$(field_value "${dir}/quality.md" "- Quality gate status:")"
    d_status="$(field_value "${dir}/decisions.md" "- Decision status:")"

    case "${state:-draft}" in
      draft|in-progress|ready-for-review|complete|integration-ready|archived) ;;
      *) fail "Invalid Workspace state '${state}' in ${dir}/report.md" ;;
    esac

    case "${q_status:-draft}" in
      draft|planned|passed|passed-with-skips|deferred) ;;
      *) fail "Invalid Quality gate status '${q_status}' in ${dir}/quality.md" ;;
    esac

    case "${d_status:-none}" in
      none|brief-needed|accepted|deferred|mixed) ;;
      *) fail "Invalid Decision status '${d_status}' in ${dir}/decisions.md" ;;
    esac
  fi
done < <(find docs/workflows -mindepth 2 -maxdepth 2 -type d -print0 2>/dev/null)

if [[ "$failures" -gt 0 ]]; then
  echo "Harness validation failed with ${failures} issue(s)." >&2
  exit 1
fi

echo "Harness validation passed."
