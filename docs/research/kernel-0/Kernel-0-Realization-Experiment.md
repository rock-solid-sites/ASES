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

## Result

**A — Conforming experiment, within the finite still-live-service profile and
the explicit trusted assumptions below.** No unrepaired service/model divergence
or semantic counterexample was found. This is bounded experimental evidence,
not an unbounded proof, independent audit or production architecture decision.
The original semantics, verification obligations, model and finite-model evidence
are unchanged.

The central finding is that one separate holder can retain the complete finite
view and accepted content while real executors disappear. Fixed endpoint
associations distinguish authority even when local descriptor labels and request
bytes are identical; one service lock keeps current validation and whole
publication together. The protected boundary includes the trusted bootstrap,
runtime and OS, rather than just the policy reducer.

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

At the pre-implementation checkpoint:

**WHY:** This is the smallest realization route identified by the fixed comparison
that can lose an executor without losing accepted information or authority.
**WHAT:** Existing semantics, verification obligations and finite-model evidence.
**HOW CERTAIN:** Contract and test plan only at this checkpoint; no realized
conformance conclusion yet. **WHAT-NOT-TESTED:** Implementation and all concrete
attacks are pending; exclusions and trusted assumptions are listed above.

## Implementation and reproducible evidence

- [Service](./kernel0_service.py): 233 lines, standard library only. It does not
  import or call the model. There is one ingress handler and one guarded resolver.
- [Checks and adapter](./kernel0_realization_check.py): maps requests, retained
  state and outcomes to the unchanged model; launches separate service/executor
  processes; generates and shrinks traces; checks concurrent histories.
- [Test dependency](./kernel0_experiment_requirements.txt): Hypothesis 6.168.1,
  installed in a temporary isolated environment. No service dependency was added.
- [Generated results](./Kernel-0-Realization-Experiment-results.json): counts,
  concrete loss outcomes, concurrent witnesses, minimized mutant counterexamples,
  runtime version and source hashes.
- [Conformance review](./Kernel-0-Realization-Conformance.md): twelve requirement
  reviews, enforcement paths, assumptions, exclusions and reverse-direction findings.

Final checks ran from a clean `git archive` export of
`bbb67d1281f0ad080869a6a84ddf052b31a02440`, with new service processes and no
Hypothesis example database. The recorded environment was Linux, CPython 3.11.15
and Hypothesis 6.168.1. The final results' source hashes were checked against the
working branch before committing the report. The final publication adds evidence
and documentation; the tested implementation/checker sources are unchanged.

Agent reproduction, in a Python environment with the pinned test dependency:

```sh
python3 docs/research/kernel-0/kernel0_finite_model.py --output /tmp/kernel0-finite-check.json
python3 docs/research/kernel-0/kernel0_realization_check.py --output /tmp/kernel0-realization-check.json
```

Run without `-O` because test assertions are the oracle. The service itself does
not use assertions for enforcement. Local Unix sockets and process termination
must be permitted. The restricted session sandbox blocked socket traffic; the
actual process suite ran through approved execution outside that restriction.
The initial standard `venv` bootstrap lacked `ensurepip`; installed `uv` created
the temporary environment instead. Neither required changing the experiment.

## Checks and model correspondence

