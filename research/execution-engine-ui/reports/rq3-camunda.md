# RQ3 — Camunda/BPMN

## Question

Can **Camunda** (https://camunda.com) and the **BPMN** (Business Process Model and Notation) standard it implements be used as execution infrastructure for EDASES without imposing workflow semantics that conflict with EDASES methodology?

The question decomposes into:
1. Is Camunda an *orchestration* engine (coordinating external work) or an *execution* engine (running the substantive work)? What does it assume it controls?
2. What semantic assumptions does BPMN make — does it assume sequential/parallel gateways and predefined process models? Does it require activities to fit into a BPMN diagram? Can it handle emergent/adaptive execution?
3. Which of Camunda/BPMN's core assumptions would conflict with EDASES (e.g. rigid process definitions, enforced execution semantics such as timers/compensation/error boundaries that clash with artefact versioning, business-process framing as a wrong abstraction for engineering work)?
4. Which parts of Camunda could be reused without adopting BPMN fully (e.g. the Zeebe engine, job workers, state persistence)?
5. Can Camunda compose with a separate statechart layer (XState) for artefact lifecycles, or does BPMN assume it owns the full lifecycle?

This is a **gap analysis**, not a fit recommendation: the goal is to identify conflicts and reusable parts, not to judge whether Camunda is "good."

## Scope

**Investigated:**
- Camunda's self-positioning as an orchestration engine and the architectural split between the Zeebe broker (state + scheduling) and external job workers (business logic).
- Camunda 7 vs Camunda 8 (Zeebe): the two are architecturally distinct; which one is the relevant subject of analysis.
- BPMN's semantic assumptions: predefined process models, gateway-based control flow, token semantics, and the requirement that activities fit a BPMN diagram.
- BPMN's support for emergent/adaptive execution (ad-hoc sub-processes, introduced in Camunda 8.7) and its limits.
- BPMN-enforced execution semantics that may conflict with artefact versioning: compensation, error/timer/escalation boundary events, message correlation.
- State ownership: who owns process-instance state and how recovery works (event-sourced log, replay).
- Reusable engine parts decoupled from BPMN semantics (job-worker dispatch, durable event log, exporters, message correlation, horizontal scaling).
- Documented/demonstrable composition with a statechart layer (XState); comparison with the Temporal case (sibling report).
- Licensing posture of Camunda 8 (Zeebe) vs Camunda 7, as it bears on reuse.

**Excluded:**
- Hands-on deployment, benchmarking, or running Camunda/Zeebe (this is a literature/evidence review; no Camunda code was executed).
- Quantitative throughput/latency profiling (no authoritative benchmark located for the EDASES workload shape).
- Deep comparison against other engines (covered by sibling reports in this research line: rq3-temporal.md, rq3-langgraph.md).
- Cost, operational burden, and cluster-sizing guidance beyond what bears on the semantic-conflict question.
- Any recommendation or implementation proposal (per research constraints; Camunda is named only as evidence).

## Evidence

### 1. Orchestration vs execution engine

- **Observation:** Camunda's own product page titles Zeebe "The Distributed Orchestration Engine" and states: "Zeebe is the distributed engine at the heart of Camunda… ready for the durable multi-agent coordination that comes next." It describes the engine as driving "long-running, mission-critical processes" and holding "state across long-running, multi-agent work." (camunda.com/platform/orchestration-engine; camunda.com/products/zeebe)
- **Observation:** The Zeebe architecture documentation states the broker's only responsibilities are: "Processing commands sent by clients; Storing and managing the state of active process instances; Assigning jobs to job workers." It explicitly notes: "It's important to note that no application business logic lives in the broker." (docs.camunda.io/docs/components/zeebe/technical-concepts/architecture)
- **Observation:** A job worker is "a Zeebe Client that polls for and executes available jobs. An uncompleted job prevents Zeebe from advancing process execution to the next step." The worker "performs them and sends back a `complete` or `fail` command." Business logic lives in the worker application, which connects via gRPC/REST. (docs.camunda.io/docs/components/concepts/job-workers)
- **Observation (Camunda 7 contrast):** Camunda 7 allows embedding the engine as a library in the application; "both run in the same JVM, share thread pools, and can even use the same data source and transaction manager." Camunda 8 (Zeebe) "is always a remote resource for your application, while the embedded engine mode is not supported." (docs.camunda.io/docs/guides/migrating-from-camunda-7/conceptual-differences)
- **Interpretation:** Camunda 8 (Zeebe) is an **orchestration / durable-execution engine**, not an execution engine in the sense of running the substantive work. It coordinates and durably persists the *coordination* of work (process-instance state, job assignment, timers, message correlation); the side-effecting work executes in external worker processes the user owns. This is structurally analogous to Temporal's orchestration/worker split (see rq3-temporal.md). Camunda 7, by contrast, can be an *embedded* engine that shares the application's transaction boundary — a different and, for EDASES, arguably more invasive assumption (the engine lives inside your process and your database). The relevant subject for EDASES is **Camunda 8 / Zeebe**, because Camunda 7 is in long-term support with end-of-life in April 2027 (automationatlas.io/guides/camunda-vs-zeebe-2026; altkomsoftware.com/blog/camunda-8-vs-camunda-7-challenges).

### 2. Semantic assumptions: predefined models, gateways, token flow

- **Observation:** BPMN is "an open standard for modelling business processes" and "BPMN workflows are simply XML files that are created using purpose built visual modelling tools." A BPMN file "needs a Start Node" and "at least one end node." Activities are connected by sequence flows and routed by gateways (exclusive / parallel / inclusive). (medium.com/@justintilson/workflows-bpmn-32a05c1f757a)
- **Observation:** BPMN's execution semantics are formally ambiguous. Multiple academic sources note the specification "does not include a formal semantics" (Wong, A Process Semantics for BPMN) and that "the BPMN standard lacks a commonly agreed formal foundation, leading to variability in execution across different BPM systems (BPMSs)." (Dijkman, Dumas, Ouyang, "Semantics and analysis of business process models in BPMN", Information and Software Technology 2008; Casciani et al., Information Systems 2026)
- **Observation:** Camunda 8 only allows storage of "primary data types or JSON as process variables" (not arbitrary serialized objects as Camunda 7 did), and expressions use FEEL, which "can only access the process instance data and variables." (docs.camunda.io/docs/guides/migrating-from-camunda-7/conceptual-differences)
- **Interpretation:** BPMN **assumes a predefined process model exists before execution** and that every activity, gateway, and event is a node in that deployed diagram. Control flow is expressed declaratively as a graph of gateways and sequence flows, not as arbitrary code. This is a stronger structural assumption than Temporal's (where control flow is code). The well-documented *ambiguity* of BPMN semantics across engines is itself a risk: EDASES would inherit not just Camunda's interpretation but the broader hazard that BPMN diagrams are not a precise, formally-grounded execution contract. The JSON-only process-variable model is a coarse-grained, instance-scoped data container — a poor fit for EDASES's artefact version graphs, which are expected to be first-class, queryable, and externally owned (RQ6).

### 3. Emergent / adaptive execution — and its limits

- **Observation:** Camunda 8.7 (2025) introduced **ad-hoc sub-processes**, described as "the first step towards dynamic processes and execution of ad-hoc activities." Inner elements "are not connected to a start or end event. Each element can be executed multiple times, in any order, or skipped." Which elements execute "could be a person, rule, microservice, or artificial intelligence." (camunda.com/blog/2025/04/camunda-8-7-release; docs.camunda.io/docs/components/modeler/bpmn/ad-hoc-subprocesses)
- **Observation (constraint):** Ad-hoc sub-processes "Must have at least one activity; Must not have start events or end events." Activation is driven by an `activeElementsCollection` expression evaluated *on entering* the sub-process; the docs note: "Currently, it is not possible to activate elements dynamically after the ad-hoc sub-process is activated, only on entering the subprocess." Completion is via a `completionCondition` or when all activated elements complete. (docs.camunda.io/docs/components/modeler/bpmn/ad-hoc-subprocesses)
- **Interpretation:** Camunda has moved *toward* emergent execution, but only within a BPMN container that is still deployed as a model and still owns the instance lifecycle. The ad-hoc sub-process is a bounded relaxation of rigidity (choose-which-tasks, in-any-order), not a genuine abandonment of the predefined-model assumption: the *set of possible* elements is fixed at design time, and dynamic activation is limited to entry-time evaluation. For EDASES, where artefact lifecycles may need to emerge from engineering events rather than from a pre-drawn diagram, BPMN remains a *constraining frame* even with ad-hoc sub-processes. **Assumption:** that EDASES artefact lifecycles are more open-ended than ad-hoc sub-processes permit — treated as an assumption because the exact EDASES lifecycle shape is not specified in this review.

### 4. Enforced execution semantics that may conflict with artefact versioning

- **Observation:** BPMN provides compensation events that "undo the effects of activities that already successfully completed… when the side-effects of a completed action need to be reversed because the larger transaction failed." (github.com/dr-dobermann/gobpm, bpmn-spec/semantics/compensation.md; dev.to/nirankari/bpmn-compensation-events) Camunda lists "Compensation: Roll back a transaction cleanly when downstream steps fail" as a native engine pattern. (camunda.com/platform/orchestration-engine)
- **Observation:** BPMN boundary events (error, timer, escalation, message, cancel) attach to activities and alter flow. Timer boundary events force waits or timeouts; error boundary events catch business exceptions; escalation routes overdue work to a higher tier. These are "native support for the patterns enterprise processes actually need." (flowsforapex.org/latest/boundary-events; camunda.com/platform/orchestration-engine)
- **Observation:** Zeebe correlates "inbound messages from external systems to the correct in-flight process instance" (message correlation) and supports "Time-based escalation: Automatically route overdue tasks to the next tier when SLAs are at risk." (camunda.com/platform/orchestration-engine)
- **Interpretation:** These are precisely the **conflict locus** with EDASES artefact versioning. In EDASES, a completed artefact version is expected to be an immutable, observable record; "undo" is a *new* version, not a rollback of the old one. BPMN compensation semantics assume a reversible transaction model where completed activities can be *undone* — directly at odds with an immutable-version-graph model. Timer/escalation/SLA boundary events assume a business-process temporality (deadlines, human escalation tiers) that is a wrong abstraction for engineering artefact progression, where timeouts and escalations are domain-specific and owned by the artefact's own statechart, not by the orchestration engine. If these BPMN semantics are *not used*, they are simply absent from the model — but their *availability and centrality* in the BPMN mental model means any BPMN-authored process is tempted to express lifecycle concerns in engine-native terms that EDASES wants to keep in the statechart layer.

### 5. State ownership and recovery

- **Observation:** Zeebe "tracks the state of active process instances" in brokers; state is an "event-sourced log" in RocksDB, "replicated via Raft." (automationatlas.io/guides/camunda-vs-zeebe-2026) The exporter system "provides an event stream of state changes within Zeebe." (docs.camunda.io/docs/components/zeebe/technical-concepts/architecture)
- **Observation:** Process-instance state is held as element instances with "Active, completed, terminated states," scoped variables, and job keys. (deepwiki.com/camunda/camunda/2.1-zeebe-workflow-engine)
- **Interpretation:** Zeebe claims ownership of **process-instance execution state** and recovers by **replaying its event-sourced log**, not by reading the artefact's own statechart or provenance. This is the same structural conflict identified for Temporal (rq3-temporal.md, §3): the engine becomes the authority on lifecycle progression and the recovery substrate. For EDASES, where recovery is expected to derive from **artefact history/provenance** (RQ6) and the **statechart owns the lifecycle**, Zeebe's ownership of instance state inverts the intended responsibility boundary. The exporter event stream is a *mitigating* feature — it externalises state changes and could feed an EDASES provenance store — but it is a *copy* of Zeebe's state, not the authoritative artefact record.

### 6. Reusable parts decoupled from BPMN

- **Observation:** The job-worker pattern is a generic work-distribution mechanism: workers poll/stream for jobs of a `type`, execute, and report `complete`/`fail`; Zeebe guarantees each job goes to exactly one worker and reassigns on timeout. Workers can be implemented "in any language with a Camunda client" (Java, Node.js, C#, Go, Python). (docs.camunda.io/docs/components/concepts/job-workers; docs.camunda.io/docs/apis-tools/java-client/job-worker)
- **Observation:** Zeebe provides horizontal scalability ("no central database to choke on. Add nodes to add throughput"), self-healing peer-to-peer brokers ("no single point of failure"), and message correlation to in-flight instances. (camunda.com/platform/orchestration-engine)
- **Observation:** The exporter system emits a continuous event stream of state changes usable for "monitoring the current state of running process instances" and external analytics. (docs.camunda.io/docs/components/zeebe/technical-concepts/architecture)
- **Interpretation:** The **reusable substrate** inside Camunda, separable from BPMN's business framing, is: (a) a durable, distributed **job dispatcher / task queue** with at-least-once delivery and timeout-based reassignment; (b) an **event-sourced, replicated state log** with recovery-by-replay; (c) a **message-correlation** mechanism; (d) operational infrastructure (scaling, self-healing, exporters). These could, in principle, be reused as neutral execution infrastructure *without* authoring BPMN diagrams — but **only with significant caveats**: Zeebe's job model is intrinsically tied to BPMN service tasks and process instances; there is no first-class "run this arbitrary durable function" API independent of a deployed process definition (unlike Temporal's Workflow/Activity SDKs, which are language-native). Using Zeebe as a bare job engine would mean modelling even trivial coordination as BPMN, or driving it through ad-hoc sub-processes / call activities — i.e. the BPMN frame cannot be fully escaped. **Assumption:** that Zeebe cannot be cleanly used as a BPMN-free durable-execution kernel — treated as an assumption because no authoritative "Zeebe without BPMN" deployment pattern was located in this review.

### 7. Composition with a statechart layer (XState)

- **Observation:** Because business logic lives in external job workers, a statechart (e.g. XState) *could* run inside a worker: the BPMN process would be a thin orchestration shell (a service task or ad-hoc sub-process) and the statechart would own the per-artefact lifecycle internally. Camunda 8.7's ad-hoc sub-process "can be handled internally by Zeebe, or by using a job worker," and "in an ad-hoc sub-process handled by a job worker, the job worker decides which elements to activate and when the ad-hoc sub-process is complete." (docs.camunda.io/docs/components/modeler/bpmn/ad-hoc-subprocesses)
- **Observation:** Call activities allow invoking "another process as part of this process… stored as separated BPMN" — but this is BPMN-to-BPMN composition, not statechart composition. (docs.camunda.io/docs/components/modeler/bpmn/call-activities/call-activities.md)
- **Observation (contrast with Temporal):** The sibling rq3-temporal.md records a *demonstrated* XState-inside-Temporal pattern (Devessier/temporal-electronic-signature) with Signals→XState events and Queries→XState state. No equivalent documented, working demonstration of XState (or any statechart) running inside a Camunda/Zeebe worker for the EDASES pattern was located in this review.
- **Interpretation:** Composition is **architecturally possible** (statechart inside a worker, engine as neutral coordinator) but **not demonstrated** for the EDASES shape, and it would reproduce the same inversion seen with Temporal: BPMN/Zeebe would still own the *process-instance durability, recovery-by-replay, and external interaction surface*, while the statechart is nested *within* a BPMN task and recovered *through* Zeebe's log, not independently. This is the inverse of the EDASES intent (statechart owns lifecycle; engine is a neutral coordinator). Whether a *reversed* composition (statechart owns lifecycle, Zeebe only dispatches jobs) is feasible depends on whether Zeebe can be driven without a controlling BPMN process definition — see §6 and Unknowns.

### 8. Licensing posture (bears on reuse)

- **Observation:** Camunda 7 is "Free, open source (Apache 2.0)." Camunda 8 / Zeebe is "source-available (Camunda Platform License)"; the SaaS has a free Starter tier and self-managed starts at a commercial price. (automationatlas.io/guides/camunda-vs-zeebe-2026)
- **Interpretation:** If EDASES were to reuse Zeebe's engine internals (the reusable parts in §6), it would do so under a **source-available, non-OSI license**, not a permissive open-source license. This is a governance/abstraction-boundary consideration: reusing Zeebe as infrastructure couples EDASES to Camunda's commercial licensing, which may conflict with EDASES's research/implementation independence goals (per AGENTS.md, methodology should remain tool-independent). **Assumption:** that EDASES requires permissive/open licensing for reused infrastructure — treated as an assumption because the project's licensing policy is not specified in this review.

## Findings

1. **Camunda 8 (Zeebe) is an orchestration engine, not an execution engine.** It coordinates and durably persists coordination state; substantive work runs in external job workers. This matches EDASES's intended split (engine coordinates; artefact content lives elsewhere) at the architectural level. (§1)
2. **BPMN imposes a predefined-model assumption that conflicts with emergent artefact lifecycles.** Activities must be nodes in a deployed BPMN diagram; control flow is declarative gateway graph, not code. Ad-hoc sub-processes relax but do not remove this frame. (§2, §3)
3. **BPMN's enforced execution semantics (compensation, error/timer/escalation boundaries, SLA escalation) are a direct conflict with artefact versioning.** They assume reversible transactions and business-process temporality, whereas EDASES expects immutable versions and domain-owned lifecycle timing. (§4)
4. **Zeebe owns process-instance state and recovers by replay of its event log**, inverting the EDASES intent that the statechart owns the lifecycle and recovery derives from artefact provenance. (§5)
5. **Reusable parts exist** (durable job dispatch, event-sourced replicated log, message correlation, scaling/self-healing, exporters) but are **intrinsically coupled to the BPMN process-instance model**; clean BPMN-free reuse is unconfirmed. (§6)
6. **Composition with a statechart is architecturally possible but not demonstrated** for the EDASES pattern, and would reproduce the engine-dominant inversion seen with Temporal. (§7)
7. **Licensing**: Zeebe is source-available (Camunda Platform License), not permissive open source — a governance consideration for reuse. (§8)

The central conflict is **not** "Camunda runs our code" (it does not, by design) but **"Camunda/BPMN owns the lifecycle frame"**: the predefined BPMN model, the engine-native execution semantics, and the engine-owned instance state together assert authority over exactly the lifecycle concerns EDASES intends to delegate to statecharts and artefact provenance.

## Rejected options

- **Adopt Camunda 7 as an embedded engine.** Rejected as the primary subject because it is in LTS with EOL April 2027 and because embedding the engine inside the application (sharing JVM, database, and transactions) is a *more* invasive assumption than Zeebe's remote model — it couples EDASES's data store and transaction boundary to Camunda. Still noted as evidence for the C7/C8 architectural contrast (§1).
- **Treat BPMN ad-hoc sub-processes as sufficient for emergent lifecycles.** Rejected as a resolution because activation is limited to entry-time evaluation and the element set is fixed at design time; it relaxes rigidity without removing the predefined-model assumption (§3).
- **Use Zeebe purely as a BPMN-free durable-execution kernel.** Considered but not substantiated: no authoritative pattern for driving Zeebe without a deployed BPMN process definition was located; its job model is tied to BPMN service tasks (§6). Left as an Unknown rather than accepted.
- **Assume XState-inside-Camunda composition is demonstrated.** Rejected: unlike the Temporal case, no working demonstration of this specific composition was found in this review (§7).

## Unknowns

- Whether Zeebe can be driven as a durable job/execution engine **without authoring any BPMN process definition** (e.g. via ad-hoc sub-processes, call activities, or undocumented APIs). This determines whether the reusable parts in §6 are attainable without adopting BPMN's semantic frame.
- The exact shape of EDASES artefact lifecycles and whether they exceed what BPMN ad-hoc sub-processes can express (assumption in §3).
- Whether EDASES's artefact versioning is naturally immutable-versioned vs reversible (assumption in §4) — this governs the severity of the compensation/rollback conflict.
- Whether EDASES requires permissive/open licensing for reused infrastructure (assumption in §8), which would rule out Zeebe's source-available license regardless of technical fit.
- The behaviour of Zeebe's exporter stream as a provenance feed: fidelity, ordering guarantees, and whether it can serve as the authoritative EDASES provenance record rather than a copy of engine state (§5).
- Whether a *reversed* composition (statechart owns lifecycle, Zeebe only dispatches jobs) is feasible given Zeebe's process-instance-centric model (§6, §7).

## Confidence

**Medium.**

Justification: The architectural facts (Zeebe as remote orchestration engine, external job workers, event-sourced replicated state, BPMN predefined-model and gateway semantics, compensation/boundary-event semantics, Camunda 7 vs 8 distinction, source-available licensing) are well-documented by Camunda's own materials and corroborated by independent sources, giving **high confidence** on the *structural* conflict (engine owns lifecycle frame; BPMN assumes predefined models and reversible/transactional execution semantics).

Confidence is **medium** rather than high because: (a) the possibility of using Zeebe *without* BPMN (clean reuse of the engine substrate) is unconfirmed and could materially change the reusability verdict; (b) no demonstration of XState/Camunda composition was located, leaving the composition question partly open; and (c) several findings depend on assumptions about EDASES's own (unspecified here) lifecycle and versioning models. These are gaps in *this review's* evidence, not in Camunda's documentation.

## References

- Camunda. "Zeebe: The Distributed Orchestration Engine." camunda.com/platform/orchestration-engine
- Camunda. "Zeebe: Cloud-Native Workflow Engine." camunda.com/products/zeebe
- Camunda Docs. "Architecture" (Zeebe technical concepts). docs.camunda.io/docs/components/zeebe/technical-concepts/architecture
- Camunda Docs. "Job workers." docs.camunda.io/docs/components/concepts/job-workers
- Camunda Docs. "Job worker" (Java client). docs.camunda.io/docs/apis-tools/java-client/job-worker
- Camunda Docs. "Conceptual differences" (Camunda 7 vs 8). docs.camunda.io/docs/guides/migrating-from-camunda-7/conceptual-differences
- Camunda Docs. "Ad-hoc sub-processes." docs.camunda.io/docs/components/modeler/bpmn/ad-hoc-subprocesses
- Camunda Docs. "Call activities." docs.camunda.io/docs/components/modeler/bpmn/call-activities/call-activities.md
- Camunda Blog. "Camunda 8.7 Release is Here." camunda.com/blog/2025/04/camunda-8-7-release
- Camunda Blog. "An Advanced Ad-Hoc Sub-Process Tutorial." camunda.com/blog/2025/04/an-advanced-ad-hoc-sub-process-tutorial
- Camunda. "Case Management." camunda.com/solutions/case-management
- Altkom Software. "Camunda 8 vs Camunda 7: Key Differences, Architecture and…" altkomsoftware.com/blog/camunda-8-vs-camunda-7-challenges (2025-01-10)
- Automation Atlas. "Camunda vs Zeebe 2026." automationatlas.io/guides/camunda-vs-zeebe-2026-comparison
- Medium. "Camunda 7 vs. Camunda 8: A Real-World Look at the Orchestration Shift." medium.com/@naziasultanaz_81855 (2025-11-08)
- Medium. "Decoding Camunda: JobWorkers in Camunda 8 and Service Tasks in Camunda 7." medium.com/@praveenbuya (2025-01-13)
- Tilson, J. "Workflows / BPMN." medium.com/@justintilson/workflows-bpmn-32a05c1f757a (2021-12-10)
- Wong, P. "A Process Semantics for BPMN." University of Oxford. www.cs.ox.ac.uk/people/peter.wong/pub/bpmnsem.pdf
- Dijkman, R.M., Dumas, M., Ouyang, C. "Semantics and analysis of business process models in BPMN." Information and Software Technology 50(12), 2008. doi:10.1016/j.infsof.2008.02.006
- Casciani, A. et al. "Formal semantics for knowledge representation and automated reasoning in BPMN process models." Information Systems 140, 2026. doi:10.1016/j.is.2026.102718
- Flows for APEX. "Boundary Events." flowsforapex.org/latest/boundary-events
- dev.to. "BPMN Compensation Events Explained." dev.to/nirankari/bpmn-compensation-events-explained-with-practical-workflow-examples-3nie (2026-03-10)
- gobpm. "BPMN compensation semantics." github.com/dr-dobermann/gobpm/blob/master/docs/bpmn-spec/semantics/compensation.md
- DeepWiki. "Zeebe Workflow Engine." deepwiki.com/camunda/camunda/2.1-zeebe-workflow-engine
- Sibling report: research/execution-engine-ui/reports/rq3-temporal.md (orchestration/worker split and state-ownership conflict, used for comparison)
- Sibling report: research/execution-engine-ui/reports/rq2-xstate.md (statechart/engine composition patterns)
