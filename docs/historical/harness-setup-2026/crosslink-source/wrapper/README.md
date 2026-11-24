# Claude Wrapper — fix-then-activate (audit #505 §3.1c)

This is the fixed `~/.local/bin/claude` wrapper that translates `claude` CLI args to `opencode run`.

**Why:** Previously dropped `--allowedTools` and `--permission-mode` via `shift 2` with no forwarding — silent enforcement loss. Any claim “kickoff is restricted to allowed tools” was false for `--container none`.

**What changed:**
- `--allowedTools <list>` now preserved in `CROSSLINK_ALLOWED_TOOLS` env + logged (preview 200 chars), not dropped. `opencode run` has no --allowedTools flag, so env preservation is the safe audit path; container mode (launch.rs:1023) bypasses wrapper and enforces directly.
- `--permission-mode <mode>` now mapped: `bypassPermissions|acceptEdits|auto` → `--auto`, others logged, preserved in `CROSSLINK_PERMISSION_MODE` env, not dropped.

**How to install:** `cp .crosslink/wrapper/claude-wrapper.sh ~/.local/bin/claude && chmod +x ~/.local/bin/claude`

**Verification:** `crosslink kickoff run --dry-run` + live kickoff logs show `[wrapper] --allowedTools forwarded` in tmux pane.

**Related:** launch.rs:57 sandbox.command, hook-config.json `sandbox.command`, crosslink-guard.ts S2 read-only block.
