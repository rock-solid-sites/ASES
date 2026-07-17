# RQ3 — Burr (Retry)

## Question

Can Burr (Apache Burr, incubating — https://github.com/apache/burr) be used as execution
infrastructure for EDASES without imposing workflow semantics that conflict with EDASES
methodology? Specifically: does Burr's model of orchestration, state, and lifecycle overlap
or conflict with EDASES's intended separation (statecharts such as XState own per-artefact
lifecycles; the execution engine owns coordination only)?

This is a gap analysis, not a fit recommendation. The prior `rq3-burr.md` established the
core conflict (Burr's state machine overlaps XState's lifecycle role; Burr owns the state
model). This retry refines that analysis with (a) Apache incubation-status evidence, (b)
corporate-backing change (DAGWorks → Salesforce), (c) Burr's *not-yet-built* exception/retry
and state-validation capabilities, (d) in-process parallelism model, (e) fork/rewind
state capability, and (f) a cross-link to RQ4 (graph-structured artefacts vs. Burr's flat
`State`).

## Scope

**Investigated:**
- What Burr is (orchestration engine vs. execution engine) and its core execution model.
- Burr's semantic assumptions: graph-based workflows, LLM involvement, predefined action graph, state ownership.
- Conflict points between Burr's assumptions and EDASES's intended architecture.
- Reusable parts of Burr that could be adopted without adopting its full model.
- Composability with a separate statechart layer (XState).
- Ecosystem health (maintenance, community, backing, governance/incubation status).
- Burr's maturity gaps relevant to an execution engine (exception management, validation, parallelism).

**Excluded:**
- Hands-on code evaluation / running Burr against EDASES artefacts (no EDASES implementation exists yet).
- Deep API-by-API audit of every Burr integration.
- Performance/scale benchmarking.
- The question of whether EDASES *should* adopt Burr (this is a gap analysis, not a fit recommendation).

## Evidence

**E1 — Burr is a state-machine framework, not a distributed orchestration engine.**
Observation: The GitHub README states "With Apache Burr you express your application as a
state machine (i.e. a graph/flowchart)" and lists as core components "(1) A (dependency-free)
low-abstraction python library that enables you to build and manage state machines with simple
python functions." The comparison table explicitly marks Burr as "Asynchronous event-based
orchestration: ❌" while Temporal is "✅". Source: https://github.com/apache/burr,
https://burr.apache.org/docs/concepts/state-machine/.

**E2 — Burr was originally a stateful harness over Hamilton DAGs.**
Observation: The README states "Originally Apache Burr was built as a *harness* to handle state
between executions of Apache Hamilton DAGs (because DAGs don't have cycles), but realized that it
has a wide array of applications." Source: https://github.com/apache/burr. Interpretation: Burr's
fundamental job is to add stateful, potentially cyclic execution on top of acyclic computation graphs.

**E3 — Core model: actions, transitions, entrypoint, State.**
Observation: An Application requires (a) actions passed to `with_actions(...)`, (b) transitions
(with conditions), (c) an entry point. Actions "read from state and write to state" and declare
`reads=[...]` / `writes=[...]` dependencies. State is a Burr `State` object (a flat, dict-like
structure with `.update()` / `.append()`). Source:
https://burr.apache.org/docs/concepts/state-machine/, https://burr.apache.org/docs/concepts/actions/.

**E4 — LLM involvement is NOT required.**
Observation: The README example comment says "query the LLM however you want (or don't use an
LLM, up to you...)" and "Burr doesn't care how you use LLMs!" Non-LLM examples are listed
explicitly: time-series forecasting simulation, hyperparameter tuning, ML training. The comparison
table marks "Works with non-LLM use-cases: ✅". Source: https://github.com/apache/burr,
https://burr.apache.org/docs/concepts/state-machine/.

**E5 — Burr owns the state model.**
Observation: State is represented by Burr's own `State` class; actions declare which state keys
they read/write; persistence is keyed by `app_id` and `partition_key` and assumes JSON-serializable
state (customizable via a serde API). Source:
https://burr.apache.org/docs/concepts/state-persistence/.

**E6 — Built-in telemetry/tracking with a projects/applications/steps data model and a UI.**
Observation: The tracking system models "Projects" (top-level grouping), "Applications" (a trace,
shared state path across steps), and "Steps" (individual state-machine steps with input/state/result/timestamps).
A tracking server runs via `burr` (port 7241) and can be mounted inside a FastAPI app. The docs note
the tracking client "currently defaults to (and only supports) the `LocalTrackingClient`" writing to
`~/.burr`, with pluggability "in the future." Source: https://burr.apache.org/docs/concepts/tracking/.

