---
title: Kernel-0 Realization Conformance Review
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
  - Kernel-0-Realization-Experiment.md
consumed_by:
  - Further Kernel-0 assurance experiments
---

# Kernel-0 Realization Conformance Review

## Method and scope

This is the operator-approved, in-session adaptation of the installed
`spec-to-code-compliance` skill. The skill's separate-agent workflow was absent;
this review is **not independent of the implementation author**. It was performed
after ordinary and generated tests passed, followed by a correspondence attack
that corrected misleading mutation tests. No absent workflow or independent
refutation run is claimed.

The specifications are [Abstract Semantics](./Kernel-0-Abstract-Semantics.md)
(all sections) and [Verification Obligations](./Kernel-0-Verification-Obligations.md)
(all sections), interpreted through the explicitly finite experiment contract.
All 233 lines of [the service](./kernel0_service.py) were read. There is one
ingress handler and one guarded resolver, no inherited implementation/framework
routes, and no imported model code. The test adapter, callers, process bootstrap,
and whole-history checker were also read. Line references below refer to that
service unless another filename is named.

## Requirement review

### R1 — Complete authoritative view

> “all distinctions whose current meaning determines accepted work, current permission, or a critical invariant”
> — Abstract Semantics, Parameters and meaning

**Classification: concretely enforced within the finite profile; trusted initial
configuration. Verdict: implemented, conditional on declared bootstrap trust.**
`View` (22–30) contains work, content, issuance, rights and parents. Fixed position
interpretation (18) and `Boundary.profile` (170–174) supply the remaining policy
distinctions. Endpoint association (221–224) supplies authentic request context;
it is part of the trusted concrete boundary, not a caller assertion. The cycle
tuple remains zero in the three main profiles; it is explicitly included in the
separate three-bit fixture. Paths: bootstrap → handler → decode → resolver →
candidate/valid. No admission cache, time, external fact, URL, file or remote
store was found. The abstraction does not omit any inspected admission input.

### R2 — Initial state and management origin

> “For an initial state, `I(σ₀)` holds.”
> — Abstract Semantics, Resolved transition relation

**Classification: concretely enforced initial values; trusted management source.
Verdict: implemented under assumption.** Defaults (22–30, 173) map exactly to
`State()`. The initial-state branch of `valid` is 79–80. Establishment requires
context `-1` and absent work (104–107). The trusted supervisor supplies the initial
management endpoint; its legitimacy is an assumption, not something `-1` proves.
Root management revocation is excluded by the finite profile.

### R3 — Current authority and guarded authority changes

> “A request ordered after invalidation cannot commit using only the invalidated authority.”
> — Verification Obligations, Model invariants 2

**Classification: concretely enforced, with trusted endpoint isolation.
Verdict: implemented.** Management restrictions are checked at 123, 135 and 139;
delegation uses current parent rights at 131. Work requires current rights at
147–150. These checks execute inside the resolver lock (177–184), not on an
earlier observation. The only handler calls that resolver with its bootstrap
context (214); JSON has no evidence/identity override (56–57). Stale-read gates,
later-started requests, worker attempts to grant, and forged fields exercise
these paths. Possession of a genuinely current transferred handle remains valid;
physical-producer exclusion is not claimed.

### R4 — Fresh, non-confusable replacement

> “Old authority evidence must not become valid again merely because a representation is reused while old attempts remain possible.”
> — Abstract Semantics, Authority and order

**Classification: concretely enforced finite no-reuse; trusted non-theft of
handles. Verdict: implemented.** The issued bit is checked before grant,
delegation and replacement (127–129), and updated only in the tentative successor
(144–145). Revocation does not clear it. Replacement checks the same position,
withdraws dependent authority, and installs a fresh context (139–145). No handler
rebinding exists. Old/replacement executors using the same local descriptor label
`64` and identical JSON receive different outcomes because their connected
endpoints differ. Exhausting the four contexts denies further grants; indefinite
freshness is not established.

### R5 — Whole current-view effect and denial stutter

> “A proposed effect cannot silently become a different or partial authoritative effect.”
> — Abstract Semantics, Resolved transition relation

**Classification: concretely enforced, conditional on runtime/lock integrity.
Verdict: implemented.** Frames are decoded to a frozen scalar proposal (33–38,
50–75). Candidate changes use private lists and a new frozen `View` (109–166).
The lock covers candidate computation, invariant checking and the sole protected
assignment (177–185). Every denial branch retains `self.state`; mixed requests
return no candidate (151–152). Reads serialize copies under the same lock.
Executor loss at the validated cut cannot interrupt this separate process into
a half pair/replacement. Allocation/runtime failure and service death are outside
the profile. Proposal identity begins at the complete retained ingress frame;
partially sent bytes are not already an accepted model proposal.

### R6 — One acyclic order and real-time precedence

> “A completed relevant change precedes a later initiated affected request.”
> — Abstract Semantics, Authority and order

**Classification: concretely enforced, conditional on lock and IPC behavior.
Verdict: implemented, with a documented stronger ordering choice.** All protected
paths use one lock (177); no current-state guard runs outside it. Reply generation
follows publication (184–185), and transmission follows resolver return (214–216).
An acknowledged revocation therefore precedes a later-started request's guarded
decision. Overlapping histories are checked for one whole-set ordering, including
denials, observed successor views and response-before-invocation edges. The
separate cycle fixture (157–160) uses this same resolver. A global order also
serializes unrelated operations; the abstract contract does not require that
extra order. The harness's barriers are not the enforcement mechanism.

### R7 — Rights, exclusivity and attenuation

> “Delegated rights are a subset of current delegable parent rights when that policy is claimed.”
> — Verification Obligations, Model invariants 4

