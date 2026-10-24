---
title: Phoenix Grove subscription 2 — Paseo Codex acceptance report
program: Tooling
layer: Implementation
document_type: Implementation Report
status: Active
authority: Derived
canonical_repository: rock-solid-sites/ASES
depends_on: []
consumed_by: []
related_documents:
  - docs/research/Paseo Role Capability Matrix.md
supersedes: []
superseded_by: []
last_updated: 2026-10-24
---

# Phoenix Grove subscription 2 — configured and verified

Verified on 24 October 2026. Paseo provider **Codex — Phoenix Grove 2** (`codex-pgs2`) is available on IT3812, using the existing native Codex integration and `https://api.pgsgrove.com/v1`. All three requested models passed streamed Responses requests, native shell execution, tool-result handling, and final-answer delivery. DeepSeek is the default model. Reasoning **Off** is the compatibility default. This provider-wide choice addresses MiMo; DeepSeek and GLM also passed with Low and expose that option.

Resumed work through the final audit took **24 minutes 39.690 seconds**, from 08:13:56 to 08:38:35.690 Budapest time. Configuration, execution testing, and the final process capture occupied the first **20 minutes 30.254 seconds**; evidence/report preparation and the six-agent archive audit followed. The earlier inspection and credential handoff are excluded.

## Exact changes

| Location on VPS | Change |
| --- | --- |
| `/home/claude-code/.paseo/config.json` | Added only `agents.providers.codex-pgs2`; mode remains 0600. |
| `/home/claude-code/.paseo/config.json.pre-pgs2-20261024T061722Z` | New mode-0600 backup of the complete original configuration. All older backups remain unchanged. |
| `/home/claude-code/.local/bin/codex-pgs2` | New mode-0700 launcher that validates and reads the protected credential, then executes the pinned Codex binary. |
| `/home/claude-code/.paseo/codex-pgs2/` | New mode-0700 dedicated Codex home, separating session state from native ChatGPT Codex. |
| `/home/claude-code/.paseo/codex-pgs2/config.toml` | New mode-0600 configuration with `model_reasoning_effort = "none"`. |
| `/home/claude-code/.secrets/paseo-pgs2.key` | User-installed credential retained, owned by `claude-code`, mode 0600, inside an owned mode-0700 directory. Its contents were never displayed or committed. |

The exact secret-free provider fragment is in [codex-pgs2-provider.json](codex-pgs2-provider.json). The installed launcher is reproduced in [codex-pgs2-launcher.py](codex-pgs2-launcher.py). This is the essential configuration:

```json
{
  "extends": "codex",
  "label": "Codex — Phoenix Grove 2",
  "command": ["/home/claude-code/.local/bin/codex-pgs2"],
  "env": {
    "OPENAI_BASE_URL": "https://api.pgsgrove.com/v1",
    "OPENAI_API_KEY": "loaded-by-codex-pgs2-wrapper",
    "CODEX_HOME": "/home/claude-code/.paseo/codex-pgs2"
  },
  "models": [
    {
      "id": "deepseek-v4.1-flash-1017",
      "label": "DeepSeek V4.1 Flash 1017",
      "isDefault": true,
      "thinkingOptions": [
        {"id": "none", "label": "Off", "isDefault": true},
        {"id": "low", "label": "Low"}
      ]
    },
    {
      "id": "mimo-v2.6-flash",
      "label": "MiMo V2.6 Flash",
      "thinkingOptions": [
        {"id": "none", "label": "Off", "isDefault": true}
      ],
      "description": "Use reasoning Off; low reasoning did not return final text in compatibility tests."
    },
    {
      "id": "glm-5.3-flash",
      "label": "GLM 5.3 Flash",
      "thinkingOptions": [
        {"id": "none", "label": "Off", "isDefault": true},
        {"id": "low", "label": "Low"}
      ]
    }
  ]
}
```

