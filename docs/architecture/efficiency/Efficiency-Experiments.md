---
title: Efficiency Architecture Discriminating Experiments
program: EDASES
layer: Architecture
document_type: Research Protocol
status: Experimental
authority: Derived
canonical_repository: edases
crosslink_issue: 572
baseline_commit: 8d158e3e82d5811e420c80cc6c9664d3ae4a6088
depends_on:
  - Efficiency Architecture Investigation Record
  - Efficiency Architecture Evidence Ledger
consumed_by:
  - Future Observer research
  - Future Processor research
  - Future Orchestrator research
  - Execution Engine research planning
related_documents:
  - EDASES Efficiency Architecture
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Discriminating experiments

## What ran, and what did not

Eight finite countermodels were executed in this pass using the Python standard library. [Source](models/countermodels.py) and [exact deterministic output](models/countermodels.json) are retained. Run from repository root with `python3 docs/architecture/efficiency/models/countermodels.py`; compare stdout byte-for-byte with the saved JSON. This is an agent reproduction command, not a request for the operator to run it.

| Countermodel | Observed output | What it discriminates / what it cannot establish |
| --- | --- | --- |
| Reuse cost | Direct 1000; reuse 570 with V=2, 1270 with V=9, same 80/100 applicable hits | Validation cost can reverse benefit. Units/rates are invented; no EDASES speedup estimate. |
| Burst repair | Eager 1000; dirty/final-demand 21 | Coalescing can eliminate unused intermediate computation. Invalid if each intermediate output is required. |
| Negative domain | Included tokens unchanged; cached absence true; present absence false | Included-object identity cannot certify domain completeness. Domain epochs are illustrated, not a selected authority protocol. |
| Cache corruption | Matching key, cached 7, required 6; scoped checker rejects; removal recomputes 6 | Removability does not imply safe unchecked use. Does not establish a cheap checker for arbitrary f. |
| Context collision | Same summary, different required future answer | Lossy retention cannot preserve arbitrary future distinctions. Does not quantify real summarization error. |
| Negative proof scope | Base UNSAT, strengthened UNSAT, relaxed SAT over a two-variable universe | Formal negative reuse has assumption directionality. Does not turn failed semantic search into a proof. |
| Cold recovery | Conditional work floor 125, equal-job schedule 130, hypothetical deadline 50 | Correlated reconstruction can fail a timing bound even with available inputs. Disjoint per-job work floors and deadline are assumed, not established core requirements. |
| Cascade cost | Direct 10; cheap/check/escalate 4 at p=0.2, 11 at p=0.9 | Cheap-first is not always cheap. No model quality or calibration measured. |

**WHY:** these are the cheapest tests that can falsify unconditional readings before building a cache, router or scheduler. **WHAT:** deterministic arithmetic, explicit history collisions and finite propositional enumeration. **HOW CERTAIN:** proven implications within the defined toy models; evidence-based interpretation of their architectural relevance. **WHAT-NOT-TESTED:** real workloads, source/epoch trust, actual cache corruption recovery, statistical quality, external effects, production costs, independent review or any full-system implementation.

The following X01–X12 are **proposed**, not completed experiments. They name what must be measured to select designs without rerunning the survey. No numerical acceptance threshold below is asserted as project policy.

## Common comparison contract

Before an empirical run, freeze a small manifest containing:

- Consumer question and required successful outputs/observations, admissible uncertainty, relevant failure profile and mandatory versus preferred deadlines.
- Input corpus and revisions; algorithms/tools/models/policy versions; visible context; scoped permissions. Keep future-outcome information out of the treatment's input.
- Baseline, one changed mechanism, workload generator/replay, cost-accounting horizon and shared-cost attribution rule.
- Predeclared quality criteria, smallest worthwhile improvement, latency/space budgets and stopping rule. Report disagreement or missing requirements rather than picking them implicitly.
- Warmup, cold runs, repetitions/seeds, ordering/randomization, confidence/uncertainty reporting and artifact retention.

