===== BEGIN FILE: docs/research/kernel-0/Kernel-0-Abstract-Semantics.md =====
---
title: Kernel-0 Abstract Semantics
program: EDASES
layer: Research
document_type: Provisional Specification
status: Provisional
authority: Derived
canonical_repository: ASES
last_updated: 2026-09-26
crosslink_issue: 566
---

# Kernel-0 Abstract Semantics

This is a realization-neutral candidate contract. It defines the smallest presently justified authoritative boundary, not a physical component, data schema, proof tool, or canonical Work Unit ontology. The [reasoning record](./Kernel-0-Reasoning-Phase-Result.md) gives its evidence and unresolved questions.

## Parameters and meaning

An instantiation declares:

- an **authoritative view** `σ`: all distinctions whose current meaning determines accepted work, current permission, or a critical invariant. If an accepted fact depends on live external data, changes to that data belong to this view unless the dependency is made immutable or a later guarded acceptance is the only event that can change authoritative meaning;
- a set of **proposed effects** `q`, each with a declared effect granularity, affected domain, and authority evidence. A policy-generated event that changes authority is also a proposal. A caller's identity or assertion is not itself permission;
- a current **admissibility predicate** `G(σ,q,f)`, where `f` is an optional external fact with an explicit source, freshness, and ordering assumption;
- a proposed whole-effect relation `E(σ,q,σ′)` and critical invariant `I(σ)`;
- a declared failure boundary and, for any protected external action beyond a change in `σ`, its authorization point and meaning under later invalidation.

`σ` is the combined state of whatever trusted components the claim actually relies on. Locating a distinction outside one proposed kernel component does not remove it from the trusted assurance boundary. Two histories may share the same abstract `σ` only if every required future permission and continuity observation is equivalent.

`G`, `E`, and `I` are a checkable decomposition of one admissible-transition relation, not three required kernel APIs or stored objects. The optional fact `f` can be carried in a request or trusted state if its source and timing remain explicit.

## Resolved transition relation

For an initial state, `I(σ₀)` holds. A resolved proposal has one of these outcomes:

```text
commit:  σ --q/commit--> σ′  only if  G(σ,q,f) ∧ E(σ,q,σ′) ∧ I(σ′)
deny:    σ --q/deny--> σ    with no authoritative effect attributable to q
```

The first line describes a permitted commitment; it does not authorize an arbitrary successor merely because an unspecified predicate is named `G`. Each instantiation must supply enough policy and state to evaluate `G`, `E`, and `I`. The `σ` used for admission and the whole effect is one coherent current view at that commitment point. Validation against an earlier snapshot cannot be detached from the effect if another commitment could change its validity. A proposed effect cannot silently become a different or partial authoritative effect. A request may remain pending without a resolved transition; no eventual response or progress follows. Commitment and the caller's knowledge of commitment are distinct.

Every event that changes the authoritative view must be represented as a guarded proposal, including an externally triggered or policy-generated event. Its triggering fact has a declared trust boundary. A mutable external location that changes an accepted live reference is therefore protected even if no nominal kernel record changes. An external candidate that cannot alter authoritative meaning before a separate guarded acceptance can be changed speculatively outside this boundary. External visibility and reversibility alone do not decide whether an effect is protected.

## Authority and order

Authority is the state-dependent eligibility of a proposed effect, not a privileged property of the proposing actor. An authority grant, restriction, transfer, or invalidation is itself subject to the resolved transition relation. The source of initial management authority is an explicit trusted initial-state assumption.

Independently resolved commitments whose effects can change one another's admission or invariant result must admit one common **acyclic** abstract order across the entire interacting set, consistent with the views used to validate each commitment. This includes authority changes and affected requests, and conflicting changes to work state. Each request is judged against the relevant current view produced by its predecessors in that order. A completed relevant change precedes a later initiated affected request. Overlapping operations may resolve either way if one coherent order exists. A truthful read made before invalidation cannot justify a commitment ordered afterward. Unrelated commitments need no universal total order, clock, or stored sequence number. A declared composite proposal may instead have one atomic whole-effect transition; independent proposals cannot silently be treated as a batch validated against one old snapshot.

If one producer must remain eligible while a superseded producer is denied, their attempts must differ in a trustworthy admission observation or pass through a trusted mediator that distinguishes them. Current permission for a principal shared by both is insufficient. Old authority evidence must not become valid again merely because a representation is reused while old attempts remain possible. This requires a non-confusable current authority relationship, not a primitive Execution identity, generation number, token type, or lineage record. If the claim excludes the old **physical producer** even when it obtains new current evidence, the instantiation additionally needs trustworthy source binding or a non-transfer condition. A genuinely new grant to that producer is a separate authority event, not survival of its old grant.

## Continuity and failure

An executor-loss event does not itself erase the authoritative view, end the continuing work, or require a resident executor for inactive work. An instantiation supplies a continuity projection identifying the same work and executor-facing position and the authoritative information needed to continue. Replacement may change current authority while preserving that projection. Work Unit, Attachment Point, and Execution are consumer interpretations, not required kernel object types.

The minimum claimed failure class is loss or replacement of an executor, including any authoritative information improperly co-located with it. If an executor is lost during a proposed protected change, the post-loss authoritative state must still correspond to whole committed effects at the declared granularity; the caller may remain uncertain which outcome occurred. A sequence of separately committed changes may leave an allowed prefix. Independent failure and restart of an authority service, loss of trusted persistent state, corruption below the trusted boundary, and a recovery deadline are not established by the evidence. An instantiation that claims those failures must state stronger recovery obligations.

## Boundary of external action claims

An outside action is necessarily protected when its occurrence changes the authoritative view. Other external actions are protected only when an instantiation expressly claims that their occurrence exercises substrate-governed authority. Such a claim must identify the event at which authority is required, the trusted mediation or conformance contract, and whether invalidation cancels an action authorized earlier but completed later. Exclusion of stale authority at an earlier authorization point does not imply that no previously authorized consequence becomes visible after replacement; that stronger claim requires a coherently ordered boundary at the effect sink or an equivalent cancellation contract. An irreversible protected consequence cannot be made valid by a later denial or compensation. No general transaction system follows from this contract.

## Necessity and limits

| Retained distinction | Why it cannot be removed for the stated claim |
| --- | --- |
| Authoritative view versus unaccepted candidate material | Otherwise a stale external write can change an accepted fact without crossing the guard. |
| Proposal versus whole commitment | Otherwise a caller's action or a valid subpart can silently become an unauthorized authoritative change. |
| Current eligibility versus past permission | Otherwise a superseded executor can reuse old authority. |
| Trustworthy distinction among attempts requiring different outcomes | Otherwise old and replacement executions that look identical to admission cannot be treated differently. |
| Coherent validity view for affected commitments | Otherwise a stale observation can authorize a later invalid commitment, or two separately validated changes can jointly violate an invariant. |
| Continuing information versus executor lifetime | Otherwise executor loss can destroy the same work or position needed for continuation. |

The model does not select a representation for any of these distinctions. A Work Unit instantiation must still provide non-vacuous successful histories and its own continuity, exclusivity, and authority policy. Arbitrary work-product correctness, general scheduling, and unclaimed external effects remain outside Kernel-0.
===== END FILE: docs/research/kernel-0/Kernel-0-Abstract-Semantics.md =====

===== BEGIN FILE: docs/research/kernel-0/Kernel-0-Verification-Obligations.md =====
---
title: Kernel-0 Verification Obligations
program: EDASES
layer: Research
document_type: Provisional Verification Specification
status: Provisional
authority: Derived
canonical_repository: ASES
last_updated: 2026-09-26
crosslink_issue: 566
---

# Kernel-0 Verification Obligations

This is the minimum verification target for the provisional [abstract semantics](./Kernel-0-Abstract-Semantics.md). A checked model proves only the properties and assumptions it represents. No proof tool or realization is selected.

## Model invariants

For a declared authoritative view `σ`, proposed whole effect `q`, guard `G`, effect relation `E`, and critical invariant `I`:

1. **Admissibility and whole effect:** every committed `q` satisfies `G(σ,q,f)`, `E(σ,q,σ′)`, and `I(σ′)` using one coherent current validation view. A denied `q` causes no authoritative effect; pending has no completion guarantee.
2. **Current authority:** an authority change is itself guarded. A request ordered after invalidation cannot commit using only the invalidated authority. An old authority representation cannot become eligible again by accidental reuse while old attempts remain possible.
3. **Acyclic conflict history:** all independently resolved commitments that can change one another's guard or invariant result admit one common acyclic order consistent with their validation views and completed-before-initiated precedence. Unrelated commitments need no stipulated order.
4. **Configured exclusivity and rights:** no reachable authoritative view violates the declared conflict or rights policy. Delegated rights are a subset of current delegable parent rights when that policy is claimed.
5. **Executor-loss continuity:** loss or replacement of an executor preserves the declared continuing work/position observation and all authoritative information needed for a later valid continuation. Current authority may change only through a guarded event.
6. **Protected-meaning closure:** every event that changes accepted authoritative meaning, including mutation of a live external dependency, is represented by a guarded commitment or excluded by an explicit trusted immutability/mediation assumption.

Old-grant exclusion is unconditional once that grant is invalidated. Exclusion of the old physical producer after it obtains a new valid grant is a separate, conditional source-binding claim. No general exactly-once, eventual progress, or independent authority-service restart property is inferred.

## Model-adequacy obligations

Before exhaustiveness is meaningful, the model must contain enough state to distinguish current from invalidated authority, old from replacement evidence when different outcomes are required, work from execution lifetime, position continuity, configured rights/conflicts, and every live external dependency that can change authoritative meaning. It must model relevant external facts with their trust and ordering assumptions. A caller-supplied assertion alone cannot satisfy an authority premise.

The event alphabet must allow proposal, commit, deny or pending, authority update, executor loss, replacement, compatible and conflicting work changes, and any external fact or protected effect the claim includes. It must represent materially different orders, including overlapping operations and conflict cycles. Non-vacuity requires at least successful establish, authorized change, replacement, and continuation histories. A model that only rejects is inadequate even if all its safety invariants hold.

## Trace properties

| Regression trace | Required result |
| --- | --- |
| Read authority; invalidate it; attempt commitment based on the old read | Deny the later commitment. |
| Race replacement with an old request in both orders | Before replacement may commit; after replacement cannot use old authority. |
| Reuse or replay old evidence after replacement | Old evidence remains invalid. If the old producer presents genuinely new valid evidence, physical exclusion needs the declared source-binding rule. |
| Two writes each validated against `(0,0)` but together violating `d1+d2≤1` | At most one independent proposal commits. |
| Three proposals with guard dependencies requiring `A<B<C<A` | All three cannot commit independently; pairwise consistency is insufficient. |
| A revocation finishes and is acknowledged before an affected old-authority request begins | The later request cannot be ordered before the revocation to justify commitment. |
| Executor loss between validation and effect, or effect and durable record | The authoritative view after recovery corresponds to whole allowed commitments at declared granularity; no accepted invalid partial state. |
| A stale executor changes an accepted live external referent | Reject/prevent the change or fail the protected-meaning claim. Candidate material awaiting separate acceptance is a different case. |
| Accept a reference/hash to bytes stored only with the executor; then lose that executor | If continuation needs the bytes, the reference does not preserve continuity. Retain accepted content or rely on a declared trusted holder before acceptance. |
| Conflicting grants/revocations and an over-broad delegated grant | Every accepted order preserves configured rights and exclusivity. |
| Authorization of an outside action before invalidation, with consequence afterward | Apply the declared authorization-point and cancellation contract; no universal outcome is inferred. |
| Commit followed by lost acknowledgement and replay | Authoritative outcome remains definite. A repeated authorized request may commit again; exactly-once behavior needs separate declared semantics. |

If independent authority-service restart, storage interruption, or corruption is claimed, add traces for the exact covered failure and recovery points. If external actions are in the protected set, include their effect-sink ordering and irreversible completion behavior. These are profile-specific additions.

## Realization-conformance obligations

A realization must define an abstraction from its concrete records, memory, external dependencies, and trusted services to `σ`. Every protected concrete effect must refine one permitted whole abstract commitment; a denial refines a no-effect outcome. Concrete validation and effect must behave as one coherent abstract transition across all relevant dependencies, including three-way conflicts and cross-component authority updates. Executor loss must preserve or reconstruct the declared authoritative view. If an external sink is protected, its authorization point and effect ordering must refine the abstract contract. An implementation cannot claim a smaller trusted boundary by placing an authoritative fact or mediator outside its named kernel component.

The mapping must also account for observations: a caller may not receive a commitment acknowledgement, and speculative external work cannot be treated as authoritative before guarded acceptance. Independent restart, safe retry, or progress need separate correspondence arguments if claimed.

## Trusted assumptions and claim boundary

