---
title: When must Work Unit handover order be fixed?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Local-owner-admission-and-replay.md
  - docs/research/kernel-0/Repeated-handover-histories.md
related_documents:
  - docs/research/kernel-0/Reconstructing-a-cut-from-prepared-updates.md
last_updated: 2026-11-28
---

# When must Work Unit handover order be fixed?

An abandoned append may commit before replacement and have its reply delayed. It may instead reach admission after replacement and be rejected as stale. Both are legitimate. A completed-history checker correctly accepts both. Can that checker establish that the disposition of old work was fixed by the time replacement returned? A finite mutation shows the gap. It also shows why the same test over the public wire history alone would reject a correct owner. [Existing owner crash windows](Local-owner-admission-and-replay.md) · [Completed-history decision procedure](Repeated-handover-histories.md)

## Two owners with overlapping public traces

In the test contract X is the old executor at a stable position. At most one append, of a named value, is outstanding. Replacement is a single abstract operation: it moves the current authority to Y, retains earlier accepted contents and returns OK. An append linearized under X accepts and changes the contents. An append linearized after replacement returns STALE and leaves the contents alone. A later Y read returns the authoritative contents. A separate observer event T occurs strictly after the replacement reply and before the append reply. T neither changes the Work Unit nor supplies authority.

The honest owner either commits the append before replacing X or leaves it to be rejected after replacement. In both cases it withholds the append reply until after T. In the late-decision mutant, the operation that returns replacement OK has not fixed the disposition. The mutant sees T, then chooses either to report STALE or to record the old append as accepted and to return it to Y. With T a binary input, the mutant chooses accepted exactly when T is 1. For either terminal trace, there is a legal sequential explanation. In the accepted trace the explanation puts the still-pending append before replacement. In the stale trace it puts it after replacement. The result of the later Y read agrees with each explanation. The mutant's public traces are a subset of the honest owner's public traces. This also holds with unrelated stuttering events and lost append replies before the Y read, under the same test boundary. The schedules require no aliased writer and vary no caller grants.

Every public prefix through the replacement reply is the same. In any prefix-preserving linearization, replacement must already have been included at this cut. To allow the accepted continuation, the prefix must already start with the accepted append. To allow the stale continuation, it cannot start with that append. No one choice extends to both. If the checker retains a trustworthy, complete stream of real append commits, the honest owner has separate concrete prefixes and a prefix map exists. If the checker merely receives a note emitted after T claiming that the accepted append committed earlier, the prefixes at the cut are still identical. Trusted events are needed at the real decision boundary.

The distinction is an instance of strong linearizability on execution histories. Ordinary linearizability quantifies over each complete history and some possible order. A prefix-preserving proof also requires each chosen order to extend the order already fixed for every shared prefix. A missing such proof over the public projection may reflect loss of information about actual decisions. This is why the fixture checks the honest owner both with and without instrumentation. The general distinction and the connection to randomized clients are established prior art. [Golab, Higham and Woelfel, *Linearizable Implementations Do Not Suffice for Randomized Distributed Computation*](https://arxiv.org/abs/1103.4690)

## A conditional observable consequence

If an independent fair coin is sampled at T, the late-decision owner has probability one of making the indicator for accepted old work equal to the coin. Any nonanticipating atomic owner has already fixed that indicator at the replacement reply: the old append can only succeed before this cut. Its match probability is one half, even if the owner randomized earlier. Independence of the coin from the previous execution is needed, and the mutant needs access to its result or an equivalent post-return input. This is a discriminator for applications that rely on irrevocability before a subsequent unpredictable input. ASES has yet to establish that all consumers need this stronger behavioral contract. If the actual effect-side append and replacement events are already independently trusted and ordered, those events give a more direct invariant check.

## How much prefix evidence can be necessary?

Generalize the fixture to n independently admissible, distinguishable X appends, each targeting a separate position in a vector of accepted contents. They belong to the same replaced tenure. All invocations precede completion of replacement, and all append replies arrive after it. Suppose any subset S can be accepted before the cut, and Y's later read exposes that exact subset. Fix the order of the n invocations and the rest of the public prefix. The prefix witness must distinguish at least 2^n possibilities at this cut. If two subsets share a witnessed prefix, an append in their symmetric difference must already precede replacement in one linearization and cannot precede it in the other. Any prefix-preserving map on the common witness fails. Recording the accepted set suffices for this family: append its members in fixed index order, then replace, then record each stale append when it returns. It preserves real time because all the pre-cut appends overlap. This is an evidence lower bound of n bits at a common public cut. The bits may be conveyed in incremental trusted events, store records or a single snapshot. It is independent of whether the verifier must recover after storage loss. If all accepted appends enter a single ordered log, the order itself can be observable and a set need not suffice. An alternative observation contract returns the accepted cut as part of the replacement reply. This separates the public prefixes at the right time and makes a conflicting later disposition fail even ordinary linearizability. It requires authority to disclose the cut to the replacement caller. An opaque token works only if its checked meaning binds to one admissible cut at reply time. [Related prepared-cut recovery result](Reconstructing-a-cut-from-prepared-updates.md)

## How to test the contract

Instrument the actual resource admission and authoritative replacement boundaries. Pause an old call before deciding it, return replacement, and deliver the old call including a later input T. Also pause a reply after a genuine old commit, return replacement, and show that Y sees the committed value in this case. Treat the delayed reply and the delayed decision as distinct controls. A replay auditor can use a chronological, effect-bound certificate and compare it with the actual replies and Y's accepted contents. A certificate generated after the fact from the very status responses under question does not supply a witness at the cut.

Run `python3 docs/research/kernel-0/handover_prefix_refinement.py`. The finite model enumerates legal sequential completions, including returning or dropping each pending invocation, and searches for a single prefix-preserving assignment on the entire trace tree. Both owners pass ordinary linearizability. The honest owner passes the prefix test on 22 instrumented prefixes and fails on its 18 public prefixes. The mutant fails on both its 12 public and its 14 instrumented prefixes. The cut-reporting replacement passes on 21 public prefixes, and both false reports are ordinary linearizability failures. The script also checks the independence example and the compatible-prefix counting argument for one through five pending appends. [Executable checker and controls](handover_prefix_refinement.py)

**Outstanding obligations.** The model does not instrument or prove conformance of any existing owner. A production certificate would need complete mediation of effect boundaries, an observation of the actual owner commit or its equivalent with known authority, and a check that recovery preserves those facts. Distributed handover, append cancellation, and implementations with only backward or prophecy-based simulation need a separately specified observation contract. No result makes a Work Unit tree or a particular primitive vocabulary necessary.
