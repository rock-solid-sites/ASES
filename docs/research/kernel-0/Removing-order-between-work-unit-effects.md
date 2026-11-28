---
title: When can ordering between Work Unit effects be removed?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
  - docs/research/kernel-0/Minimum-revalidation-at-commit.md
  - docs/research/kernel-0/What-a-receipt-reveals.md
  - docs/research/kernel-0/Disconnected-resource-allowances.md
last_updated: 2026-11-28
---

# When can ordering between Work Unit effects be removed?

Two requests may commute on an empty snapshot but cease to commute after another permitted request. A proof that eliminates order has to cover the reachable prefix at which the swap occurs and the replies attributable to each request. Static read/write disjointness is one sufficient shortcut. A proof of matching local outcomes under swaps gives a more general criterion. [Historical locality argument, §P4](https://github.com/rock-solid-sites/ASES/blob/00086d1722a22b481daa834b1e2b0f1a2d3e2b9e/docs/research/kernel-0/Kernel-0-Generalization.md)

## Sufficient local conditions

Fix an authoritative sequential model. Each request step gives a reply and a next state. Include failed admissions as distinct replies with their declared effects. The chosen observation contract keeps replies attributed to request identities and the final state. It allows a permutation of the relative order of replies for independent requests. If a global order is observable, include that order in the required result or leave it in the dependency relation.

At any reachable prefix, two independent requests A and B have a valid swap when both orders give the same final state and A and B each get their own same reply in both orders. Equality of final projected states also suffices if a previously established congruence preserves all future decisions along their suffixes. A configuration that calls a request “optional” must still include its refusal, side effects and reply where the observer is entitled to see them.

**Local-to-global argument.** If every allowed adjacent swap at every reachable prefix satisfies the condition, each swap conserves the full subsequent trace up to the allowed response permutation. A common prefix produces the same state for both orders. The two swapped steps leave the same state for the remaining suffix. Joining these local arguments proves the result for every finite chain of permitted swaps.

For finitely many distinct requests with a dependency partial order, every two linear extensions can be connected by swapping consecutive incomparable requests. Take the first request in the target order and move it left through the source order until it is first. Every element crossed must be incomparable with it, since either required order between them would forbid one of the two lists. Repeat on the suffix. Thus the local test permits any linear extension of the retained dependencies, even when the two chosen concrete schedules have different total orders. Reachability must include all prefix transitions allowed by the model, including loss/recovery and authority changes when those can precede a swap.

## Counterexamples that set-equality misses

- A capacity-two owner starts empty and three distinct requests each need one unit. Every two requests can be accepted in either order from the empty state, with identical replies and final usage two. With three requests only the last is refused. Reversing their order changes which request obtains the last unit. Pair checks at the initial snapshot miss the failure at the reachable prefix where one unit is used. To remove more runtime order, provision independent allowances or another conservation proof. [Independent allowance envelope](Disconnected-resource-allowances.md)
- Two non-overlapping append resources can reach the same content if each accepts its update in either order. If both callers are also given a position in a global log, reversing the order can change both receipts. The data updates commute. The observed interface does not. A scope-relative receipt or an explicitly ordered log is a different contract. [Receipt observations](What-a-receipt-reveals.md)
- A revocation and a fresh append might both be accepted relative to their own preflight states. An append admitted after the revocation can be forbidden even when its data would not conflict with whatever records the revocation writes. Independence concerns the guard and reply at the effect point, including authority evidence and negative dependencies, not only byte writes. [Commit revalidation](Minimum-revalidation-at-commit.md)

The proof also identifies a verification shortcut. A reviewer can reuse one schedule's observation test for schedules related entirely by proved swaps, while keeping one discriminating control for each hidden dependency under challenge. This is distinct from assuming every execution is a serialized reference schedule. A concurrent implementation must first show it actually corresponds to allowed whole transitions, without extra partial effects, duplicated admissions or stale observations. A valid local diamond does not establish storage isolation or compile away a real coordinator on its own. [Partial-order reduction, Flanagan and Godefroid](https://patricegodefroid.github.io/public_psfiles/popl2005.pdf)

## Mechanized obligations

The [Lean proof](proofs/CommutingEffects.lean) checks the local-to-global result for lists related by independent adjacent swaps under common prefixes. The theorem preserves final state and reply multiplicities, with each reply still paired with its request. It also verifies the capacity-two counterexample: every pair commutes at the empty state, while two schedules of three requests disagree. Run `lean docs/research/kernel-0/proofs/CommutingEffects.lean` on Lean 4.19.0. The check exited 0. The generic local-diamond theorem reports no axioms. The argument connecting linear extensions and the native implementation mapping remain separate.

**Disposition.** Additional order constraints are unnecessary where the reachable local swap and effect correspondence premises can be proved for the declared observations. An opportunity to remove a particular native ordering step needs those premises and a reachable witness for the affected effects. No native order change or new schedule experiment is implied here.
