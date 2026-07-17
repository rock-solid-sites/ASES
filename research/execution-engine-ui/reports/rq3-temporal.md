# RQ3 — Temporal

## Question

Can **Temporal** (https://temporal.io) be used as execution infrastructure for EDASES without imposing workflow semantics that conflict with EDASES methodology?

The question decomposes into:
1. Is Temporal an *orchestration* engine (coordinating external services) or an *execution* engine (running the actual work)? What does it assume it controls?
2. What semantic assumptions does it make — does it assume workflows are DAGs, assume sequential steps, or require a predefined structure? Can it handle emergent/adaptive execution?
3. Which of its core assumptions would conflict with EDASES (e.g. owning execution state, requiring idempotent activities, enforcing retry/persistence semantics that clash with artefact versioning)?
4. Which parts of Temporal could be reused without adopting its full model (durable execution, activity scheduling, state persistence)?
5. Can Temporal compose with a separate statechart layer (XState) for artefact lifecycles, or does it assume it owns both orchestration and lifecycle?

This is a **gap analysis**, not a fit recommendation: the goal is to identify conflicts and reusable parts, not to judge whether Temporal is "good."

## Scope

**Investigated:**
- Temporal's architectural model: orchestration vs execution, the role of the Temporal server (History/Matching services) versus user-hosted Workers.
- The determinism + event-sourcing/replay model and what it constrains.
- Whether Temporal assumes a DAG, sequential steps, or a predefined static structure; its support for dynamic/emergent, parallel, and long-running execution.
- State ownership: who owns the durable execution/lifecycle state vs domain data.
- The idempotency and retry semantics of Activities and their interaction with versioned artefacts.
- Event-history growth limits and their bearing on long-lived artefact lifecycles.
- Documented and demonstrated composition with XState/statecharts.
- Temporal's own positioning relative to state machines (relevant because EDASES intends statecharts to own artefact lifecycles).

**Excluded:**
- Hands-on deployment, benchmarking, or running Temporal (this is a literature/evidence review; no Temporal code was executed).
- Quantitative throughput/latency profiling (no authoritative benchmark located for the EDASES workload shape).
- Deep comparison against other engines (covered by sibling reports in this research line).
- Cost, operational burden, and cluster-sizing guidance beyond what bears on the semantic-conflict question.
- Any recommendation or implementation proposal (per research constraints; Temporal is named only as evidence).

## Evidence

### 1. Orchestration vs execution engine

- **Observation:** Temporal's own architecture document states: "A Temporal cluster executes units of application logic called Workflows in a durable manner that automatically handles intermittent failures, and retries failed operations." User code is "segregated into Workflow definitions and Activity definitions. Workflow code must be deterministic and have no side effects… and activity code must either be idempotent or non-retryable." (github.com/temporalio/temporal, docs/architecture/README.md)
- **Observation:** The actual side-effecting work runs in **user-hosted Worker processes**, not in the Temporal server. "In addition, the user segregates some of their application code into Temporal Workflow and Activity definitions, and hosts Worker processes, which execute their Workflow and Activity code." The Temporal server (History/Matching/ Frontend services) "store[s] all state required for durable execution" and dispatches tasks; Workers poll for tasks and report results. (docs/architecture/README.md)
- **Observation:** Activities are described as "everything that interacts with the outside world, like: API calls, Database queries, LLM invocations, File I/O." Workflows "orchestrate" and "make decisions"; Activities "do actual work in the world." (docs.temporal.io/workflows; arpitbhayani.me/blogs/temporal-primer)
- **Interpretation:** Temporal is an **orchestration / durable-execution engine**, not an execution engine in the sense of running the substantive work itself. It coordinates and makes durable the *coordination* of work; the work (side effects) executes in processes the user owns. It assumes it controls the **durable record of execution** (the event history) and the **scheduling/retry of units of work**, but not the internals of those units. This is consistent with EDASES's intended split (engine coordinates; artefacts' real content lives elsewhere) — *with the caveat* that Temporal also claims ownership of the *process/execution state*, which is the locus of the conflict (see §3, §5).

### 2. Semantic assumptions: DAG, sequential steps, predefined structure