**E7 — Pluggable state persistence.**
Observation: Burr provides a `StatePersister` API with pre-built persisters (e.g. `SQLLitePersister`)
and the ability to implement custom persisters for any database. Source:
https://burr.apache.org/docs/concepts/state-persistence/.

**E8 — Graph is separable from the application.**
Observation: A `GraphBuilder` lets you define the action graph separately from `ApplicationBuilder`,
so "you can run it in a web-server (create a graph once, application many times), import the graph
from another context, or run it in multiple contexts." Source:
https://burr.apache.org/docs/concepts/state-machine/.

**E9 — Execution is in-process, synchronous or async, step/iterate/run APIs.**
Observation: Execution APIs are `step`/`astep`, `iterate`/`aiterate`, `run`/`arun`, and
`stream_result`. These run inside the calling Python process. Source:
https://burr.apache.org/docs/concepts/state-machine/.

**E10 — Ecosystem health (GitHub stats).**
Observation (GitHub API, retrieved 2026-07-14): Apache incubating; 2,472 stars; 171 forks;
111 open issues; created 2024-01-29; last commit 2026-07-12; latest release `0.42.0-incubating`
(2026-05-10); Apache-2.0 license. PyPI `apache-burr` latest 0.42.0, requires Python >=3.9.
Corporate origin/backing: DAGWorks Inc. (the same org behind Apache Hamilton). Source:
https://api.github.com/repos/apache/burr, https://pypi.org/pypi/apache-burr/json.

**E11 — Positioning is AI/LLM-centric despite technical generality.**
Observation: The README lead is "makes it easy to develop applications that make decisions
(chatbots, agents, simulations, etc...)" and the example set is dominated by chatbots, RAG,
multi-agent collaboration, and adventure games; DAGWorks markets "Burr + Burr Cloud" for
"RAG + Agentic applications." Source: https://github.com/apache/burr, https://www.dagworks.io/.

**E12 — Apache incubation status and governance.**
Observation (Apache Incubator clutch page): Burr "Started: 2025-05-24; Last Status Update:
2025-12-19"; "Committers: 10"; "All Committers are PPMC members"; Mentors: Kevin Ratnasekera
(djkevincr), Ayush Saxena (ayushsaxena), PJ Fanning (fanningpj), Jarek Potiuk (potiuk). The
clutch description: "Burr is a lightweight in-process python framework that standardizes the
expression and execution of state machines as action-driven graphs, while making graph execution
easily observable. It is particularly suited for AI agent workflows, simulations, and other dynamic
systems, and comes with a self-hostable observability UI that integrates with OpenTelemetry."
Note: mentor Jarek Potiuk is the creator of Apache Airflow — relevant because Airflow is a
reference-point workflow-orchestration engine; his mentorship signals Apache's workflow/ML
community is engaged with Burr. Source: https://incubator.apache.org/clutch/burr.html,
https://incubator.apache.org/projects/burr.html.

**E13 — Corporate backing change: DAGWorks Inc. acquired by Salesforce.**
Observation: DAGWorks Inc.'s own about page states "DAGWorks Inc. has joined Salesforce." DAGWorks
is the original creator/steward of both Apache Hamilton and Apache Burr. Source:
https://www.dagworks.io/about. Interpretation (assumption): this changes the stewardship risk
profile — long-term direction now depends partly on Salesforce's priorities, though the code is
under ASF governance (E12). This is an assumption about future stewardship, not a documented fact
about Burr's roadmap.

**E14 — Exception management / retries are NOT yet built (roadmap only).**
Observation (Planned Capabilities): "Currently, exceptions will break the control flow of an
action, stopping the program early... We will be adding the ability to conditionally transition
based on exceptions, which will allow you to transition to an error-handling (or retry) action."
The documented API for error-based transitions (`error(APIException)`, `error(APIException, max=3)`)
is presented as "just some ideas" / "We will have to come up with ergonomic APIs." Source:
https://burr.apache.org/docs/concepts/planned-capabilities/. Interpretation: a production execution
engine typically needs first-class retry/error-handling; Burr does not yet provide it natively
(manual try/except inside actions is the current workaround).

