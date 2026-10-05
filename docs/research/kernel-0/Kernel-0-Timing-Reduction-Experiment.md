---
title: Kernel-0 Timing Reduction Experiment
program: EDASES
layer: Research
document_type: Research Protocol
status: Experimental
authority: Derived
canonical_repository: ASES
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
  - Kernel-0-Direct-RTL-Experiment.md
  - Kernel-0-Re-Minimization.md
related_documents:
  - Kernel-0-Ingress-Reduction.md
  - Kernel-0-Finite-Model.md
  - Kernel-0-Direct-RTL-Result.md
  - Kernel-0 Ingress Reduction Independent Review at 2a97e9dd8a6af9dc447d5d8f07009b2c0abba5b6
consumed_by:
  - Independent review of the Kernel-0 timing contract
  - Bounded timing observation-refinement experiment
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-10-05
---

# Kernel-0 Timing Reduction Experiment

## Decision and claim boundary

**Candidate reduction:** retain a trustworthy interpretation of each whole
proposal and a compatible history of guarded whole authoritative transitions.
Remove a periodic clock, a common physical sampling/publication edge, fixed
latency, and total ordering of unrelated commitments from the semantic contract.
No particular replacement timing mechanism has been shown necessary.

The remaining timing obligation is observational: admission, whole-effect
publication, and observations must describe the same permissible commitment
history. Physical changes can take different times. An intermediate encoding
cannot become current authoritative meaning, authorize another request, or be
reported as a completed successor. An earlier coherent view cannot authorize an
effect at a later incompatible position in that history.

This is a proposed reduction of the realization contract, **not a demonstrated
clockless circuit or a physical minimality result**. Stop here at an independently
reviewable experiment design. No circuit, controller, handshake, new proposal
kind, or revised Kernel primitive is introduced.

## Pinned inputs and preserved target

The realization baseline and branch parent are
`ac9d128e984dddecbbf08c810a9cfc53e9754ac9`. The governing
[Abstract Semantics](./Kernel-0-Abstract-Semantics.md),
[Verification Obligations](./Kernel-0-Verification-Obligations.md),
[Direct RTL Experiment](./Kernel-0-Direct-RTL-Experiment.md), and
[Re-Minimization](./Kernel-0-Re-Minimization.md), plus the
[finite model](./Kernel-0-Finite-Model.md), oracle/codecs and
[ingress result](./Kernel-0-Ingress-Reduction.md), were read at that baseline.

