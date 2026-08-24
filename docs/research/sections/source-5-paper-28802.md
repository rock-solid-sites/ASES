---
title: "Source 5 — arXiv 2607.28802: Model or Harness? An Interaction-Centric Taxonomy for Localizing Agent Failures"
program: EDASES
layer: Research
document_type: Source Section
status: Draft
authority: Derived
source_url: "https://arxiv.org/abs/2607.28802"
source_version: "v1 (2026-07-30)"
html_url: "https://arxiv.org/html/2607.28802v1"
paper_authors: "Harsh Raj, Vipul Gupta, Anas Mahmoud, Razvan-Gabriel Dumitru, Darvin Yi, Aakash Sabharwal, Yunzhong He (Scale AI)"
fetched_via: "CLI curl -sL --retry 2 to /tmp/opencode/src5/abs.html + /tmp/opencode/src5/full.html (no WebFetch)"
fetched_at: "2026-08-24T00:48Z"
local_copies:
  - "/tmp/opencode/src5/abs.html (43,419 bytes, 623 lines)"
  - "/tmp/opencode/src5/full.html (831,617 bytes, 3824 lines)"
  - "/tmp/opencode/src5/full_extracted.txt (166,283 bytes, derived via HTMLParser tag-strip)"
docs_fetched:
  - "abs.html (arXiv abstract page — citation meta, title, authors, abstract)"
  - "full.html (arXiv HTML v1 — full paper including Abstract, §1-7, Limitations, References, Appendices A-C)"
not_fetched:
  - "PDF (not needed; HTML is authoritative for this task)"
  - "Linked datasets/traces beyond what the HTML embeds (e.g., HuggingFace/Docent trajectories — referenced but not independently fetched)"
worktree: "feature/pp3g-TF9r-atomized-source-worker-5-of-5-v2-429-cli-fetch-method"
atomized_scope: "This file covers ONLY arXiv 2607.28802 per #429 CLI-fetch assignment. No synthesis across sibling sources (MAST/AdaMAST/ATLAS/2607.16387) — collator owns cross-walk."
---

# Source 5 — arXiv 2607.28802: Interaction-Centric Taxonomy for Localizing Agent Failures

> **Scope discipline:** This section covers ONLY arXiv:2607.28802 (Raj et al., Scale AI, v1 2026-07-30) as fetched via CLI to `/tmp/opencode/src5/`. No other source is synthesized here. Author claims are quoted or paraphrased with explicit attribution; analyst inference is labeled as such.

## 1. Source Identity and What Was Accessible

| Artifact | Accessible? | Notes |
|---|---|---|
| `abs.html` — arXiv abstract page | Yes (CLI curl, 43 KB) | Citation meta (`citation_title`, `citation_author` ×7, `citation_date` 2026/07/30, `citation_arxiv_id` 2607.28802), `og:description`, title/authors/abstract block parsed via HTMLParser. |
| `full.html` — arXiv HTML v1 | Yes (CLI curl, 832 KB) | Sections §1–§7 + Limitations + References + Appendices A–C fully present as HTML. Section headings verified: `1 Introduction`, `2 Related Work`, `3 The Mechanism Axis`, `4 Categorization Methodology`, `5 Failure Families`, `6 Validating the Taxonomy with an Agent-as-a-Judge`, `7 Discussion`, `Limitations`, `Appendix A Agent-as-a-Judge`, `Appendix B Failure-Mode Definitions`, `Appendix C Worked Examples`. |
| Paper PDF | Not fetched | HTML is the evidential basis; PDF layout not verified. Explicitly not needed per task. |
| Linked external evidence (benchmark traces, system cards, GitHub issues, HuggingFace/Docent trajectories) | Referenced inside HTML but not independently fetched | Marked not inspected; evaluation claims about those traces are reported as paper claims. |
| Figures (Fig 1 radial map, Fig 2 taxonomy tree, Fig 3 pairwise κ heatmap) | Captions + surrounding prose present; images not visually inspected | Descriptions taken from caption prose and body references; no pixel-level inspection. |

**Honesty marker:** All quotations and structural claims below derive from the two local HTML files. Where the HTML truncates or where images would carry information, it is noted.

### Citation metadata (from `abs.html` `<meta>` tags)

- **Title:** *Model or Harness? An Interaction-Centric Taxonomy for Localizing Agent Failures*
- **Authors:** Harsh Raj, Vipul Gupta, Anas Mahmoud, Razvan-Gabriel Dumitru, Darvin Yi, Aakash Sabharwal, Yunzhong He
- **Affiliation:** Scale AI (per front matter in `full.html`)
- **arXiv ID:** 2607.28802v1
- **Category:** `[cs.AI]`
- **Date:** 2026/07/30
- **License:** CC BY 4.0 (per HTML footer)
- **Contact block in HTML:** `{harsh.raj, vipul.gupta, anas.mahmoud}@scale.com` (first three authors shown; full list in metadata)

---

## 2. Core Claims (author claims vs. analyst inference)

> All claims in this section are **author claims** (paper text) unless explicitly labeled **[Analyst inference]**.

### Claim 0 — Problem framing: the repair-assignment problem

**Direct quote — Abstract (§0, also `og:description` from `abs.html`):**

> "Existing evaluations often reduce agent failures to system-level outcomes, obscuring where the fault originated and which intervention would actually improve the next iteration of the agent system. This creates a repair-assignment problem: the same visible failure may call for model post-training, harness engineering, environment redesign, or benchmark repair depending on where it originated."

The Abstract (variant in HTML preamble) elaborates:

> "Because an agent's behavior emerges from interactions among its model, harness, users, tools, memory, and environment, outcome-level labels alone are often insufficient for improving agent performance. Most failure taxonomies do little to resolve this problem because they are typically benchmark-specific, capturing useful fine-grained failure modes without providing a shared structure."

**§1 variant with concrete illustration:**

