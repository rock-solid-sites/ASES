# RQ3 — Burr

## Question

Can Burr (Apache Burr, incubating — https://github.com/apache/burr) be used as execution
infrastructure for EDASES without imposing workflow semantics that conflict with EDASES
methodology? Specifically: does Burr's model of orchestration, state, and lifecycle overlap
or conflict with EDASES's intended separation (statecharts such as XState own per-artefact
lifecycles; the execution engine owns coordination only)?

## Scope

**Investigated:**
- What Burr is (orchestration engine vs. execution engine) and its core execution model.
- Burr's semantic assumptions: graph-based workflows, LLM involvement, predefined action graph, state ownership.
- Conflict points between Burr's assumptions and EDASES's intended architecture.
- Reusable parts of Burr that could be adopted without adopting its full model.
- Composability with a separate statechart layer (XState).
- Ecosystem health (maintenance, community, backing).

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

**E10 — Ecosystem health.**
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

## Findings

**F1 — Burr is an in-process stateful execution library, not a workflow orchestration engine.**
Interpretation of E1, E2, E9: For RQ3, Burr does not impose *distributed* workflow-orchestration
semantics (no durable task scheduling, no cross-process workflow engine, no event bus). It imposes
*state-machine* semantics on in-process execution. This is a meaningful distinction: the conflict
risk is not "heavyweight workflow engine semantics" but "Burr wants to be the state machine."

**F2 — Burr's state machine would overlap with XState's intended lifecycle role.**
Interpretation of E3, E5: EDASES intends statecharts (XState) to own per-artefact lifecycles, while
the execution engine owns coordination only. Burr, by design, models the *entire* application as one
state machine whose transitions sequence actions and whose `State` holds the data. If Burr is adopted
as the execution engine, its state machine naturally becomes the lifecycle owner too — directly
competing with XState for the lifecycle role. This is the central conflict for RQ3.

**F3 — Burr owns the state model, not EDASES.**
Interpretation of E5: Engineering artefacts would have to be projected into Burr's flat `State`
dict with `reads`/`writes` declarations and JSON-serializability assumptions. EDASES's artefact
model would be subordinate to Burr's state abstraction. Whether this conflicts depends on whether
EDASES is willing to let the engine own the state representation (assumption — EDASES artefact
model is not yet specified).

**F4 — LLM involvement is technically optional, reducing one anticipated conflict.**
Interpretation of E4: A common concern — "does it assume AI/LLM?" — is answered negatively at the
technical level. Burr does not require an LLM. However, see F6 for the residual risk.

**F5 — The action graph is predefined at build time.**
Interpretation of E3, E8: Transitions are declared statically when building the application/graph.
This is a graph-based, compile-time workflow assumption. If EDASES execution coordination requires
dynamically emergent or data-driven graphs, this is a potential conflict (assumption — EDASES
coordination dynamism is not yet specified).

**F6 — AI/LLM gravity is a softer, ecosystem-level conflict.**
Interpretation of E11: Although Burr is technically non-LLM, its documentation, examples, community,
and commercial offering (Burr Cloud for GenAI) are AI-centric. Adopting Burr may import
AI-application assumptions and priorities into EDASES tooling even without an LLM dependency.

**F7 — Reusable parts exist that are separable from the state-machine ownership claim.**
Interpretation of E6, E7, E8: The telemetry/tracking data model (projects/applications/steps) and UI,
the pluggable persistence API, and the separable `GraphBuilder` graph definition are potentially
usable as observability/persistence/graph-modeling infrastructure without ceding lifecycle
ownership to Burr. Caveat (E6): tracking is currently LocalTrackingClient-only, so the "pluggable"
telemetry claim is not yet fully realized — treat as partial.

**F8 — Composition with XState is technically possible but creates dual state models.**
Interpretation of E3, E9: Because Burr actions are arbitrary Python, XState-driven lifecycle logic
could live inside a Burr action, with Burr handling only action sequencing (coordination). But this
yields two parallel state representations (Burr `State` + XState state) and two state machines. The
boundary must be disciplined so Burr's transitions do not also encode lifecycle. Feasible, but the
architectural tension (F2) remains.

## Rejected options

- **Adopt Burr wholesale as both orchestrator and lifecycle owner.** Rejected as an answer to RQ3
  because it directly violates the EDASES separation premise (statecharts own lifecycle). This is a
  conflict finding, not a recommendation.
- **Treat Burr as a drop-in replacement for a distributed workflow engine (Temporal/Airflow class).**
  Rejected because E1/E9 show Burr is in-process and explicitly not asynchronous event-based
  orchestration; it is the wrong category of tool for distributed coordination.
- **Assume Burr requires an LLM and therefore disqualify it on that basis.** Rejected because E4
  demonstrates LLM involvement is optional; disqualification on LLM grounds would be unfounded.

## Unknowns

- **U1 — EDASES execution-coordination requirements are unspecified.** Whether EDASES needs dynamic
  graphs (vs. Burr's static build-time graph), distributed execution, or durable recovery is unknown;
  this determines how severe F5 and the in-process limitation (F1) are. (Assumption flagged.)
- **U2 — EDASES artefact/state model is unspecified.** The degree to which projecting artefacts into
  Burr's `State` (F3) is acceptable is unknown.
- **U3 — Telemetry pluggability maturity.** E6 states only `LocalTrackingClient` is currently
  supported; the real cost of adapting Burr's tracking to EDASES observability is unknown.
- **U4 — Licensing/governance posture of Apache incubation.** Burr is "incubating"; incubation status
  and DAGWorks's continued stewardship could affect long-term stability (observed active as of
  2026-07, but incubation is not graduation).

## Confidence

**Medium.** The core conflict (F2: Burr's state machine overlaps XState's lifecycle role; F3: Burr
owns the state model) is well-supported by primary documentation (E1–E5, E8). The LLM-optional
finding (F4) is firmly evidenced (E4). Confidence is capped at Medium because the severity of several
conflicts depends on EDASES requirements that are not yet specified (U1, U2), and because Burr's
telemetry pluggability is not yet fully realized (U3, E6). The ecosystem-health picture is
high-confidence (E10).

## References

- Apache Burr GitHub repository (primary): https://github.com/apache/burr
- Apache Burr documentation — State Machine / Applications: https://burr.apache.org/docs/concepts/state-machine/
- Apache Burr documentation — Actions: https://burr.apache.org/docs/concepts/actions/
- Apache Burr documentation — State Persistence: https://burr.apache.org/docs/concepts/state-persistence/
- Apache Burr documentation — Tracking/Telemetry: https://burr.apache.org/docs/concepts/tracking/
- Burr introductory blog post (DAGWorks): https://blog.dagworks.io/p/burr-develop-stateful-ai-applications
- DAGWorks product page: https://www.dagworks.io/
- GitHub API repo stats (stars/forks/issues/license/dates), retrieved 2026-07-14: https://api.github.com/repos/apache/burr
- PyPI project metadata: https://pypi.org/pypi/apache-burr/json
