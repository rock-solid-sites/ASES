---
updated: 2026-08-18
---

# Model Discipline

OpenCode has two distinct provider categories with different cost and reliability profiles. Agents constantly confuse them. This page documents the rules.

## Go (paid) vs Zen (free)

| | OpenCode Go | OpenCode Zen / Free tier |
|---|---|---|
| **Provider prefix** | `opencode-go/` | Varies by model |
| **Cost** | Paid per token | Free (rate-limited) |
| **Reliability** | Production-grade | May hit rate limits, slower |
| **Use for** | Agent work, kickoff, swarm | Quick interactive sessions only |

## Mandatory Rules

1. **Never assume a model ID.** Always verify with `opencode models <provider>` before using any model.

2. **Ask the operator which provider to use.** Do not pick a provider on your own. The operator decides based on cost, reliability, and access.

3. **Do not use free-tier models for kickoff or swarm agents.** Rate limits will cause agents to hang or fail mid-task.

4. **Use the full verified model ID.** Copy it exactly from `opencode models`. Do not guess, shorten, or modify.

## Standing Facts (Operator-Stated, 2026-08-18)

1. **Only OpenCode credits exist — there are NO OpenRouter credits.** OpenRouter is NOT an available provider for agent work. Only models reachable via OpenCode's own providers ('opencode/' free Zen and 'opencode-go/' paid) are in scope, unless the operator explicitly states otherwise. Do NOT propose, dispatch, or reason about OpenRouter routes. Do NOT list openrouter/* model IDs in this page.

