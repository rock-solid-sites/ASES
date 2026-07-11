#!/usr/bin/env bash
# crosslink-cleanup.sh — clean up a crosslink worktree after verification.
#
# Usage:
#   scripts/crosslink-cleanup.sh --worktree <path> [options]
#
# Flow:
#   1. Run verification fresh (no caching)
#   2. Pass: remove worktree, release lock
#   3. Fail: move worktree to .worktrees/failed/<timestamp>-<agent-id>/, release lock
#   4. Optional: archive failed worktrees older than threshold
#
# Options:
#   --worktree <path>         Path to the worktree to clean up (required)
#   --issue <id>              Issue ID for lock release (optional, extracted from branch if omitted)
#   --batch                   Non-interactive mode (auto-confirm archive deletions)
#   --archive-older-than <n>  Archive failed worktrees older than <n> days (default: 7)
#   -h, --help                Show this help
#
# Exit codes:
#   0   Cleanup succeeded (worktree removed or quarantined)
#   1   Verification failed, worktree quarantined
#   2   Usage error
#   3   Worktree path not found or invalid

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Project root is the parent of scripts/ — fixed from script location,
# NOT derived from worktree, because worktrees also contain .crosslink/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---- Defaults ----
WORKTREE=""
ISSUE_ID=""
BATCH=false
ARCHIVE_OLDER_THAN=7

# ---- Colors / formatting ----
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  CYAN='\033[0;36m'
  NC='\033[0m' # No Color
else
  RED=''
  GREEN=''
  YELLOW=''
  CYAN=''
  NC=''
fi

# ---- Usage ----
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME --worktree <path> [options]

Clean up a crosslink worktree after verification.

Required:
  --worktree <path>  Path to the worktree directory to clean up

Options:
  --issue <id>           Issue ID for lock release (e.g. 4 for issue #4)
                         If omitted, extracted from the worktree branch name
  --batch                Non-interactive mode (auto-confirm archive deletions)
  --archive-older-than <n>  Archive failed worktrees older than <n> days (default: 7)
  -h, --help             Show this help

Exit codes:
  0  Cleanup succeeded (worktree removed or quarantined)
  1  Verification failed, worktree quarantined
  2  Usage error
  3  Worktree path not found or invalid
EOF
}

# ---- Log helpers ----
info()  { echo -e "${CYAN}info${NC}  $SCRIPT_NAME: $*"; }
ok()    { echo -e "${GREEN}ok${NC}    $SCRIPT_NAME: $*"; }
warn()  { echo -e "${YELLOW}warn${NC}  $SCRIPT_NAME: $*" >&2; }
err()   { echo -e "${RED}error${NC} $SCRIPT_NAME: $*" >&2; }

