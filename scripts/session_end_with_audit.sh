#!/usr/bin/env bash
# session_end_with_audit.sh — wrap `crosslink session end` with a
# pre-flight audit of `research` issues.
#
# Usage:
#   scripts/session_end_with_audit.sh --notes "..."
#   scripts/session_end_with_audit.sh --prompt
#   scripts/session_end_with_audit.sh --help
#
# What it does:
#   1. Runs scripts/audit_research_issues.py
#   2. Displays the audit output
#   3. If --notes or --prompt is used, appends an audit summary line to
#      the notes under a "---" separator
#   4. Calls `crosslink session end --notes "$NOTES"`
#
# This is advisory, not preventive. The audit reports violations but
# does not block session end. Pair with manual review of the violations
# in the next session's `session start` output.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_SCRIPT="$SCRIPT_DIR/audit_research_issues.py"
NOTES=""
PROMPT=false
JSON=false

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options:
  --notes "TEXT"   Use TEXT as the session-end notes. The audit summary
                   is appended under a "---" separator.
  --prompt         Read session-end notes from stdin (Ctrl-D to finish).
                   The audit summary is appended.
  --json           Pass --json to the audit script.
  -h, --help       Show this help.

The audit runs unconditionally. If no notes are provided, the audit
output is shown but not included in any session-end call.

Exit codes:
  0 — session end completed (audit may have found violations)
  1 — crosslink not on PATH, audit script missing, or session end failed
  2 — invalid arguments
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --notes) NOTES="$2"; shift 2 ;;
    --prompt) PROMPT=true; shift ;;
    --json) JSON=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if ! command -v crosslink >/dev/null 2>&1; then
  echo "ERROR: crosslink not on PATH" >&2
  exit 1
fi
if [[ ! -f "$AUDIT_SCRIPT" ]]; then
  echo "ERROR: audit script not found at $AUDIT_SCRIPT" >&2
  exit 1
fi

# Run the audit
audit_args=()
if [[ "$JSON" == true ]]; then
  audit_args+=(--json)
fi
audit_output="$(python3 "$AUDIT_SCRIPT" "${audit_args[@]}" 2>&1)" || audit_exit=$?
audit_exit="${audit_exit:-0}"

echo "$audit_output"
echo

# Optionally read notes from stdin
if [[ "$PROMPT" == true && -z "$NOTES" ]]; then
  echo "Enter session-end notes (Ctrl-D to finish):"
  NOTES="$(cat || true)"
fi

# Build a one-line summary for the notes (if not JSON)
if [[ "$JSON" == true ]]; then
  # Extract count from JSON
  count="$(echo "$audit_output" | python3 -c 'import sys, json; d=json.load(sys.stdin); print(d.get("count", 0))' 2>/dev/null || echo '?')"
  audit_summary="research-issue audit: $count violation(s)"
else
  if echo "$audit_output" | grep -q "VIOLATIONS:"; then
    count="$(echo "$audit_output" | grep -oE '[0-9]+ open' | head -1 | grep -oE '[0-9]+')"
    audit_summary="research-issue audit: ${count:-?} violation(s); see scripts/audit_research_issues.py"
  else
    audit_summary="research-issue audit: pass"
  fi
fi

# Append the audit summary to the notes if we have any
if [[ -n "$NOTES" || "$PROMPT" == true ]]; then
  if [[ -n "$NOTES" ]]; then
    NOTES="$NOTES

---
$audit_summary"
  else
    NOTES="---
$audit_summary"
  fi
fi

# Call crosslink session end
if [[ -n "$NOTES" ]]; then
  crosslink session end --notes "$NOTES"
else
  crosslink session end
fi