State the origin of initial management authority; authenticity, freshness, non-confusability, and any physical-source binding of authority evidence; correctness of the supplied policy and conflict relation; integrity and availability of retained state across executor loss; trust/freshness of outside facts; immutability or mediation of live external dependencies; and any failure classes excluded beneath the retained-state boundary. Implementation-specific compiler, runtime, OS, storage, circuit, or hardware assumptions belong in a later realization claim.

**WHY:** Each obligation closes a specific false-confidence path: stale admission, indistinguishable authority, cyclic validation, hidden authoritative dependencies, invalid partial recovery, or model-to-realization mismatch.

**WHAT:** The Evidence Packet, the abstract semantics, the finite Work Unit adequacy attempt, and open Astra falsification of the candidate.

**HOW CERTAIN:** Evidence-based verification target. The stated counterexample traces logically invalidate models that admit them; adequacy and realization conformance remain to be demonstrated.

**WHAT-NOT-TESTED:** No model has been exhaustively checked, no concrete realization has been mapped to this specification, and no external sink, substrate restart, or liveness guarantee has been verified.
===== END FILE: docs/research/kernel-0/Kernel-0-Verification-Obligations.md =====

===== BEGIN FILE: docs/research/kernel-0/Kernel-0-Finite-Model.md =====
---
title: Kernel-0 Finite Model
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
related_documents:
  - Kernel-0-Reasoning-Phase-Result.md
  - Kernel-0-Realization-Comparison.md
consumed_by:
  - Kernel-0 realization-conformance experiment
---

# Kernel-0 Finite Model

## Result and evidence

**Frontier A, restricted to the explicitly bounded model family below.** The candidate survives the encoded exhaustive searches and adversarial checks. Deliberately weakened variants produce concrete counterexamples. No counterexample requires changing the current Abstract Semantics or Verification Obligations; neither file was changed. This is evidence for one finite consumer instantiation and its assurance boundary, not proof of general Work Unit adequacy or a realization.

The executable [kernel0_finite_model.py](./kernel0_finite_model.py) and generated [results](./Kernel-0-Finite-Model-results.json) are the reproducible evidence. The results include the source SHA-256, counts, successful histories, and counterexample traces with before/after states. Use Python 3.10 or later, without optimization:

```sh
python3 docs/research/kernel-0/kernel0_finite_model.py --output docs/research/kernel-0/Kernel-0-Finite-Model-results.json
```

This work starts from the two current specifications at `af3bf3d2885c9c4d653b635a0dbb80663557abe2` on `codex/kernel-0-reasoning-566`. Only the specified finite Work Unit, composition, and adequacy material was read from the reasoning record. Historical derivation was not used as a contract. The realization comparison was read after the finite result stabilized.

## Declared profile and finite bounds

The trusted holder remains alive. Executors can disappear at any modeled request stage and lose **all** their private evidence and candidate bytes. There is no independently failing authority service, storage interruption, corruption, outside admission fact `f`, or protected external action beyond accepted state/content. Executor death does not implicitly revoke authority. An already submitted request can resolve after its executor dies; an unsubmitted request can remain unstarted forever.

| Bound / policy | Reason for inclusion and limit |
| --- | --- |
| One continuing identity; two stable positions | Both positions refer to the same work. A single establishment proposal creates both associations. No general association topology, work deletion, or cross-work authority claim is made. |
| Four distinct authority contexts | `a0,a1,a2` belong to position 0; `a3` to position 1. This admits two successive replacements and compatible concurrent authority. A context can be issued only once. Exhausting this finite supply denies further fresh grants; this does not establish indefinite replacement. |
| Two Boolean work fields `x,y` | Both can change independently. The independent profile permits all four values; the coupled profile requires `x+y≤1`. These bounds discriminate compatible changes from invariant-conflicting changes. |
| Three rights, all seven nonempty subsets | Rights permit changing `x`, changing `y`, and accepting content. Work grants never carry management authority. The rights masks are finite consumer policy, not kernel types. |
| At most one active context per position | A separate exclusive profile permits only one active context across both positions. The independent/coupled profiles permit two. |
| One delegation edge, from a position-0 context to `a3` | Delegated rights are a subset of the current parent's rights. Restriction intersects child rights; revocation/replacement removes them. This **chosen cascading policy** is not a universal Kernel-0 rule. Arbitrary delegation trees are untested. |
| Two accepted content atoms, plus absence in the content-loss model | Atoms stand for required byte strings. An established work has initial retained content. Acceptance replaces the retained value. Continuation must obtain the bytes, match them, and use their value in a proposed work change. A reference alone is insufficient. |
| Two in-flight requests per asynchronous fixture | Enough for the listed authority, field, grant, delegation, composite, loss, and replay races. These searches do not exhaust every pair of the 148 proposal templates or their full product with content modes. |
| Three requests and three bits in the order fixture | Required to expose the specified three-way cycle. Two-request checks would omit this behavior. All accepted subsets and all 64 directed precedence relations are examined, including cyclic relations. |

These are small discriminating bounds, not a cutoff theorem. In particular, a four-way dependency cycle, more than two simultaneous executor failures, more fields, arbitrary content structure, and longer delegation chains are not reduced to the tested cases by a proved theorem. The finite authoritative graphs have no depth cutoff: exploration reaches closure and includes arbitrarily repeated field/content changes and denial stutters within the four-context bound.

## State, events, and transitions

The authoritative state is:

```text
σ = (established, (x,y), required_content, issued, rights[4], parent[4])
C = {position 0 ↦ work, position 1 ↦ work} when established; otherwise empty
```

`issued` witnesses the effective no-reuse distinction. It is proof state for this instantiation, not a demand for a stored generation, epoch, token, or lineage object. `parent` exists solely because the selected consumer policy makes later restriction depend on delegation provenance. Work/position names are fixed interpretation constants. The model does not install Work Unit, Attachment Point, Execution, clock, scheduler, or transaction primitives in Kernel-0.

Each proposal contains its effect kind, scope/value, and trusted authority-context observation. The `authentic` bit in the executable is an **ideal trusted-ingress premise**, never a Boolean the caller is entitled to assert. Forgery is separately attacked. Evidence can be copied and replayed; copying does not create a new context. Physical source exclusion after acquisition of new valid transferable evidence is not claimed.

| Proposal | Admission and whole effect |
| --- | --- |
| Establish | Initial trusted management authority; absent work becomes the two associations, `(0,0)`, and retained content 0. |
| Grant / restrict | Management authority; grant requires an unused context. Restriction cannot amplify rights and cascades to the declared child. All configured conflicts are checked. |
| Replace | Management authority, an active old context, a fresh context for the same position; withdraw old and its dependent rights and install the replacement in one whole effect. Preserve work and content. |
| Delegate | Current parent's rights cover the requested subset; fresh child at the other position; check rights and coexistence invariants. |
| Set / flip / pair | Current context covers every changed field; the resulting whole state satisfies the configured invariant. A pair is one declared proposal. A flip makes repeated successful application observable. |
| Accept | Current content right; retain the entire accepted atom. |
| Resume | Current `x` right and the provided actual content matches the retained accepted content; set `x` to that value if the resulting invariant permits it. |
| Mixed composite | One worker proposal requests a permitted `x` change and an impermissible authority grant. Deny the entire proposal. |

`candidate` supplies explicit `G` and `E`; `resolve` commits only a candidate satisfying `I`, otherwise returns the identical authoritative state. The catalog has 148 well-formed finite templates. Malformed wire data and arbitrary parameter values are outside this abstract input alphabet.

This consumer chooses commitment whenever its guards permit it. The abstract contract also permits denial or indefinite pending. Additional policy-independent denials are authoritative stutters and cannot add an unsafe authoritative state; successful reachability would change, so no progress claim follows from this choice.

The asynchronous state adds request phases, captured observations, outcomes, executor availability, and response-before-invocation edges. Each request can be submitted, observed, resolved, and acknowledged or lose its acknowledgement. Submission copies the whole proposal to the retained boundary. Death removes executor-only state; submitted copies remain. A validation observation is advisory: commitment reevaluates the current view. BFS explores all available event choices in each fixture and retains a shortest counterexample for a weakened transition.

The content model separately contains executor-local bytes, accepted identity, retained bytes, current/replacement authority, and a continuation result. Candidate mutation before acceptance is unprotected and cannot change copied accepted meaning. After death, a fresh replacement must fetch retained bytes to continue. The `accepted` value in the hash-only mutant is the checker's expected-content identity; clients have no operation that reconstructs bytes from this identity. Integer encodings of two symbolic atoms do **not** justify treating a concrete digest as reconstructible content.

## Exhaustive checks and non-vacuity

| Search | States / cases | Transitions | Result |
| --- | ---: | ---: | --- |
| Independent authoritative graph | 8,442 | 1,249,416 | Invariants and effect checks pass |
| Coupled authoritative graph | 6,332 | 937,136 | Invariants and effect checks pass |
| Exclusive authoritative graph | 1,914 | 283,272 | Invariants and effect checks pass |
| Nine reference asynchronous fixtures | 1,195 | See per-fixture results | All current-view checks pass |
| Whole-history order checker | 4,096 histories | All candidate orders searched | 1,712 admit a common order; 2,384 do not |
| Copied-content boundary | 33 | 111 | No loss/bypass counterexample; continuation after death succeeds |
| Live-reference / hash-only mutants | 39 / 25 | 123 / 55 | Both fail |
| Split two-field effect | 48 failure cuts | 16 before/after pairs × 3 cuts | Four cuts expose a forbidden partial effect |

The authoritative graphs check 2,469,824 proposal edges, including 309,459 commitment edges. Checks cover initial validity, current rights, no reuse, attenuation, exclusivity, invariant preservation, work/content preservation under authority operations, whole requested work effects, and denial equality. Authority-changing operations require management authority except the explicitly bounded delegation operation.

The order checker is separate from the BFS transition engine. It asks whether **any** permutation of the full accepted set both respects precedence and executes with the required guard observations. A second algorithm derives read/write dependency edges and checks acyclicity by eliminating vertices without predecessors. The algorithms agree on all 4,096 cases. A deliberately pairwise checker accepts eight histories that the whole-set checker rejects.

Successful histories exclude always-deny adequacy:

1. Establish; grant `a0`; change `x`; accept content 1; replace `a0→a1`; consume content in a permitted continuation; change work; replace `a1→a2`; continue; authorize `a3`; change `y` concurrently under the independent policy. Final data is `(1,1)` and both current positions have authority.
2. Create candidate 1; accept and retain its bytes; lose the original executor and all private bytes; replace its authority; the replacement fetches and consumes accepted content 1.
3. Both compatible field proposals commit. Under `x+y≤1`, at most one of the two proposals setting separate fields to 1 commits. Under the exclusive-grant policy, at most one competing grant commits.
4. Old work may commit before replacement. If replacement commits first, the old work proposal is denied. Replays of both `a0` and `a1` after two replacements are denied.

These are existential successful histories and exhaustive bounded safety checks, not eventual-service guarantees.

## Attacks and concrete counterexamples

The generated file preserves executable traces and their states. The following summaries identify what each trace falsifies.

| Attack / removed distinction | Discriminating trace and result |
| --- | --- |
| Past versus current authority | Observe `a0`; revoke or replace it; resolve old `x:=1`. Reference denies; detached-validation mutant commits. Both orders of the reference race are explored. |
| Evidence reuse | Grant `a0`; withdraw it; grant the same label again; replay retained `a0`. Dropping no-reuse admits the replay. Reference rejects the repeated issuance and replay. |
| Confusable old/replacement evidence | After `a0→a1`, map old `a0` to the currently active position context. Old work incorrectly commits. Exhausting the two Boolean admission answers for one shared observation shows the dilemma: allow admits old; deny excludes the required successful replacement. |
| Copied/refreshed evidence | Copies of invalidated contexts remain invalid. A physical old producer presenting genuinely valid new `a1` evidence can commit in this transferable-evidence profile. This is a conditional-source-binding limit, not a semantic failure. |
| Forged authority assertion | Claim an active context with untrusted evidence. Reference denies; dropping the authenticity premise admits the effect. A trustworthy context label cannot be supplied by assertion alone. |
| Independent stale validation of conflicting fields | Both observe `(0,0)`; one commits `(1,0)`; the other applies its old-view `y:=1`. Mutant reaches `(1,1)` under `x+y≤1`; current-view reference denies the second. |
| Pairwise consistency without a common order | At `000`, A reads `y=0`, writes `x=1`; B reads `z=0`, writes `y=1`; C reads `x=0`, writes `z=1`. Pair orders are A<B, B<C, C<A. Applying all old validations reaches `111`, but no common order permits all three, even though no data invariant forbids `111`. |
| Reordering across completed-before-initiated precedence | With overlapping revoke R and old write W, W<R can explain both commitments. Acknowledged R before W's initiation adds R<W; the checker finds no valid order for both commitments. Omitting that edge falsely admits the history. |
| Torn validation view | Actual views are `(eligible,flag)=(1,0)→(0,0)→(0,1)`. A guard requiring `(1,1)` never holds. Taking authority from the first view and flag from the last falsely admits it. All nine pairs of component observations are checked. |
| Executor death during request handling | Every reference stage admits death. Before submission no request need complete; after submission an authorized whole effect may survive death; after commitment the acknowledgement may be lost. Authority does not vanish merely because its executor dies. |
| Split whole effect | Propose `(x,y):=(1,1)` from `(0,0)`; expose `x:=1`; lose executor before `y`. Observed `(1,0)` is neither the old state nor the declared whole effect. It fails despite satisfying the independent data invariant. |
| Co-located authoritative view | Erase the established view with the executor. Work associations, required content, and current authority disappear. This directly violates the declared loss projection. |
| Accepted bytes held only by executor | Accept identity/hash; lose the sole immutable byte holder. Identity survives but content is absent and replacement cannot continue. Copying accepted content to the still-live holder survives this attack. |
| Mutable live-reference bypass | Accept local referent; revoke; old executor overwrites it. Accepted meaning changes without a guarded commitment. Copied acceptance permits later candidate mutation without changing accepted meaning. |
| Exclusivity | Independently observe no grants; resolve two incompatible grants using the old view. Mutant retains both. Current-view admission permits only one. |
| Delegation amplification / racing restriction | Parent has only `x`; delegate `x,y,content` by skipping attenuation. Also: observe parent restriction before a child exists, commit delegation, apply the old restriction without cascading. Both violate the selected current-parent policy. |
| Denied composite partial effect | Worker requests permitted `x:=1` plus unauthorized grant. A mutant applies `x` and returns deny. Reference leaves all authoritative fields, including issuance facts, unchanged. |
| Mutable proposal | Submit `x:=0`; later retarget the proposal to `x:=1`. Rights and state invariants still hold, but the effect is not the declared proposal. Frozen proposal/effect identity is part of the whole-effect correspondence. |
| Lost acknowledgement and replay | Commit `flip(x)` from 0 to 1; lose reply; replay while authority remains valid; commit back to 0. Both commitments are allowed and observable. The model intentionally does not deduplicate. |

