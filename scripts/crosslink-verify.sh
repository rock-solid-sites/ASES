#!/usr/bin/env bash
# crosslink-verify.sh — verify that a range of commits satisfies
# repository, task, and policy constraints before merging.
#
# Usage:
#   scripts/crosslink-verify.sh [options] [<base_commit>]
#
# Repository Verification (always run):
#   1. HEAD resolves to a different commit than BASE_COMMIT
#   2. BASE_COMMIT is an ancestor of HEAD
#   3. Working tree is clean (git status --porcelain is empty)
#   4. Diff is non-empty
#   5. No stubs (TODO, FIXME, unimplemented!(), todo!(), panic!()) in diff
#
# Task Verification (configurable):
#   --expect-changes <pathspec>  Fail if no changes in given paths
#   --min-file-size <bytes>      Fail if any changed file is smaller
#   --file-type <ext>            Fail if changed files don't match ext
#
# Policy Verification (if .crosslink/ exists):
#   - Commit message format (conventional commits)
#   - Issue linkage in commit messages
#
# Options:
#   --worktree <path>  Run git commands with -C <path>
#   --batch            Silent mode (exit 0/1 only, no output)
#   -h, --help         Show this help
#
# Default BASE_COMMIT: origin/main or origin/master (whichever exists)

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"

# ---- Configuration ----
WORKTREE=""
BATCH=false
EXPECT_CHANGES=""
MIN_FILE_SIZE=""
FILE_TYPE=""
BASE_COMMIT=""
GIT_ARGS=()

# ---- Usage ----
usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [options] [<base_commit>]

Repository, task, and policy verification for crosslink-tracked repos.

Options:
  --worktree <path>        Run git commands with -C <path>
  --batch                  Silent mode (exit 0/1 only)
  --expect-changes <path>  Fail if no changes in <path> (git pathspec)
  --min-file-size <bytes>  Fail if files are smaller than <bytes>
  --file-type <ext>        Fail if files don't match extension <ext>
  -h, --help               Show this help

Exit codes:
  0   All checks pass
  1   One or more checks failed
EOF
}

# ---- Parse arguments ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --worktree)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --worktree requires a path argument" >&2
        exit 2
      fi
      WORKTREE="$2"
      shift 2
      ;;
    --batch)
      BATCH=true
      shift
      ;;
    --expect-changes)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --expect-changes requires a pathspec argument" >&2
        exit 2
      fi
      EXPECT_CHANGES="$2"
      shift 2
      ;;
    --min-file-size)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --min-file-size requires a byte argument" >&2
        exit 2
      fi
      MIN_FILE_SIZE="$2"
      shift 2
      ;;
    --file-type)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --file-type requires an extension argument" >&2
        exit 2
      fi
      FILE_TYPE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "ERROR: Unknown option: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [[ -z "$BASE_COMMIT" ]]; then
        BASE_COMMIT="$1"
        shift
      else
        echo "ERROR: Unexpected argument: $1" >&2
        usage
        exit 2
      fi
      ;;
  esac
done

# Build git args for worktree
if [[ -n "$WORKTREE" ]]; then
  GIT_ARGS=(-C "$WORKTREE")
fi

# Detect default base commit
if [[ -z "$BASE_COMMIT" ]]; then
  if git "${GIT_ARGS[@]}" show-ref --verify refs/remotes/origin/main >/dev/null 2>&1; then
    BASE_COMMIT="origin/main"
  elif git "${GIT_ARGS[@]}" show-ref --verify refs/remotes/origin/master >/dev/null 2>&1; then
    BASE_COMMIT="origin/master"
  else
    echo "ERROR: No base commit specified and neither origin/main nor origin/master found." >&2
    echo "       Provide a <base_commit> argument explicitly." >&2
    exit 1
  fi
fi

# ---- State ----
OVERALL_EXIT=0
PASS_COUNT=0
FAIL_COUNT=0

# ---- Helpers ----
out() {
  if [[ "$BATCH" != true ]]; then
    echo "$@"
  fi
}

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  out "  PASS  $1"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  OVERALL_EXIT=1
  out "  FAIL  $1"
}

# Resolve base commit hash for checks that need it
BASE_HASH=""
HEAD_HASH=""

