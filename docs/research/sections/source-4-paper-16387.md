---
title: "Source 4 — Fantastic Adaptive Taxonomies and How to Use Them (arXiv 2607.16387)"
program: EDASES
layer: Research
document_type: Report
status: Active
authority: Experimental
canonical_repository: edases
related_documents:
  - "Issue #429 — MAST + AdaMAST + ATLAS repos and two arXiv papers comparison"
  - "Source 1 — MAST (this worktree sibling file, not reused here)"
  - "docs/research/Workflow Topology Design and Reasoning Record.md"
  - "docs/ORCHESTRATOR.md"
supersedes: []
last_updated: 2026-08-24
---

# Source 4 — Fantastic Adaptive Taxonomies and How to Use Them (arXiv 2607.16387)

**Source:** arXiv 2607.16387 — Cemri et al., *Fantastic Adaptive Taxonomies and How to Use Them*, v2 2026-07-29. Repository: https://github.com/multi-agent-systems-failure-taxonomy/AdaMAST. No other sources consumed per #429 atomized scope.

**Fetch method (mandate-compliant):** CLI only — no WebFetch tool used. Commands executed on 2026-08-24 in worktree `feature/pp3g-K7Ak-atomized-source-worker-4-of-5-v2-429-cli-fetch-method`:

```
mkdir -p /tmp/opencode/src4 \
  && curl -sL --retry 2 -o /tmp/opencode/src4/abs.html https://arxiv.org/abs/2607.16387 \
  && curl -sL --retry 2 -o /tmp/opencode/src4/full.html https://arxiv.org/html/2607.16387v2
```

Local reads: `/tmp/opencode/src4/abs.html` (44,888 bytes, arXiv abs page) and `/tmp/opencode/src4/full.html` (559,887 bytes, arXiv HTML v2 via LaTeXML). Text extraction stripped `<script>/<style>` and tags into `/tmp/opencode/src4/body.txt` (~126K body chars post-introduction, 133K full extraction). Citations below are against that local HTML rendering; PDF not consumed.

**Atomized scope:** This file covers ONLY arXiv 2607.16387. No synthesis across sibling sources (MAST/AdaMAST/ATLAS/2607.28802) — collator owns cross-walk. No claim is borrowed from other fetches.

**Author-claim vs. inference discipline:** Every numbered claim in §2 is labeled **Author claim** (paper assertion) or **Repo-evidenced** (visible in HTML/repo artifact). My inference is confined to §6 and explicitly marked. Negative-space disclosure (`WHAT-NOT-TESTED`) follows each evidence-quality judgment.

---

## 1. Source Identity and What Was Accessible

| Artifact | Accessible? | Notes |
|---|---|---|
| arXiv abs page (`/abs/2607.16387`) | Yes | `og:title` = *Fantastic Adaptive Taxonomies and How to Use Them*; `citation_author` = Cemri, Mert + 11 co-authors (Cojocaru, Pan, Liu, Agarwal, Krentsel, Tang, Ramchandran, Gonzalez, Zaharia, Dimakis, Stoica); `citation_date` 2026-07-17, `citation_arxiv_id` 2607.16387, `citation_online_date` 2026-07-29; abstract HTML matches HTML paper abstract verbatim. |
| arXiv HTML v2 (`/html/2607.16387v2`) | Yes | Full paper LaTeXML rendering with TOC §1–6 + Appendices A–I, figures/tables/citations intact; body extraction used. |
| Paper PDF | Not fetched per mandate (HTML is evidential basis; PDF layout not verified) | Marked not inspected. |
| AdaMAST GitHub repo | Not fetched in this atomized worker (no git clone, no WebFetch per ban) | Repo URL cited in paper (`Code: https://github.com/multi-agent-systems-failure-taxonomy/AdaMAST`); this file makes no repo-content claim beyond that citation. Marked not tested. |
| MAST repo (parent work) | Not fetched here | Sibling worker #1 covers MAST; not reused. |

**Honesty marker:** No content below is fabricated from unfetched repo state. Where HTML rendering is truncated or ambiguous (e.g., figure images not rendered, math as `{\sim}18\times`), it is noted.

---

## 2. Core Claims (strictly the paper's — load-bearing quotes included)

> In this section **Author claim** = sentence is in the paper and quoted/paraphrased with locus; **My inference** is flagged explicitly. Certainty annotations follow AGENTS.md reasoning-certainty rules.

### Claim 1 — Raw traces are a poor feedback medium; a named, durable failure vocabulary should replace them as the feedback interface

**Author claim (Abstract, verbatim):**

> "An agent system's execution traces record how it fails, and procedures that improve such a system without changing model weights (trajectory selection, prompt and workflow optimization, runtime monitoring) read these traces for feedback. Yet raw traces are a poor medium for accumulating that feedback: long, instance-specific, and lacking a stable vocabulary for recurring failures. We argue that an agent system should instead maintain an explicit representation of how it fails, induced from its own behavior and reusable wherever failure feedback is needed."

**Author claim (Introduction):**

> "Our central claim is that the raw trace need not double as the feedback interface: what can serve instead is an artifact durable like a score and diagnostic like a critique, a compact vocabulary of named failure modes, produced once from the system's own traces."

**Author claim (Introduction, amortization thesis):**

> "The claim is amortization, not prompt formatting (section I.2): each target system's taxonomy is induced and validated once, then consumed unchanged by every procedure that reads its traces."

Relevance to us: This positions the taxonomy as infrastructure amortized across consumers, not per-run prose — directly maps to our durability/claim-discipline concerns.

**WHY / WHAT / HOW CERTAIN:** WHY — authors diagnose scalar outcomes (lose "why") and free-text critiques (re-diagnosed per run, non-reusable). WHAT — basis is their characterization of current trace-consuming procedures. HOW CERTAIN — conceptual framing, proven only via downstream gains (§4–5). Evidence-based for problem framing, not yet proven at this claim alone. **WHAT-NOT-TESTED:** No independent measurement here of trace reuse cost vs. vocabulary cost — that evidence is deferred to §5.4.

### Claim 2 — Fixed catalogues (exemplified by MAST's 14-mode taxonomy) are structurally insufficient; vocabularies must be induced from the target system's own traces

**Author claim (Introduction, verbatim):**

> "MAST [4], the reference catalogue for multi-agent failures, distills fourteen recurring failure modes from hundreds of annotated traces, and it remains a strong baseline throughout our experiments. But a catalogue fixed before the target system is observed faces a limit that is structural, not a consequence of quality: role-specific failures presuppose roles that exist only once an architecture is instantiated, and domain-specific failures presuppose task knowledge no general catalogue enumerates."

**Author claim (Introduction, measurability):**

