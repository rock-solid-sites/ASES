---
title: Phase I Processorless Core Falsification
program: EDASES
layer: Architecture
document_type: Design and Reasoning Record
status: Draft
authority: Derived
canonical_repository: edases
crosslink_issue: 571
baseline_commit: 4e800957a673c8bd07eeea3c3c909349cdae76ac
depends_on:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - EDASES Work Unit Component Design
  - EDASES Execution Engine Roadmap
  - EDASES Currentness and Recovery Assurance
consumed_by:
  - EDASES Phase I Core Substrate Closure
  - Phase I architectural closure review
related_documents:
  - Work Unit-0 Foundational Reduction
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-28
---

# Try to force a Processor into the correctness core

## Meaning of the claim and how it could fail

The [roadmap](../EDASES-Execution-Engine-Roadmap.md) asks whether Kernel + Work Unit
and their necessary realization/recovery/execution mechanisms suffice without a
persistent first-class Processor. Here that means no independent durable derived
state that governs permission or continuation, and no persistent computation
lifecycle needed in addition to the retained authoritative view. It does **not**
mean a guard without arithmetic, traversal, decoding or other computation.

A counterexample must identify an existing required observation or successful
history, remove Processor, and show why neither recomputation/verification from
retained inputs nor preservation of required information as ordinary accepted
state can meet it. Calling arbitrary new machinery Kernel would not be a valid
reduction. The comparator below therefore fixes the policy's actual computation
and bounds rather than hiding a generic derivation engine inside an unspecified G.

These are constructed histories and a conditional simulation argument, not new
model-checker output or independent review. Existing counterexamples are linked
through the [closure record](./Phase-I-Closure.md). No broad prior-art survey is
needed: the discriminating questions here concern the information and authority
requirements of the supplied contracts, not competing products.

## The non-vacuous comparator

Use finite bounded records for Work Units, their current single-parent forest,
explicit management and action grants, restrictions, supported resource quantities,
and retained accepted contents. A trusted admission operation can inspect this
complete current state and perform these total, bounded checks:

- object existence, identity/scope and current ingress relationship;
- explicit local permission and restrictions on the entire actual containment path;
- management permission distinct from being parent or creator;
- absence of cycles, missing parents, unaccounted dependents or forbidden exposures;
- capacity conservation using defined arithmetic without overflow/wraparound;
- exact accepted content/evidence applicability and retained-content availability;
- whole declared effect and resulting invariants; sealed recovery and no widening
  of latent permissions on a move.

The supported effect vocabulary is create empty object, grant/restrict/revoke,
accept protected content, replace an authorized ingress, seal, recover cold,
move a sealed child while preserving/reducing restrictions, explicitly activate,
dispose content, and remove a boundary only after safe disposition. A selected
external attachment adds only its declared effect/outcome contract. A shell,
policy-language interpreter, arbitrary theorem prover, AST system, scheduler,
general dependency engine and derivation queue are not required by this comparator.

The policy evaluates only supported finite descriptions. It may reject an
unrepresentable restriction before activation. If a future mandatory consumer
needs more, its counterexample must state why the finite comparator no longer
satisfies an accepted requirement. Arbitrary program analysis or semantic truth
is not silently promised by a Work Unit boundary.

This permits useful paths: grant, accept x, replace, read x and accept y; recover
x that was accepted before engine loss; move a restricted sealed child and later
successfully read while denied write; disposition children across bounded commits
and remove the empty parent. No independently persistent derivation is needed to
determine these transitions. Adequate testing must execute these paths, including
successful continuation after actual loss, rather than merely show deny-all safety.

## A conditional elimination argument

Suppose a proposed persistent derived value D is completely determined by retained
input B and specified interpretation P: D = f(B,P). Require:

1. B includes every relevant positive, negative, historical, configuration and
   observation dependency, and survives the promised failures with a current cut.
2. f terminates on the supported finite domain; its result is correctly computed
   or soundly checked; no required timing bound is lost by recomputation.
3. Replacing the stored D with f(B,P) changes no required future observation,
   including consumer audit/provenance and continuation observations.
4. Admission binds the calculation to the inputs/policy current for that effect;
   concrete computation itself introduces no unaccounted protected effect.

Relate the design with D to the comparator by equal B/P and equal required
observations. Recomputing D changes no authoritative state and can be a stuttering
step. A committed transition has the same guard result and whole effect. On a
covered failure, the comparator recovers B/P and recomputes; it does not need to
recover a computation lifecycle. Thus retained D adds no correctness distinction
under these premises. This is a proof sketch conditional on a total f and an
adequate observation relation, not a machine-checked refinement theorem.