Use completed **equivalent useful work** as the denominator. Include failures, retries, misses, rebuild, migration, cancellation, cleanup and human intervention. Compare output/evidence equivalence before comparing cost. Improvements on one cost dimension must not be reported as whole-system savings if another unpriced dimension worsens.

Start with finite fixtures or read-only replay. External effects in experimental arms must be simulated or otherwise independently authorized. Introduce persistence, remote services or models only when the preceding cheap comparison says the question matters. If a required core premise is unresolved, record the corresponding B01–B06 dependency and stop that branch.

## Priority and selection

| Priority | Experiment | Decision unlocked | Prerequisite / earliest roadmap home |
| --- | --- | --- | --- |
| P0 | X01 Workload and observer-cost inventory | Identify repeated cost and a viable comparison contract | Any working minimal comparator; measurement, not a telemetry subsystem |
| P0 | X02 Applicability versus recomputation | Whether reuse pays; coarse versus precise identity | X01; Phase III candidate |
| P0 | X03 Demand/dirty/rebuild versus incrementality | Whether a dependency engine adds value beyond coalescing | X01 and a repeated derived query; Phase III |
| P0 | X04 Cold recovery and retention closure | Whether persistence/reclamation changes total economics | Retention/failure contract; Phases III/VI, B03/B04 if guarantee affected |
| P1 | X05 Evidence/context/tool projection | Whether smaller representations reduce completed-task cost | Narrow tasks with independently checkable evidence requirements; IV/VI |
| P1 | X06 Negative reuse | Which negative result type is safe and profitable | X02 domain/assumption evidence; III/VI |
| P1 | X07 Specialization | Whether stable mechanics repay extraction/compilation | Repeated specified subproblem; III/IV |
| P1 | X08 Observation strategies | Poll, event, demand or hybrid at matched obligations | Source observation contract; II |
| P2 | X09 Locality, sharing and coalescing | Whether avoided work exceeds transport/coordination costs | X02 and explicit authorized sharing scope; V/VI |
| P2 | X10 Approximation and routing | Risk/coverage/cost frontier | Defined ground truth, loss and abstention/fallback; IV |
| P2 | X11 Scheduling/topology | Whether planner sophistication pays | Traces showing contention or critical-path delay; V |
| P2 | X12 Adaptive investment | Whether dynamic optimization beats simple thresholds | Multiple measured candidate costs and workload regimes; VI |

Priorities are recommendations from this pass, not a roadmap resequencing decision. A demonstrable large recurring cost can reorder them. Stop after a simpler comparator wins; completing every row is not a goal.

## X01 — Workload inventory and cost of observing it

**Question:** Where does repeated work actually occur, and can measurement itself remain cheap?

**Cheapest gate:** inspect a small, authorized set of existing task traces or record a short minimal-system run using coarse counters. Classify repeated versus unique operations and missing observation fields. If the data cannot distinguish useful repeated work from retries or unrelated operations, repair that limited measurement before estimating savings.

**Comparators:** instrumentation off; coarse counters; sampled operation traces. Same workload with matched cold/warm state. Count useful completion, direct computation, inference, retrieval, coordination, validation/currentness, reconstruction, retries, and retention. Attribute shared work once; separately report allocation policy. Record measurement CPU/I/O/bytes and human time needed to interpret it.

**Workload families:** many dormant/few active objects; long single tasks; bursty edits with sparse reads; repeated stable queries; high-churn unique tasks; restart after common service loss. Do not assume a production mixture before obtaining it.

**Discriminator:** stable bottleneck ranking across minimally perturbing measurements, with enough information to bound a candidate's savings. Reject richer telemetry if it costs more than the decision it improves, changes workload behavior materially, or does not change a decision. Rare-failure and tail uncertainty must remain visible; absence in a short sample is not proof of absence.