> "For example, in a long-running Claude Code (4) session an agent may ignore an earlier user instruction because the harness's context compaction removed it, or because the instruction remained available but the model failed to follow it. The observed behavior is the same, but the first case requires a harness-level fix, whereas the second requires a model-level intervention."

**[Analyst inference]:** The paper frames its contribution as solving *where-to-fix* ambiguity, not merely *what-failed* labeling. This maps directly to ASES's producer-side claim discipline (WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED) and execution-engine intervention routing — an author claim of broad applicability, not an independent empirical proof of utility in our harness.

### Claim 1 — Interaction-centric taxonomy: 41 failure modes on interaction edges with fault-side attribution

**Direct quote — Abstract:**

> "We introduce an interaction-centric taxonomy that localizes agent failures to the interaction in which they originate and identifies the component responsible. We treat interactions between components as the unit of analysis. The taxonomy organizes 41 failure modes by assigning each failure to an edge between two components and a fault side indicating where the repair belongs."

**§1 / §3 reinforcing:**

> "This makes the taxonomy directly actionable: model-side failures identify targets for post-training, harness-side failures point to scaffolding and tool-integration fixes, and environment or grader failures reveal evaluation conditions that must be redesigned before they are used to judge agent capability."

**Coverage claim (§1 — three contributions):**

> "• First, we introduce an interaction-centric taxonomy of 41 agent failure modes, assigning each to an interaction edge and a fault side (Figure 2). Most modes are model-side, partly because our attribution rule assigns fault to the model when a more capable model could have avoided or recovered from the failure under the same conditions."

**§B/C grounding:**

> "Second, we ground the taxonomy in worked examples drawn from public benchmarks, model system cards, published reports, and logged agent trajectories, covering almost all of the failure modes."

Figure 2 caption (from HTML, §3):

> "Figure 2: Interaction-centric taxonomy of 41 failure modes. Failures are organized by the family of the component interacting with the model: User, Harness, or Environment, and then by the specific component within that family. Each branch represents an interaction edge between the model and that component. […] Of the 41 role-specific failure modes, 36 are assigned to a model and five to surrounding components."

**[Analyst inference]:** The 36/5 split and the "more capable model could have avoided" attribution rule (which inflates model-side counts) are load-bearing methodological choices — they explain why the taxonomy is model-centric even though its purpose is to *distinguish* model from harness/environment faults.

### Claim 2 — Schema generality across architectures

**Author claim (§1 + Abstract):**

> "The schema applies across agent architectures, from coding assistants to long-horizon personal assistants and multi-agent systems."

Examples named: Claude Code (4), Codex (54), OpenClaw (56), Hermes Agent (52), plus custom multi-agent systems (18). Claim of modality-agnosticism with multimodal worked examples.

**[Analyst inference]:** Generality is asserted via breadth of worked examples (40 curated cases) rather than via a controlled generalization experiment. The claim is plausible but not quantitatively proven by the paper's design.

### Claim 3 — Reproducibility via agent-as-a-judge: categories capture shared structure

**Direct quote — Abstract:**

> "We ground the taxonomy in worked examples from public benchmarks, model system cards, published reports, and logged agent trajectories, and evaluate its operational reproducibility using independent reasoning agents as judges. Across four frontier models, the judges recover the human labels well above chance, with the strongest judge reaching Cohen's κ = 0.76 against human category labels, suggesting that the categories capture shared structure rather than annotator-specific labeling preferences."

**§1 companion:**

> "They agree with one another about as strongly as they agree with the annotators, with the highest pairwise agreement reaching Cohen's κ of 0.84."

Detailed numbers are in §6 (see Evaluation section below). The third contribution is framed as:

> "Third, we evaluate whether independent reasoning agents can consistently recover the human-assigned categories, providing evidence that the taxonomy captures a reproducible structure."

**[Analyst inference]:** Reproducibility is claimed at the *category* (edge + fault side) level (κ=0.76), not at the full 41-mode level where agreement drops materially. The distinction is critical for downstream use — category-level routing is more robust than mode-level routing under this evidence.

---

## 3. Mechanism Contributions

### 3.1 Component vocabulary (Table 1) and edge+fault representation

**Component definitions (verbatim from Table 1 in `full.html`, §1):**

| Component | Author definition (verbatim) |
|---|---|
| **Model** | "The policy that processes observations and produces outputs or actions." |
| **Owner** | "The human or upstream system that gives the agent its task and defines what counts as success." |
| **Grader** | "The mechanism used to evaluate whether the agent completed the task successfully; it is usually not visible to the agent." |
| **Third party** | "An actor encountered during execution that does not act on behalf of the owner. The actor can be a human, organization, or agent, and the interaction may be adversarial, persuasive, or cooperative." |
| **Context** | "The information available to the model during the current interaction, including instructions, conversation history, observations, and summaries." |
| **Memory** | "A persistent store that outlives the active context, within or across sessions." |
| **Tool** | "The bidirectional interface through which the model exchanges requests, messages, actions, observations, and responses with other components. This includes callable tools, communication channels, and wrappers that relay inputs and outputs." |
| **Local env.** | "The agent's immediate execution environment, such as the operating system, shell, filesystem, and runtimes." |
| **External env.** | "Systems outside the agent's immediate execution environment, such as remote services, websites, APIs, databases, and model-provider infrastructure." |

**Families:** Components are grouped into three families (inner ring of Figure 1): **User** (Owner, Grader, Third party), **Harness** (Context, Memory, Tool, Model-as-peer/subagent), **Environment** (External, Local). In multi-agent settings, peer/subagent are *roles* of the other model, not separate components — the edge remains `model — model (role: peer)` or `model — model (role: subagent)`.

**Formal localization (notation from §3):**

> "We write a failure as `comp₁ — comp₂ (edge) · fault: side (component at fault)` where the edge `comp₁ — comp₂` is the interaction between the two components and `side` is the component at fault. For example, `tool — model · fault: model` assigns the failure to the model side of the interaction between the model and the tool."