- **Observation:** Temporal does **not** model workflows as a static DAG. "Conceptually, a workflow defines a sequence of steps. With Temporal, those steps are defined by writing code, known as a Workflow Definition." Workflows are ordinary functions in a supported SDK language; control flow (loops, branches, recursion, dynamic dispatch) is expressed in code, not declared as a graph. (docs.temporal.io/workflows)
- **Observation:** Temporal supports parallelism and composition: `workflow.Go` / Promise-based concurrency, Child Workflow Executions, Signals, Timers, and Nexus operations. A Child Workflow "can act as an entirely separate service" and "can continue on if its Parent is canceled" (Parent Close Policy `ABANDON`). (docs.temporal.io/child-workflows)
- **Observation:** Temporal explicitly supports **dynamic/emergent** execution. A Temporal blog on AI agents shows a workflow whose control flow is a `while` loop that calls an LLM Activity to *decide the next step at runtime*; the blog states: "Your Workflow is the orchestration layer… It needs to be deterministic so Temporal can help your agent survive… Your Activities are where the actual work happens… these can be as unpredictable and non-deterministic as needed." The distinction drawn: "Deterministic in execution… BUT NOT predetermined: You don't know what the LLM will decide until runtime." (temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal, 2025-11-12)
- **Observation:** Dynamic Handlers allow Workflows/Activities/Signals to be dispatched by name resolved at runtime, "for handling cases where the names… aren't known at run time" (docs.temporal.io/dynamic-handler). The docs caution they are a fallback, not the primary approach.
- **Observation (the binding constraint):** Despite the above, **Workflow code must be deterministic**. "Any time your Workflow code is executed it makes the same Workflow API calls in the same sequence, given the same input." On replay, "the Commands that are generated are compared with the existing Event History. If a generated Command doesn't match… the Workflow Execution returns a non-deterministic error." (docs.temporal.io/workflow-definition)
- **Interpretation:** Temporal does **not** assume a DAG, does **not** assume sequential-only steps, and does **not** require a predefined static structure — control flow can be arbitrary code, including runtime-emergent branching driven by external decisions. **However**, it imposes a single hard semantic assumption that subsumes the others: the *orchestration code* must be **deterministic** — given the same event history it must emit the same command sequence. Emergence is permitted only insofar as the *points of non-determinism* (which branch to take, which tool to call) are resolved by Activities/Signals/Queries whose results are recorded in the history and reused on replay. The workflow is "not predetermined" in *content* but is "predetermined" in *structure of decision points*. This is the central semantic assumption EDASES must evaluate against.

### 3. State ownership

- **Observation:** "Each Temporal Workflow Execution has exclusive access to its local state." "This history is the source of truth for everything that happens in the Workflow." (docs.temporal.io/workflows; docs.temporal.io/workflow-execution)
- **Observation:** The History Service "store[s] all state required for durable execution of the workflow" and "the sequence of History Events alone… is sufficient to recover all other relevant information about the workflow execution's state." (docs/architecture/README.md; docs/architecture/history-service.md)
- **Observation (nuance):** Temporal's own "Beyond State Machines" blog concedes domain data can live outside: "Teams can still keep domain data in their own database, but the process state itself no longer needs to be reconstructed from side effects." (temporal.io/blog/temporal-replaces-state-machines-for-distributed-applications, 2025-04-11)
- **Interpretation:** Temporal claims ownership of **process/execution state** (the event history and the derived mutable state), not necessarily of **domain/artefact content**. For EDASES this is a precise and important boundary: an artefact's *content* (its bytes, its version graph) could live in EDASES's own store, but its *lifecycle/execution state* — if driven through Temporal — would be owned by Temporal's event history, and recovery would be by **replay of that history through deterministic workflow code**, not by reading the artefact's own statechart. This directly collides with the EDASES intent that the **statechart (XState) owns the artefact lifecycle** and that recovery should be from **artefact history/provenance** (RQ6), not from execution replay. The conflict is not "Temporal stores our data" but "Temporal becomes the authority on lifecycle progression and the recovery substrate."

### 4. Idempotency, retry, and artefact versioning

