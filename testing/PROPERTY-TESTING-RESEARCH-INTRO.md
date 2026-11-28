---
title: Property and Stateful Testing Research — Next-Session Introduction
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

# Property and stateful testing — research introduction

**Start here for the next session.** Two related questions are open: **when do generated properties/stateful histories add reliable evidence beyond simpler tests**, and **can the experimental knowledge index retrieve and connect that research more accurately than repository search**? Neither question creates a new mandatory ASES method, service or skill. Durable findings stay in the owning repositories; this document is a routing map, not a session transcript.

## Evidence already available

- **Synthetic engine canary:** [ASES PR #58](https://github.com/rock-solid-sites/ASES/pull/58) compared Hegel and proptest on an intentionally simplified Kernel-0 stale-execution witness. Both detected three deliberate mutants and shrank to a two-operation counterexample. This does **not** verify Kernel-0 or identify a framework winner. See the [executed result](https://github.com/rock-solid-sites/ASES/blob/experiment/hegel-proptest-kernel0-20261119/research/testing-assurance-pilot/property-engines/RESULTS-2026-11-18.md).
- **Real-code follow-ups:** [cross-project research and findings](https://github.com/rock-solid-sites/ASES/blob/experiment/hegel-proptest-kernel0-20261119/docs/research/Generated%20Property%20and%20Stateful%20Testing%20Cross-Project%20Pilot%202026-11-19.md), including [ASES Rust Store PR #59](https://github.com/rock-solid-sites/ASES/pull/59), HMS generated reservation/finance tests ([#20](https://github.com/rock-solid-sites/HMS/pull/20), [#21](https://github.com/rock-solid-sites/HMS/pull/21), [#23](https://github.com/rock-solid-sites/HMS/pull/23)), and [Trip'n booking-contract PR #30](https://github.com/TripN-Chill-Zone/tripn-astro/pull/30). Distinguish real code from synthetic fixtures, an invalid HMS signed-zero oracle from a product defect, and observed provider behavior from deployed assurance.
- **Experimental method workbench:** [ASES PR #60](https://github.com/rock-solid-sites/ASES/pull/60) — [selection candidate](methods/selection-candidate.md), [experiments](experiments/2026-11-cross-project-pilot.md), [counterexamples](counterexamples/README.md), and [lessons](lessons/2026-11-cross-project-lessons.md). Independent review before any method promotion: Work Notes `WNASES-10`; lab tracking `WNASES-14`.
- **Knowledge-index experiment:** [ASES PR #61](https://github.com/rock-solid-sites/ASES/pull/61), currently draft/unmerged; [post-review 49-test CI](https://github.com/rock-solid-sites/ASES/actions/runs/44587792625) passed. That verifies prototype regressions, **not** retrieval quality, graph semantics or permission enforcement.

## First new task — property-testing research retrieval pilot

1. Build a small **public, source-pinned manifest** of relevant documents, test files, CI evidence and reviews. PRs #58/#59/#60/#61 are different unmerged branches; resolve **repository + commit/ref + path** for each rather than assuming one checkout or `main` contains everything.
2. Independently establish source-backed answers to **15–20 representative questions**: which claims were tested on real code, which negative controls failed, where an oracle was rejected, what was actually repaired, which seeds/replays survive, and what provider or concurrency boundary remains untested.
3. Compare the knowledge index against ordinary repository search over the **same authorized sources**. Record misses, misleading candidate relationships, bad identity/provenance links, confusion between proposed/experimental/adopted work, correction effort and costs **only where measured**.
4. Publish one small reproducible evaluation card in the testing laboratory, including minimal failing queries or a legitimate zero-finding result. Stop for the ASES-19 pilot decision before building connectors, adopting a framework or promoting a method.

**Boundary:** no raw private chats or restricted HMS/Trip'n records in public ASES/CI; no production changes, live bookings, payments, deployment or automatic issue synchronization. The index is a derived cache and cannot confer source authority.

## Where the next session picks up

**Human decision:** Projektor `ASES-19` (index pilot); **agent execution:** Work Notes `WNASES-16` (benchmark). Existing method review `WNASES-10` remains distinct. Use source-linked Git results rather than recreating the previous conversation. Verify the current PR heads and evidence before acting.

Legacy `SESSION-START.md` and `docs/SESSION-END.md` still refer to retired Crosslink commands; the separate modernization task is Projektor `ASES-11`. Current handoff surfaces are **GitHub evidence, Projektor planning, and Work Notes execution records**. If this introduction cannot lead a fresh session to the primary tests and unresolved questions without the chat, correct the routing links first.