> "The gap is measurable: taxonomies we induce for six domains share codes at a mean pairwise Jaccard of only 0.14 (Section 5.2); were a fixed checklist sufficient, induction would keep rediscovering it."

Role axis evidence: Frontier-CS multi-agent induces 13 role codes; flat solver–verifier on TheoremQA induces none (Method). Illustrative unforeseeable codes: "a competitive-programming agent committing to a greedy strategy where the problem requires dynamic programming, or a STEM agent producing a numerically coherent derivation that violates a physical law."

**WHY / WHAT / HOW CERTAIN:** WHY — fixed vocabularies cannot anticipate instance-specific roles/tools/domains. WHAT — six-domain Jaccard + role-code induction asymmetry. HOW CERTAIN — evidence-based (quantitative overlap + constructive example). **WHAT-NOT-TESTED:** No test of a richer fixed catalogue larger than MAST; claim is structural, not bounded-size.

### Claim 3 — AdaMAST induces compact, evidence-grounded taxonomies along three fixed axes with zero hand-authored codes, gated by inter-annotator agreement and maintained online

**Author claim (Abstract + §1, verbatim):**

> "AdaMAST builds this representation by converting a target system's traces into a compact, evidence-grounded failure taxonomy: named failure codes organized along three fixed axes (system-level, role-specific, and domain-specific), with every name, definition, and evidence pattern induced from the traces; no code is hand-authored, no trace human-annotated."

**Author claim (Contributions, verbatim bullet):**

> "Adaptive failure taxonomies from traces. A pipeline that induces compact, evidence-grounded failure taxonomies from a target system's execution traces along three fixed axes (system-level, role-specific, domain-specific), with no hand-authored codes and no per-trace human annotation, gated by inter-annotator agreement before deployment and refined online as the system evolves (Section 3.1)."

Axes definition (Method, verbatim):

> "Only the axes are fixed, so that taxonomies stay comparable across systems and every code maps to an intervention point. The codes themselves (names, definitions, role labels, and evidence patterns) are induced from the traces: no code is hand-authored, no trace human-annotated. A taxonomy is accepted only when independent annotators apply it consistently to held-out traces, so the artifact is auditable before anything consumes it (Section 3.1). Moreover, as the system evolves, online refinement merges, adds, or relabels codes, so the vocabulary tracks the current system, rather than a snapshot of its past (Section 3.3)."

**Gate specifics (Fig. 2 caption, verbatim):**

> "inter-annotator agreement gates deployment: four independent LLM annotators label stratified held-out traces under a five-phase deliberation protocol, over up to five rounds of five traces each; the taxonomy is accepted once mean pairwise area-level agreement reaches κ ≥ 0.75 with a coverage floor of 0.70, and a failed round triggers merge/add/relabel edits and re-runs (Appendix B.2)."

Online refinement (Method, verbatim):

> "Because a taxonomy describes the system whose traces produced it, any consumer whose target system changes can invoke an online refinement round: the current taxonomy is replayed against a pool of recent traces and merge, add, and relabel edits are proposed, exactly as in the gate's failure loop."

**WHY / WHAT / HOW CERTAIN:** WHY — operationalize Claim 2 into an implementable induction lifecycle. WHAT — pipeline description + gate thresholds. HOW CERTAIN — evidence-based as mechanism description (not yet effectiveness). **WHAT-NOT-TESTED:** Human labor in LLM annotators not zero; LLM-as-annotator reliability is separately validated in §5.1, not assumed here.

### Claim 4 — The induced vocabulary itself is compact, human-faithful, and adaptive (artifact-level properties independent of downstream gains)

**Author claim (Abstract, verbatim compressed properties):**

> "Beyond these downstream gains, the induced vocabulary is compact, compressing the failure-relevant content of traces by an order of magnitude while largely preserving their distinctions; human-faithful, matching expert failure annotations more closely than a hand-crafted reference vocabulary; and adaptive, with taxonomies induced for different domains sharing only a small fraction of their codes."

**Author claim (Contributions, verbatim metrics):**

> "The taxonomy as a measurable feedback interface. Independent of downstream gains, the induced vocabulary is compact without collapsing distinctions (∼18× compression, 89% unique code signatures; Section 5.4), aligns with expert annotations better than a hand-crafted vocabulary under a matched panel (κ = 0.682 vs. 0.516 on TRAIL; Section 5.1), and genuinely adapts to its target (mean cross-domain Jaccard 0.14; Section 5.2)."

TRAIL isolation (Abstract, verbatim substring): "matching expert failure annotations more closely than a hand-crafted reference vocabulary"

**WHY / WHAT / HOW CERTAIN:** WHY — establish artifact trust before downstream consumption. WHAT — §5 measurements (compression, TRAIL κ, Jaccard). HOW CERTAIN — evidence-based per reported §5 protocol. **WHAT-NOT-TESTED:** §5 protocol details are methodological (see §5 of main paper + Appendices E/F); not independently replicated here.

### Claim 5 — One interface, three consumers: the same induced vocabulary improves search, runtime monitoring, and trajectory selection (downstream effectiveness)

**Author claim (Abstract, verbatim):**

> "In agent-system search, taxonomy-coded diagnoses of failed candidates outperform free-form reflection on all five benchmarks we test. At runtime, taxonomy feedback raises SWE-agent's resolution on SWE-bench Verified Mini from 60% with free-text reflection to 70%, and improves Claude Code from 64.0% to 70.7% as a runtime skill. In trajectory selection, AdaMAST-Judge, a verifier built on the induced codes, improves best-of-5 accuracy on Terminal-Bench 2.0 by 8–15 points over Pass@1."

**Author claim (Contributions, verbatim inclusive of MAST baseline):**

> "One interface, three consumers. Taxonomies induced by the same pipeline, consumed unchanged within each target system, improve agent-system search on five benchmarks (Section 4.2), raise SWE-agent's resolution on SWE-bench Verified Mini from 60% (Reflexion) and 68% (MAST) to 70% via an in-context integration (Section 4.3), and improve best-of-5 selection on Terminal-Bench 2.0 by 8–15 points over Pass@1, retaining a +3.4 to +4.5 point margin over the fixed MAST vocabulary on the two non-saturated harnesses (Section 4.4)."

**WHY / WHAT / HOW CERTAIN:** WHY — demonstrate reusability across dissimilar consumers. WHAT — §4 matched comparisons. HOW CERTAIN — evidence-based as paper-reported with matched backbones; causality caveats noted by authors (see §4.2 Fig. 4 caption: "We read this figure as a within-run mechanism trace, not an independent causal ablation"). **WHAT-NOT-TESTED:** No fifth setting beyond the three; cross-domain transfer to OfficeQA is single-run, not confirmatory (authors say so explicitly).

---

## 3. Mechanism Contributions