- **Observation:** "An Activity is idempotent if multiple Activity Task Executions do not change the state of the system beyond the first Activity Task Execution." Activities are automatically retried by the server per a Retry Policy; "the API to schedule an Activity Execution provides an 'effectively once' experience, even though there may be several Activity Task Executions." (docs.temporal.io/activity-definition; docs.temporal.io/tasks)
- **Observation:** Temporal provides idempotency mechanisms: "activity IDs and idempotency tokens to ensure side effects are executed exactly once" (temporal.io/blog/temporal-replaces-state-machines-for-distributed-applications). Heartbeats carry forward payloads so long activities resume from a checkpoint.
- **Interpretation:** Temporal's retry model assumes activities are **idempotent or non-retryable**. If an EDASES activity *creates or versions an artefact*, an automatic retry after a crash could produce a **duplicate version** unless an idempotency key (e.g. the artefact version id) is supplied and the version store dedupes on it. This is a real, concrete conflict between Temporal's "retry until success" semantics and EDASES's artefact-versioning semantics, where a retry is not transparent — a second version is a distinct, observable artefact. It is *mitigable* (idempotency tokens, dedup-on-write) but the mitigation must be engineered at the artefact boundary; Temporal does not provide it for free for versioned content. **Assumption:** that EDASES artefact versioning is not naturally idempotent — treated as an assumption because the exact versioning model is not specified in this review.

### 5. Event-history growth limits vs long-lived artefact lifecycles

- **Observation:** "The Temporal Service logs a warning after 10,240 Events… The Workflow Execution is terminated when the Event History: exceeds 51,200 Events; contains more than 2000 Updates; contains more than 10000 Signals." Mitigation: "use the Continue-As-New feature to close the current Workflow Execution and create a new one." (docs.temporal.io/workflow-execution/event)
- **Observation:** Workflows "can run—and keep running—for years" (docs.temporal.io/workflows), but only by periodically Continue-As-New, which **resets the event history** (a new Run with a fresh history; the old history is retained separately per Run).
- **Interpretation:** A single Temporal Workflow Execution is **not** a suitable unbounded, queryable store for a multi-year artefact lifecycle if that lifecycle generates many events/signals. Continue-As-New resets history, fragmenting the durable log across Runs. For EDASES, where artefact provenance is expected to be a persistent, queryable record (RQ6), Temporal's per-execution event history is a **bounded, periodically-reset** substrate — a conflict if one expected a single Temporal execution to be the artefact's lifelong provenance log. Provenance would have to be externalised to EDASES's own store.

### 6. Composition with a statechart layer (XState)

- **Observation:** There is a documented, working demonstration of XState running **inside** a Temporal Workflow: `Devessier/temporal-electronic-signature`. The workflow function creates an XState machine, `interpret`s it, maps Temporal **Signals → XState events**, exposes Temporal **Queries → XState state**, and `await`s the machine reaching a final state. The comment in the code states: "When using XState, logic should never happen where events are sent. Logic is handled inside the state machine." (github.com/Devessier/temporal-electronic-signature, packages/temporal/src/workflows/index.ts)
- **Observation:** The sibling RQ2 (XState) report already records the general pattern: "XState often runs *inside* a workflow engine task"; "XState owns in-process/UI↔backend orchestration while workflow engines own cross-service durability." (research/execution-engine-ui/reports/rq2-xstate.md, §7)
- **Observation:** In the demo, the XState machine runs *inside the deterministic Temporal workflow function*. Because XState transitions are a pure function of (signal sequence, current state), and Temporal records signals in its event history, the machine is **replay-deterministic** — given the same signal history it reaches the same state. So the composition is technically coherent with Temporal's determinism requirement.
- **Interpretation:** Composition is **possible and demonstrated**, but the demonstrated pattern places Temporal in the **dominant** role: Temporal owns the durable execution, the recovery-by-replay, and the external interaction surface (Signals/Queries); the statechart is nested *within* Temporal's workflow and is recovered *through* Temporal's replay, not independently. This is the **inversion** of the EDASES intent: EDASES wants the statechart to own the artefact lifecycle and the engine to be a neutral coordinator. Under the demonstrated composition, Temporal owns the lifecycle *durability* and the statechart is a passenger. Whether a *reversed* composition (statechart owns lifecycle, Temporal only schedules activities) is feasible is an open question — see Unknowns.

### 7. Temporal's positioning relative to state machines

- **Observation:** Temporal markets itself as a **replacement** for hand-rolled state machines: "Temporal: Beyond State Machines for Reliable Distributed Applications" argues "you stop building a state machine framework inside your application and start treating orchestration as infrastructure." A third-party analysis (techbytes.app, 2026-04-06) makes the same case: custom state machines "scatter process logic across services"; Temporal "turns the happy path back into readable code." (temporal.io/blog/temporal-replaces-state-machines-for-distributed-applications; techbytes.app/posts/temporal-workflow-engine-replacing-state-machines)
- **Interpretation:** Temporal's *design philosophy* is that durable process state should be owned by the orchestration engine, not by a separate statechart. This is a **philosophical conflict** with EDASES's methodology, which assigns lifecycle ownership to statecharts and reserves the engine for coordination. The conflict is not merely technical — it is a clash of which layer is authoritative for lifecycle. EDASES would be using Temporal against its intended grain.

