---
title: Efficiency Architecture Investigation Record
program: EDASES
layer: Architecture
document_type: Design and Reasoning Record
status: Experimental
authority: Derived
canonical_repository: edases
crosslink_issue: 572
baseline_commit: 8d158e3e82d5811e420c80cc6c9664d3ae4a6088
depends_on:
  - EDASES Work Unit Component Design
  - EDASES Execution Engine Roadmap
  - Phase I Processorless Core Falsification
consumed_by:
  - EDASES Efficiency Architecture
  - Efficiency Architecture Discriminating Experiments
related_documents:
  - Efficiency Architecture Evidence Ledger
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Efficiency Architecture investigation record

## Basis and independence

This is an architecture research pass, not methodology, a core amendment, or an implementation plan. Its exact repository basis is Stage-1 commit `8d158e3e82d5811e420c80cc6c9664d3ae4a6088`. The initial Efficiency Architecture is blob `349eee3b51171a9365201eff5d2bd10d8cbfa719`. The research branch starts at that commit; the original document body will remain available in full as historical reasoning when the new synthesis is introduced.

The separate reconciliation `ad24f856a` and its independent review are excluded as settled evidence. Neither its diff nor its conclusions were consulted. Repository tracking state is administrative provenance, not research evidence. This investigation is independent analysis by this session; it is not a claim of independent adversarial verification or a multi-agent consensus.

| Frozen input | Git blob |
| --- | --- |
| `docs/architecture/EDASES-Efficiency-Architecture.md` | `349eee3b51171a9365201eff5d2bd10d8cbfa719` |
| `docs/architecture/EDASES Work Unit Component Design.md` | `22c98dbabdaed7f41d656209a6ce96269dde8390` |
| `docs/architecture/EDASES-Execution-Engine-Roadmap.md` | `a82d8a3fc54fd075fd6a20cf9e64ce560313f87c` |
| `docs/architecture/core-substrate/Phase-I-Processorless-Falsification.md` | `33ff65100cbb10c107337e0f325d1db023e8ffe1` |
| `docs/standards/Documentation Standard.md` | `15c47446695686b19d5e4e67325dd45e0592aa7f` |
| `docs/standards/Concept - Levels of Abstraction.md` | `88c23fe6b43b8249f0b66282b3a8bbfd989016a9` |
| `AGENTS.md` | `4e284d23966bdcb16e6394b715665dc3d4cecff1` |
| `ORIENTATION.md` | `9423fa71597f5a525bfd29378978b6daacbcfc22` |

## Initial observations and discriminating questions

1. The baseline already conditions elimination of derived state on retained inputs, interpretation, observations and deadlines. The research must test those conditions rather than attack an unconditional recomputation claim the baseline does not make.
2. Work Unit A–L distinguishes containment lifetime from execution. A sealed Work Unit can still compute internally under surviving grants. Therefore sealed, dormant, and cheap cannot be treated as synonyms.
3. Phase-I falsification P1 requires trusted guard evaluation or sound verification. Processorless does not mean computation-free or universally untrusted derivation.
4. Phase-I P3/P4 already expose incomplete negative domains and validation/commit races. A cache hit or input hash cannot settle either by itself.
5. Phase-I P6/P8/P9 preserves observations, historical choices and accepted outputs. Derived origin does not imply disposable lifetime.
6. Phase-I P11 names a real reopening condition: a required timing bound plus a defensible recomputation lower bound. A slow benchmark alone cannot establish a new core component.

**WHY:** these distinctions prevent false challenges and prevent efficiency from rewriting the frozen contract. **WHAT:** the frozen documents and sections above. **HOW CERTAIN:** evidence-based textual interpretation. **WHAT-NOT-TESTED:** implementation conformance, acceptance of the frozen core, the separate reconciliation, or any workload performance.

The next analysis asks whether applicability cost dominates reuse; which observations permit lossy reduction; whether maintenance and recovery erase fast-path gains; and which coordination costs can be eliminated without changing required outcomes. Counterexamples and economic models will precede recommendations to build mechanisms.

## 1. Result and epistemic boundary

The baseline survives as a direction toward a small substrate, but not as a single preference ordering of mechanisms. Its sharper replacement is **contract-constrained elimination of total work**: remove a computation, retained representation or coordination step only after naming the observations it must preserve; then compare complete lifecycle costs against the simplest admissible alternative.

Three independent axes replace the misleading derived/persistent dichotomy:

- **Information role:** authoritative fact, accepted historical content, current observation, reproducible derivation, or candidate judgment.
- **Retention:** ephemeral, cached, durably materialized, or retained because an accepted contract requires the information.
- **Trust:** untrusted proposal, checked result, scoped attestation, or trusted computation. “Derived” determines none of the other axes by itself.

This is a synthesis, not a new Kernel ontology. A derived output accepted for future reading becomes required information without making its producer a persistent primitive. A durably stored candidate remains a candidate. A disposable calculator can nevertheless be trusted if its unchecked output governs an effect.

The source ledger [E01–E21](Efficiency-Evidence.md) supplies established correspondences. Findings F01–F10 below are this investigation's deductions, with explicit counterexamples and transfer limits. “Proven” is reserved for narrow mathematical implications with stated premises; no EDASES realization is proven here.

## 2. What does “smallest trustworthy substrate” minimize?

### F01 — Minimize required distinctions before optimizing their representation

Let a consumer contract K specify required observations O, permitted effects, accepted failure histories, quality obligations and any required timing bounds. Two histories may be collapsed into one retained representation only if no required future continuation can distinguish them through O. Write `h1 ~K h2` for that equivalence; this is a **reasoning criterion**, not an algorithm for constructing a minimal state machine.