### 3.1 Three fixed axes as organizational scaffold, not optimal partition

AdaMAST organizes every code along:

- **Axis A — System-level:** "remedy is to repair the harness or orchestration around the agents"
- **Axis B — Role-specific:** "rewire a discovered role" — codes are fully trace-induced, roles themselves discovered from the architecture via regex + LLM role-inference (B.1 Step 2); B-codes exist only when architecture has differentiated roles
- **Axis C — Domain-specific:** "inject task knowledge"

**Paper notes the axes are a scaffold, not claimed optimal:**

> "We treat the three axes as a practical organizational scaffold rather than a uniquely optimal partition. In a three-seed granularity ablation, the full taxonomy is directionally higher than a flat code list by 3.3 percentage points on TheoremQA and 1.7 percentage points on MMLU-Pro, but neither difference is statistically conclusive (Appendix I)."

**Contribution:** Axes make taxonomies comparable across systems and map every code to an intervention point. C-codes are entirely domain-specific; B-codes appear only in multi-agent systems; A-codes form a partial universal backbone (see §5.2 / Appendix A.6: full Jaccard 0.14 vs. A-code-only J 0.47 and universal-backbone projection 0.50).

**What is hand-authored vs. induced — subtle but load-bearing:** System-level and domain-specific *candidate* codes are seeded by broad priors that the pipeline's own analysis phase proposes (coarse architectural-risk patterns, common domain error modes, suggested before any trace is examined), but "a seeded candidate is retained only when trace evidence supports it." Role-specific candidates have no such prior. No code is hand-authored offline by a human — priors are LLM-generated inside the run. This nuance matters for reproducibility claims.

### 3.2 Taxonomy induction pipeline — four phases, eight steps, with amortization

**Four phases:** `analysis` → `curation` → `consolidation` → `inter-annotator agreement`. The split is deliberate: analysis grounds generation in observed behavior before curation proposes codes.

**Eight-step realization (Appendix B.1, not 1:1 with LLM calls):**

1. Domain analysis — domain, subdomains, terminology, common error patterns from stratified trace sample
2. Role and topology discovery — regex + LLM infers functional roles/topology; roles like solver/checker/refiner/coordinator are examples only
   - Signal extractor (LLM-free) identifies truncation, looping, refusal, tool errors
3–5. System-level / Role-specific / Domain-specific code generation — two complementary passes per category + within-category consolidation; Category B considers all discovered active roles jointly, every code tagged `applies_to_role`
6. Cross-category deduplication — strict boundary rules
7. Structural validation — category placement, naming, role attribution
8. Quality and coverage check — overlap, structural issues, coverage gaps → targeted repairs

**Amortization accounting:** Construction is variable-call cost per target system/domain, then reused unchanged. Appendix B.5 gives cost windows; Section 3.1 states: "Taxonomy construction is therefore a one-time, variable-call cost per target system, amortized across every downstream procedure and trace that later consumes it." Each refinement adds a bounded number of calls on top.

**Inventory dynamics (Table 10, evidence-based measurement, not model):** Across 203 complete generation records (same pipeline version): median raw 24 → final 20 codes (pooled 5,379 → 4,498, 16.4% reduction). 181 shrank, 7 unchanged, 15 grew. First refinement (n=32): median 22.5 → 21 codes (0–21.8% IQR reduction, median 4.7%). Generation and refinement can both consolidate and expand.

### 3.3 Inter-annotator agreement gate — the deployment gate (not a correctness certifier)

**Paper is explicit that the gate certifies applicability, not correctness:**

> "This gate certifies that the taxonomy is consistently applicable; it does not certify that its codes are correct. Correctness is assessed externally, against expert human annotations, in Section 5.1."

**Protocol (Appendix B.2, Fig. 2):** Four LLM annotators (cross-family in the rigorous run: Claude Opus 4.7, GPT-5.4, Gemini-2.5-Pro, GPT-5.4-mini per B.3) independently label same held-out trajectories under five sequential phases — (1) independent error discovery, (2) error reconciliation with 2-of-4 quorum, (3) failure typing into A/B/C, (4) code assignment with format validation, (5) code-level deliberation bounded at two rounds — with a shared knowledge base (decision rules, anchor examples, confusion pairs) accumulating across rounds. **Thresholds:** mean pairwise Cohen's κ ≥ 0.75 at failure-area level + coverage floor 0.70, over up to five rounds of five stratified traces each; failure triggers merge/add/relabel edits and re-run.

**Why this matters for us:** Our own failure matrix and claim discipline rely on human review. The paper separates applicability (LLM-LLM consistency) from correctness (LLM-human agreement on TRAIL) — a distinction we should adopt if we gate any adaptive taxonomy on LLM judgments.

### 3.4 Online refinement — taxonomy lifecycle, not per-consumer hack

Refinement reuses the gate's edit operators (merge/add/relabel) replayed against recent traces. Trigger is consumer-specific:

- **Search (Section 3.3):** Triggers on stagnation of evaluator score (warmup 5 rounds, stagnation window 10 iterations, ε 0.10 above noise floor, minimum refine interval 10 iterations — Table 11). Operates over post-warmup trace pool so vocabulary co-evolves with system: "search changes the system, the system's new traces revise the taxonomy, and the revised taxonomy shapes the next round of search."
- **Other consumers:** "whenever the target system or its trace distribution shifts, any of them can invoke the online refinement round." Refinement events are bounded and measured (Appendix G: iterations 29 and 78 each precede breakthrough score jumps at 69 and 89 — correlated, not claimed causal).

### 3.5 Three taxonomy-conditioned consumers (conditioning = interface, not component)

The paper stresses AdaMAST introduces no consumer; it supplies the vocabulary they share. Conditioning means "the failure-relevant portion of its output is constrained to the taxonomy's code set: it reports which codes fired, on which evidence."

**Consumer 1 — Agent-system search (Section 3.3):** Plugs into AdaEvolve (seed = minimal three-agent analyzer/solver/verifier, sequential solve-verify-refine loop). Mutator receives taxonomy-coded diagnosis of parent's failed traces: recurring codes + quoted evidence + cross-problem patterns (e.g., `B.6 Coordinator_Aggregation_Mismatch` fires with "aggregated results conflict due to divergent FINAL ANSWER lines across branches"). Codes are the signal: "they fire disproportionately on breakthrough parents, and all existed in the taxonomy before the jumps, so the gains come from the mutator acting on established codes."