resolve_hashes() {
  BASE_HASH="$(git "${GIT_ARGS[@]}" rev-parse --verify "$BASE_COMMIT" 2>/dev/null)" || true
  HEAD_HASH="$(git "${GIT_ARGS[@]}" rev-parse --verify HEAD 2>/dev/null)" || true
}

resolve_hashes

# ---- Ensure base commit is valid ----
if [[ -z "$BASE_HASH" ]]; then
  echo "ERROR: Cannot resolve base commit '$BASE_COMMIT'" >&2
  exit 1
fi
if [[ -z "$HEAD_HASH" ]]; then
  echo "ERROR: Cannot resolve HEAD" >&2
  exit 1
fi

# ══════════════════════════════════════════════
# 1.  REPOSITORY VERIFICATION (always run)
# ══════════════════════════════════════════════

out "=== crosslink-verify ==="
out "Base: $BASE_COMMIT ($BASE_HASH)"
out "HEAD: $HEAD_HASH"
out
out "--- Repository Checks ---"

# 1a. HEAD and BASE_COMMIT differ
if [[ "$HEAD_HASH" != "$BASE_HASH" ]]; then
  pass "HEAD differs from BASE_COMMIT"
else
  fail "HEAD is at BASE_COMMIT — no new commits"
fi

# 1b. BASE_COMMIT is an ancestor of HEAD
if git "${GIT_ARGS[@]}" merge-base --is-ancestor "$BASE_COMMIT" HEAD 2>/dev/null; then
  pass "BASE_COMMIT is ancestor of HEAD"
else
  fail "BASE_COMMIT is not an ancestor of HEAD"
fi

# 1c. Working tree is clean
WORKTREE_STATUS="$(git "${GIT_ARGS[@]}" status --porcelain 2>/dev/null)" || true
if [[ -z "$WORKTREE_STATUS" ]]; then
  pass "Working tree is clean"
else
  fail "Working tree is dirty — has uncommitted changes"
fi

# 1d. Diff is non-empty
DIFF_STAT="$(git "${GIT_ARGS[@]}" diff --stat "$BASE_COMMIT..HEAD" 2>/dev/null)" || true
if [[ -n "$DIFF_STAT" ]]; then
  pass "Diff is non-empty"
else
  fail "Diff is empty — no changes between BASE_COMMIT and HEAD"
fi

# 1e. Stub detection
STUB_COUNT=0
STUB_OUTPUT="$(git "${GIT_ARGS[@]}" diff "$BASE_COMMIT..HEAD" 2>/dev/null \
  | grep -inE "TODO|FIXME|unimplemented!\(\)|todo!\(\)|panic!\(\)" 2>/dev/null)" \
  || STUB_OUTPUT=""
if [[ -z "$STUB_OUTPUT" ]]; then
  pass "Stub detection — no stubs found in diff"
else
  STUB_COUNT="$(echo "$STUB_OUTPUT" | wc -l)"
  fail "Stub detection — $STUB_COUNT stub(s) found in diff"
fi

# ══════════════════════════════════════════════
# 2.  TASK VERIFICATION (configurable)
# ══════════════════════════════════════════════

TASK_CHECKS=false
if [[ -n "$EXPECT_CHANGES" || -n "$MIN_FILE_SIZE" || -n "$FILE_TYPE" ]]; then
  TASK_CHECKS=true
  out
  out "--- Task Checks ---"
fi

# Collect changed files (null-delimited for safety with special chars)
CHANGED_FILES=()
while IFS= read -r -d '' f; do
  CHANGED_FILES+=("$f")
done < <(git "${GIT_ARGS[@]}" diff "$BASE_COMMIT..HEAD" --name-only -z 2>/dev/null || true)

# 2a. Expect changes in specific paths
if [[ -n "$EXPECT_CHANGES" ]]; then
  PATHDIFF="$(git "${GIT_ARGS[@]}" diff "$BASE_COMMIT..HEAD" --stat -- "$EXPECT_CHANGES" 2>/dev/null)" || true
  if [[ -n "$PATHDIFF" ]]; then
    pass "Expect changes: $EXPECT_CHANGES"
  else
    fail "Expect changes: $EXPECT_CHANGES — no changes found in specified paths"
  fi
fi

