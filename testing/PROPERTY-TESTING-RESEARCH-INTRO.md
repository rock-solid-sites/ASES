---
title: Property and Stateful Testing Research — Introduction and Next-Session Route
program: ASES
layer: Research
document_type: Research Introduction
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md
related_documents:
  - testing/README.md
  - testing/methods/selection-candidate.md
last_updated: 2026-11-19
---

# Property-testing research — introduction for the next session

**Begin here.** This is a thin routing document, not a transcript, a new testing method or a claim that any implementation is production-verified. The next research session should examine **when generated property/stateful tests add distinctive, trustworthy evidence over simpler deterministic tests**, and use that existing research as the **first practical retrieval/provenance evaluation of the ASES knowledge-index prototype**. Those are related but separate experiments.

## Research question and established evidence

Start with a consequential claim about **real source code**, its authority boundary, an independently checkable oracle, and an observation that could falsify it. Evaluate whether generated input cases, ordered state histories, shrinking and replay add useful discrimination; report oracle errors, no findings, blind spots and costs as results, not as failures to find bugs.

The initial [Hegel/proptest synthetic Kernel-0 witness, ASES PR #58](https://github.com/rock-solid-sites/ASES/pull/58) showed that both frameworks detect three deliberately inserted stale-execution violations, each shrinking to a simple two-operation witness. That **does not test Kernel-0 itself or establish a framework winner**. The larger [cross-project research document](https://github.com/rock-solid-sites/ASES/blob/experiment/hegel-proptest-kernel0-20261119/docs/research/Generated%20Property%20and%20Stateful%20Testing%20Cross-Project%20Pilot%202026-11-19.md) records subsequent real-code experiments, including [ASES Rust Store, PR #59](https://github.com/rock-solid-sites/ASES/pull/59), HMS fast-check reservation/finance experiments ([PR #20](https://github.com/rock-solid-sites/HMS/pull/20), [PR #21](https://github.com/rock-solid-sites/HMS/pull/21), [PR #23](https://github.com/rock-solid-sites/HMS/pull/23)), and [Trip'n booking-contract evidence, PR #30](https://github.com/TripN-Chill-Zone/tripn-astro/pull/30). Distinguish synthetic mutation detection, generated tests against real code, a rejected oracle (the HMS signed-zero case), provider observations, and actual deployed behavior.

The experimental ASES [testing laboratory, PR #60](https://github.com/rock-solid-sites/ASES/pull/60), holds the [candidate selection rules](methods/selection-candidate.md), [experiments](experiments/2026-11-cross-project-pilot.md), [counterexample index](counterexamples/README.md) and [transferable lessons](lessons/2026-11-cross-project-lessons.md). This laboratory is **not** a competing installed skill or adopted methodology. Independent method-promotion review remains in Work Notes `WNASES-10`; laboratory readiness is tracked in `WNASES-14`.

## First knowledge-index pilot: retrieve the property-testing evidence

The [knowledge-index prototype, draft PR #61](https://github.com/rock-solid-sites/ASES/pull/61), is a **read-only derived cache**, not a source of authority. It passed [49/49 regression tests after independent post-repair review](https://github.com/rock-solid-sites/ASES/actions/runs/44587792625). Prototype acceptance as an experiment is separate from any hosted, permission-aware cross-project service; track that decision in Projektor **ASES-19**.

1. **Pin a public source manifest** of the selected research documents, fixture/test code, CI reports and independent-review records. PRs #58, #59, #60 and #61 are separate **unmerged branches**: a checkout of only one branch does not automatically contain the others. Resolve each repository/ref/path explicitly; never silently substitute `main` for a draft source.
2. **Design 15–20 representative retrieval questions** covering: the initial stale-execution invariant, a real-code negative control, a rejected test oracle, a red→green repair, the actual provider/trust boundary, reproducible seeds/versions, a model-review false positive or timeout, and an unanswered research question. Pre-record source-backed reference answers independently of the index.
3. **Compare index retrieval with ordinary repository search** on the same authorized corpus. Record relevant sources returned/missed, incorrect links or identities, unsupported graph edges, classification errors (proposal vs experiment vs accepted), manual correction effort, and measured tool/compute/token cost *only where available*.
4. **Publish one small experiment card and results**, with minimal failing queries and exact pinned source/CI pointers, in the ASES testing laboratory; report NO_DISCREPANCY, INCONCLUSIVE, REJECTED_ORACLE, or confirmed defects precisely. Do not write a chronological reconstruction or call candidate edges verified facts.

**Privacy boundary:** do not ingest raw private conversations, archives or restricted HMS/Trip'n material into the public ASES repository or public Actions. Begin with deliberately published sources; any later restricted corpus requires a separate, authorized and isolated environment. No live bookings, settlements, production deployment, automatic issue synchronization or methodology promotion are authorized.

## Route and stopping conditions

- **Research evidence:** draft [PR #58](https://github.com/rock-solid-sites/ASES/pull/58) and its linked owner-repository results; **test-laboratory framing:** draft [PR #60](https://github.com/rock-solid-sites/ASES/pull/60); **retrieval engine and security limits:** draft [PR #61](https://github.com/rock-solid-sites/ASES/pull/61).
- **Planning:** Projektor `ASES-19` (index pilot) and `ASES-7` (existing assurance methodology review); **agent work:** Work Notes `WNASES-10` (independent method review) and `WNASES-14` (testing laboratory).
- **Next action:** run the small property-testing source-manifest and retrieval benchmark first, then decide whether the index actually helps. A new generator, service, connector, repository migration or multi-model review requires an explicit evidence gap, not a default next step.
- **Known documentation debt:** root `SESSION-START.md` and `docs/SESSION-END.md` still refer to obsolete Crosslink operations. Modernization is separately tracked in Projektor `ASES-11`; this handoff uses GitHub/Projektor/Work Notes pointers instead.

**Fresh-session check:** Can a new reviewer locate the real-code tests, rejected oracle, independently verified outcomes and unresolved questions from these pointers **without relying on this chat**? If a link or claim is stale, verify the live repository/issue first, correct the routing pointer and mark the uncertainty; do not reconstruct facts from memory.