| Check | Final evidence / precise limit |
| --- | --- |
| Unchanged finite model | 16,688 authoritative states; 2,469,824 transitions; 1,195 asynchronous states; 4,096 ordering histories. Generated finite results exactly match the original JSON. |
| Exhaustive reducer differential | All 148 templates at every reachable state of the independent, coupled and exclusive profiles: 2,469,824 matching edges, including 309,459 commitments. This is direct reducer comparison, not 2.4 million IPC tests. |
| Recorded-model replay | 13 trace groups: success, six mutant reference traces, newly valid evidence at an old physical producer, and five shortest detached-validation counterexamples; also stale replays after two replacements. Labels/outcomes/states are read from the existing evidence. Detached traces replay observations and recorded resolution order, not every abstract scheduling event. |
| Generated live sequences | 200 Hypothesis-generated programs plus one pinned shrunk generator regression, up to 50 choices each; 1,921 differentially checked live requests including ordinary trace replay (1,402 commits, 519 denials). Every successful operation kind is exercised. |
| Generated live order histories | 100 three-request histories. Search all permutations for a common explanation of commits, denials, returned views, final state and observed response-before-invocation edges. No model ordering is supplied to the service. |
| Generated bypass attempts | 150 forbidden-evidence envelopes with generated payloads, through real ingress; no protected state change. Twelve additional deterministic malformed/retargeted/oversized cases. This is not exhaustive parser fuzzing. |
| Generated executor loss | 59 actual process kills before candidate submission within generated sequences; view equality checked afterward. Deterministic cuts below cover later request stages. |
| Concrete concurrent attacks | Compatible fields, coupled writes, exclusive grants, delegation/restriction and six three-request cycle launch labelings. The final run observed overlapping invocation/response intervals in all 110 generated/targeted histories. Six labelings are not six forced service schedules. |
| Deliberate concrete weakening | Five local reducer wrappers fail: no-reuse, confusion, partial denial, attenuation, stale admission. Hypothesis shrinks each and the checker verifies that the failing operation is the intended one. These are controlled test variants, not executable service bypass modes. |

Properties come from the contract and unchanged model: current rights, stale
exclusion, whole effects, denial equality, configured invariants, continuity,
common affected-operation order and no mutation through copied snapshots or
asserted authority. Three quarters of generated choices prefer model-enabled
operations; the rest include rejected operations, with additional forged
assertions. There is no `assume` filtering. An exhausted authority supply falls
back to denial traces rather than inventing progress. Deterministic generation
and pinned dependencies support reproduction; OS scheduling remains variable.

## Required concrete attacks

| Attack | Observation |
| --- | --- |
| Valid authority → protected change | Commits; all ten successful operation kinds have live witnesses. |
| Read old authority, revoke, attempt commit | An ingress-held old request denies after acknowledged revocation; earlier read does not authorize it. |
| Replacement versus old request in both orders | Old-before-replacement commits; replacement-before-old denies. Two successive fresh replacements are exercised. |
| Replay/reuse of withdrawn evidence | Old endpoint remains denied; the issued context cannot be granted again. |
| Deliberately confusable evidence | Old and replacement processes use local fd `64` and identical JSON. Different service endpoint associations yield deny/commit. Claimed identity fields cannot override them. |
| Compatible independent work | Both changes commit and have one coherent explanation. |
| Conflicting writes valid at old `(0,0)` | Under `x+y≤1`, only one commits. |
| Three-request cyclic precedence | All three observe `000`; fewer than three commit. The existing whole-set history oracle finds an allowed order for the committed set and final view. |
| Acknowledged revocation, later-started request | Later request denies; no reordering before the completed change is used to explain it. |
| Loss before request / before acceptance | Private candidate/proposal disappears; accepted view is unchanged. |
| Loss during receive and handling | Partial frame has no effect. Complete retained request can commit after executor death. At the validated cut the lock also prevents a racing replacement from intervening. |
| Loss after publication, before reply | Whole state is visible on another endpoint while the caller has no acknowledgement; killing that caller preserves it. |
| Replacement continuation | Kill producer after accepting content; replacement process fetches actual retained content and consumes it in `resume`. |
| Bypass/live-reference attack | Mutating client candidate or returned nested snapshots does not change accepted meaning; attempted state/rights/identity fields deny. No external referent is accepted. |
| Composite with one forbidden portion | Mixed work-plus-grant denies without changing work or issuance. |
| Attenuation and racing parent restriction | Over-broad delegation denies; concurrent restriction cannot leave an over-broad child. |
| Duplicate after lost reply | Authorized replayed `flip` commits again, restoring the starting bit. No exactly-once guarantee is added. |

## Correspondence attack and findings