If two histories map to the same retained summary but require different answers to a future permitted query, no deterministic reconstruction from that summary alone can answer both correctly. The [context collision](models/countermodels.json) exhibits this with identical retained decisions but different discarded constraints. Additional retained evidence can restore the distinction; a cleverer summarizer cannot recover an absent bit.

Consequences:

1. A minimal authoritative cut need not be a full event log. Conversely, a current snapshot is insufficient when audit, historical choices or external observations must remain distinguishable.
2. “Reconstructible” requires **available** inputs, interpretation and necessary observations throughout the promised retention period. A hash of deleted bytes or the name of an unavailable interpreter is not reconstruction material.
3. There is no contract-independent smallest substrate. Adding “explain the decision as it was made” changes the retained distinctions even if present permissions are unchanged.
4. Small byte count and small trusted base are different objectives. A tiny proof plus a huge verifier may reduce storage while increasing assurance work. Indexes may increase bytes while reducing the amount of trusted execution needed at use time.

**WHY:** information erased from all surviving representations cannot distinguish future cases. **WHAT:** frozen Phase-I P6/P8/P9, the finite collision, and the conditional observation argument. **HOW CERTAIN:** proven conditional impossibility for collapsed distinguishable inputs; evidence-based architecture interpretation. **WHAT-NOT-TESTED:** a complete EDASES observation contract, minimal-state construction, or the pending core reconciliation. **Decision:** keep retention and compaction conditional on named consumers; do not mandate event sourcing or snapshots here.

### F02 — Removal, corruption and overload are different ablations

Deleting a cache can lead to correct recomputation. Leaving a corrupt cache in place can supply the wrong answer under a correct input key. In the finite example `f(3)=6`, a matching key accompanies cached `7`; removal succeeds while unchecked reuse fails. Therefore **removability is evidence of optional persistence, not evidence of safe consumption or absence from the trusted base**.

A useful decomposition is:

`candidate production → result checking → applicability binding → authorized consumption`

Correct bytes, right problem, current relevant dependencies and permission to consume are distinct. A signature authenticates an assertion's source; it does not establish its truth. A content digest checks byte identity; it does not show that the bytes compute f. [Proof-carrying code](Efficiency-Evidence.md) (E18) is a correspondence for moving work to an untrusted producer while retaining a scoped verifier, not a universal cheap proof mechanism.

At least four ablations are necessary: remove acceleration; inject incorrect/stale data; lose it during recovery; exhaust its budget or connectivity. A fallback that retains safety by refusing all work fails any required successful-continuation contract. A correct fallback that exceeds a mandatory deadline may also fail. No accepted new deadline is supplied by this pass.

**WHY:** normal operation, failure and absence expose different paths. **WHAT:** finite corruption example; frozen P1/P2/P10/P11/P12. **HOW CERTAIN:** evidence-based counterexample to the stronger removal-only test. **WHAT-NOT-TESTED:** a real cache/checker, hostile implementation, deadline conformance. **Decision:** require these ablations as candidate evaluation criteria; do not enlarge the Kernel.

## 3. Total economics and applicability

### F03 — A cache hit is not the economic unit

Compare complete equivalent work over a horizon T. Track a cost vector:

`C = (compute, inference, latency distribution, memory-time, durable-byte-time, network, energy, human attention, engineering/maintenance effort)`

Track trusted-state complexity and assurance obligations separately as structural constraints; a single byte or dollar proxy is insufficient. Hard correctness constraints are not weighted against savings. Latency quantiles are not additive; repeated averages conceal queueing and correlated failures. Record them from workload traces rather than summing per-operation percentiles.

For one **chosen additive cost dimension**, let:

- N be requests; H be hits that are actually applicable and accepted; R be direct recomputation cost;
- L and V be average lookup and applicability/check cost per request, including misses as appropriate;
- B be extra materialization/index setup, excluding f executions already counted as misses; U and m be updates and average maintenance per update;
- S(T) be retained storage/resource cost; F and r be failures and average repair/recovery cost;
- O be extra observation, coordination, engineering and review cost charged to this mechanism in the horizon.

Common authoritative retention and admission costs cancel only when identical in both arms. R includes the direct path's necessary production/checking cost; L/V and lifecycle terms represent additional reuse-path costs. If persistence pins otherwise disposable inputs or changes admission/observation work, those differences must be added.

Use the deliberately simple homogeneous comparator:

`C_recompute = N R`

`C_reuse = N(L + V) + (N - H)R + B + U m + S(T) + F r + O`

Reuse wins only if:

`H R > N(L + V) + B + U m + S(T) + F r + O`.

With `h = H/N` and fixed other terms, amortization requires `hR > L+V`; otherwise growing N alone never repays setup. This model omits heterogeneous costs and shared dependencies; those require summing request-level values, and counting shared work once. If a failed validation costs more than a successful one, use the appropriate separate counts rather than hiding it in a hit average.

The finite examples use N=100, H=80, R=10, L=1 and lifecycle overhead 70. V=2 yields 570 versus direct 1000; V=9 yields 1270. These are invented units demonstrating a sign reversal, not a cache forecast. A fast-path benchmark would miss it.

A candidate with fewer direct calls but more retrieval, validation, repair and human review has not established savings. Conversely, expensive one-time verification can amortize over many authorized reuses if its applicability remains cheap and sound. Tail latency can justify an otherwise more expensive materialization, but the trade must be explicit.

