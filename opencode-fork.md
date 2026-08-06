---
title: "opencode Fork (durable silent-hang fix)"
tags: ["opencode", "fork", "silent-hang", "reliability"]
sources:
  - url: "https://github.com/anomalyco/opencode"
    title: ""
    accessed_at: "2026-08-06"
contributors: ["pp3g-nHSI-resume-phase-2-154-durable-fork-build-task-on-issue"]
created: 2026-08-06
updated: 2026-08-06
---

# opencode Fork (durable silent-hang fix, gh#154)

The durable silent-hang fix for the opencode CLI is maintained as a fork of
[anomalyco/opencode](https://github.com/anomalyco/opencode) (the upstream
published as `opencode-ai`), pinned at tag **v1.18.13** (commit `a105350`).
This page is the operational reference: upstream identity, the patch set, how
to build/replace/rollback, how to detect the fork vs upstream at runtime, and
the upgrade-survival invariant.

## Upstream identity and pin

- Upstream repo: `https://github.com/anomalyco/opencode.git` (npm package
  `opencode-ai`).
- Pinned tag: `v1.18.13` = commit `a105350` (`release: v1.18.13`).
- Fork source (working copy): `/tmp/opencode/fork-build`, branch
  `pp3g-fork-v1.18.13`, commit `a7a80ef` (parent `a105350`).
- Durable export (applyable patch + tests + harness): `fork/` in this repo —
  `fork/patches/opencode-fork-v1.18.13-pp3g.patch`, `fork/tests/`,
  `fork/harness/`. The patch applies cleanly to pristine v1.18.13
  (verified with `patch --dry-run`).

## What the fork changes (patches A-E + Patch D MAJOR)

Both guard copies are patched with a `wrapBodyIdle` dispatcher (Option A'
idle-progress deadline):

1. `packages/opencode/src/provider/provider.ts` (v1 native path) and
   `packages/core/src/aisdk.ts` (v2 AI-SDK path): after `fetch()` resolves,
   if the response is NOT `text/event-stream`, wrap the body with
   `wrapBodyIdle(res, bodyIdleTimeout, ctl, bodyAbsoluteTimeout)`. The
   dispatcher routes SSE bodies through the existing `wrapSSE`
   (`chunkTimeout`) and non-SSE bodies through `wrapBodyIdle`.
2. `wrapBodyIdle`: an idle-progress deadline — the timer resets on every
   chunk, so slow-but-progressing bodies are never aborted; a body that
   stalls >= `bodyIdleTimeout` ms between chunks aborts with
   `ProviderError.ResponseStreamError("Body read timed out")`. Optional
   `bodyAbsoluteTimeout` is a total wall-clock cap (opt-in, default off).
3. `packages/opencode/src/session/llm.ts` (Patch D MAJOR): turn-level guard
   on the parsed-event stream via `Stream.timeoutOrElse` — if no parsed
   stream event arrives within `experimental.llmIdleTimeout`
   (default 300_000 ms), fail with
   `ProviderError.ResponseStreamError("Turn stalled: ...")`. The binding is
   derived from `config.get()` in the `live` layer scope, NOT the sibling
   stream binding (the TS2304 fix). Adds per-parsed-event DEBUG
   instrumentation (`llm stream start` / `llm stream event`).
4. `packages/opencode/src/session/retry.ts` (Patch E): error-class-scoped
   retry budget `RETRY_MAX_RETRIES = 2` for the timeout/stream class
   (`ProviderResponseStreamError`, `ProviderHeaderTimeoutError`,
   `ECONNRESET`, `ZlibError`) — initial + 2 retries = exactly 3 POSTs, then
   terminal `WARN "retry budget exhausted"` with `totalPOSTs: meta.attempt`
   (=3, not 4). 429 / usage-limit / other APIErrors keep the existing
   unbounded retry-after semantics. Per-attempt `WARN "retry"` logs
   attempt/code/nextDelay.
5. Config schema (`packages/core/src/v1/config/config.ts`,
   `packages/core/src/v1/config/provider.ts`,
   `packages/sdk/openapi.json`): adds `bodyIdleTimeout`,
   `bodyAbsoluteTimeout` provider options and `llmIdleTimeout`
   experimental option so typos are caught at config parse.

