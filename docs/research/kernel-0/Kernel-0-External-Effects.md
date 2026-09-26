---
title: Kernel-0 Protected External Effects
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 567
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Crash-Recovery.md
consumed_by:
  - Kernel-0 composition and minimality assurance
---

# Phase 2: choose the claim before mechanisms

An authorization decision, irrevocable sink acceptance, and later observation are
three events. Current authority at the first does not imply current authority at
the second. A consequence accepted before revocation can become observable later
without any stale authorization. A read of current permission followed by a later
unguarded sink action cannot enforce permission *at sink acceptance*.

Select a useful minimal **decision-authorized obligation profile**. A producer with
current authority may commit an immutable obligation to cause a specified effect.
The commitment is the authority-checking event. Later producer revocation forbids
new decisions but does not cancel this obligation. A trusted mediator may cause
sink acceptance only from a committed matching obligation. The sink's effect is
irreversible in the declared event alphabet. Pending obligations survive source
crash; once accepted, the sink consequence survives its declared failure class.
No cancellation, no at-most-once, no deadline, no unconditional delivery liveness.

The finite witness has one monotone intent slot, one payload, two authority
observations, at most two sink acceptances and two crashes of each participant.
Repeated delivery of that one intent may produce duplicate effects. Keeping the
intent forever removes the need for a delivery acknowledgement record or cleanup
protocol. This is a finite experiment, not a proposal for unbounded retention.
An implementation wanting multiple distinct obligations or reclamation must prove
that the obligations and their outcomes remain distinguishable.

| Candidate guarantee | Selected profile / additional necessity |
| --- | --- |
| Revoked evidence cannot create a later decision | Required: current guard at durable decision. |
| Sink effect has a matching authoritative commitment | Required: durable whole intent before a mediator can send its exact payload; sink accepts only trusted mediated ingress. |
| Previously committed required consequence cannot silently disappear | Required as durable recoverability of the obligation until sink acceptance; no promise that an adversarial scheduler ever delivers it. Conditional eventual acceptance needs live sink plus fair repeated delivery. |
| No effect accepted after producer revocation | Not promised. Requires a coherent order at the sink spanning revocation and acceptance, or cancellation that wins before acceptance. A stale permission check is insufficient. |
| No visibility after revocation | Not promised. Even earlier irrevocable acceptance may be observed later. Such a claim needs stronger control of visibility itself, not just cancellation of unaccepted work. |
| No duplicate effect after lost acknowledgement | Not promised. Requires idempotent consequence, sink deduplication with durable identity, or an equivalent outcome-resolution contract. Source retry policy alone cannot infer an unknown sink outcome. |
| Compensation repairs an unauthorized irreversible effect | False: a later compensating event does not make the first event authorized. Compensation is a consumer policy, not required here. |

Minimum forced additions are an enduring accepted obligation, mediation binding
its exact effect to sink ingress, and explicit failure assumptions for source and
sink. A queue, networking, global transaction, consensus and exactly-once protocol
are not forced. The obligation's authorization survives producer revocation by
this selected policy, not by a universal Kernel-0 rule.

WHY: separating these events prevents temporal authority claims from changing
meaning during realization. WHAT: the base external-action contract plus the
chosen obligations. HOW CERTAIN: conditional profile derivation; model/experiment
pending. WHAT-NOT-TESTED: general sinks, cancellation and eventual delivery.


## Result A2: selected obligation profile survives

The finite sink model `kernel0_effect_model.py` closes at **2,715 states and
9,924 edges**. Six independent weakenings fail: past authority at decision,
volatile intent, sending tentative intent, forgetting on send, volatile accepted
sink outcome, and cancelling an uncancelled obligation merely on producer
revocation. Shortest BFS counterexamples and seven pinned temporal histories are
in `Kernel-0-External-Effects-model-results.json`. Pinned histories distinguish
acceptance from later visibility, pre/post-intent crashes, in-flight messages that
survive source failure, and duplicate retry after lost sink acknowledgement.
The bounded search also allows in-flight message loss; delivery is not built in
as inevitable. No fairness or cutoff theorem is claimed.

`kernel0_effect_experiment.py` supplies the stricter source consumer and a tiny
separate sink process. Source uses Phase 1's whole-image transactional boundary;
its only intent update is monotone acceptance of the one exact content atom.
An attempted overwrite denies. The sink holds a counter whose committed increment
is irreversible in its API. Only the trusted mediator has its descriptor. The
mediator reads a committed immutable obligation, so producer revocation cannot
make that observation stale for the selected delivery policy. This does **not**
justify checking a revocable permission outside a sink and using it later.

The concrete evidence includes five source kill/restart cuts around decision,
preparation, durable commitment and acknowledgement; two sink kill/restart cuts
around acceptance; and completed revocation before delivery. Pre-intent source
loss causes no sink effect; post-intent loss retains a deliverable obligation.
Sink loss before acceptance retries to one consequence. Sink acceptance with a
lost reply retries to **two** consequences. New use of revoked producer evidence
denies, while delivery of its earlier durable obligation succeeds after revocation.
See `Kernel-0-External-Effects-experiment-results.json` for source digests and
observed values. Run each executable with `--output PATH`, without `-O`; the
process experiment needs local Unix sockets. No new dependency is required.

### Adequacy and conformance attack

The first abstract draft erased every in-flight message on crash, omitting a
possible acceptance after source loss. It now explores both loss and survival and
has an explicit surviving-message history. Generic successful-state reachability
could also hide wrong temporal order; the seven pinned histories assert exact
orders in addition to exhaustive closure. The stale-check mutation also preserves the actually observed permission, so its failure requires a previously valid observation, rather than simply bypassing every guard. These were model-adequacy repairs.

The sink trusts descriptor possession as mediator provenance; it does not verify
a portable source certificate. The mediator and configured source/sink identity
are part of the trusted boundary, including failure-safe selection of the actual
committed obligation. The concrete sink is a controlled count, not a proof about
arbitrary financial, physical or network consequences. Source and sink storage
inherit the Phase 1 currentness/atomicity assumptions. The experiment does not
claim a joint source/sink transaction, source garbage collection, distinct intent
IDs, arbitrary payloads, message reordering across multiple intents, sink-current
authority, cancellation, or delivery liveness.

**Strong negative:** decision; revocation; delayed sink acceptance is permitted
here and refutes the stronger claim that decision-time authority alone prevents
post-revocation effects. Acceptance; lost acknowledgement; retry produces a
second consequence. Compensation afterward would not remove either historical
fact. The disposition is to state this profile precisely, not silently add
cancellation or deduplication.

**WHY:** the guard protects the chosen authorization event; retained obligation
and trusted sink mediation preserve the intended causal contract across loss.
**WHAT:** finite closure, six weakened variants, pinned orders and actual source/
sink termination. **HOW CERTAIN:** evidence-based bounded **A2**, self-reviewed;
not a universal effect transaction system. **WHAT-NOT-TESTED:** exclusions above,
independent refinement and OS/storage internals. No new Kernel-0 primitive follows.
Proceed to Phase 3.