If a premise fails, identify the missing guarantee. Do not conclude "Processor"
from the failure alone. Irreplaceable observations, accepted historical choices,
committed external effects or required output bytes are already authoritative
information; dropping them is not legitimate derivation elimination. Conversely,
renaming a complex independently evolving derived state machine "ordinary data"
without eliminating its necessary behavior would not establish this argument.

## Falsification attempts

| ID | Hostile history and failed simpler design | Smallest repair, and why it does or does not force Processor |
| --- | --- | --- |
| P1 — a guard necessarily computes | The child has a grant; an ancestor lacks it. Trust an external worker's claim that effective permission holds. The child acts illegally. | Trusted path evaluation or sound proof verification is necessary. This refutes **all guard derivation may be untrusted/external**. The finite computation above has no independent persistent derivation state or lifecycle. The roadmap hypothesis survives, but only in this qualified form. |
| P2 — stale positive result | Compute allowed=true, revoke an ancestor, then submit the old authentic derivation. | Recompute against the current path, or check sound applicability at commitment. Durable invalidation machinery is unnecessary; without current validation it would also be insufficient. |
| P3 — missing dependency/negative fact | Derive no children from a supplied graph omitting C; destroy its parent. | Establish completeness of the queried authoritative domain. Enumerating the actual finite forest in one coherent view suffices. A signed dependency list or proof of every included edge does not prove absence. |
| P4 — phantom after correct enumeration | Enumerate all children, find none, then create C before final removal. | Couple validation and commitment, or revalidate the complete relevant domain at commitment. This is Kernel ordering, not a need for a persistent dependency graph. The same attack applies to an up-to-date cache after its last read. |
| P5 — restart loses invalidation | Save derived readiness, withdraw evidence, crash, reload the saved readiness. | Recover the current withdrawal/selection facts with authoritative state and recompute. If both source and invalidation knowledge rolled back, a Processor inside the same failure domain has no additional information. A surviving discriminating authority fact is recovery trust, not derivation power. |
| P6 — inputs cannot be retained | An external measurement can be read only once; its derived result controls later action; the measurement disappears at crash. | Preserve the accepted observation, a sufficient trustworthy result/witness, or required resulting decision before promising continuity. These are irrecoverable information under Kernel continuity, regardless of which component stores them. Merely rerunning f is invalid. No separately authoritative computation lifecycle is demonstrated. |
| P7 — “deterministic” but environment-dependent | f(x) uses a changed tool version, locale, clock, random seed or external service; replay differs. | Either those dependencies and interpretation are included in B/P, or the outcome is an accepted observation/choice rather than a pure derived fact. Exact replay is not assumed. Keeping just the name of a deleted tool/version is not enough. |
| P8 — history-sensitive derivation | Two identical present inputs have different correct results because a review was previously withdrawn or a stream accumulated different events. | Present inputs were an insufficient authoritative view. Retain the required historical fact or an adequate folded state with evidence required by the consumer. Folding can occur in an ordinary guarded update. A separately scheduled Processor is not required. |
| P9 — accepted output, no reconstructible inputs | A result was accepted and must remain readable, but the source has since been legitimately disposed of. Recompute-only recovery loses it. | The result is now required accepted content. Retain it as such; do not call accepted work a cache to evade continuity. This is a necessary durable value, not evidence that its producer must remain a first-class subsystem. |
| P10 — interrupted multi-step derivation | Half a graph is built when the executor dies; publishing its partial result permits an invalid transition. | Leave all unfinished computation candidate/private; publish only a complete checked result through a whole commitment. Restart from retained inputs. If intermediate states themselves are promised outcomes, accept each under its own defined policy. A durable computation checkpoint is otherwise an efficiency choice. |
| P11 — expensive derivation before a deadline | Recomputing takes longer than a hypothetical safety deadline; a saved derived state would meet it. | This could force persistent computation state under a genuine correctness deadline and resource lower bound. No such deadline or compulsory algorithm occurs in the Phase I contract. Latency preference does not falsify it. Obtain the precise timing requirement before changing the core. |
| P12 — proof verification is harder than computing | An arbitrary semantic claim has no available sound, tractable proof checker. | The core cannot promise that truth merely by accepting a worker's certificate. It can compute a supported guard, use a specifically trusted attestor for a scoped fact, accept an authorized judgment **as a judgment**, or refuse the unsupported claim. No existing Work Unit property requires deciding arbitrary program truth. A generic Processor would not create that guarantee by being persistent. |
| P13 — external outcome is unknown | Sink accepts, reply vanishes, executor dies; replacement must decide whether to retry. | H10's sink observation/deduplication or weaker contract is needed. A deterministic local derivation cannot recover information absent from all local observations. Persistent Processor state cannot encode a fact it never observed. |
| P14 — aggregate resource safety | Two children each derive enough remaining capacity from the same old total and both allocate. | Evaluate conserved quantities in the coherent commitment, recomputing totals from allocations if necessary. No persistent aggregate is forced. Actual usage metering, if part of a stronger promise, requires trusted measurement and its history; it is not supplied by a cached total. |
| P15 — recovering a computed containment path | Cached paths disagree with current parentage after a coupled move; restart chooses a cached permissive path. | Reconstruct from the current authoritative parent relation and complete restrictions. If parentage itself is lost or split, neither cached paths nor a Processor prove a valid whole cut. Recovery and structural-transition obligations remain. |