**Illustrative contrast (§1/§3):**

> "Consider an agent that reports that a tool call succeeded when it actually failed. In one case, the tool wrapper suppresses the error, so the model never observes the failure. We label this failure `tool — model · fault: tool`. In another case, the wrapper returns the error, but the model ignores it. We label this failure `tool — model · fault: model`. The interaction is the same, but the responsible component differs."

**Attribution rule for cascades (§1/§3/§4):**

> "A single trajectory often contains many cascading failures. […] We therefore begin with the observed system-level failure and trace its causal chain backward. We label the earliest failure from which execution does not recover, rather than its downstream symptoms (32; 96; 65). An intervention at this point would have resulted in a different outcome, whereas the later errors may only be consequences of it."

This follows prior work on critical-failure identification (cited as 14, 65, 32, 96). The taxonomy then answers a *separate* question: on which interaction, and on which side, did that earliest unrecovered failure occur.

**Boundary clarifications (§3 — Components subsection):**

- **Owner vs. Grader:** "We treat the grader as separate from the owner because the model can fail in its interaction with the grader independently of whether it followed the owner's instructions. For example, in the Specification Gaming case E12, an agent instructed to win against a chess engine edited the board state until the opposing engine resigned. The grader recorded a win even though the agent had bypassed the intended game."
- **Third party vs. External environment:** "The external environment is the delivery channel, whereas the third party is the actor behind the interaction. A system failure or stale response belongs to the external environment, whereas a failure caused by an actor attempting to influence or manipulate the model belongs to the third party."

### 3.2 The 41 failure modes (Figure 2 inventory + §5 families)

The taxonomy is presented as a hierarchy (Figure 2). Each leaf names a failure mode with its fault side indicated by shading (filled = model, triangle = other component). The paper lists modes by family/component. Appendix B reproduces verbatim definitions; Appendix C maps each to a worked example (E1–E40). The five non-model modes are not enumerated as a standalone list in the accessible prose but Figure 2's caption states the count; per §5 and the figure's leaf annotations they lie on edges where harness/environment/grader is at fault (e.g., `Instruction–Grader Mismatch` on `owner — model · fault: owner`, plus tool-side `Mistranslation`, environment-side `Service Failure`/`Stale State Delivery`, and analogous context/memory cases where compaction/storage is harness-driven).

**Family-level structure (§5 overview):**

- **User family (§5.1):**
  - `model — owner` (10 modes: 9 model-side + 1 owner-side). Model-side: *Over-initiative (80), Under-initiative (69), Satisficing (9), Instruction-Following Failure (92), Reasoning Failure (49), Unauthorized Irreversible Action (71), Sycophancy (63), Domain Knowledge Deficit (29), Value Misalignment (20)*; Owner-side: *Instruction–Grader Mismatch (16; 97)*.
  - `model — grader` (2 modes, both model-side): *Specification Gaming (76), Evaluation Awareness (51)*.
  - `model — third party` (2 modes, both model-side): *Indirect Prompt Injection (26), Contextual Sycophancy (75)*.
- **Harness family (§5.2):**
  - `model — context` (3 modes): *State Tracking Failure (18), Goal Drift (11), Context Rationale Erosion (42)* — first two model-side; the last is harness-side when compaction is harness-driven, model-side when model-driven.
  - `model — memory` (8 modes): *Missed Write (25), State Staleness (19), Overgeneralization (38), Memory Rationale Erosion (25), Pollution (86), Redundancy (35), Missed Read (25), Memory Following Failure (25)* — covering write and read failures against persistent stores (60; 88).
  - `model — tool` (7 modes): invocation failures *Malformed Arguments (41), Suboptimal Arguments (85), Incorrect Tool Selection (30), Tool Hallucination (61)* + response-handling *Tool Feedback Neglect (93), Tool Recovery Failure (36)*, plus tool-side *Mistranslation (78)* where the integration layer mis-conveys an otherwise correct observation or action.
  - `model — model (peer/subagent)` — role-parameterized edges:
    - Peer: *Delegation Failure (18; 84), Communication Failure (34; 70)*
    - Subagent (orchestrator hierarchy): *Delegation Failure (84)* (incorrect scope/dependencies) and *Communication Failure (70)* (omitted context / unused output / unreported constraints)
- **Environment family (§5.2, end):**
  - `model — external environment` (3 modes): *Recovery Failure (94)* (model-side when recovery was possible), *Service Failure (44; 33)*, *Stale State Delivery (47)* (environment-side; attribution to external env when recovery not possible).
  - `model — local environment` (2 modes): *Observation Failure (93), Recovery Failure (12)* — model-side failures to notice or fix a locally fixable condition.