The expressly requested comparison input is the
[independent review synthesis at `2a97e9d`](https://github.com/rock-solid-sites/ASES/blob/2a97e9dd8a6af9dc447d5d8f07009b2c0abba5b6/docs/research/kernel-0/Kernel-0-Ingress-Reduction-Independent-Review.md).
It is read as review evidence, not imported into this branch or substituted for
baseline semantics. This explicit cross-ref comparison is the only exception to
the Direct RTL Experiment's same-ref rule. Neither frozen artifact is modified.

The synthesis supports bounded behavioral preservation and a structural ingress
reduction, conditional on protected lanes and synchronous timing. It expressly
leaves whole-event capture, current-view observation, whole publication and
interacting order for this research step. It also reports a pre-existing
Python/RTL discrepancy for some raw non-catalog words. Consequently:

- Semantic correspondence remains the **148 authentic catalog proposals** and
  all legal states in the independent, coupled and exclusive profiles: 8,449,
  6,337 and 1,921 states, including the 19 legal but unreachable states.
- Protected fixed lanes and their management origin remain trusted. No authority
  label or authenticity verdict is returned to caller control.
- The five-lane input abstraction remains exactly-one-valid submission;
  zero/multiple valids at the effective capture boundary mean **no submission**,
  no resolution and no effect. This is a retained interface choice, not a Kernel
  requirement for arbitrary transports or arbitration.
- Raw encoding checks use the frozen RTL's specified decoding behavior, separately
  from catalog oracle checks. No all-raw-word Python/RTL equivalence is claimed.
- The holder survives executor loss. Accepted content, issued distinctions,
  rights, parent and work information remain within its assurance boundary.
  Holder restart, persistence and protected outside effects are excluded.

The abstract contract permits arbitrary denial or pending. The reviewed bounded
consumer chooses `resolve`'s outcome for a resolved catalog proposal. Preserve
that exact behavior and its successful histories; always-deny or never-resolve
is not an adequate bounded replacement. This adds an experimental non-vacuity
obligation, not an eventual-service guarantee.

## Derivation: which boundaries carry meaning?

The synchronous machine currently collapses submission, evaluation against the
retained state, and register publication into one correctly timed rising-edge
step. Its settled outputs provide a whole-state observation. That implementation
supplies four semantic facts, but the edge itself does not appear in `G`, `E`,
`I`, current authority, or the continuity projection.

1. **A proposal denotes one effect.** `E(σ,q,σ′)` cannot preserve a submitted
   effect if the realization later changes `q`. Only the semantically relevant
   fields and their trustworthy origin must remain associated. There is no
   derived requirement to sample all inactive lanes or store a separate copy.
2. **Admission has a current coherent meaning.** Individually truthful reads
   can form a tuple that never existed. A tuple that did exist can also be
   obsolete. Coherence and currentness are different obligations; neither is
   established by a successful Boolean guard evaluated sometime earlier.
3. **The successor is whole in authoritative observations.** `I` does not
   identify the designated successor. `E` and proposal identity do. No
   authoritative intermediate or denied partial effect is permitted, even when
   it passes every state invariant.
4. **Local stories must agree.** Each interacting commitment must have one
   compatible position in a common acyclic history. Separate snapshots,
   pairwise agreement and an acceptable final state are insufficient. Completed
   relevant changes constrain later initiated requests. Unrelated commuting
   effects need no additional order.

These facts concern interpretation and observable transitions. They do not
require simultaneous physical bit switching, a duration, a frequency, or a
device that announces completion. Internal settling, speculative computation,
partial reception and partial candidate construction may all be invisible
steps. Whether they are actually invisible must be justified for every consumer
of authoritative meaning, including the next admission computation.

## Precise candidate minimal contract

### Definitions

Let `R_p(σ,q) = (σ′,o)` be the unchanged bounded oracle `resolve` in profile `p`,
where `o` is commit or deny. The full authoritative view remains the frozen
22-bit decoder's state, not merely `(x,y)` or the output invariant.

A realization declares its proposal interpretation `β`, its authoritative-state
abstraction `α`, and its observation interface. An observation interface includes
all reads or effects that consumers can treat as current state: internal guard
reads, accepted content reads, exposed state, and any completion/outcome report.
Raw candidate wires may be outside that interface only with an explicit trusted
non-use/qualification boundary. Naming them speculative does not establish one.

An **effective capture** means the point at which a whole offered envelope is
bound to an operation, if such a point exists. It may coincide with resolution.
An **authoritative publication** is the logical change of accepted meaning, not
necessarily a physical pulse or stored marker. Invocation, capture, preliminary
observation, publication, and reply need not be distinct physical events.
An operation starts with its invocation and remains unresolved until resolution;
any completion report must be later than that resolution. Executor death does
not end an already-bound operation's lifetime. An unsubmitted offer may disappear
without resolution, and a submitted operation may remain pending indefinitely.

For each finite execution prefix, use a history witness comprising resolved
operations, trustworthy proposal labels, relevant observations, and a common
acyclic precedence relation. The relation includes semantic dependencies and
completed-before-initiated edges between affected operations. A coherent cut is
a predecessor-closed portion of that history. A linear extension may be used to
compute a full `σ` for a cut; it is assurance notation, not a required execution
sequence or stored counter. Unordered effects must be compatible, including
their guards, invariants, whole effects and observed projections.

### B — Whole proposal interpretation

Every resolved operation has one whole proposal `q = β(envelope)` that was
actually offered through its trustworthy ingress boundary. All uses of its
effect, scope, evidence and reported outcome refer to that same semantic `q`.
It cannot be assembled from different proposals, silently retargeted after
capture, or paired with another lane's origin.

For the frozen interface, `β` is its existing exact-one-valid relation over the
selected protected lane and that lane's 11-bit payload. The selector, selected
payload and source association must describe one whole offered event. A
transient mixture is not a new caller proposal just because it decodes legally.
Inactive payload changes need no timing constraint. Zero/multiple selection is
idle under this interface; it is not an implicit batch or denial.

This requires semantic identity, not universal raw-bit immutability. A different
representation of the same proposal is permissible if the correspondence proves
it equivalent. If reception is incomplete or loses its source, it can remain
unsubmitted/pending without authoritative effect. A separate retained envelope,
handshake, buffering stage, or executor's continued presence is not forced.

The ingress contract must declare what constitutes a whole logical offer. It
can obtain that meaning from a trusted source/environment condition or capture
mediation; it cannot infer the sender's intended envelope from arbitrary changing
wires alone. A fully offered pair value 1 and W1's transient mixture can have
identical observed wire values. Accepting the former while excluding the latter
requires a trustworthy whole-offer distinction or a condition that excludes the
mixture at qualified capture. Rejecting every value-1 proposal loses the bounded
target. This residual framing/association premise is explicit; no particular
physical framing signal or protocol is prescribed.

### R — Compatible guarded whole history

There must be one compatible history witness for each execution prefix, extending
the interpretation of earlier authoritative observations. It satisfies all of:

**R1: Coherent current admission.** For each resolved operation there is one
coherent current `σ` at its position in that history such that its resolution is
`R_p(σ,q)`. The same view supplies guard dependencies, whole-effect evaluation,
and invariant dependencies. A preliminary observation may be older, but cannot
authorize publication if relevant intervening commitments make the resolution
incompatible. A completed relevant change precedes a later initiated affected
request. A commit point lies within that operation's lifetime; a reply, if
reported, cannot precede its claimed resolution.

Only relevant dependencies need be physically read together. Reads spread across
time are admissible if they have the same meaning as one such current view.
Unchanged or provably irrelevant components need no simultaneous sampling.
However, this is not permission to discard fields from `σ`: unwritten fields
and continuing information must still have their current whole-state meaning.

**R2: Whole authoritative publication and faithful observation.** A commit
changes accepted meaning exactly from that `σ` to `σ′`; a denial has no
authoritative effect attributable to its `q`. Pending, idle and internal steps
add no protected transition. Every authoritative observation, including a next
guard and a resolution report, must be consistent with a coherent cut of the
same history. Across a single isolated proposal, state observations therefore
show the old view or the whole successor, never a mixed intermediate. A report
of commit is bound to that `q` and its whole effect. It cannot be used to certify
an unfinished publication.

A read explicitly returning a historical snapshot can be truthful without
claiming currentness. It cannot serve as current admission evidence after an
incompatible change. A multi-field observation claiming one current view must
be coherent; separately declared reads at different cuts need not have equal
versions. Internal partial writes are allowed only while they cannot affect
authoritative observation or later admission. A failed or withheld response
does not reverse an already whole commitment.

**R3: Common order only where required.** The witness covers the entire
interacting set, including authority changes, work conflicts, and observations
that constrain their cuts. Every dependency is respected without cycles.
Overlapping affected operations can take either legal order. Independently
resolved proposals cannot be re-described as one composite effect to evade
their guards. Unrelated compatible operations have no stipulated mutual order.
They must still compose correctly: copying a stale full-state successor must
not erase another operation's effect.

The order is existential and may be discovered after a trace. No global clock,
global sequence number, runtime history log, or scheduling object follows.
Once an observation or completed-before-initiated edge rules out an ordering,
a later explanation cannot resurrect that ordering.

### Collapse result and conditional sufficiency

`B` and `R` are the compact contract. R1–R3 expose its review obligations; they
are not three independent Kernel mechanisms. Coherent validation and publication
collapse into one guarded transition relation. Common ordering is the
compatibility condition on those transitions, not an extra controller.
Defining R1 using a single already-serialized global state would make R3
automatic, but would assume more ordering than the semantics requires.

Conditionally, sufficiency follows by taking a linear extension of the common
acyclic dependency relation. Start with the trusted legal initial view. `B`
supplies each operation's actual `q`; R1 supplies its current resolution; R2
supplies exactly its successor or deny stutter. Invariant closure and the
unchanged oracle preserve the bounded semantics inductively. R3 allows the
local histories and observations to belong to that same execution. Compatible
unordered effects admit equivalent cuts without needing a physical global
sequence. Executor-only loss is a stutter unless an already-bound whole
proposal subsequently resolves through this relation; holder retention supplies
the existing continuity guarantee.

This argument assumes the mappings, dependency adequacy and observation
boundary are faithful. It does not prove a physical circuit enforces them.
Minimal means the weakest presently justified observable obligations for this
claim, modulo equivalent formulations and irrelevant representations. It does
not mean a uniquely minimal clause count, wire count, or physical substrate.

## Removal and collapse attacks

The following are small discriminating histories. Setup establishes work and
the named rights; unmentioned authoritative fields stay fixed. Counterexamples
are digital/abstract cuts, not claims about actual analog behavior of the frozen
circuit. They attack individual aspects of `B/R`, some of which logically
overlap after the collapse above.

### W1 — Remove whole-envelope capture

Use the ingress preflight's independent-profile state after grant `a0` with
rights 7 and replacement `a0→a1`: data `00`, current `a1` rights 7, state word
14385. On `a1`, the offered pair values are 0 (`00`) and 3 (`11`). Their
payloads are 9 and 201; their baseline proposal words are 16409 and 17945.
Sampling one value bit from each yields payload 73, word 16921: pair value 1.
The oracle commits data `10`, although no whole offered proposal requested it.

Two changing value bits suffice; one cannot form a third Boolean value from
two endpoints. Wellformed decoding, current rights, coherent admission, whole
publication and `I` all pass for the wrong proposal. A Boolean validity check
or independent bit synchronizers cannot replace whole-envelope association.

### W2 — Keep a payload whole but remove source association

After `a0→a1`, the stale `a0` offers `set x=1`; current `a1` offers `set x=0`.
Capture `a1`'s selection with `a0`'s intact payload. The resulting catalog
proposal is `set(a1,x,1)`, which commits `10`. The actual stale proposal must
deny and the actual current proposal can only keep `00`. Two lanes and one
payload distinction suffice. Protected access to lanes still holds; the attack
is an incorrect timing association inside selection/capture.

Thus proposal fields and the ingress discriminator cannot be captured as
unrelated facts. They collapse into `B`; a new dynamic classifier is not needed.

### W3 — Remove coherent observation, retain truthful components

In the independent profile grant `a0` the `x` right and `a3` the content right,
with content 0. Revoke `a0`; then `a3` accepts content 1. For the proposed
`resume(a0,1)`, the actual `(eligible-for-x,content)` views are:

```text
(1,0) --revoke a0--> (0,0) --accept 1 on a3--> (0,1)
```

The resume guard fails at all three cuts. Reading eligibility from the first
and content from the last fabricates `(1,1)` and admits `x=1`. The fabricated
full tuple can still satisfy the state invariant. These are existing catalog
operations, not an added policy. Two guard facts and three cuts suffice to
show that individually true observations need not form one true view.

### W4 — Keep a coherent snapshot, remove currentness at publication

Grant `a0` the `x` right. Cache that coherent view. Complete and acknowledge
replacement `a0→a1`, then initiate old `set(a0,x,1)`. Detached validation against
the cache commits; current `resolve` denies. One relevant authority change and
one affected request suffice. No torn bits or malformed evidence are needed.

If the old request overlaps replacement, old-before-replacement can be legal.
The counterexample deliberately includes completed-before-initiated precedence
so that explanation is unavailable. Removing that precedence edge admits the
invalid explanation `old-write < replacement`; overlap alone does not falsify
it. Thus coherence cannot absorb freshness, and ordering must retain this edge.

### W5 — Remove joint current guard/effect consistency

In the coupled profile, data is `00` and `a0` has both field rights. Independently
validate `X: set x=1` and `Y: set y=1` against `00`; each isolated successor
passes `x+y≤1`. Publish X, then apply Y's stale authorized field update. Data
becomes `11`, violating `I`. The reverse order fails symmetrically. Two proposals
and two constrained fields suffice. Neither commit may rely on the detached
old guard once the other commitment changes its invariant dependencies.

For comparison, the **independent** profile permits both changes without a
semantic X/Y ordering requirement, and either serial explanation yields `11`.
If both compute complete old-view images `10` and `01`, then wholesale
publication of `01` after `10` loses X. Every image satisfies `I`, but neither
order of the two declared effects explains the final `01`. This demonstrates
why weakening snapshot synchronization does not authorize stale overwrites of
unwritten fields. The obligation is effect preservation, not ordering otherwise
compatible changes.

### W6 — Remove whole publication, retain invariant checks

At W1's independent-profile state, propose the single pair value 3. Its whole
successor is `11`; exposing `10` after only x changes satisfies `I` but is
neither endpoint of this proposal. Two changed bits and one intermediate
observation suffice. Making the next admission read `10` is already a violation,
even if no outside caller sees it and even if the final publication later reaches
`11`. Calling that intermediate a separate `set` invents an unoffered proposal.

The same failure applies to partial authority replacement or cascaded rights
updates, but those larger examples are unnecessary to establish this condition.
No physical simultaneity is inferred: the partial encoding may exist internally
provided the authoritative observation boundary excludes it in fact.

### W7 — Collapse deny into partially applied work

At data `00`, a worker with the `x` right submits the catalog mixed proposal:
permitted `x=1` plus an unauthorized authority grant. The oracle denies the
whole proposal and retains `00`. Publishing just `x=1` while reporting deny
produces invariant-valid `10`. One request with two subeffects suffices.
Commit-only checking cannot establish the contract; denial and pending paths
must not release partial accepted meaning.

A related timing collapse is to report commit while the next current-state
observation still shows an incomplete successor. For a smallest example, report
completed `set x=1` from `x=0`, then begin a current read that still reports `x=0`
with no intervening change. One changed bit, one completion report and one later
read suffice. The result cannot simultaneously mean whole completion and merely
permission to start changing fields. Response loss is allowed; a false
whole-completion claim is not. Likewise a pending pair that exposes `10` without
any committed proposal cannot explain that authoritative change.

### W8 — Replace common acyclic history with pairwise consistency

Use the **already-governing separate three-bit order fixture**, not an extension
of the 22-bit RTL proposal alphabet. Starting at `000`:

```text
A: require y=0; write x=1     requires A<B
B: require z=0; write y=1     requires B<C
C: require x=0; write z=1     requires C<A
```

Each isolated operation and each pair has a valid order. All three can publish
whole local effects and reach invariant-valid `111` using their old coherent
observations. No common order exists. Three operations are the minimum needed
for pairwise consistency to miss a cycle. This fixture distinguishes history
compatibility from local guard checks; it adds no general concurrency service.

The frozen history audit enumerates 4,096 cases: 1,712 admit a common order,
2,384 do not, and a pairwise checker has eight false positives. Requiring just
pairwise interlocks or independent local clocks does not discharge R3. Conversely,
a central scheduler is only one possible enforcement mechanism; the fixture
forces compatibility, not its physical location or algorithm.

### Necessity coverage and further collapses

| Retained aspect | Small witness | Weakening that fails / successful collapse |
| --- | --- | --- |
| Whole offered effect | W1 | Legal decoding of a mixed word is insufficient; capture and semantic effect identity can share one boundary. |
| Whole origin/effect binding | W2 | Whole payload alone is insufficient; selected origin belongs in the same interpretation. |
| Coherent validity observation | W3 | Truth of individual components is insufficient; a physical simultaneous full-state read is stronger than necessary. |
| Currentness and relevant real-time precedence | W4 | A coherent old view or a reordered completed replacement is insufficient; only relevant predecessor meaning must be current. |
| Guard/effect/invariant dependency agreement | W5 | Detached valid decisions or stale complete images are insufficient; one guarded transition subsumes separate check/update stages. |
| Whole authoritative successor and observation | W6 | `I` and eventual final equality are insufficient; internal candidate stages need no authoritative interpretation. |
| No effect on denial/pending; truthful resolution | W7 | Successful-path checks are insufficient; lost replies need no retry or exactly-once machinery. |
| One common compatible history | W8 | Pairwise stories are insufficient; this is a property of transitions, not an added ordering primitive. |

`B` can be folded into `R` by making whole trustworthy `q` part of each history
label. R1–R3 can likewise be written as observational refinement to the governing
transition system. These are equivalent collapses, not further eliminations of
their meaning. There is no argument for separately retained capture, observation,
decision and publication clocks or devices.

## Synchronous properties that are unnecessary

| Present or tempting mechanism/property | Removal assessment |
| --- | --- |
| Periodic edges, a frequency, duty cycle or fixed latency | No guard or effect depends on elapsed time. Arbitrary delay/pause and irregular advancement preserve safety when `B/R` hold. A stopped implementation alone would fail experimental non-vacuity. |
| Common physical edge for request, guard, effect and response | Logical consistency is sufficient. Stages may be separate or collapsed; intervening dependencies must remain compatible. |
| Physically simultaneous switching of all 22 state bits | Not claimed by the baseline and not derived here. Only authoritative observations must be whole. |
| Stability of every input and state bit for a universal interval | Only meaning used by an operation must be faithfully associated; inactive lanes and irrelevant facts need no such interval. Actual devices may need setup/hold or other constraints. |
| A global total order, common wall time or stored sequence | Only affected commitments and their observations need a common acyclic order. Independent x/y updates in the independent profile are a positive commutation witness. |
| One operation per edge, bounded response time, fairness | Throughput and progress are outside the semantic claim. Pending can remain pending. |
| Per-source acknowledgement, exactly-once acceptance | The frozen interface has shared outcome signals. A held valid signal may denote repeated offered events at distinct capture boundaries; replay of an authorized flip can commit twice. Whole capture does not imply deduplication. |
| Handshake, completion detector, asynchronous protocol | None follows from W1–W8. Each is a candidate way to realize qualification; each requires its own timing and observation argument. A signal named ready/done supplies no proof. |
| Scheduler, controller, arbiter, lock or processor | No witness requires one. The frozen interface can leave collisions unsubmitted indefinitely. General programmability is not introduced. |

No clockless correctness claim is made for the frozen RTL with its clock simply
removed. Its registers still require correctly timed edges and settled
observations. Its edge/SAT and synthesis proofs do not quantify over bit arrival
times, output skew, asynchronous consumers or metastability. They cannot be
reinterpreted as a proof of `B/R` for a different realization.

## Residual assumptions and their classification

| Item | Classification and residual obligation |
| --- | --- |
| Whole proposal, current guard/effect, whole outcome, compatible history | Semantic/refinement obligations `B/R`; not facts established merely by assuming atomic oracle steps. |
| 148 templates, three profiles, four contexts, 22-bit encoding, fixed lanes and collision idle | Bounded consumer/interface or realization choices. Preserve them for this comparison; no universal minimality follows. |
| Protected non-confusable lanes, trusted manager origin, no silent rebinding | Physical/trust premise retained from ingress reduction. Timing qualification must not mix a protected discriminator with another proposal. |
| Whole-offer interpretation at capture | Residual ingress/timing trust: sources or trusted mediation supply meaningful envelope boundaries. Arbitrary raw wire levels cannot reveal whether a legal word is a whole offer or a transient mixture. |
| Faithful observation qualification and sole guarded path | Residual realization premise: every consumer of accepted meaning and every later guard obeys `α/β`. No unchecked intermediate or other writer changes accepted meaning. Qualification/mediation remains inside the assurance boundary wherever located. |
| Integrity of law, wiring, initialization and policy configuration | Physical/trust premise. Requests cannot alter the fixed law, write authoritative state or invoke reset. Reset is initialization only, not an executor-loss event. |
| Retained holder and accepted content survive executor loss | Existing failure/trust boundary. Power, reset/configuration and retained-state integrity survive; indefinite replacement and holder failure are excluded. Timing reduction does not remove retention. |
| Valid digital meaning at qualified observations | Physical refinement premise. A deployment must explain how unresolved/metastable inputs, hazards, skew and delays cannot be mistaken for completed authoritative meaning. No universal settling duration, delay bound, eventual metastability resolution, or detector correctness is assumed in this candidate. Any selected mechanism must declare its actual physical assumptions. |
| Accurate dependency supports and abstraction | Verification/model-adequacy premise. Omitting authority, issued bits, cascading parent rights, content or observation edges can make a false local proof pass. Ghost information cannot enforce the realization. |
| Oracle, codecs, checkers, event exploration, SAT/synthesis and logs | Assurance apparatus. Correctness and adequate modeling remain trusted for evidence; none may provide runtime origin, currentness, completion or arbitration. |

This moves trust from an unspecified global synchronous envelope to explicit
whole-event and authoritative-observation refinement obligations. It does not
show that every physical realization has a smaller trusted boundary. For a
clocked deployment, clock integrity, setup/hold and qualified output timing
remain its mechanism-specific way of satisfying those obligations. A different
deployment might exchange them for delay, encoding, isolation or completion
assumptions. No such exchange is selected without evidence.

## Bounded follow-up experiment design

### Question and entry gate

Can a model of independently ordered reception, reads, candidate changes and
observations satisfy exactly `B/R`, preserve the frozen catalog outcomes, and
admit all required successful histories without relying on a common periodic
edge? Alternatively, does a smallest counterexample expose a missing observable
condition or an assumption hidden in the observation boundary?

Independent contract review is the entry gate. Review must challenge the
interpretation mappings, currentness versus coherence, whether irrelevant state
has really been removed from physical synchronization, observation closure,
and the `B/R` collapse. This document does not claim that review has occurred.
The follow-up is a finite observation-refinement experiment, not a replacement
hardware build or a general concurrency architecture.

### Fixed domain and apparatus

1. Pin the future run to its experiment commit and record the baseline and
   synthesis refs above. Verify source hashes against the baseline before and
   after the run. Write all new harness/results outside `direct-rtl/` and
   `ingress-reduction/`; never overwrite frozen evidence.
2. Reuse the unchanged oracle, legal-state enumeration, codecs and profile
   constants. Cover all 2,472,636 legal-state/authentic-catalog combinations for
   isolated completed resolutions. Keep raw-word RTL-interface tests separate.
3. Add a finite **event/cut model**, not an RTL replacement. Its alphabet
   distinguishes invocation/withdrawal, individual envelope arrivals or changes,
   semantic capture, component reads, speculative decision, candidate component
   writes, authoritative observations/publication, outcome observation/loss and
   executor loss. These labels may coincide in some histories; no global tick,
   physical time or fairness is supplied.
4. Use a maximum of two in-flight catalog proposals in the listed race fixtures,
   and three only in the inherited order fixture. Data/content stay Boolean,
   contexts stay at four, and loss affects executor-only information. No external
   facts, holder restart, persistent writes or protected sinks are added.
5. Define `α`, `β` and observation qualification independently from the driver.
   The driver must permit mixed capture, stale reads, partial writes and
   premature outcome observations. The monitor extracts actual offered and
   observed values, then checks `B/R` against the oracle/history witness. It
   must not manufacture a complete envelope, current snapshot or successor
   merely because the driver labeled an event capture/commit/done.

### Cheapest discriminators and bounded exploration

Run W1–W8 first. Enumerate the two pair payload endpoints and all four choices
of their two changed value bits; the correct reference interpretation must
exclude both mixed proposals as captures of either endpoint. Enumerate W3's
nine pairs of component cuts; only the fabricated `(1,1)` admits the impossible
resume. Enumerate both orders of W4/W5, W6's changed-bit subsets, W7's partial
subeffect cuts and the 4,096 existing history cases. These tests discriminate
the premise before expensive exhaustive correspondence work.

For whole publication, enumerate **all subsets of changed authoritative bits**
between each legal catalog input and its oracle successor, quotienting duplicate
cuts. Include the outcome report before/at/after completion and next-guard
observation at each cut. Endpoints and invariant-valid intermediate images must
be checked against `E`, not just `I`. This is a bounded encoding-cut audit; it
does not model all gate delays or prove a physical qualifier.

The frozen encoding gives a useful analytic bound: a replacement changes at
most three old-right bits, three new-right bits, one issued bit, three cascading
child-right bits and two parent bits, hence at most 12 bits. Other catalog
effects change no more. Verify that bound during enumeration before allocating
cut vectors; each completed input has at most 4,096 distinct subset cuts. Keep
counts and quotienting explicit rather than silently sampling those cuts.

For interacting timing, explore these named fixtures to finite closure:
replacement versus old write in both orders; completed replacement before old
invocation; content/right torn resume; coupled x/y writes; independent x/y
updates including stale full-state overwrite; exclusive grants; delegation
versus parent restriction; whole pair; denied mixed effect; and executor loss
before capture, after preliminary validation, around candidate/publication and
before reply. Test repeated authorized flip after a lost reply, retaining its
permitted second commitment. Avoid an unbounded product of general requests.

Quotient internal repetitions only when future proposal, authority, publication
and observation possibilities are identical. Canonical state includes retained
proposal meaning, local observations, phase, outcome knowledge and relevant
precedence edges. A work/depth/time limit is not closure: on reaching one, record
INCOMPLETE and stop without a safety claim.

Use initial laboratory ceilings of 30 minutes and 1 GiB memory per profile's
correspondence/cut stage, and one million canonical states per race fixture.
Exceeding a ceiling is a tractability obstruction with retained counts and
frontier, not a semantic counterexample. Adjusting a ceiling requires an explicit
revised run record; never convert the ceiling into a bound on allowed histories.

A separate monitor searches for one whole-set order/cut explanation, checking
each operation and each authoritative observation. Cross-check it with an
independent dependency/cycle algorithm on the inherited fixture. Do not pre-sort
events into a global commit order and then cite that sorted schedule as proof
that cycles were excluded. Do not silently omit deny, idle or pending effects
from the observation audit.

### Positive witnesses and sensitivity

Required successful histories include establishment; grants; x/y changes;
content acceptance and content-consuming continuation after executor loss;
`a0→a1→a2` replacement with old-lane denial and current continuation; allowed
delegation; independent compatible changes; whole pair; and lost-response replay.
Preserve the frozen collision-idle and reset-initialization behavior. Partial
reception/candidate changes can leave the view unchanged indefinitely.

Exhibit at least one positive trace with staggered capture/read/candidate events
and one with compatible operations whose event stages interleave. They must
have no common sampling/publication clock and still extract a valid `B/R`
history. This establishes a contract-level witness only: the qualification
profile is a declared assumption being audited, not physical enforcement proven
by the model. Internal stages must remain visible to the checker so exclusion
of intermediate meaning can be inspected.

Mutation checks must detect: mixed payload; source/payload mismatch; mutable
captured proposal; torn guard view; coherent-but-stale admission; lost independent
update; partial successor; denied partial effect; early/mismatched completion;
pairwise-only order; omitted completed-before-initiated edge; and always-idle or
always-deny. A tool crash or an assumed atomic transition is not a detected
mutant. Save the shortest failing event trace, concrete words, decoded endpoints,
offered proposals, observations and missing order/cut witness.

### Success and stopping conditions

**Contract-level success requires all of:**

- Independent review finds no unresolved missing condition or hidden global
  timing premise in `B/R` and its sufficiency argument.
- Exact isolated correspondence passes in all three profiles on all legal
  states and 148 authentic proposals, with no raw-domain claim inflation.
- The cut/fixture searches reach the declared finite closure. Every accepted
  authoritative trace has an independently checked whole-history witness;
  every targeted removal produces its expected smallest counterexample.
- All named successful histories and staggered/interleaved witnesses exist;
  neither progress nor exactly-once behavior is used to exclude bad histories.
- Every listed mutant is detected for the intended reason; manifests confirm
  frozen sources/evidence unchanged. Assumptions and observation qualification
  are reported as such.

Then stop and report a **bounded observational timing reduction**, conditional
on the faithful `α/β` and qualified-observation boundary. Do not report a
fabricated clockless realization, timing closure, metastability safety or a
universal asynchronous theorem. Choosing/building a physical mechanism is a
separate review gate after this result.

**Stop as falsified or incomplete when:** a trace satisfies the proposed
conditions but has no legal catalog/history explanation; a required positive
history cannot be represented; a removed condition is secretly reintroduced by
driver/monitor; a mutant is missed; hashes change; or exploration/verification
does not complete. Preserve the smallest obstruction and identify which
condition, mapping, bound or physical premise it attacks. Propose only the
weakest repair justified by that obstruction. Do not add a clock, handshake,
controller, liveness assumption, broader failure profile or wider concurrency
architecture merely to force success.

## Evidence from this design step

Focused read-only checks used the frozen `preflight.witnesses()`, catalog oracle
and codecs to verify W1/W6's exact words and invariant-valid torn image; W2's
denied old proposal versus synthesized current proposal; W3's three real guard
views and accepted fabricated tuple; W4's old/current outcomes; W5's coupled
exclusion and independent commutation/lost update; and W7's whole denial.
`history_attacks()` reproduced W8's 4,096-case counts and the real-time order
obstruction. The final focused check passed. An initial reporting snippet used
the wrong key for the history counts; it was corrected and rerun. No oracle,
stored evidence or realization was changed.

Those checks confirm the named witnesses in the frozen bounded target; they
are not execution of the proposed event/cut harness, a baseline suite rerun,
independent review or asynchronous physical verification.

**WHY:** whole proposal identity, coherent current guarded meaning, whole
authoritative publication and compatible interacting history each exclude a
small concrete false-success path; no such path forces a periodic/common clock
or a particular completion mechanism. **WHAT:** the pinned semantics and review
synthesis, existing ingress cut witnesses, focused frozen-oracle checks and the
inherited whole-history audit. **HOW CERTAIN:** evidence-based necessity and a
conditional semantic sufficiency argument; proposed minimum observable contract,
not a proof of physical minimality. **WHAT-NOT-TESTED:** independent review of
this contract; the new event/cut harness and exhaustive cut counts; replacement
circuit or physical observation qualification; analog timing, delays, hazards,
metastability or skew; hostile reset/state faults; holder failure/persistence;
protected outside effects; arbitrary asynchronous transports or lane rebinding;
unbounded contexts/concurrency; progress and exactly-once service.