**E15 — No compile-time / build-time state validation.**
Observation (Planned Capabilities): "We currently do not validate that the chain of actions provide
a valid state, although we plan to walk the graph to ensure that no 'impossible' situation is reached.
E.G. if an action reads from a state that is not written to (or not initialized), we will raise an
error, likely upon calling validate." Source:
https://burr.apache.org/docs/concepts/planned-capabilities/. Interpretation: Burr does not currently
guarantee that an action graph is internally consistent with respect to state; this is a gap for an
engine that must reliably coordinate artefact lifecycles.

**E16 — State immutability uses an inefficient copy mechanism (planned improvement).**
Observation (Planned Capabilities): "Currently state is immutable, but it utilizes an inefficient
copy mechanism. This is out of expedience... We will likely have: each state object be a node in a
linked list, with a pointer to the previous state." Source:
https://burr.apache.org/docs/concepts/planned-capabilities/. Interpretation: for an execution engine
processing large or numerous engineering artefacts, the current full-copy immutability model is a
documented performance liability (assumption — magnitude unmeasured).

**E17 — In-process parallelism via map-reduce style APIs.**
Observation (Parallelism concepts): Burr provides `MapStates` (same action over different states),
`MapActions` (different actions over same state), `MapActionsAndStates` (cartesian product), and
`RunnableGraph` (replace one action with a subgraph), plus a low-level API. "Under the hood it's all
treated as a 'sub-application'." All parallelism is in-process (no distributed scheduler). Source:
https://burr.apache.org/docs/concepts/parallelism/. Interpretation: Burr can fan out coordination
work in-process, but it is not a distributed task executor.

**E18 — Full self-comparison table.**
Observation (README comparison vs. Langgraph, Temporal, Langchain, Superagent, Hamilton):
Burr marks "Explicitly models a state machine: ✅", "Framework-agnostic: ✅", "Asynchronous
event-based orchestration: ❌", "Built for core web-service logic: ✅", "Open-source
user-interface for monitoring/tracing: ✅", "Works with non-LLM use-cases: ✅". Source:
https://github.com/apache/burr. Interpretation: Burr self-identifies as a state-machine runtime for
application logic, explicitly *not* an async/event orchestration engine.

**E19 — Fork / rewind state capability.**
Observation (State Persistence): Burr supports `fork_from_app_id` / `fork_from_partition_key` /
`fork_from_sequence_id` to "start from a previous application's state... useful if you want to fork
from a specific point in the application, rather than the latest state. This is especially useful for
debugging, or building an application that enables you to rewind state and make different choices."
Source: https://burr.apache.org/docs/concepts/state-persistence/. Interpretation: Burr has a
built-in replay/branch-from-history primitive, which is conceptually adjacent to EDASES artefact
recovery (RQ6) — but it operates on Burr's flat `State`, not on EDASES artefacts directly.

**E20 — Cross-link: Burr's flat `State` vs. EDASES graph-structured artefacts (RQ4).**
Observation: Burr `State` is a flat, dict-like key/value container (E3, E5). Separately, RQ4 of this
research programme evaluates graph databases (Kuzu, Memgraph, Neo4j, pgvector, SQLite) for storing
EDASES engineering artefacts, which are relationship-rich graph entities. Interpretation (assumption):
projecting EDASES artefacts — which RQ4 treats as graph nodes/edges — into Burr's flat `State` dict
is a structural mismatch; the engine's state abstraction would flatten artefact relationships that
EDASES intends to keep explicit. This compounds the F3 conflict from the prior report.

## Findings

**F1 — Burr is an in-process stateful execution library, not a workflow orchestration engine.**
Interpretation of E1, E2, E9, E18: For RQ3, Burr does not impose *distributed* workflow-orchestration
semantics (no durable task scheduling, no cross-process workflow engine, no event bus). It imposes
*state-machine* semantics on in-process execution. This is a meaningful distinction: the conflict
risk is not "heavyweight workflow engine semantics" but "Burr wants to be the state machine." Burr
itself disclaims async/event-based orchestration (E18).

**F2 — Burr's state machine would overlap with XState's intended lifecycle role.**
Interpretation of E3, E5: EDASES intends statecharts (XState) to own per-artefact lifecycles, while
the execution engine owns coordination only. Burr, by design, models the *entire* application as one
state machine whose transitions sequence actions and whose `State` holds the data. If Burr is adopted
as the execution engine, its state machine naturally becomes the lifecycle owner too — directly
competing with XState for the lifecycle role. This is the central conflict for RQ3 (carried from
prior report, unchanged).

