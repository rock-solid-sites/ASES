# RQ3 — LangGraph

## Question

Can an existing workflow engine — specifically **LangGraph** (https://langchain-ai.github.io/langgraph/), a framework for building stateful, multi-actor applications with LLMs, built on LangChain — be used as execution infrastructure for EDASES without imposing workflow semantics that conflict with EDASES methodology?

The EDASES framing is: the execution engine coordinates execution; per-artefact lifecycles are owned by statecharts (e.g. XState); the workflow engine must not impose lifecycle-management or other semantics that conflict with EDASES. This report is a **gap analysis**, not a fit recommendation: it identifies conflicts and reusable parts.

## Scope

**Investigated:**
- Whether LangGraph is an orchestration engine or an execution engine, and what it assumes
- Whether LangGraph assumes graph-based workflows, LLM involvement, or a predefined/compiled graph structure
- Which of LangGraph's core assumptions would conflict with EDASES (state-model ownership, graph semantics, agent/LLM framing, language/ecosystem coupling, persistence-format stability)
- Which parts of LangGraph could be reused without adopting its full model (Pregel runtime, checkpointer/persistence, channel/reducer state model, human-in-the-loop)
- Whether LangGraph can compose with a separate statechart layer (XState) or assumes it owns both orchestration and lifecycle

**Excluded:**
- Hands-on code execution or benchmarking (this is a literature/evidence review; no LangGraph code was run)
- The LangGraph Platform / LangSmith / Agent Server managed deployment product (only the open-source `langgraph` library and its runtime are in scope)
- The Functional API (`@entrypoint`) depth beyond what is needed to characterise the runtime
- Other LangChain-incumbent engines (Temporal, Airflow, Step Functions) — covered by sibling reports
- Quantitative throughput/latency of the Pregel runtime at scale (no benchmark located in this review)

## Evidence

### 1. Orchestration vs execution engine
- **Observation:** The official overview states LangGraph is "a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents" and is "focused entirely on agent **orchestration**" (docs.langchain.com/oss/python/langgraph/overview).
- **Observation:** The same overview states "LangGraph provides low-level supporting infrastructure for *any* long-running, stateful workflow or agent" and lists its central benefits as persistence, human-in-the-loop, memory, debugging, and deployment (docs.langchain.com/oss/python/langgraph/overview).
- **Observation:** The runtime is the `Pregel` engine: "Compiling a StateGraph … produces a `Pregel` instance that can be invoked with input." `Pregel` "implements LangGraph's runtime, managing the execution of LangGraph applications" (docs.langchain.com/oss/python/langgraph/pregel).
- **Observation:** LangGraph is built by LangChain Inc and is positioned throughout as an "agent runtime" / "agent orchestration" product; its sibling products (LangSmith, Agent Server, Deep Agents) are all agent-oriented (docs.langchain.com/oss/python/langgraph/overview; blog.langchain.com/building-langgraph).
- **Interpretation:** LangGraph is both an orchestration *framework* and a *runtime* (the Pregel engine), but it is explicitly scoped to "agent orchestration" and "long-running, stateful agents/workflows." It is not a general-purpose execution engine for arbitrary engineering artefacts. Its execution model is real, but its conceptual centre of gravity is AI-agent orchestration. Confidence: **High** for the "orchestration, agent-scoped" characterisation; the boundary between "orchestration" and "execution engine" is a matter of framing — LangGraph does execute, but it executes *graphs of agent steps*.

### 2. Semantic assumptions
- **Observation (graph-based):** "At its core, LangGraph models agent workflows as graphs" composed of `State`, `Nodes`, and `Edges` (docs.langchain.com/oss/python/langgraph/graph-api). The runtime is a message-passing / Bulk-Synchronous-Parallel (BSP) "super-step" engine inspired by Google's Pregel (docs.langchain.com/oss/python/langgraph/graph-api; docs.langchain.com/oss/python/langgraph/pregel).
- **Observation (LLM not required):** The Graph API overview explicitly states: "To emphasize: `Nodes` and `Edges` are nothing more than functions—they can contain an LLM or just good ol' code." (docs.langchain.com/oss/python/langgraph/graph-api). The overview also states "you don't need to use LangChain to use LangGraph" (docs.langchain.com/oss/python/langgraph/overview).
- **Observation (predefined/compiled graph):** "You **MUST** compile your graph before you can use it." Compilation performs structural checks and is where checkpointers/breakpoints are attached; `graph.compile()` returns a `CompiledStateGraph` (a `Pregel` instance) (docs.langchain.com/oss/python/langgraph/graph-api). The graph topology (nodes/edges) is therefore fixed at build time; only *routing* is dynamic via conditional edges / `Command` / `Send` (docs.langchain.com/oss/python/langgraph/graph-api).
- **Observation (single shared state schema):** The graph `State` is "a shared data structure that represents the current snapshot of your application," typically a `TypedDict` or Pydantic model, with per-key reducer functions. All nodes read/write the same state channels (docs.langchain.com/oss/python/langgraph/graph-api). Private channels exist but live *inside the same graph's* state (docs.langchain.com/oss/python/langgraph/graph-api).
- **Interpretation:** LangGraph does **not** assume LLM involvement in every step — nodes can be plain code. But it **does** assume (a) a graph structure, (b) a single shared, typed, reducer-driven state schema per run ("thread"), and (c) a graph that is defined and compiled before execution. These are hard structural assumptions, not optional conventions. Confidence: **High**.

### 3. State-model ownership and persistence
- **Observation:** LangGraph's persistence is "state checkpointing": a checkpoint is "a snapshot of the graph state at a given point in time," organised into `thread_id`s; savers include `InMemorySaver`, `SqliteSaver`, `AsyncSqliteSaver`, `PostgresSaver`, `AsyncPostgresSaver` (reference.langchain.com/python/langgraph/checkpoints; docs.langchain.com/oss/python/langgraph/persistence).
- **Observation:** Checkpoints are taken at super-step boundaries, not mid-node; on resume the affected node re-runs from the start, so node logic "should be idempotent" (docs.langchain.com/oss/python/langgraph/graph-api). A separate `Store` persists cross-thread long-term memory (docs.langchain.com/oss/python/langgraph/persistence).
- **Observation (format-stability caveat):** The `DeltaChannel` docs warn that "Rolling back to a version without `DeltaChannel` support is not supported … earlier versions cannot read [the new] checkpoints," and provide a migration script (docs.langchain.com/oss/python/langgraph/pregel). This shows the persisted checkpoint format is version-sensitive and not a guaranteed-stable public contract.
- **Observation (graph migrations):** LangGraph supports topology changes for finished threads, limited changes for interrupted threads, and add/remove of state keys with backward/forward compatibility — but renaming a state key "loses their saved state in existing threads" (docs.langchain.com/oss/python/langgraph/graph-api).
- **Interpretation:** LangGraph assumes it **owns** the durable state model: the checkpoint *is* the workflow state, and persistence is tied to LangGraph's own format and runtime. For EDASES, per-artefact lifecycle state is meant to be owned by XState actors; if LangGraph also checkpoints a single shared graph state, two state models coexist and LangGraph's checkpoint becomes the de-facto source of truth for workflow progress. Confidence: **High** for the ownership assumption; **Medium** for how painful the dual-model coexistence would be in practice (inferred, not measured).

### 4. Agent/LLM-centric framing
- **Observation:** Terminology throughout is agent-oriented: "agents," "tools," "messages," "human-in-the-loop," "multi-agent handoffs," "chat model interface" (docs.langchain.com/oss/python/langgraph/graph-api; docs.langchain.com/oss/python/langgraph/overview). `MessagesState` and the `add_messages` reducer exist specifically for LLM chat history (docs.langchain.com/oss/python/langgraph/graph-api).
- **Observation:** Human-in-the-loop is a first-class, built-in primitive via `interrupt()` and `Command(resume=...)` (docs.langchain.com/oss/python/langgraph/graph-api; docs.langchain.com/oss/python/langgraph/interrupts).
- **Interpretation:** Even though nodes can be plain code, adopting LangGraph imports an "agent orchestration" worldview (messages, tools, human approval gates, streaming token-by-token). This framing may sit awkwardly with EDASES methodology, which frames the engine around engineering-artefact lifecycles rather than agent reasoning loops. Confidence: **Medium** — the framing is evident from the docs, but whether it *conflicts* with EDASES methodology is a methodological judgement, not a technical fact.

### 5. Language / ecosystem coupling
- **Observation:** LangGraph is a Python library (with a JS/TS port, `@langchain/langgraph`); nodes implement LangChain's `Runnable` interface; state schemas commonly use Pydantic; the runtime depends on `langgraph-checkpoint*` packages (docs.langchain.com/oss/python/langgraph/pregel; reference.langchain.com/python/langgraph/checkpoints).
- **Interpretation:** LangGraph is coupled to the Python/LangChain ecosystem. EDASES methodology is meant to be tool- and language-independent (per AGENTS.md "Tool Independence"). Using LangGraph as *the* execution infrastructure would import a language/ecosystem dependency that the methodology explicitly seeks to avoid at the conceptual layer. Confidence: **Medium** — factual that it is Python/LangChain-coupled; the conflict with EDASES tool-independence is an interpretation.

### 6. Reusable parts (decoupled from the agent model)
- **Observation:** The `Pregel` runtime can be used *directly* (not only via `StateGraph`): the docs show `Pregel(nodes=..., channels=..., input_channels=..., output_channels=...)` with `NodeBuilder().subscribe_only(...).do(...).write_to(...)` (docs.langchain.com/oss/python/langgraph/pregel). This is a general BSP execution engine (actors + channels), independent of LLM concepts.
- **Observation:** The channel abstractions (`LastValue`, `Topic`, `BinaryOperatorAggregate`, `DeltaChannel`) are general-purpose state primitives with reducer/update functions, not LLM-specific (docs.langchain.com/oss/python/langgraph/pregel).
- **Observation:** The `Checkpointer` interface and saver implementations provide durable execution / resume / time-travel that are, in principle, separable from graph topology (reference.langchain.com/python/langgraph/checkpoints).
- **Interpretation:** The genuinely reusable substrate is the Pregel BSP runtime + channel/reducer state model + checkpointer persistence. These are general and could back a durable execution layer. However, they are delivered inside the LangChain ecosystem (Runnable, Pydantic, `langgraph-checkpoint*`) and are documented/optimised for agent graphs, so extracting them cleanly would mean depending on LangGraph internals rather than a standalone library. Confidence: **Medium** — the parts exist and are general, but their standalone reusability without the agent framing is inferred from the API surface, not from a documented "use Pregel without agents" path beyond the low-level examples.

### 7. Composition with a separate statechart layer (XState)
- **Observation:** A LangGraph node is "nothing more than [a] function" that receives state and returns an update (docs.langchain.com/oss/python/langgraph/graph-api). A node can therefore call arbitrary code, including creating/driving an XState actor.
- **Observation:** LangGraph supports subgraphs and `Command(graph=Command.PARENT)` for parent/subgraph navigation (docs.langchain.com/oss/python/langgraph/graph-api).
- **Interpretation:** LangGraph *could* orchestrate while XState owns per-artefact lifecycles: a LangGraph node would invoke/drive an XState actor as a side-effecting step. But LangGraph would still own (a) the orchestration graph, (b) its own checkpointed workflow state, and (c) the human-in-the-loop/streaming layer. The XState actor would be a child of a LangGraph node, not a peer. Two state models would coexist (LangGraph checkpoint vs XState snapshot). If instead one LangGraph *thread* is used per artefact, LangGraph's graph would itself encode the artefact lifecycle — directly competing with XState's intended role. No evidence was found of a native "LangGraph + XState" integration; composition is inferred from LangGraph's ability to call arbitrary functions. Confidence: **Medium** — technical feasibility is plausible from the API, but the integration pattern is inferred, not documented, and the dual-state-model tension is a real conflict rather than a clean composition.

## Findings

1. **Orchestration, agent-scoped.** LangGraph is an orchestration framework + Pregel runtime explicitly built for "long-running, stateful agents." It executes, but it executes *agent-step graphs*. It is not a neutral, general execution engine. (Evidence §1)
2. **LLM not required, but graph + shared-state + compile are.** Nodes can be plain code, and LangChain is optional. However LangGraph hard-assumes a graph structure, a single shared typed/reducer state schema per thread, and a graph compiled before use. (Evidence §2)
3. **LangGraph owns the durable state model.** Checkpointing is the workflow state, tied to LangGraph's own (version-sensitive) format. This conflicts with EDASES placing per-artefact lifecycle state in XState. (Evidence §3)
4. **Agent/LLM framing is pervasive.** Messages, tools, human-in-the-loop, streaming, multi-agent handoffs are first-class. This imports an "agent orchestration" worldview that may conflict with EDASES's artefact-lifecycle framing. (Evidence §4)
5. **Language/ecosystem coupling.** Python/LangChain-coupled (Runnable, Pydantic, `langgraph-checkpoint*`), which conflicts with EDASES tool-independence at the conceptual layer. (Evidence §5)
6. **Reusable substrate exists but is entangled.** The Pregel BSP runtime, channel/reducer state primitives, and checkpointer persistence are general and could back a durable execution layer — but they ship inside the LangChain ecosystem and are optimised for agent graphs. (Evidence §6)
7. **Composition with XState is possible but awkward.** A node can drive an XState actor, but LangGraph still owns orchestration + its own checkpointed state, producing a dual state model; per-artefact-thread use would make LangGraph compete with XState for the lifecycle role. (Evidence §7)

**Overall read on RQ3:** LangGraph *can* execute workflows without requiring LLMs, so it is not disqualified on the "AI in every step" axis. But its core assumptions — graph structure, single shared compiled state schema, ownership of durable checkpoint state, agent/LLM framing, and Python/LangChain coupling — are semantic impositions that would conflict with EDASES's intended division of labour (statecharts own lifecycles; the engine only coordinates). The reusable parts (Pregel runtime, checkpointer, channel/reducer model) are real but entangled with the agent model, so adopting them means adopting the framework. The principal conflict is **state-model ownership**: LangGraph wants to be the source of truth for workflow progress, which overlaps the role EDASES reserves for statecharts.

## Rejected options

- **Treating LangGraph as LLM-mandatory.** Rejected: the Graph API overview explicitly says nodes "can contain an LLM or just good ol' code," and LangChain is optional. The conflict is not "it forces AI," it is structural/orchestration assumptions.
- **Treating LangGraph as a general-purpose execution engine.** Rejected: the docs scope it to "agent orchestration" and "long-running, stateful agents/workflows"; its runtime, persistence, and terminology are agent-centred.
- **Assuming LangGraph's checkpoint format is a stable public contract.** Rejected: the `DeltaChannel` docs explicitly warn that downgrading LangGraph leaves newer checkpoints unreadable; format stability is not guaranteed.
- **Assuming a clean "LangGraph orchestrates, XState owns lifecycle" composition exists.** Rejected: no native integration was found; composition is inferred from arbitrary-function nodes, and it produces a dual state model / potential role overlap.
- **Assuming the Pregel runtime is cleanly separable as a standalone library.** Rejected: it is usable directly, but it is delivered inside the LangChain ecosystem (Runnable, Pydantic, `langgraph-checkpoint*`) and documented for agent graphs; standalone reuse would mean depending on LangGraph internals.

## Unknowns

- **Cost/awkwardness of the dual state model in practice** — LangGraph checkpoint vs XState snapshot coexistence is inferred to be tension-prone, but no concrete integration was located to confirm how bad it is.
- **Whether a LangGraph node driving an XState actor is performant/clean at scale** — no benchmark or reference implementation found.
- **Stability of the persisted checkpoint format across LangGraph major versions** — only a `DeltaChannel`-specific warning was found; general format-stability guarantees were not located.
- **Behaviour of the Pregel runtime outside agent graphs** — the low-level API exists, but all documented optimisations (streaming, tracing, human-in-the-loop) assume the agent model.
- **Whether EDASES's engineering-artefact workflows map onto a single compiled graph at all** — this is a methodological question about EDASES, not LangGraph; left as an open unknown rather than assumed.
- **Exact boundary between "orchestration" and "execution engine" for EDASES's purposes** — LangGraph blurs it (it executes graphs), so the conflict may be one of framing as much as mechanism.

## Confidence

**Medium.**

Justification: The *technical* findings are well-supported by official LangGraph documentation (overview, Graph API, Pregel runtime, checkpoints/persistence, interrupts) and the LangChain "Building LangGraph" engineering blog — LangGraph's graph assumption, shared-state schema, compile-before-use requirement, checkpoint ownership, and agent framing are all directly evidenced. Confidence is **High** for those.

Confidence is **Medium** rather than High because the *conflict* claims are partly interpretive: whether LangGraph's assumptions "conflict with EDASES methodology" depends on EDASES's own (not fully specified here) division of labour, and the dual-state-model tension / XState composition is inferred from API capability rather than a documented integration. The reusable-parts assessment is also Medium because standalone reuse of Pregel/checkpointer is API-plausible but not a documented, supported path. RQ3 is answered with reasonable confidence: LangGraph imposes graph + shared-state + checkpoint-ownership + agent-framing semantics that conflict with EDASES's intended engine/statechart separation, while its execution substrate is reusable only by adopting the framework.

## References

- LangGraph overview (orchestration framework/runtime, "any long-running stateful workflow or agent," LangChain optional) — https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph Graph API (State/Nodes/Edges, "functions—LLM or just good ol' code," compile required, reducers, private channels, Send/Command, graph migrations) — https://docs.langchain.com/oss/python/langgraph/graph-api
- LangGraph runtime / Pregel (BSP, actors + channels, direct Pregel usage, channel types, DeltaChannel format warning) — https://docs.langchain.com/oss/python/langgraph/pregel
- LangGraph checkpoints / persistence (checkpoint = graph-state snapshot, thread_id, saver implementations, Store for cross-thread memory) — https://reference.langchain.com/python/langgraph/checkpoints ; https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph interrupts / human-in-the-loop (interrupt(), Command(resume=...)) — https://docs.langchain.com/oss/python/langgraph/interrupts
- Building LangGraph: Designing an Agent Runtime from first principles (6 features, BSP execution, structured agents) — https://blog.langchain.com/building-langgraph/ (also https://www.langchain.com/blog/building-langgraph)
- LangGraph overview (LangChain product ecosystem: LangSmith, Agent Server, Deep Agents) — https://docs.langchain.com/oss/python/langgraph/overview
- Third-party characterisation of LangGraph as "stateful AI agent orchestration framework," Pregel/Beam-inspired, checkpointing/streaming/human-in-the-loop — https://pyshine.com/LangGraph-Stateful-AI-Agent-Orchestration-Framework/ ; https://nerova.ai/guides/what-is-langgraph-stateful-ai-agent-orchestration-2026
- Third-party production-architecture account (state persistence mandatory, stateless executors, Redis/Postgres backends) — https://markaicode.com/architecture/langgraph-production-architecture/
- Third-party state-management write-up (shared global state, reducers, checkpointers, concurrency via super-steps) — https://medium.com/@bharatraj1918/langgraph-state-management-part-1-how-langgraph-manages-state-for-multi-agent-workflows-da64d352c43b
- Go-native port inspired by LangGraph (confirms "graph-based workflow approach for LLM applications" lineage) — https://github.com/dshills/langgraph-go
