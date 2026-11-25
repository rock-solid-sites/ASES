---
title: "Frontier reasoning comparison: Kernel-0 and Work Unit continuity"
version: 0.1.3
status: Experimental
authority: Derived
last_updated: 2026-11-25
---

# Comparison — 2026-11-25

## Provenance and limitations

Common intended input: [v0.2.0 reasoning packet at 5385e4157c8506baf8e40d4bf288fec364656360](https://github.com/rock-solid-sites/ASES/blob/5385e4157c8506baf8e40d4bf288fec364656360/docs/research/astra-followup-20261125/frontier-comparison/WORK-UNIT-AUTHORITY-QUESTION.md). The operator supplied three responses labelled ChatGPT GPT-6.2 High, Codex Sol 6.2 High and Codex Astra 6.2 High. [ChatGPT attachment](responses/chatgpt-6.2-high.md) was preserved in full, connector readback identical to extracted text. [Codex responses](responses/codex-high.md) transcribed with table padding normalized and common source link consolidated. Session provenance, elapsed times, allowance deltas and independence of execution were not independently verified. Operator subsequently supplied screenshots confirming the reported 24k and 37k figures are **context-window occupancy**, not cumulative inference-token usage: Codex Astra 6.2 High 24k/258k (UI 9% used, 91% left), Codex Sol 6.2 High 37k/475k (UI 8% used, 92% left). Sol's displayed context capacity is approximately 84% larger in these configurations. Operator clarification: these were fresh one-shot tasks, well below context compaction thresholds. For this exploratory comparison use displayed counts as approximate task-token-usage proxies (Astra 24k versus Sol 37k, approximately 35% fewer for Astra), not as verified cumulative provider inference accounting. Context compaction can permit continuation beyond a context window, so capacity is not a total task budget. Actual metered inference tokens, reasoning-token breakdown, subscription allowance deltas and elapsed time remain unknown. Operator notes GPT-6.2 High in ChatGPT is included in the plan without a separately counted token allowance. Treat context occupancy, subscription entitlement/consumption and verified outcome quality as separate routing dimensions; the one-shot token proxy supports a provisional relative token-efficiency observation, not a cost or allowance-efficiency ratio. Earlier 46% remaining Astra allowance was a pre-pilot observation, not a per-response measurement. The comparison is an unblinded coordinator analysis of one task, not a controlled ranking or cross-family assurance.

## Convergence

All three reason from the custom Kernel-0 / Work Unit requirements rather than historical prototypes. They separate durable work and attachment continuity from temporary execution and currently valid authority; require atomic authorization/admissibility at the authoritative decision point; keep authority changes themselves governed; require coherent ordering where conflicts or invariants demand it, not necessarily global ordering; distinguish known failure from unresolved external effects; preserve historical outcomes without reviving superseded authority; and permit scoped concurrency without treating attachment identity as the whole conflict boundary. All identify the external-effect boundary as a consequential unresolved issue. None establishes the kernel's actual minimal ontology, a complete transition relation, or realization conformance.

## Differentiating contributions

- ChatGPT: explicit observational minimality test, seven candidate invariants, bootstrap trust, separation of authority issuances, negative control against vacuous deny-all safety, explicit durability/failure-model limits and distinction between logical categories and physical storage. Most detailed; not proof of greater reasoning capacity.
- Sol: economical articulation of dependencies and shared invariants across different records, authority lifetime versus process timeout, distinction between eligibility and holding conflicting operations pending reconciliation.
- Astra: concise statement of stable work and mutable authority, precise question of what acceptance actually authorizes (enduring obligation vs continued execution authority), vacancy during handoff and limits on recalling externally dispatched actions.
- No material frontier-only semantic requirement established by this sample. Do not infer a general model performance or efficiency ranking; compare actual measured cost/allowance and repeat on genuinely harder tasks if justified.

## Architectural implications (hypotheses, not adopted specification)

Treat the convergence as support for a scoped, atomic authoritative-change contract, not a decision to add specific kernel objects or primitives. The historical ISOLATE/CONNECT/ORDER vocabulary remains a separate kernel-level research question; the reports neither prove sufficiency nor justify its replacement. Distinguish domain-level work continuity and history retention from what must be protected or enforced at the kernel boundary. The kernel must support external effect constraints where required, not automatically implement a universal effect ledger or guarantee exactly-once behavior. A pre-handoff committed obligation may remain actionable according to its own authority and policy; this does not grant the former executor new authority.

Further research: construct the smallest abstract candidate with explicit authority-change rules, conflict/dependency scopes and external-effect contract. Attempt to falsify it with both positive and negative histories: fresh grants, stale replay/identifier reuse, authority laundering through derived/delegated grants or queued requests, split decisions across shared resources, interruption/recovery and unknown external outcomes. Determine which distinctions are expressible, which require intrinsic semantics, and which remain outside the kernel. The shared-authority composition and delegated/derived authority question was not developed sufficiently in any of these reports. No choice of implementation language or reuse of prototype owner justified. No tests performed in this comparison.

Next: consolidate here, obtain missing allowance/time measurements and actual inference-token accounting if available, and consider an anonymized cross-family assessment only if it would resolve consequential ambiguity. Do not spend frontier allowance repeating this same derivation. Retain previous native/Rust evidence as separately scoped evidence, not a design anchor.
