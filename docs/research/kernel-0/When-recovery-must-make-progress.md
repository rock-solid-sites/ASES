---
title: When does a recovery implementation have to make progress?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
  - docs/research/kernel-0/Recovery-as-repeated-decisions.md
  - docs/research/kernel-0/Restoring-history-without-restoring-authority.md
last_updated: 2026-11-28
---

# When does a recovery implementation have to make progress?

Every finite projected history of an implementation can be legal while a continuing Work Unit is permanently unable to run again. An implementation can stage, inspect, poll, or reopen forever and publish no prohibited effect. If the specification permits temporary deferral, every finite prefix can satisfy the safety proof. The corresponding infinite history can still violate a promise to reactivate work after the owner, custody, and delivery assumptions hold. This must be checked independently of whether a correct response can be chosen when a decision is made. [Kernel-0 adequacy requirements](Kernel-0-Evidence-Packet.md#verification-requirements) · [Choice under incomplete recovery evidence](Recovery-as-repeated-decisions.md) · [Attie, refinement of liveness properties](https://groups.csail.mit.edu/tds/papers/Attie/Attie-liveness.pdf)

## A finite-state decision procedure for one outstanding obligation

Augment the concrete transition graph with a monitor for a particular obligation. The monitor records the request or tenure incarnation, which observations start the promise, and which response or effect actually discharges it. First check the ordinary safety relation. Then keep the reachable vertices and edges on which that obligation remains pending. Preserve distinct outgoing edge labels even when the source and destination coincide. Treat an actual deadlock as a quiescent repeat of the same state if the environment contract permits time to pass there. If legitimate cancellation discharges the promise, encode its concrete, observed conditions in the monitor. A new request or an unrelated success cannot clear the old promise by overwriting the monitor.

For each fairness assumption i, mark the set of concrete states Eᵢ in which its action is enabled and the set of concrete edges Tᵢ on which it is taken. Evaluate Eᵢ in the full system, including possible edges that leave the pending region. Under weak fairness, perpetual enablement from any point requires infinitely many taken edges. Under strong fairness, enablement infinitely often requires infinitely many taken edges. These assumptions about scheduling and delivery differ. Neither follows from an action having a queue or an eventual-retry label. [Weak fairness and generalized Büchi checks](https://www.lrde.epita.fr/~renault/publis/LPAR13.pdf) · [Checking strong fairness](https://dlnext.acm.org/doi/10.1007/s10703-006-4342-y)

A reachable bad run exists exactly when the pending graph contains a reachable strongly connected subgraph S with at least one cycle, satisfying each applicable row.

| Assumption | Required in S for the bad run to be fair |
| --- | --- |
| Weak fairness for i | Some vertex is outside Eᵢ, or some internal edge belongs to Tᵢ. |
| Strong fairness for i | Every vertex is outside Eᵢ, or some internal edge belongs to Tᵢ. |
| Event that must recur | Some internal edge records that event. |
| Condition that must eventually hold continuously | Every vertex satisfies that condition. |

For necessity, discard the finite prefix containing the last occurrence of every nonrecurring vertex and edge. The remainder visits the recurrent vertices, with paths between every pair, and witnesses every row's condition. For sufficiency, in a candidate subgraph connect the selected witness edges and a visit to every vertex by internal paths and repeat the resulting nonempty closed walk. Its recurring vertices and selected edges satisfy all rows. Reach it through any pending prefix. The bounded system therefore has a finite explanatory prefix and a repeating walk for every violated promise under these assumptions. Timing guarantees require additional evidence and the proof makes no deadline claim.

For an effective check, first restrict the recurrent graph to vertices satisfying the eventual continuous conditions. Reachability still uses the original pending graph because those conditions need not hold in the prefix. Enumerate cyclic maximal strongly connected components of the restricted graph. Failure of a weak fairness row or a recurrence row rules out the entire component and its subgraphs. If a strong fairness row fails in a component, it contains an enabled vertex but no internal taken edge. Any good subgraph of that component must omit every vertex in Eᵢ. Remove those vertices and run the same check on the resulting components. Repeated failures remove vertices or whole components, so the finite procedure terminates. A final accepted component constructs the witness. A component with no outgoing pending edge still needs a cycle to support the witness. For purely weak fairness the pruning step is unnecessary.

## What goes wrong with coarse checks

- A pending state can stutter and can also discharge by a fair action. Compute enablement after deleting discharge edges and the enabled action appears absent. The stutter is then reported fairly permanent even when continuous enablement and weak fairness rule it out.
- Two pending states can alternate between enabled and disabled while never taking the discharge action. Weak fairness admits that loop. Strong fairness rules it out. If a disabled state has a stutter loop of its own, a fair bad run under strong fairness can still get there and stay there. Rejecting an entire maximal component at the first failed strong fairness row would miss that run.
- A process-local success receipt can witness the historical outcome of the old call while its owner-selected settlement is still unresolved. An abstract monitor that clears on any related success code would hide this outstanding obligation. The admitted native owner rollback observation demonstrates that these facts can separate. It makes no fairness or infinite scheduling claim. [Native distinction and exact cut](Native-owner-selection-rollback-result.md)

## Non-vacuity and responsibility

Weak or strong fairness is conditional on the actual enabled predicate. The implementation can make a required action permanently disabled on an admissible service history unless the interface independently constrains that behavior. Include concrete conditions such as retained custody, visible selected state, and an actual authorized effect path in the checked graph. Express an environmental availability premise using facts the implementation cannot silently redefine as “ready.” For example a stable owner during the obligation might be an external availability premise. Eligibility at its protected gate is a property of the collector, authorization state, and gate.

Also check which admissible finite prefixes have a fair extension. Apply the same recurring-component test to the whole graph with the promise filter removed, and take the backwards reachable set through admissible edges. A missing fair continuation means progress is vacuous for that prefix. Starting with a graph whose legal prefixes already represent the environment contract matters. This check alone cannot validate that the contract reflects the intended environment or establish a particular actor's implementation-side duty. Fairness constraints may also need to be preserved through candidate state elimination. Public finite replies by themselves omit enabling and scheduling facts the proof uses.

**Disposition.** A defensible positive recovery promise needs both safety correspondence and discharge on the declared environment histories. The procedure gives a deductive, finite-state discriminator with a finite loss witness, independent of the choice of kernel primitive. To apply it to the native owner, specify exactly which acknowledgments discharge F3, whether unresolved activation may terminally fail, and which custody and delivery facts remain externally visible. Correspondence with concrete scheduling remains to be established, and a new native run remains admission-gated.
