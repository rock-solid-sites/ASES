# RQ2 — XState/Stately

## Question

Can hierarchical statechart frameworks model independent artefact lifecycles? This report investigates **XState** (https://xstate.js.org, the statechart/state-machine library) and **Stately** (https://stately.ai, the visual editor/platform built around it) as a candidate against that question — specifically whether each artefact can carry its own independent lifecycle, and how inspection, versioning, visualization, persistence, hierarchy, and composition behave.

## Scope

**Investigated:**
- Independent lifecycle per artefact (one machine definition, many instances; modelling ~5000 artefacts; memory/overhead)
- Runtime state inspection (current-state read, debugging/visualization tooling)
- Versionable definitions (versioning machine definitions; running v1 and v2 simultaneously; changing a definition while instances run)
- Visual tooling (Stately Studio editor; import/export; usefulness for non-programmers)
- Persistence (serialization, format, restore, database)
- Hierarchy (nested, parallel, history states)
- Composition (does XState own the full app lifecycle, or compose with a separate graph/workflow layer?)
- Whether XState v5 ("Glacier") materially changes any of the above

**Excluded:**
- Hands-on benchmarking or code execution (this is a literature/evidence review; no XState code was run)
- Quantitative memory profiling at 5000 instances (no official benchmark located)
- Stately paid-tier feature depth beyond what is needed to answer RQ2 (e.g. Stately Sky deploy, team billing)
- The `@xstate/store` package except where it informs persistence/versioning
- Other statechart frameworks (SCXML engines, Sismic, etc.) — covered by sibling reports

## Evidence

### 1. Independent lifecycle per artefact
- **Observation:** XState v5 is explicitly "actor-based." A *machine* is a declarative behaviour definition; it does not run by itself. A running instance is an *actor*, created with `createActor(machine)` (XState v5 blog, stately.ai/blog/2023-12-01-xstate-v5; stately.ai/docs/xstate). Each actor has its own internal, encapsulated state, a mailbox, and an independent lifecycle (start/stop) (stately.ai/docs/actors).
- **Observation:** The README quick-start shows `const toggleActor = createActor(toggleMachine); toggleActor.start();` — one definition, one instance (github.com/statelyai/xstate README).
- **Observation:** In the actor model, "actors communicate with other actors by sending and receiving events asynchronously… Internal actor state is not shared between actors" (stately.ai/docs/actors). This is the mechanism by which 5000 artefacts each get an isolated lifecycle: 5000 actors, each from the same machine definition.
- **Observation:** A GitHub discussion (statelyai/xstate #3775) asks how XState scales with ~1000 WebSocket clients each holding its own machine instance, but the captured thread contains only the question — no authoritative answer or benchmark was found in this review.
- **Observation:** Context (the per-instance data bag) "must be JSON-serializable" for persistence; functions/classes cannot be persisted (stately.ai/docs/persistence caveats). This bounds what an artefact's per-instance state may contain.
- **Interpretation:** Each artefact maps naturally to one actor instance of a shared machine definition. The machine definition is compiled once and shared; per-instance cost is the snapshot (state value + context) plus a mailbox. No evidence was found that XState imposes a per-instance ceiling. **Assumption:** 5000 lightweight actors are feasible in a single Node process, but the precise memory/CPU cost is undocumented — treat as unverified.

### 2. Runtime state inspection
- **Observation:** `actor.getSnapshot()` returns the current observable state: `state.value` (the active state, possibly nested), `state.context`, `state.status`, and methods such as `state.matches('green')` (stately.ai/docs/xstate; stately.ai/blog/2023-12-01-xstate-v5). State can be read at any time from a running actor.
- **Observation:** XState v5 introduces an **Inspect API**: `createActor(machine, { inspect: (inspectionEvent) => {...} })` emits `@xstate.actor` (lifecycle), `@xstate.snapshot` (snapshot updates), and `@xstate.event` (event communication) for every actor in the system (stately.ai/blog/2023-12-01-xstate-v5). This gives granular, programmatic visibility into all actors and their communication.
- **Observation:** Third-party **XState DevTools** (Chrome extension, MIT) inspects v5 machines at runtime — browser and Node — with an actor list (parent→child hierarchy), active-state highlighting, context JSON viewer, event log with click-to-time-travel, and a server-side WebSocket bridge (github.com/mjbeswick/xstate-devtools; chrome web store listing).
- **Observation:** The **Stately VS Code extension** (91k+ installs) provides visual editing, autocomplete, typegen, and linting, and can open any machine in a visual editor (marketplace.visualstudio.com/items/statelyai.stately-vscode).
- **Observation:** **XState Viz** exists as a legacy visualizer; Stately Studio's editor is the current replacement (stately.ai/viz).
- **Interpretation:** Runtime inspection is first-class: current state is readable synchronously via `getSnapshot()`, and the Inspect API + DevTools + Studio provide visualization, time-travel, and event tracing. Confidence: **High** for capability; the precise overhead of always-on inspection is not quantified here.

### 3. Versionable definitions
- **Observation:** A machine definition is ordinary JavaScript/TypeScript configuration (a `createMachine({...})` object). It is versionable like any code artifact (git, packages, Stately Studio versions).
- **Observation:** Running v1 and v2 simultaneously is straightforward: create actors from two different machine definitions — `createActor(machineV1)` for old artefacts, `createActor(machineV2)` for new ones. The actor captures its logic at creation; existing instances are unaffected by a later definition change.
- **Observation:** Stately Studio's REST API can "fetch a specific version of a machine" and export machines in multiple formats (stately.ai/docs/studio-api; stately.ai/docs/export-as-code). Machine versions are a first-class Studio concept.
- **Observation:** XState v4 and v5 can be installed **side-by-side** via npm aliases (`xstate` + `xstate5: npm:xstate@5`, `@xstate/react` + `@xstate/react5`) for incremental migration (stately.ai/blog/2024-02-02-migrating-machines-to-xstate-v5).
- **Observation (caveat):** The persistence docs warn: "if the machine or actor logic changes, the restored state may be incompatible with the new logic" (stately.ai/docs/persistence caveats). So changing a definition while instances are persisted/restored is safe for *running* in-memory actors but risky for *persisted* snapshots tied to the old shape.
- **Observation:** A third-party library `xstate-migrate` exists to generate and apply migration patches between machine versions for persisted snapshots (add/remove context properties, handle nested/parallel states) (npmjs.com/package/xstate-migrate). `@xstate/store/persist` supports a `version` + `migrate` callback (stately.ai/docs/xstate-store/persist).
- **Interpretation:** Definitions are versionable and multiple versions coexist trivially at runtime (different actors from different definitions). The only hazard is persisted-snapshot compatibility across a definition change, which is a known, mitigable problem (migrate-on-load). Confidence: **High** for runtime coexistence; **Medium** for persisted-snapshot migration (relies on manual migration or third-party tooling, not a built-in guarantee).

### 4. Visual tooling
- **Observation:** **Stately Studio** is "a visual software modeling platform for modeling your app & business logic as state machines/statecharts and actors" with a drag-and-drop editor in **Design** and **Simulate** modes; "no code required" (stately.ai/docs/studio; stately.ai/docs).
- **Observation:** Studio supports collaborative shared projects/teams, and **Stately AI** can generate/edit machines in XState v5 code (github.com/statelyai/xstate README; stately.ai/blog/2023-12-01-xstate-v5).
- **Observation:** **Import from code**: Studio imports existing machines from JavaScript/TypeScript `createMachine()` definitions (stately.ai/blog/2022-11-29-import-from-code). **Export as code**: JSON, JavaScript, TypeScript (v4 and v5 toggle), Markdown, Mermaid, and "Stories" (stately.ai/docs/export-as-code).
- **Observation:** The docs state XState "is most useful for… making app logic visually collaborative, so that your entire team (technical and non-technical) can easily understand and contribute to it" (stately.ai/blog/2023-12-01-xstate-v5).
- **Interpretation:** Stately Studio is a genuine visual, collaborative, no-code-entry editor with round-trip code import/export and Mermaid output — directly useful for non-programmers to model and read artefact lifecycles. Confidence: **High**.

### 5. Persistence
- **Observation:** `actor.getPersistedSnapshot()` returns a plain object that can be `JSON.stringify`'d; restore via `createActor(machine, { snapshot: restoredState }).start()` (stately.ai/docs/persistence; stately.ai/blog/2023-10-02-persisting-state).
- **Observation:** Storage strategies listed: browser — localStorage, IndexedDB, cookies, sessionStorage, in-memory; server — databases (MongoDB, PostgreSQL examples in the XState repo), caches (Redis), cookies/session (stately.ai/blog/2023-10-02-persisting-state; stately.ai/docs/persistence).
- **Observation:** **Deep persistence** in v5: invoked/spawned actors are recursively persisted and restored, unlike v4 where they were not (stately.ai/blog/2023-12-01-xstate-v5).
- **Observation (caveats):** State must be JSON-serializable (no functions/classes); restored state may be incompatible if logic changed; already-executed actions are not re-executed on restore (stately.ai/docs/persistence caveats).
- **Observation:** **Event sourcing** is offered as an alternative: persist events via the Inspect API and replay them to rebuild state (stately.ai/docs/persistence). `@xstate/store/persist` provides `version` + `migrate` (stately.ai/docs/xstate-store/persist).
- **Interpretation:** Persistence is built-in and storage-agnostic (serialize snapshot → any store → restore). The format is a JSON-serializable snapshot object. The main risks are non-serializable context and definition drift, both documented and mitigable. Confidence: **High** for the mechanism; **Medium** for long-lived/migrated persistence at scale (relies on user-built migration discipline).

### 6. Hierarchy
- **Observation:** XState supports **nested/compound states** (nested `states` blocks); substates inherit transitions from their parent (miguelarmengol.com/blog/applied-ai-engineering-notes/xstate; stately.ai/docs). State node types include `compound`, `atomic`, `parallel`, `history`, `final` (github.com/statelyai/xstate migration.md; xstate v4+).
- **Observation:** **Parallel (orthogonal) states** via `type: 'parallel'` allow multiple regions active simultaneously, each its own lifecycle within one machine (timdeschryver.dev; miguelarmengol.com).
- **Observation:** **History states** via `type: 'history'` (shallow by default, `history: 'deep'` for deep) remember the last active substate and resume on re-entry (miguelarmengol.com; github migration.md).
- **Observation:** **Delayed transitions** via `after: { ms: target }` (miguelarmengol.com).
- **Observation (important nuance):** Context is defined once at the root; "context is the same for every state and should only be defined in the top-level machine." Local/private state per region requires a separate invoked/spawned actor, which has its own context (github statelyai/xstate discussion #1528, maintainer reply).
- **Interpretation:** XState implements the full Harel statechart hierarchy vocabulary (nested, parallel, history, delayed). The single shared context per machine is a modelling constraint — fine-grained per-region private data must be pushed into child actors. Confidence: **High**.

### 7. Composition
- **Observation:** XState is described as "a state management and orchestration solution… zero dependencies… useful for frontend and backend application logic" and "orchestrates any logic, from promises to state machines" (github.com/statelyai/xstate README; stately.ai/blog/2023-12-01-xstate-v5). It is a library, not an application framework.
- **Observation:** XState composes via the actor model: machines can `invoke` or `spawn` other actors (promise, observable, callback, or machine actors), with `machine.provide()` supplying per-instance implementations (stately.ai/docs/invoke; stately.ai/docs/actors; stately.ai/blog/2024-02-02-migrating-machines-to-xstate-v5). Composable actor logic wrappers (e.g. `withLogging`) are shown in the v5 blog.
- **Observation:** A comparison of XState vs workflow engines (Temporal, Airflow, Step Functions, Inngest) states they are complementary: "XState often runs *inside* a workflow engine task"; XState owns in-process/UI↔backend orchestration while workflow engines own cross-service durability (miguelarmengol.com/blog/applied-ai-engineering-notes/xstate).
- **Interpretation:** XState does **not** assume ownership of the full application lifecycle. It can manage artefact lifecycles (one actor per artefact) while a separate workflow/graph engine owns execution and cross-service durability. The two layers compose: XState as the per-artefact statechart, the workflow engine as the orchestrator. Confidence: **High** for the composability claim; the exact integration pattern is inferred from documented actor composition rather than a specific "XState + external graph engine" reference implementation.

### XState v5 ("Glacier") impact
- **Observation:** v5 is a major rewrite (released 2023-12-01) that makes **actors the main focus** rather than machines (stately.ai/blog/2023-12-01-xstate-v5). This directly strengthens RQ2's "independent lifecycle per artefact" answer — actors are the unit of execution.
- **Observation:** v5 adds **deep (recursive) persistence** of invoked/spawned actors (absent in v4) — strengthens the hierarchy + persistence answers (stately.ai/blog/2023-12-01-xstate-v5).
- **Observation:** v5 replaces `interpret()` with `createActor()`, `Machine()` with `createMachine()`, and the magic `devTools: true` with the explicit **Inspect API** — strengthens the inspection answer (stately.ai/blog/2023-12-01-xstate-v5; stately.ai/docs/migration).
- **Observation:** v5 adds `setup()` (typed config), `input`/`output`, parameterized actions/guards, and `machine.provide()` for per-instance implementations (stately.ai/blog/2023-12-01-xstate-v5; stately.ai/blog/2024-02-02-migrating-machines-to-xstate-v5).
- **Interpretation:** v5 does **not** change the qualitative answers to RQ2, but it materially improves them: actor-centric execution, deep persistence, and a cleaner inspect API. All evidence in this report is drawn from v5 docs unless explicitly noting v4.

## Findings

1. **Independent lifecycle per artefact — Yes.** Each artefact maps to one `createActor(machine)` instance. The machine definition is shared; instances are isolated (own state, context, mailbox, lifecycle). 5000 artefacts = 5000 actors. No documented per-instance ceiling; per-instance cost is the snapshot + mailbox. *Caveat:* no official 5000-instance benchmark located — feasibility is inferred, not measured.
2. **Runtime inspection — Strong.** `getSnapshot()` reads current state synchronously; the Inspect API streams lifecycle/snapshot/event events; XState DevTools (time-travel), Stately Studio, and the VS Code extension provide visualization.
3. **Versionable definitions — Yes, with a persistence caveat.** Definitions are ordinary code/Studio versions; v1 and v2 run simultaneously as different actors; v4/v5 coexist via npm aliases. Changing a definition does not disturb running in-memory actors, but persisted snapshots may become incompatible — mitigated by migrate-on-load (`xstate-migrate`, `@xstate/store/persist` version+migrate).
4. **Visual tooling — Strong and non-programmer-friendly.** Stately Studio is a no-code, collaborative, drag-and-drop editor with Design/Simulate modes, AI assistance, and round-trip import/export (JSON/JS/TS/Mermaid/Markdown). Directly useful for non-programmers.
5. **Persistence — Built-in and storage-agnostic.** `getPersistedSnapshot()` → JSON → any store (localStorage, IndexedDB, MongoDB, Postgres, Redis) → restore via `createActor(machine, { snapshot })`. Deep persistence in v5. Caveats: JSON-serializable context only; definition drift breaks restore; actions not replayed (use event sourcing as alternative).
6. **Hierarchy — Full statechart vocabulary.** Nested/compound, parallel (orthogonal), history (shallow/deep), and delayed transitions are all supported. Single shared root context is a modelling constraint; per-region private state requires child actors.
7. **Composition — Clean.** XState is a library, not a lifecycle-owning framework. It composes with a separate graph/workflow layer via the actor model; it is documented as commonly running *inside* a workflow engine. It can own per-artefact lifecycles while an external engine owns execution.
8. **v5 impact — Improves, does not alter.** Actor-centric execution, deep persistence, and the Inspect API make v5 a strictly better fit for RQ2 than v4, but the qualitative conclusions hold in both.

**Overall read on RQ2:** XState/Stately can model independent artefact lifecycles well — one actor per artefact, full hierarchy, strong inspection/visualization, versionable definitions, and built-in persistence — and it composes cleanly with a separate execution/workflow layer rather than demanding ownership of it. The principal uncertainties are quantitative (memory at 5000+ instances, persisted-snapshot migration discipline) rather than qualitative capability.

## Rejected options

- **Treating XState as a full application framework that owns the lifecycle.** Rejected: evidence shows it is a library/orchestration layer that composes via actors and is documented as running *inside* workflow engines; it does not assume app-lifecycle ownership.
- **Assuming a single shared context can hold per-region private state.** Rejected: maintainer guidance (discussion #1528) states context is root-level only; local state requires separate actors.
- **Assuming persisted snapshots are automatically forward-compatible across definition changes.** Rejected: persistence docs explicitly warn of incompatibility; migration is the user's responsibility (or a third-party lib's).
- **Relying on the 1000-client scaling discussion (#3775) as evidence.** Rejected: the captured thread contains only the question, no benchmark or authoritative answer; treated as an open unknown, not evidence.
- **Assuming v4 and v5 behave identically for RQ2.** Rejected: v5's deep persistence and Inspect API are material improvements; findings are reported against v5.

## Unknowns

- **Memory/CPU cost at 5000+ concurrent actors** — no official or independent benchmark located; feasibility inferred from architecture, not measured.
- **Behaviour of always-on Inspect API at scale** — documented as available, overhead not quantified.
- **Robustness of long-lived persisted-snapshot migration** across many definition versions in production — relies on user discipline or third-party `xstate-migrate`; no built-in guarantee observed.
- **Whether a specific "XState + external graph/workflow engine" reference integration exists** — composability is inferred from actor-model documentation and the XState-vs-workflow-engine comparison, not from a concrete paired example.
- **Stately Studio's non-programmer usability in practice** (beyond marketing/"no code required" claims) — not independently user-tested in this review.
- **Exact snapshot format stability** — a 2026 third-party account (StateKeep) reports the v5 snapshot format broke v4-persisted state on upgrade, underscoring that the serialized format is not a guaranteed-stable public contract.

## Confidence

**High** for the capability findings: independent lifecycle (actor model), inspection, hierarchy, visual tooling, persistence mechanism, and composition are all well-supported by official XState v5 docs, the Stately Studio docs, the v5 launch blog, and the GitHub repo.

**Medium** for the quantitative/operational findings: 5000-instance memory behaviour lacks a benchmark; persisted-snapshot migration across definition versions depends on user-built or third-party tooling and the serialized format is not a stable contract.

Justification: RQ2 ("can hierarchical statechart frameworks model independent artefact lifecycles?") is answered with reasonable confidence as **yes** for XState/Stately — the capability is present and well-documented. The residual uncertainty is concentrated in scale quantification and persistence-versioning discipline, not in whether the modelling is possible.

## References

- XState v5 launch blog (actors, Inspect API, deep persistence, v5 changes) — https://stately.ai/blog/2023-12-01-xstate-v5
- XState v5 migration guide — https://stately.ai/docs/migration
- Migrating machines to XState v5 (side-by-side v4/v5, `provide()`) — https://stately.ai/blog/2024-02-02-migrating-machines-to-xstate-v5
- XState docs (actors, invoke, persistence, studio, export-as-code, xstate-store/persist) — https://stately.ai/docs
- XState docs: Actors — https://stately.ai/docs/actors
- XState docs: Invoke — https://stately.ai/docs/invoke
- XState docs: Persistence (caveats, event sourcing) — https://stately.ai/docs/persistence
- XState docs: Stately Studio — https://stately.ai/docs/studio
- XState docs: Export as code — https://stately.ai/docs/export-as-code
- XState docs: Studio API (machine versions) — https://stately.ai/docs/studio-api
- XState docs: `@xstate/store/persist` (version + migrate) — https://stately.ai/docs/xstate-store/persist
- Persisting and restoring state in XState (blog) — https://stately.ai/blog/2023-10-02-persisting-state
- XState GitHub repo (README, packages, zero-dep, MIT) — https://github.com/statelyai/xstate
- XState GitHub migration.md (state node types) — https://github.com/statelyai/xstate/blob/main/migration.md
- GitHub discussion #3775 (scaling question, 1000 clients) — https://github.com/statelyai/xstate/discussions/3775
- GitHub discussion #1528 (single root context; local state needs actors) — https://github.com/statelyai/xstate/discussions/1528
- XState DevTools (Chrome, v5, time-travel) — https://github.com/mjbeswick/xstate-devtools ; Chrome Web Store listing
- Stately VS Code extension — https://marketplace.visualstudio.com/items?itemName=statelyai.stately-vscode
- XState Viz (legacy) — https://stately.ai/viz
- Import from code (Studio) — https://stately.ai/blog/2022-11-29-import-from-code
- Parallel states write-up — https://timdeschryver.dev/blog/building-incremental-views-with-xstate-parallel-states
- XState formal-concept mapping & XState-vs-workflow-engines comparison — https://miguelarmengol.com/blog/applied-ai-engineering-notes/xstate
- `xstate-migrate` (persisted-snapshot migration library) — https://www.npmjs.com/package/xstate-migrate
- StateKeep (third-party account of v5 snapshot-format breakage / persistence gap) — https://dev.to/statekeep/the-xstate-persistence-problem-is-five-years-old-here-is-what-we-built-to-finally-solve-it-39af