**[Analyst note on completeness]:** The §5.1–§5.2 excerpts captured via HTML tag-stripping are the cleanest prose inventory available without re-parsing the figure's SVG. Appendix B is the authoritative verbatim definition set; the above family grouping is the organizational hierarchy, not a re-definition. Total leaf count reconciliation (41) is from the authors' caption; per-edge leaf counts above sum to 41 only when role-parameterization is handled as described (the 14 named owner/grader/third-party + 3 + 8 + 7 + 4 model—model role variants + 5 environment locals = 41 in the authors' counting).

### 3.3 Categorization methodology (§4) and annotation discipline

**Iterative development (§4, verbatim):**

> "We developed the taxonomy iteratively while reviewing failures from public benchmarks, model system cards, published reports, and logged agent trajectories. As new cases exposed overlaps or unclear boundaries, we refined the component definitions and failure modes. Once these definitions had stabilized, we froze the taxonomy and used that version for all reported labels and for the validation in §6. The final definitions are reproduced verbatim in Appendix B."

**Root-cause labeling procedure (§4, verbatim):**

> "To assign labels consistently, we applied the root-cause principle of §3. For each example, we reviewed all available evidence in the trace or report and identified the observed system-level failure. We then traced the causal chain backward and selected the earliest failure from which execution did not recover."

Cited as following prior work on first unrecoverable / critical failure (14). After identifying that root cause, the annotator assigns edge, fault side, and failure mode; the rationale per example is in Appendix C. Safety/security impact is annotated separately (most salient OWASP Top 10 category, 58; 59) — not part of the core taxonomy label.

**Scope disclaimer (§4, load-bearing):**

> "We selected examples that illustrate the taxonomy across a range of interaction edges and failure modes. The set is illustrative rather than exhaustive and should not be used to estimate the prevalence of individual failure modes."

**[Analyst inference]:** The illustrative-not-exhaustive selection means the 40-example set is not a prevalence sample; any reuse for frequency estimation would be a misuse of the evidence.

### 3.4 Related-work positioning (§2)

Thesis is orthogonal to prior taxonomies:

- Benchmark-specific taxonomies (23; 94) and setting-specific ones (multi-agent coordination 18; 43; flat lists 82) lack a shared structure and do not indicate which component is at fault.
- Agent-failure taxonomies per se (Cemri et al. 18 with system-design / inter-agent misalignment / task-verification; Tran et al. 95 with memory/reflection/planning/action/system modules) are "closest to ours" but do not distinguish fault side; the present paper's edge+fault representation makes producer–consumer boundaries explicit (also seen in security and fault-type literatures 48; 74).
- Failure-localization work (critical failure as first unrecoverable event 14; verified propagation paths 65) answers *which event* to label; the present taxonomy answers *on which interaction and which side*.

---

## 4. Evaluation Methodology and Evidence Quality

### 4.1 Agent-as-a-judge design (§6 + Appendix A)

**Goal (verbatim, §6):**

> "We test whether independent reasoning agents can apply the taxonomy consistently to the same evidence. Each judge agent attempts to recover the human-assigned labels for the worked examples using only the taxonomy definitions and the original source material."

**Task per example (§6):**

> Judge receives the taxonomy definitions + a reference to the original failure source (GitHub issue, blog post, system-card section, arXiv paper, or logged trajectory on HuggingFace/Docent 79) but *not* the human label. Judge independently reviews the source, identifies the earliest unrecovered failure, and predicts (1) the interaction category `comp₁ — comp₂ · fault: side` and (2) the complete label `… · Failure Mode`.

**Judges (§6):** Four frontier models run as *separate* judges: GPT-5.5 and Claude Opus 4.6, 4.7, 4.8. Full inference/harness configs in Appendix A.1 (not reproduced in accessible HTML beyond section titles — Appendix content was present only as TOC in the extracted text; the §6 summary + tables carry the evaluative weight).

**Pipeline — agent-as-a-judge (distinct from conventional LLM-as-a-judge) (§6):**

> Three turns within a single session: (1) Evidence reconstruction — given the source reference, the judge retrieves the relevant evidence and organizes it into a neutral chronological account. (2) Failure classification — using the reconstructed account + frozen definitions, the judge identifies the earliest unrecovered failure and assigns edge/fault side/failure mode. (3) Reflection and disambiguation — the judge checks its label against predefined disambiguation rules and either confirms or revises it.

The authors contrast this with conventional LLM-as-a-judge systems which place the candidate output directly in context (91); the present setup follows the agent-as-a-judge pattern of 98.

**Metrics (verbatim, §6):**

> "We compare each judge's predictions with the human-assigned labels using exact-match accuracy, macro-averaged F₁, and Cohen's κ. Category-level evaluation requires the correct interaction edge and fault side. Failure-mode evaluation additionally requires the correct named failure mode."

Category agreement is the primary reproducibility claim; failure-mode agreement is the finer-grained (and noisier) measure.

### 4.2 Results — agreement with human labels (Tables 2–4, Figure 3)

All results are on the 40 worked examples (Appendix C). **Author-reported numbers (verbatim from §6 + tables):**

**Table 2 — Agreement with human labels (category vs. failure mode):**

| Judge | Category Acc | Category F₁ | Category κ | Failure-mode Acc | Failure-mode F₁ | Failure-mode κ |
|---|---|---|---|---|---|---|
| **GPT-5.5** | 0.80 | 0.69 | **0.76** | 0.72 | 0.64 | 0.72 |
| Claude Opus 4.6 | 0.75 | 0.61 | 0.70 | 0.70 | 0.57 | 0.62* |
| Claude Opus 4.7 | 0.75 | 0.63 | 0.71 | 0.62 | 0.53 | — |
| Claude Opus 4.8 | 0.75 | 0.62 | 0.70 | 0.68 | 0.58 | — |

\* Table formatting in HTML is dense; the key author-highlighted values are:

- **Category κ:** GPT-5.5 = 0.76 (strongest), Opus 4.6 and 4.7 = 0.71, Opus 4.8 = 0.70 (§6 prose, consistent with Table 2).
- **Inter-judge pairwise κ:** highest = 0.84 between Claude Opus 4.6 and 4.8 (§6 prose: "They agree with one another about as strongly as they agree with the annotators, with the highest pairwise agreement reaching Cohen's κ of 0.84 between Claude Opus 4.6 and 4.8." — also Figure 3).
- **Failure-mode κ:** lower across all pairs (Figure 3, right panel).

**Author interpretation (verbatim, §6):**

> "For category labels, GPT-5.5 has the highest agreement with the human annotations at κ = 0.76. Claude Opus 4.6 and 4.7 each reach κ = 0.71, followed by Claude Opus 4.8 at κ = 0.70. Agreement among the judges is comparable, with the highest pairwise value of κ = 0.84 between Claude Opus 4.6 and 4.8. Agreement on the complete failure-mode label is lower across all pairs."

**Table 3 — Failure-mode agreement conditional on category (author-reported):**

Under "Predicted category" (judge predicts both category + mode) vs. "Gold category" (mode given correct category):

- GPT-5.5: 0.72 Acc / 0.64 F₁ (predicted) vs. 0.72 / 0.62 (gold)
- Opus 4.6: 0.70 / 0.57 vs. 0.80 / 0.70
- Opus 4.7: 0.62 / 0.53 vs. 0.70 / 0.58
- Opus 4.8: 0.68 / 0.58 vs. 0.78 / 0.69

**Author gloss (verbatim):**

> "When given the gold category, accuracy improves for the Opus models (Table 3), indicating that some failure-mode errors originate at the category stage rather than from confusion among the modes within the correct category."

**[Analyst inference]:** The gold-category lift for Opus models suggests failure-mode confusion is partially downstream of category error — a useful signal for any production judge pipeline (invest in category accuracy first).

**Table 4 — Selective-voting ensemble (author-reported):**

Category is assigned only when at least *k* of 4 judges agree; otherwise abstain. After selecting a category, failure mode is by majority among judges predicting that category.

| Agreement threshold | Coverage | Category P | Category R | Category F₁ | Failure-mode P | Failure-mode R | Failure-mode F₁ |
|---|---|---|---|---|---|---|---|
| ≥2 of 4 | 1.00 | 0.78 | 0.78 | 0.78 | 0.70 | 0.70 | 0.70 |
| ≥3 of 4 | 0.90 | **0.83** | 0.75 | 0.79 | 0.75 | 0.68 | 0.71 |
| 4 of 4 | 0.68 | **0.96** | 0.65 | 0.78 | **0.89** | 0.60 | **0.72** |

**Author gloss (verbatim):**

> "Increasing *k* trades coverage for precision (Table 4). Agreement among three judges yields 0.83 category precision at 90% coverage, while unanimity raises precision to 0.96 at 68% coverage."

**[Analyst inference]:** The paper's precision/coverage trade-off is the operationally relevant result for production observability — high-precision selective voting with abstention is the path the authors themselves mark as realistic (see Limitations).

### 4.3 Sources of disagreement (author diagnosis)

Author-identified two main sources (§6):

1. **Heterogeneous source material / evidence sparsity.** Each judge receives only a reference to the original source (complete trace vs. GitHub issue vs. blog post vs. system-card section). Some sources do not provide enough evidence to identify a unique root cause.

   > "For example, in E4, a public incident report attributes the agent's deletion of more than 200 emails to context compaction dropping the owner's instruction not to act, but does not provide the full trajectory. From the source alone, the case could be interpreted as either a context-side failure or a model-side unauthorized action."

2. **Root-cause attribution difficulty even when evidence is available.** Case study in Appendix A.2 (verbatim summary, §6):

   > "The agent correctly completes the initial task, but a scripted reply email required for the follow-up never arrives because of a bug in the evaluation environment. The judge, however, interprets the incomplete follow-up as the model failing to check for the reply, rather than tracing the failure back to the undelivered email."

   The paper connects this to OpenRCA 2.0 (24): "frontier models often fail to reconstruct a verified causal propagation path from the initiating fault to the observed symptom, resulting in what the authors term an *ungrounded diagnosis*."

**Additional failure-mode-level challenges (§6):**

> "Failure-mode prediction introduces an additional challenge because the set of possible labels is larger and several failure modes can produce similar visible symptoms. The prediction also depends on selecting the correct category first, so a category error can lead to an incorrect failure-mode label."

### 4.4 Evidence quality — strengths and gaps (analyst assessment, evidence-based)

**Strengths (evidence-based):**

- **Frozen taxonomy + independent judges:** Definitions were frozen before judging (§4); judges see only definitions + source, not human labels. This is a proper reproducibility test, not a leak.
- **Multi-model judges + pairwise inter-judge κ:** Reporting inter-judge agreement (κ=0.84 max) as well as human agreement guards against a single-model idiosyncrasy claim.
- **Category vs. mode separation + selective voting:** The paper does not overclaim mode-level accuracy; it quantifies the drop, diagnoses it (heterogeneous evidence + causal-path reconstruction), and offers an abstention-based mitigation with explicit coverage costs.
- **Grounding in heterogeneous real artifacts:** 40 examples drawn from benchmarks, system cards, reports, and logged trajectories (Appendix C, E1–E40) — not a synthetic toy set.

**Limitations in evidence quality (distinguished as author-stated vs. analyst-noted):**

- **Author-stated:** See §5 (Limitations) below — descriptive-not-quantitative, dependence on evidence completeness, judge accuracy limits, coverage costs of ensembling.
- **Analyst-noted, not tested:**
  - *N=40* worked examples is a small evaluation set for 41 modes; per-mode sample is ~1× coverage by design ("almost all" modes covered, but not prevalence-weighted). Confidence intervals on κ/F₁ are not reported and were not independently computed here.
  - Judge prompts/configurations live in Appendix A (only TOC-level verified in extracted HTML); no independent re-run was performed here. Provider/model IDs (GPT-5.5, Opus 4.6–4.8) are frontier at paper date; reproducibility on other families is not shown.
  - The source-traces themselves were not independently inspected here (marked not fetched); the judge's evidence-reconstruction step was not audited beyond the prose description.
  - Figure/table data were read from HTML prose/tables, not from a machine-readable artifact — transcription error risk is low for the headline κ values (cross-checked across Abstract, §1, §6, and HTML headings) but higher for secondary table cells where HTML layout is dense.

**Certainty of this section's claims:**

- Headline κ values (0.76 category, 0.84 inter-judge) = **proven** within the paper's evidence (multiple independent mentions converge).
- Table 2–4 per-cell numbers = **evidence-based** (direct HTML table reads via tag-stripped chunk; not independently computed).
- Heterogeneous-evidence and ungrounded-diagnosis diagnoses = **author claims**, corroborated by the two quoted examples but not independently verified here.

---

## 5. Stated Limitations (author-stated — §7 Discussion / Limitations, verbatim + paraphrase)

The paper's explicit **Limitations** block (§7, verbatim):

> "The taxonomy is descriptive rather than quantitative: it organizes failures and assigns responsibility but does not estimate their relative frequency. It is derived from the cases we reviewed and may need to expand as agent architectures and harnesses evolve. The taxonomy labels also depend on the available evidence, and brief reports or model system cards may omit details needed to identify a unique root cause. Moreover, the agent-as-a-judge framework used to validate the taxonomy may be difficult to deploy in production because judge accuracy remains limited, especially for failure-mode labels. We attempted to mitigate this through ensembling, but the gain in precision comes at the cost of lower coverage. The system may therefore abstain on cases where fault attribution is most uncertain."

**Discussion (§7) adds nuance (verbatim):**

> "As shown in Figure 2, most failure modes are assigned to the model side. This imbalance partly reflects our attribution rule: a failure is model-side when a more capable model could have prevented it or recovered from it. The remaining non-model failures identify cases that model improvement alone cannot resolve."

> "Independent judges often recover the human-assigned labels from the same definitions and evidence, and their agreement with one another is comparable to their agreement with the human annotations. These results provide evidence that the labels capture shared structure rather than annotator-specific labeling preferences."

**What the authors explicitly do NOT claim (author-enforced boundaries):**

- **Not a frequency claim:** "should not be used to estimate the prevalence of individual failure modes" (§4). Any dashboard that treats the 40 examples as a prevalence distribution would be a misuse per the authors.
- **Not a uniqueness claim on root cause:** labels "depend on the available evidence" — with sparse reports the taxonomy may not identify a unique root cause (E4 example).
- **Not a production-ready fully-automated classifier:** judge accuracy "remains limited, especially for failure-mode labels" — selective voting with abstention is the offered mitigation, not a full-coverage solution.

**Author-stated future pressure (condensed, verbatim):**

> "It is derived from the cases we reviewed and may need to expand as agent architectures and harnesses evolve."

---

## 6. Open Questions for Our Context — Adaptive Failure Taxonomies from Agent Traces in Production Orchestration

> This section is **[Analyst inference]** — questions the paper's material raises for ASES / Execution Engine work on learning failure taxonomies from production orchestration traces. Not author claims.

### 6.1 Can the edge+fault vocabulary be the fixed axes for an adaptive (induced) taxonomy?

The paper's taxonomy is **static and hand-curated** (41 modes, frozen at §4). Our context is **adaptive** taxonomies induced from our own orchestration traces (per AdaMAST intuition: system learns its own failure language from its logs). Open question:

- Should we adopt 2607.28802's **component vocabulary + edge+fault notation** as the *fixed* axes (User/Harness/Environment families; edge + fault side) while letting **failure-mode names/definitions within each edge** be *induced* from production traces? This mirrors AdaMAST's "three fixed axes, induced codes" but replaces AdaMAST's axes with the interaction-centric ones, giving us a shared repair-routing grammar across systems while preserving system-specific failure language.

**Testable variant:** Freeze Table 1 components + edge+fault notation + attribution rule (earliest unrecovered failure), induce mode codes per edge from traces, and measure per-edge induced-mode stability under the paper's agent-as-a-judge validation.

### 6.2 How does fault-side attribution compose with ASES's four-role topology and claim discipline?

ASES currently routes work through Orchestrator (plan/delegate/gate), Builder (implement), Reviewer (pre-consumption audit), Auditor (in-flight divergence verifier), with a producer claim discipline (WHY/WHAT/HOW CERTAIN/WHAT-NOT-TESTED) and cheap staleness triggers. The paper's fault side (`model` vs. `harness`/`tool`/`environment`/`grader`) answers "where to fix" but does not map 1:1 to ASES roles.

Open questions:

- **Intervention routing table:** For each edge+fault pair, which ASES role + which artifact owns the fix? Example: `context — model · fault: harness-driven compaction` → Harness/Orchestrator (compaction policy); `model — tool · fault: model (Tool Recovery Failure)` → Model/Borrowed capability (post-training or prompt policy); `model — grader · fault: model (Specification Gaming)` → Grader/Owner (evaluation redesign) vs. Model (alignment). The paper hints at this mapping (§3/§7) but does not formalize it for an orchestrated multi-agent stack with durable position stores.
- **Claim discipline integration:** Can we require the Builder/Auditor's failure attribution claim to state the paper's edge+fault tuple *as* the WHAT, the trace evidence as the WHAT-it-is-based-on, the judge κ as HOW CERTAIN, and the evidence gaps as WHAT-NOT-TESTED — directly reusing ASES's existing discipline rather than inventing a parallel one?
- **Staleness semantics:** Is a `context — model · fault: harness` misclassification a "phantom document"–class staleness trigger (compare §4 of ASES audit findings on playbook section citations) requiring a cheap discriminating test before expensive induction work?

### 6.3 Evidence-binding and log-format heterogeneity

The paper's biggest disagreement source is heterogeneous evidence (complete trace vs. brief report). Our production orchestration already emits structured logs (Crosslink issue comments, `.crosslink` knowledge pages, `opencode.log` session trails, `.git/worktrees` reflogs, `.kickoff-status` markers) with varying completeness.

Open questions:

- What is the **minimum evidence quorum** for a production trace to be eligible for labeling vs. abstention? Should we adopt the paper's selective-voting abstention semantics (Table 4: ≥3/4 judges → 0.83 precision at 90% coverage; 4/4 → 0.96 at 68% coverage) as a quality gate for adaptive-taxonomy acceptance (analogous to AdaMAST's κ≥0.75 + coverage≥0.70 gate), or fold it into the durable store's position-advancement check?
- Can the paper's three-turn agent-as-a-judge pipeline (evidence reconstruction → classification → reflection/disambiguation) be ported to our "Auditor as one-role/two-phase in-flight divergence verifier" without violating role permission boundaries (Auditor is read-only; Builder owns fixes)? The paper's judges read external sources — our auditor would read cross-worktree git state via `git show` + `opencode.log` process trails.

