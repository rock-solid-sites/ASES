---
title: Kernel-0 Whole-History Refinement Assurance
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 567
depends_on:
  - Kernel-0-Generalization.md
  - Kernel-0-Verification-Obligations.md
  - Kernel-0-Crash-Recovery.md
consumed_by:
  - Kernel-0 re-minimization and stronger realization decision
---

# Phase 5: decide a concrete refinement question

Selected gap: individually plausible operation replies and recovered states might
not belong to any single allowed commitment history when multiple operations
cross service loss. Earlier reducer agreement and isolated crash cuts do not
settle that proposition for an observed concurrent trace. Checking final invariants
or replaying operations in the tester's preferred order can hide the failure.

Build a separate finite **whole-history refinement search**. Input consists only
of an initial declared state, authentic request observations, invocation/response
events, actual holder-loss events and observed recovered views. It is not given a
service linearization order, internal commit flag, or which unknown calls committed.
At each observed-event boundary it may resolve any invoked pending request using
the unchanged abstract policy, or defer it. A normal reply must match a prior
resolution's outcome and whole returned view. Lost replies place no outcome
constraint. At a crash unresolved operations may disappear; already committed
state cannot. Recovery must equal the current whole abstract state. New operations
may start afterward. Enumerate every such finite possibility with memoization.

This search decides whether **there exists** an allowed explanation of the complete
observed history, respecting invocation, response and crash boundaries. The finite
algorithm is sound by induction over its construction rules; completeness for
this event abstraction follows by choosing each operation's slot in an allowed
history. Neither claim says that all hidden implementation behavior is correct.
Known returned snapshots are captured at commitment, so they need not equal the
state when a delayed reply is finally consumed. Bytes/replies already in transport
may arrive after holder loss. Pre-crash pending requests cannot be silently
executed after restart without a new invocation.

No new formal language is selected. A theorem prover assuming perfect atomic
storage would duplicate the conditional lemmas; this explicit finite decision
procedure addresses actual observed histories without making an I/O proof claim.
The implementation and checker share the original abstract consumer policy as a
specification dependency, but not the concrete reducer or trace order. Algorithmic
separation is not independent human/model judgment or independent formal evidence.

## Result: observed implementation histories admit whole abstract explanations

`kernel0_trace_refinement.py` collected **15 real process histories**: five
adversarial schedules repeated three times, each with two overlapping calls,
holder SIGKILL, recovery, a post-recovery old-evidence call, and a second
loss/recovery observation. All admit a whole-history explanation. The schedules
cover independent composite work, coupled field admission, published replacement
with an old request, old ingress held across completed replacement, and accepted
content followed by continuation. Returned evidence includes the entire witness
order; the checker does not inherit a preferred implementation order.

Four short deliberately inconsistent histories are rejected: stale success after
acknowledged replacement, rollback of acknowledged replacement, a partial composite
with no reply, and two individually plausible but mutually incompatible successful
snapshots. The last cannot be detected merely by checking each snapshot's invariant.
Two explicit positive histories retain the ambiguity of no reply: both old and
whole-new recovery are accepted when either could explain the pending operation.

`Kernel-0-Refinement-results.json` includes the observed event streams, source
hashes, discovered explanations, rejected histories and search-state counts. Run
`python3 docs/research/kernel-0/kernel0_trace_refinement.py --output PATH` without
`-O`, with local Unix socket/process permissions. No formal-tool installation or
new runtime dependency was needed.

### Attack on the checker and interpretation

The checker initially allowed an unknown transport result to end a call while
the holder was live. A still-live holder could subsequently commit that call,
which would require keeping it unresolved in the history model. This experiment
only records unknown outcomes after actual holder loss; the checker now enforces
that boundary explicitly. It is not a general network-loss history checker.
The concrete recorder waits for all pre-crash responses before restarting, while
allowing already buffered successful replies to be observed after loss.

Negative traces are short, designed discriminators, not claimed globally minimal
counterexamples. Search is exhaustive for each supplied finite trace, not for all
OS schedules. The policy oracle is the earlier finite specification; a shared
policy error would survive both. The input abstraction assumes authentic endpoint
association, truthful invocation/response observations and no undeclared outside
writes. At most three operations are recorded per fixture and no external sink is
included in this refinement layer. Original source/sink temporal evidence remains
Phase 2 evidence.

**WHY:** returned state snapshots and uncertain calls must have one joint
explanation, not separate convenient explanations. **WHAT:** a separately written
finite decision procedure, 15 actual concurrent/crash histories and six oracle
discriminators. **HOW CERTAIN:** bounded implementation-trace refinement evidence;
same-session reasoning, **not independent formal assurance**. **WHAT-NOT-TESTED:**
all schedules, independent policy specification, arbitrary stream errors, low-level
SQLite I/O faults, compiler/OS proof or general liveness. No semantics changed.
The remaining strongest tractable gap is storage-boundary crash placement.