**WHY:** avoided computation is only one term. **WHAT:** algebra and finite cost evaluation, supported by build/materialization correspondences E01/E04/E07. **HOW CERTAIN:** proven algebra under the homogeneous model; economics in EDASES remains a guess until measured. **WHAT-NOT-TESTED:** workload rates, amortization horizon, real dependency cost, correlated failures, maintenance hours. **Decision:** measure avoided cost net of validation and lifecycle cost; raw hit rate is secondary.

### F04 — Applicability has multiple dimensions and an unavoidable completeness problem

A reuse claim should identify, as relevant to its consumer:

| Dimension | What must be established | Failure if omitted |
| --- | --- | --- |
| Claim and interpretation | Exact result meaning, algorithm/tool/policy version and scope | Same bytes answer a different question |
| Positive inputs | Values or identities actually used, with a coherent observation boundary | Undeclared environment or concurrent mutation changes f |
| Negative/aggregate domain | Which complete set was quantified over, and its revision/completeness evidence | A new child, file, rule or dependency is missed |
| Production | Computation trusted or result soundly checked; nondeterministic outputs labeled as observations/judgments | Authentic wrong result is reused |
| Currency | Relevant inputs still meet the consumer's required freshness relation | Result was true but is no longer applicable |
| Authorized consumption | Current permission to access/use/act on the result in this scope | Reuse crosses a revoked or forbidden boundary |
| Retention and availability | Inputs, interpreter, witnesses or accepted result survive promised failure/retention interval | Digest survives but the answer cannot be recovered |

This table is an investigation checklist, **not a proposed universal envelope schema**. Many cheap local pure computations need only a small subset. Requiring a full generic provenance graph for every integer addition would defeat the objective.

A complete coarse snapshot identity can simplify applicability but invalidate on irrelevant changes. Precise dependencies can avoid those misses while costing more to discover, retain and validate. Dynamic dependencies require tracking the branch/control inputs that chose the dependency set; a previous run's reads alone are insufficient if their selection conditions changed. Environment hermeticity narrows the domain but has setup, storage and review cost (E06/E07).

Negative claims are particularly expensive: “no child exists” quantifies over the authoritative domain, not the list returned by an untrusted index. The finite phantom example keeps all included record tokens unchanged while inserting a child. A scoped domain revision, complete scan, or specifically sound absence witness can address this **if bound to the consumption point**. A timestamp, TTL or signed list does not by itself solve completeness or the validation/commit race. This repeats frozen P3/P4 without settling their unresolved realization.

Even a valid result can become stale between lookup and effect. This pass assumes the governing core supplies the selected admission/currentness contract; it does not specify a new atomicity or authority service. Immutable result reuse and current action authorization must remain separable.

**WHY:** sameness of observed inputs is weaker than completeness, and truth at production is weaker than applicability at use. **WHAT:** E01/E06/E07/E09, frozen P2–P5/P7/P15, finite phantom. **HOW CERTAIN:** evidence-based; phantom counterexample proven in its finite domain. **WHAT-NOT-TESTED:** applicability costs or a concrete complete-domain realization. **Decision:** first compare coarse snapshot reuse with direct recomputation; earn finer dependency tracking through measurements.

## 4. Mechanisms currently conflated

### F05 — Incremental, lazy, memoized and materialized are independent choices

- **Memoization** reuses a result for a matching applicable input identity.
- **Incremental computation** transforms a previous result/trace using change information.
- **Demand evaluation** determines whether an output is needed now.
- **Materialization** chooses what representation to retain, where, and for how long.
- **Early cutoff** stops propagation when the relevant output is unchanged.
- **Scheduling** chooses when and where admitted work runs.

A materialized answer may be rebuilt from scratch; a memo table may be ephemeral; a lazy computation may never cache; incremental state may be reconstructed after failure. These choices should not arrive as one prospective Processor package. Build systems separate rebuilding from scheduling (E01), Adapton separates dirtying from demand repair (E02), and differential dataflow treats iterative change under explicit operators and retained traces (E03).

**Constructed burst:** 100 updates arrive before one final read. If only the final value matters, eager R=10 recomputations cost 1000; marking at 0.1 each, one repair and one check cost 21. If every intermediate observation is required, this coalescing is invalid. The semantic query, not the word “event”, determines whether work can disappear.

For incremental work, compare `trace construction + dependency tracking + delta propagation + output comparison + retained state + recovery` with full recomputation. A one-edge graph change can affect all reachable nodes; one input deletion can retract a widely shared result. High fan-out, control-flow churn and poor change locality defeat the “small input change = small repair” heuristic. Fine granularity increases metadata and scheduling traffic. A coarse dirty bit with a full rebuild can beat an elaborate graph.

Early cutoff also depends on the consumer: equal displayed text does not establish equal provenance or current authority. Stop propagation only when the outputs relevant to that consumer are equivalent; preserve changed evidence if its observation is required.

**WHY:** each choice eliminates a different kind of work and introduces a different maintenance burden. **WHAT:** E01–E05 and burst arithmetic. **HOW CERTAIN:** evidence-based mechanism distinction; numeric saving proven only in the toy workload. **WHAT-NOT-TESTED:** an EDASES incremental operator set, graph traces or interaction deadlines. **Decision:** favor a sequence of small comparisons—direct query, coarse memoization, dirty-on-change/rebuild-on-demand, then selected incremental operators—rather than a generalized engine.

### Negative computation is a family, not a boolean cache