**F3 — Burr owns the state model, not EDASES.**
Interpretation of E5, E20: Engineering artefacts would have to be projected into Burr's flat `State`
dict with `reads`/`writes` declarations and JSON-serializability assumptions. EDASES's artefact model
(RQ4: graph-structured) would be subordinate to Burr's state abstraction and would be flattened.
Whether this conflicts depends on whether EDASES is willing to let the engine own the state
representation (assumption — EDASES artefact model is not yet specified).

**F4 — LLM involvement is technically optional, reducing one anticipated conflict.**
Interpretation of E4: A common concern — "does it assume AI/LLM?" — is answered negatively at the
technical level. Burr does not require an LLM. However, see F6 for the residual risk.

**F5 — The action graph is predefined at build time.**
Interpretation of E3, E8: Transitions are declared statically when building the application/graph.
This is a graph-based, compile-time workflow assumption. If EDASES execution coordination requires
dynamically emergent or data-driven graphs, this is a potential conflict (assumption — EDASES
coordination dynamism is not yet specified).

**F6 — AI/LLM gravity is a softer, ecosystem-level conflict.**
Interpretation of E11, E12: Although Burr is technically non-LLM, its documentation, examples,
community, commercial offering (Burr Cloud for GenAI), and the Apache clutch description ("particularly
suited for AI agent workflows") are AI-centric. Adopting Burr may import AI-application assumptions and
priorities into EDASES tooling even without an LLM dependency.

**F7 — Reusable parts exist that are separable from the state-machine ownership claim.**
Interpretation of E6, E7, E8: The telemetry/tracking data model (projects/applications/steps) and UI,
the pluggable persistence API, and the separable `GraphBuilder` graph definition are potentially
usable as observability/persistence/graph-modeling infrastructure without ceding lifecycle
ownership to Burr. Caveat (E6): tracking is currently LocalTrackingClient-only, so the "pluggable"
telemetry claim is not yet fully realized — treat as partial. The fork/rewind primitive (E19) is also
a candidate reusable recovery primitive, conceptually adjacent to RQ6.

**F8 — Composition with XState is technically possible but creates dual state models.**
Interpretation of E3, E9: Because Burr actions are arbitrary Python, XState-driven lifecycle logic
could live inside a Burr action, with Burr handling only action sequencing (coordination). But this
yields two parallel state representations (Burr `State` + XState state) and two state machines. The
boundary must be disciplined so Burr's transitions do not also encode lifecycle. Feasible, but the
architectural tension (F2) remains.

**F9 — Burr lacks first-class execution-engine reliability primitives (retry/validation).**
Interpretation of E14, E15: A production execution engine coordinating artefact lifecycles would
normally expect native error/retry transitions and graph-level state validation. Burr currently has
neither — exceptions break control flow (manual try/except is the workaround) and there is no
build-time validation that actions' `reads`/`writes` are consistent. These are documented roadmap
items, not present capabilities. This is a maturity gap that bears directly on RQ3: adopting Burr
as execution infrastructure would mean either waiting for or building these primitives yourself.

**F10 — Burr's parallelism is in-process map-reduce, not distributed coordination.**
Interpretation of E17: Burr can fan out sub-applications in-process via `MapStates`/`MapActions`/
`RunnableGraph`, but there is no distributed scheduler or worker pool. If EDASES execution coordination
needs cross-process/multi-node execution, Burr alone does not provide it (assumption — EDASES
distribution requirements unspecified; see U1).

**F11 — Governance is healthy but stewardship is in transition.**
Interpretation of E10, E12, E13: Burr is actively maintained (last commit 2026-07-12, frequent
releases), under ASF incubation with 10 PPMC committers and strong mentors (including the Airflow
creator). However, the original corporate steward (DAGWorks) has been acquired by Salesforce (E13),
introducing a future-direction assumption. Incubation is not graduation — long-term ASF status is
not yet assured.

## Rejected options

- **Adopt Burr wholesale as both orchestrator and lifecycle owner.** Rejected as an answer to RQ3
  because it directly violates the EDASES separation premise (statecharts own lifecycle). This is a
  conflict finding, not a recommendation.
- **Treat Burr as a drop-in replacement for a distributed workflow engine (Temporal/Airflow class).**
  Rejected because E1/E9/E18 show Burr is in-process and explicitly not asynchronous event-based
  orchestration; it is the wrong category of tool for distributed coordination.
- **Assume Burr requires an LLM and therefore disqualify it on that basis.** Rejected because E4
  demonstrates LLM involvement is optional; disqualification on LLM grounds would be unfounded.
- **Assume Burr is production-ready as an execution engine on reliability grounds.** Rejected because
  E14/E15 show native retry/exception transitions and state validation are not yet built; readiness
  for lifecycle-coordination reliability is unproven.

## Unknowns

- **U1 — EDASES execution-coordination requirements are unspecified.** Whether EDASES needs dynamic
  graphs (vs. Burr's static build-time graph, F5), distributed execution (vs. Burr's in-process model,
  F10), or durable recovery is unknown; this determines how severe F5 and the in-process limitation
  (F1) are. (Assumption flagged.)
- **U2 — EDASES artefact/state model is unspecified.** The degree to which projecting artefacts into
  Burr's flat `State` (F3, E20) is acceptable, and whether the RQ4 graph model can coexist with it,
  is unknown.
- **U3 — Telemetry pluggability maturity.** E6 states only `LocalTrackingClient` is currently
  supported; the real cost of adapting Burr's tracking to EDASES observability is unknown.
- **U4 — Licensing/governance posture of Apache incubation.** Burr is "incubating"; incubation status
  and DAGWorks's continued stewardship (now under Salesforce, E13) could affect long-term stability
  (observed active as of 2026-07, but incubation is not graduation).
- **U5 — Timeline for Burr's reliability roadmap.** E14/E15 list retry/exception handling and state
  validation as planned but give no committed delivery date; whether they will land before any EDASES
  adoption decision is unknown.
- **U6 — Magnitude of the state-copy performance liability.** E16 documents an inefficient copy
  mechanism but gives no benchmark; the real cost for large/many artefacts is unmeasured.

## Confidence

**Medium.** The core conflict (F2: Burr's state machine overlaps XState's lifecycle role; F3: Burr
owns the state model, now reinforced by E20's graph-vs-flat mismatch) is well-supported by primary
documentation (E1–E5, E8, E20). The LLM-optional finding (F4) is firmly evidenced (E4). The
in-process / non-orchestration classification is firmly evidenced (E1, E9, E18). Confidence is capped
at Medium because: (a) the severity of several conflicts depends on EDASES requirements not yet
specified (U1, U2); (b) Burr's telemetry pluggability is not yet fully realized (U3, E6); (c) key
reliability primitives are roadmap-only (U5, E14, E15); and (d) the corporate-backing change (E13)
introduces a stewardship assumption (U4). The ecosystem-health picture is high-confidence (E10, E12).

## References

- Apache Burr GitHub repository (primary): https://github.com/apache/burr
- Apache Burr documentation — State Machine / Applications: https://burr.apache.org/docs/concepts/state-machine/
- Apache Burr documentation — Actions: https://burr.apache.org/docs/concepts/actions/
- Apache Burr documentation — State: https://burr.apache.org/docs/concepts/state/
- Apache Burr documentation — State Persistence: https://burr.apache.org/docs/concepts/state-persistence/
- Apache Burr documentation — Tracking/Telemetry: https://burr.apache.org/docs/concepts/tracking/
- Apache Burr documentation — Parallelism: https://burr.apache.org/docs/concepts/parallelism/
- Apache Burr documentation — Planned Capabilities: https://burr.apache.org/docs/concepts/planned-capabilities/
- Apache Incubator — Burr clutch page: https://incubator.apache.org/clutch/burr.html
- Apache Incubator — Burr project status: https://incubator.apache.org/projects/burr.html
- Apache Incubator — Burr proposal (history/stats): https://cwiki.apache.org/confluence/display/INCUBATOR/BurrProposal
- Burr introductory blog post (DAGWorks): https://blog.dagworks.io/p/burr-develop-stateful-ai-applications
- DAGWorks product page: https://www.dagworks.io/
- DAGWorks "joined Salesforce" notice: https://www.dagworks.io/about
- GitHub API repo stats (stars/forks/issues/license/dates), retrieved 2026-07-14: https://api.github.com/repos/apache/burr
- PyPI project metadata: https://pypi.org/pypi/apache-burr/json
- Prior report (this retry refines it): research/execution-engine-ui/reports/rq3-burr.md