## Findings

**F1 — Temporal is an orchestration / durable-execution engine, not an execution engine.** The substantive work runs in user-owned Workers; Temporal owns the durable record of coordination and the scheduling/retry of work units. This matches EDASES's intended split *in principle* (engine coordinates; content lives elsewhere), but only if "coordination" is understood narrowly. (Evidence §1)

**F2 — Temporal does not assume a DAG, sequential steps, or a predefined static structure.** Control flow is arbitrary code; parallelism, child workflows, signals, and runtime-emergent branching are all supported. The single hard assumption is **determinism of the orchestration code**: given the same event history, the same command sequence must be emitted. Emergence is allowed only at points resolved by recorded Activities/Signals. (Evidence §2)

**F3 — Temporal claims ownership of process/execution state, not domain content.** The event history is "the source of truth." Artefact *content* can live in EDASES's own store, but artefact *lifecycle/execution state* driven through Temporal would be owned by Temporal and recovered by **replay**, not by reading the artefact's own statechart. This collides with the EDASES intent that the statechart owns lifecycle and that recovery is from artefact provenance (RQ6). (Evidence §3)

**F4 — Temporal's retry/idempotency model conflicts with artefact versioning.** Automatic activity retry assumes idempotency; a retry of a "create/version artefact" activity can produce a duplicate version unless an idempotency key is supplied and the version store dedupes. Mitigable, but not free, and the mitigation lives at the artefact boundary. (Evidence §4)

**F5 — A single Temporal Workflow Execution is a bounded, periodically-reset log, not a lifelong provenance store.** Event-history caps (51,200 events; Continue-As-New resets history) make it unsuitable as the unbounded, queryable provenance record an EDASES artefact lifecycle would need. Provenance must be externalised. (Evidence §5)

**F6 — Composition with XState is demonstrated but inverts the intended authority.** XState can run inside a Temporal workflow (Signals→events, Queries→state), and is replay-deterministic. But in that pattern Temporal owns durability and recovery; the statechart is nested within Temporal. This is the reverse of EDASES's intended layering (statechart owns lifecycle, engine coordinates). (Evidence §6)

**F7 — Temporal's design philosophy is to replace state machines, not to host them as lifecycle authority.** Its marketing and third-party analysis position it as the owner of durable process state. Using it as a neutral coordinator under a statechart-owned lifecycle runs against its intended grain. (Evidence §7)

**Net assessment for the gap question:** Temporal *can* be used as execution infrastructure, and several of its parts are reusable (durable task scheduling, retry with idempotency tokens, signal/query interaction, event-sourced durability). But its **core semantic assumptions — determinism of orchestration code, ownership of process/execution state, replay-based recovery, idempotent-retry activities, and bounded per-execution history — each conflict, to varying degrees, with EDASES's methodology** that assigns lifecycle authority to statecharts and recovery to artefact provenance. The conflicts are mitigable only by pushing EDASES lifecycle logic *into* Temporal's model (making the statechart a passenger) or by using Temporal in a reduced capacity (a durable task scheduler + event log) that forgoes the parts of Temporal that create the conflicts.

## Rejected options

- **Treating Temporal as a neutral task queue with no semantic assumptions.** Rejected: Temporal's determinism + replay model and its ownership of event history are not optional — they are load-bearing for its durability guarantees. One cannot use Temporal for durable execution while ignoring the determinism constraint.
- **Treating Temporal as a drop-in statechart host where the statechart remains the lifecycle authority.** Rejected as the *demonstrated* pattern: the only documented XState+Temporal integration nests XState inside the Temporal workflow, making Temporal the recovery authority. A reversed composition (statechart authority, Temporal as pure scheduler) is unevidenced here and is recorded as an Unknown rather than asserted.
- **Treating Temporal's event history as the EDASES artefact provenance store.** Rejected: per Evidence §5 the per-execution history is bounded and reset by Continue-As-New; it is not a lifelong, queryable provenance substrate. Provenance must live in EDASES's own store.
- **Relying on Temporal's marketing/"Beyond State Machines" material as evidence that statecharts are unnecessary.** Rejected: that material argues Temporal *replaces* state machines, which is the opposite of the EDASES assignment of lifecycle ownership to statecharts; it is cited as *evidence of the conflict* (F7), not as a recommendation.
- **Recommending or proposing a specific EDASES+Temporal implementation.** Explicitly excluded per research constraints; Temporal is named only as evidence for the gap analysis.