| Negative result | Valid reuse condition | Competing simpler mechanism / falsifier |
| --- | --- | --- |
| Exact absence in a finite domain | Domain completeness, query/policy identity and current binding | Rescan. Insert a previously absent object without changing existing records. |
| Proven contradiction under assumptions A | Checkable proof/witness and matching logic/background; future constraints imply the relevant assumptions | Rerun bounded solver. Relax an assumption and test whether the negative is wrongly retained. |
| “This search found no solution” | Algorithm, budget and explored scope are part of the claim; it is not impossibility | Retain a scoped search trace or retry. A wider/different search finding a solution is compatible. |
| Tool/service failure | Specific failure class and recovery conditions | Bounded backoff. Recovery before expiry reveals availability cost; no result becomes evidence of nonexistence. |
| Rejected approach or semantic dead end | Reasons, context, goals and what changed are retained; advisory unless revalidated | Short decision record and retrieval. Change a decisive constraint and challenge the rejection. |

RFC 2308's distinct absence and failure cases (E09) illustrate scope, not a TTL-based truth proof. Formal incremental solving (E21) is a closer correspondence for reusable contradictions. In ordinary propositional logic, if conjunction F is UNSAT, adding conjuncts preserves UNSAT, but removing one may not. The finite enumeration demonstrates both directions. A semantic engineering dead end has no such monotonicity automatically.

## 5. Demand, observation and dormant-state economics

### F06 — Cheap dormancy means no unnecessary per-object activity, not zero cost

The target should be an overhead model such as:

`cost(T) = authoritative/accepted retention(N,T) + active work(A,T) + required observation(Q,T) + shared maintenance(T) + recovery bursts`.

N durable identities need representation; contents, indexes, backups, scrubbing, migration and audit may scale with retained volume. Eliminating a resident process per Work Unit cannot eliminate that lower bound. Nor does sealing establish dormancy: the frozen Work Unit explicitly permits surviving internal computation.

Measure marginal cost with A fixed while N increases. A million dormant objects whose timers, leases, heartbeats or materialized graphs wake continuously violate the intended economics, even if each worker is “serverless”. Shared services can amortize activity but still have a fixed floor and common failure/restart costs. A small warm pool or predictive prefetch may improve latency economically; literal zero idle resources is too strong.

Events and demand are complements, not replacements for each other. Event delivery can mark relevant state dirty; the next reader can compute. Other consumers require each event itself, so coalescing would erase evidence. Missing-event detection needs a declared source contract, gap handling and reconciliation. Kubernetes' versioned list/watch and expired-history recovery (E12) are a concrete analogy. A generic “event bus” provides none of those guarantees merely by existing.

For a horizon T, compare roughly `poll count × query cost` against `subscription setup + delivered-event handling + duplicate/gap repair + reconciliation + recovery`. Include fan-out and reconnect storms. High event rates, few consumers, costly subscriptions or a cheap bulk snapshot can make polling/batching cheaper. Low churn with trustworthy resumable notifications can make events better. A short periodic reconciliation may be the cheapest companion to event hints; it is not architectural defeat.

**WHY:** dormant representation, observation obligations and active computation have different scaling terms. **WHAT:** frozen Work Unit C/E/H/L; E02/E12/E13 and cost decomposition. **HOW CERTAIN:** evidence-based; proposed scaling target is unmeasured. **WHAT-NOT-TESTED:** idle slopes, backend storage cost, event completeness, shared-service floor or warm-start benefit. **Decision:** measure slopes and storms, not only average per-Work-Unit runtime.

## 6. Context, specialization and deterministic retrieval

### F07 — Compression preserves a consumer, not arbitrary future meaning

Four operations must be separated: exact byte compression; lossless restructuring/indexing; query-specific evidence selection; and semantic summarization. The first two can preserve data while changing access cost. The latter two discard information from the immediate representation and require task-specific validation and a route back to retained evidence.

A context packet can be a derived view containing selected source fragments, source/version references, unresolved questions and scoped findings. If the source survives and access remains authorized, the packet can be disposable. If a summary becomes the only surviving record of an accepted constraint or observation, retention semantics have changed. F01 applies.

Token reduction alone is a poor success metric. Charge retrieval/index construction, extraction, packet validation, prompt growth after misses, rediscovery, answer correction and human review. Required-evidence omission is distinct from model reasoning failure. A semantic-similarity hit is a candidate for inspection, not identity or applicability evidence. Long-context position sensitivity in E16 motivates an experiment control, not a universal shorter-is-better claim.

Deterministic tool/interface discovery can first use stable identifiers, scoped catalog metadata and on-demand schema retrieval. Compare that with a small complete tool catalog and direct file/text search before building a semantic registry. Narrow discovery can hide the only correct tool; measure recall, wrong-version selections and extra discovery rounds. A cached schema does not grant the corresponding capability. Catalog completeness and current tool permissions remain separate questions.

**WHY:** reducing representation and reducing necessary information are different operations. **WHAT:** F01 collision, E16, frozen accepted-content boundary. **HOW CERTAIN:** evidence-based; arbitrary-query losslessness is conditionally impossible for a colliding summary. **WHAT-NOT-TESTED:** context budgets, retrieval recall, current model performance or acceptable omission rate. **Decision:** begin with task-specific projections retaining source access; defer generalized compression.

### Specialization is not the same as converting judgment into truth

For specified `f(static, dynamic)`, partial evaluation constructs `g(dynamic)` with the same relevant behavior under fixed static inputs (E08). Static dependencies, interpretation and environment must remain bound; changed static inputs require respecialization or fallback.

Turning repeated semantic work into code has at least three forms:

1. **Extract already-deterministic mechanics:** parsing, schema checks, reproducible transforms. Specification and tests can validate the mechanic.
2. **Specialize a specified program:** retain the equivalence obligation and its assumptions.
3. **Induce a rule from prior judgments:** this is policy formation or statistical generalization. Repeated agreement is not semantic equivalence; separate review and scoped empirical evidence are needed.

Compare `construction + review + tests/proof + distribution + version maintenance + fallback` against saved work during the rule's useful lifetime. A frequently changing policy can invalidate a specialized program before it repays its creation. A tiny table or existing tool may dominate a compiler. Cheap deterministic execution of an incorrect learned rule is not progress.

## 7. Placement, sharing, scheduling and optimization overhead

### F08 — Reuse locality and scheduling change the economics together

For the same admissible output, compare local computation with remote access as vectors. A simple latency decomposition is:

`local = local queue + input acquisition + local execution + result check`

`remote reuse = remote queue + round trips + request/result bytes ÷ effective bandwidth + lookup + applicability/check + fallback on failure`.

Do not sum monetary and latency terms or assume warm availability. Remote execution can have faster compute yet slower end-to-end completion. A local index can save network while duplicating storage and updates. Co-locating computation with retained inputs can dominate both moving a large context and sharing a tiny result. RDD locality and lineage (E11) supply a useful restricted-computation analogy.

Cross-Work-Unit/project reuse requires **two decisions**: computational equivalence and permitted sharing. A pure toolchain output might share a computation identity while access remains separately checked for each consumer. Conversely, policy, confidential source, trust scope or accepted-judgment provenance may make sharing invalid despite identical text. Cross-project cache membership and metadata can reveal information; account for access control and isolation as real cost. Do not widen a Work Unit boundary merely to improve a hit rate.

A shared computation should be counted once in system cost; allocations to beneficiaries are a separate accounting policy. Adding all recipients' “avoided work” can overstate savings if they would not independently have performed it. Removing a shared cache may change scheduling and demand itself. Use paired workload replays and report interactions.

**Graphs must be typed by purpose.** Containment edges constrain authority; dependency edges describe inputs; work edges may describe organization or precedence; communication edges say who can exchange information; resource conflicts may be absent from all four. Neither the containment tree nor a visual issue graph is automatically an executable DAG. Two nodes with no displayed dependency may still contend for a shared effect or require independent reasoning before synthesis.

For a fixed admitted acyclic task graph with total work W, unlimited-resource critical path L, and capacity P measured in compatible work units per time, completion time is at least `max(W/P, L)`. Parallelism cannot reduce either bound. Scheduling, communication and integration add cost. Cyclic semantic refinement requires a stopping rule, not simply a topological sort. E01's scheduler/rebuilder split and E03's explicit iteration model warn against calling every graph a workflow.

Batching amortizes setup and network but adds waiting. Fine tasks improve cancellation/interactivity but add overhead. Speculation can reduce expected tail latency while increasing total work. E13 shows the correspondence for hedging; it does not justify duplicating effectful tasks. Cancellation must actually release resources, and cancellation of a request is not proof that an external effect was cancelled. Backpressure and admission limits can be a smaller intervention than an intelligent scheduler. Any promised fairness or deadline is a contract to validate separately.

**WHY:** data movement, contention and dependency semantics can dominate computation. **WHAT:** E01/E03/E11/E13, the elementary work/path bound and frozen boundary rules. **HOW CERTAIN:** evidence-based; bound proven under stated assumptions. **WHAT-NOT-TESTED:** scheduling traces, remote failure rates, sharing-policy costs, graph completeness or contention. **Decision:** compare local direct execution and bounded concurrency before remote shared services or topology-driven scheduling.

### F09 — Approximation needs an error model; cheap-first needs an economic model

Separate at least three families:

1. **Sound conservative abstraction:** prove a selected property for an overapproximation, or fall back when inconclusive (E17). False alarms can cost progress; a universal-refusal analysis is safe but may violate required successful behavior.
2. **Statistical approximation:** sampling, probabilistic classification or estimated simulation with an explicit error distribution/bound and tested applicability. A simulator's numerical bound says nothing about omitted environment behavior unless that is also justified.
3. **Heuristic prioritization:** order inspection or propose actions without asserting exact truth. Even this can violate liveness if it permanently excludes necessary work.

Thus “behind the exact guard” is insufficient if the optimizer controls which candidates ever reach the guard. A search prefilter with false negatives can suppress the only successful path while every executed effect remains safe. Measure successful continuation and coverage, not just absence of unsafe acceptance.

For a cheap-first cascade, a simple per-request cost is:

`C_cascade = C_cheap + C_check + p_escalate C_expensive + C_repair + C_calibration_amortized`.

Compare it with direct expensive execution plus the corresponding quality checks. With cheap=1, check=1, expensive=10, escalation=0.2, the toy cost is 4; escalation=0.9 costs 11 versus direct 10, before calibration and repair. Escalation also adds serial latency. Confidence alone cannot establish low error: report coverage, error on accepted cases, misses, calibration, distribution shift and how abstention is resolved. E14 supplies the risk/coverage distinction and E15 the measured-cascade correspondence; neither validates the toy policy.

A cheap classifier is warranted only when a measured task distribution, acceptable loss and meaningful fallback are available. Cheap models can be good endpoints on some cases rather than mere precursors; an expensive model is not an oracle. Evaluation must avoid training/test leakage, representation omissions and using the producing model's preference as ground truth. Retain uncertainty when independent reference answers are unavailable.