**Classification: concretely enforced. Verdict: implemented.** `valid` enforces
coupled data, per-position/coexistence exclusion, issued authority and parent
rights (83–96). Delegation checks attenuation (131); restriction/replacement
cascade in the tentative view (112–120). `valid` runs on every candidate (181).
Exhaustive differential edges cover all masks and reachable states. Live
competing-grant and delegation/restriction races exercise the shared boundary.
The parent relation is one declared edge, not arbitrary delegation topology.

### R8 — Executor-loss continuity

> “An executor-loss event does not itself erase the authoritative view”
> — Abstract Semantics, Continuity and failure

**Classification: concretely enforced process separation, with trusted live
holder and supervisor. Verdict: implemented under assumption.** `serve` constructs
the holder once (191); handler EOF/lost reply only returns from that handler
(206–218). It never clears work or authority. The trusted supervisor keeps its
management endpoint alive; loss of that supervisor and all service endpoints is
not the executor-only failure profile. Actual separately executed processes are
killed at five cuts in `loss_cuts`, not simulated by toggling a Boolean. Work and
position names are fixed interpretations; no executor lifetime is stored in them.

### R9 — Accepted meaning and necessary bytes

> “If continuation needs the bytes, the reference does not preserve continuity.”
> — Verification Obligations, Trace properties

**Classification: concretely enforced for two content strings; trusted memory
retention. Verdict: implemented.** Acceptance retains the decoded immutable
string (153–154); continuation compares the provided string and consumes its
finite value (155–156). There is no accepted URL/path/digest or mutable object
reference. Replies use detached serialized copies. The producing executor is
killed after acceptance, and a fresh process reads and consumes retained bytes
through its replacement endpoint. A producer killed before acceptance leaves
accepted content unchanged. Both strings are finite test atoms known to the
program; this is not evidence for arbitrary large or externally held content.

### R10 — Pending, acknowledgement loss and replay

> “Commitment and the caller's knowledge of commitment are distinct.”
> — Abstract Semantics, Resolved transition relation

**Classification: concretely enforced outcomes; deliberately excluded progress
and exactly-once guarantees. Verdict: implemented.** Incomplete/oversized frames
return without protected mutation (205–207). Complete malformed frames deny
(208–214, 178–179). A failed reply does not roll back state (215–218). The
published-before-reply kill followed by a replayed `flip` produces two commits
and returns the bit to its starting value. There is no request-ID table or retry
deduplication. Endpoint ordering does not promise fairness or eventual replies.

### R11 — Non-vacuity and concrete/model correspondence

> “A model that only rejects is inadequate even if all its safety invariants hold.”
> — Verification Obligations, Model-adequacy obligations

**Classification: concretely demonstrated within the tested bounds.
Verdict: implemented as a bounded witness, not a universal proof.** The adapter
maps every catalog request and all authoritative fields. All 2,469,824 reachable
model edges match the separately implemented concrete reducer. Thirteen recorded
trace groups, live generated sequences and the successful continuation exercise
real ingress/publication. Direct reducer comparison does not exhaust all OS
interleavings; live traces do not constitute a whole-stack refinement proof.
The cycle fixture uses the existing independent history oracle rather than
pretending three bits belong to the two-bit authoritative graph.

### R12 — Outside actions and stronger failures

> “Independent failure and restart of an authority service ... are not established by the evidence.”
> — Abstract Semantics, Continuity and failure (excerpt)

**Classification: deliberately out of scope. Verdict: not claimed, not missing
enforcement inside this profile.** The service imports dataclasses, JSON, OS,
sockets, sys and threading (9–14); its only outside effects are IPC/diagnostic
output and supervisor-only test gates. No work-executing external sink is offered.
No persistent store or restart path exists. Searches for state assignments,
`open`, `subprocess`, socket/JSON calls and all resolver callers were checked;
there is one post-bootstrap protected assignment and one handler call site.
Runtime/OS/hardware correctness, resource exhaustion, hostile debugging,
descriptor theft and attacks on the trusted supervisor remain assumptions or
excluded failures, not audited security guarantees.

## Reverse-direction findings and remaining uncertainty

The concrete protocol adds a 4,096-byte frame limit, strict JSON field/type
validation, finite pre-provisioned contexts, a total service order, and readable
state snapshots for any endpoint holder (including stale holders). These are
explicit experiment choices. The contract does not promise confidentiality,
unbounded content, an indefinite fresh-context supply, or concurrent execution
*inside* one commitment. No extra mutable policy or outside admission dependency
was found.

Ingress interprets a complete newline-delimited frame as a proposal; incomplete
fragments are pre-submission material. Concurrent writers/readers sharing one
stream can corrupt framing or consume one another's replies. The tests use
separate endpoints for concurrent requests; they do not establish a client-side
multiplexing protocol. Every complete received frame still crosses the same
guard. End-to-end intent preservation before whole ingress, confidential
capability distribution, and reply routing between shared-handle holders are
not additional guarantees of this experiment.

**Result:** no missing enforcement found within the declared profile. The main
residual uncertainty is whole-stack correspondence beyond tested traces and
trusted runtime/OS behavior. The self-review cannot replace independent review.

**WHY:** Every relevant obligation was traced through the actual sole ingress,
guard, candidate construction, invariant check, publication and response paths.
**WHAT:** Source inspection, model differential checks, concrete loss/concurrency
tests and generated properties; exact counts/hashes are in the experiment results.
**HOW CERTAIN:** Evidence-based bounded conformance assessment, not a formal
refinement proof. **WHAT-NOT-TESTED:** Independent review, all possible runtime
schedules/frames, OS security, stronger failure profiles and unbounded witnesses.