**Consumer 2 — Runtime monitoring (Section 3.4):** Induced taxonomy enters the acting agent's context; the agent itself reviews its own recent trace at declared checkpoints at no additional LLM calls beyond the agent's own. Delivery adapts to harness: Claude Code exposes mid-run hooks (after tool calls, sub-agent completion, task completion) → drop-in runtime skill; SWE-agent has no enforcement logic → checkpoints declared in instructions + submit-gate. Checkpoints: observable (environment events), introspective (agent state transitions), mandatory pre-submission check. Bounded repair loop ≤3 attempts: "after which the agent must report any remaining issues rather than claim success."

**Consumer 3 — Trajectory selection (Section 3.5, AdaMAST-Judge):** Each code becomes a verification criterion: semantic failures → LLM scoring prompts (e.g., "does this trajectory exhibit Defensive_Pivoting?"), structural failures → heuristic checks (trace length, retry counts). A per-harness forward selector under leave-one-task-out CV retains only most discriminative criteria; pool is induced per target system, not fixed. Authors flag that selection gains reflect both codes and selector — "search and runtime monitoring, where codes are consumed directly, carry the cleanest vocabulary claims."

---

## 4. Evaluation Methodology and Evidence Quality

### 4.1 Setup — benchmarks, models, matched comparisons (Section 4.1 + Appendix B)

**Benchmarks by setting:**

| Setting | Benchmarks | N (test) | Integration note |
|---|---|---|---|
| Search | Frontier-CS (competitive programming)* | 132 unseen | Single run |
|  | OlympiadBench (math competition) | 655 held-out (20 dev during search) | Longest trace (97 iter), cleanest held-out estimate |
|  | MMLU-Pro (STEM QA subset) | 40 (two-seed mean) | Small — multi-seed replication in C.1 |
|  | TheoremQA (graduate math) | 30 (n=4 seeds) | Flat solver–verifier, no B-codes |
|  | DROP (discrete reasoning) | 30 (n=5 seeds) | Small |
| Runtime | SWE-bench Verified Mini (SWE-agent, GPT-5 solver) | 50 (1 seed) | 75 LLM calls/instance, $4/task, $200/run, greedy |
|  | SWE-bench Verified Mini (Claude Code, Haiku 4.5 solver) | 150 (3 seeds × 50) | Native self-verification vs. SWE-agent's prompted reflection |
|  | OfficeQA Pro (cross-domain transfer) | 133 hard oracle-parsed | Single-run, no budget matching — not confirmatory |
| Selection | Terminal-Bench 2.0 (terminus-2, claude-code, ForgeCode harnesses) | 89 tasks; 17–35 swing tasks per config (mixed pass/fail across 5 trials) | Leave-one-task-out CV for selector |
| Validation | TRAIL (117 GAIA-derived traces, 4 expert annotators) | 20-category hand-crafted gold | No TRAIL labels used to induce taxonomy |

*Frontier-CS is author-introduced (Mang et al., 2025, arXiv:2512.15699) — potential lineage bias.

**Models (Section 4.1 + B.3):** Search/taxonomy generation/mutation/free-form reflection = GPT-5.4-mini. Claude Code harness = Claude Haiku 4.5 solver (with Claude Opus 4.6 agents underpinning TB selection per B.3 string: "all three agents based on Claude Opus 4.6"). SWE-agent harness = GPT-5 solver. Terminal-Bench verifier = GPT-5.4. TRAIL panel = Claude Opus 4.7 + GPT-5.4 + Gemini-2.5-Pro + GPT-5.4-mini (cross-family). **Note:** GPT-5.4 / Opus 4.7 / Haiku 4.5 nomenclature is not verifiable against public model catalogs at time of writing; quoted as paper-reported identifiers.