**WHY:** error location and conditional escalation determine both quality and cost. **WHAT:** E14/E15/E17 and finite cascade arithmetic. **HOW CERTAIN:** evidence-based distinction; EDASES routing gain remains a guess. **WHAT-NOT-TESTED:** any model calls, error calibration, simulation validity, fallback correctness or acceptable policy loss. **Decision:** defer general routing until narrow cases and evaluation criteria exist; no provider/model selected by this research.

### F10 — Optimization has a budget, a lifetime and a disposal obligation

An optimizer consumes observation, search, review and execution resources. Deciding whether to reuse can cost more than computing. Searching indefinitely for a better schedule can miss the execution deadline. Repeatedly reconstructing a dependency graph to prove a tiny answer current is a negative optimization.

The metareasoning connection (E20) is to choose additional computation when its expected improvement to the decision exceeds its total cost, under allowed risk. That expectation is itself uncertain and costly to estimate. The practical first candidate is a fixed measurement/planning budget with a direct fallback, not a recursive “optimal optimizer”. Cheap discriminating tests have high value because they can end a branch before machinery is built.

Materialization under unknown reuse resembles online rent/buy (E19). If setup B=12 and net saving per future use s=3, more than four **future applicable uses** repay setup in a no-churn model. Four past uses do not imply four future ones. Changes, eviction, failure and maintenance reset or erode the benefit. Hysteresis and minimum evidence horizons may prevent oscillating between build/delete/rebuild, but their own tuning cost must be charged. E04's adaptation and E05's hostile access pattern establish why “self-tuning” is not inherently economical.

**Retention is a missing efficiency mechanism family.** Every retained dependency, certificate, source version, context fragment and cached answer needs an owner/scope, retention reason, expiry/eviction condition, reconstruction route if promised, and disposition compatible with the Work Unit boundary. Merely deleting an index may retain its backing blobs forever. Conversely, deleting all sources while promising later derivation is invalid. Garbage collection, provenance closure, version migration and orphan detection can dominate quiet systems.

This does not require a new central retention service. A bounded local cache with eviction and retained-source assumptions is the first comparator. Cross-project deduplication, reference ownership and authorized disposition are more complex candidates. Derived origin does not give permission to delete accepted evidence. State-size reduction must be measured after the transitive dependencies it pins are counted.

**Recovery amplification is another missing family.** Optional caches can all fail together. One slow-path recomputation may be affordable; thousands after a restart may overload the same store and cause retries, duplicate work and yet more load. Durable materialization, request coalescing, throttled rebuild, locality and selective warming compete with rebuilding everything. Coalescing must not cross authority scopes or merge independent required judgments.

The toy cold-recovery workload assumes 100 disjoint mandatory jobs with no shared computation, an assumed work floor of 10 each and capacity 8; it requires at least 125 time units, exceeding an invented deadline of 50. This is a conditional boundary example, **not** an accepted EDASES deadline or a demonstrated algorithmic lower bound. Under a genuine mandatory bound it would open B03 below; otherwise it is an operational trade. A retained value, resource reservation or narrower requirement might suffice; a persistent Processor does not follow.

Finally, telemetry is itself retained derived state. Count collection, indexing, transmission and interpretation. Bounded counters and sampled traces may answer economic questions; sampling can miss rare failures and tails. Measurements used for billing or enforceable quotas are no longer merely disposable economic dashboards if their loss changes a required guarantee.

**WHY:** costs recur across construction, adaptation, failure and retirement, not just reads. **WHAT:** E04/E05/E11/E19/E20, cold-recovery arithmetic and frozen retention rules. **HOW CERTAIN:** evidence-based architectural deduction; usefulness of individual controls is unmeasured. **WHAT-NOT-TESTED:** outage storms, retention closure size, garbage collection, policy adaptation stability, telemetry bias or real maintenance effort. **Decision:** require lifecycle and recovery accounting before enlarging the optimization portfolio.

## 8. Candidate mechanism portfolio

These cards are **selection records**, not a build list. Each names avoided work; added state and costs; applicability evidence; the workload that may pay; a simpler competitor; incremental introduction; disposability; and a falsifier. F03 determines whether maintaining the stated evidence is cheaper than the avoided work. For all cards, economic claims are guesses until their corresponding experiment passes; the mechanism distinctions are evidence-based. No card authorizes changing a required guarantee.