# ---- Parse arguments ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --worktree)
      if [[ $# -lt 2 ]]; then
        err "--worktree requires a path argument"
        exit 2
      fi
      WORKTREE="$2"
      shift 2
      ;;
    --issue)
      if [[ $# -lt 2 ]]; then
        err "--issue requires an ID argument"
        exit 2
      fi
      ISSUE_ID="$2"
      shift 2
      ;;
    --batch)
      BATCH=true
      shift
      ;;
    --archive-older-than)
      if [[ $# -lt 2 ]]; then
        err "--archive-older-than requires a number argument"
        exit 2
      fi
      ARCHIVE_OLDER_THAN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      err "Unknown option: $1"
      usage
      exit 2
      ;;
    *)
      err "Unexpected argument: $1"
      usage
      exit 2
      ;;
  esac
done

# ---- Validate required arguments ----
if [[ -z "$WORKTREE" ]]; then
  err "--worktree is required"
  usage
  exit 2
fi

if [[ ! -d "$WORKTREE" ]]; then
  err "Worktree path does not exist or is not a directory: $WORKTREE"
  exit 3
fi

# Resolve to absolute path
WORKTREE="$(cd "$WORKTREE" && pwd)"

# ---- Determine agent ID ----
# Use CROSSLINK_AGENT_ID if set, otherwise fall back to hostname + PID
AGENT_ID="${CROSSLINK_AGENT_ID:-$(hostname -s 2>/dev/null || echo "unknown")-$$}"

WORKTREES_DIR="$PROJECT_ROOT/.worktrees"
FAILED_DIR="$WORKTREES_DIR/failed"

# ---- Ensure .worktrees/failed/ exists ----
mkdir -p "$FAILED_DIR"

# ---- Discover the worktree branch name ----
get_worktree_branch() {
  git -C "$WORKTREE" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached"
}

WORKTREE_BRANCH="$(get_worktree_branch)"

# ---- Extract issue ID if not provided ----
if [[ -z "$ISSUE_ID" ]]; then
  EXTRACTED=""
  # Method 1: Read from .kickoff-metadata.json in the worktree (most reliable)
  if [[ -f "$WORKTREE/.crosslink/issue-id" ]]; then
    EXTRACTED="$(cat "$WORKTREE/.crosslink/issue-id" 2>/dev/null)"
  fi
  # Method 2: Parse from KICKOFF.md header line (backup)
  if [[ -z "$EXTRACTED" && -f "$WORKTREE/KICKOFF.md" ]]; then
    EXTRACTED="$(grep -oP 'Issue:\s+#?\K\d+' "$WORKTREE/KICKOFF.md" 2>/dev/null | head -1 || true)"
  fi
  # Method 3: Extract from crosslink agent slug (last resort)
  # Agent slugs look like: pp3g-LUZK-description-<issue_hash>
  # The issue ID is NOT in the slug; use crosslink to resolve it
  if [[ -z "$EXTRACTED" && -f "$WORKTREE/.kickoff-slug" ]]; then
    slug="$(cat "$WORKTREE/.kickoff-slug" 2>/dev/null)"
    if [[ -n "$slug" ]]; then
      EXTRACTED="$(crosslink kickoff report "$slug" 2>/dev/null | grep -oP 'issue:\s+#?\K\d+' | head -1 || true)"
    fi
  fi

  if [[ -n "$EXTRACTED" ]]; then
    ISSUE_ID="$EXTRACTED"
    info "Extracted issue ID #$ISSUE_ID from worktree metadata"
  else
    warn "Could not extract issue ID from worktree metadata; lock will not be released"
    warn "Pass --issue <id> to release the lock explicitly"
  fi
fi

# ---- Helper: release lock ----
release_lock() {
  local id="$1"
  info "Releasing lock on issue #$id ..."
  if crosslink locks release "$id" 2>&1; then
    ok "Lock released on issue #$id"
  else
    # Lock may already be released or never held
    warn "Could not release lock on issue #$id (may already be released)"
  fi
}

# ---- Helper: get directory mtime (Unix timestamp) ----
get_mtime() {
  local path="$1"
  if [[ -e "$path" ]]; then
    stat -c '%Y' "$path" 2>/dev/null || stat -f '%m' "$path" 2>/dev/null || echo "0"
  else
    echo "0"
  fi
}

# ══════════════════════════════════════════════════════════════
#  1.  RUN VERIFICATION (fresh, no caching)
# ══════════════════════════════════════════════════════════════

info "Running verification on worktree: $WORKTREE (branch: $WORKTREE_BRANCH)"

# Capture mtime BEFORE verification (for invalidation check)
VERIFY_START_MTIME="$(get_mtime "$WORKTREE")"

VERIFY_SCRIPT="$SCRIPT_DIR/crosslink-verify.sh"
if [[ ! -x "$VERIFY_SCRIPT" ]]; then
  # Fall back: look in PROJECT_ROOT/scripts/
  VERIFY_SCRIPT="$PROJECT_ROOT/scripts/crosslink-verify.sh"
fi

if [[ ! -x "$VERIFY_SCRIPT" ]]; then
  err "Cannot find crosslink-verify.sh (checked: $SCRIPT_DIR/crosslink-verify.sh and $PROJECT_ROOT/scripts/crosslink-verify.sh)"
  exit 2
fi

# Run verification — capture exit code and output
VERIFY_OUTPUT=""
VERIFY_EXIT=0
VERIFY_OUTPUT="$("$VERIFY_SCRIPT" --worktree "$WORKTREE" 2>&1)" || VERIFY_EXIT=$?

echo "$VERIFY_OUTPUT"

# ══════════════════════════════════════════════════════════════
#  2.  INVALIDATION RULE — check if worktree was modified during verification
# ══════════════════════════════════════════════════════════════

VERIFY_END_MTIME="$(get_mtime "$WORKTREE")"

if [[ "$VERIFY_END_MTIME" -gt "$VERIFY_START_MTIME" ]]; then
  warn "Worktree was modified during verification (mtime changed)"
  warn "Re-running verification to ensure accuracy..."

  VERIFY_OUTPUT=""
  VERIFY_EXIT=0
  VERIFY_OUTPUT="$("$VERIFY_SCRIPT" --worktree "$WORKTREE" 2>&1)" || VERIFY_EXIT=$?

  echo "$VERIFY_OUTPUT"

  # Check again — if still changing, warn and proceed
  FINAL_MTIME="$(get_mtime "$WORKTREE")"
  if [[ "$FINAL_MTIME" -gt "$VERIFY_START_MTIME" ]]; then
    warn "Worktree continues to be modified; proceeding with current verification result"
  fi
fi

# ══════════════════════════════════════════════════════════════
#  3.  ACT ON VERIFICATION RESULT
# ══════════════════════════════════════════════════════════════

OVERALL_EXIT=0
QUARANTINE_DIR=""

if [[ "$VERIFY_EXIT" -eq 0 ]]; then
  # ── PASS: remove worktree, release lock ──
  info "Verification PASSED — cleaning up worktree"

  # Remove the git worktree
  if git -C "$PROJECT_ROOT" worktree remove "$WORKTREE" 2>&1; then
    ok "Git worktree removed: $WORKTREE"
  else
    # If git worktree remove fails (e.g. dirty state), force remove
    warn "Standard worktree removal failed, attempting force remove..."
    if git -C "$PROJECT_ROOT" worktree remove --force "$WORKTREE" 2>&1; then
      ok "Git worktree force-removed: $WORKTREE"
    else
      # Last resort: manual cleanup
      warn "Force remove failed, cleaning up manually..."
      rm -rf "$WORKTREE" 2>/dev/null || true
      git -C "$PROJECT_ROOT" worktree prune 2>&1 || true
      if [[ ! -d "$WORKTREE" ]]; then
        ok "Worktree manually removed: $WORKTREE"
      else
        err "Failed to remove git worktree: $WORKTREE"
        err "You may need to remove it manually: rm -rf $WORKTREE && git worktree prune"
      fi
    fi
  fi

  # Release the lock if we have an issue ID
  if [[ -n "$ISSUE_ID" ]]; then
    release_lock "$ISSUE_ID"
  fi

  ok "Cleanup complete"
  OVERALL_EXIT=0

else
  # ── FAIL: quarantine worktree, release lock ──
  warn "Verification FAILED (exit code $VERIFY_EXIT) — quarantining worktree"

  # Build quarantine path
  TIMESTAMP="$(date +%Y%m%dT%H%M%S)"
  QUARANTINE_DIR="$FAILED_DIR/${TIMESTAMP}-${AGENT_ID}"
  QUARANTINE_WORKTREE="$QUARANTINE_DIR/worktree"

  mkdir -p "$QUARANTINE_DIR"

  # Move worktree contents into quarantine
  # Note: git worktree remove would delete the worktree; we want to preserve
  # the content for investigation. Since git worktrees are linked to the
  # parent repo, we can't simply mv them. Instead, we:
  # 1. Archive the worktree content first
  # 2. Remove the git worktree
  # 3. Place the archive in the quarantine directory

  info "Archiving worktree content to: $QUARANTINE_DIR"

  # Create a tarball of the worktree content (excluding .git)
  ARCHIVE_FILE="$QUARANTINE_DIR/worktree-content.tar.gz"
  if tar -czf "$ARCHIVE_FILE" -C "$WORKTREE" --exclude='.git' . 2>&1; then
    ok "Worktree content archived to $ARCHIVE_FILE"
  else
    warn "Failed to create archive, trying to copy files directly..."
    mkdir -p "$QUARANTINE_WORKTREE"
    cp -a "$WORKTREE/." "$QUARANTINE_WORKTREE/" 2>/dev/null || \
      warn "Could not preserve worktree files — partial quarantine"
  fi

  # Save metadata
  {
    echo "agent_id:       $AGENT_ID"
    echo "branch:         $WORKTREE_BRANCH"
    echo "worktree_path:  $WORKTREE"
    echo "issue_id:       ${ISSUE_ID:-unresolved}"
    echo "timestamp:      $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "verify_exit:    $VERIFY_EXIT"
    echo "verify_output:  QUARANTINED"
  } > "$QUARANTINE_DIR/meta.txt"

  # Save the verification output
  echo "$VERIFY_OUTPUT" > "$QUARANTINE_DIR/verify-output.txt"

  # Remove the git worktree after quarantine
  if git -C "$PROJECT_ROOT" worktree remove "$WORKTREE" 2>&1; then
    ok "Git worktree removed after quarantine"
  else
    warn "Standard worktree removal failed, attempting force remove..."
    if git -C "$PROJECT_ROOT" worktree remove --force "$WORKTREE" 2>&1; then
      ok "Git worktree force-removed after quarantine"
    else
      warn "Force remove failed, cleaning up manually..."
      rm -rf "$WORKTREE" 2>/dev/null || true
      git -C "$PROJECT_ROOT" worktree prune 2>&1 || true
      if [[ ! -d "$WORKTREE" ]]; then
        ok "Worktree manually removed after quarantine"
      fi
    fi
  fi

  # Release the lock if we have an issue ID
  if [[ -n "$ISSUE_ID" ]]; then
    release_lock "$ISSUE_ID"
  fi

  err "Worktree quarantined to: $QUARANTINE_DIR"
  err "Verification failure reason — see: $QUARANTINE_DIR/verify-output.txt"
  OVERALL_EXIT=1
fi

# ══════════════════════════════════════════════════════════════
#  4.  ARCHIVE OLD QUARANTINED WORKTREES
# ══════════════════════════════════════════════════════════════

purge_old_quarantines() {
  local days="$1"
  local batch_mode="$2"
  local failed_dir="$3"
  local purged=0
  local errors=0

  if [[ ! -d "$failed_dir" ]]; then
    return 0
  fi

  # Find directories in .worktrees/failed/ older than threshold
  # Use mtime in seconds, compare with (now - days*86400)
  local cutoff
  cutoff="$(date -d "$days days ago" +%s 2>/dev/null)" || \
    cutoff="$(python3 -c "import time; print(int(time.time() - $days * 86400))" 2>/dev/null)" || \
    cutoff="$(( $(date +%s) - days * 86400 ))"

  local stale_dirs=()
  local dir entry mtime

  while IFS= read -r -d '' entry; do
    mtime="$(get_mtime "$entry")"
    if [[ "$mtime" -lt "$cutoff" && "$mtime" -gt 0 ]]; then
      stale_dirs+=("$entry")
    fi
  done < <(find "$failed_dir" -maxdepth 1 -mindepth 1 -type d -print0 2>/dev/null || true)

  if [[ ${#stale_dirs[@]} -eq 0 ]]; then
    info "No quarantined worktrees older than $days days found"
    return 0
  fi

  echo ""
  info "Found ${#stale_dirs[@]} quarantined worktree(s) older than $days days:"
  for dir in "${stale_dirs[@]}"; do
    local age
    age="$(( ($(date +%s) - $(get_mtime "$dir")) / 86400 ))"
    echo "    $dir  ($age days old)"
  done

  # Confirm unless --batch
  if [[ "$batch_mode" != "true" ]]; then
    echo ""
    read -r -p "Remove these ${#stale_dirs[@]} quarantined worktrees? [y/N] " CONFIRM
    if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
      info "Archive purge cancelled"
      return 0
    fi
  fi

  for dir in "${stale_dirs[@]}"; do
    if rm -rf "$dir" 2>/dev/null; then
      info "Removed old quarantine: $(basename "$dir")"
      purged=$((purged + 1))
    else
      warn "Failed to remove: $dir"
      errors=$((errors + 1))
    fi
  done

  echo ""
  if [[ "$errors" -eq 0 ]]; then
    ok "Archived quarantine cleanup complete: $purged removed"
  else
    warn "Archived quarantine cleanup: $purged removed, $errors failed"
  fi
}

# Only run archive purge if the failed directory exists and has entries
if [[ -d "$FAILED_DIR" ]]; then
  purge_old_quarantines "$ARCHIVE_OLDER_THAN" "$BATCH" "$FAILED_DIR"
fi

exit "$OVERALL_EXIT"
