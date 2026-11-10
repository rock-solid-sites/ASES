#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
repo="$(git rev-parse --show-toplevel)"
task_dir="$repo/docs/research/phase-i-termination-evidence"
pin="9fb8a525c32b56b9191d3f33df9925939636dc9a"
worktree="$task_dir/prechange-worktree"
evidence="$task_dir/evidence/prechange-comparator"
mkdir -p "$evidence"
if ! git -C "$repo" worktree list --porcelain | rg -F -q "worktree $worktree"; then
  git -C "$repo" worktree add --detach "$worktree" "$pin"
fi
test "$(git -C "$worktree" rev-parse HEAD)" = "$pin"
cp "$task_dir/prechange_native.rs" "$worktree/resource-control/tests/native_termination_comparator.rs"
export CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo
export RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup
export CARGO_TARGET_DIR=/workspace/ases-resume/resource-control/target
export CARGO_PROFILE_TEST_DEBUG=1
export ASES_PRECHANGE_EVIDENCE_DIR="$evidence"
"$CARGO_HOME/bin/cargo" test --locked --offline \
  --manifest-path "$worktree/resource-control/Cargo.toml" \
  --test native_termination_comparator -- --nocapture
printf 'Pinned pre-change comparator evidence: %s\n' "$evidence/prechange-live-finalize.json"