| ID / avoided work | State, applicability and disposal | Economic condition, simpler competitor and incremental admission | Falsifier / experiment |
| --- | --- | --- | --- |
| M01 Snapshot-scoped memoization: repeated deterministic calls | Input/interpretation identity, checked output, scoped access; storage and lookup/validation. Disposable only while required inputs remain available. | Stable repeated requests with costly f and cheap complete identity. Start with one pure operation; compare direct calls. Introduce persistence only after ephemeral reuse wins. | Net saving ≤0 including failed validations, or wrong hit after environment/policy mutation. X02. |
| M02 Dirty-on-change, rebuild-on-demand: unused intermediate versions | Dirty markers, dependency scope, demand set and rebuild route. Lost markers must cause conservative reconstruction, not false clean state. | Bursty updates, sparse reads, no obligation to observe intermediates. Start with a coarse scope token and full rebuild. Compare eager updates and direct reads. | Needed intermediate evidence lost, interaction deadline missed, or tracking exceeds avoided repairs. X03. |
| M03 Selected delta maintenance and early cutoff: repeated full derivation | Traces/indexes, operator semantics, change completeness, equality appropriate to consumer, retractions and recovery. Usually disposable from retained base. | Large repeated query with local change and stable operators. Add one operator after M02 loses; compare dirty/full rebuild. | High-fan-out change or control churn makes whole-horizon cost worse; deletion/provenance change missed. X03. |
| M04 Durable materialization/checkpoints: repeated restart reconstruction or long lineage | Versioned result, provenance, retained-source or accepted-output contract, integrity and migration. Persistence alone adds no authority. Required accepted output is not disposable. | Measured reconstruction dominates storage/checkpoint/recovery cost or a reviewed deadline requires investigation. Start with one expensive stable view; compare ephemeral cache and capacity-limited rebuild. | Rare reuse, frequent churn or restore/currentness cost erase gain; removal loses a required fact. X04/B03/B04. |
| M05 Scoped negative reuse: rediscovering absence, contradictions or failures | Domain/reason/assumption/budget identity; invalidation and review. Preserve accepted decisions separately from advisory cache. | Repeated expensive failures with stable causes. Start with one exact negative type; compare rescan or bounded retry. | New object, relaxed constraint or service recovery wrongly suppressed; unknown becomes impossible. X02/X06. |
| M06 Mechanics extraction/specialization: repeated semantic/tool-composition steps | Specified transformation, static inputs, generated code, validation/review, version maintenance and fallback. Optional until its output becomes a required artifact. | Stable specified subproblem and enough future reuse. Start with a script/table or existing tool before compiler generation. | Change invalidates rule before break-even; learned rule lacks specification; construction exceeds avoided effort. X07. |
| M07 Task-specific context and lazy tool discovery: repeated reading, oversized packets/catalogs | Source references, query/schema identity, catalog access, index/summary construction and omission checking. Disposable if sources and needed accepted facts survive. | Repeated narrow consumer questions. Start with direct search plus exact source fragments; compare full relevant context and small complete catalog. | Required evidence/tool omitted, extra retrieval/repair outweighs token reduction, old permissions reused. X05. |
| M08 Event hints plus demand/reconciliation: idle polls | Subscription/filter/cursor state, delivery scope, snapshot consistency and gap recovery; connection/fan-out cost. Rebuildable only if current state suffices, otherwise required events must be retained. | Sparse relevant changes and reliable cheap change source. Start with one source; compare periodic bulk queries at matched observation quality. | Expired history, storms or hidden gaps cause missed obligations or greater total cost. X08/B04. |
| M09 Local/remote and cross-scope reuse: duplicate computation/data movement | Computation identity plus per-consumer access, placement, transport, tenant isolation and retention ownership. Shared storage is not shared authority. | High authorized reuse with transfer/check cost below saved execution. Start same Work Unit, then same authorized scope; compare local recompute. | Transfer dominates, unauthorized membership leaks, policy churn destroys hits, shared outage dominates. X09. |
| M10 Conservative filters/statistical routing/simulation: costly exact work on easy cases | Explicit property/error contract, calibration/reference labels, coverage, abstention and fallback; drift review. Model artifacts disposable only if fallback meets required behavior. | Defined case distribution, acceptable uncertainty, net cost gain at acceptable coverage. Start in shadow evaluation; compare direct tool/model/analysis. | Missed required path, shift harms accepted risk, cascade cost exceeds direct. X10/B06. |
| M11 Bounded scheduling, batching and speculation: waiting, duplicate setup, idle capacity | Demand/precedence/resource facts, queue/cancellation state, integration cost and policy. Readiness graphs are advisory to actual authorization. | Demonstrated contention or tail problem. Start bounded FIFO/concurrency, then one measured policy; compare direct serial/parallel baselines. | Wrong edge interpretation, starvation, harmful duplicates, cancellation waste or planner cost exceed benefit. X09/X11. |
| M12 Retention/eviction and reclamation: unused bytes, indexes and pinned ancestry | Ownership, retention reason, dependency closure, disposition and reconstruction evidence; cleanup/review cost. Cannot dispose accepted content by relabeling it cache. | Material unused retention over realistic horizon. Start size/age-bounded derived cache; compare no persistent cache/manual scoped cleanup. | Recoverability or audit lost; transitive storage remains; cleanup costs exceed reclaimed resource. X04/B04. |
| M13 Bounded measurement and accounting: optimization of the wrong bottleneck | Counters/sample traces, attribution and shared-cost policy, schema/retention; observer overhead. Economic telemetry normally disposable, enforcement evidence may not be. | A concrete decision can change with the measurement. Start minimal counters and paired replay; compare coarse totals. | Observer changes workload materially, tails missed, double counting, or no decision changes. X01/B05. |
| M14 Budgeted optimization/adaptation: repeated planning and poor prospective investment | Decision-cost estimates, short histories, thresholds and rollback/fallback; tuning and evaluation effort. Derived hints can be reset. | Repeated material choices under reasonably stable workloads. Begin with fixed budgets and measured break-even, not a universal optimizer. | Oscillation, stale workload estimates or optimizer cost exceed savings. X12. |

## 9. Hypotheses after attack