**Matched comparisons (paper's stated control, verbatim):**

> "Our comparisons hold the surrounding procedure fixed and vary only the source of failure feedback. Search uses the same AdaEvolve backbone, seed architecture, and iteration number; within each runtime harness, variants use the same solver, instance set, and evaluation protocol; selection uses the same trajectory pools and verifier pipeline. This isolates whether replacing free-form or fixed failure feedback with induced taxonomy feedback changes the downstream procedure."

For us: This is a within-harness content ablation (Reflexion vs. MAST vs. AdaMAST share identical scaffold; Base vs. reflection ladder isolates "does adding reflection help" from "what should anchor it"). Cross-harness numbers are not compared — authors state this explicitly (Section 4.3: "The two harnesses are therefore separate case studies, not a controlled pair… no number compared across them").

### 4.2 Search results — evidence quality

**Paper-reported post-search accuracy (Table 1, Figure 3):**

| Benchmark | Problems | Pre-Evol | LLM Guidance (free-text reflection) | AdaMAST | AdaMAST Δ vs Guidance |
|---|---|---|---|---|---|
| Frontier-CS | 132 unseen | 20.8% | 26.0% | **32.7%** | +6.7 pp |
| OlympiadBench | 655 held-out | 84.6% | 87.9% (89.5% MAST-guided third arm) | **91.9%** | +4.0 pp (+2.4 pp over MAST) |
| MMLU-Pro | 40 (2-seed mean) | 21.3% | 35.0% | **42.5%** | +7.5 pp |
| TheoremQA | 30 (4-seed mean) | 39.0% | 60.0% | **65.0%** | +5.0 pp |
| DROP | 30 (5-seed mean) | 80.3% | 88.2% | **91.7%** | +3.5 pp |

All five favor AdaMAST. Authors' own framing (Figure 4 caption): "We read this figure as a within-run mechanism trace, not an independent causal ablation." Vanilla saturates at iteration 26 (dev 0.30); AdaMAST reaches 0.40 early, jumps 0.40→0.50 at iteration 69 and 0.50→0.55 at iteration 89; gains carry to held-out (Figure 4b).

**Evidence quality assessment:**

- **Strengths:** Same backbone/seed/budget; largest benchmark (OlympiadBench, N=655 held-out) provides cleanest estimate and includes MAST-guided third arm (89.5% — AdaMAST still +2.4 pp). Breakthrough analysis (Table 2) maps fired codes → concrete architecture edits (e.g., 67→69: A.3/B.3/C.2 → final-answer verifier + tournament solver pool + edge-case checks; 79→89: A.6/B.6/C.3 → planner upstream, verifier promoted to score boost). Codes fire disproportionately on breakthrough parents and pre-existed — authors present this as signal vs decoration.
- **Caveats marked by authors:** Frontier-CS and OlympiadBench are **single runs** (no variance). Small benchmarks (40/30) rely on multi-seed means but remain low-N. Search ablations (C.1–C.4), wrong-domain transfer (C.2), and sample efficiency (C.3) are in appendix — not evaluated here as primary evidence. Frontier-CS as author-introduced benchmark may inflate relevance.
- **Confidence:** Evidence-based that taxonomy-coded mutation outperformed free-text under stated budgets; **not proven** that gains generalize beyond the tested AdaEvolve backbone or that MAST→AdaMAST gap (+2.4 pp on OlympiadBench) replicates.

**WHAT-NOT-TESTED:** Statistical significance per benchmark not shown in main Table 1; cost/latency parity not shown here (Appendix B.5/C.3 cover it separately, not verified here). No test with stronger free-text baseline (e.g., chain-of-thought critique with retrieval).

### 4.3 Runtime results — evidence quality

**SWE-bench Verified Mini (Table 3, Appendix H):**

| Variant | Claude Code (Haiku 4.5, N=150 = 3×50) | SWE-agent (GPT-5, N=50) |
|---|---|---|
| Base | 64.0% | 50% |
| Reflexion | — | 60% |
| MAST (14-code, same delivery) | 67.3% | 68% |
| **AdaMAST** | **70.7%** | **70%** |

**Author thesis per harness (Section 4.3, verbatim split):**

> "on Claude Code, whether anchoring an agent that already self-verifies to its induced failure vocabulary further resolves it; on SWE-agent, where reflection must be added wholesale, what content the added reflection should carry."

**Evidence quality assessment:**

- **Claude Code (150 sessions, 3 seeds):** +6.7 pp over Base, +3.4 pp over identical-skill MAST. Per-seed gaps +10/+8/+2 pp — directionally consistent, magnitude variable across seeds. Authors note gain is vocabulary-specific: "the induced 32-code taxonomy's role axis names single-agent phases (Edit/Plan/Verify) rather than multi-agent roles, and the induced vocabulary primarily reduces verification-phase failures, including B.8 Verify ignored import or syntax errors and B.6 Plan skips verification loop, while MAST's reductions concentrate on broader patch-footprint errors (B.3 Edit overbroad patch footprint)."
- **SWE-agent (50 sessions, 1 seed):** 70% = +20 pp over Base, +10 pp over Reflexion (free-text), +2 pp over MAST (fixed checklist). Authors isolate content: "adding prompted reflection at all recovers +10% over Base, anchoring it to a categorical vocabulary adds a further +8% (MAST over Reflexion), and the induced, harness-specific vocabulary adds another +2%."
- **MAST as baseline:** "Fixed catalogues remain strong baselines (MAST reaches parity with AdaMAST in some runtime settings; Section 4.3), which sharpens rather than undercuts the distinction: what an adaptive vocabulary adds is the role- and domain-specific long tail that no pre-committed catalogue can anticipate." This is an honest margin: AdaMAST's edge over MAST in runtime is small (2–3 pp).
- **Cross-domain OfficeQA:** 69/133 vs 59/133 for Base under Claude Code with 15-code taxonomy induced from 50 transcripts. **Authors explicitly qualify (verbatim):** "Because this is a single-run transfer study without budget-matched accounting, we treat it as evidence that the integration operates in a new domain rather than as a confirmatory effectiveness comparison."

**WHAT-NOT-TESTED:** No N=150 replication for SWE-agent; single-seed 50-instance estimates have wide CIs (~±12 pp). No blind evaluation of patch correctness beyond SWE-bench harness verdicts. No cost/latency breakdown in main (Appendix H covers, not inspected here). No direct test that checkpoint taxonomy consumption doesn't cause repair-loop overfitting (bounded at 3 attempts + mandatory reporting mitigates but not measured).

### 4.4 Selection results — evidence quality

**Terminal-Bench 2.0 best-of-5 accuracy (Table 4, fixed trajectory pools, §3.5 verifier pipeline; MAST row = same pipeline with fixed 14-code MAST vocab):**

| Method | terminus-2 | claude-code | ForgeCode |
|---|---|---|---|
| Pass@1 | 61.8% | 57.5% | 81.8% |
| LLM-as-a-Verifier | 71.2% | 61.2% | 86.5% |
| MAST | 68.5% | 69.0% | 88.8% |
| **AdaMAST-Judge** | **73.0%** | **72.4%** | **89.9%** |
| Oracle best-of-5 | 77.5% | 80.5% | 89.9% |

AdaMAST-Judge: +11.2 / +14.9 / +8.1 pp over Pass@1; +4.5 / +3.4 / +1.1 pp over MAST. ForgeCode is near ceiling (89.9% = oracle) — "so the comparison is less informative."

**Discriminativity check (Figure 5, 85 trials on 17 swing tasks only):** Passing median 3 fired codes vs failing median 4; fewest-fired-codes heuristic → 67% swing-task accuracy vs 58% uniform (+9 pp) — signal exists before learned selector.

**Held-out check (author framing, verbatim):**

> "As a sanity check against the taxonomy overfitting the evaluation pool, a held-out 5-fold validation regenerates the taxonomy on train folds and evaluates on held-out task categories; held-out accuracy meets or exceeds the same-pool result on the two non-saturated configurations. We report this as a robustness check rather than a confirmatory result."

**Evidence quality assessment:**

- **Strengths:** Same trajectory pools + verifier pipeline; forward selector under LOO CV; per-harness selector prevents cross-harness tuning.
- **Caveats flagged by authors themselves (Section 3.5, verbatim):** "Because selection routes the vocabulary through this learned machinery, its gains reflect both the codes and the selector that consumes them; search and runtime monitoring, where codes are consumed directly, carry the cleanest vocabulary claims." This is the strongest honesty signal in the paper — selection is the least isolated test of vocabulary content.
- **WHAT-NOT-TESTED:** No test with taxonomy ablated but selector retained on random codes; no cost/latency vs plain verifier; cheaper verifier / top-K / token-matched ablations are in Appendix D (D.1 wrong-domain, D.2–D.5), not primary evidence.

### 4.5 Taxonomy validation — evidence quality (Section 5, Appendices A–F)

**Human faithfulness on TRAIL (§5.1, Table 5):**

| Vocabulary | Panel | Area-κ vs 4-expert gold |
|---|---|---|
| TRAIL hand-crafted (20 cats) | matched panel + prompts | 0.516 |
| AdaMAST-induced | matched panel + prompts | **0.682** |
| AdaMAST-induced | span grounding + deliberation (full protocol) | **0.725** |

Same-model panel (four GPT-5.4) drops 0.682 → 0.625 at 1-of-4 reporting threshold — "indicating that at this threshold the alignment is carried by the induced codes rather than by a labeling regime shared within one model family."

**Cross-domain adaptivity (§5.2):** Six evolution domains, mean pairwise Jaccard on full code sets = **0.14** (Figure 9a); projected onto universal failure backbone = **0.50**; A-code-only mean = **0.47** (Table 9, Appendix A.6). C-codes entirely domain-specific (Table 8 examples: `Complexity_Class_Constraint_Mismatch`, `Physical_Law_Violation`, `Negotiation_Leverage_Failure`); B-codes exist only in multi-agent topologies (Frontier-CS 13B, TheoremQA 0B).

**Failure modes over search (§5.3, OlympiadBench):** By iteration 92, 12/28 mid-run codes retired, severity-weighted burden −23% though firings/iter stay flat; B-share 39.8%→46.9% as roles added, C-share 32.0%→25.5% as solver acquires guardrails.

**Compression (§5.4, Appendix E):** On 223 traces from SWE-bench runtime study: **~18× compression**, median 5 codes/trace, 30 codes all fire, **89% unique code signatures** (near-unique diagnoses). Functional substitution (Qwen3.5-122B/27B predicting held-out success given verbatim pool vs induced taxonomy, N≤40 labeled runs): Terminal-Bench taxonomy matches verbatim pool at every N with ~95× fewer tokens (1.2K vs 114K); TheoremQA taxonomy alone strongest at every N for 27B (0.925 vs 0.850 at N=20, p≤0.012), verbatim pool degrades to 0.767 at N=40 below no-context 0.850. **Injection-location ablation (verbatim):** "Consumption is most effective when the taxonomy is simply present in context: a paired ablation that forces the consumer to audit the current run code-by-code before deciding lowers accuracy (−0.13 to −0.24, p≤0.006) by biasing it toward predicting failure even when the run succeeds (Appendix E)."

**Evidence quality assessment:** Protocol is well-specified (5-phase deliberation, coverage/accommodations, mapping to TRAIL categories in F.6). Leaf-level diagnostics and vocabulary comparison in F.4–F.5 provide granularity. **WHAT-NOT-TESTED:** Independent re-annotation of TRAIL under same prompts not performed here; entropy/compression measurement details (E.1) rely on authors' token accounting; functional substitution uses Qwen consumers not deployed in main experiments.

---

## 5. Stated Limitations (what the authors explicitly mark — not my inference)

The paper has no dedicated "Limitations" section; limitations are distributed and phrased as scoped claims or explicit qualifications. Listed here with loci; no inference added:

1. **Axes not claimed optimal (§3, Appendix I):** "In a three-seed granularity ablation, the full taxonomy is directionally higher than a flat code list by 3.3 percentage points on TheoremQA and 1.7 percentage points on MMLU-Pro, but neither difference is statistically conclusive."

2. **Selection gains confounded with selector (Section 3.5, 4.4):** "Because selection routes the vocabulary through this learned machinery, its gains reflect both the codes and the selector that consumes them; search and runtime monitoring, where codes are consumed directly, carry the cleanest vocabulary claims."

3. **Figure 4 is a mechanism trace, not a causal ablation (Fig. 4b caption):** "We read this figure as a within-run mechanism trace, not an independent causal ablation."

4. **OfficeQA transfer is not confirmatory (Section 4.3):** "Because this is a single-run transfer study without budget-matched accounting, we treat it as evidence that the integration operates in a new domain rather than as a confirmatory effectiveness comparison."

5. **Held-out selection check is a robustness check, not confirmatory (Section 4.4):** "We report this as a robustness check rather than a confirmatory result."

6. **Refinement–breakthrough timing is correlational, not causal (§5.3):** "Finally, the two taxonomy-refinement events (iterations 29 and 78) each precede one of the run's score jumps (iterations 69 and 89). This is not a causal ablation, but it is consistent with the vocabulary participating in the breakthroughs rather than labeling them after the fact."

7. **Gate certifies applicability, not correctness (§3.1):** "This gate certifies that the taxonomy is consistently applicable; it does not certify that its codes are correct. Correctness is assessed externally, against expert human annotations, in Section 5.1."

8. **Forgecode harness near ceiling limits informativeness (§4.4):** "On ForgeCode, both MAST and AdaMAST approach the oracle ceiling, so the comparison is less informative."

9. **MAST parity in some runtime settings is acknowledged, not hidden (§2, §4.3):** "Fixed catalogues remain strong baselines (MAST reaches parity with AdaMAST in some runtime settings; Section 4.3), which sharpens rather than undercuts the distinction."

10. **Cost is variable and distinct from per-consumer overhead (Appendix B.5):** Construction cost is "a one-time, variable-call cost per target system" not pooled across domains; per-consumer overhead differs (per-iteration, per-checkpoint, per-task) — numbers are tabulated separately, not collapsed to a single claim.

**My audit on missing limitation disclosures:** No discussion of (a) taxonomy staleness if refinement never triggers (no-maintenance drift), (b) judge-panel evaluator bias (LLM annotators judging LLM traces), beyond TRAIL human anchoring which partially addresses (b). These are not author-stated limitations; they are my open questions below.

---

## 6. Open Questions for Our Context (multi-agent failure taxonomy applied to production orchestration)

These are **my inferences** — labeled as such, grounded in the paper but not claimed by it. Context: ASES four-role topology (Orchestrator/Builder/Reviewer/Auditor), failure matrix, claim discipline (WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED), durable store, cheap staleness trigger, position-emitting agents.

### Q1 — Adaptive vs. fixed taxonomy for our failure matrix: where does MAST stop and domain-specific long tail begin?

**Author fact:** MAST (14 codes, 3 categories) is competitive — parity with AdaMAST in some runtime settings, only 2–3 pp gap in SWE-bench, and A-codes alone have mean Jaccard 0.47 across domains. The long tail is domain- and role-specific (C-codes entirely domain-specific, B-codes only in multi-agent).

**Inference for us:** Our current failure matrix is closer to MAST's shape (system-design / inter-agent / verification families; cross-cutting A-like codes). AdaMAST suggests we should keep A-codes as a stable backbone but induce B- and C-codes from our own 2026-08-23 lived traces (silent-hang after tool-burst, free-tier rate-limit kill, consent-gate fatal, pane-probe misread, status-RUNNING-but-dead) — those are precisely the role-/orchestration-/provider-specific failures no pre-committed checklist predicted. Open question: **What is the maintenance cadence for B/C codes?** The paper's refinement triggers on score stagnation (search) or trace-distribution shift — we need an analogue (e.g., trigger on staleness-detector firing with no position advance for 2× budget) to avoid vocabulary drift where C-codes go stale while A-backbone persists.

### Q2 — Can we adopt the gated-induction + online-refinement lifecycle without inheriting LLM-as-judge circularity?

**Author mechanism:** Gate uses four LLM annotators (cross-family) to certify applicability (κ ≥ 0.75 + coverage 0.70); correctness is anchored on TRAIL human experts (κ 0.682 vs 0.516 hand-crafted under matched panel). The gate's edit language (merge/add/relabel) is identical for pre-deployment and online refinement.

**Inference for us:** We have a genuine human auditor (Reviewer) and a claim-discipline harness that already requires WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED per producer claim. A production analogue would: (a) use LLM panels only for applicability (consistent coding of held-out orchestration traces), (b) reserve human reviewers/AUDITOR for correctness on a TRAIL-like probe set of our own failure categories, and (c) reuse the same merge/add/relabel operators for staleness-triggered refinement. Open question: **Do we need a human TRAIL equivalent for orchestration failures?** Without it, LLM-LLM agreement risks certifying an internally consistent but human-unfaithful vocabulary — the paper's key separation (applicability ≠ correctness) should become a methodological rule in our taxonomy.

### Q3 — Where should an induced vocabulary be consumed in our orchestration: search, runtime, or post-hoc selection?

**Author map:** Three consumers are formally separated, with different suitability:

- **Search (AdaEvolve):** Codes injected as mutation diagnoses (fired codes + quoted evidence + cross-problem patterns) — cleanest vocabulary signal, largest gains (+3.5–7.5 pp)
- **Runtime (checkpoints):** Codes in the acting agent's context as self-check guidance, no extra LLM calls, ≤3 repair attempts — gains +6.7 pp (Claude Code) / +20 pp (SWE-agent over Base, but +2–3 pp over MAST)
- **Selection (Verifier):** Codes as scoring criteria through a learned selector — gains large but least isolated

**Inference for us:** Mapping to ASES:

- **Search analogue:** Prompt/workflow/role evolution in the Execution Engine (e.g., mutating orchestrator guard allowlists, agent-orchestration playbook section citations) — biggest upside but requires an evolvable seed like AdaEvolve.
- **Runtime analogue:** Adding a taxonomy-anchored self-check at our cheap staleness trigger checkpoints (observable: `crosslink issue show` wall-clock vs position; introspective: agent breadcrumb self-report) — most immediately implementable, aligns with "no additional LLM calls beyond the agent's own" and with our `position-emitting agent` contract. Risk: forcing code-by-code auditing lowers accuracy (Appendix E: −0.13 to −0.24 by biasing toward failure) — taxonomy should be *present* in context, not executed as a checklist audit loop.
- **Selection analogue:** Choosing among redundant swarm outputs (e.g., picking the best adversarial review verdict) via a verifier that scores candidates per induced code + heuristics — useful but requires training a selector and is the least isolated claim; forward-selector CV must be reproduced.

**Open question:** Should runtime consumption be delivered as a drop-in skill (Claude Code model) vs. in-prompt instructions with a submit-gate (SWE-agent model)? Our orchestrator currently uses in-prompt guard policy + crosslink-guard plugin. The paper shows both work but with different enforcement strengths (hooks fire automatically vs. instructions can be ignored).

### Q4 — Compression as a durable-store contract: can a taxonomy substitute for the trace pool?

**Author fact:** On 223 SWE-bench traces: ~18× compression, 89% unique signatures, median 5 codes/trace, all 30 codes fire; functional substitution with Qwen consumers: taxonomy matches/exceeds verbatim trace pool at ~95× fewer tokens (1.2K vs 114K) and beats a growing pool that degrades (0.767 at N=40 < no-context 0.850).

**Inference for us:** Our durable store (Crosslink `issues.db` with comments + worktree artifacts) is the analogue of the trace pool. A taxonomy could compress its failure-relevant content for handoffs (session end notes, orchestrator dispatch context). But: the paper's substitution win is strongest when taxonomy is simply present — adding code-by-code auditing hurts. Design implication: store per-trace code signatures + shared taxonomy once, not a per-handoff audit trace. Open question: **What is our compression floor?** 18× is SWEBench-specific; orchestration traces (issue comments + crosslink-guard denials + pane captures) may compress differently; measurement with our own satisfied-harness benchmark (analogous to TRAIL) is needed before claiming.

### Q5 — What does AdaMAST imply about our claim-testing principles (Cheapest-Test-First, negative-space disclosure)?

**Author stance:** AdaMAST's strongest epistemic point is separating applicability (gate) from correctness (TRAIL), and explicitly labeling some results as "robustness check rather than confirmatory result" and "within-run mechanism trace, not causal ablation."

**Inference for us:** This aligns with our WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED discipline and the cheapest-test-first principle (gate is a cheap discriminating test before expensive search/runtime). A direct import: every taxonomy-conditioned claim should carry the same split — "κ = 0.682 vs 0.516 under matched panel (WHAT = TRAIL expert labels, HOW-CERTAIN = evidence-based under reported protocol, WHAT-NOT-TESTED = independent re-annotation, cross-provider replication)." For production, the cheapest discriminating test for a new induced C-code could be: does it fire disproportionately on failed orchestrations vs. passing ones (analogous to Figure 5's 3 vs 4 median) before promoting it to the live taxonomy.

---

## 7. Direct Quotes — Load-Bearing Passages (verbatim from local HTML read)

1. **Feedback interface thesis (Abstract):**
   > "An agent system's execution traces record how it fails, and procedures that improve such a system without changing model weights (trajectory selection, prompt and workflow optimization, runtime monitoring) read these traces for feedback. Yet raw traces are a poor medium for accumulating that feedback: long, instance-specific, and lacking a stable vocabulary for recurring failures."

2. **Durable-vs-diagnostic synthesis (Abstract & §1):**
   > "We argue that an agent system should instead maintain an explicit representation of how it fails, induced from its own behavior and reusable wherever failure feedback is needed."
   > "what can serve instead is an artifact durable like a score and diagnostic like a critique, a compact vocabulary of named failure modes, produced once from the system's own traces."

3. **Structural limit of fixed catalogues (Introduction):**
   > "But a catalogue fixed before the target system is observed faces a limit that is structural, not a consequence of quality: role-specific failures presuppose roles that exist only once an architecture is instantiated, and domain-specific failures presuppose task knowledge no general catalogue enumerates."

4. **Three fixed axes as comparable backbone (§1/Method):**
   > "it produces a compact set of named failure codes organized across three fixed axes: system-level, role-specific, and domain-specific (Figure 1). Only the axes are fixed, so that taxonomies stay comparable across systems and every code maps to an intervention point. The codes themselves (names, definitions, role labels, and evidence patterns) are induced from the traces: no code is hand-authored, no trace human-annotated."

5. **Auditability and lifecycle (§1):**
   > "A taxonomy is accepted only when independent annotators apply it consistently to held-out traces, so the artifact is auditable before anything consumes it (Section 3.1). Moreover, as the system evolves, online refinement merges, adds, or relabels codes, so the vocabulary tracks the current system, rather than a snapshot of its past (Section 3.3)."

6. **Amortization vs formatting (§1 + Contributions):**
   > "The claim is amortization, not prompt formatting (section I.2): each target system's taxonomy is induced and validated once, then consumed unchanged by every procedure that reads its traces."

7. **Gate thresholds (Fig. 2 caption):**
   > "inter-annotator agreement gates deployment: four independent LLM annotators label stratified held-out traces under a five-phase deliberation protocol, over up to five rounds of five traces each; the taxonomy is accepted once mean pairwise area-level agreement reaches κ ≥ 0.75 with a coverage floor of 0.70, and a failed round triggers merge/add/relabel edits and re-runs (Appendix B.2)."

8. **Gate does not certify correctness (§3.1):**
   > "This gate certifies that the taxonomy is consistently applicable; it does not certify that its codes are correct. Correctness is assessed externally, against expert human annotations, in Section 5.1."

9. **Matched comparison discipline (§4.1):**
   > "Our comparisons hold the surrounding procedure fixed and vary only the source of failure feedback. Search uses the same AdaEvolve backbone, seed architecture, and iteration number; within each runtime harness, variants use the same solver, instance set, and evaluation protocol; selection uses the same trajectory pools and verifier pipeline."

10. **Within-run vs causal (§4.2, Fig. 4 caption):**
    > "We read this figure as a within-run mechanism trace, not an independent causal ablation."

11. **Vocabulary-specific runtime gain (§4.3, Claude Code):**
    > "the induced 32-code taxonomy's role axis names single-agent phases (Edit/Plan/Verify) rather than multi-agent roles, and the induced vocabulary primarily reduces verification-phase failures, including B.8 Verify ignored import or syntax errors and B.6 Plan skips verification loop, while MAST's reductions concentrate on broader patch-footprint errors (B.3 Edit overbroad patch footprint)."

12. **Runtime ladder isolation (§4.3, SWE-agent):**
    > "Because the three reflection arms share the identical scaffold and differ only in what anchors the check, the ordering isolates content: adding prompted reflection at all recovers +10% over Base, anchoring it to a categorical vocabulary adds a further +8% (MAST over Reflexion), and the induced, harness-specific vocabulary adds another +2%."

13. **Selection confound honest mark (§3.5/§4.4):**
    > "Because selection routes the vocabulary through this learned machinery, its gains reflect both the codes and the selector that consumes them; search and runtime monitoring, where codes are consumed directly, carry the cleanest vocabulary claims."

14. **Single-run qualification (§4.3, OfficeQA):**
    > "Because this is a single-run transfer study without budget-matched accounting, we treat it as evidence that the integration operates in a new domain rather than as a confirmatory effectiveness comparison."

15. **TRAIL separation of panel and vocabulary (§5.1):**
    > "Substituting a same-model panel (four GPT-5.4 annotators) for the cross-family panel lowers agreement from κ = 0.682 to 0.625 at the 1-of-4 reporting threshold under an otherwise identical protocol (Appendix F), indicating that at this threshold the alignment is carried by the induced codes rather than by a labeling regime shared within one model family."

16. **Compression functional substitution (§5.4):**
    > "A downstream procedure can therefore consume the taxonomy in place of the trace pool at one to two orders of magnitude less context."
    > "Consumption is most effective when the taxonomy is simply present in context: a paired ablation that forces the consumer to audit the current run code-by-code before deciding lowers accuracy (−0.13 to −0.24, p ≤ .006) by biasing it toward predicting failure even when the run succeeds (Appendix E)."

17. **Conclusion — infrastructure framing (§6):**
    > "AdaMAST treats an agent system's failure vocabulary as infrastructure: induced once from the system's own traces, validated once, and then consumed by every procedure that would otherwise re-derive its diagnosis in disposable free text."

---

## 8. Inference Audit, Certainty, and WHAT-NOT-TESTED

**This file's epistemic status:**

- **Author claims vs. my inference:** §2–5 paraphrase paper claims with inline `Author claim` labels and verbatim quotes where load-bearing. §6 is my inference (labeled as such) applying the paper's findings to ASES's four-role topology / failure matrix / orchestration context. No sibling-source claim is imported.
- **Provenance:** All paper-content claims trace to local reads of `/tmp/opencode/src4/abs.html` and `/tmp/opencode/src4/full.html` (arXiv HTML v2) — no PDF, no repo clone, no WebFetch. ArXiv HTML is a LaTeXML conversion; figure images and some LaTeX fragments are rendering artifacts, not inspected as images/PDF.
- **Branch-specific artifact:** This file lives on `feature/pp3g-K7Ak-atomized-source-worker-4-of-5-v2-429-cli-fetch-method`; no cross-worktree filesystem reads were performed (per sandbox).
- **Model discipline:** Not applicable to this research-only task, but paper-referenced model IDs (GPT-5.4-mini, GPT-5.4, GPT-5, Claude Haiku 4.5, Claude Opus 4.7, Gemini-2.5-Pro) are reproduced verbatim as paper-reported — not verified against live `opencode models` catalog.

**WHAT-NOT-TESTED (explicit negative-space — cheapest-test-first for a consumer of this note):**

- Repo contents of `https://github.com/multi-agent-systems-failure-taxonomy/AdaMAST` not fetched or inspected (no clone, no file tree, no commit hash verified). Paper's `Code:` link is the only repo evidence in this file.
- Taxonomy files (A.1–A.7 examples, 13–36 codes each) not independently compared to an induced run; taxonomy YAML/JSON not inspected.
- Paper's appendices I (expanded design ablations), G (OlympiadBreakthrough mechanism detail), H (runtime monitoring detail), D (selection ablations), E/F (compression/TRAIL protocols), B.5 (cost accounting) are summarized from TOC/abstracted body read; not line-audited for image/table data beyond what HTML text contains.
- No re-execution of AdaEvolve, SWE-agent, Claude Code, or Terminal-Bench harnesses; no verifier or judge re-run.
- No independent recomputation of κ, Jaccard, compression ratio, or p-values; numbers are paper-reported.
- PDF-specific typesetting (e.g., footnotes about multi-agent lineage vs single-agent scope, Figure 1/2 rendering) not cross-checked against PDF.
- Cross-domain transfer (OfficeQA) not treated as confirmatory effectiveness evidence per authors' own qualification — any reuse must preserve that qualifier.

**Honesty rule compliance:** Where the paper explicitly hedges (within-run trace not causal, robustness check not confirmatory, gate ≠ correctness, selection confounded with selector, axes not proven optimal), this note preserves the hedge verbatim and does not upgrade it to a stronger claim. Where I infer for our context (§6 Q1–Q5), inference is labeled and kept separate from author claims.

---

*Source fetched via mandated CLI path; file written to `docs/research/sections/source-4-paper-16387.md` in worktree `feature/pp3g-K7Ak-atomized-source-worker-4-of-5-v2-429-cli-fetch-method`. Committed referencing [#429]. Single-source file per atomized assignment — no synthesis across other #429 sources.*