**Exit:** one or two real candidate operations and a frozen comparison manifest, or an evidence-based recommendation to build no optimizer yet. No universal tracing platform required. B05 applies if accounting is also enforcement.

## X02 — Applicability cost, identity granularity and hostile reuse

**Question:** Does establishing a reusable result's applicability cost less than recomputation?

**Cheapest gate:** choose one deterministic, repeated, bounded read-only computation. Enumerate its actual input/interpretation dependencies and result checker. If the set cannot be bounded or the source cannot establish the relevant complete domain, do not construct a general cache; record the gap and compare direct computation.

**Arms:** direct execution; ephemeral cache keyed by a complete coarse snapshot; cache with selected precise dependencies. Durable/shared variants enter only if an ephemeral arm wins. Compare a trusted-computation result with a cheaply checked candidate only where a meaningful checker already exists; input-key matching alone is not the checker.

**Sweep:** repetition, compute cost, change rate, negative versus positive query, dependency cardinality/fan-out, environment/policy changes, failed validations, corruption, eviction and workload shift. Include creation of a previously absent object, changing branch selectors, a result under the right key but wrong bytes, and mutation between checking and consumption in a fixture governed by the selected contract.

**Measure:** true applicable hits, rejected/stale candidates, false acceptance, total L/V/R, tracking/build/storage/recovery cost, break-even horizon and p95/p99 latency where sample size supports them. Avoid speedup claims from supplied hits alone.

**Falsifier:** coarse reuse has no net gain; precise dependency savings fail to pay tracking cost; or any relevant mutation is missed. A wrong authoritative acceptance rejects the mechanism regardless of average savings. If fixing it needs unresolved currentness semantics, stop at B01.

**Exit:** admit one scoped reuse mechanism with measured domain and retained fallback, or retain direct computation. This is the first recommended empirical discriminator.

## X03 — What demand eliminates before a graph is worthwhile

**Cheapest gate:** replay a finite burst of edits and record which output versions consumers actually request. If consumers require every version, the unused-version saving is unavailable; do not infer it from a sparse UI alone.

**Arms:** recompute each requested output; eager full repair on change; dirty/rebuild-on-demand; selected incremental repair; incremental repair plus consumer-valid early cutoff. Preserve one common observation contract and full-recompute oracle on fixtures.

**Sweep:** read/update ratio, long idle periods, hot key skew, graph size and fan-out, control-flow changes, deletes/retractions, equal visible output with changed provenance, and change patterns that touch most descendants. Account for demand-tracking and graph initialization, including outputs later abandoned.

**Discriminator:** break-even surface for total time/space and response latency. If dirty/full rebuild matches or beats incrementality, defer generalized dependency machinery. If exact evidence changes but text does not, an early-cutoff optimization must still preserve the required evidence observation.

**Exit:** one justified operator/granularity or no incremental engine. No inference from one favorable graph family to arbitrary Work Unit topology.

## X04 — Retention closure, correlated cold reconstruction and disposition

**Cheapest gate:** list the actual source/result/witness dependencies of one retained view; walk their retention closure on a fixture. Remove disposable state and reconstruct a useful output. A missing input or interpreter already falsifies the reconstruction premise without a load test.

**Arms:** no retained derivation; bounded ephemeral cache; selected durable materialization; periodic derived checkpoint; coalesced/throttled rebuild. Use the same promised accepted content and same currentness mechanism in every arm.

**Sweep:** retained population with fixed active demand; dependency chain length; restart of one cache versus all caches; repeated failures; unavailable remote source; tool-version retirement; simultaneous demand; cache eviction while sources remain; planned disposal and migration. Distinguish sealing from inactivity. Exercise successful continuation, not just safe refusal.

**Measure:** steady-state idle slope per object and byte, transitive bytes pinned, time to first and all requested outputs, peak recovery CPU/network/memory, duplicate work, queuing, maintenance/cleanup effort and resulting retained volume. Measure the complete failure cycle, not only successful cache restoration.