| Starting hypothesis | Disposition | Stronger, narrower interpretation |
| --- | --- | --- |
| Dormant logical state should be cheap | Retain, qualify | No unnecessary resident activity; retained identities, contents and lifecycle maintenance still have cost. Sealed is not dormant. F06. |
| Active resources follow active work | Retain as scaling target | Account for observation, warm capacity, shared maintenance and recovery bursts separately. Prediction can legitimately spend before demand. F06/F10. |
| Derived views normally reconstructible | Retain conditionally | Consumer-relative retention and available sources/interpretation required; accepted historical outputs can become required content. F01/F07. |
| Recompute competes with persistence | Strengthen | Compare entire workload horizon, applicability, correlated failures and retirement; neither has universal priority after measurements. F03/F10. |
| Events/demand beat polling/residency | Split | Demand controls need, events indicate change, polling can reconcile; compare matched observation contracts. F05/F06. |
| Reuse deterministic results when cheap | Retain, strengthen | Determinism, checked production, complete applicability and authorized consumption are separate. F02/F04. |
| Compile repeated semantic work | Split | Mechanics extraction and specified specialization differ from learning/approving a semantic rule. F07. |
| Optimization removable without correctness change | Retain, strengthen | Test missing, wrong, stale and overloaded behavior, with successful continuation. Removal alone does not show untrusted operation. F02. |
| Rich UX need not inflate authority | Retain conditionally | Display projections are derived; user edits/acceptances and uniquely captured observations need durable authoritative/accepted representation. F01. |
| Persistent Processor not required by correctness | Survives this pass within frozen scope | No new witness meets the existing falsification burden. This is not proof for arbitrary future contracts or acceptance of unresolved core semantics. B01–B06. |

Rejected stronger hypotheses: zero-cost dormant population; a hit proves useful reuse; a removable cache is necessarily untrusted; any summary is a sufficient future context; small changes always make incremental work cheap; a graph determines lawful scheduling; cheap-first always saves; deterministic execution makes an induced policy correct; and event-driven means reconciliation-free. Rejections apply to these stronger readings, not retrospectively to qualifications already present in the frozen baseline.

## 10. Architectural decision points: stop these branches here

| ID | Smallest case / missing requirement | Implication and stopping boundary |
| --- | --- | --- |
| B01 Currentness at use | A correct permission/readiness result is computed; the relevant grant or evidence is withdrawn before use. Or the entire source/epoch rolls back. | Economic reuse is conditional on the selected core currentness/admission contract. Same-domain caches supply no missing information. This pass neither endorses the pending reconciliation nor defines a new service. Continue pure immutable-result experiments; stop cached-authority design. |
| B02 Unknown external effect | A sink performs an effect, the reply is lost, and a replacement wants to reuse “not completed” or retry. | This is outcome information/attachment-contract uncertainty, not an invalidation optimization. Require the governing effect contract; do not design exactly-once delivery or infer completion from a cache. |
| B03 Required cold deadline | Required answers have a defensible total work floor exceeding available capacity × mandatory recovery interval. | Durable values or another guarantee/resource choice may become necessary. The toy arithmetic is conditional and the frozen contract supplies no such bound. Obtain the actual requirement and lower-bound evidence; stop before choosing a Processor or replacement core. |
| B04 Irreplaceable history / disposition | Delete source/history then promise reconstruction of a distinguishable accepted observation; or remove a “derived” UI that was the sole record of a user acceptance. | Retention role must be corrected. Acknowledging accepted content does not prove a separate lifecycle primitive necessary. Unspecified audit scope goes upward for a contract decision; no retrospective deletion policy invented here. |
| B05 Enforced accounting | Disposable telemetry is lost while an exact quota/billing contract depends on its cumulative value. | An economic view has crossed into required evidence. Define the guarantee and authoritative measurement boundary separately. This research does not make all telemetry trusted or required. |
| B06 Required progress under heuristics | Approximate routing/pruning permanently hides the only permitted successful path while the exact guard never makes a mistake. | Safety alone is inadequate if progress/coverage is promised. Require a fallback/fairness contract and check it; do not claim an advisory heuristic is correctness-neutral merely because it cannot authorize effects. |

No row establishes that a new Kernel primitive or persistent Processor is needed under the **existing frozen comparator**. Rows identify where a later requirement or unresolved semantics would change the evaluation. Following those branches into a new authority/recovery architecture would exceed this pass.

## 11. Recommended research reduction

The highest-value next question is empirical: **is complete applicability cheap enough on a real repeated operation?** Start with the direct processorless comparator and a small workload/observation inventory (X01), then compare coarse snapshot reuse (X02), burst-aware demand repair (X03), and simultaneous cold reconstruction/retention (X04). These discriminate the largest architectural assumptions without committing to a subsystem.

Task-specific context/tool discovery (X05) is a parallel empirical candidate when a real repeated task with defensible expected evidence exists. Negative reuse, compilation and event handling should follow their demonstrated repeated cost. Learned routing, remote global reuse and general scheduling should wait for workload and contract evidence. Do not buy a universal dependency graph, semantic cache, global catalog, optimizer or telemetry lake prospectively.

Missing concepts worth adding to later roadmap investigations are: **applicability economics; retention and reclamation; correlated reconstruction cost; optimization's own budget; and coverage/progress consequences of advisory heuristics**. These are questions attached to Phases II–VI, not new components or a phase reorder. The [main architecture](../EDASES-Efficiency-Architecture.md) links this reduction; the [experiment protocol](Efficiency-Experiments.md) contains execution-ready comparisons and stop criteria.

**Handoff claim — WHY:** the original hypotheses now have scoped counterexamples, mechanism alternatives, economic conditions and named empirical discriminators. **WHAT:** frozen-input manifest, F01–F10, M01–M14, B01–B06, primary-source ledger and eight executed finite countermodels. **HOW CERTAIN:** evidence-based architecture synthesis; toy implications hold only under explicit premises. **WHAT-NOT-TESTED:** production workload economics, independent adversarial review, implementation refinement, actual model/tool routing, real fault injection, accepted core timing/progress contracts, or the separate authority/recovery reconciliation. This pass recommends research choices and does not promote them to Canonical authority.
