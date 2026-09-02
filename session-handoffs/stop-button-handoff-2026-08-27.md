# Handoff — Stop-Button Tiny V2 Interrupt Plugin — 2026-08-27

**Status: READY TO LAUNCH (durable kickoff) — do not repeat completed work**

## Where we are
- **Original interrupt plugin never completed.** Interop Probe #464 T5a: global `plugins/plugin.ts + plugins/interrupt.ts` parsed but not executed; worktree `.opencode/plugins/` guards not loaded on S1 beta. Repo currently has 3 guards only (orchestrator-guard, crosslink-guard, rtk-guard).
- **Native V2 escape broken:** `session_interrupt` → `escape` never stops agent, shows "press esc again" dialog with multiple hits, no kill. Handler exists `packages/server/src/handlers/session.ts:366 yield* session.interrupt` but TUI wiring doesn't reach `SessionRunCoordinator` fiber. User wants web-chat style: **mouse Stop button right of prompt, toggle Send↔Stop, confirm popup, stops agent.**
- **Adversarial reviews done (Task, short job, per user approval):** Big Pickle **FAIL**, hy3 **CONDITIONAL PASS** — both require 6-point server-side gate before UI wiring, and cheapest-test-first.
- **Existence check done (cheapest test per user correction):** No drop-in Stop-button plugin to install. `opencode.nvim` maps `<Esc>→session.interrupt` (proves endpoint works, reference impl), `opencode-auto-resume` detects stuck + respects ESC. Treat as reference, not install. `ecosystem.mdx` 39 plugins, 0 with stop.
- **Upgraded to major:** uncancellable auth interrupt hit this session + free-model `Launching Swarm Orchestrator Automation` 429-parked again. Go model (muse spark paid via Go) works, free fails. Earlyoom constraint: other ongoing work, must keep headroom.
- **Dynamic-models plugin broken:** `~/.config/opencode/plugins/dynamic-models.js Cannot find module './time.js'` 09:08/09:37 — free models still visible but will 429.

## Agreed scope (bare minimum)
- One file, branch `stop-button` (AGENTS.md: ≤3 words, hyphens), commit `feat(tui): add stop button with confirm → session.interrupt`
- Toggle `Send` (idle) ↔ `■ Stop` (running) right of prompt input (same row as submit, data-action="prompt-submit"), disabled grey when idle.
- Click → confirm `Stop agent? Yes/No` → Yes → authoritative `ctx.session.interrupt(sessionID)` / `POST /api/session/:id/interrupt` (same as opencode.nvim), debounced, toast, log /tmp/stop-button.log. Fail-closed when no session.
- No new server route, no durable state, idempotent.

## Hard acceptance (6-point, not "button fires")
1. Click Stop → session → idle
2. Model stream actually terminates
3. Active bash/tool (sleep 60) terminates
4. Session can immediately accept new prompt
5. Auth failure/parked 401/429 also interruptible
6. Kill/restart UI → no orphaned server execution (active not showing running)

UI showing "Stopped" while server lives is worse than useless — already evidenced in V2/server API.

## Why Task failed (diagnosis for new orchestrator)
- Three straight `ases-builder` Task aborts `Tool execution interrupted: subagent` + two server restarts → no Code Mode tools, no durable checkpoint.
- Task is in-memory, no `.active-issue` / `CROSSLINK_AGENT_TYPE`, so `orchestrator-guard` + `crosslink-guard` blocked `bash`/`write`; Task has no `systemd-run --scope MemoryMax` cap, first to be reaped on earlyoom. Other agents work because they use durable `crosslink kickoff` (isolated .worktrees + issues.db checkpoints) — divergence is dispatch surface, not Go model.

## Model pinned
`opencode-go/muse-spark` (muse spark paid via Go) — same Go that stayed well in other session. Verify `opencode models opencode-go` before launch, never guess. Free `...-free` banned for agents.

## Next step (do not use Task)
When Code Mode available, run **durable** single builder (earlyoom-safe, no swarm):

```
crosslink kickoff run --agent builder --model opencode-go/muse-spark --branch stop-button
```

Phase 0: `curl POST /api/session/:id/interrupt` during long run, verify 1-6 via curl + log tail. If API fails to kill fiber/tool, halt UI and fix `SessionRunCoordinator` interruption first. Phase 1 only if Phase 0 passes.

References: `opencode.nvim` (<Esc>→session.interrupt), `opencode-auto-resume` (respect ESC), `packages/app/src/components/prompt-input.tsx:1584` (Send→Stop toggle), `packages/tui/src/component/prompt/index.tsx:393` (double-Escape), `packages/plugin/src/tui.ts:630` (session_prompt_right slot), `CONTEXT.md:176` (idempotent interrupt), `specs/v2/session.md:167`.