### Follow-through on the strongest candidates

**P1 cannot be dismissed by saying “derive externally.”** Arithmetic and traversal
that determine a guard are correctness mechanisms. A system accepting an arbitrary
boolean from an untrusted agent fails. The proper boundary includes the evaluator
or the sound verifier, with its actual inputs, interpretation and implementation
assumptions. This is a necessary trusted deterministic calculation, and must appear
in the TCB and tests. It is already demanded by G, not evidence for an independent
persistent derivation layer. If “Processorless” were intended to exclude *any*
trusted deterministic machinery, that stronger hypothesis is falsified by P1.

**P6/P8/P9 prevent a tautological recomputation claim.** A source reading, historical
choice, accepted output or outcome affecting future permission cannot be discarded
just because someone calls it derivable. The elimination test applies only when
retained information is sufficient for every promised future observation. A folded
state can be smaller than full history, but must retain separately required audit
meaning. If the only correct fold requires persistent state, store it within the
ordinary authoritative transition; then separately test whether its computation
requires a new independent lifecycle. The histories above require data retention,
not that lifecycle. A builder must not invent an autonomous derivation subsystem
as the default representation of this obligation.

**P3/P4 require more than input hashes.** “There are no children” and “all applicable
boundaries admit” quantify over a complete domain. Hashing the submitted subset
only authenticates that subset. The first comparator scans its own current finite
state. A later optimization must prove equivalent completeness and ordering; it
cannot make its index the authority merely by giving it a version number.

**P11 is a legitimate reopening condition.** Suppose an accepted requirement says
an emergency safety action must complete within T after recovery, and a defensible
lower bound shows no recomputation from retained inputs can meet T. Durable
precomputation may then be necessary to correctness. Whether that also needs a
first-class Processor rather than a retained value and bounded guard is a further
question. Phase I contains neither the deadline nor the lower bound. No performance
experiment is justified until there is a concrete required workload and deadline.

## Removal after the attacks

Remove a Processor process, work queue, cache, dependency graph, invalidation
stream, incremental computation state, deterministic tool registry, and scheduler.
Retain the finite authoritative policy state and its trusted evaluator, complete
input/policy binding, accepted contents/observations, concrete mediation and the
selected current recovery cut. Every required comparator history remains
expressible. Lost speculative computation is recomputed or replaced; accepted
information is not erased.

Now also remove the evaluator/verifier, complete inputs, interpretation, or retained
accepted results. P1, P3, P7 or P9 respectively fail a required claim. Those are the
surviving correctness obligations. None introduces a Kernel object type beyond
its existing parameters; none makes a separate Processor lifecycle necessary.

**Result:** the stated persistent-Processor hypothesis survives these fifteen
attacks for the comparator. The unrestricted claim “no trusted derivation” fails.
The conditional elimination argument removes architectural discretion to add
persistent derivation machinery for convenience, but does not pre-prove every
future consumer reducible.

**WHY:** each failed weak design has a stated, smaller repair and non-vacuous
histories without independent derivation state; the strongest contrary reading
has an explicit counterexample. **WHAT:** P1–P15, the fixed comparator, conditional
elimination argument, Kernel semantics and Work Unit A–L. **HOW CERTAIN:**
evidence-based scoped sufficiency; conditional proof sketch, not exhaustive proof
or independent cross-family agreement. **WHAT-NOT-TESTED:** finite model product,
implementation refinement, arbitrary guard languages, deadlines, semantic truth,
resource lower bounds, and independent adversarial review.
