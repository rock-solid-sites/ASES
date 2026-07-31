---
title: "model discipline"
tags: []
sources: []
contributors: ["OL2r"]
created: 2026-07-31
updated: 2026-07-31
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
