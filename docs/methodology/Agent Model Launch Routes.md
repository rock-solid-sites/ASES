---
title: Agent Model Launch Routes — Cross-Environment
program: ASES
layer: Methodology
document_type: Operational Runbook
status: Active (dated environment snapshot)
authority: Informative
canonical_repository: ases
version: 1.0.0
date: 2026-10-31
last_verified: 2026-10-31
depends_on:
  - AGENTS.md
  - docs/ORCHESTRATOR.md
  - skills/prompt/SKILL.md
related_documents:
  - docs/research/registry/Model-Routing-Matrix.md
---

# Agent Model Launch Routes — v1.0.0 (2026-10-31)

**Purpose:** provide a selected, concrete route for agents launched from Codex Desktop, Codex Cloud, OpenCode Desktop, ChatGPT/MCP, Paseo, or directly on the IT3812 VPS, avoiding repeated route discovery. The VPS commands below come from a working review, not a fresh live probe by this author.

**Provenance:** source report on branch `docs/model-launch-routes-guide` at `3130d9b8b436b461495fbfd553d23f92a4464bdd`; independent F3 L5 review at `831f2bb9c1fe6b30e09520acb249043b72a29bc0`. Related October failures (missing ChatGPT Codex Tasks control actions, Codex sessions unable to reach VPS, an agent repeatedly closing the user's local OpenCode app) are operator-reported; this runbook does not claim to have reproduced them.

## 1. Resolve the control surface before invoking a launcher

Four separate coordinates must be fixed by the **caller**, not rediscovered by the receiving agent:

| Coordinate | Choices / examples | Significance |
| --- | --- | --- |
| Controller | Codex Desktop, Codex Cloud, OpenCode Desktop, ChatGPT, Paseo, Windows SSH, VPS shell | Where the parent agent or human starts |
| Execution host | IT3812 VPS, Windows laptop, hosted Codex Cloud | Where commands, code and files actually run |
| Launcher | `codex-pgs2`, `opencode` pp3g fork, `opencode2` preview, Paseo profile | Executable and credentials |
| Target provider/model | `pgs2/glm-5.3-flash`, `opencode/mimo-v2.6-flash-free`, etc. | Authorized child route; record actual result outside child prompt |

**Environment-specific entry points:**

- **Already on the VPS:** execute in-place in `/home/claude-code/projects/ASES` using the absolute launcher paths in `3`. Do not SSH from the VPS to itself.
- **Windows controller with configured SSH:** `ssh it3812` reaches IT3812 (Ubuntu, `claude-code`; custom SSH port in *client* configuration). The alias is client-local, not a global network name. Use `2` for complex PowerShell-to-Bash commands. A single `ssh -G it3812` check can distinguish an absent client alias from a remote error.
- **Codex Desktop remote:** its SSH-launched remote Codex app-server is distinct from the Codex CLI and the Codex Cloud service. If the active session actually executes on IT3812, use VPS-local launchers; verify the remote host once, not by opening new exploratory SSH connections.
- **OpenCode Desktop:** the active app session may be local or connected remotely. Its **actual execution host** determines whether to use VPS-local commands or the Windows SSH entry. A general OpenCode Desktop→VPS route was not independently verified here: do not assume it inherits Paseo or Codex Desktop settings.
- **Paseo Desktop:** an SSH remote IT3812 connection and agent profiles have been observed; Paseo sessions are distinct from direct native Codex/OpenCode launches. Don't assume a daemon/profile installed in one controller is exposed in another.
- **Codex Cloud:** runs in a separate, disposable GitHub-backed environment. No automatic access to the Windows `it3812` alias, Tailscale, VPS credential, local daemon, or persistent worktree. Use a branch/commit handoff unless a separate VPS route is explicitly authorized and **verified**.
- **ChatGPT/MCP:** GitHub read/write access is not shell or agent-launch access. The Codex Tasks skill was previously discoverable while its `list_tasks`/`read_task` tools were absent. Check actual exposed actions before claiming task access; if missing, record that control-plane blocker instead of fabricating a VPS route.

**Routing precedence:** chosen execution host and authorized route → minimal non-destructive verification → task execution. An available alternative is **not** permission to substitute it. A previous model or fallback approval applies only to its stated scope.

### Caller-only dispatch record (never paste as receiver self-identification)

```yaml
controller: windows-ssh | codex-desktop-remote | opencode-desktop | vps-shell | codex-cloud | chatgpt-mcp
execution_host: IT3812 | codex-cloud-container
entry: in-place | ssh-it3812 | cloud-git-branch
launcher: codex-pgs2 | opencode-pp3g | opencode2 | approved-paseo-profile
receiver_model: <selected at launch only, outside receiving prompt>
authorized_child_routes: [<exact approved provider/model targets>]
approved_fallbacks: []  # unless specifically authorized for this task
workspace: /home/claude-code/projects/ASES
pinned_source: <commit>
output_branch: <unique branch>
completion: <tests/evidence + verified remote SHA>
```

**Prompt invariant:** Never tell an agent which model, provider, model family or reasoning-effort level *it is*, and never ask it to identify or verify its own routing. Configure these in the caller/launcher and preserve provenance there. A coordinating agent *may* receive exact provider/model routes for the **child agents it is authorized to dispatch**. Include the selected host/launcher route in its prompt when the route matters; do not assign it a new routing investigation. Example: `Work in-place on IT3812 using the pinned source and the `codex-pgs2` launcher described in this guide; report a blocker rather than changing providers.`

## 2. Shell quoting is the number one source of failure

**Only for Windows-driven SSH sessions:** the driver shell observed was Windows PowerShell 5.1. It expands subexpressions, backticks
and quotes before the string reaches the remote bash, which silently corrupts
heredocs, for-loops and python one-liners.

Reliable pattern: write the remote script to a local file, base64-encode it,
then decode it on the VPS.

```powershell
$script = Get-Content -Raw .\task.sh
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($script))
ssh it3812 "echo $b64 | base64 -d > /tmp/task.sh && bash /tmp/task.sh"
```

Rules that follow from this:

- Never put subexpressions, variables or backticks inside a double-quoted
  ssh it3812 "..." command that also needs remote expansion. Use the base64
  pattern instead.
- When a remote command will create or observe files, write helper scripts to
  the VPS rather than trying to inline them.
- Pass multi-line prompts to models via files on the VPS, not as giant quoted
  arguments.
- A PowerShell here-string used to hold the script must not contain a line that
  begins with the here-string terminator at column zero. If it does, the string
  closes early and parsing fails. Prefer reading the script from a file.

## 3. Model launchers available on the VPS

There are three distinct execution stacks. Know which one you are using.

### 3.1 codex-pgs2 - Codex CLI against the Phoenix Grove gateway

This is the route to the Phoenix Grove (pgs2) subscription models. It is a
Python wrapper that loads the subscription-2 key and execs a pinned Codex build.

- Wrapper: /home/claude-code/.local/bin/codex-pgs2
- Key: ~/.secrets/paseo-pgs2.key (loaded by the wrapper; do not print it)
- Endpoint: https://api.pgsgrove.com/v1
- Codex home: ~/.paseo/codex-pgs2
- Models: glm-5.3-flash, mimo-v2.6-flash, deepseek-v4.1-flash-1017

Critical: the wrapper sets OPENAI_BASE_URL, but the pinned Codex build does not
use it on its own and falls back to api.openai.com (401). You must inject a
provider on every run:

```bash
/home/claude-code/.local/bin/codex-pgs2 exec \
  -m glm-5.3-flash \
  -s read-only --skip-git-repo-check \
  -c 'model_providers.pgs2.name="pgs2"' \
  -c 'model_providers.pgs2.base_url="https://api.pgsgrove.com/v1"' \
  -c 'model_providers.pgs2.env_key="OPENAI_API_KEY"' \
  -c 'model_providers.pgs2.wire_api="responses"' \
  -c 'model_provider="pgs2"' \
  "PROMPT" </dev/null
```

Notes:

- Always redirect stdin with </dev/null. Without it the process hangs on
  "Reading additional input from stdin...".
- The model_provider="pgs2" override plus the four model_providers.pgs2.* keys
  are mandatory; dropping any leaves you pointed at OpenAI.
- -s selects the sandbox: read-only for audits, workspace-write when the model
  must write a report file.
- Phoenix Grove subscriptions have a daily allowance. On exhaustion the gateway
  returns HTTP 402 Payment Required with a refill timestamp. Do not retry in a
  loop; stop or request an explicitly approved fallback. A prior fallback is not standing permission.

### 3.2 opencode - the pp3g fork (free models)

- Binary: /home/claude-code/.opencode/bin/opencode
  (invoke by absolute path; opencode is not reliably on the non-interactive
  PATH)
- Providers: opencode and opencode-go only.
- Free models (cost 0), verified working:
  - opencode/mimo-v2.6-flash-free
  - opencode/glm-5.3-flash-free
- Also listed (untested here): opencode/deepseek-v4.1-flash-free,
  opencode/beam-free, opencode/nemotron-3.5-lightning-free,
  opencode/flint-40b-free, opencode-go/beam-free,
  opencode-go/iceman-contributor-free, and many openrouter/*:free.
- Known-broken entry: opencode/ling-3.0-flash-fin-free (Model not found).

List available models:

```bash
/home/claude-code/.opencode/bin/opencode models | grep -i free
```

Run a review headlessly (JSONL output so the result is capturable non-TTY):

```bash
/home/claude-code/.opencode/bin/opencode run --format json \
  -m opencode/mimo-v2.6-flash-free \
  "PROMPT" </dev/null > /tmp/out.jsonl 2>/tmp/err.log
```

Extract the final text from JSONL:

```bash
python3 -c 'import json;print("".join(json.loads(l)["part"].get("text","") for l in open("/tmp/out.jsonl") if json.loads(l).get("type")=="text"))'
```

Notes:

- Non-TTY runs print nothing to stdout unless --format json is used; rc=0 with
  empty output is normal otherwise.
- Large prompts cause exploration instead of a final answer. Prefer a compact
  single prompt with the evidence embedded inline, and instruct the model to
  "write the report file now", rather than pointing it at many repo files.
- There is no Phoenix Grove provider in this stack.

### 3.3 opencode2 - OpenCode 2.0 preview (@opencode-ai/cli)

A separate, newer build. It is not found by default non-interactive PATH
searches because it lives under nvm:

- Binary: /home/claude-code/.nvm/versions/node/v22.22.3/bin/opencode2
  (symlink to @opencode-ai/cli/bin/opencode2.exe)
- Version: 0.0.0-beta-19271 (OpenCode 2.0 preview)
- Logged-in providers: OpenCode Go, Anthropic, Cerebras, Cohere, Google, Groq,
  Mistral, Ollama Cloud, OpenAI, OpenCode, OpenRouter, SambaNova.
- No Phoenix Grove provider.
- Different CLI shape: opencode2 <subcommand> [flags] [directory], with
  --prompt, --standalone, and acp/api/debug subcommands.
- Exposes about 550 models (e.g. opencode-go/glm-5.3-flash,
  mistral/zai-glm-5-3, ollama-cloud/mimo-*).

Verify it is reachable only via an absolute path or a login shell:

```bash
bash -lic 'command -v opencode2'
/home/claude-code/.nvm/versions/node/v22.22.3/bin/opencode2 --version
```

Discovery pitfall: opencode2 will not appear via find -maxdepth 4 under the home
directory or in a non-interactive ssh it3812 "command -v ...". Check nvm bin
directory and the login shell PATH explicitly.

### 3.4 Paseo agent profiles (optional orchestration layer)

~/.paseo/config.json defines agent profiles (ases-orchestrator, ases-builder,
ases-reviewer, ases-researcher, codex-pgs2, etc.). These are convenience
wrappers for long-lived sessions; for one-shot reviews it is simpler and more
transparent to call codex-pgs2 or opencode directly as in sections 3.1-3.3.

## 4. Choosing a route

- Need Phoenix Grove models (GLM/MiMo/DeepSeek pgs2): use codex-pgs2 (section
  3.1) with the full provider override.
- Need a free/zero-cost cross-check: use opencode free models (section 3.2), or
  opencode2 opencode-go/* models (section 3.3).
- Phoenix Grove returns 402: the daily allowance is spent. Either wait for the
  refill timestamp in the error, or seek operator approval for an exact free route.
  Do not change provider/model without authorization. Record the actual launch
  route and any permitted substitution; do not mislabel a free-endpoint review.

## 5. Reproducing a clean-room review on this environment

A pattern that worked end to end:

1. From the laptop, create an isolated worktree on the VPS from the exact
   pinned commit:

   ```bash
   cd ~/projects/ASES
   git fetch origin <commit>
   git worktree add -b review/<name> ~/reviews/<name> <commit>
   ```

2. Read pinned artifacts with git show <commit>:<path> or from the worktree.
   Do not read RESULT.md, OBSTRUCTION.md, prior *REVIEW*/*AUDIT* files, or other
   reviewers output before recording an independent verdict.
3. Re-run the verifier and the implementation in an isolated disposable copy
   under /tmp (e.g. cp -a lifecycle /tmp/repro), never editing the pinned source
   or recorded raw observations.
4. Run independent model reviews (section 3) with a compact self-contained
   prompt; each writes its report to its own /tmp/<model>-review.md.
5. Copy reports into the worktree, commit only the report(s), push the branch,
   and verify the remote SHA with: git ls-remote origin <branch>
6. Leave main and all existing worktrees untouched.

## 6. Quick reference of paths

| Purpose | Path |
| --- | --- |
| Phoenix Grove launcher | /home/claude-code/.local/bin/codex-pgs2 |
| Phoenix Grove key | ~/.secrets/paseo-pgs2.key |
| Codex (pgs2) home | ~/.paseo/codex-pgs2 |
| opencode fork binary | /home/claude-code/.opencode/bin/opencode |
| opencode2 binary | /home/claude-code/.nvm/versions/node/v22.22.3/bin/opencode2 |
| opencode config | ~/.config/opencode/opencode.json |
| Paseo profiles | ~/.paseo/config.json |
| ASES repo | ~/projects/ASES |
| Review worktrees | ~/reviews/ |

## 7. Failure signatures and fixes

| Symptom | Cause | Fix |
| --- | --- | --- |
| 401 Unauthorized ... api.openai.com | Provider override missing | Add the four model_providers.pgs2.* -c flags and model_provider="pgs2" |
| Hangs on "Reading additional input from stdin" | stdin not closed | Append </dev/null |
| 402 Payment Required | Phoenix Grove daily allowance spent | Wait for the refill timestamp or use a free route; disclose the substitution |
| opencode run exits 0 with no output | Non-TTY default formatting | Use --format json and parse JSONL |
| opencode2: command not found | nvm bin not on non-interactive PATH | Use absolute path or bash -lic |
| Model not found: opencode/ling-... | Broken model entry | Use a verified free model |
| PowerShell parse/quote errors on multi-line scripts | Local expansion of $()/backticks | Base64-encode the script and decode on the VPS |
| Model explores forever, never writes report | Prompt too broad / points at many files | Embed evidence inline; instruct write-the-report-now |


## 8. Cross-environment launch and prompt criteria

The incoming task should already establish: chosen controller and execution host; direct/in-place vs SSH vs cloud branch; exact launcher and approved child routes; pinned source/claims; run isolation; output and stopping condition. Put host credentials, receiver's model and reasoning effort **only in caller-side configuration**, not in the model-visible task. A route reference and one bounded health check beat pages of instructions.

**Successful one-shot child launch:** verified executable/provider, a real model/tool response, correct output artifact, captured exit status and routed provenance. `RUNNING` in a status file, a populated terminal pane, or return code 0 with an empty report is not proof of liveness. For long sessions inspect actual recent logs/heartbeats or commits. Do not send every child an identical model/provider claim as part of its prompt.

**Independence:** post-build review contexts must be fresh, isolated and withheld from each other until their first verdicts. Use the exact pinned source, specifications and claim, not builder reports, previous reviewer findings or orchestration history. Record each child model's provider and actual execution route from launch evidence. A single orchestrator commit collecting reports does **not** independently prove separate contexts or identical test depth.

**Working-branch publication:** use a unique worktree based on the specified commit, preserve `main` and other worktrees, commit bounded progress, push the agent's own branch and verify `git ls-remote origin` against its final SHA. Follow the 2026-10-30 branch-push policy in `docs/ORCHESTRATOR.md`, rather than stale Crosslink-guard approval prose elsewhere.

**Shared environment protection:** this ~8 GiB VPS has had memory pressure and long-lived MCP-helper accumulation. Minimize concurrent memory-heavy agents; preserve active sessions. Diagnostic work on OpenCode Desktop, Codex Desktop, Paseo, and app-server/daemons is read-only unless a specific change is authorized. Do **not** kill, close, restart, upgrade, reconfigure or replace a running app/daemon, especially a user's active local GUI, as a supposed harmless routing test. Existing processes may hold unsaved work.

**Secrets:** never print, paste, fetch into model context, commit or transfer SSH private keys or API tokens. Paths and environment variable names may be used to select existing credentials, but credentials remain in their configured stores. A PowerShell base64 script transport is encoding, not encryption; do not place secrets in it.

## 9. Dispatch failure triage additions

| Symptom | Smallest discriminating interpretation / action |
| --- | --- |
| VPS alias fails in Codex Cloud | Expected: Windows-local alias/credentials not inherited. Use Cloud Git handoff; no ad hoc credential provisioning. |
| Remote Codex session cannot use `it3812` | First establish where that Codex session runs; if already on VPS, run in-place. A missing alias is not proof of server failure. |
| ChatGPT can read the Codex Tasks skill but not call task tools | Adapter unavailable in this conversation; do not infer launch/read ability or spawn another agent to diagnose SSH. |
| Phoenix Grove `402` / refill time | Stop; keep requested route fixed. A free fallback needs per-task approval, with recorded provider/model provenance. |
| User's OpenCode Desktop closes during a "diagnostic" | This is unacceptable state interference. Stop process/service changes and preserve error evidence; no more restarts without approval. |
| Multiple agents coordinate before independent reviews | Ensure reviewer contexts were isolated *before* evidence exposure. Coordination during environment setup is not an independent source review. |

## 10. Versioning and review of the route inventory

**v1.0.0, 2026-10-31:** promotes the Oct 31 laptop→VPS runbook to a cross-environment, caller/host/launcher/model contract and includes reported recent failure lessons. Launcher paths, flags and observed provider behavior are a **dated snapshot**, not a promise about today's installation, entitlement or uptime. To revise, record exact launcher/provider, command (without secrets), environment, verification result, date, source commit and version increment. Distinguish **listed**, **tested one-shot**, **tested multi-turn**, **failed**, and **not tested**. Historical qualitative model rankings at `docs/research/registry/Model-Routing-Matrix.md` are not live route inventory.

**Sources:** original `docs/methodology/VPS Model Launch Routes.md` on `docs/model-launch-routes-guide` @ `3130d9b8b436b461495fbfd553d23f92a4464bdd`; three F3 L5 reviews @ `831f2bb9c1fe6b30e09520acb249043b72a29bc0`; canonical `skills/prompt/SKILL.md`, `docs/ORCHESTRATOR.md` and `AGENTS.md`.
