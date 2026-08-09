---
title: "opencode Fork (durable silent-hang fix)"
tags: ["opencode", "fork", "silent-hang", "reliability"]
sources:
  - url: "https://github.com/anomalyco/opencode"
    title: ""
    accessed_at: "2026-08-06"
contributors: ["pp3g-nHSI-resume-phase-2-154-durable-fork-build-task-on-issue", "pp3g-AMm2-hardening-issue-274-high-value-enforce-upgrade-ffb9"]
created: 2026-08-06
updated: 2026-08-09
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
- INSTALLED (2026-08-08): fork binary LIVE at
  `/home/claude-code/.nvm/versions/node/v22.22.3/lib/node_modules/opencode-ai/bin/opencode.exe`
  (sha256 `3872f6ef7fa0246dde0f2691f72750679655ceaf3224c7cfe05b220621f803d5`,
  148,449,408 B, `--version` = `1.18.13-pp3g-fork`). Pre-fork stock binary
  preserved in place as `opencode.exe.stock-20260808-234726` and in
  `~/.local/share/opencode/fork-backups/20260808-233133/`.

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
  (grep the binary: each present in the compiled output). On the installed
  fork: `grep -c 'Body read timed out'` = **2**, `grep -c 'Turn stalled'` =
  **1** (verified 2026-08-08).
- Runtime log markers: `WARN ... "retry"` per attempt, terminal
  `WARN "retry budget exhausted"`, `ERROR ... Body read timed out`,
  `ERROR ... Turn stalled`.

### Enforced wrapper guard (gh#274, live 2026-08-09)

`~/.local/bin/opencode` is a wrapper that execs the fork binary at the
resolved `REAL` path. Since 2026-08-09 it FAILS CLOSED on fork drift:
before exec it verifies the resolved binary is the fork:

1. `grep -ac 'Body read timed out' "$REAL"` — expect count >= **2**
   (fast, ~0.8s).
2. If the marker count < 2, fall back to `"$REAL" --version` — the
   resolved binary passes only if the version string contains `fork`
   (protects a future rebuild that renames marker strings).

If BOTH fail, the wrapper prints a loud `FATAL: opencode fork identity
check FAILED — refusing to exec.` banner to stderr and exits 1 WITHOUT
exec'ing. A silent upgrade/config loss therefore cannot silently replace
the fork with stock opencode: the guard trips loudly instead. Verified
2026-08-09: stock binary (`--version` 1.18.13, marker count 0) -> FATAL
exit 1; nonexistent path -> FATAL exit 1; live fork -> exec, exit 0.
Backup of the pre-guard wrapper: `~/.local/bin/opencode.pre-guard-20260809`.

Operator drift check (manual, after any opencode upgrade):
`opencode --version` must report `-pp3g-fork` AND the binary markers above
must be present. `grep -c "if(false)return" $(which opencode)` detects the
EPHEMERAL stopgap byte patch (#145/#179), not the fork.


A reconstructable copy of the guarded wrapper is committed at `fork/wrapper/opencode-wrapper` in the ASES repo (identical to the live `~/.local/bin/opencode`; verified diff-clean 2026-08-09). Restore/reinstall: copy it to `~/.local/bin/opencode`, `chmod 755`, and verify `opencode --version` reports `1.18.13-pp3g-fork`.

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

## Upgrade-survival invariant (ENFORCED, not procedural)

The fork must survive opencode self-upgrades. This is now enforced at the
wrapper, not just documented:

- `~/.config/opencode/opencode.json` sets `"autoupdate": false`
  (applied by #179 stopgap; verified present 2026-08-09) so opencode does
  not overwrite the binary on its own. **This is only a config
  short-circuit** — it does not protect against a manual upgrade, config
  loss, or reinstall.
- `~/.local/bin/opencode` (the wrapper on PATH) runs the fork-identity
  drift check above BEFORE exec and REFUSES to exec if the resolved binary
  is not the fork (gh#274). This is the enforcement layer: a silent
  replacement cannot pass unnoticed.
- Any manual upgrade MUST still be followed by the drift check above, and
  the fork build re-applied if the installed binary no longer reports
  `-pp3g-fork`.
- Recovery if the guard trips: re-apply the fork build (below), or restore
  the fork backup and re-verify markers + `--version`; see also the wrapper
  FATAL banner for the exact restore steps.

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

- INSTALLED + VERIFIED live (2026-08-08, #270 3B/3C): installed-binary
  hang gate row1 8/8 PASS (`Body read timed out` + exit 1 not 124 + 3-POST
  budget), healthy regression PASS. Full 16-row matrix green 67/67 vs the
  rebuilt binary (sha 3872f6ef) on #270.
- Wrapper guard live 2026-08-09 (gh#274); drift simulations trip loudly
  (stock / missing path), live fork path passes.
- The interim #179 stopgap byte patch has been superseded by the installed
  fork; the preserved stock binary (with the stopgap byte patch) remains
  as the rollback target.
