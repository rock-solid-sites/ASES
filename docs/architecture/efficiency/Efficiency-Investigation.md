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
- B be initial materialization/index setup; U and m be updates and average maintenance per update;
- S(T) be retained storage/resource cost; F and r be failures and average repair/recovery cost;
- O be extra observation, coordination, engineering and review cost charged to this mechanism in the horizon.

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