The review examined every admission input, all assignments of protected state,
ingress parsing, candidate copies, lock lifetime, reply construction, descriptor
bootstrap and the test harness's monitors. Passing tests were not treated as the
result gate by themselves.

| Discovery / challenge | Classification and disposition |
| --- | --- |
| Inherited descriptor used OS nonblocking mode with a fresh Python wrapper configured as blocking | **Implementation defect in verification harness**, repaired by matching timeout configuration. The worker had failed before returning its result; this was not a service counterexample. |
| Readiness polling after a buffered stdout read could miss an already buffered second line | **Implementation defect in verification harness**, repaired with unbuffered subprocess pipes and explicit child-error inspection. |
| Generator assumed some permitted operation always remained after finite-context exhaustion | **Implementation defect in verification harness / wrong progress premise**, shrunk to `[1477,2670,705,1,1,1,1]`; repaired and pinned. The model permits only denials at that point. |
| Initial mutation wrappers could alter restriction itself and report detection before the intended stale/delegation attack | **Implementation defect in verification evidence**, found after the suite first passed. Repairs restrict weakening to the intended operation; final counterexamples include expected/actual outcomes and states. |
| Endpoint association and immutable startup policy are not fields of the finite tuple | **Trusted assumption / correspondence accounting**, resolved by including them in concrete configuration and request abstraction. Caller JSON does not authenticate itself. |
| Extra cycle bits, protocol buffers, gate state and reply copies | **Conformance-boundary ambiguity**, resolved explicitly: cycle uses the existing separate history fixture; buffers/gates affect submission/pending/order, and copies are observations. None silently supplies current permission. |
| Copying new valid evidence to an old physical producer | **Deliberately excluded physical-source guarantee**; new current evidence can commit, as the model permits. Revoked evidence itself remains invalid. |
| Shared stream handles and incomplete bytes | **Conformance-boundary limit**: proposal identity is the complete retained ingress frame. Client multiplexing and intent preservation before complete ingress are not claimed. No endpoint holder can bypass current guarded admission. |
| Accepted strings versus arbitrary live/large content | **Deliberately excluded generalization**. The entire accepted string is retained; arbitrary object graphs, external bytes and storage failures were not tested. |
| Total serialization, safe memory copies and process isolation | **Trusted runtime/OS assumptions plus an explicit stronger ordering choice**. The service lock, not the harness, enforces order. No compiler, OS or hardware proof is implied. |

No discovery required changing the semantic contract or finite model. The
conformance review classifies the obligations as enforced, assumption-dependent,
or deliberately excluded; none remains missing inside this profile. This does
not prove completeness of the review.

## Final claim and next discriminating step

**WHY:** The separate holder and guarded publication preserved the finite contract
under exhaustive reducer comparison and discriminating live loss/order attacks;
weakened enforcement produced the intended counterexamples.

**WHAT:** The committed sources, generated source-hashed evidence, unchanged
finite-model rerun, 451 generated/pinned test cases across three property groups,
ordinary attacks, repaired mutation checks and direct conformance review.

**HOW CERTAIN:** Evidence-based **bounded Result A**. Reducer agreement is
exhaustive over the declared reachable finite states/templates; concrete process
behavior is supported by tested traces and source inspection, not a formal
whole-stack proof or independent judgment.

**WHAT-NOT-TESTED:** Independent service restart; persistent storage; protected
external actions; arbitrary outside facts; physical binding after evidence
transfer; cryptography; arbitrary/unbounded content, contexts or delegation;
all OS schedules and byte streams; fairness/progress; exactly-once handling;
runtime/OS/hardware correctness or hostile supervisor compromise; independent
review. The original finite-model fixture-composition limits remain in force.

The next smallest discriminating step is an **independent review of this exact
ingress → current validation → publication → acknowledgement correspondence**,
using the unchanged semantics/model and concrete source. Target incomplete/shared
ingress, unknown replies after loss, and the completeness of the declared trusted
boundary; attempt a counterexample before considering any additional machinery.
This addresses the present self-review limitation. It does not call for service
restart, a database, a new formalism, or architectural expansion.