**Falsifier:** retention savings disappear when pinned sources are counted; reconstruction promise cannot be met; a common outage causes unbounded retry amplification; or a cache becomes the sole required evidence store. For an actual mandatory deadline, obtain a defensible workload/resource lower bound and refer B03. A preference for faster restart alone remains economics.

**Exit:** bounded retention/rebuild policy for that view, or a documented contract decision. Do not build a general garbage collector or recovery service from this experiment alone.

## X05 — Context reconstruction and deterministic tool discovery

**Cheapest gate:** select a few real repeated questions with independently justified answers and necessary evidence. Verify the answer is derivable from each treatment's visible material; classify omissions as representation failures, not model errors. Keep test questions independent of the compressor/retriever and hold out whole task families/repositories where practical.

**Arms:** complete relevant source context; direct deterministic search with exact fragments; structured projection plus source links; semantic summary; small complete tool catalog versus scoped metadata plus on-demand schemas. Do not vary both representation and model in the first comparison. If models are needed later, choose and authorize them under the existing model discipline; this protocol supplies no model selection.

**Controls:** move necessary evidence to beginning/middle/end; add irrelevant material; withdraw/replace a decisive fact; change a tool schema or capability; require recovery after deleting only the derived packet. Include “no available tool solves this” and missing-source cases. Measure additional discovery rounds and failure to find the only appropriate interface.

**Measure:** end-to-end correct completed decisions, evidence recall, unsupported claims, tool-selection correctness, total tokens/retrieval/extraction/validation cost, latency and human correction. Repeated-source reuse should be distinguished from merely reducing a single prompt.

**Falsifier:** cheaper packets lose required distinctions, extra retrieval erases savings, or reuse treats past permission as current. Better scores from leaked answer fields reject the evaluation. Unknown semantic truth remains unscored or explicitly uncertain.

**Exit:** one task-relative projection with measured limits and source fallback, or retain direct retrieval/full relevant context. No universal summary policy.

## X06 — Negative results and dead ends

**Cheapest gate:** label each candidate as exact absence, formal contradiction, bounded search miss, transient failure, or semantic rejection. If a record does not contain enough scope/reason to distinguish these, it cannot safely prune future work.

**Arms:** recompute/retry; exact-input negative cache; reason/assumption-scoped reuse. For semantic dead ends compare a short retrievable decision record with automatic pruning; the latter needs additional justification.

**Mutations:** add an absent object; relax one contradictory premise; increase search budget/change algorithm; recover a service; change user goal or relevant tool; retain the same incidental text. Include stable truly impossible cases so rejecting everything is not rewarded.

**Measure:** avoided work minus revalidation, false suppression, delayed discovery after a decisive change, retention/review cost and successful continuation. Measure the scope check itself: expensive subset/proof matching can exceed retry cost.

**Falsifier:** any unknown promoted to impossibility, or repeated false suppression whose cost dominates savings. **Exit:** one negative type with an applicability contract, or advisory records only. B01/B06 stop authority/progress crossings.

## X07 — Repeated mechanics versus semantic rule induction

**Cheapest gate:** write the repeated operation's input/output specification and list static inputs. If no specification exists, classify the proposal as a candidate policy/heuristic, not partial evaluation.

**Arms:** existing deterministic tool or lookup table; current semantic/tool-composition path; extracted mechanic; specialized mechanic with reviewed fallback. Count implementation and review effort even if performed before the measured calls.

**Workloads:** stable static inputs, frequent policy/tool/schema changes, rare repetition, previously unseen boundary cases, specialization explosion and invalid static assumptions. Use exhaustive small-domain or meaningful property checks where possible before paid inference.

**Measure:** construction/review/testing time, size, lifetime before invalidation, per-use applicability and execution, repair cost and behavioral equivalence on the declared domain. **Falsifier:** no future-use break-even, untested policy induction masquerading as equivalence, or fallback missing after version change.

