---
title: "EDASES Topic: Model Capability — 16-Review Wave"
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Finding
canonical_repository: edases

depends_on:
  - Model Agreement Schema (draft, #241)
  - AI Capability Registry Specification (#190)
  - Workflow Topology Design and Reasoning Record

related_documents:
  - capability-mapping/Model-Routing-Matrix.md
  - docs/research/review-inbox/agent-tooling-and-permission-enforcement-reviews.md
  - docs/research/review-inbox/agent-tooling-and-permission-enforcement-reviewed-reviews.md
  - docs/research/review-inbox/gemini-synthesis-original-doc.md
  - docs/research/review-inbox/gemini-synthesis-reviewed-doc.md
  - docs/research/agent-tooling-and-permission-enforcement-reviewed.md

consumed_by:
  - capability-mapping/Model-Routing-Matrix.md
  - EDASES Model Data Collection epic (#255)
  - Model feedback registry (#181)

last_updated: 2026-08-10
---

# EDASES topic: Model Capability — the 16-Review Wave

**Date:** 2026-08-10
**Status:** Research retrospective — model-capability evidence for the Model Data Collection epic (#255)
**Scope:** Two read-only-boundary review waves over the same brief class (adversarial review of the permission-enforcement system), 16 reviews across 8 distinct models, plus two Gemini syntheses. The 16 reviews are a natural experiment: a same-class adversarial review run across 8 models TWICE. This document synthesizes the agreement/disagreement data as model-capability evidence and feeds the model-agreement index (#241), the capability registry (#190), and the routing matrix (capability-mapping/Model-Routing-Matrix.md).
**Refs:** #255 (epic), #241 (model-agreement index), #190 (registry), #314/#320 (review-wave parents), #315/#316/#317/#321/#322/#323 (reviewer sub-issues), #319/#326 (Gemini syntheses), #337 (sync-guard Level-2 test).

---

## 1. Wave Description

Two review waves, same brief class, same eight-model panel composition. Both waves were **read-only** adversarial assessments of the agent-tooling/permission-enforcement documentation; reviewers had no write access and were instructed to post verdicts only to their isolated sub-issue (independence per playbook §5.6).

| | Wave 1 (original doc) | Wave 2 (reviewed doc) |
|---|---|---|
| Subject | `docs/research/agent-tooling-and-permission-enforcement.md` @ 4cbae854 | `docs/research/agent-tooling-and-permission-enforcement-reviewed.md` @ 527c5eb7 |
| Brief | Adversarial review of the permission-enforcement current-state document (#314) | Carry-on-or-refactor assessment of the merged reviewed document (#320) |
| Parent issue | #314 | #320 |
| External reviewers (5) | Reviews 1–5: ChatGPT web chat, Claude Sonnet 5 (High effort), GLM-5.2, Deepseek-v4-Pro, Qwen3.8 Max | Reviews 4–8: ChatGPT Web, Claude Sonnet 5, GLM-5.2, Deepseek V4 Pro, Qwen 3.8 Max |
| Internal reviewers (3) | Reviews 6–8: luna (#315), kimi-k2.7-code (#317), hy3 (#316) | Reviews 1–3: luna (#321), kimi-k2.7-code (#322), hy3 (#323) |
| Synthesis | Gemini #319 (gemini-3.5-flash) | Gemini #326 (gemini-3.5-flash) |

**Which models ran twice:** luna, kimi-k2.7-code, and hy3 participated in **both** waves (internal; the only models with live repository access). The five external models (ChatGPT, Sonnet 5, GLM-5.2, Deepseek-v4-Pro, Qwen3.8 Max) were consulted once per wave, i.e. each external model reviewed both the original and the reviewed document — the panel composition is identical across waves, only the subject changed.

**Experimental properties that make this a natural experiment:**

- **Same brief class, twice** — a controlled-ish repetition: same task type, same panel, different subject (original vs. reviewed-and-corrected doc).
- **Isolation** — internal reviewers explicitly did not read each other's verdicts (hy3 #316 WHAT-NOT-TESTED 7: "Independence held: I did not read #315 or #317").
- **Context asymmetry** — internal reviewers had live binary/repo access (versions, counts, logs); external reviewers had only the document plus public knowledge. This asymmetry produced the most informative divergence of the whole wave (see §3).
- **Synthesis layer** — two Gemini tabulations (#319, #326) converted 16 unstructured verdicts into finding-level agreement matrices; the synthesis layer itself became a data source when hy3 caught an attribution error inside it (§3.1).

---

## 2. Finding-Level Agreement (the load-bearing part)

Per the model-agreement schema (#241), the load-bearing data is **finding-level agreement**, not verdict-level agreement. All eight models returned CHANGES-REQUESTED / do-not-carry-on in both waves (verdict-level consensus 8/8), but the finding-level rows show where that consensus was unanimous, where it was context-dependent, and where it split.

### 2.1 Wave 1 agreement matrix (#319, gemini-3.5-flash)

| Finding / Theme | ChatGPT | Sonnet5 | GLM | Deepseek | Qwen | luna | hy3 | kimi | Count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Read-only by construction overstated | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| Builder can modify enforcement config | Partial | Y | Partial | Y | Y | N | Y | N | 6/8 |
| `--allowedTools` surface dormant/dead | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| Identity resolution fails open to Builder | Y | Y | Y | Y | Y | N | Y | Y | 7/8 |
| No explicit adversary/threat model | Y | Y | Y | Y | Y | N | Y | N | 6/8 |
| Deployed-vs-source version conflation | N | N | N | N | N | Y | Y | Y | **3/8 (all internal)** |
| Countable claim errors | N | N | N | N | N | Y | Y | Y | **3/8 (all internal)** |
| Wrapper injects `--auto` under tmux | N | N | Y | N | N | Y | Y | Y | 4/8 |
| MCP filesystem tool names mis-identified | N | Partial | N | Partial | Partial | N | N | Y | 4/8 |
| Confidentiality/exfiltration unaddressed | Y | N | N | Y | Y | N | Y | N | 4/8 |
| `#313` sqlite3 treated as settled fact | Y | Y | Y | Y | Y | N | Y | N | 6/8 |
| Model-whitelist plugin global | N | Y | N | N | Y | N | Y | N | 3/8 |

### 2.2 Wave 2 agreement matrix (#326, gemini-3.5-flash)

| Finding / Theme | luna | kimi | hy3 | ChatGPT | Sonnet5 | GLM | Deepseek | Qwen | Count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Read-only overstated | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| Builder can edit config (mutable trust root) | Y | Y | Partial | Y | Y | Partial | Y | Y | 7/8 |
| `--allowedTools` dormant | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| Identity fails open | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| No explicit threat model | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| `--pure` bypass (disables all guard plugins) | Y | Y | Y | N | Y | Y | Y | Y | 7/8 |
| `--auto` injection | Y | Y | Y | N | N | Y | N | N | 4/8 |
| MCP write-tool gap (omits directory/move tools) | Y | Y | Y | Y | Y | N | Y | Y | 7/8 |
| Version conflation | Y | Y | Y | N | N | N | N | N | **3/8 (all internal)** |
| Countable errors | Y | Y | Y | N | N | N | N | N | **3/8 (all internal)** |
| Global whitelist plugin | Y | Y | Y | N | Y | N | N | Y | 5/8 |

### 2.3 Reading the agreement data

**Unanimous both waves (8/8 × 2):**

- **Read-only overstated** — 8/8 in wave 1 and 8/8 in wave 2. The strongest consensus cell: no model accepted "read-only by construction" once it saw the broad bash grants (`git *`, `opencode *`, `cargo *`, `npm *`) and finite blocklists. This survived the doc's own corrections between waves — rewording the claim did not change the models' verdict.
- **`--allowedTools` dormant** — 8/8 both waves. Every model, external and internal, independently concluded the fork-constructed tool-allowlist surface was not enforced end-to-end (wrapper drops the flag; `opencode run --help` lists no such flag).

**Identity fail-open** moved from 7/8 (wave 1; luna dissented) to **8/8** (wave 2) — luna's own wave-2 review of the corrected doc caught it once the identity-resolution path was described more fully (#321).

**Internal-only (both waves):** version conflation and countable errors were found **only** by internal models — no external model flagged either. Caveat on the count: the matrices show "3/8 (all internal)" for version conflation because they attribute Y to luna, but luna did **not** flag it (its wave-1 review explicitly declined to verify deployment versions; #315 WHAT-NOT-TESTED) — the true version-conflation catch is hy3 + kimi = 2 flagged. Countable errors were genuinely flagged by all three internal models (luna 29-vs-49 in #315, hy3 M2 in #316, kimi ~40-vs-33 in #317). These are the same-family blind-spot signal in reverse: external models cannot see deployment-vs-source drift or inventory counts because they have no runtime/artifact access; internal models share repo context and therefore see them.

**Split findings (mixed agreement):**

- **MCP tool names** — kimi alone asserted the blocked names were wrong (wave 1); Sonnet5/Deepseek/Qwen marked Partial (surfaced the tool-audit question without asserting names). Runtime evidence later refuted kimi's mechanism but confirmed its conclusion (§3.2). By wave 2, the MCP **write-tool gap** (create_directory/move_file unblocked) was 7/8 — only GLM dissented.
- **`--auto` injection** — 4/8 in both waves (luna/kimi/hy3/GLM). The wrapper behavior is repo-internal; the external models that missed it lacked the wrapper source.
- **Confidentiality/exfiltration** — 4/8 wave 1 (ChatGPT, Deepseek, Qwen, hy3), not tabulated as a separate row in wave 2. A genuine split: only a minority of models extended "permission" from write-authority to read-plus-egress.

---

## 3. Per-Model Observations (capability evidence, with issue refs)

### 3.1 hy3 — the meta-reviewer: caught contradictions the synthesis matrix missed

hy3's wave-2 review (#323) is the only review that audited the *synthesis artifact itself*. It caught two internal contradictions inside the reviewed doc's consensus matrix:

- **luna Y vs. "luna did not flag"** — the #319/#326 matrices list luna as "Y" on version conflation, but luna's actual review did not flag it. hy3 (#323): "claim (c) says luna did not flag the version conflation while the section 4 matrix lists luna Y." The reviewed doc itself later conceded: "the #319 matrix lists luna Y; the resolution below is verified directly regardless of count" (reviewed doc §3.3) — the true count is hy3 + kimi = **2 flagged**, not 3.
- **kimi refuted vs. confirmed** — the matrix framed kimi's MCP finding as refuted when only its *mechanism* (tool names) was wrong while its *conclusion* (MCP leg open) was confirmed. hy3 demanded the distinction be made explicit.

This is a distinct capability: **synthesis-quality auditing** — verifying that an agreement matrix's attribution cells match the underlying verdicts. hy3's wave-1 review (#316) also demonstrated the deepest source re-derivation of the wave (M1–M7, all against live CLI/source; WHAT-NOT-TESTED 1–8 explicitly scoped), consistent with its registry profile (novel edge-cases + source re-derivation, #176/#182).

### 3.2 kimi-k2.7-code — mechanism wrong, conclusion right (the sharpest correctness lesson)

kimi's wave-1 MUST-FIX (#317): "MCP filesystem write tools are mis-identified... the configured server is modelcontextprotocol server-filesystem, whose tools are named write_file, edit_file, create_directory, and move_file per upstream docs. Therefore orchestrator-guard does not close the MCP leg of the gap."

- **The mechanism was WRONG.** Runtime log evidence (`/tmp/orchestrator-guard.log`, the plugin's own append-only log) proved opencode's MCP client exposes the tools with the `filesystem_` prefix: `filesystem_write_file` (51 logged executions) and `filesystem_edit_file` (107) ARE the real runtime names. kimi consulted upstream server documentation, not opencode's client naming (its own WHAT-NOT-TESTED admits this).
- **The conclusion was RIGHT.** The same MCP server exposes `create_directory`/`move_file` (→ `filesystem_create_directory`/`filesystem_move_file`), which are NOT in `BLOCKED_TOOLS` — the MCP leg of the #33677 gap was genuinely open, just for a different reason than kimi stated.

Resolution (reviewed doc §3.4): **PARTIALLY CONFIRMED — names correct as opencode exposes them; the true gap is the unlisted MCP write tools.** The correct read: a model can be wrong about the mechanism and right about the conclusion; finding-level agreement must record the conclusion (gap open) separately from the mechanism (which names). This is the B2-divergence lesson (#241) in new clothing — verdict cells alone would have recorded kimi as "refuted" and lost the real finding.

### 3.3 hy3 + kimi — the internal-context advantage (version conflation)

The deployed-vs-source version conflation was caught **only by hy3 and kimi**, the two internal models that actually ran the live commands (`crosslink --version` = `0.9.0-beta.1+a87bd513` vs. `git describe` = `v0.9.0-beta.1-59-g6221309e`; wave 1: hy3 #316 M1, kimi #317; wave 2: hy3 #323, kimi #322). **All five external models missed it** — they had no binary access. luna is often counted as a third catcher because the #319/#326 matrices list luna Y, but luna did not actually flag it (see §3.1 — this is precisely the attribution error hy3 caught). The correct count is 2 flagged, both with runtime access. Same-family blind-spot signal, reversed: **repo-context-sharing models catch deployment-truth errors; context-free models cannot.** Routing implication: any wave reviewing claims about deployed state MUST include at least one model with runtime access.

### 3.4 The external five — the hostile-agent perspective (OS/container isolation)

The external models pushed systematically harder toward OS/container-level isolation than the internal three:

- Wave 2 remediation-strategy divergence is sharp: **luna/hy3/kimi recommended hardening the existing system** (fix MUST-FIX list, close MCP gap, fail closed on identity, document `--auto`); **ChatGPT/Sonnet5/GLM/Deepseek/Qwen recommended architectural refactor** — moving the trust boundary outside the agent process entirely (read-only mounts, separate users, containers/namespaces, out-of-process guard daemon, capability-based MCP tools).
- The adversary-model divergence is the explanatory variable: external reviewers default to a **misaligned/adversarial agent** threat model; internal reviewers assume **honest-but-buggy**. Sonnet5 (wave 2) makes the split explicit: "Prefix-matched shell strings checked by an in-process plugin are not a security boundary against a misaligned agent; they're a speed bump against a buggy one" — and "the distinction is the actual crux, and it's claim (k) — no threat model exists." ChatGPT (wave 2) frames it as a boundary problem: "the architecture is trying to establish repository integrity and authority isolation using mechanisms that live inside the same agent execution environment they are supposed to constrain."
- Each external model contributed a unique architectural proposal: ChatGPT's three-property distinction (A tool denial / B repository immutability / C authority isolation) + ten invariants; Qwen's revoke-bash-for-non-builders + ten threat classes; Deepseek's signed role tokens + policy daemon; GLM's out-of-process guard; Sonnet5's read-only bind mounts.

Capability reading: **external models are the independent adversary lens.** Their lack of repo context is a feature for threat-modeling (they cannot be assumed to trust the in-repo narrative), and a liability for deployment-truth findings (§3.3).

### 3.5 Delivery-failure modes (per-model, all issue-referenced)

- **hy3 (#323):** the wave-2 hy3 verdict could not be posted by hy3 itself — "Could not run crosslink to post the result (bash-deny rule; verified by two failed attempts)" (#323 WHAT-NOT-TESTED). The verdict was posted verbatim by the orchestrator-side agent from `/tmp/hy3-verdict-323.md`. This is a *self-consistent* failure: the read-only role definition blocks the very `crosslink` bash invocation needed to deliver its verdict (hy3 #316 noted the same unsatisfiable .md-vs-enforcement conflict). Plus the standing hy3 504 long-verdict history (Workflow Topology record §7.5: verdict lost to 504 twice, then chunked).
- **kimi (#317):** transient provider **Forbidden** — recorded in the #314 synthesis: "r2 kimi-k2.7-code (#317, retry after transient Forbidden)". Provider-side, resolved on retry; the review completed.
- **north-mini-code-free (#313 wave-1 auditor attempt):** provider **401** (auth) on the first auditor attempt — a distinct failure class from 429/rate-limit and silent-hang (permission-enforcement doc §6.6, reviewed doc §7.3).
- **Gemini #319/#326:** the synthesis agents stranded on shell-quoting (backticks + apostrophes) while posting their tabulated matrices; the workaround (write to `/tmp/gemini-synthesis-*.md`, then `crosslink issue comment ... "$(cat /tmp/...)"`) is recorded in the #319/#326 plans. A delivery-failure mode specific to long, quote-dense verdicts.

---

## 4. Non-Delivery as First-Class Outcome

Per the model-agreement schema (#241) and the workflow-topology design (§7.5), non-delivery is recorded as **data, not silence**. Every reviewer sub-issue that did not deliver its verdict through the nominal path is a first-class observation about the model *and* the harness:

| Incident | Wave | Model | Delivery failure | Outcome |
|---|---|---|---|---|
| hy3 #323 stranded | 2 | hy3 | bash-deny blocked `crosslink` posting (verified by two failed attempts) | Verdict delivered verbatim by orchestrator-side agent from /tmp |
| kimi #317 transient Forbidden | 1 | kimi-k2.7-code | Provider-side 403/Forbidden on posting | Resolved on retry; full review delivered |
| north-mini-code-free 401 | 1 (auditor attempt) | north-mini-code-free | Provider auth 401 on launch | Auditor re-dispatched on different model; 401 recorded as distinct failure class |
| Gemini #319/#326 stranding | 1 + 2 | gemini-3.5-flash | Shell-quoting (backticks/apostrophes) broke comment posting | Workaround: write to /tmp, post via `$(cat ...)`; verdict delivered |
| hy3 504 history (standing) | prior | hy3 | Long verdicts lost to provider 504 twice (Workflow Topology §7.5) | Chunked posting; pattern recorded |

The three failure classes are distinct: **harness-enforcement denial** (hy3 bash-deny — a policy interaction, not a model defect), **provider-side transient/auth errors** (kimi Forbidden, north-mini-code 401 — infrastructure), and **shell-quoting/verdict-shape failure** (Gemini — tooling interaction with long quote-dense text). All three are routing-relevant: they determine whether a given model+task combination can actually deliver.

---

## 5. Confidence + Correctness Anchors

Which claims carried external correctness anchors (runtime/artifact/test evidence) vs. reviewer-opinion-only:

| Claim | Anchor type | Evidence | Status |
|---|---|---|---|
| Deployed-vs-source version conflation | **Runtime anchor** | `crosslink --version` = `0.9.0-beta.1+a87bd513` vs. `git describe` = `v0.9.0-beta.1-59-g6221309e`; delta commit 6221309e touches launch.rs/prompt.rs (reviewed doc §3.3; hy3 #316 M1, kimi #317) | **CONFIRMED** — the strongest-anchored finding of the wave; the reviewed doc re-verified it live |
| MCP tool names (`filesystem_write_file` IS real) | **Runtime log anchor** | `/tmp/orchestrator-guard.log`: filesystem_write_file 51, filesystem_edit_file 107 executions; create_directory/move_file 0 (reviewed doc §3.4, verified-sources #27) | **CONFIRMED** — kimi's mechanism refuted, conclusion confirmed |
| Countable errors (49/21/34 vs 29/19/~40) | **Source anchor** | hook-config.json lines 128–176 (49), 16–36 (21); orchestrator.md (34) (hy3 #316 M2; reviewed doc §7.3 check script) | **CONFIRMED** — cheap, deterministic, re-checkable |
| Sync guard (fail-closed on stale hub) | **Level-2 test anchor** | #337 isolated behavioral test: DEMONSTRATED-FAIL-CLOSED — scratch env, sync refused, local comment survived; control + repro deterministic | **CONFIRMED** — the only finding with a dedicated behavioral test (relevant context for the durability findings the reviewed doc addresses) |
| `--auto` injection under tmux | Source anchor | `~/.local/bin/claude` lines 66–68 + `opencode run --help` (hy3 #316 M7) | **CONFIRMED at source level** — WHAT-NOT-TESTED: no live demonstration that ask→allow conversion occurs |
| Identity fail-open (fallback to builder) | Source anchor | crosslink-guard.ts lines 892–918 fallback; no `by_type.builder` entry (hy3 #316 M4a) | **CONFIRMED at source level** — not observed live (hy3's own session had CROSSLINK_AGENT_TYPE set) |
| Read-only overstated | Source anchor | reviewer.md/auditor.md bash grants + finite blocklists (all 16 reviews) | **CONFIRMED** — 8/8 × 2; the highest-agreement finding |
| OS/container-isolation refactor proposals | **Reviewer-opinion-only** | Architectural recommendations; no bypass executed by any reviewer (all wave-2 WHAT-NOT-TESTED sections) | **NOT TESTED** — directionally informed but zero live demonstrations; explicitly marked capability-inference, not proof |
| Confidentiality/exfiltration risk | **Reviewer-opinion-only** | hy3 #316 S6 confirmed env carries provider API keys (observed, not reproduced); no exfiltration demonstrated | **PARTIAL** — risk-flagged, not demonstrated |

The anchor hierarchy is the payload for the index (#241): claims with runtime/log/test anchors (version, MCP names, counts, sync guard) are provable; claims with only source anchors are high-confidence-but-not-observed; architectural recommendations are opinion data that must never be recorded as findings.

---

## 6. Feed to Registry + Routing Matrix

### 6.1 What the wave says about each model's review style/lens (per model-feedback template)

| Model | Review style/lens (this wave) | Strength | Blind spot / risk | Failure mode |
|---|---|---|---|---|
| **hy3** | Deep source re-derivation + **synthesis-quality auditing** (caught matrix attribution errors #323; M1–M7 with live CLI #316) | Finds what the matrix itself got wrong; deployment-truth verification | Findings can be implementation-heavy (prior profile) | Delivery starvation: bash-deny blocked posting (#323); 504 long-verdict history |
| **kimi-k2.7-code** | Source-grounded, mechanism-level claims; independently caught version conflation + env-fallback gap (#317) | Right conclusions even when mechanism is wrong (MCP gap) | Mechanism errors from consulting upstream docs instead of runtime (tool names) | Transient provider Forbidden (#317, resolved on retry) |
| **luna** | Systems/durability lens; wave-2 upgrade to boundary-redesign framing (deny-by-default capability boundary, #321) | Correct, concise, conditional-with-controls; caught countable errors (29-vs-49, #315); systems-level read-only critique | Wave-1 miss on identity fail-open (N in #319 matrix, Y by wave 2); did not flag version conflation (#315 WHAT-NOT-TESTED, #321) | None observed this wave |
| **ChatGPT web** | Structured security-property thinker (tool-denial / immutability / authority-isolation trichotomy; 10 invariants) | Forward-looking security argument; external adversarial lens | Missed internal-only findings; accepted MCP leg as closed (wave 1) | None observed (external; no delivery data) |
| **Claude Sonnet 5** | Architectural ceiling analysis: self-modifying trust root, fork justification on single incident (#156) | Names structural limits rather than patch lists | Missed `--auto`, version conflation | None observed |
| **GLM-5.2** | Enforcement-sprawl critic: stacking layers → larger attack surface; architecture contradictions | High-level architectural contradiction detection | Missed version/counts; N on MCP gap (wave 2) | None observed |
| **Deepseek-v4-Pro** | Threat-model inversion: the write-capable role should face the strongest curbs | Strong risk inversion argument; kill-switch fail-open catch | Missed internal-only findings | None observed |
| **Qwen3.8 Max** | Strongest external refactor push: category error, revoke bash for non-builders, VFS/identity isolation | Threat-model taxonomy (10 classes + control mapping) | Missed internal-only findings | None observed |
| **gemini-3.5-flash** (synthesis) | Tabulation/synthesis specialist: produced both agreement matrices (#319/#326) | Finding-level matrix construction; per-review summaries | Matrix attribution errors (luna Y cell) — synthesis output must be audited | Shell-quoting stranding on delivery (#319/#326); workaround needed |
| **north-mini-code-free** (auditor attempt) | (Not delivered) | — | — | Provider 401 on launch (distinct failure class) |

### 6.2 Routing-matrix updates implied

1. **Security/permission-boundary reviews: dispatch ≥1 internal (runtime-access) + ≥1 external model.** The 16-review wave shows the two groups find disjoint finding classes: internal-only (version conflation — hy3+kimi; countable errors — luna/hy3/kimi; wrapper internals like `--auto`) vs. external-only perspective (hostile-agent OS-isolation critique, threat-model taxonomy). Neither group alone gives the full picture. This extends the existing "luna+hy3+big-pickle" reviewer-selection rule (#190) with an explicit **context-mixing requirement**.
2. **Add hy3 to synthesis-check roles.** hy3's #323 matrix-attribution catch validates using a deep re-derivation model to audit synthesis output, not just to produce primary reviews.
3. **Record kimi's mechanism/conclusion distinction in the agreement index.** The MCP finding was conclusion-right/mechanism-wrong; per-claim cells must record conclusion and mechanism separately to avoid recording it as "refuted" (#241 implication).
4. **Delivery-failure modes are routing constraints.** hy3 (bash-deny starvation) and gemini-3.5-flash (shell-quoting) need delivery workarounds pre-dispatch (verdict-to-/tmp + orchestrator-side posting); kimi/north-mini-code transient auth errors are retry-class, not avoid-class.
5. **Verdict-level consensus is weak signal; finding-level is load-bearing.** 8/8 verdict-level consensus in both waves masked 5/8–3/8 finding splits; the index must keep finding rows as the primary record (#241 design confirmed by this wave).

---

## 7. WHAT-NOT-TESTED / OPEN QUESTIONS

- No reviewer (internal or external) executed a bypass; all write-path claims are capability inferences from permission maps/blocklists/help text, explicitly un-demonstrated (all WHAT-NOT-TESTED sections; #337 is the only behavioral test, and it covers the sync guard, not the permission boundary).
- The external models' OS/container-isolation proposals were not implemented or tested.
- Confidentiality risk was flagged but no exfiltration was demonstrated; API-key presence was observed by hy3 but not reproduced here.
- The 401/Forbidden incidents are single-observation classes (n=1 each); the auth-failure taxonomy (401 vs 429 vs Forbidden vs silent-hang) needs more incidents to be reliable.
- Matrix attribution accuracy was audited by one model (hy3, #323) on one wave; the wave-1 matrix (#319) may contain further attribution errors not yet caught.
- Open question for #241: whether "conclusion-level agreement" should be a separate cell from "mechanism-level agreement" in the standardized schema (this wave produced one clear case where they diverged).