`loaded-by-codex-pgs2-wrapper` is an intentional **nonsecret marker**, not the API key. This installed Paseo build requires a nonempty provider-environment value to select API-key authentication. The launcher replaces the marker with the real key before executing Codex. Process inspection confirmed the actual child received the correct key and base URL, recording booleans only.

Final configuration SHA-256: `6216ff05758d98fd70326f1e265e70348eae81725fb3541f381d9c1f433e9ad1`.

Pre-change backup SHA-256: `a35ed244385413fbb5dc8f9992f494246b201ad40f9b32dd3d6addf995d6933d`.

## Verified implementation and preservation

The installed `rock-solid-sites/paseo/docs/operations.md`, patched source, compiled Codex adapter, provider schema, and command-launch code were inspected. Compatibility conclusions use the installed implementation, rather than current upstream documentation.

- Paseo remains **0.11.0-beta.4** at clean commit `6108e714bd5d5b2bdb2fb6e0c6fb1535396bbb1f`.
- Codex remains **0.157.1**, pinned by the launcher to `/home/claude-code/.codex/packages/standalone/releases/0.157.1-x86_64-unknown-linux-musl/bin/codex`.
- The compiled adapter explicitly constructs a custom provider with `wire_api = "responses"`, the normalized `/v1` base URL, `env_key = "OPENAI_API_KEY"`, and `requires_openai_auth = false`.
- The installed schema accepted the new provider. Both applications of `paseo reload --json` reported only `agents.providers` applied and an empty `restartRequiredPaths` list. The suggested restart command printed by reload was not executed.
- Service launcher PID stayed **3917442**, `NRestarts` stayed **0**, and the existing service remained active. Final `/api/status` returned beta.4 at `127.0.0.1:6767`.
- Fourteen watched files retained identical hashes and permission modes: native Codex authentication/configuration, VPS OpenCode settings/authentication, the systemd unit, all six older configuration backups, and the three specialist overlay files.
- Removing only `codex-pgs2` from the final configuration reproduces the entire original configuration. All four ASES profiles and their permission restrictions therefore remain unchanged.
- No source patch, upgrade, service restart, quota rotation, shared API-key environment, unrelated provider edit, or new ChatGPT login was introduced. The dedicated Codex home contains no `auth.json`.

## Model and execution evidence

Authenticated `/v1/models` discovery returned all three exact IDs. Each then passed an HTTP-200 `text/event-stream` Responses test with a function call and a subsequent function-result response. Each model also executed the real native Codex `exec_command` tool through Paseo.

The initial DeepSeek session wrote and read `native-marker.txt`; its contents were exactly `PGS2_NATIVE_TOOL_OK\n`. Subsequent native sessions read that marker with exit code 0 and returned exactly `PGS2_NATIVE_OK`.

These are successful native tool turns with the final **Off** default:

| Model ID | Native turn time | Input tokens | Cached input subset | Output tokens | Evidence agent |
| --- | ---: | ---: | ---: | ---: | --- |
| `deepseek-v4.1-flash-1017` | 2.307 s | 16,245 | 8,242 | 49 | `4dd6873f-2d4b-4c7f-8508-e264c16faa1c` |
| `mimo-v2.6-flash` | 85.539 s | 15,905 | 15,666 | 94 | `7c3e8aec-fbff-42bf-84e0-6c55f64ace60` |
| `glm-5.3-flash` | 3.303 s | 15,537 | 0 | 31 | `cb7662e5-15bd-4708-8d07-9ec420aeb328` |

Native turn times come from Codex's completion events. DeepSeek's complete CLI invocation took 4.072 seconds; GLM's took 4.640 seconds. MiMo's successful tool turn was the second turn in a session whose first text-only check took 34.693 seconds and used another 7,809 input / 8 output tokens. That full MiMo session used 23,714 input / 102 output tokens.

Token figures above include both inference requests in each tool round trip. They are derived from cumulative native usage events, with the preceding turn subtracted for MiMo. Cached input and reasoning output are subsets, not extra tokens. Paseo's `LastUsage` alone describes the last inference response and would undercount the full tool turn. Cost fields reported as zero are not treated as proof of free Phoenix Grove usage; exact billed charges were not available.