### 6.4 Interaction with multi-agent coordination failures

The paper's `model — model (peer/subagent)` edge is the closest to our multi-agent orchestration concerns (delegation/communication failures under §5.2). Our current orchestration has independent failure surfaces: concurrent atoms, shared free-tier rate limits, pane-vs-process misreads, and fan-out contention on the Crosslink hub.

Open questions:

- Does the paper's `model — model` edge adequately localize *orchestration-layer* failures (e.g., the five-worker free-tier quota co-exhaustion observed tonight on this same issue), or do we need a dedicated **orchestrator-harness** component beyond the paper's vocabulary?
- How should **cascading failures** be handled when the earliest unrecovered failure lies on a different edge than the most visible symptom? The paper's "trace backward to earliest unrecovered" rule (§1/§3/§4) is compatible with our failure-matrix causal-chain practice, but our matrix currently keys rows to *outcome* families — does adopting edge+fault as the primary key require a matrix re-index?

### 6.5 Descriptive vs. quantitative — prevalence and intervention prioritization

The paper explicitly warns the taxonomy is descriptive, not a prevalence estimator, and that it "may need to expand as architectures evolve." For adaptive taxonomies in production we *need* quantitative frequency and severity to prioritize interventions.

Open questions:

- **Frequency estimation:** Under what sampling discipline can an induced per-system taxonomy support valid frequency estimates? The paper's illustrative 40-example set cannot; an adaptive learner that samples stratified production traces continuously may be able to, but would need to control for evidence completeness and judge abstention rates.
- **Expansion protocol:** When the adaptive learner proposes a mode that does not fit the 41, do we treat it as an extension under an existing edge (consistent with the paper's allowance to expand) or as evidence that the component vocabulary itself needs extension (new component or family)?
- **Severity/impact layering:** The paper annotates OWASP impact separately from the core label. Should production taxonomies layer severity (e.g., email-deletion vs. test-flake) as an orthogonal annotation, keeping the core taxonomy strictly about *where* vs. *how bad*?

### 6.6 Practical deployment of agent-as-a-judge in production

The paper's judges are frontier models (GPT-5.5, Opus 4.6–4.8) with moderate category accuracy (0.75–0.80) and lower mode accuracy; ensembling improves precision but cuts coverage. For nightly regression tracking on production traces:

- What **cost/latency/coverage** operating point is acceptable? Is 0.83 precision at 90% coverage (≥3/4 agreement) sufficient for a pre-consumption reviewer gate, with unanimous 0.96 precision reserved for the durable store's ground-truth labels?
- Can weaker/cheaper judges be calibrated against the stronger judge's labels (distillation), or does the causal-path reconstruction bottleneck (ungrounded diagnosis, per OpenRCA 2.0) require reasoning strength that only the frontier tier provides?
- How do we prevent the induction loop from **reifying its own blind spots** — i.e., the paper's induced codes align with human faithfulness under a matched panel, but only when the induction traces actually contain the failure? Sparse production reporting could systematically hide harness-side faults as model-side apparent failures.

---

## 7. Direct Quotes — Load-Bearing Passages (verbatim, with provenance)

All quotations below are verbatim from the local `full.html` (and cross-checked against `abs.html` where noted). Ellipses and bracketed insertions are analyst-added for brevity only where indicated.

**Q1 — Repair-assignment framing (Abstract, also `abs.html` `og:description`):**

> "Existing evaluations often reduce agent failures to system-level outcomes, obscuring where the fault originated and which intervention would actually improve the next iteration of the agent system."

**Q2 — Interaction-centric thesis (Abstract):**

> "We introduce an interaction-centric taxonomy that localizes agent failures to the interaction in which they originate and identifies the component responsible. We treat interactions between components as the unit of analysis. The taxonomy organizes 41 failure modes by assigning each failure to an edge between two components and a fault side indicating where the repair belongs."

**Q3 — Actionability mapping (Abstract/§1):**

> "This makes the taxonomy directly actionable: model-side failures identify targets for post-training, harness-side failures point to scaffolding and tool-integration fixes, and environment or grader failures reveal evaluation conditions that must be redesigned before they are used to judge agent capability."

**Q4 — Minimal-illustration of edge+fault ( §1/§3):**

> "Consider an agent that reports that a tool call succeeded when it actually failed. In one case, the tool wrapper suppresses the error, so the model never observes the failure. We label this failure `tool — model · fault: tool`. In another case, the wrapper returns the error, but the model ignores it. We label this failure `tool — model · fault: model`. The interaction is the same, but the responsible component differs."

**Q5 — Claude Code compaction example ( §1):**

> "For example, in a long-running Claude Code (4) session an agent may ignore an earlier user instruction because the harness's context compaction removed it, or because the instruction remained available but the model failed to follow it. The observed behavior is the same, but the first case requires a harness-level fix, whereas the second requires a model-level intervention."

**Q6 — Formal notation (§3):**

> "We write a failure as `comp₁ — comp₂ (edge) · fault: side (component at fault)` where the edge `comp₁ — comp₂` is the interaction between the two components and `side` is the component at fault."

**Q7 — Attribution rule for cascades (§1/§3):**

> "A single trajectory often contains many cascading failures. […] We therefore begin with the observed system-level failure and trace its causal chain backward. We label the earliest failure from which execution does not recover, rather than its downstream symptoms."

**Q8 — Three contributions (§1):**

> "First, we introduce an interaction-centric taxonomy of 41 agent failure modes, assigning each to an interaction edge and a fault side (Figure 2). Most modes are model-side, partly because our attribution rule assigns fault to the model when a more capable model could have avoided or recovered from the failure under the same conditions. Second, we ground the taxonomy in worked examples drawn from public benchmarks, model system cards, published reports, and logged agent trajectories, covering almost all of the failure modes. Third, we evaluate whether independent reasoning agents can consistently recover the human-assigned categories, providing evidence that the taxonomy captures a reproducible structure."

**Q9 — Reproducibility numbers ( §6):**

> "Across four frontier models, the judges recover the human labels well above chance, reaching a Cohen's κ of 0.76. […] They agree with one another about as strongly as they agree with the annotators, with the highest pairwise agreement reaching Cohen's κ of 0.84."

> "For category labels, GPT-5.5 has the highest agreement with the human annotations at κ = 0.76. Claude Opus 4.6 and 4.7 each reach κ = 0.71, followed by Claude Opus 4.8 at κ = 0.70."

**Q10 — Selective-voting trade-off ( §6):**

> "Increasing *k* trades coverage for precision (Table 4). Agreement among three judges yields 0.83 category precision at 90% coverage, while unanimity raises precision to 0.96 at 68% coverage."

**Q11 — Sources of disagreement (§6):**

> "For example, in E4, a public incident report attributes the agent's deletion of more than 200 emails to context compaction dropping the owner's instruction not to act, but does not provide the full trajectory. From the source alone, the case could be interpreted as either a context-side failure or a model-side unauthorized action."

> "In the case study in Appendix A.2, the agent correctly completes the initial task, but a scripted reply email required for the follow-up never arrives because of a bug in the evaluation environment. The judge, however, interprets the incomplete follow-up as the model failing to check for the reply, rather than tracing the failure back to the undelivered email."

**Q12 — Limitations block ( §7, verbatim):**

> "The taxonomy is descriptive rather than quantitative: it organizes failures and assigns responsibility but does not estimate their relative frequency. It is derived from the cases we reviewed and may need to expand as agent architectures and harnesses evolve. The taxonomy labels also depend on the available evidence, and brief reports or model system cards may omit details needed to identify a unique root cause. Moreover, the agent-as-a-judge framework used to validate the taxonomy may be difficult to deploy in production because judge accuracy remains limited, especially for failure-mode labels. We attempted to mitigate this through ensembling, but the gain in precision comes at the cost of lower coverage. The system may therefore abstain on cases where fault attribution is most uncertain."

**Q13 — Illustrative-not-prevalence disclaimer (§4):**

> "We selected examples that illustrate the taxonomy across a range of interaction edges and failure modes. The set is illustrative rather than exhaustive and should not be used to estimate the prevalence of individual failure modes."

---

## 8. Methodology Notes — Honesty, Certainty, and What Was Not Tested

**Distinguishing author claims from analyst inference:** Every factual claim about the paper's content above is attributed as an **author claim** (with quotation or §/table provenance) or explicitly flagged **[Analyst inference]**. The open-questions section (§6) is by construction inference, not paper content.

**Reasoning certainty for this source section (producer-side disclosure):**

- **WHY** this section exists: to provide the atomized evidence base for arXiv 2607.28802 that the Issue #429 collator will later compare against MAST / AdaMAST / ATLAS / 2607.16387 and against ASES methodology (four-role topology, failure matrix, claim discipline, adaptive-taxonomy relevance).
- **WHAT** it is based on: CLI-fetched local copies of the arXiv abstract page and HTML v1 (byte sizes above), tag-stripped text extraction via `HTMLParser`, section-boundary regex slicing for S3–S7, and manual cross-check of headline κ values across Abstract/§1/§6/Appendix.
- **HOW CERTAIN:** Headline claims (41 modes, edge+fault notation, component definitions, κ=0.76 category / 0.84 inter-judge, Limitations block) are **proven** within the paper's evidence (multiple independent mentions converge). Per-cell table numbers beyond the headline κ values are **evidence-based** (direct HTML reads, not independently recomputed). Open-questions (§6) are **guess / hypothesis** (labeled as such).
- **WHAT-NOT-TESTED:**
  - Paper PDF not fetched; HTML-only reading — PDF-specific figures/equations not visually verified.
  - Linked external traces (HuggingFace, Docent, GitHub issues, system cards) not independently fetched or inspected; any trace-specific detail is paper-reported, not verified here.
  - No independent judge re-run; Appendix A prompt/config details were present only at TOC level in the extracted text and were not executed.
  - No statistical re-computation (confidence intervals, per-mode κ, significance tests) on the 40-example set; table transcriptions not independently regenerated from a machine-readable artifact.
  - No prevalence or frequency inference attempted (explicitly disclaimed by authors).
  - No synthesis with sibling sources (MAST et al.) — intentional per atomized scope.

**Cheapest-test-first posture:** The paper's central discriminating claim is that category-level judge agreement (κ=0.76) demonstrates the taxonomy captures shared structure, not annotator idiosyncrasy. The cheapest test for a consumer wishing to adopt the taxonomy is therefore to replicate §6 on a *small* local trace sample with two judges and check whether category κ remains well above chance before investing in full 41-mode induction.

**Evidence-preservation note:** Local copies at `/tmp/opencode/src5/abs.html` and `/tmp/opencode/src5/full.html` are outside the worktree (`/tmp` is ephemeral) — the *content* of this section is the durable record. Future readers should re-fetch from `https://arxiv.org/abs/2607.28802` and `https://arxiv.org/html/2607.28802v1` to audit quotations; byte sizes and fetch timestamps are recorded in frontmatter for provenance.

---

## 9. Quick-Reference — Interaction-Centric Vocabulary for the Collator

For the Issue #429 collator: the paper's contribution is a **repair-routing grammar** (edge + fault side + earliest-unrecovered attribution) with **41 leaves** and a **reproducibility result at the category level** (κ=0.76). Its direct value for adaptive taxonomies is as a *fixed-axis proposal* whose codes can be induced per system from traces, with the agent-as-a-judge + selective-voting machinery as a candidate quality gate — subject to the paper's own limits (descriptive, evidence-dependent, mode-level judge accuracy with coverage costs).

---

*Source section prepared under Issue #429 atomized-source-worker-5-of-5-v2 — CLI-fetch method (curl to local HTML, no WebFetch). All synthesis deferred to collator.*