# 2b. Min file size
if [[ -n "$MIN_FILE_SIZE" ]]; then
  ALL_SIZE_OK=true
  for f in "${CHANGED_FILES[@]}"; do
    # Resolve full path relative to worktree
    if [[ -n "$WORKTREE" ]]; then
      FULL_PATH="${WORKTREE%/}/$f"
    else
      FULL_PATH="$f"
    fi
    if [[ -f "$FULL_PATH" ]]; then
      SIZE="$(stat -c%s "$FULL_PATH" 2>/dev/null || stat -f%z "$FULL_PATH" 2>/dev/null)" || true
      if [[ -z "$SIZE" ]]; then
        fail "Min file size: $f — could not determine file size"
        ALL_SIZE_OK=false
      elif [[ "$SIZE" -lt "$MIN_FILE_SIZE" ]]; then
        fail "Min file size: $f ($SIZE bytes < $MIN_FILE_SIZE bytes)"
        ALL_SIZE_OK=false
      fi
    fi
  done
  if [[ "$ALL_SIZE_OK" == true ]]; then
    pass "Min file size: all files >= $MIN_FILE_SIZE bytes"
  fi
fi

# 2c. File type check
if [[ -n "$FILE_TYPE" ]]; then
  # Normalize extension (add leading dot if missing)
  EXT="$FILE_TYPE"
  [[ "$EXT" != .* ]] && EXT=".$EXT"
  ALL_MATCH=true
  for f in "${CHANGED_FILES[@]}"; do
    if [[ "$f" != *"$EXT" ]]; then
      fail "File type: $f does not match expected extension $EXT"
      ALL_MATCH=false
    fi
  done
  if [[ "$ALL_MATCH" == true ]]; then
    pass "File type: all files match expected extension $EXT"
  fi
fi

# ══════════════════════════════════════════════
# 3.  POLICY VERIFICATION (if .crosslink/ exists)
# ══════════════════════════════════════════════

POLICY_DIR=""
if [[ -n "$WORKTREE" ]]; then
  POLICY_DIR="${WORKTREE%/}/.crosslink"
else
  POLICY_DIR=".crosslink"
fi

if [[ -d "$POLICY_DIR" ]]; then
  out
  out "--- Policy Checks ---"

  # 3a. Commit message format — check for conventional commits
  COMMIT_MSGS=()
  while IFS= read -r msg; do
    COMMIT_MSGS+=("$msg")
  done < <(git "${GIT_ARGS[@]}" log "$BASE_COMMIT..HEAD" --format="%s" 2>/dev/null || true)

  TOTAL_COMMITS="${#COMMIT_MSGS[@]}"
  BAD_FORMAT=0

  for msg in "${COMMIT_MSGS[@]}"; do
    if ! echo "$msg" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]*\))?:\s'; then
      BAD_FORMAT=$((BAD_FORMAT + 1))
    fi
  done

  if [[ "$TOTAL_COMMITS" -eq 0 ]]; then
    out "  SKIP  Commit message format — no commits to check"
  elif [[ "$BAD_FORMAT" -eq 0 ]]; then
    pass "Commit message format (conventional commits)"
  else
    fail "Commit message format: $BAD_FORMAT/$TOTAL_COMMITS commit(s) not in conventional format"
  fi

  # 3b. Issue linkage — check for cross-reference patterns
  NO_ISSUE=0
  for msg in "${COMMIT_MSGS[@]}"; do
    if ! echo "$msg" | grep -qiE '(#[0-9]+|refs? #[0-9]+|close[sd]? #[0-9]+|fix(e[sd])? #[0-9]+|resolve[sd]? #[0-9]+)'; then
      NO_ISSUE=$((NO_ISSUE + 1))
    fi
  done

  if [[ "$TOTAL_COMMITS" -eq 0 ]]; then
    out "  SKIP  Issue linkage — no commits to check"
  elif [[ "$NO_ISSUE" -eq 0 ]]; then
    pass "Issue linkage in commit messages"
  else
    fail "Issue linkage: $NO_ISSUE/$TOTAL_COMMITS commit(s) without issue reference"
  fi
fi

# ══════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════

out
out "Results: $PASS_COUNT passed, $FAIL_COUNT failed"

exit "$OVERALL_EXIT"