None of these counterexamples occurs in the corresponding reference fixture. The failures are already prohibited by the candidate contract or by the explicitly selected consumer policy. They identify necessary distinctions and realization obligations, rather than new kernel primitives.

## Attack on model adequacy

**The initial encoding was too weak as evidence.** Merely retaining a content field did not demonstrate a continuation that needed it. The model was amended with a content-consuming operation and a post-loss fetch/consume history. A first continuation-witness detector could also count a consume *before* death; it was tightened to require consumption *after* death. Both content-loss mutants now have no such witness. These were model/monitor repairs, not semantic repairs.

**What histories are collapsed?** The authoritative search merges equal tuples and drops request history. That is sound for this finite policy only because future admission/continuity uses exactly those tuples and fresh-context status; there is no time, external fact, deduplication, or hidden local permission cache in `G`. The separate asynchronous search retains observations, phases, outcomes and real-time edges that this quotient would erase. Content-holder placement is varied in its own model rather than collapsed into a retained identifier. Fixture composition is not an exhaustive product proof.

The executable supplies reachable distinguishability witnesses: never-issued versus revoked contexts differ on a future grant; different current scopes differ on a write; independent versus delegated grants with identical rights differ on parent revocation; different accepted content differs on continuation; and different work values differ on a future invariant-sensitive write. These show why the respective information matters. They do not prove globally minimal state count. Stable work/position constants avoid unnecessary identity permutations while preserving the consumer's required equality across loss/replacement.

**Which order is assumed?** The reference transition relation deliberately represents whole commitments atomically, so invariant checks on it cannot prove that an implementation enforces atomicity or coherent order. BFS schedules are linearizations; every finite acyclic relevant order has a linear extension, and unrelated commuting effects can be enumerated in either order without demanding a universal stored sequence. The independent history checker accepts cyclic relations as inputs and rejects them where no common order exists. It therefore tests the property that a conventional interleaving engine would otherwise exclude by construction. The three-bit extension is essential evidence against relying solely on two-request races.

**Which atomicity is trusted?** The reference transition publishes one successor. Detached validation, torn views, mutable proposals, denied partial application, and split-effect death explicitly remove that assumption and fail. This establishes the need for a correspondence obligation; it does not discharge it. A fully visible whole effect before an acknowledgement or bookkeeping record can still be a commitment. No separate log/record primitive or exactly-once outcome is inferred.

**Can evidence be copied, refreshed, or confused?** Yes: the mutations and direct witnesses cover stale copies, reused labels, collapsed contexts, forged assertion, and newly valid transferable evidence. Authenticity and non-confusable issuance themselves are ideal premises. There is no cryptographic model, adversary able to compromise the holder, or proof of physical source binding. Three finite contexts at one position cannot establish unbounded freshness or resistance to numeric wraparound.

**Does loss remove everything local?** In-flight fixtures delete the executor's availability and all ability to submit from its local state. The separate content model actually replaces private bytes with absence. Retained envelopes are explicit copies owned by the still-live boundary. The model does not keep an executor-only pointer and call it retained. Submit/copy is one abstract ingress event: a concrete interrupted or partially received message must refine pending/no protected effect until its whole proposal is available. Networks, torn decoding and retransmission protocols are not explored.

**Can meaning change elsewhere?** The live-reference mutant says yes, and fails protected-meaning closure. The passing profile instead copies two opaque content atoms. It does not prove that an arbitrary nested object, file, closure, URL, or device dependency is immutable. A realization must either map all such dependencies into the authoritative view or establish its claimed copying/immutability/mediation boundary.

**Are invariants vacuous?** The same explorer admits establishment, authority, content acceptance, two replacements, delegation, compatible concurrent changes, and continuation. It rejects coupled-field and exclusive-grant combinations. The cyclic-history and mutable-proposal attacks satisfy ordinary final-state invariants while still violating the contract, so passing `I` alone is not treated as success. Lost-ack replay succeeds twice; dead executors can leave pending requests. Safety has not silently been expanded into progress or exactly-once claims.

## Trusted assumptions and claim boundary

The root manager remains trusted and authorized throughout this profile; authority changes it proposes still cross the guard. Revocation of root management authority is not modeled. Authority observations are authentic and distinct where required; effective no-reuse survives executor loss. Policy, effect scopes, the chosen cascade, and the continuation projection are supplied correctly. The complete retained view and accepted bytes remain intact and available while executors die. Accepted content is copied or supplied by a declared immutable, available trusted holder. A submitted proposal cannot be silently retargeted. These assumptions describe the assurance boundary, not properties established by enumerating an abstract model.

The checker itself, Python execution, finite encodings, property monitors, and this abstraction argument remain trusted. No proof-assistant-certified checker or theorem about arbitrary populations was produced. Agreement of the two ordering algorithms and detection of weakened variants reduce specific false-confidence risks; they do not eliminate specification or checker errors.

**WHY:** Positive histories show that the finite contract can support the requested consumer. Negative histories show that removing retained distinctions or enforcement assumptions admits forbidden outcomes; separate ordering/content checks expose omissions an atomic state explorer would hide.

**WHAT:** Exhaustive finite authoritative closure, nine asynchronous fixtures, 4,096 relational ordering cases, content-boundary closure, 48 partial-effect failure cuts, and recorded targeted mutations/distinguishability witnesses.

**HOW CERTAIN:** Evidence-based bounded result. The reported searches completed with their checks enabled. The finite encoding and its adequacy argument remain reviewable research evidence, not an unbounded proof or a claim of realized protection.

**WHAT-NOT-TESTED:** Independent authority-service restart; persistent-storage failure or corruption; protected effect sinks; arbitrary external facts; physical source binding after new-evidence acquisition; cryptography; unbounded context freshness; arbitrary delegation/identity/content topology; all larger concurrent interactions; fairness/progress; exactly-once processing; implementation, runtime, operating-system, or hardware conformance.

## Next realization gate

The [existing comparison](./Kernel-0-Realization-Comparison.md) still justifies the tiny **still-live in-memory authority-service experiment as a falsification experiment**. No tested semantic premise invalidates that choice. Its benefit is that one retained boundary can hold the complete finite view and accepted bytes while executors are independently terminated. This remains an inference about experimental scope, not a production selection or conformance result. No service was built here and broad realization research was not reopened.

Before interpreting an experiment result, define an abstraction `α` from the complete concrete authority holder, ingress/freshness mechanism and retained content to the modeled view. Any auxiliary history used for the freshness argument must be justified by the concrete issuer's behavior; a proof-only issued set cannot manufacture protection. Record invocation, validation observation, whole publication, reply/loss and executor-loss events separately.

| Concrete experiment trace | Exact model correspondence / pass condition |
| --- | --- |
| Establish, authorize, accept bytes, replace twice, continue at both positions | Map work/position equality, rights and accepted bytes to the successful witness. A replacement fetches the actual required bytes after deleting/terminating the original holder of candidate material. Mere receipt of an identifier is insufficient. |
| Pause old request around validation; revoke/replace in both orders | Concrete publication must refine one current-view `resolve`. Old-before-replacement may commit; replacement-before-old must deny. A check followed by an independently visible mutation is insufficient. |
| Complete and acknowledge revocation; only then initiate old request | Trace contains the real-time edge R<W. Reject any explanation that serializes W before R. Include any admission cache or intermediary in `α`. |
| Replayed old evidence, deliberate label reuse, indistinguishable/shared evidence, forged assertion | Demonstrate how trusted ingress distinguishes contexts and rejects old/forged evidence. Test the actual mechanism, not a test client setting `authentic=True`. If old-producer exclusion after acquiring new evidence is desired, declare and test a separate source-binding contract. |
| Two compatible changes, two coupled conflicting writes, competing exclusive grants, delegation/restriction race | Map the configured policy exactly. Both compatible changes can succeed; the conflicting combinations cannot coexist; restriction cannot leave an over-broad child. |
| Three independently validated guarded requests | Preserve all three guard dependencies and search for one common order. Do not treat pairwise success or a valid final `111` state as sufficient. A third Boolean fixture is enough; it need not become a production kernel primitive. |
| Kill executor before submission, after validation, around publication, and before reply | Concrete observations refine unchanged state or a permitted **whole** effect. No half pair or half replacement becomes authoritative. Retained authority/content must not live only in the killed executor. The service remains alive throughout. |
| Modify candidate after acceptance; delete its sole external copy; retarget request payload | Accepted meaning must remain the accepted immutable value, or changes must cross the declared guard. Proposal identity must still match the committed effect. Inspect indirect references, not just top-level records. |
| Denied mixed composite; lost reply followed by replay | Denial maps to no attributable protected mutation. Lost reply maps to a definite authoritative result with uncertain caller knowledge. Two valid replay commitments are allowed unless a separately declared retry contract is added. |

Passing those tests would supply bounded concrete traces refining this model. It would still not prove all code paths conform, establish service-restart durability, or validate unmodeled external effects.
===== END FILE: docs/research/kernel-0/Kernel-0-Finite-Model.md =====