DeepSeek and GLM also passed native tests with Low reasoning. MiMo with Low reasoning executed its tool, but omitted its final answer in two checks. Off restored both text-only answers and tool-result completion. The picker therefore exposes only Off for MiMo. This is an observed compatibility setting, not a claim that the gateway defect is fixed upstream.

The first generic Python HTTP client was blocked with edge error 403/1010. Requests identifying the Codex client succeeded. The real installed Codex client worked without an edge-filter workaround.

## Memory and retained processes

Completed, unarchived sessions retained one Codex app-server process each. Before final archival, the three dedicated processes were:

| PID | RSS | Process high-water RSS |
| --- | ---: | ---: |
| 3944838 | 147,752 KiB | 150,224 KiB |
| 3945364 | 148,236 KiB | 148,952 KiB |
| 3945537 | 148,680 KiB | 149,972 KiB |

Their combined RSS was **434.25 MiB**. High-water figures are the kernel's per-process `VmHWM` values; they are not service-wide peaks or summed simultaneous peaks.

The service group measured **2.763 GiB** before final archival and **2.683 GiB** afterward. Its task/thread count changed from 487 to 418. These samples include other existing workloads; they are not an isolated attribution of all memory changes to this task.

All six disposable agents were archived, across the initial and final verification phases. After archival, **zero dedicated Phoenix Grove 2 Codex processes remained**. Two unrelated pre-existing Codex processes were left untouched. The original visible agent-state counts returned to six idle and 48 closed, with no executing agents. No service restart was used to release test processes. The temporary marker workspace remains under `/tmp/paseo-pgs2-smoke-20261024` as disposable evidence.

## Independent selection and remaining limits

Paseo's live catalog lists **Codex — Phoenix Grove 2**, **Codex**, and **OpenCode** as separately available providers, along with all four available ASES providers. The new provider has its own endpoint, protected key, launcher, model catalog, and Codex home. Native ChatGPT authentication was checksum-verified unchanged.

The operator confirmed subscription 1 lives in **Windows desktop OpenCode**. No Windows provider settings or credentials were written. Access to its standard protected configuration remained unavailable, even after a specific read grant; accessible metadata did not establish its Phoenix Grove route. Consequently this task confirms independent provider registration on the VPS and preservation of the desktop setup, but does **not** claim a fresh GUI selection or inference test of desktop subscription 1. No subscription 1 credential was reused.

The provider retains Codex's existing Default Permissions, Auto-review, and Full Access modes. Acceptance used **Default Permissions** (`auto`) in the disposable workspace; it does not establish compatibility of automatic approval-review subagents with this gateway. The existing beta.4/desktop version limitations in the operations guide still apply.

The launcher is intentionally pinned to the tested Codex binary path. A future deliberate CLI replacement would require reviewing that path; no upgrade was performed here.

One diagnostic metadata read included Paseo's existing local MCP bearer credential in tool context. It is excluded from the saved evidence and report. The Phoenix Grove API key was never displayed, and checks confirmed it appears in neither Paseo configuration nor the verification files. No daemon credential rotation was attempted, as that would affect existing consumers.

## Evidence artifacts

- [Final verification: native events, usage, memory, preservation and provider catalog](final-verification.json)
- [Authenticated model discovery and streamed Responses probes](api-probes.json)
- [Exact installation manifest and configuration hashes](installation.json)
- [Provider configuration fragment without secrets](codex-pgs2-provider.json)
- [Installed protected-credential launcher](codex-pgs2-launcher.py)
- [Independent Luna review](independent-review.md)

The VPS retains the sanitized evidence under `/home/claude-code/.paseo/verification-pgs2-20261024/`, mode 0700, with evidence files mode 0600. A Luna medium subagent reviewed the credential handoff and final evidence; delegation pricing was unavailable in tool metadata.