**Exit:** one maintained mechanic and restricted claim, or keep the flexible baseline. No compiler framework justified by this alone.

## X08 — Event, poll and hybrid observation

**Cheapest gate:** establish whether a source offers current snapshots, complete/resumable changes, hints only, or irreplaceable events. A replay with one deliberately dropped change distinguishes a robust observation contract from an unsupported notification assumption.

**Arms:** periodic scoped polling; event-driven reads; event dirtying plus demand reads; snapshot/watch plus bounded reconciliation. Match required detection latency and history obligations; otherwise cost comparisons are unfair.

**Faults/workloads:** long dormancy; high event rate and low consumption; duplicates/out-of-order delivery; disconnect past retained history; lost cursor; source restart; fan-out and mass reconnect. Current-state reconciliation cannot recover a vanished event when its history is required.

**Measure:** source and consumer work, bandwidth, missed/late required observations, gap repair, idle overhead, queue depth, reconnect amplification and retained event/cursor bytes. **Falsifier:** savings rely on silent gaps or relaxed detection obligations, or handling changes costs more than bulk queries.

**Exit:** per-source choice, including hybrid or polling where appropriate; no global Observer service design. B04 applies to unique observations.

## X09 — Locality, shared reuse and in-flight duplicate work

**Cheapest gate:** compare payload size/round-trip/verification cost with actual local computation on a fixture; identify whether sharing is authorized. If transport/checking already dominates, stop remote-cache design for that operation.

**Arms:** local direct computation; local memoization; remote result cache; move computation to data; permitted in-flight request coalescing. Hold result and authority contracts fixed. Compare narrow same-scope sharing before cross-project sharing.

**Workloads/faults:** small cheap results, large source packets, costly stable computation, permission churn, hot-key bursts, remote failure, producer poisoning, unauthorized reader and independent-review tasks that must not share an answer before their judgment.

**Measure:** total work once, per-consumer completion, transport, egress/storage, checks, duplicate work, cancellation, cold misses and shared outage effects. Report allocation separately from total savings.

**Falsifier:** extra data movement/coordination exceeds saved work or coalescing changes required independence/authority. **Exit:** one placement/sharing scope with a fallback, or local work. Unknown external effects stop at B02.

## X10 — Conservative approximation and statistical routing

**Cheapest gate:** distinguish a sound property abstraction from a heuristic predictor; define loss, coverage and fallback. Build a tiny missed-required-path fixture before training a router.

**Arms:** direct exact/deterministic baseline when available; direct established reasoning baseline; cheap route plus check/abstention/escalation; conservative filter plus exact fallback. Evaluation data must be independently defensible and split before optimization. Do not treat the expensive model's outputs as unquestioned ground truth.

**Controls:** out-of-distribution cases, missing evidence, answer-option reordering, ambiguous/unanswerable cases, forced high escalation, correlated scorer/model mistakes, and tasks whose only successful path looks unlikely. Simulations need separate validation of modeled environment assumptions as well as numerical error.

**Measure:** accepted risk versus coverage, eventual task success, false exclusions, abstention resolution, scorer/calibration/labeling cost, repair, inference and tail latency. Compare against routing everything directly; include calibration cost over a credible lifetime.

**Falsifier:** quality threshold missed, calibration collapses under shift, required paths excluded, or aggregate cost exceeds direct execution. **Exit:** narrowly measured routing policy or no router. Any required progress issue stops at B06; exact Kernel premises stay outside statistical acceptance.

## X11 — Graph/scheduler ablation

**Cheapest gate:** label each edge by actual dependency, organization, authority, communication or resource constraint. On a small fixture, compare a legal hand-audited order with the proposed graph order. If the graph cannot explain legality/readiness, do not optimize it as an execution plan.