===== BEGIN FILE: docs/research/kernel-0/kernel0_finite_model.py =====
#!/usr/bin/env python3
"""Finite research witness, not a service or a general Kernel-0 implementation.

Run with Python 3.10+: python3 kernel0_finite_model.py --output Kernel-0-Finite-Model-results.json
No dependencies, network, randomness, clocks, or persistent service state.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass, fields, replace
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path


POSITIONS = (0, 0, 0, 1)  # Consumer interpretation only; contexts 0 -> 1 -> 2.
X, Y, CONTENT = 1, 2, 4
MANAGER = -1


@dataclass(frozen=True)
class Profile:
    name: str
    coupled: bool = False
    exclusive: bool = False


@dataclass(frozen=True)
class State:
    established: bool = False
    data: tuple[int, int] = (0, 0)
    content: int = -1  # -1 absent; 0 and 1 stand for two required byte strings.
    issued: int = 0  # Proof witness for non-reuse, not a mandated kernel record.
    rights: tuple[int, ...] = (0, 0, 0, 0)
    parents: tuple[int, ...] = (-1, -1, -1, -1)


@dataclass(frozen=True)
class Request:
    kind: str
    evidence: int = MANAGER
    target: int = 0
    value: int = 0
    other: int = 0
    authentic: bool = True

    def label(self):
        who = "management" if self.evidence == MANAGER else f"a{self.evidence}"
        return f"{self.kind}({who}, {self.target}, {self.value}, {self.other})"


def invariant(s: State, p: Profile) -> bool:
    if not s.established:
        return s == State()
    if s.content not in (0, 1) or any(d not in (0, 1) for d in s.data):
        return False
    if p.coupled and sum(s.data) > 1:
        return False
    active = [i for i, r in enumerate(s.rights) if r]
    if any(not s.issued & (1 << i) for i in active):
        return False
    if any(sum(POSITIONS[i] == pos for i in active) > 1 for pos in (0, 1)):
        return False
    if p.exclusive and len(active) > 1:
        return False
    for i, parent in enumerate(s.parents):
        if parent != -1:
            if i != 3 or parent not in (0, 1, 2) or not s.rights[i]:
                return False
            if s.rights[i] & ~s.rights[parent]:
                return False
    return all(0 <= r <= 7 for r in s.rights)


def candidate(s: State, q: Request, weakness: str = "") -> State | None:
    """Explicit consumer G and E. None means G fails; I is checked separately."""
    if not q.authentic and weakness != "forgery":
        return None
    k, a, t, v = q.kind, q.evidence, q.target, q.value
    if weakness == "confusion" and a in (0, 1, 2) and not s.rights[a]:
        a = next((i for i in (0, 1, 2) if s.rights[i]), a)
    management = a == MANAGER
    if k == "establish":
        return replace(s, established=True, content=0) if management and not s.established else None
    if not s.established:
        return None
    rights, parents = list(s.rights), list(s.parents)
    issued = s.issued

    def fresh(i):
        return not rights[i] and (weakness == "reuse" or not issued & (1 << i))

    def restrict(i, mask):
        rights[i] = mask
        if not mask:
            parents[i] = -1
        for child, parent in enumerate(parents):
            if parent == i:
                rights[child] &= mask  # Declared cascading attenuation policy.
                if not rights[child]:
                    parents[child] = -1

    if k == "grant":
        if not management or not fresh(t) or not 1 <= v <= 7:
            return None
        rights[t], parents[t], issued = v, -1, issued | (1 << t)
    elif k == "restrict":
        if not management or not rights[t] or v & ~rights[t]:
            return None
        restrict(t, v)
    elif k == "replace":
        new = q.other
        if not management or not rights[t] or not fresh(new) or POSITIONS[t] != POSITIONS[new]:
            return None
        previous = rights[t]
        restrict(t, 0)
        rights[new], parents[new], issued = previous, -1, issued | (1 << new)
    elif k == "delegate":
        if a not in (0, 1, 2) or t != 3 or not rights[a] or not fresh(t) or not 1 <= v <= 7:
            return None
        if v & ~rights[a] and weakness != "amplify":
            return None
        rights[t], parents[t], issued = v, a, issued | (1 << t)
    else:
        needed = {"set": 1 << t, "flip": 1 << t, "accept": CONTENT, "resume": X,
                  "pair": X | Y, "mixed": X}.get(k)
        if needed is None or a not in range(4) or needed & ~rights[a]:
            return None
        if k == "mixed":  # One proposal: set x=1 AND grant authority as a worker.
            return None
        if k == "accept":
            return replace(s, content=v)
        if k == "resume":
            # A consumer continuation uses the actual accepted content, not
            # merely the existence of a reference. Wrong/missing bytes deny.
            return replace(s, data=(v, s.data[1])) if v == s.content else None
        data = list(s.data)
        if k == "pair":
            data = [v & 1, (v >> 1) & 1]
        else:
            data[t] = v if k == "set" else 1 - data[t]
        return replace(s, data=tuple(data))
    return replace(s, rights=tuple(rights), parents=tuple(parents), issued=issued)


def resolve(s, q, p, weakness=""):
    out = candidate(s, q, weakness)
    if out is not None and (invariant(out, p) or weakness in ("amplify", "exclusivity")):
        return out, "commit"
    if weakness == "partial" and q.kind == "mixed" and s.rights[q.evidence] & X:
        return replace(s, data=(1, s.data[1])), "deny"
    return s, "deny"


def catalog():
    yield Request("establish")
    for a in range(4):
        for rights in range(1, 8):
            yield Request("grant", target=a, value=rights)
        for rights in range(8):
            yield Request("restrict", target=a, value=rights)
        for t, v in product(range(2), repeat=2):
            yield Request("set", a, t, v)
        for t in range(2):
            yield Request("flip", a, t)
        for v in range(2):
            yield Request("accept", a, value=v)
            yield Request("resume", a, value=v)
        for v in range(4):
            yield Request("pair", a, value=v)
        yield Request("mixed", a)
    for old, new in permutations(range(3), 2):
        yield Request("replace", target=old, other=new)
    for a, rights in product(range(3), range(1, 8)):
        yield Request("delegate", a, target=3, value=rights)


def check_edge(s, q, out, outcome, p):
    assert invariant(out, p), ("invariant", q, s, out)
    if outcome == "deny":
        assert out == s, ("denial mutated", q)
        return
    assert q.authentic
    assert s.issued & ~out.issued == 0
    if q.kind in ("grant", "restrict", "replace", "delegate"):
        assert (out.established, out.data, out.content) == (s.established, s.data, s.content)
    if q.kind in ("set", "flip", "pair", "accept", "resume"):
        assert (out.established, out.rights, out.parents, out.issued) == (
            s.established, s.rights, s.parents, s.issued)
        needed = CONTENT if q.kind == "accept" else X | Y if q.kind == "pair" else 1 << q.target
        assert s.rights[q.evidence] & needed == needed
        if q.kind == "resume":
            assert q.value == s.content and out.data[0] == s.content
        if q.kind in ("set", "flip"):
            expected = q.value if q.kind == "set" else 1 - s.data[q.target]
            assert out.data[q.target] == expected and out.data[1 - q.target] == s.data[1 - q.target]
        if q.kind == "pair":
            assert out.data == (q.value & 1, (q.value >> 1) & 1)
        if q.kind == "accept":
            assert out.content == q.value and out.data == s.data
        else:
            assert out.content == s.content
    if q.kind in ("establish", "grant", "restrict", "replace"):
        assert q.evidence == MANAGER
    if q.kind in ("grant", "delegate"):
        assert not s.issued & (1 << q.target)
    if q.kind == "replace":
        assert not s.issued & (1 << q.other)
        assert not out.rights[q.target]
    if q.kind == "delegate":
        assert out.rights[q.target] & ~s.rights[q.evidence] == 0


def authoritative_graph(p):
    requests = tuple(catalog())
    queue, seen = deque([State()]), {State()}
    counts = {"states": 0, "edges": 0, "commit_edges": 0, "deny_edges": 0}
    kinds = set()
    while queue:
        s = queue.popleft()
        counts["states"] += 1
        for q in requests:
            out, outcome = resolve(s, q, p)
            check_edge(s, q, out, outcome, p)
            counts["edges"] += 1
            counts[outcome + "_edges"] += 1
            if outcome == "commit":
                kinds.add(q.kind)
            if out not in seen:
                seen.add(out)
                queue.append(out)
    assert {"establish", "grant", "restrict", "replace", "set", "flip", "pair", "accept", "resume"} <= kinds
    if not p.exclusive:
        assert "delegate" in kinds
    return dict(profile=p.name, requests_per_state=len(requests), committed_kinds=sorted(kinds), **counts)


def established(*grants, p=Profile("independent")):
    s, outcome = resolve(State(), Request("establish"), p)
    assert outcome == "commit"
    for a, rights in grants:
        s, outcome = resolve(s, Request("grant", target=a, value=rights), p)
        assert outcome == "commit"
    return s


def apply_trace(s, requests, p, weakness=""):
    trace = []
    for q in requests:
        before = s
        s, outcome = resolve(s, q, p, weakness)
        trace.append({"event": q.label(), "outcome": outcome,
                      "before": asdict(before), "after": asdict(s)})
    return s, trace


def merge_effect(current, observed, proposed):
    """Deliberately broken detached validation: apply old-view writes now."""
    changes = {}
    for f in fields(State):
        old, new, now = getattr(observed, f.name), getattr(proposed, f.name), getattr(current, f.name)
        if isinstance(old, tuple):
            changes[f.name] = tuple(n if n != o else c for o, n, c in zip(old, new, now))
        elif f.name == "issued":
            changes[f.name] = now | new
        else:
            changes[f.name] = new if old != new else now
    return replace(current, **changes)


@dataclass(frozen=True)
class Flight:
    state: State
    phases: tuple[int, ...]  # 0 unstarted, 1 submitted, 2 observed, 3 resolved, 4 reply, 5 reply lost
    observations: tuple[State | None, ...]
    outcomes: tuple[str, ...]
    alive: int
    before: frozenset[tuple[int, int]] = frozenset()  # Response-before-invocation edges.


def flight_explore(name, initial, requests, owners, p, weakness="", death=True, replay_after=False):
    """Enumerate all reachable interleavings, including all executor death cuts.

    Submission copies the complete proposal into the retained boundary. All
    executor-only evidence/candidate material is represented by alive; death
    clears it. Submitted copies are not executor-owned. Pre-submit death can
    leave an operation permanently unstarted. No fairness is assumed.
    """
    n = len(requests)
    alive = sum(1 << e for e in set(owners) if e >= 0)
    start = Flight(initial, (0,) * n, (None,) * n, ("",) * n, alive)
    queue, parents = deque([start]), {start: None}
    edges, commits, denials, losses = 0, 0, 0, 0
    seen_results, violation = set(), None

    def path(node):
        result = []
        while parents[node] is not None:
            prev, label = parents[node]
            result.append(label)
            node = prev
        return list(reversed(result))

    def add(s, out, label):
        nonlocal edges
        edges += 1
        if out not in parents:
            parents[out] = s, label
            queue.append(out)

    while queue:
        s = queue.popleft()
        seen_results.add((s.outcomes, s.state.data))
        for i, q in enumerate(requests):
            phase = s.phases[i]
            phases, obs, results = list(s.phases), list(s.observations), list(s.outcomes)
            owner_live = owners[i] < 0 or bool(s.alive & (1 << owners[i]))
            out, precedence = s.state, s.before
            if phase == 0:
                if not owner_live or replay_after and i == 1 and s.phases[0] != 5:
                    continue
                precedence |= frozenset((j, i) for j in range(n) if s.phases[j] == 4)
                label = f"{i}: invoke/copy {q.label()}"
                phases[i] = 1
            elif phase == 1:
                obs[i], phases[i] = s.state, 2
                label = f"{i}: observe {s.state}"
            elif phase == 2:
                expected = resolve(s.state, q, p)
                if weakness == "stale_view":
                    proposed, result = resolve(obs[i], q, p)
                    out = merge_effect(s.state, obs[i], proposed) if result == "commit" else s.state
                else:
                    out, result = resolve(s.state, q, p, weakness)
                if (out, result) != expected and violation is None:
                    violation = {"trace": path(s) + [f"{i}: {result} -> {out}"],
                                 "current_view_requires": expected[1],
                                 "expected_state": asdict(expected[0]), "actual_state": asdict(out)}
                if not weakness:
                    check_edge(s.state, q, out, result, p)
                commits += result == "commit"
                denials += result == "deny"
                results[i], phases[i] = result, 3
                label = f"{i}: {result} -> {out}"
            elif phase == 3:
                phases[i] = 5
                lost = replace(s, phases=tuple(phases))
                add(s, lost, f"{i}: acknowledgement lost")
                losses += 1
                if not owner_live:
                    continue
                phases[i] = 4
                label = f"{i}: acknowledgement delivered"
            else:
                continue
            add(s, Flight(out, tuple(phases), tuple(obs), tuple(results), s.alive, precedence), label)
        if death:
            for e in range(4):
                if s.alive & (1 << e):
                    out = replace(s, alive=s.alive & ~(1 << e))
                    assert out.state == s.state  # Authority is NOT implicitly revoked by death.
                    add(s, out, f"lose executor {e}: erase all its private material")
    if weakness:
        assert violation is not None, ("mutant survived", name, weakness)
    else:
        assert violation is None
    return {"name": name, "weakness": weakness or None, "states": len(parents), "edges": edges,
            "commit_edges": commits, "deny_edges": denials, "lost_ack_edges": losses,
            "both_commit_reachable": any(all(o == "commit" for o in outcomes) for outcomes, _ in seen_results),
            "repeated_flip_returns_to_start": all(q.kind == "flip" for q in requests) and any(
                all(o == "commit" for o in outcomes) and data == initial.data for outcomes, data in seen_results),
            "counterexample": violation}


def serial_witness(initial, operations, accepted, precedence, final=None):
    """Independent history oracle: search all orders; input edges may be cyclic.

    Operations are tiny (guard, effect) functions, separate from State/resolve.
    A witness is an order of the entire accepted set, never pairwise voting.
    """
    for order in permutations(accepted):
        rank = {a: i for i, a in enumerate(order)}
        if any(a in rank and b in rank and rank[a] >= rank[b] for a, b in precedence):
            continue
        s = initial
        for i in order:
            guard, effect = operations[i]
            if not guard(s):
                break
            s = effect(s)
        else:
            if final is None or s == final:
                return list(order)
    return None


def history_attacks():
    counts = {"cases": 0, "accepted": 0, "rejected": 0, "pairwise_false_positives": 0}
    directed = tuple(permutations(range(3), 2))
    cycle_example = None
    # Enumerate all eight required observation patterns, all accepted
    # subsets, and all 64 precedence relations INCLUDING the cyclic ones.
    for expected in product((0, 1), repeat=3):
        operations = []
        for i in range(3):
            read = (i + 1) % 3
            operations.append((lambda s, r=read, v=expected[i]: s[r] == v,
                               lambda s, w=i: tuple(1 if j == w else v for j, v in enumerate(s))))
        for mask in range(8):
            accepted = tuple(i for i in range(3) if mask & (1 << i))
            for bits in range(64):
                edges = frozenset(e for j, e in enumerate(directed) if bits & (1 << j))
                witness = serial_witness((0, 0, 0), operations, accepted, edges)
                # A second algorithm derives necessary read/write constraints
                # and removes vertices with no predecessors. Compare it with
                # full serial execution, not with the scheduling loop.
                dependencies = {(a, b) for a, b in edges if a in accepted and b in accepted}
                possible = True
                for reader in accepted:
                    writer = (reader + 1) % 3
                    if writer in accepted:
                        dependencies.add((writer, reader) if expected[reader] else (reader, writer))
                    elif expected[reader]:
                        possible = False
                remaining = set(accepted)
                while remaining:
                    roots = {a for a in remaining if not any(b in remaining and c == a for b, c in dependencies)}
                    if not roots:
                        break
                    remaining -= roots
                assert (witness is not None) == (possible and not remaining)
                pairwise = all(serial_witness((0, 0, 0), operations, pair, edges) is not None
                               for pair in combinations(accepted, 2))
                # Singleton validity is also required of the deliberately weak checker.
                pairwise &= all(serial_witness((0, 0, 0), operations, (i,), edges) is not None for i in accepted)
                counts["cases"] += 1
                counts["accepted" if witness is not None else "rejected"] += 1
                if pairwise and witness is None:
                    counts["pairwise_false_positives"] += 1
                    if expected == (0, 0, 0) and mask == 7 and bits == 0:
                        cycle_example = {"observations": ["A: y=0", "B: z=0", "C: x=0"],
                                         "effects": ["A: x=1", "B: y=1", "C: z=1"],
                                         "required_order": ["A<B", "B<C", "C<A"],
                                         "pair_orders": [[0, 1], [1, 2], [2, 0]],
                                         "weak_trace": ["initiate A, B, C", "observe all guards at (0,0,0)",
                                                        "apply A from old observation", "apply B from old observation",
                                                        "apply C from old observation: (1,1,1)"],
                                         "whole_set_witness": witness}
    assert cycle_example is not None
    # Revocation is completed before an affected request is initiated.
    operations = [(lambda s: True, lambda s: (False, s[1])),
                  (lambda s: s[0], lambda s: (s[0], 1))]
    overlapping = serial_witness((True, 0), operations, (0, 1), frozenset())
    completed_first = serial_witness((True, 0), operations, (0, 1), frozenset({(0, 1)}))
    assert overlapping == [1, 0] and completed_first is None
    # A coherent view cannot be assembled from individually truthful components.
    views = [(True, 0), (False, 0), (False, 1)]
    torn = [(a, b) for a in range(3) for b in range(3) if views[a][0] and views[b][1] == 1]
    assert torn == [(0, 2)] and not any(a and b == 1 for a, b in views)
    return dict(counts, cycle=cycle_example,
                real_time={"overlapping_order": overlapping, "completed_before_initiated_order": completed_first},
                torn_view={"coherent_views": views, "false_admission_by_components": torn})


@dataclass(frozen=True)
class ContentState:
    current: bool = True
    alive: bool = True
    private: int = 0
    accepted: int = -1  # Accepted identity/hash alone in the local-reference mutant.
    retained: int = -1
    replacement: bool = False
    resumed: int = -1


def content_explore(mode):
    def meaning(s):
        if s.accepted == -1:
            return -1
        return s.retained if mode == "copy" else s.private

    start = ContentState()
    queue, paths = deque([start]), {start: []}
    edges, violation, stale_violation, continuation = 0, None, None, None
    while queue:
        s = queue.popleft()
        transitions = []
        if s.alive:
            if mode != "hash_only" or s.accepted == -1:
                transitions.extend((f"private candidate := {v}", replace(s, private=v), False) for v in (0, 1))
            transitions.append(("lose executor and ALL private bytes", replace(s, alive=False, private=-1), False))
        if s.alive and s.current:
            transitions.append(("guarded accept", replace(s, accepted=s.private,
                                                          retained=s.private if mode == "copy" else -1), True))
        if s.current:
            transitions.append(("guarded revoke", replace(s, current=False), True))
        if not s.replacement:
            transitions.append(("guarded replacement with fresh evidence", replace(s, current=False, replacement=True), True))
        if s.replacement and meaning(s) != -1:
            transitions.append(("replacement consumes required accepted bytes", replace(s, resumed=meaning(s)), True))
        for label, out, guarded in transitions:
            edges += 1
            bad = (not guarded and meaning(s) != meaning(out)) or (out.accepted != -1 and meaning(out) == -1)
            if mode == "hash_only":
                # This mutant promises an immutable reference but loses its only holder.
                bad = out.accepted != -1 and meaning(out) == -1
            if bad and violation is None:
                violation = {"trace": paths[s] + [label], "before": asdict(s), "after": asdict(out),
                             "meaning_before": meaning(s), "meaning_after": meaning(out)}
            if bad and not s.current and label.startswith("private candidate") and stale_violation is None:
                stale_violation = {"trace": paths[s] + [label], "before": asdict(s), "after": asdict(out)}
            if label == "replacement consumes required accepted bytes" and not s.alive and out.resumed == out.accepted == 1 and continuation is None:
                continuation = paths[s] + [label]
            if out not in paths:
                paths[out] = paths[s] + [label]
                queue.append(out)
    assert (violation is None) == (mode == "copy")
    if mode == "copy":
        assert continuation is not None
    else:
        assert continuation is None
    if mode == "live":
        assert stale_violation is not None
    return {"mode": mode, "states": len(paths), "edges": edges, "counterexample": violation,
            "stale_writer_counterexample": stale_violation, "continuation_after_loss": continuation}


def direct_witnesses():
    p = Profile("independent")
    s = State()
    sequence = [Request("establish"), Request("grant", target=0, value=7),
                Request("set", 0, 0, 1), Request("accept", 0, value=1),
                Request("replace", target=0, other=1), Request("resume", 1, value=1), Request("flip", 1, 0),
                Request("replace", target=1, other=2), Request("set", 2, 0, 1),
                Request("grant", target=3, value=Y), Request("set", 3, 1, 1)]
    final, successful = apply_trace(s, sequence, p)
    assert all(t["outcome"] == "commit" for t in successful)
    assert final.data == (1, 1) and final.content == 1 and final.rights == (0, 0, 7, Y)
    base = established((0, 7))
    tests = {}
    variants = {
        "confusion": [Request("replace", target=0, other=1), Request("set", 0, 0, 1)],
        "reuse": [Request("restrict", target=0, value=0), Request("grant", target=0, value=7), Request("set", 0, 0, 1)],
        "partial": [Request("mixed", 0)],
        "forgery": [Request("set", 0, 0, 1, authentic=False)],
        "amplify": [Request("restrict", target=0, value=X), Request("delegate", 0, 3, 7)],
        "exclusivity": [Request("grant", target=3, value=Y)],
    }
    for weakness, qs in variants.items():
        profile = Profile("exclusive", exclusive=True) if weakness == "exclusivity" else p
        good, reference = apply_trace(base, qs, profile)
        bad, mutant = apply_trace(base, qs, profile, weakness)
        assert bad != good, weakness
        tests[weakness] = {"reference": reference, "mutant": mutant}
    # Same observable evidence cannot yield the required two different answers.
    admission_tables = [{"answer_for_shared_observation": answer,
                         "old_denied": not answer, "replacement_admitted": answer} for answer in (False, True)]
    assert not any(t["old_denied"] and t["replacement_admitted"] for t in admission_tables)
    # A physical old producer with genuinely new transferable evidence is eligible.
    replaced, _ = apply_trace(base, [Request("replace", target=0, other=1)], p)
    refreshed, refresh_trace = apply_trace(replaced, [Request("set", 1, 0, 1)], p)
    assert refreshed.data == (1, 0)  # Deliberately no physical-source exclusion claim.
    # Split a declared pair effect and lose the executor before completing/recording it.
    proposed = candidate(base, Request("pair", 0, value=3))
    partial = replace(base, data=(1, 0))
    assert partial not in (base, proposed)
    crash_cuts = []
    for old, new in product(product((0, 1), repeat=2), repeat=2):
        for cut in range(3):
            visible = tuple(new[i] if i < cut else old[i] for i in range(2))
            if visible not in (old, new):
                crash_cuts.append({"before": old, "whole": new, "writes_before_loss": cut, "partial": visible})
    assert len(crash_cuts) == 4  # All 16 before/after pairs, all 3 death cuts.
    declared, retargeted = Request("set", 0, 0, 0), Request("set", 0, 0, 1)
    intended, _ = resolve(base, declared, p)
    swapped, _ = resolve(base, retargeted, p)
    assert intended != swapped and invariant(swapped, p)
    # These are reachable pairs, not invented invalid states. Erasing the
    # named distinction collapses histories with different future behavior.
    revoked, _ = apply_trace(base, [Request("restrict", target=0)], p)
    independent_child, _ = apply_trace(base, [Request("grant", target=3, value=Y)], p)
    delegated_child, _ = apply_trace(base, [Request("delegate", 0, 3, Y)], p)
    distinctions = []
    for name, left, right, q, profile in [
        ("issued versus never issued", established(), revoked, Request("grant", target=0, value=7), p),
        ("current authority scope", established((0, X)), established((0, Y)), Request("set", 0, 0, 1), p),
        ("delegation dependency", independent_child, delegated_child, Request("restrict", target=0), p),
        ("required accepted content", base, replace(base, content=1), Request("resume", 0, value=1), p),
        ("invariant-relevant work field", base, replace(base, data=(1, 0)), Request("set", 0, 1, 1), Profile("coupled", coupled=True)),
    ]:
        l, r = resolve(left, q, profile), resolve(right, q, profile)
        assert invariant(left, profile) and invariant(right, profile) and l != r
        distinctions.append({"distinction": name, "left": asdict(left), "right": asdict(right),
                             "future_request": q.label(), "left_result": [asdict(l[0]), l[1]],
                             "right_result": [asdict(r[0]), r[1]]})
    # Superseded requests remain stale even after a second replacement.
    old_requests = [Request("set", 0, 0, 0), Request("set", 1, 0, 0)]
    _, stale_replays = apply_trace(final, old_requests, p)
    assert all(t["outcome"] == "deny" for t in stale_replays)
    return {"success": successful, "mutants": tests, "indistinguishable_evidence": admission_tables,
            "distinction_witnesses": distinctions, "replay_after_two_replacements": stale_replays,
            "new_evidence_at_old_physical_producer": refresh_trace,
            "split_effect_crash": {"trace": ["submit pair := (1,1)", "validate", "write x := 1",
                                              "executor dies before y write / whole-effect record"],
                                   "before": asdict(base), "whole": asdict(proposed), "actual": asdict(partial),
                                   "cuts_examined": 48, "invalid_cuts": crash_cuts},
            "mutable_proposal": {"declared": declared.label(), "later_retargeted": retargeted.label(),
                                  "required": asdict(intended), "actual": asdict(swapped),
                                  "violation": "invariant and authority hold, but the declared whole effect changed"},
            "co_located_view_loss": {"before": asdict(base), "after": asdict(State()),
                                      "violation": "executor death erased continuing work, content and authority"}}


def run():
    profiles = (Profile("independent"), Profile("coupled", coupled=True), Profile("exclusive", exclusive=True))
    graphs = []
    for p in profiles:
        graphs.append(authoritative_graph(p))
        print(f"authoritative {p.name}: {graphs[-1]['states']} states, {graphs[-1]['edges']} edges", flush=True)
    p, coupled = profiles[:2]
    base, parallel = established((0, 7)), established((0, 7), (3, Y))
    cases = [
        ("replacement race", base, (Request("set", 0, 0, 1), Request("replace", target=0, other=1)), (0, -1), p),
        ("revocation race", base, (Request("set", 0, 0, 1), Request("restrict", target=0)), (0, -1), p),
        ("compatible fields", parallel, (Request("set", 0, 0, 1), Request("set", 3, 1, 1)), (0, 3), p),
        ("coupled fields", parallel, (Request("set", 0, 0, 1), Request("set", 3, 1, 1)), (0, 3), coupled),
        ("exclusive grant race", established(), (Request("grant", target=0, value=X), Request("grant", target=3, value=Y)), (-1, -1), profiles[2]),
        ("delegation versus parent restriction", base, (Request("delegate", 0, 3, Y), Request("restrict", target=0, value=X)), (0, -1), p),
        ("denied composite and loss", base, (Request("mixed", 0),), (0,), p),
        ("whole pair and loss", base, (Request("pair", 0, value=3),), (0,), p),
    ]
    flights = [flight_explore(*case) for case in cases]
    assert flights[2]["both_commit_reachable"] and not flights[3]["both_commit_reachable"]
    assert not flights[4]["both_commit_reachable"]
    flights.append(flight_explore("lost acknowledgement then replay", base,
                                  (Request("flip", 0, 0), Request("flip", 0, 0)), (0, 0), p,
                                  replay_after=True))
    assert flights[-1]["repeated_flip_returns_to_start"]
    mutants = [flight_explore(*cases[i], weakness="stale_view") for i in (0, 1, 3, 4, 5)]
    return {"format": 1, "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "authoritative_graphs": graphs, "interleavings": flights, "detached_validation_mutants": mutants,
            "history_oracle": history_attacks(), "content_boundary": [content_explore(m) for m in ("copy", "live", "hash_only")],
            "witnesses": direct_witnesses()}


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without -O: verification assertions must be enabled.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = run()
    if args.output:
        args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "all checks passed; all deliberate mutants detected",
                      "authoritative_states": sum(g["states"] for g in results["authoritative_graphs"]),
                      "interleaving_states": sum(g["states"] for g in results["interleavings"]),
                      "history_cases": results["history_oracle"]["cases"]}, sort_keys=True))
===== END FILE: docs/research/kernel-0/kernel0_finite_model.py =====

===== BEGIN FILE: docs/research/kernel-0/kernel0_service.py =====
#!/usr/bin/env python3
"""Still-live finite research service. See Kernel-0-Realization-Experiment.md.

