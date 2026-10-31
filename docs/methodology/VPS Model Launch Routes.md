---
title: VPS Model Launch Routes (Laptop-Driver Environment)
program: ASES
layer: Methodology
document_type: Operational Runbook
status: Active
authority: Informative
canonical_repository: ases
depends_on:
  - AI Orchestration Guide
  - Clean Room Execution Guide
related_documents:
  - docs/research/registry/Model-Routing-Matrix.md
---

# VPS Model Launch Routes

This runbook records the known-good ways to launch and manage models when
driving work from a local laptop while the actual execution happens on the
it3812 VPS. It exists so future agents do not re-discover these routes (or fall
into the same traps) by trial and error.

It is environment-specific. The named hosts, paths, wrappers and models reflect
this deployment at the time of writing; re-verify versions and quotas before
relying on them.

## 1. Topology

- Driver: the operator laptop. All commands are issued from here over SSH.
- Worker: the it3812 VPS (Tailscale host 100.74.173.23, port 5771, Ubuntu,
  user claude-code). All model execution, repositories, worktrees and builds
  live here.
- Rule of thumb: nothing of substance should run on the laptop. The laptop only
  issues SSH commands and reads back results.

### Getting onto the VPS

SSH config (laptop ~/.ssh/config) defines the alias used throughout:

```
Host it3812
    HostName 100.74.173.23
    Port 5771
    User claude-code
    IdentityFile ~/.ssh/vps-tripn
    IdentitiesOnly yes
```

Connect with: ssh it3812 "<command>"

## 2. Shell quoting is the number one source of failure

The driver shell is Windows PowerShell 5.1. It expands subexpressions, backticks
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
  loop; switch routes (section 4) or wait for the stated refill.

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
  refill timestamp in the error, or pick a free route. But disclose any route
  substitution in the artifact you produce. Do not silently present a
  free-endpoint review as a Phoenix Grove one.

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
