---
title: "Source 3 — ATLAS / AdaMAST Repository (CLI Fetch)"
source: "https://github.com/multi-agent-systems-failure-taxonomy/ATLAS"
fetch_method: "CLI — git clone --depth 1 https://github.com/multi-agent-systems-failure-taxonomy/ATLAS.git /tmp/opencode/src3/atlas"
fetched: "2026-08-24"
commit: "546687a (ATLAS: Point readers to AdaMAST docs and paper) — shallow clone depth 1, single commit visible locally"
local_path: "/tmp/opencode/src3/atlas"
---

# Source 3 — ATLAS Repository: AdaMAST Adaptive Taxonomy System

> **Retrieval note.** Fetched via CLI as mandated — `git clone --depth 1` to `/tmp/opencode/src3/atlas`. WebFetch is banned this dispatch; no `webfetch` calls were made. All claims below are drawn from the locally cloned tree (README, `docs/*.md`, `adamast_runtime/*.py`, `finding/mast.json`, `pyproject.toml`, and asset templates). The bundled `adamast_paper.pdf` is binary and was not parsed; paper claims are cited only as surfaced in README/docs text. No other sources consulted; no synthesis beyond faithful extraction.

## 1. Source identity and scope

- **Repository URL:** `https://github.com/multi-agent-systems-failure-taxonomy/ATLAS`
- **Local title mismatch — load-bearing for citation:** The repository at that URL presents itself as **AdaMAST** (`# AdaMAST` heading in `README.md`), not "ATLAS" in its own copy. The README's `Repository` link points to `https://github.com/multi-agent-systems-failure-taxonomy/ATLAS`, and the git log message in the shallow clone — `546687a Point ATLAS readers to AdaMAST docs and paper` — indicates ATLAS now redirects to the AdaMAST runtime and docs. The package name is `adamast` (`pyproject.toml: name = "adamast"`, version `0.1.0`).
- **What it is:** A Python runtime (`adamast_runtime/`) plus host adapters (`adamast_integration/{claude_code,codex,interactive,single_llm}/`) plus taxonomy registry (`finding/`), judge types (`judge_types/`), and a vendored research pipeline (`vendor/adamast/`). It provides a **diagnostic feedback layer** on top of an existing agent/harness and a **learning loop** that turns completed traces into a project-specific failure-mode taxonomy.
- **Canonical docs:** `docs/CONCEPTS.md`, `docs/TAXONOMIES.md`, `docs/TRACES_AND_LEARNING.md`, `docs/NATIVE_LEARNING.md`, `docs/ARCHITECTURE.md`, `docs/CONFIGURATION.md`, `docs/INTEGRATION.md`, `docs/CLAUDE_CODE.md`, `docs/EXAMPLE_RUN.md`, `docs/GETTING_STARTED.md`, plus runtime assets under `adamast_runtime/assets/` (gate protocols, checkpoint prompts, reflection templates).

## 2. Central claims (with basis)

### 2.1 Why adaptive taxonomies

Direct quote (README):

> "Improvement procedures need feedback that preserves *why* a trajectory failed. Scalar rewards discard the reason. Free-form reflection is difficult to aggregate. A fixed taxonomy cannot know the target agent's roles, tools, or domain before observing it."

And:

> "AdaMAST learns a compact set of evidence-grounded failure codes from the target system's own traces. Until a learned taxonomy is active, runs start from the built-in 14-code adaptation of MAST from [\"Why Do Multi-Agent LLM Systems Fail?\" (Cemri et al., 2025)](https://arxiv.org/abs/2503.13657)."