## Unknowns

- **Reversed composition feasibility.** Whether a viable architecture exists where the XState statechart owns the artefact lifecycle and Temporal is used *only* as a durable activity scheduler (statechart drives; Temporal merely makes activity execution durable) — without nesting the statechart inside a Temporal workflow. The reviewed evidence covers only the nested (Temporal-dominant) pattern.
- **Determinism cost for EDASES lifecycles.** How much of a typical EDASES artefact lifecycle (external-event-driven, possibly LLM/agent-driven transitions) can be expressed as deterministic orchestration code with non-determinism pushed into Activities/Signals, and at what engineering cost. Not quantified here.
- **Idempotency at the artefact boundary.** Whether EDASES's artefact-versioning store can dedupe on an idempotency token such that Temporal's automatic retries never create spurious versions. Depends on the (unspecified here) versioning model.
- **Multi-artefact coordination model.** How Temporal would coordinate *many* independent artefact lifecycles (one workflow per artefact? one parent workflow with child workflows per artefact?) and whether the per-execution event-history caps become a practical limit at EDASES's artefact counts. Not assessed.
- **Recovery substrate interaction with RQ6.** Temporal recovers by replay of execution history; RQ6 favours recovery from artefact provenance. Whether these two recovery substrates can coexist without contradiction (e.g. Temporal durability for *coordination*, EDASES provenance for *reasoning recovery*) is unresolved by this review.

## Confidence

**Medium-High.**

- **High confidence** on the architectural facts that drive the conflicts: Temporal is an orchestration/durable-execution engine (§1); it does not assume a DAG/sequential/predefined structure but requires deterministic orchestration code (§2); it owns process/execution state via event history (§3); activities are retried and assumed idempotent (§4); per-execution history is bounded and reset by Continue-As-New (§5). These are directly documented by Temporal's own architecture docs and SDK documentation.
- **High confidence** on the demonstrated XState-inside-Temporal composition pattern (§6) — it is a published, code-level demonstration.
- **Medium confidence** on the *severity* of each conflict for EDASES specifically, because the precise EDASES artefact-versioning model, lifecycle shape, and recovery requirements are not fully specified in this review; the conflicts are inferred from documented Temporal semantics against the stated EDASES intent. The reversed-composition option (§6, Unknowns) is unevidenced and lowers confidence on the "can it compose as intended" sub-question.
- Confidence is **not High overall** because the most EDASES-favourable composition (statechart authority + Temporal as neutral scheduler) was not found evidenced and remains an open architectural question.

## References

- Temporal architecture overview — github.com/temporalio/temporal, docs/architecture/README.md
- Temporal Workflow Execution overview — docs.temporal.io/workflow-execution
- Temporal Workflow — docs.temporal.io/workflows
- Temporal Workflow Definition (determinism, versioning) — docs.temporal.io/workflow-definition
- Events and Event History — docs.temporal.io/workflow-execution/event
- Tasks (Workflow/Activity/Query tasks, replay) — docs.temporal.io/tasks
- Child Workflows — docs.temporal.io/child-workflows
- Dynamic Handler — docs.temporal.io/dynamic-handler
- Activity Definition (idempotency) — docs.temporal.io/activity-definition
- History Service internals — github.com/temporalio/temporal, docs/architecture/history-service.md
- Workflow lifecycle sequence — github.com/temporalio/temporal, docs/architecture/workflow-lifecycle.md
- "Of course you can build dynamic AI agents with Temporal" — temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal (2025-11-12)
- "Temporal: Beyond State Machines for Reliable Distributed Applications" — temporal.io/blog/temporal-replaces-state-machines-for-distributed-applications (2025-04-11)
- "Temporal Workflow Engine: Replacing State Machines" — techbytes.app/posts/temporal-workflow-engine-replacing-state-machines (2026-04-06)
- "Temporal Primer — Building Long-Running Systems" — arpitbhayani.me/blogs/temporal-primer (2026-05-20)
- XState-inside-Temporal demonstration — github.com/Devessier/temporal-electronic-signature (packages/temporal/src/workflows/index.ts)
- Sibling report: RQ2 — XState/Stately — research/execution-engine-ui/reports/rq2-xstate.md (§7 composition)
- Sibling report: RQ6 — Artefact recovery from artefact history — research/execution-engine-ui/reports/rq6-artefact-recovery.md
