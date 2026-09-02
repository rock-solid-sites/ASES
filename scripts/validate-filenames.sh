#!/usr/bin/env bash
# validate-filenames.sh — project-agnostic early filename portability check
#
# Scans git-tracked files (and optionally staged/untracked) for characters
# that break cross-platform merges, Windows, or URL decode handling.
# Primary trigger: colon (:) caused 200 decode errors on merge of
# specifications/Adverarial Test Suite Reviews:.md (#544).
#
# Rules (project-agnostic — applies to every project, not observer-specific):
#   - Windows-illegal: < > : " | ? *  (colon is the #544 regression)
#   - Control characters 0x00-0x1F / 0x7F
#   - Trailing space or dot in any path component (Windows strips these)
#   - Leading dash in basename is flagged as warning (not hard fail)
#
# Usage:
#   scripts/validate-filenames.sh [--worktree <path>] [--staged] [--all]
#
# Exit codes:
#   0  All filenames clean
#   1  One or more illegal filenames found
#   2  Usage error
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
WORKTREE=""
MODE="tracked"  # tracked | staged | all
GIT_ARGS=()

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [options]

Project-agnostic filename portability check.

Options:
  --worktree <path>  Run git with -C <path>
  --staged           Check staged (git diff --cached) instead of tracked files
  --all              Check tracked + untracked files (git ls-files --others)
  -h, --help         Show this help

Exit codes:
  0  All filenames clean
  1  Illegal filenames found
  2  Usage error
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --worktree)
      if [[ $# -lt 2 ]]; then echo "ERROR: --worktree requires a path" >&2; exit 2; fi
      WORKTREE="$2"
      shift 2
      ;;
    --staged) MODE="staged"; shift ;;
    --all) MODE="all"; shift ;;
    -h|--help) usage; exit 0 ;;
    --*) echo "ERROR: Unknown option: $1" >&2; usage; exit 2 ;;
    *) echo "ERROR: Unexpected argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -n "$WORKTREE" ]]; then
  GIT_ARGS=(-C "$WORKTREE")
  if [[ ! -d "$WORKTREE" ]]; then
    echo "ERROR: Worktree does not exist: $WORKTREE" >&2
    exit 2
  fi
fi

# Collect files null-delimited
FILES=()
collect_tracked() {
  while IFS= read -r -d '' f; do
    FILES+=("$f")
  done < <(git "${GIT_ARGS[@]}" ls-files -z 2>/dev/null || true)
}
collect_staged() {
  while IFS= read -r -d '' f; do
    FILES+=("$f")
  done < <(git "${GIT_ARGS[@]}" diff --cached --name-only -z 2>/dev/null || true)
}
collect_all() {
  while IFS= read -r -d '' f; do
    FILES+=("$f")
  done < <(git "${GIT_ARGS[@]}" ls-files -z --cached --others --exclude-standard 2>/dev/null || true)
}

case "$MODE" in
  tracked) collect_tracked ;;
  staged) collect_staged ;;
  all) collect_all ;;
esac

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "validate-filenames: no files to check (mode=$MODE)"
  exit 0
fi

FAIL_COUNT=0
WARN_COUNT=0

is_illegal() {
  local path="$1"
  # Check each path component for illegal patterns
  local IFS='/'
  local component
  read -ra parts <<< "$path"
  for component in "${parts[@]}"; do
    # Empty component (should not happen except leading /)
    [[ -z "$component" ]] && continue
    # Windows-illegal chars: < > : " | ? *
    # Use glob patterns to avoid regex escaping issues
    if [[ "$component" == *":"* ]]; then
      echo "colon ':'"
      return 0
    fi
    if [[ "$component" == *"<"* ]] || [[ "$component" == *">"* ]]; then
      echo "angle bracket '<' or '>'"
      return 0
    fi
    if [[ "$component" == *'"'* ]]; then
      echo "double quote '\"'"
      return 0
    fi
    if [[ "$component" == *"|"* ]]; then
      echo "pipe '|'"
      return 0
    fi
    if [[ "$component" == *"?"* ]]; then
      echo "question mark '?'"
      return 0
    fi
    if [[ "$component" == *"*"* ]]; then
      echo "asterisk '*'"
      return 0
    fi
    if [[ "$component" == *"\\"* ]]; then
      echo "backslash '\\'"
      return 0
    fi
    # Control characters
    if [[ "$component" == *$'\n'* ]] || [[ "$component" == *$'\r'* ]] || [[ "$component" == *$'\t'* ]]; then
      echo "control character"
      return 0
    fi
    # Check for any control char 0x01-0x1F 0x7F using bash pattern with [:cntrl:]
    if [[ "$component" =~ [[:cntrl:]] ]]; then
      echo "control character"
      return 0
    fi
    # Trailing space or dot in component
    if [[ "$component" == *" " ]] || [[ "$component" == *"." ]]; then
      echo "trailing space/dot"
      return 0
    fi
  done
  return 1
}

for f in "${FILES[@]}"; do
  reason=""
  if reason="$(is_illegal "$f")"; then
    echo "  FAIL  $f — illegal $reason"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  # Warning: leading dash could break shell globbing (not hard fail)
  base="${f##*/}"
  if [[ "$base" == "-"* ]]; then
    echo "  WARN  $f — leading dash in basename"
    WARN_COUNT=$((WARN_COUNT + 1))
  fi
done

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  echo ""
  echo "validate-filenames: $FAIL_COUNT illegal filename(s) found (mode=$MODE)"
  echo "  Fix: rename files to remove illegal characters (especially colon ':')."
  echo "  See issue #544: colon caused 200 decode errors on merge."
  exit 1
fi

if [[ "$WARN_COUNT" -gt 0 ]]; then
  echo "validate-filenames: $WARN_COUNT warning(s), 0 failures"
fi
echo "validate-filenames: PASS — ${#FILES[@]} file(s) clean (mode=$MODE)"
exit 0