No model imports, persistence, network listener, caller-asserted identity, or
state-loading endpoint. Bootstrap descriptors/configuration are trusted input.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import os
import socket
import sys
import threading


CONTENTS = ("accepted\u0000zero\n", "accepted\u0000one\n")
POSITIONS = (0, 0, 0, 1)
MAX_FRAME = 4096


@dataclass(frozen=True)
class View:
    established: bool = False
    data: tuple = (0, 0)
    content: str | None = None
    issued: int = 0
    rights: tuple = (0, 0, 0, 0)
    parents: tuple = (-1, -1, -1, -1)
    cycle: tuple = (0, 0, 0)  # Only used in the separate cycle profile.


@dataclass(frozen=True)
class Proposal:
    kind: str
    target: int = 0
    value: int | str = 0
    other: int = 0


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate field")
        out[key] = value
    return out


def decode(raw):
    obj = json.loads(raw, object_pairs_hook=unique_object)
    if type(obj) is not dict:
        raise ValueError("object required")
    if obj == {"kind": "read"}:
        return Proposal("read")
    if set(obj) != {"kind", "target", "value", "other"}:
        raise ValueError("exact proposal fields required")
    k, t, v, o = (obj[key] for key in ("kind", "target", "value", "other"))
    if type(k) is not str or k not in {
        "establish", "grant", "restrict", "replace", "delegate", "set",
        "flip", "pair", "accept", "resume", "mixed", "cycle",
    }:
        raise ValueError("unknown effect")
    if type(t) is not int or t not in range(4) or type(o) is not int or o not in range(4):
        raise ValueError("invalid context or target")
    if k in ("accept", "resume"):
        if type(v) is not str or v not in CONTENTS:
            raise ValueError("content outside finite witness")
    elif type(v) is not int or v not in range(8):
        raise ValueError("invalid value")
    if k in ("set", "flip") and (t > 1 or v > 1):
        raise ValueError("invalid field")
    if k == "pair" and v > 3 or k == "cycle" and (t > 2 or v > 1):
        raise ValueError("invalid composite or cycle")
    return Proposal(k, t, v, o)


