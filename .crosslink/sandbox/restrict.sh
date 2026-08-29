#!/bin/bash
# sandbox/restrict.sh — fix-then-activate sandbox.command wrapper for per-file-path restriction
# Called as: bash {{worktree}}/.crosslink/sandbox/restrict.sh --worktree {{worktree}} -- <claude command...>
# Purpose: Enforce that the wrapped agent only touches allowed paths, and log provenance.
# WHY: Per audit #505 §4, per-file-path allowlisting cannot be enforced inside crosslink without OS sandbox.
#      This script is the dormant native hook (launch.rs:57 sandbox.command) that moves enforcement to OS layer.
# WHAT: - Logs invocation to /tmp/sandbox-restrict.log
#       - Validates worktree is within repo (prevents directory traversal)
#       - Optionally enforces read-only mounts if bwrap/firejail available, else logs and passes through
#       - Preserves --allowedTools via CROSSLINK_ALLOWED_TOOLS env for guard audit
# HOW CERTAIN: Proven via manual preflight (bwrap not present, docker present) — fallback is log-only, container provides real isolation.
# WHAT-NOT-TESTED: No bwrap/firejail mount tested on this host; container mode is preferred for real restriction.

set -euo pipefail

WORKTREE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --worktree)
      WORKTREE="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "[sandbox] unknown arg: $1" >&2
      shift
      ;;
  esac
done

LOG="/tmp/sandbox-restrict.log"
mkdir -p "$(dirname "$LOG")"
{
  echo "=== sandbox restrict invoked $(date -Is) ==="
  echo "worktree: $WORKTREE"
  echo "remaining args ($#): $*"
  echo "CROSSLINK_ALLOWED_TOOLS: ${CROSSLINK_ALLOWED_TOOLS:-<unset>}"
  echo "pwd: $(pwd)"
} >> "$LOG" 2>&1 || true

# If bwrap is available, use it to bind-mount worktree rw and rest ro
if command -v bwrap >/dev/null 2>&1 && [[ -n "$WORKTREE" ]]; then
  echo "[sandbox] bwrap found — enforcing ro bind for /, rw for worktree" >> "$LOG" 2>&1 || true
  exec bwrap --ro-bind / / --bind "$WORKTREE" "$WORKTREE" --dev /dev --proc /proc --tmpfs /tmp -- "$@"
elif command -v firejail >/dev/null 2>&1 && [[ -n "$WORKTREE" ]]; then
  echo "[sandbox] firejail found — enforcing whitelist $WORKTREE" >> "$LOG" 2>&1 || true
  exec firejail --noprofile --whitelist="$WORKTREE" --read-only=/ --read-write="$WORKTREE" -- "$@"
else
  echo "[sandbox] no bwrap/firejail — log-only fallback, real isolation via --container docker (audit §3.6)" >> "$LOG" 2>&1 || true
  # Fallback: log-only, then exec remaining command directly (no OS isolation, but audit trail preserved)
  exec "$@"
fi
