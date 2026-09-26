---
title: Kernel-0 Still-Live Realization Experiment
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
last_updated: 2026-09-26
crosslink_issue: 566
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
  - Kernel-0-Finite-Model.md
related_documents:
  - Kernel-0-Realization-Comparison.md
consumed_by:
  - Further Kernel-0 assurance experiments
---

# Kernel-0 Still-Live Realization Experiment

## Contract recorded before implementation

This experiment instantiates the existing finite consumer policy; it does not
change Kernel-0 or select production architecture. The starting branch is
`codex/kernel-0-reasoning-566` at `c24f680bcf90a5989d49a07da83f272d4ede60eb`
(verification-skill installation after finite-model result `f4c84568`).

One Python process owns the complete retained view. Separate executor processes
receive only connected Unix socket handles. At trusted bootstrap each service
endpoint is permanently associated with management or one of four finite
authority contexts. Requests cannot supply or override that association. Several
handles can denote the same context; copies do not create new authority. The
service never rebinds a handle after withdrawal. A finite issued mask additionally
prevents re-granting a withdrawn context. Replacement uses a different context
and handle, even when the executor uses the same local descriptor number.

The supervisor initially has the handles and distributes them intentionally;
it is trusted management, not an adversarial executor. Executable bootstrap and
OS descriptor isolation are part of the trusted boundary. Management authority
remains valid throughout. Old physical producers obtaining a replacement handle
are not excluded: the profile uses transferable authority evidence.

| Model distinction | Concrete representation / abstraction |
| --- | --- |
| `established`, two stable positions, one work | Retained established flag; fixed interpretation maps both positions to the same work. No executor identifier is part of work identity. |
| Two work bits | Immutable tuple of two integers. |
| Required content atoms 0/1 | Complete retained strings, including their bytes on the wire, mapped bijectively to the two model atoms. No external reference or digest substitutes for content. |
| Issued mask, rights, delegation parent | Explicit retained mask and immutable tuples with the exact finite policy. Initial unissued contexts may have bootstrap handles but no permission. |
| Authentic authority context | Service-side association of the connected endpoint, outside caller-controlled JSON. This is the concrete counterpart of the model's ideal authenticity premise. |
| Proposal | Complete bounded JSON frame copied and decoded in the service; frozen scalar request. Effect kind/target/value/other map to the model request. |
| Commit | Under one service lock, evaluate guard and candidate invariant against current state, then replace the entire immutable view. |
| Deny | No view replacement; reply reports denial. Malformed complete frames are additional denial stutters outside the model's well-formed alphabet. |
| Pending / unknown caller outcome | Incomplete or unprocessed frame, blocked request, or no reply after an executor dies. Absence of acknowledgement never implies denial. |
| Executor loss | Terminate a separate OS process, discarding its private memory and handles; submitted copies and service state survive. Death does not revoke authority. |
| Retained content holder | The service's immutable view, independent of the executor process. Replacement fetches and consumes the actual content. |
| Interacting order | One service lock covers all guard dependencies and whole publication. Replies follow resolution. A completed affected change therefore precedes a request initiated later. |
| Three-request order fixture | Separate explicit three-bit consumer extension using the same guarded boundary, checked against the finite model's `serial_witness` history oracle; not silently mapped to the two-bit state graph. |

No required distinction is left implicit: continuity names are fixed interpretation
constants; policy is fixed startup configuration; endpoint association is trusted
ingress state and must be included in the abstraction of requests. The optional
three-bit fixture is separately accounted for. Buffers, request phases, locks and
reply delivery refine asynchronous events; they do not grant authority.

Serializing unrelated operations is an implementation choice stronger than the
required partial order. Concurrent executors and overlapping submissions remain
possible. There is no deduplication: repeated valid `flip` requests commit twice.
The finite evidence supply cannot be refreshed after exhaustion.

## Planned falsification and trusted assumptions

Use the unchanged finite model as an oracle for every concrete operation in
generated traces, replay its recorded success and counterexample reference
traces, compare its reachable graph against the independent concrete reducer,
and check concurrent histories for a whole-set serial explanation. Terminate
executors at deterministic ingress, validated-before-publication, and
published-before-reply cuts. Test malformed ingress, capability confusion,
retargeted payloads, copied snapshots and accepted-content retention.

Test-only scheduling gates may pause a service handler through supervisor-only
pipes. They cannot assign state or supply a replacement validation view; no
executor receives these descriptors. Ungated concurrent tests must also run.

Assumptions: trusted supervisor and initial management; correct finite policy;
Python interpreter/standard library and lock behavior; Unix process/descriptor
isolation and stream byte delivery; no runtime/OS/hardware corruption or memory
exhaustion; service remains live with its memory intact. Same-user hostile
debugging, signals against the service, arbitrary descriptor theft and executable
replacement are below this experiment's isolation boundary, not tested defenses.
No cryptographic or remote-network authentication claim is made.

Independent service restart, persistent storage, protected external sinks,
unbounded identities/content/delegation, progress, fairness, deadlines,
exactly-once handling, physical producer binding and work-product correctness
remain outside scope. Property tests are counterexample searches, not proofs.

The operator authorized Hypothesis as an experiment-only dependency and an
in-session requirement-by-requirement adaptation of the installed
`spec-to-code-compliance` skill. Its separate-agent workflow was not included in
the installation. The compliance report must not claim independent review.

**WHY:** This is the smallest realization route identified by the fixed comparison
that can lose an executor without losing accepted information or authority.
**WHAT:** Existing semantics, verification obligations and finite-model evidence.
**HOW CERTAIN:** Contract and test plan only at this checkpoint; no realized
conformance conclusion yet. **WHAT-NOT-TESTED:** Implementation and all concrete
attacks are pending; exclusions and trusted assumptions are listed above.