def valid(s, profile):
    if not s.established:
        return s == View()
    if s.content not in CONTENTS or any(x not in (0, 1) for x in s.data + s.cycle):
        return False
    if profile == "coupled" and sum(s.data) > 1:
        return False
    active = [i for i, mask in enumerate(s.rights) if mask]
    if profile == "exclusive" and len(active) > 1:
        return False
    if any(sum(POSITIONS[a] == p for a in active) > 1 for p in (0, 1)):
        return False
    if any(not s.issued & (1 << a) for a in active):
        return False
    for child, parent in enumerate(s.parents):
        if parent != -1 and (child != 3 or parent not in (0, 1, 2)
                             or not s.rights[child] or s.rights[child] & ~s.rights[parent]):
            return False
    return all(0 <= mask <= 7 for mask in s.rights)


def candidate(s, a, q, profile):
    """Concrete policy, independently implemented from the model oracle."""
    k, t, v, o = q.kind, q.target, q.value, q.other
    if a not in (-1, 0, 1, 2, 3):
        return None
    if k == "establish":
        return replace(s, established=True, content=CONTENTS[0]) if a == -1 and not s.established else None
    if not s.established:
        return None
    if k in ("grant", "restrict", "replace", "delegate"):
        masks, parents = list(s.rights), list(s.parents)
        issued = s.issued

        def withdraw_or_limit(context, mask):
            masks[context] = mask
            if not mask:
                parents[context] = -1
            for child in range(4):
                if parents[child] == context:
                    masks[child] &= mask
                    if not masks[child]:
                        parents[child] = -1

        if k == "restrict":
            if a != -1 or not masks[t] or v & ~masks[t]:
                return None
            withdraw_or_limit(t, v)
        else:
            destination = o if k == "replace" else t
            if issued & (1 << destination):
                return None
            if k == "delegate":
                if a not in (0, 1, 2) or t != 3 or not v or v & ~masks[a]:
                    return None
                masks[t], parents[t] = v, a
            elif k == "grant":
                if a != -1 or not v:
                    return None
                masks[t], parents[t] = v, -1
            else:
                if a != -1 or not masks[t] or POSITIONS[t] != POSITIONS[o]:
                    return None
                previous = masks[t]
                withdraw_or_limit(t, 0)
                masks[o], parents[o] = previous, -1
            issued |= 1 << destination
        return replace(s, issued=issued, rights=tuple(masks), parents=tuple(parents))

    required = {"set": 1 << t, "flip": 1 << t, "pair": 3,
                "accept": 4, "resume": 1, "mixed": 1, "cycle": 1}.get(k)
    if a < 0 or required is None or required & ~s.rights[a]:
        return None
    if k == "mixed":
        return None  # Its authority-grant portion is forbidden to every worker.
    if k == "accept":
        return replace(s, content=v)  # Actual immutable decoded string retained.
    if k == "resume":
        return replace(s, data=(CONTENTS.index(v), s.data[1])) if v == s.content else None
    if k == "cycle":
        if profile != "cycle" or s.cycle[(t + 1) % 3] != v:
            return None
        return replace(s, cycle=tuple(1 if i == t else bit for i, bit in enumerate(s.cycle)))
    data = list(s.data)
    if k == "pair":
        data = [v & 1, v >> 1]
    else:
        data[t] = v if k == "set" else 1 - data[t]
    return replace(s, data=tuple(data))


class Boundary:
    def __init__(self, profile):
        if profile not in ("independent", "coupled", "exclusive", "cycle"):
            raise ValueError("unknown profile")
        self.profile, self.state = profile, View()
        self.lock = threading.Lock()

    def resolve(self, context, q, gate=lambda stage: None):
        with self.lock:
            if q is None or q.kind == "read":
                return {"outcome": "deny" if q is None else "read", "state": asdict(self.state)}
            successor = candidate(self.state, context, q, self.profile)
            admitted = successor is not None and valid(successor, self.profile)
            gate("validated")
            if admitted:
                self.state = successor  # Sole post-bootstrap protected publication.
            reply = {"outcome": "commit" if admitted else "deny", "state": asdict(self.state)}
        gate("published")
        return reply


def serve(config):
    boundary = Boundary(config["profile"])
    gate_config = config.get("gate")  # Trusted test bootstrap only; no wire control API.
    gate_used = threading.Event()

    def handle(lane, context, fd):
        def gate(stage):
            if (gate_config and not gate_used.is_set() and gate_config["lane"] == lane
                    and gate_config["kind"] == q.kind and gate_config["stage"] == stage):
                gate_used.set()
                os.write(gate_config["event_fd"], b"G")
                os.read(gate_config["release_fd"], 1)

        with socket.socket(fileno=fd) as conn, conn.makefile("rb") as incoming:
            while True:
                raw = incoming.readline(MAX_FRAME + 1)
                if not raw or len(raw) > MAX_FRAME or not raw.endswith(b"\n"):
                    return  # Incomplete/oversized proposal has no protected effect.
                try:
                    q = decode(raw)
                except (ValueError, TypeError, RecursionError):
                    q = None
                if q is not None:
                    gate("received")
                reply = boundary.resolve(context, q, gate)
                try:
                    conn.sendall(json.dumps(reply).encode() + b"\n")
                except (BrokenPipeError, ConnectionResetError):
                    return  # Lost acknowledgement does not undo publication.

    threads = []
    for lane, (context, fd) in enumerate(config["channels"]):
        if context not in (-1, 0, 1, 2, 3):
            raise ValueError("invalid trusted channel association")
        thread = threading.Thread(target=handle, args=(lane, context, fd), daemon=True)
        thread.start()
        threads.append(thread)
    print("ready", flush=True)
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    serve(json.loads(sys.argv[1]))
===== END FILE: docs/research/kernel-0/kernel0_service.py =====

===== BEGIN FILE: docs/research/kernel-0/kernel0_realization_check.py =====
#!/usr/bin/env python3
"""Model-derived checks for the still-live service; run without -O on Unix."""
from __future__ import annotations

import argparse
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from hashlib import sha256
from itertools import permutations, product
import json
import os
from pathlib import Path
import re
import select
import socket
import subprocess
import sys
import threading
import time

from hypothesis import given, settings, strategies as st, find, example
import hypothesis
import kernel0_finite_model as m
import kernel0_service as c

HERE = Path(__file__).resolve().parent
PROFILES = (m.Profile('independent'), m.Profile('coupled', coupled=True),
            m.Profile('exclusive', exclusive=True))
CATALOG = tuple(m.catalog())
METRICS = Counter()
EVIDENCE = {}


def wire(q):
    out = {key: getattr(q, key) for key in ('kind', 'target', 'value', 'other')}
    if q.kind in ('accept', 'resume'):
        out['value'] = c.CONTENTS[q.value]
    if not q.authentic:
        out['authentic'] = True  # Deliberate caller assertion: forbidden schema field.
    return out


def abstract(raw):
    return m.State(raw['established'], tuple(raw['data']),
                   -1 if raw['content'] is None else c.CONTENTS.index(raw['content']),
                   raw['issued'], tuple(raw['rights']), tuple(raw['parents']))


def concrete(s):
    return c.View(s.established, s.data, None if s.content == -1 else c.CONTENTS[s.content],
                  s.issued, s.rights, s.parents)


def packet(obj):
    return json.dumps(obj, separators=(',', ':')).encode() + b'\n'


def receive(conn):
    # Byte-at-a-time intentionally leaves no buffered reply in a killed executor.
    buf = bytearray()
    while not buf.endswith(b'\n'):
        part = conn.recv(1)
        if not part:
            raise EOFError('peer closed before reply')
        buf.extend(part)
    return json.loads(buf)


