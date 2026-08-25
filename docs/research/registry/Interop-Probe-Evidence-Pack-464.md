---
title: Interop Probe Evidence Pack — crosslink-drives-v2-headless (Issue #464)
document_type: Evidence Record
status: Probe-complete
date: 2026-08-25
issue: "Crosslink #464 (EPIC #423 R0b/F2)"
runs: pp3g-KXdh (T1–T4) + pp3g-OgQA (T5a–T5d)
target: opencode2 v0.0.0-beta-17963
---

# Interop Probe Evidence Pack — #464

Verdict and full claim discipline live in the Crosslink issue #464 result
comment. This file preserves the raw evidence and the exact reconstruction
commands so the probe is reproducible after `/tmp/opencode/probe-v2/` is
reclaimed.

## Environment

- Binary: `opencode2 v0.0.0-beta-17963` (`~/.nvm/versions/node/v22.22.3/bin/opencode2`)
- Background service: `opencode2 serve --service`, long-lived (PID 2179167, up since 2026-08-24)
- Scratch: `/tmp/opencode/probe-v2/` (prior run pp3g-KXdh + continuation)

## T1–T4 (prior run pp3g-KXdh; artifacts re-verified from scratch)

| Test | Command pattern | Result |
|---|---|---|
| T1 plain headless | `opencode2 run "Reply with exactly: PROBE-T1-OK"` | exit 0, `PROBE-T1-OK` |
| T2 explicit model | `opencode2 run --model opencode-go/ox-alpha-free "…PROBE-T2-OK"` | exit 0, banner `> build · ox-alpha-free` |
| T3 JSON stream | `opencode2 run --format json …` | NDJSON events (`step_start`, `text`) each carrying `sessionID` |
| T4 AGENTS.md pickup | canary line in cwd `AGENTS.md` | `CANARY-AGENTSMD-V2` echoed in reply |

## T5a — plugin loading scope

Setup: git repo `/tmp/opencode/probe-v2/proj-t5a` with
`.opencode/plugins/t5a-canary.js` writing a marker at module top-level
(`factory-invoked`) and inside the default-export factory
(`factory-returned`). File exists ONLY in that project.

Findings:

1. **Project plugins auto-load.** Marker `factory-invoked` written during
   headless run in that cwd; no config listing involved.
   - Caveat: `process.cwd()` inside plugin = `/home/claude-code`
     (background-service root), not the session directory.
2. **Global dir fallback does NOT load.** Temporary canary placed at
   `~/.config/opencode/plugins/zz-probe-t5a-canary.js` produced NO marker
   during a v2 run that DID fire the project canary. (Canary removed after test.)
3. **Global config `plugin[]` parsed but not executed.**
   `GET /api/config` shows the global document loaded with
   `"plugins":["./plugins/plugin.ts","./plugins/interrupt.ts"]`, yet:
   - `opencode2 models` (688 lines): grok present
     (`cloudflare-ai-gateway/xai/grok-4.5` etc.), cloudflare-ai-gateway
     deepseek/openai present.
   - `opencode models` on the v1 fork (722 lines): 0 grok matches, no
     cloudflare-ai-gateway — because fork executes `plugin.ts`, which
     disables those providers and blacklists grok
     (`~/.config/opencode/plugins/plugin.ts`, FORBIDDEN MODEL PATTERNS block).
4. **Plugin load cached per service lifetime.** Second headless run in the
   same project did NOT re-fire the marker; the long-lived background
   service loads plugins once.

Reconstruction:

```bash
mkdir -p /tmp/probe/.opencode/plugins && cd /tmp/probe && git init -q
cat > .opencode/plugins/canary.js <<'EOF'
const fs=require("fs");
try{fs.appendFileSync("/tmp/marker.txt",JSON.stringify({event:"top-level",cwd:process.cwd()})+"\n")}catch(e){}
export default async()=>({try:fs.appendFileSync("/tmp/marker.txt","factory\n")});
EOF
opencode2 run --model opencode-go/ox-alpha-free "say OK"; cat /tmp/marker.txt
```

## T5b — permission model shape

Schema (from beta openapi, `components.schemas`):

- `Permission.Rule` = `{action: string, resource: string, effect: "allow"|"deny"|"ask"}` (all required)
- `Permission.Ruleset` = array of rules; attaches to Config `permissions` and per-agent `Agent.Info.permissions`
- `Permission.Request` = `{id:"per…", sessionID:"ses…", action, resources[], save[], metadata, source{type:"tool",messageID,id}}`
- `Permission.Reply` = `"once"|"always"|"reject"`

Live behavior (project config `.opencode/opencode.json` with
`{"permissions":[{"action":"shell","resource":"*","effect":"<E>"}]}`):

| Effect | Observed |
|---|---|
| *(none)* | shell tool runs freely, incl. `cat /etc/hostname` (exit 0) |
| `deny` | shell tool removed from toolset entirely; model: "I don't have a shell/bash tool in this environment" |
| `ask` | also hidden statically; runtime asks still fire for native-fs paths outside project root → **headless auto-rejects, fail-closed**: stderr `permission requested: external_directory (/etc/*); auto-rejecting`, exit≠0, never hangs |
| `ask` + `--auto` | ask auto-approved; shell + `/etc` read succeed (exit 0) |

Two-layer model: static ruleset filters tools at session build; runtime
asks (e.g. action `external_directory` when fs tools touch paths outside the
project root) fire as requests. Sandbox surface in spec = `Project.sandboxes:
string[]` only.

## T5c — live API drive

Server: `setsid nohup opencode2 serve --hostname 127.0.0.1 --port 49155 &`
→ prints `server password <PW>`; all routes require Basic auth
(`opencode:<PW>`); unauthenticated → HTTP 401.

Proven drive loop (all HTTP 200/204):

```bash
B=http://127.0.0.1:49155; A="-u opencode:$PW"
SID=$(curl -s $A -X POST $B/api/session -H 'Content-Type: application/json' \
      -d '{"title":"T5C-DRIVE"}' | jq -r .data.id)
curl -s $A -X POST $B/api/session/$SID/prompt -H 'Content-Type: application/json' \
      -d '{"text":"Reply with exactly: PROBE-T5C-DRIVE-OK"}'        # async submit, delivery:"steer"
curl -s $A -X POST $B/api/session/$SID/wait -d '{}'                 # -> 204 when idle
curl -s $A $B/api/session/$SID/message                              # assistant content: "PROBE-T5C-DRIVE-OK"
```

- `prompt_async`: **0 matches** in the full beta openapi (100 route paths) — truly absent.
- Replacement contract: prompt (async submit) + wait (block till idle);
  `GET /api/event` is an SSE stream (`data: {…}` + `: heartbeat`) for
  push consumption.
- API-driven sessions land in `session_v2` of
  `~/.local/share/opencode/opencode.db` (verified by direct sqlite read;
  id match). Fork store `opencode-fork-pp3g.db` untouched.
- Session model defaults to build agent's default (deepseek) unless pinned
  via `model` key in `POST /api/session` body.