2. **Google models are always served from Vertex AI** (prefix 'google-vertex/'). Never dispatch a Google model via any other provider route (e.g. never openrouter/google/*). The Google Vertex AI section of this page is the authoritative home for google model IDs.

3. **The OpenCode website NEVER displays full model IDs.** The Zen page lists only which models are *available*, never their exact IDs. Full model IDs are obtainable ONLY by querying the Zen catalog API (https://opencode.ai/zen/v1/models) — an agent-scoped task: a builder/agent fetches the API and reports exact IDs. The operator cannot and will not paste model IDs from the website. When a model is not in the local 'opencode models' cache, agents MUST query the Zen API themselves rather than asking the operator for IDs.

**NOTE:** `opencode models` refreshes from models.dev, which LAGS BEHIND the Zen API. Absence of a model from `opencode models` output does NOT mean the model is unavailable on Zen — the Zen catalog API is authoritative for Zen availability.

## Forbidden and Restricted Models

- **xAI / Grok — STRICTLY AND PERMANENTLY FORBIDDEN.** xAI models (grok-4.5
  and the grok family) are never to be used for any role. This is the
  standing rule (violation precedent: #249 recorded 'never use Grok/xAI').
  The models are patched out of the model catalog — `opencode models
  opencode-go` must not list them. Do not launch agents with a grok/xAI
  model ID even if one is visible in the catalog; report it instead.
- **Kimi — NOT forbidden.** `opencode-go/kimi-k2.7-code` works and has been
  used successfully (e.g. #317/#322). The only caveat is cost: **kimi-k3 is
  extremely expensive** — cost-based caution applies, not a ban.

## Failure Discrimination — Rate Limit vs Silent Hang

**Free-model failures are NOT always rate limits.** Do not assume a stalled
free/paid agent is rate-limited. On a stalled agent, check
`~/.local/share/opencode/log/opencode.log` for the error signature before
declaring the cause:

- **Rate limit = `Provider rate limit exceeded` / `429`** entries in the log.
- **Hang = an outgoing stream request with no response and no error** — the
  last log line for the session is an outgoing `message=stream` (or similar
  request) that never completes, with zero `level=ERROR` entries after it.

Do not assume a rate limit hits all free models at once — other free models in
the same window may complete normally.

**Example (laguna #129, 2026-08-03):** the 'stalled' laguna reviewer
(`laguna-s-2.1-free`, session `ses_03aa886c0ffeXKFRLMhDrbTNyd`) had ZERO
`level=ERROR` entries in its session log — the last event was an outgoing
`message=stream` request at 02:01:30 that never completed, with no error.
Historical laguna rate-limit incidents (July 23-26) all logged `Provider rate
limit exceeded`, which was absent here. Ling + big-pickle + nemotron completed
the same review in the same window on the same free tier. Conclusion: the
laguna freeze was a silent provider-side hang, NOT a rate limit.

## Provider Links

- OpenCode Go plan (paid): https://opencode.ai/docs/go/
- OpenCode Zen (incl. free models): https://opencode.ai/docs/zen/
- Providers overview: https://opencode.ai/docs/providers/
- Zen pricing (free model list): https://opencode.ai/docs/zen#pricing
- Zen model catalog API: https://opencode.ai/zen/v1/models
- Go model catalog API: https://opencode.ai/zen/go/v1/models

## Currently Verified Models

Run `opencode models` for the authoritative list. The IDs below are examples only and may be stale:

### OpenCode Go
```
opencode-go/deepseek-v4-pro
opencode-go/deepseek-v4-flash
opencode-go/mimo-v2.5
opencode-go/mimo-v2.5-pro
opencode-go/glm-5.2
opencode-go/hy3
```

### OpenCode Zen free models (whitelist, issue #103)
```
opencode/big-pickle
opencode/deepseek-v4-flash-free
opencode/laguna-s-2.1-free
opencode/ling-3.0-flash-free
opencode/mimo-v2.5-free
opencode/nemotron-3-ultra-free
opencode/north-mini-code-free
```

The Zen provider is whitelisted to exactly these free models in `~/.config/opencode/plugins/plugin.ts` and `dynamic-models.ts`. Paid Zen models are not exposed because no Zen API credits are used.

### Google Vertex AI
```
google-vertex/gemini-3.1-pro-preview
google-vertex/gemini-3.5-flash
google-vertex/gemini-2.5-pro
```

### Cohere
```
cohere/north-mini-code-1-0
```

## Configuration

Models are configured in `.crosslink/hook-config.json`:

```json
"sentinel": {
    "default_agent": {
        "model": "opencode-go/deepseek-v4-flash"
    }
}
```

Or passed via CLI:
```bash
crosslink kickoff run "description" --model opencode-go/deepseek-v4-flash
```

The `claude` wrapper enforces STRICT MODEL ENFORCEMENT — launches with invalid or implicit models are blocked.

## Request Timeout Configuration

Opencode per-API-request timeouts are configured in
`~/.config/opencode/opencode.json` — a **USER-LEVEL GLOBAL** file, NOT an
in-repo file. This is deliberate: the `claude` wrapper execs `opencode run`,
and user-level config reaches every kickoff/swarm agent, while a project-level
`.opencode/opencode.json` would only affect sessions started inside that repo.
Do not look for this configuration in the repository.

**Schema:** timeouts nest under `provider.<id>.options.*` — NOT directly
under `provider.<id>` (verified against the live opencode 1.18.11 schema):

```json
{
  "provider": {
    "opencode": {
      "options": {
        "timeout": 3600000,
        "headerTimeout": 300000,
        "chunkTimeout": 300000
      }
    },
    "opencode-go": {
      "options": {
        "timeout": 3600000,
        "headerTimeout": 300000,
        "chunkTimeout": 300000
      }
    }
  }
}
```

**Current values (same for providers `opencode` and `opencode-go`):**

| Key | Value | Meaning |
|-----|-------|---------|
| `timeout` | `3600000` ms (60 min) | Full-request backstop; generous, never aborts legitimate work |
| `headerTimeout` | `300000` ms (5 min) | Connect/header window; absorbs provider cold-start / queueing |
| `chunkTimeout` | `300000` ms (5 min) | Hung-stream cure: aborts if no SSE chunk within 5 min |

**Rationale for a 5-min `chunkTimeout`:** deepseek-v4-* reasoning models
legitimately emit sparse chunks during long chains of thought; 5 minutes
exceeds the worst-case legitimate inter-chunk gap while still catching the
observed hang fingerprint (a silent stream with no chunk for 10+ minutes).
It is kept well above the 120s heartbeat throttle so normal cadence never
triggers a false abort.

**Do not confuse this with the playbook §5.3 task-matched timeout.** The
§5.3 timeout is the agent's runtime ceiling (`--timeout` on `crosslink
kickoff run` / `crosslink swarm launch`) — how long the whole agent session
may run. The request timeout configuration here is the **per-API-request**
timeout inside opencode — how long a single provider call (including each
SSE chunk gap) may take before opencode aborts it. Both are needed: the
request timeouts stop individual hung provider calls, the §5.3 runtime
timeout bounds the overall agent session.