## Runtime identity markers / drift detection

The fork build stamps a distinct version and embeds the new marker strings.
Use these to tell a fork binary from upstream:

- `opencode --version` reports `1.18.13-pp3g-fork` (vs upstream `1.18.13`).
- The binary contains the marker strings: `Body read timed out`,
  `Body read deadline exceeded`, `Turn stalled`, `retry budget exhausted`
  (grep the binary: each present in the compiled output).
- Runtime log markers: `WARN ... "retry"` per attempt, terminal
  `WARN "retry budget exhausted"`, `ERROR ... Body read timed out`,
  `ERROR ... Turn stalled`.

Drift check (operator, after any opencode upgrade):
`grep -c "if(false)return" $(which opencode)` — this detects the EPHEMERAL
stopgap byte patch (#145/#179), not the fork. The fork-specific check is
`opencode --version` containing `-pp3g-fork` AND the marker strings above.
If the installed binary reports plain `1.18.13` without markers, the upgrade
has replaced the fork — re-apply the fork build (below).

## Build / replace / rollback

Prerequisites: bun pinned at **1.3.14** (`~/.bun/bin/bun`), workspace-root
`bun install` already done in the fork working copy.

```
# From the fork working copy (/tmp/opencode/fork-build), branch pp3g-fork-v1.18.13:
bun --cwd packages/opencode run build          # produces dist/opencode-linux-x64/bin/opencode
```

Atomic replace (stage + same-fs mv, NOT cp across devices):

```
STAGE=/tmp/opencode/stage
mkdir -p "$STAGE"
cp /tmp/opencode/fork-build/packages/opencode/dist/opencode-linux-x64/bin/opencode "$STAGE/opencode"
# backup the current live binary first
cp /home/claude-code/.nvm/versions/node/v22.22.3/lib/node_modules/opencode-ai/bin/opencode.exe \
   /tmp/opencode/opencode.exe.ORIGINAL-1.18.13.bak
mv "$STAGE/opencode" /home/claude-code/.nvm/versions/node/v22.22.3/lib/node_modules/opencode-ai/bin/opencode.exe
opencode --version    # must report 1.18.13-pp3g-fork
```

Rollback: restore the backup with the same atomic mv pattern; verify
`--version` returns the pre-fork value and the stopgap byte patch markers
(`if(false)return` x2) are present again.

## Upgrade-survival invariant

The fork must survive opencode self-upgrades. Requirements:

- `~/.config/opencode/opencode.json` sets `"autoupdate": false`
  (already applied by #179 stopgap) so opencode does not overwrite the
  binary on its own.
- Any manual upgrade MUST be followed by the drift check above, and the
  fork build re-applied if the installed binary no longer reports
  `-pp3g-fork`.
- The interim #179 stopgap byte patch stays in place until the fork binary
  is verified; it is the recovery net if the fork is reverted.

## Verification harness

`fork/harness/` contains the deterministic matrix:

- `server.js` — fake OpenAI-compatible provider with modes
  HANG / STALLED / PARSE_STALL / PER_REQUEST / GZIP / SLOW_CHUNK /
  HEALTHY_JSON, counting POSTs server-side.
- `gen-cfg.mjs` — generates per-row OPENCODE_CONFIG_DIR with the invariant
  `headerTimeout < chunkTimeout < bodyIdleTimeout < timeout`.
- `run-matrix.sh` — 16-row matrix; asserts exit code, <=3 POSTs, ERROR/WARN
  markers, terminal budget WARN, body/SSE/turn markers. Generous per-row
  outer timeouts (90-240s) so markers surface before any outer kill; the
  run_row env-arg filter prevents `env ""` 127 failures.

Unit tests: `fork/tests/retry.test.ts` (38 tests incl. 5 bounded-budget)
and `fork/tests/body-idle-timeout.test.ts` (7 tests) — green against the
fork source with bun 1.3.14.

## Known status / caveats

The matrix is run against the PRESERVED binary
(`/tmp/opencode/fork-build/packages/opencode/dist/.../opencode`, mtime
2026-08-06 01:46, 148 MB). Full 16-row results are posted on the resume
sub-issue (#205/#209). The stopgap #179 byte patch remains in place until
the fork is verified and installed with operator approval.