**Arms:** serial execution; bounded FIFO/concurrency; simple priority or critical-path heuristic; proposed scheduler. Add batching or speculative duplication separately. Preserve independent-judgment requirements and do not simulate effect cancellation as proof of real cancellation.

**Workloads:** long critical path, wide fan-out, mixed long/short tasks, burst arrivals, shared resource bottleneck, cyclic replanning, cancellation and correlated slowdowns. Include background optimization work in capacity accounting.

**Measure:** useful throughput, p95/p99 waiting, fairness/starvation, work amplification, planner time, context transfer and integration/review effort. Derive work/path lower bounds from the fixed graph as diagnostics, not promised optimality.

**Falsifier:** sophisticated planning fails to beat bounded concurrency after its own overhead, or changes permitted/progress behavior. **Exit:** one justified policy or retain simple scheduling; no global work-tracker replacement.

## X12 — Online investment, measurement budgets and retirement

**Cheapest gate:** replay measured request/update sequences with known per-arm costs. If a static threshold or no cache wins, do not implement a learning optimizer.

**Arms:** always recompute; always materialize; measured break-even threshold; threshold with hysteresis; adaptive strategy. Give each the same observation budget. An offline oracle may bound potential improvement but must not supply future information to deployable arms.

**Workloads:** stable repetition, one-off requests, phase shifts immediately after investment, cache pressure, volatile dependencies, cost drift and alternating regimes. Charge both switching and disposal, not only accumulated hits.

**Measure:** cumulative excess cost against simple baselines and the clearly labeled oracle, switching frequency, convergence time, planner/measurement overhead, retained closure and recovery cost. A formal competitive ratio from a simpler rent/buy problem is not evidence for this workload.

**Falsifier:** regret/switching/observation cost outweigh saved work or “learning” never recovers setup within useful lifetime. **Exit:** budgeted policy with a reset/fallback or intentionally unbuilt adaptive machinery.

## Ablation acceptance and reporting

For an admitted candidate, report normal, absent, stale/incorrect, recovering and overloaded behavior. Include a successful path in every required mode; safety through permanent refusal is not sufficient when the baseline promises continuation. Run interaction checks only where mechanisms share costs or evidence—for example context compression plus semantic caching, or delta maintenance plus eviction—not an indiscriminate combinatorial test suite.

A report should state WHY the result changes a design choice, WHAT corpus/versions/failures it covers, HOW CERTAIN it is with uncertainty intervals where appropriate, and WHAT-NOT-TESTED. A negative result is a successful experiment if it prevents needless machinery. Promotion from this Experimental / Derived pass requires separate review and project direction.

## Completion validation — 2026-09-29

The following checks were executed by the producing session after its self-review:

- Research branch ancestry resolves to the exact frozen commit; all eight input-manifest blobs match that commit.
- The original Efficiency Architecture body is preserved byte-for-byte as the revised file's historical suffix; its original complete-file blob matches the supplied `349eee3b51171a9365201eff5d2bd10d8cbfa719`.
- Required metadata fields, repository-local link targets and linked heading anchors resolve for all changed Markdown files.
- `git diff --check` passes. The eight countermodels rerun with stdout exactly matching the saved JSON.
- Source SHA-256: `51048e1c85b326cf67608a0435b8211c3aa45c23d9ca6b32796ab2abe82f6a11`.
- Output SHA-256: `b2c209d4f5fed06ccab6af3f9674631573ae1a3cbcc941c85027fefa4098f795`.

The self-review corrected a possible double count of cache setup versus miss execution and made the cold-recovery model's disjoint-work assumption explicit. These checks validate provenance, document structure and finite artifacts. They are **not independent adversarial review**, an audit of all cited proofs, or execution of X01–X12.

A reviewer can focus first on F02's stronger ablation boundary, F03/F04's applicability economics, and whether X02–X04 discriminate enough to defer generalized machinery. Any challenge to core currentness or recovery should be associated with B01–B06 rather than imported as settled semantics.