class Service:
    # Three independent endpoints denote a0; none can upgrade itself to manager.
    CONTEXTS = (-1, 0, 1, 2, 3, 0, 0, -1)

    def __init__(self, profile='independent', gate=None):
        pairs = [socket.socketpair() for _ in self.CONTEXTS]
        self.clients = [p[0] for p in pairs]
        self.children = []
        for conn in self.clients:
            conn.settimeout(10)
        config = {'profile': profile,
                  'channels': [(a, p[1].fileno()) for a, p in zip(self.CONTEXTS, pairs)]}
        inherited = [p[1].fileno() for p in pairs]
        self.event, event_write = os.pipe()
        release_read, self.release = os.pipe()
        if gate:
            config['gate'] = dict(gate, event_fd=event_write, release_fd=release_read)
            inherited += [event_write, release_read]
        self.process = subprocess.Popen([sys.executable, str(HERE / 'kernel0_service.py'), json.dumps(config)],
                                        pass_fds=inherited, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=0)
        for _, server in pairs:
            server.close()
        os.close(event_write)
        os.close(release_read)
        assert select.select([self.process.stdout], [], [], 10)[0], 'service startup timed out'
        assert self.process.stdout.readline() == b'ready\n'

    def call(self, obj, lane=0):
        self.clients[lane].sendall(packet(obj))
        return receive(self.clients[lane])

    def request(self, q, lane=None):
        if lane is None:
            lane = self.CONTEXTS.index(q.evidence)
        return self.call(wire(q), lane)

    def read(self, lane=0):
        return self.call({'kind': 'read'}, lane)['state']

    def setup(self, *grants):
        assert self.request(m.Request('establish'))['outcome'] == 'commit'
        for a, rights in grants:
            assert self.request(m.Request('grant', target=a, value=rights))['outcome'] == 'commit'
        return abstract(self.read())

    def gated(self):
        assert select.select([self.event], [], [], 10)[0], 'gate timed out'
        assert os.read(self.event, 1) == b'G'

    def unblock(self):
        os.write(self.release, b'R')

    def worker(self, lane, obj, mode='send'):
        # A fresh exec, not a forked Python heap. Only its own endpoint is inherited.
        proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker',
                                 str(self.clients[lane].fileno()), mode, json.dumps(obj)],
                                pass_fds=[self.clients[lane].fileno()], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, bufsize=0)
        self.children.append(proc)
        assert select.select([proc.stdout], [], [], 10)[0]
        assert proc.stdout.readline() == b'private-ready\n'
        return proc

    def close(self):
        worker_errors = []
        for proc in self.children:
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)
            error = proc.stderr.read().decode()
            if error or proc.returncode > 0:
                worker_errors.append((proc.returncode, error))
            proc.stdout.close()
            proc.stderr.close()
        for conn in self.clients:
            conn.close()
        os.close(self.event)
        os.close(self.release)
        if self.process.poll() is None:
            self.process.terminate()
        self.process.wait(timeout=10)
        errors = self.process.stderr.read().decode()
        self.process.stdout.close()
        self.process.stderr.close()
        assert not errors, errors
        assert not worker_errors, worker_errors

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def worker_main(fd, mode, obj):
    # Candidate bytes and the serialized proposal exist in this process before loss.
    os.dup2(fd, 64)  # Deliberately identical descriptor label in every executor.
    if fd != 64:
        os.close(fd)
    conn = socket.socket(fileno=64)
    conn.settimeout(10)  # Match inherited O_NONBLOCK to Python's timeout wrapper.
    raw = packet(obj)
    print('private-ready', flush=True)
    if mode == 'before':
        threading.Event().wait()
    if mode == 'partial':
        conn.sendall(raw[:len(raw)//2])
        print('partial-sent', flush=True)
        threading.Event().wait()
    if mode == 'resume':
        conn.sendall(packet({'kind': 'read'}))
        retained = receive(conn)['state']['content']
        raw = packet(dict(kind='resume', target=0, value=retained, other=0))
    conn.sendall(raw)
    if mode == 'no-ack':
        threading.Event().wait()
    print(json.dumps(receive(conn)), flush=True)
    if mode == 'ack-stay':
        threading.Event().wait()


def check_one(service, s, q, p):
    expected, outcome = m.resolve(s, q, p)
    response = service.request(q)
    actual = abstract(response['state'])
    assert (actual, response['outcome']) == (expected, outcome), (s, q, response, expected, outcome)
    m.check_edge(s, q, actual, outcome, p)
    METRICS['live_requests'] += 1
    METRICS['live_' + outcome] += 1
    METRICS['kind_' + q.kind + '_' + outcome] += 1
    return actual


def graph_differential():
    parsed = [(q, c.decode(packet(wire(q)))) for q in CATALOG]
    results = []
    for profile in PROFILES:
        queue, seen = deque([m.State()]), {m.State()}
        count = Counter()
        while queue:
            s = queue.popleft()
            view = concrete(s)
            for q, decoded in parsed:
                expected, outcome = m.resolve(s, q, profile)
                candidate = c.candidate(view, q.evidence, decoded, profile.name)
                accepted = candidate is not None and c.valid(candidate, profile.name)
                actual = candidate if accepted else view
                assert (actual, 'commit' if accepted else 'deny') == (concrete(expected), outcome), (s, q)
                count['edges'] += 1
                count[outcome] += 1
                if expected not in seen:
                    seen.add(expected)
                    queue.append(expected)
        result = dict(profile=profile.name, states=len(seen), **count)
        results.append(result)
        print('differential graph:', result, flush=True)
    EVIDENCE['differential_graphs'] = results


def parse_label(label, authentic=True):
    match = re.fullmatch(r'(\w+)\((management|a[0-3]), (\d), (\d), (\d)\)', label)
    assert match, label
    kind, actor, target, value, other = match.groups()
    return m.Request(kind, -1 if actor == 'management' else int(actor[1]),
                     int(target), int(value), int(other), authentic)


def recorded_traces():
    evidence = json.loads((HERE / 'Kernel-0-Finite-Model-results.json').read_text())
    assert evidence['source_sha256'] == sha256((HERE / 'kernel0_finite_model.py').read_bytes()).hexdigest()
    witnesses = evidence['witnesses']
    traces = {'success': witnesses['success'], **{k: v['reference'] for k, v in witnesses['mutants'].items()}}
    traces['new_current_evidence'] = witnesses['new_evidence_at_old_physical_producer']
    for name, trace in traces.items():
        p = PROFILES[2] if name == 'exclusivity' else PROFILES[0]
        with Service(p.name) as service:
            s = m.State()
            if name != 'success':
                s = service.setup((0, 7))
            if name == 'new_current_evidence':
                s = check_one(service, s, m.Request('replace', target=0, other=1), p)
            for step in trace:
                assert asdict(s) == {k: tuple(v) if k in ('data', 'rights', 'parents') else v
                                     for k, v in step['before'].items()}
                q = parse_label(step['event'], name != 'forgery')
                s = check_one(service, s, q, p)
                assert json.loads(json.dumps(asdict(s))) == step['after']
            if name == 'success':
                for step in witnesses['replay_after_two_replacements']:
                    s = check_one(service, s, parse_label(step['event']), p)
    # Replay the model's shortest detached-validation counterexamples against the
    # real service in their recorded resolution orders. Observations stay advisory.
    for fixture in evidence['detached_validation_mutants']:
        name = fixture['name']
        p = PROFILES[2] if name == 'exclusive grant race' else PROFILES[1] if name == 'coupled fields' else PROFILES[0]
        grants = () if name == 'exclusive grant race' else ((0, 7), (3, 2)) if name == 'coupled fields' else ((0, 7),)
        with Service(p.name) as service:
            s, requests = service.setup(*grants), {}
            for event in fixture['counterexample']['trace']:
                if ': invoke/copy ' in event:
                    index, label = event.split(': invoke/copy ')
                    requests[int(index)] = parse_label(label)
                elif ': observe ' in event:
                    service.read()
                elif ': commit -> ' in event or ': deny -> ' in event:
                    s = check_one(service, s, requests[int(event.split(':')[0])], p)
            assert json.loads(json.dumps(asdict(s))) == fixture['counterexample']['expected_state']
    EVIDENCE['recorded_trace_groups'] = len(traces) + len(evidence['detached_validation_mutants'])


def authority_and_bypass():
    p = PROFILES[0]
    with Service() as service:
        s = service.setup((0, 7))
        for order in (0, 1):
            # Both orders tested with successive fresh replacements.
            work = m.Request('flip', order)
            replacement = m.Request('replace', target=order, other=order + 1)
            for q in ((work, replacement) if order == 0 else (replacement, work)):
                s = check_one(service, s, q, p)
        # Old endpoint and replacement endpoint use same apparent request identity.
        payload = wire(m.Request('set', 0, value=1))
        assert service.call(payload, 1)['outcome'] == 'deny'
        assert service.call(payload, 3)['outcome'] == 'commit'
        s = abstract(service.read())
        for field in ('evidence', 'context', 'authentic', 'manager', 'state', 'rights'):
            bad = dict(payload, **{field: -1})
            assert service.call(bad, 1)['outcome'] == 'deny'
            assert abstract(service.read()) == s
        # Worker cannot become manager even with an otherwise valid management frame.
        assert service.call(wire(m.Request('grant', target=3, value=2)), 3)['outcome'] == 'deny'
        snapshot = service.read()
        snapshot['rights'][2] = 0
        snapshot['data'][0] = 0
        snapshot['content'] = 'changed'
        assert abstract(service.read()) == s
        s = check_one(service, s, m.Request('accept', 2, value=1), p)
        candidate = wire(m.Request('accept', 2, value=1))
        candidate['value'] = c.CONTENTS[0]
        assert service.read()['content'] == c.CONTENTS[1]
        s = check_one(service, s, m.Request('mixed', 2), p)
        s = check_one(service, s, m.Request('flip', 2), p)
        s = check_one(service, s, m.Request('flip', 2), p)
        assert abstract(service.read()) == s
    EVIDENCE['authority_and_bypass'] = 'pass: both replacement orders, same payload/different endpoint, forgery, copies, mixed denial, replay'
    with Service() as service:
        service.setup((0, 7))
        assert service.request(m.Request('replace', target=0, other=1))['outcome'] == 'commit'
        for lane, outcome in ((1, 'deny'), (2, 'commit')):
            proc = service.worker(lane, wire(m.Request('set', 0, value=1)))
            assert select.select([proc.stdout], [], [], 10)[0]
            assert json.loads(proc.stdout.readline())['outcome'] == outcome
            proc.wait(timeout=10)
    EVIDENCE['confusable_descriptor_label'] = 'old and replacement both use local fd 64 and identical JSON; old denied, replacement committed'


def kill(proc):
    proc.kill()
    proc.wait(timeout=10)
    assert proc.returncode < 0


def loss_cuts():
    observations = []
    for stage in ('before', 'partial', 'received', 'validated', 'published'):
        gate = None if stage in ('before', 'partial') else {'lane': 1, 'kind': 'pair', 'stage': stage}
        with Service(gate=gate) as service:
            before = service.setup((0, 7))
            q = m.Request('pair', 0, value=3)
            proc = service.worker(1, wire(q), stage if stage in ('before', 'partial') else 'send')
            if stage == 'partial':
                assert select.select([proc.stdout], [], [], 10)[0]
                assert proc.stdout.readline() == b'partial-sent\n'
            elif gate:
                service.gated()
            kill(proc)
            # Remove the supervisor's duplicate so the service really sees EOF.
            service.clients[1].close()
            if stage in ('received', 'validated', 'published'):
                service.unblock()
                # Synchronize through a read on a separate a0 channel; validated
                # gate owns the lock, received gate may not yet own it.
                for _ in range(100):
                    after = abstract(service.read())
                    if after.data == (1, 1):
                        break
                    time.sleep(.005)
                assert after == m.resolve(before, q, PROFILES[0])[0]
            else:
                after = abstract(service.read())
                assert after == before
            assert after.data in ((0, 0), (1, 1))
            observations.append({'cut': stage, 'after': asdict(after), 'executor_returncode': proc.returncode})
    # A validated old request holds the lock; replacement cannot slip in.
    with Service(gate={'lane': 1, 'kind': 'pair', 'stage': 'validated'}) as service:
        before = service.setup((0, 7))
        proc = service.worker(1, wire(m.Request('pair', 0, value=3)))
        service.gated()
        service.clients[0].sendall(packet(wire(m.Request('replace', target=0, other=1))))
        assert not select.select([service.clients[0]], [], [], .05)[0]
        kill(proc)
        service.clients[1].close()
        service.unblock()
        reply = receive(service.clients[0])
        assert reply['outcome'] == 'commit' and reply['state']['data'] == [1, 1]
        assert reply['state']['rights'] == [0, 7, 0, 0]
    # Real lost acknowledgement followed by an authorized replay on another copy.
    with Service(gate={'lane': 1, 'kind': 'flip', 'stage': 'published'}) as service:
        service.setup((0, 7))
        proc = service.worker(1, wire(m.Request('flip', 0)))
        service.gated()
        assert service.read()['data'] == [1, 0]
        kill(proc)
        service.clients[1].close()
        service.unblock()
        assert service.request(m.Request('flip', 0), lane=5)['state']['data'] == [0, 0]
    # Accepted bytes survive the sole producing process. Replacement consumes them.
    with Service() as service:
        service.setup((0, 7))
        proc = service.worker(1, wire(m.Request('accept', 0, value=1)), 'ack-stay')
        assert select.select([proc.stdout], [], [], 10)[0]
        assert json.loads(proc.stdout.readline())['outcome'] == 'commit'
        kill(proc)
        service.clients[1].close()
        assert service.request(m.Request('replace', target=0, other=1))['outcome'] == 'commit'
        replacement = service.worker(2, {}, 'resume')
        assert select.select([replacement.stdout], [], [], 10)[0]
        assert json.loads(replacement.stdout.readline())['state']['data'] == [1, 0]
        replacement.wait(timeout=10)
    with Service() as service:
        before = service.setup((0, 7))
        proc = service.worker(1, wire(m.Request('accept', 0, value=1)), 'before')
        kill(proc)
        assert abstract(service.read()) == before
    EVIDENCE['executor_loss'] = observations
    EVIDENCE['content_continuation_and_lost_ack_replay'] = 'pass'


def stale_gate():
    for operation in ('restrict', 'replace'):
        with Service(gate={'lane': 1, 'kind': 'set', 'stage': 'received'}) as service:
            service.setup((0, 7))
            old_view = service.read(1)
            proc = service.worker(1, wire(m.Request('set', 0, value=1)))
            service.gated()
            change = m.Request(operation, target=0, other=1)
            assert service.request(change)['outcome'] == 'commit'
            service.unblock()
            assert select.select([proc.stdout], [], [], 10)[0]
            assert json.loads(proc.stdout.readline())['outcome'] == 'deny'
            proc.wait(timeout=10)
            assert old_view['rights'][0] == 7 and service.read()['rights'][0] == 0
            # This new invocation starts strictly after the change's acknowledgement.
            assert service.request(m.Request('set', 0, value=1))['outcome'] == 'deny'
    EVIDENCE['stale_read_and_completed_change'] = 'pass: ingress held across acknowledged revocation/replacement'


def concurrent(service, requests):
    barrier = threading.Barrier(len(requests))
    def issue(item):
        lane, obj = item
        barrier.wait(timeout=10)
        start = time.monotonic_ns()
        response = service.call(obj, lane)
        end = time.monotonic_ns()
        return start, end, response
    with ThreadPoolExecutor(max_workers=len(requests)) as pool:
        events = list(pool.map(issue, requests))
    if any(a[0] < b[1] and b[0] < a[1] for i, a in enumerate(events) for b in events[i+1:]):
        METRICS['observed_overlapping_histories'] += 1
    return events


def whole_history(initial, qs, events, profile, final):
    edges = {(i, j) for i in range(len(qs)) for j in range(len(qs)) if events[i][1] < events[j][0]}
    for order in permutations(range(len(qs))):
        ranks = {i: n for n, i in enumerate(order)}
        if any(ranks[i] >= ranks[j] for i, j in edges):
            continue
        state = initial
        for i in order:
            state, outcome = m.resolve(state, qs[i], profile)
            if (state, outcome) != (abstract(events[i][2]['state']), events[i][2]['outcome']):
                break
        else:
            if state == final:
                return order
    return None


def concurrency_attacks():
    results = []
    for p in PROFILES:
        with Service(p.name) as service:
            if p.exclusive:
                initial = service.setup()
                qs = [m.Request('grant', target=0, value=1), m.Request('grant', target=3, value=2)]
                lanes = (0, 7)
            else:
                initial = service.setup((0, 7), (3, 2))
                qs = [m.Request('set', 0, 0, 1), m.Request('set', 3, 1, 1)]
                lanes = (1, 4)
                assert service.read(1)['data'] == service.read(4)['data'] == [0, 0]
            events = concurrent(service, [(lane, wire(q)) for lane, q in zip(lanes, qs)])
            outcomes = [event[2]['outcome'] for event in events]
            witness = whole_history(initial, qs, events, p, abstract(service.read()))
            assert witness is not None
            assert outcomes.count('commit') == (1 if p.coupled or p.exclusive else 2)
            results.append({'profile': p.name, 'outcomes': outcomes, 'witness': witness, 'concurrent': True})
    with Service() as service:
        initial = service.setup((0, 7))
        qs = [m.Request('delegate', 0, 3, 2), m.Request('restrict', target=0, value=1)]
        events = concurrent(service, [(1, wire(qs[0])), (0, wire(qs[1]))])
        final = abstract(service.read())
        witness = whole_history(initial, qs, events, PROFILES[0], final)
        assert witness is not None and final.rights == (1, 0, 0, 0)
        results.append({'profile': 'delegation/restriction', 'witness': witness, 'concurrent': True})
    # Same live commit boundary, separate three-bit model extension; all attempts
    # observed 000, but each current guard is re-evaluated under the real lock.
    for order in permutations(range(3)):
        with Service('cycle') as service:
            service.setup((0, 7))
            for lane in (1, 5, 6):
                assert service.read(lane)['cycle'] == [0, 0, 0]
            qs = [{'kind': 'cycle', 'target': i, 'value': 0, 'other': 0} for i in order]
            events = concurrent(service, list(zip((1, 5, 6), qs)))
            accepted = tuple(order[i] for i, event in enumerate(events) if event[2]['outcome'] == 'commit')
            ops = [(lambda s, r=(i + 1) % 3: s[r] == 0,
                    lambda s, w=i: tuple(1 if j == w else bit for j, bit in enumerate(s))) for i in range(3)]
            final = tuple(service.read()['cycle'])
            witness = m.serial_witness((0, 0, 0), ops, accepted, frozenset(), final)
            assert len(accepted) < 3 and witness is not None
            results.append({'profile': 'cycle', 'submission_labels': order, 'accepted': accepted,
                            'final': final, 'witness': witness})
    EVIDENCE['concurrent_attacks'] = results


@settings(max_examples=200, deadline=None, derandomize=True, database=None)
@given(st.sampled_from(PROFILES), st.lists(st.integers(0, 4095), min_size=1, max_size=50))
@example(PROFILES[0], [1477, 2670, 705, 1, 1, 1, 1])
def generated_sequences(profile, choices):
    with Service(profile.name) as service:
        state = m.State()
        state = check_one(service, state, m.Request('establish'), profile)
        for choice in choices:
            # Three quarters of choices select model-enabled operations. The rest
            # attack stale or otherwise inadmissible proposals. No assume/filter.
            pool = [q for q in CATALOG if m.resolve(state, q, profile)[1] == 'commit'] if choice % 4 else CATALOG
            if not pool:
                pool = CATALOG  # Exhausted authority permits only denial; no liveness promise.
            q = pool[(choice // 4) % len(pool)]
            if choice % 17 == 0:
                q = replace(q, authentic=False)
            state = check_one(service, state, q, profile)
            copied = service.read()
            copied['data'][0] = 99
            copied['rights'][0] = 7
            assert abstract(service.read()) == state
            if choice % 97 == 0:
                proc = service.worker(6, wire(m.Request('accept', 0, value=1)), 'before')
                kill(proc)
                assert abstract(service.read()) == state
                METRICS['generated_executor_losses'] += 1
        METRICS['generated_sequences'] += 1


@settings(max_examples=100, deadline=None, derandomize=True, database=None)
@given(st.sampled_from(PROFILES), st.tuples(st.integers(0, 99), st.integers(0, 99), st.integers(0, 99)))
def generated_histories(profile, choices):
    with Service(profile.name) as service:
        initial = service.setup((0, 7))
        if not profile.exclusive:
            assert service.request(m.Request('grant', target=3, value=2))['outcome'] == 'commit'
            initial = abstract(service.read())
        qs = []
        for actor, choice in zip((-1, 0, 3), choices):
            pool = [q for q in CATALOG if q.evidence == actor]
            qs.append(pool[choice % len(pool)])
        events = concurrent(service, [(lane, wire(q)) for lane, q in zip((0, 1, 4), qs)])
        assert whole_history(initial, qs, events, profile, abstract(service.read())) is not None, (qs, events)
        METRICS['generated_concurrent_histories'] += 1


def malformed_ingress():
    samples = [b'{}\n', b'[]\n', b'null\n', b'{"kind":"read","kind":"establish"}\n',
               b'\xff\n', b'{"kind":\n', packet(dict(kind='set', target=True, value=1, other=0)),
               packet(dict(kind='set', target=-1, value=1, other=0)),
               packet(dict(kind='accept', target=0, value={'url': 'live'}, other=0)),
               b'[' * 1100 + b']' * 1100 + b'\n']
    with Service() as service:
        state = service.setup((0, 7))
        for raw in samples:
            service.clients[1].sendall(raw)
            assert receive(service.clients[1])['outcome'] == 'deny'
            assert abstract(service.read()) == state
        # Retargeting the client-owned object after send cannot alter copied bytes.
        obj = wire(m.Request('set', 0, value=0))
        service.clients[1].sendall(packet(obj))
        obj['value'] = 1
        assert receive(service.clients[1])['state']['data'][0] == 0
        service.clients[5].sendall(b'x' * (c.MAX_FRAME + 1))
        assert service.clients[5].recv(1) == b''
        assert abstract(service.read()) == state
    EVIDENCE['malformed_ingress_cases'] = len(samples) + 2


@settings(max_examples=150, deadline=None, derandomize=True, database=None)
@given(st.binary(max_size=1000))
def generated_wire(raw):
    # Exercise actual service ingress, not just the decoder in isolation.
    with Service() as service:
        before = service.setup((0, 7))
        # This envelope always has a forbidden field, irrespective of random bytes.
        obj = dict(wire(m.Request('set', 0, value=1)), evidence=list(raw))
        encoded = packet(obj)
        if len(encoded) > c.MAX_FRAME:
            encoded = b'{"evidence":' + json.dumps(list(raw[:200])).encode() + b'}\n'
        service.clients[1].sendall(encoded)
        assert receive(service.clients[1])['outcome'] == 'deny'
        assert abstract(service.read()) == before
        METRICS['generated_bypass_envelopes'] += 1


def mutation_checks():
    # Mutate concrete reducer behavior locally; never expose a weakness switch on
    # the service wire. Hypothesis finds and shrinks differences from model policy.
    witnesses = {}
    base = m.established((0, 7))
    for name in ('reuse', 'confusion', 'partial', 'amplify', 'stale_view'):
        operations = {
            'reuse': [m.Request('restrict', target=0), m.Request('grant', target=0, value=7), m.Request('set', 0, value=1)],
            'confusion': [m.Request('replace', target=0, other=1), m.Request('set', 0, value=1)],
            'partial': [m.Request('mixed', 0)],
            'amplify': [m.Request('restrict', target=0, value=1), m.Request('delegate', 0, 3, 7)],
            'stale_view': [m.Request('restrict', target=0), m.Request('set', 0, value=1)],
        }[name]
        def mismatch(indices):
            expected, actual = base, concrete(base)
            for index in indices:
                q = operations[index]
                expected, result = m.resolve(expected, q, PROFILES[0])
                decoded, actor = c.decode(packet(wire(q))), q.evidence
                source = actual
                if name == 'reuse' and q.kind == 'grant' and not source.rights[q.target]:
                    source = replace(source, issued=source.issued & ~(1 << q.target))
                if name == 'confusion' and actor == 0 and not source.rights[0]:
                    actor = next((i for i in range(3) if source.rights[i]), actor)
                if name == 'amplify' and q.kind == 'delegate':
                    source = replace(source, rights=(7,) + source.rights[1:])
                if name == 'stale_view' and q.kind == 'set':
                    source = replace(source, rights=base.rights)
                out = c.candidate(source, actor, decoded, 'independent')
                commit = out is not None and c.valid(out, 'independent')
                if commit:
                    if name == 'stale_view' and q.kind == 'set':
                        out = replace(out, rights=actual.rights)
                    if name == 'amplify' and q.kind == 'delegate':
                        out = replace(out, rights=(actual.rights[0],) + out.rights[1:])
                    actual = out
                if name == 'partial' and q.kind == 'mixed':
                    actual = replace(actual, data=(1, actual.data[1]))
                if (actual, 'commit' if commit else 'deny') != (concrete(expected), result):
                    return {'at_request': asdict(q), 'expected_state': asdict(expected),
                            'actual_state': asdict(actual), 'expected_outcome': result,
                            'actual_outcome': 'commit' if commit else 'deny'}
            return None
        minimized = find(st.lists(st.integers(0, len(operations)-1), min_size=1, max_size=8),
                         lambda indices: mismatch(indices) is not None,
                         settings=settings(max_examples=1000, deadline=None, derandomize=True, database=None))
        counterexample = mismatch(minimized)
        assert counterexample['at_request']['kind'] == {
            'reuse': 'grant', 'confusion': 'set', 'partial': 'mixed',
            'amplify': 'delegate', 'stale_view': 'set'}[name]
        witnesses[name] = dict(trace=[asdict(operations[i]) for i in minimized], **counterexample)
    EVIDENCE['deliberate_concrete_mutants'] = witnesses


def run(output, graph=True):
    if not __debug__:
        raise SystemExit('Run without -O; assertions are the test oracle.')
    for test in ([graph_differential] if graph else []) + [recorded_traces, authority_and_bypass,
            stale_gate, loss_cuts, concurrency_attacks, malformed_ingress, generated_sequences,
            generated_histories, generated_wire, mutation_checks]:
        test()
        print('passed:', test.__name__, flush=True)
    required = {'establish', 'grant', 'restrict', 'replace', 'delegate', 'set', 'flip', 'pair', 'accept', 'resume'}
    assert all(METRICS['kind_' + kind + '_commit'] > 0 for kind in required)
    assert METRICS['observed_overlapping_histories'] > 0
    EVIDENCE['metrics'] = dict(METRICS)
    EVIDENCE['source_sha256'] = {name: sha256((HERE / name).read_bytes()).hexdigest() for name in
        ('kernel0_service.py', 'kernel0_realization_check.py', 'kernel0_finite_model.py')}
    EVIDENCE['runtime'] = {'python': sys.version, 'hypothesis': hypothesis.__version__, 'platform': sys.platform}
    EVIDENCE['status'] = 'all requested checks passed' if graph else 'development checks passed; graph omitted'
    if output:
        Path(output).write_text(json.dumps(EVIDENCE, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(METRICS), sort_keys=True), flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--worker':
        worker_main(int(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4]))
    else:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--output')
        parser.add_argument('--skip-graph', action='store_true', help='development only')
        args = parser.parse_args()
        run(args.output, not args.skip_graph)
===== END FILE: docs/research/kernel-0/kernel0_realization_check.py =====
