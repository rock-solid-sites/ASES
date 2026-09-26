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
