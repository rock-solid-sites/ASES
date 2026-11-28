---
title: When can split authorities publish a handover separately?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Native-acceptance-and-recovery-boundaries.md
  - docs/research/kernel-0/When-handover-order-must-be-fixed.md
  - docs/research/kernel-0/Custody-at-an-admission-closed-cut.md
last_updated: 2026-11-28
---

# When can split authorities publish a handover separately?

F3 can select an owner record and F4 can publish a sink cut. A future Work Unit operation might promise that both status surfaces describe one replacement. An adapter that returns local values during their publication gap can break that promise even when each local state is correct. Which surfaces must change together depends on the reads the contract allows. This distinction is useful before proposing a common authority record. [Native source crosswalk](Native-acceptance-and-recovery-boundaries.md)

## A counterexample with two single-surface reads

Consider one replace operation taking a set of fields from old to new atomically. A caller can read an owner-facing field and a sink-facing field, with each completed read claiming the current value of its field in the same abstract replacement history. Suppose the owner field becomes visible as new before the sink field does. Pause the transition. Read the owner and receive new. After that read returns, read the sink and receive old. New puts the abstract replace before the first read. Old puts it after the second. Their actual order leaves no linearization.

If publication order is reversed and the caller can also reverse read order, the same contradiction follows. A reader that joins both values in one snapshot also distinguishes an exposed mixed cut. A success response that waits for both local publications cannot repair earlier authoritative reads. The counterexample uses no crash, clocks at the API, or concurrent readers. A local management diagnostic can report partial progress without having this meaning. [Atomic visibility for transactional readers, Bailis et al.](https://people.eecs.berkeley.edu/~alig/papers/ramp.pdf)

## An exact grouping result for one replacement

The following model concerns a single successful replacement. Each observation surface i returns old until its switch time tᵢ, then returns new. Reads are immediate and authoritative. Delaying publication steps and interposing reads in a nonempty gap are allowed. Switch times lie between the replacement invocation and its reply. A required projection specifies which pairs of reads can complete in order. Include i→j when that projection permits the caller to finish reading i before reading j. If the contract requires a **common** linearization for several callers, include the cross-caller real-time orders as well. For a weaker contract that compares only one caller's projection at a time, include pairs from each allowed projection. Self-edges are immaterial.

**The exact condition is tⱼ ≤ tᵢ for every i→j.** If tᵢ < tⱼ, complete those two reads in the gap to obtain new followed by old. If the inequalities hold, no ordered pair in any required projection can contain such an inversion. The observations in a projection are therefore a sequence of old replies followed by new replies. Put the abstract replacement after the old replies and before the new ones, respecting the operation's interval. This supplies a sequential explanation of that projection. The result also applies to point reads that linearize at their sampling times, provided every observable nonoverlap can be interposed as assumed. It concerns the read interface for one successful operation. It leaves retries and overlapping replacements to a separate proof.

It follows that switches within every strongly connected component of the read-order graph must be atomic at this interface. Switching those components in reverse topological order is sufficient, so the components give the finest publication partition under the model. For example:

- If a status client may read F3 then F4 but has no observation requiring the reverse order, making F4 visible first can satisfy the two-read contract.
- If both orders are allowed, F3 and F4 must share a switch at that interface.
- If one client can read A and B in either order, and another can read B and C in either order, A, B and C form one required group even if nobody can read A and C together.
- Under global linearizability of independently callable current reads, arbitrary callers can supply both nonoverlapping orders. Partitioning by present UI workflow would then be unsound.

This makes the cost depend on the contract. If a read may defer in the gap, or reports only independently typed observations such as “selected locally” and “published at cut h”, the premises change. Such APIs need explicit semantics for interpreting uncertainty and locality. A sequence constrained to a pinned snapshot has a read-version rule absent from this model. A reusable audit asks which of these behaviors the consumer actually depends on, including joined observations and permitted causal orders, before assuming all underlying transitions need one transaction.

## A sufficient release discipline and its limits

When a common switch is required, stage each prospective state under immutable keys. Independently establish that the old admitted prefix is complete, fenced and recoverable. One protected selection then identifies the new scoped binding and the required prepared records. Current observations resolve that selection, use the records selected by it, or defer. A protected append or external effect needs its own enforcement of the selected authority at the actual effect boundary. Checking a selection, dropping the guard and committing later would reopen the authorization race. Durable fencing or one serialized decision can close that gap under the respective premises.

In this construction, staging is unobservable as authoritative change. The observable switch is selection. Prior accepted data remains bound to the earlier cut until the new cut can promise its own custody. Completed visible decisions must survive whatever faults the contract covers. If a trusted resolver forgets a version it already exposed, reconstructing the staged records by themselves cannot decide whether that version went live. This repeats the underlying evidence obligation at the publication surface. A single authoritative selection is one sufficient semantic unit here, regardless of whether a realization uses a single store or an equivalent distributed mechanism. It does not entail a global Work Unit database. [Surviving decision and material](Committing-to-a-surviving-cut.md) · [Final extent and custody](Custody-at-an-admission-closed-cut.md) · [Crash-model distinction, Izraelevitz et al.](https://www.cs.rochester.edu/u/scott/papers/2016_DISC_persistence.pdf)

**Research disposition.** For the actual native prototype, F3 and F4 document different state and the checked surface has no authenticated X→Y replacement. The counterexample applies conditionally to a proposed facade promising common current state. It is a discriminator for choosing that facade's contract, separate from the question of whether a bridged implementation can conform. The weakest remaining question is what the successor, the resource gate and management readers must be able to assert about the same cut. A source crosswalk can answer which fields exist. No new runtime or broad atomicity claim follows from this argument.