Derived claims:
1. **MAST as zero-config baseline.** When no taxonomy is inherited, the system starts from a built-in constant — the 14-code MAST adaptation (Specification/Coordination/Verification categories) defined in `finding/mast.json`. MAST is not a store record and never appears in the picker.
2. **Three-axis organization of generated codes.** Generated codes are organized along "three stable axes: System-level (any agent system, e.g. Context exhaustion), Role-specific (tied to a discovered component role, e.g. Checker rubber-stamps solver output), Domain-specific (requires task knowledge, e.g. Algorithm mismatch)" (README, table).
3. **Paper-evaluated generality.** The README attributes to the paper ([arXiv:2607.16387](https://arxiv.org/abs/2607.16387), cited but not independently parsed here) evaluations "as feedback for best-of-N selection, evolutionary agent optimization, and runtime reflection" and states: "On TRAIL, induced codes align with expert annotations at Cohen's kappa 0.725."

### 2.2 Headline empirical claims (reported summaries, not independently recomputed)

From `README.md` (§Results) and `runs/OfficeQA/README.md`:

| Experiment | Claim as stated locally |
|---|---|
| OfficeQA Pro (133 hard questions, Claude Code on Bedrock Haiku 4.5, oracle-parsed, official `reward.py`) | "44.4% → **51.9%** official scorer, same 133-question harness in both arms" — net +10 questions; AdaMAST arm used a frozen 15-code taxonomy (`officeqa_taxonomy.json`) — "The lift comes from the AdaMAST reflection/repair gate before submission." |
| Circle packing n=26 | "AdaMAST-guided search reaches 0.997 of the AlphaEvolve record in **20 evaluations**" |
| Terminal-Bench 2.0 (AdaMAST-Judge) | "89.9% accuracy" (README) |
| 655-problem evolutionary optimization | "87.9% to 91.9% held-out improvement" (README) |

Evidence-quality disclaimer carried verbatim where it appears:

> "Per-question rows and raw scorer output are not included, so the headline numbers below cannot be independently recomputed from this repository alone." (README, Results §)

> "Per-question predictions, scorer rows, prompts, and run manifests are not included. The table above is a reported summary and cannot be recomputed from the files in this directory alone." (runs/OfficeQA/README.md)

**Interpretation for honesty:** The local tree does provide the exact OfficeQA taxonomy (`runs/OfficeQA/officeqa_taxonomy.json`, 15 codes) and reproduction instructions (model, harness, scorer, freeze setup), but the underlying per-question predictions and the AlphaEvolve comparison traces are absent locally, so the deltas are asserted-not-audited from this clone alone.

## 3. Mechanisms

### 3.1 Adaptive taxonomy generation lifecycle

Conceptual sequence from `docs/CONCEPTS.md` ("The runtime loop", quoted verbatim):

> 1. "A task starts. AdaMAST selects the active taxonomy: an inherited stored taxonomy if one is configured, otherwise the built-in MAST fallback."
> 2. "At configured boundaries (checkpoints, tool failures, subagent stops), the agent is asked to reflect on its recent trajectory against the taxonomy."
> 3. "Before the final answer is released, a pre-submission gate requires a structured reflection; the agent gets a bounded number of repair attempts."
> 4. "At session end, one canonical trace of the task is recorded."
> 5. "When enough traces accumulate, AdaMAST generates a task-specific taxonomy (from MAST warm-up) or refines the active stored taxonomy. Accepted results become stored taxonomies that future runs can inherit."

Lifecycle thresholds (from `docs/CONFIGURATION.md`, `docs/TRACES_AND_LEARNING.md`, `docs/NATIVE_LEARNING.md`, and `adamast_runtime/config.py` / `generation.py` / `refinement.py`):

| Stage | Default | Config field |
|---|---|---|
| First taxonomy generation (MAST warm-up) | 5 eligible traces | `generation_threshold` (default 5) |
| First refinement review after activation | 10 traces | `k_init` (default 10) |
| Later refinement reviews | every 20 traces | `k` (default 20) |

Additional policy knobs: `generation_stops` / `refinement_stops` (whether the running task waits for generation/refinement), `skip_judge` (skip Reflection-Judge cleanup), `advanced_refinement` (one support-judge repair pass on refinement), `freeze` (inference-only, record evidence/traces but never generate/refine — for clean A/B).

Direct quote on the trace-output identity invariant (`docs/INTEGRATION.md`):

> "`trace_output` is mandatory because it is the program identity. Reusing the same `trace_output` means 'same program': counters, pending traces, active taxonomy, and local manifest state are shared. Use a different `trace_output` when two task streams should learn independently."

Generation mechanics (from `adamast_runtime/generation.py` header and docstring in `_adamast_generate`):

- Generation is **MAST → stored-taxonomy** only; the candidate has no `taxonomy_id` until accepted.
- Vendored pipeline called at `_adamast_generate()` via `vendor.adamast.generate_taxonomy`; output lands under `<program_root>/generation/` to keep artifacts inside the program's owned directory rather than the worker's CWD.
- A configurable `project_fn` projects each trace dict before generation (default `outcome_blind_trace` strips outcome metadata); custom projectors must return a dict, not a string.
- `seed_roles` declares agent roles and trace step names they own; without it, B-codes (role-specific) are effectively skipped.
- `categories` controls axes (default `("A","B","C")`); `max_codes` caps total codes.

Refinement mechanics (`docs/TRACES_AND_LEARNING.md` + `adamast_runtime/refinement.py`):

- Once a stored taxonomy is active, each program tracks its own refinement counter independently.
- On acceptance, the replacement receives a new `taxonomy_id`, lineage is recorded from predecessor → successor, the publishing program's counter resets, other programs preserve theirs.
- The worker may return `no_change` — advances cadence without creating a successor; refined successors activate only for the originating `project/task-group`, not silently for unrelated programs.
- Advanced refinement: if the support judge finds issues, the refinement model gets one repair pass; the repaired taxonomy is then accepted automatically.
- Non-blocking `overlap warnings` flag unusually similar name/description pairs for review only.

Native in-task learning (`docs/NATIVE_LEARNING.md`):

> "Codex and Claude Code can generate and refine taxonomies through a subagent in the active host conversation. No external model API key, standalone host CLI, or second login is required."

Job state machine (quoted verbatim from that doc):

```text
queued -> claimed -> awaiting_reconcile -> support_queued
       -> claimed -> awaiting_support_reconcile -> activating
       -> activated | no_change | rejected | failed
```

Seven concrete steps are enumerated there (freeze exact trace references, claim with time-bound token, main agent launches generator subagent and continues work, subagent reads `prompt.txt` + `output.schema.json` and returns one bounded receipt via `SubagentStop`, foreground reconciliation validates claim/snapshot/candidate structure/exact evidence quotes, separately claimed support-review subagent decides, atomic registration + activation at idle boundary). Polling is idempotent; missed threshold triggers are repaired on the next hook.

Storage and identity invariants (`docs/TAXONOMIES.md`, `docs/ARCHITECTURE.md`):

- Flat store: "one JSON file per taxonomy, named `<taxonomy_id>.json`" under the store dir (default `~/.adamast/taxonomies`). `taxonomy_id` is the only routing key; `repo`/`domain`/`display_name`/`summary` are display metadata that "do not route, group, or select taxonomies."
- Lineage preserves evolution history across programs; `display_name` is mutable without breaking references.
- For interactive installs the canonical Git root is resolved and program state lives under `~/.adamast/interactive/projects/<project-key>/groups/<task-group>/program/` (project key includes a canonical-path hash; choosing MAST in a project that already has a learned taxonomy creates an isolated `fresh-*` group without replacing the shared default). First resolved program path is bound to the host's stable conversation ID; resume from another shell does not recompute the project or reopen the selector.

Vendoring provenance (`README.md`, `vendor/adamast/VENDORED.md` not fully read but indexed): original research pipeline on branch `paper-pipeline`; maintained, locally patched fork under `vendor/adamast/` with documented change categories.

### 3.2 Agreement gates

AdaMAST uses a small, configuration-driven gate family:

**Gate inventory**

| Gate | When it fires | Blocking? |
|---|---|---|
| Checkpoints (`PostToolUse`, `PostToolUseFailure`, `SubagentStop`, custom `PreToolUse` etc.) | Configured boundaries — after a tool call, on failure, at subagent stop | Advisory nudges by default; can be configured `blocking` via `adamast-claude-add-hook --mode blocking` |
| Pre-submission / final gate | Before the final answer is released | **Blocking** — must emit a parseable gate decision; repair loop bounded by `repair_rounds` / `format_retries` |

**Reflection shape — the load-bearing contract** (`docs/CONCEPTS.md` + `adamast_runtime/assets/checkpoint_reflection.md` + `adamast_runtime/reflection.py`):

Quoted verbatim from `docs/CONCEPTS.md` (§ The reflection shape):

> 1. "**Observe** concrete events or missing expected steps in the recent trajectory."
> 2. "**Correlate** only evidence-supported causes."
> 3. "**Map** to taxonomy codes only when the evidence supports the match."
> 4. "**Decide** whether to make one focused repair or continue."
> "A reflection that maps no codes is a *clean checkpoint* and is recorded as evidence too. Agents must not invent a failure mode to satisfy the gate."

> "Decisions that would replace an already-committed answer are additionally held to a replacement standard: the agent must construct and run a check that demonstrates the current answer's failure (internal, source, task-constraint, or completeness consistency) — an alternative's appeal alone never authorizes a replacement."

Asset-level detail (`adamast_runtime/assets/checkpoint_reflection.md`):

- Delivered at each checkpoint: `Checkpoint ID`, `Active taxonomy`, `Failure modes to consider`, `Scope`, and `Recent trajectory excerpt` (bounded by `recent_activity_messages` / `recent_activity_chars`).
- Required output block is `AdaMAST reflection:` with `Checkpoint ID: <id>` exactly identifiable, plus four labeled sections: `Observe:` / `Correlate:` / `Map:` / `Decide:`.
- `Map:` lines must contain a known code id plus an `evidence:` phrase (verbatim fact), e.g. `<CODE> | evidence: "<verbatim fact>"`; for clean checkpoints the form is `none apply | considered: <CODE,...> | evidence: "<why clean>"`.
- `Decide:` in first person, exactly one of `change: <one focused change>` or `no change needed, because <evidence-based reason>`.
- Replacement standard restated there as: "a committed answer may be replaced only by demonstrating its own failure — never by demonstrating an alternative's appeal. Construct and run a check against the current answer: recompute it from its own stated inputs, re-read the value at its cited source location, re-check a constraint the task text explicitly states, or confirm a step the task requires never happened."

**Pre-submission gate protocol** (`adamast_runtime/assets/pre_submission_protocol.md` + `adamast_runtime/protocol.py`):

> "Before declaring the task complete, compare the full task trajectory and verification evidence against the active failure-mode taxonomy."
> "Return one of: `READY_TO_SUBMIT` when no unresolved taxonomy-relevant issue remains. `REPAIR_REQUIRED` when one or more issues remain."
> "If repair is required, address the highest-impact unresolved issue, verify the repair, and run this gate again. Perform at most $max_retries repair attempts. After $max_retries unsuccessful attempts, stop repairing and report the remaining issue honestly instead of claiming clean success."

Final gate fields (verbatim):

- `Final AdaMAST status:` READY_TO_SUBMIT | REPAIR_REQUIRED
- `Codes checked:` relevant taxonomy ids, or none
- `Evidence:` concrete task or verification evidence
- `Repair attempts used:` 0–$max_retries
- `Final decision:` submit | repair | report unresolved

Parser aliasing in `adamast_runtime/protocol.py` is generous (many synonyms for ready/repair are accepted), and `evaluate_pre_submission()` enforces the retry-budget semantics: missing/invalid gate text blocks, `REPAIR_REQUIRED` blocks while budget remains, honest `report unresolved` is the terminal honest release after budget exhaustion.

**Budgets** (`docs/CONFIGURATION.md`, `adamast_runtime/config.py`):

| Budget | Default | Purpose |
|---|---|---|
| `repair_rounds` | 3 | Substantive `REPAIR_REQUIRED` repairs before honest unresolved release |
| `format_retries` | 2 | Unparseable reflection shape re-prompts per checkpoint cycle (targeted, naming missing elements) |
| `max_retries` | 3 (legacy alias) | Maps to `repair_rounds` when `repair_rounds` unset |
| `gate_exhaustion_policy` | `"raise"` | Single-LLM only: `raise` errors at cap vs `release` returning best answer with `gate_allowed=false` |

**Gates fail open** (`docs/CLAUDE_CODE.md`, also `docs/TROUBLESHOOTING.md` — load-bearing for ASES comparison):

> "If an AdaMAST hook itself crashes or is killed at Claude Code's per-hook timeout, the agent continues normally and that gate silently does not fire. This is deliberate: an AdaMAST bug must never leave your session unable to finish. The trade-off is that a skipped gate is quiet — when gating matters (A/B runs, benchmarks), verify it happened rather than assuming:"
> "- `[adamast]` lines on stderr report retry-guard releases and internal errors;"
> "- `<trace_output>/decisions.log` records every gate decision and release;"
> "- `adamast-status --config adamast.json` shows reflections recorded per session — a finished session with no final-gate evidence means the gate was skipped."

### 3.3 Trace evidence standards

**What counts as a trace** (`docs/CONCEPTS.md` + `docs/TRACES_AND_LEARNING.md`):

- A trace is "The canonical record of one completed task (task text, redacted trajectory, metadata). Traces are the input to generation and refinement."
- Batch/integration contract: "one launched task produces one canonical trajectory."
- Codex/Claude Code episodes: "One episode is a substantive user turn followed by the main agent's work and its final Stop boundary" — with Claude Code supporting its blocking reflection loop, Codex committing "a compact `Checkpoint`/`Relevant codes`/`Evidence`/`Next action` block in one callback because a continued Codex Desktop turn is not guaranteed to redeliver Stop." Follow-up requests in the same conversation are separate episodes.
- Stored trajectory is "the transcript delta since the previous committed Stop, not a repeated copy of the entire conversation." Codex persists a bounded normalized JSONL view (human/assistant + tool interactions; excludes developer context, reasoning, hook prompts, installed-skill reads, accounting events). Incomplete interactive episodes are recovered on resume or the next substantive prompt; user-only abandoned turns, empty sessions, and AdaMAST control turns do not become learning traces. Sub-task/subagent checkpoints contribute runtime evidence but do not create extra generation traces by default.

**Evidence recording** (`adamast_runtime/evidence.py`, `adamast_runtime/dashboard.py`):

- Runtime evidence is written atomically to `<trace_output>/.adamast-runtime-evidence.json` (structure: `version`, `taxonomies` with per-code `fire_count`/`task_firings`/`events`, and `checkpoints` array). `record_reflection()` appends fired-code events plus a checkpoint entry; clean `none_apply` entries are recorded as well with `considered_codes`/`fired_codes`.
- Dashboard reads the same evidence file live (`adamast-dashboard` on localhost); filtering by gate/task/agent id supported.

**Evidence citation and validation** (generation/refinement contracts, from `docs/NATIVE_LEARNING.md` + `adamast_runtime/generation.py`):

- Native replacement codes "must cite supporting frozen trace IDs, include a verbatim span from every cited trace, and include a rationale. The coordinator verifies each normalized quote against the immutable snapshot and records the result per code." (`docs/NATIVE_LEARNING.md`)
- Replacement codes contain "one to 30 codes. The 15-to-30 guidance used by the research refinement prompt is a generation target, not a runtime minimum; smaller evidence-grounded taxonomies remain valid."
- That evidence is retained for validation and audit; the runtime-facing code definition remains only `id, name, description, category`.
- Support-review subagent: "After exact-span checks, a separate support-review subagent must approve every replacement code before foreground activation." (README) — for `no_change` refinements this phase is skipped because no taxonomy data changes.
- Overlap warnings: "Every refinement artifact also includes non-blocking overlap warnings. These warnings flag pairs of failure modes whose names/descriptions look unusually similar. They are meant for review, not automatic rejection." (`docs/TRACES_AND_LEARNING.md`)

**Redaction and privacy** (`docs/INTEGRATION.md`, `docs/CONFIGURATION.md`):

> "AdaMAST stores traces and may send trace excerpts to the AdaMAST model for generation, judging, and refinement. A harness should redact secrets before calling `record_trace()`."
> "At minimum, redact: API keys, bearer tokens, and cookies; private file paths if they are sensitive; user/private data not needed to understand the failure pattern; benchmark labels or outcomes if they would leak oracle information."
> "The bundled adapters (Claude Code, Codex, single-LLM) apply the shipped conservative redactor by default; set `redact_traces: false` to opt out. Custom harnesses remain responsible for their own redaction, including any project-specific patterns. The runtime strips known outcome fields from learning inputs, but it cannot [fully guarantee oracle-blindness without harness cooperation]."

Redactor lives in `adamast_runtime/redaction.py`; `learning_calls.outcome_blind_trace` strips outcome/final-gate status fields from learning inputs.

**Trace persistence and lifecycle** (`adamast_runtime/traces.py`, `adamast_runtime/lifecycle.py`):

- `trace_output` directory holds the program manifest, trace files, `.adamast-runtime-evidence.json`, `decisions.log`, and temporary `generation/` scratch.
- On acceptance, traces move into a per-taxonomy folder under `trace_root` (default `~/.adamast/traces`); until acceptance, warm-up traces stay in the program folder.
- After rejection, warm-up traces stay, and re-generation waits until enough new traces accumulated relative to the rejected snapshot.
- `evidence_export` can write a durable JSON snapshot at session end (exact `.json` file or `<program_id>.json` inside a directory); exporting never moves or deletes original trace/evidence files.
- Usage ledger in the program manifest counts learning calls by stage/model; when provider token/cost metadata is unavailable the event is marked `usage_available: false` instead of estimated.

### 3.4 Runtime supervision

**Session lifecycle** (`docs/INTEGRATION.md`, `adamast_runtime/lifecycle.py`):

Minimal lifecycle (quoted from `docs/INTEGRATION.md`):

```python
from adamast_runtime import GenerationTrace, end_session, pre_submission, record_trace, start_session
session = start_session(trace_output="./adamast-program", adamast_model="gpt-5", inherit=None)
# At task start: deliver session.delivery.runtime_protocol as standing behavior
# At checkpoints: deliver session.delivery.taxonomy + recent trajectory window, collect reflection
# Before release: decision = pre_submission(session, gate_text); if not decision.allow: repair
record_trace(session, GenerationTrace(problem_id="...", task="...", raw_trajectory="...", metadata={...}))
result = end_session(session)
```

`end_session()` is where generation/refinement triggers fire (or are queued, depending on `generation_stops`/`refinement_stops`). Hook integrations always run generation/refinement in background workers regardless of those flags because "a hook process is killed at the harness's per-hook timeout, so inline learning is honored only by the single-LLM and CLI paths that own their process" (`docs/CONFIGURATION.md`).

**Ownership boundary** (`docs/ARCHITECTURE.md` + `docs/INTEGRATION.md`):

| AdaMAST owns | Harness/agent owns |
|---|---|
| taxonomy selection by `taxonomy_id`, built-in MAST fallback, pre-submission gate parser + retry envelope, canonical trace persistence, generation/refinement triggers, taxonomy storage + successor lineage, optional dashboard | model execution, when a boundary occurs, how checkpoint prompts reach the agent, how the complete trajectory is collected, any redaction/summarization before `record_trace`, user-facing config + credentials |

**Host adapter flow** (`docs/ARCHITECTURE.md`):

```text
Host event
  -> host adapter resolves project and conversation
  -> interactive selector and route resolve the program
  -> adamast_runtime opens or closes an episode
  -> gate evidence and one canonical trace are persisted
  -> interactive polling checks generation/refinement thresholds
  -> a native host subagent proposes a candidate
  -> adamast_runtime validates and atomically activates it
```

"The main agent always owns the user's task. The taxonomy worker receives an immutable outcome-blind snapshot and cannot edit the taxonomy store."

**Durable project scope** (covered under 3.1; reinforces supervision: the system survives shell/directory changes and session resume via conversation-ID binding).

**Model and credential handling** (`docs/INTEGRATION.md`, `docs/CONFIGURATION.md`, `adamast_runtime/models.py`):

- `adamast_model` is the model used for generation/judging/refinement — "Keep it separate from your task-solving model."
- Transport selection by model-id shape: Claude/Anthropic/Bedrock-shaped IDs use Anthropic transports unless `OPENAI_BASE_URL` is set; Gemini-shaped IDs use `GEMINI_API_KEY`/`GOOGLE_API_KEY`; OpenAI-shaped IDs use the OpenAI client honoring `OPENAI_BASE_URL`. Unsupported shapes are rejected. `ModelProfile` resolution maps model families to conservative context windows with safety ratio 0.90.
- "AdaMAST never stores credential values. Set provider keys in your environment" / "Store only environment variable names."

**Operational commands** (`README.md` table):

`adamast-doctor` (validate paths/config/hooks/host contracts), `adamast-status` (active taxonomy + traces + learning state + usage ledger), `adamast-find` (list/select stored taxonomies), `adamast-dashboard` (read-only localhost), `adamast-traces` (inspect), `adamast-import-traces` (generate from existing traces), `adamast-*-install`/`uninstall`, `adamast-single-run` (wrap one direct model task).

## 4. Evidence quality assessment

| Dimension | Local finding | Verdict |
|---|---|---|
| **Trace corpus availability** | Warm-up and stored traces are folder-per-program on disk, but the clone ships only one production-evaluation taxonomy (`runs/OfficeQA/officeqa_taxonomy.json`) and one demo taxonomy shape (`runs/Circle-Packing/circle_packing_taxonomy.json`); the underlying 133 per-question trajectories, scorer rows, and model contexts are not included. Generation/refinement inputs beyond those taxonomies are not present locally. | Claims about end-to-end lift cannot be audited from the cloned tree alone. |
| **Reproducibility documentation** | `runs/OfficeQA/README.md` gives unusually precise replication steps: dataset (`databricks/officeqa`), scorer (`reward.py`), oracle-parsed condition, agent (Claude Code headless on Bedrock Haiku 4.5, one WD per question, Read/Grep/Glob/Bash, `<FINAL_ANSWER>` tags), AdaMAST arm setup (`adamast-register-taxonomy` + `adamast-claude-install` + `freeze: true`), and baseline condition. Circle-Packing `runs/Circle-Packing/README.md` similarly describes the evaluation setup. | Steps are sufficient to attempt external replication, but success would still require access to the external OfficeQA corpus and the exact scoring/model environment; the clone does not enable one-command recomputation. |
| **Headline-number auditability** | The READMEs explicitly warn "cannot be independently recomputed from this repository alone" / "per-question predictions … are not included." The paper PDF is present (`docs/adamast_paper.pdf`) but was not parsed in this extraction; paper-internal ablations are therefore not verified here. | Headlines are **reported, not proven**, locally — evidence-based as to documentation and taxonomy artifact presence, guess-level as to numeric correctness without external recomputation. |
| **Implementation–documentation agreement** | Protocol text in asset templates (`pre_submission_protocol.md`, `checkpoint_reflection.md`, `reflection.py`, `protocol.py`) matches the prose claims verbatim; defaults (`config.py`) match doc tables; the lifecycle invariant (`trace_output` = program identity) is enforced in `lifecycle.py` and echoed consistently across CONCEPTS/TRACES_AND_LEARNING/CONFIGURATION/INTEGRATION. The `Gates fail open` disclaimer is repeated identically in CLAUDE_CODE.md and TROUBLESHOOTING.md, indicating intentional design rather than documentation drift. | High consistency between docs and code on supervision mechanics (directly inspected). |
| **Evidence-grounding enforcement** | The exact-span citation requirement is described in NATIVE_LEARNING.md and implemented in the reconciliation path referenced by `generation.py` / `reflection_refinement.py` and evidence validation logic; `admin` assets `refinement_support_judge.md` / `reflection_refiner_*` exist. The local tree does not ship a full adversarial evaluation of the enforcement (e.g., a corpus of rejected vs accepted citations). | Mechanism is evidenced in design + code; its *effectiveness* against prompt-injection or hallucinated spans is not measured locally. |
| **Conflict with ASES context** | This source directly addresses the "lifecycle-ownership" tension noted in the ASES synthesis: AdaMAST explicitly claims *not* to own model execution or scheduling, only taxonomy selection/trace/validation/activation, and its fail-open choice trades enforcement power for session liveness — the opposite default from the ASES durable-store / cheap-staleness-trigger topology. | Both approaches exist locally; the comparison belongs in the synthesis step, not here. |

Summary verdict: **Mechanisms and lifecycle semantics are evidence-based (proven in the cloned tree); headline empirical results are reported-not-audited (explicit non-recomputability noted by the authors themselves).** The extraction below respects that distinction: load-bearing mechanism quotes are taken verbatim from the local text; empirical numbers are presented with their stated provenance caveats.

## 5. Direct quotes (load-bearing, verbatim from the cloned tree)

1. On supervision philosophy (README): `"AdaMAST adds a diagnostic feedback layer to an agent. It checks work at meaningful boundaries, records evidence about recurring failures, and learns a project-specific taxonomy from completed traces. Your existing agent or harness keeps owning the task."`

2. On adaptive taxonomy motivation (README): `"Improvement procedures need feedback that preserves *why* a trajectory failed. Scalar rewards discard the reason. Free-form reflection is difficult to aggregate. A fixed taxonomy cannot know the target agent's roles, tools, or domain before observing it."`

3. On the reflection requirement (README / CONCEPTS): `"At a checkpoint, the agent follows a fixed sequence: Observe: What concretely happened or was omitted? Correlate: Which evidence-supported cause explains it? Map: Which active failure code applies, if any? Decide: Continue, or make one focused repair."` and `"`none apply` is valid. AdaMAST does not manufacture a failure just to force a change."`

4. On taxonomy axes (README): `"Generated codes are organized along three stable axes: System-level | Role-specific | Domain-specific"` with examples System: Context exhaustion, Role: Checker rubber-stamps solver output, Domain: Algorithm mismatch.

5. On generation thresholds (NATIVE_LEARNING / TRACES_AND_LEARNING): `"At five eligible traces, AdaMAST queues taxonomy generation by default. … The first refinement review occurs after ten additional traces; later reviews occur every twenty traces by default."`

6. On evidence requirement (docs/NATIVE_LEARNING): `"Replacement codes must cite supporting frozen trace IDs, include a verbatim span from every cited trace, and include a rationale. The coordinator verifies each normalized quote against the immutable snapshot and records the result per code."`

7. On support review (README): `"After exact-span checks, a separate support-review subagent must approve every replacement code before foreground activation."`

8. On trace output invariant (docs/INTEGRATION): `"`trace_output` is mandatory because it is the program identity. Reusing the same `trace_output` means 'same program': counters, pending traces, active taxonomy, and local manifest state are shared."`

9. On fail-open gates (docs/CLAUDE_CODE): `"If an AdaMAST hook itself crashes or is killed at Claude Code's per-hook timeout, the agent continues normally and that gate silently does not fire. This is deliberate: an AdaMAST bug must never leave your session unable to finish."`

10. On replacement standard (docs/CONCEPTS / asset): `"The agent must construct and run a check that demonstrates the current answer's failure … an alternative's appeal alone never authorizes a replacement."` (CONCEPTS paraphrase compressed; full expansion in the asset quoted in §3.2).

11. On evidence non-manufacture (docs/CONCEPTS): `"A reflection that maps no codes is a *clean checkpoint* and is recorded as evidence too. Agents must not invent a failure mode to satisfy the gate."`

12. On lineage (docs/TAXONOMIES + docs/CONCEPTS): `"Generated and refined taxonomies get new taxonomy IDs. Refinement records lineage from the previous taxonomy to its replacement so future runs can preserve the evolution history."` and `"Taxonomies are selected by one immutable key: `taxonomy_id`."`

## 6. Open questions (not answered in the locally cloned tree)

1. **Early-noise grounding.** Defaults assume 5 warm-up traces suffice; failure modes when those traces are noisy, unrepresentative, or drawn from a cold-start harness without diverse task coverage are not measured locally — how much does generation quality degrade and what recovery policy (if any) besides "wait for enough new traces" exists?

2. **Fail-open vs enforcement.** When the final gate matters (A/B runs, benchmarks), the docs advise verifying gate firing via `decisions.log` / `adamast-status`; but for production multi-agent supervision, the silent-skip trade-off leaves the question of how to guarantee agreement gates were not skipped en masse unanswered.

3. **Exact-span adversary.** The coordinator verifies normalized verbatim spans against the frozen snapshot, but the local tree ships no evaluation of how well that blocks hallucinated spans, paraphrased citations, or cross-trace copy-paste, nor a corpus of rejected span attempts.

4. **Refinement cadence realism.** The 10/20 refinement cadence presupposes tens of eligible traces per program; whether that throughput is plausible for low-traffic ASES programs, and whether infrequent but high-value traces should be weighted differently, is not discussed in the local docs.

5. **Vendor/runtime version parity.** The vendored pipeline (`vendor/adamast/`) is a "maintained, locally patched fork" whose `VENDORED.md` documents change categories; exact parity with the `paper-pipeline` branch and forward-port policy for new taxonomy-generation research is not fully evident from a shallow clone.

6. **Secret surface beyond redaction.** Redaction strips API keys/tokens/cookies by default and `outcome_blind_trace` removes outcome fields, but domain-specific secrets (PII, repo-private logic, benchmark oracles in `metadata`) remain harness-responsible — the boundary of what AdaMAST itself guarantees to strip is left implicit.

7. **Scalability of evidence and dashboards.** Traces and `.adamast-runtime-evidence.json` grow unboundedly per program (manual archive/prune recommended); dashboards keyed to those stores are read-only but their behavior under large program folders (thousands of episodes) is not specified.

8. **Cross-host equivalence.** Architecture maps adapters for Codex (`PostToolUse` compact checkpoint), Claude Code (blocking reflection loop), and single-LLM; whether agreement-gate semantics and trace canonicalization are truly equivalent across those adapters under all hook-timeout / resume conditions is not proven locally.

9. **Taxonomy code semantics vs. ASES failure matrix.** MAST's 14 codes (Specification/Coordination/Verification) and AdaMAST-generated codes (System/Role/Domain) overlap partially with ASES concepts but use different granularity — the cross-walk to ASES's four-role topology, claim discipline, and durable-store staleness trigger is left to the comparison report, not this source extraction.

## 7. What was *not* tested (honesty clause for this dispatch)

- The bundled `docs/adamast_paper.pdf` was **not parsed** (binary PDF; extraction via local read only inspected the first bytes to confirm MIME, not content) — so any paper-internal ablation or methodology detail beyond what README/docs surface is marked inaccessible here.
- The vendor pipeline under `vendor/adamast/` was indexed (top-level listing) but **not executed**; its generation quality, judge calibration, or refinement repair pass was not exercised.
- Per-question recomputation of the OfficeQA / Circle-Packing / Terminal-Bench headlines was **not attempted** — the tree itself declares those numbers "cannot be independently recomputed" locally.
- No `WebFetch` calls were made (banned); all remote freshness beyond the shallow-clone tip (`546687a`) is unknown. If a later commit changes thresholds or gate semantics, this dispatch would not observe it without a re-clone.
- Evidence standards that require running an instrumented agent (e.g., how often `none apply` vs fired codes appear in live traces, or how silently skipped gates distribute) were **not measured** — only the design and the code that would record them were inspected.

## 8. File map observed (local clone, depth 1)

Key paths inspected directly: `README.md` (primary), `docs/CONCEPTS.md`, `docs/TAXONOMIES.md`, `docs/TRACES_AND_LEARNING.md`, `docs/NATIVE_LEARNING.md`, `docs/ARCHITECTURE.md`, `docs/CONFIGURATION.md`, `docs/INTEGRATION.md`, `docs/CLAUDE_CODE.md`, `docs/EXAMPLE_RUN.md`, `docs/GETTING_STARTED.md`, `docs/TROUBLESHOOTING.md`, `finding/mast.json` (verbatim 14-code list), `finding/mast.py`, `adamast_runtime/{lifecycle,evidence,protocol,reflection,generation,models,config}.py`, `adamast_runtime/assets/{pre_submission_protocol,checkpoint_reflection,standard_refinement_prompt}.md`, `pyproject.toml`, `runs/OfficeQA/README.md`, `runs/Circle-Packing/README.md`. All reads were local filesystem reads (`cat`) against `/tmp/opencode/src3/atlas`.

---

*This section is source-atomic: it covers only the ATLAS/AdaMAST repository as fetched via CLI. No synthesis with other sources has been performed here. Cross-walk against ASES methodology (four-role topology, failure matrix, claim discipline, adaptive-taxonomy relevance) belongs in the downstream comparison document.*
