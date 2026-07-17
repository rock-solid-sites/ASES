# RQ2 — SCXML

## Question

Can hierarchical statechart frameworks model independent artefact lifecycles? This report investigates SCXML (State Chart XML, the W3C standard) and its implementations as a candidate answer, focusing on whether each artefact can carry its own independent, inspectable, versionable, persistable, and composable statechart lifecycle.

## Scope

**Investigated:**
- W3C SCXML 1.0 Recommendation (1 September 2015) — core constructs, data model, external communications, `<invoke>`.
- JavaScript: scion-core (jbeard4) and the SCION-SCXML ecosystem (GitLab).
- C/C++: uSCXML (tklab-tud) — the most W3C-compliant engine.
- Python: PySCXML (jroxendal), PyBlendSCXML (alexzhornyak), scxml4py (Open-MBEE).
- Other: Apache Commons SCXML (Java), Qt SCXML, Rust `scxml` crate (GnomesOfZurich), itemis CREATE / YAKINDU, ScxmlEditor, NVIDIA UI Composer.
- Ecosystem health: release cadence, activity, and whether SCXML has been superseded.

**Excluded (out of scope for this pass):**
- XState and other JSON-based statechart libraries — noted only as ecosystem context, not a SCXML implementation.
- Deep benchmarking of interpreter performance under thousands of concurrent instances (no public multi-instance throughput data found; overhead characterized as an assumption).
- Line-by-line conformance of every engine against the full IRP test suite (only the compliance summary table from the SCXML tutorial was available).

## Evidence

### 1. Independent lifecycle per artefact
- SCXML interpreters are instantiated **per document**. Each instance is an independent execution context: scion-core via `new scion.SCInterpreter(model)` (jbeard4/SCION-CORE README); uSCXML via `uscxml::Interpreter::fromURL(...)` (tklab-tud/uscxml README); scxml4py via `Application(scxmlDoc=...)` (Open-MBEE/scxml4py README).
- *Observation:* Because instantiation is per-document and the interpreter owns its own configuration + datamodel, two artefacts can each run a different SCXML definition (or different versions of the same definition) in separate instances simultaneously.
- *Interpretation/Assumption:* Running many instances implies per-instance memory for the active configuration and datamodel. No engine was found that offers a shared/optimised multi-instance pool; overhead is therefore assumed to scale roughly linearly with instance count. This is an assumption — no published multi-instance memory/throughput figures were located.

### 2. Runtime state inspection
- scion-core exposes the active **configuration** (the set of currently active states) via `getConfiguration()` (jbeard4/SCION-CORE README: "its **configuration** (the set of states the state machine is currently in)").
- uSCXML provides an `InterpreterMonitor` callback API (`enterState`, `exitState`) and `step()` returns the current state; the class reference explicitly distinguishes "the state ... not to be confused with the interpreter's configuration" (tklab-tud/uscxml docs).
- scxml4py exposes `get_current_status()` and a `StatusListener` that "receives current state configuration updates" plus an `EventListener` (Open-MBEE/scxml4py README).
- *Observation:* All major engines permit inspecting the live active-state set at runtime. Debugging tooling beyond logging/callbacks (breakpoints, step-through visual debuggers) is implementation-specific and concentrated in commercial tooling (itemis CREATE simulation view).

### 3. Versionable definitions
- SCXML definitions are plain XML text (W3C Recommendation). *Observation:* XML is inherently diff-/version-friendly (git, etc.).
- *Observation:* Because each interpreter instance loads a specific document, artefact A can run definition v1 while artefact B runs v2 in the same process. Simultaneous multi-version execution is a direct consequence of independent per-instance loading, not a separately specified feature.

### 4. Visual tooling
- **ScxmlEditor** (alexzhornyak) — graphical SCXML editor with a tutorial; positioned for non-expert authoring (alexzhornyak/SCXML-tutorial).
- **Qt SCXML** (Qt Creator) — "a simple graphical editor for SCXML documents" (itemis blog, "Taking SCXML to the next level").
- **itemis CREATE / YAKINDU Statechart Tools** — SCXML domain with higher-level modeling, interactive simulation, and SCTUnit unit testing; requires a **Professional Edition License** (itemis.com docs; medium.com/@andreasmuelder).
- **GnomesOfZurich live editor** — browser-based WASM editor that renders the statechart instantly and lets you send events to simulate transitions (gnomesofzurich.github.io/scxml).
- **NVIDIA UI Composer Studio** — editor + runtime for SCXML statecharts used in automotive in-vehicle UIs (phrogz.net white paper, EICS 2014).
- **Apache Commons SCXML Eclipse GMF editor** — sandbox project, old (commons.apache.org).
- *Interpretation:* Visual tooling exists but is fragmented. The most capable (itemis) is commercial; free editors are either simple (Qt) or community/maintained-by-individuals (ScxmlEditor, GnomesOfZurich). Whether a true non-programmer can author correct SCXML unaided is an assumption — SCXML's XML verbosity means most non-trivial models are generated from a higher-level editor rather than hand-written.

### 5. Persistence
- The W3C spec's only "Serialization" clause (Appendix B.2.9) concerns serializing the **data model** to JSON for transmission via the Basic HTTP Event I/O Processor — *not* the full interpreter state (w3.org/TR/scxml B.2.9).
- uSCXML exposes a `serialize()` method on `Interpreter`, but issue #93 records the maintainer's note: "The problem with serializing the complete state of an interpreter instance is the state of the embedded data-model. It is, generally, not possible to serialize the state of an embedded JavaScriptCore instance or a Google V8 engine" (tklab-tud/uscxml issue #93).
- The SCION-SCXML project has a "multilevel-state-machine-monitor-proof-of-concept" demonstrating how to "capture the state of a multi-level state machine, persist it to the filesystem, and load it from the serialized state" (GitLab scion-scxml PoC).
- *Observation:* Full interpreter-state persistence (configuration + datamodel + event queue) is **not standardized** by SCXML and is implementation-specific and partial. Data-model serialization to JSON is standardized but covers only the data, not execution position.

### 6. Hierarchy
- SCXML natively specifies compound (nested) states, parallel (`<parallel>`) states, history states (deep and shallow), and final states (W3C Recommendation §3).
- W3C IRP compliance summary (alexzhornyak/SCXML-tutorial):
  - **uSCXML 2.0** — ecmascript datamodel — 159/159 mandatory, 33/33 optional — **Full**.
  - **SCION CLI 1.0.37** — 156/159 mandatory, 18/33 optional — Partial.
  - **PyBlendSCXML 1.0.0** (python) — 159/159 mandatory, 22/33 optional — Partial.
  - **Qt SCXML 5.15** — 141/159 mandatory, 17/33 optional — Partial.
- *Observation:* The hierarchy primitives are delivered **fully** by uSCXML and **partially** by the others (gaps concentrated in optional features). The spec's hierarchical promises are real but implementation fidelity varies.

### 7. Composition
- SCXML provides `<invoke>` to instantiate external services or other SCXML machines from within a state, plus `<send>`/`<cancel>` and external event I/O processors (W3C Recommendation §6). PySCXML notes "The only service that can be instantiated with `<invoke>` is another SCXML state machine" (jroxendal/PySCXML README); scxml4py uses `<invoke id="ActivityOnline"/>` to launch a concurrent `Activity` (Open-MBEE/scxml4py).
- Engines are embeddable as libraries: uSCXML as `libuscxml`, scxml4py as an `Application` object, scion-core as a JS module.
- *Observation:* SCXML does **not** assume sole ownership of the full lifecycle. It can (a) be embedded as a component inside a larger application/workflow layer, and (b) delegate to or communicate with other machines/services via `<invoke>`/`<send>`. It does not itself provide a higher-level workflow-orchestration layer above statecharts; composition is achieved by embedding or by invocation, not by native cross-artefact orchestration.

### Ecosystem health
- SCXML 1.0 became a **W3C Recommendation on 1 September 2015** and has had **no new version since** (w3.org/TR/scxml status section). The `w3c/scxml` GitHub repo (created 2025-09-29) is described as "the editor's copy" — a mirror, not evidence of active new standardization.
- Implementation activity is **fragmented and largely stale**:
  - uSCXML: C/C++, full compliance, but README states "There are no installers yet and we do not feature any releases"; last substantive changelog entry 2017; ~114 stars, 22 open issues (tklab-tud/uscxml).
  - scion-core: last commit 2018; partial compliance.
  - Apache Commons SCXML: v0.9 (2015); a "2.0 Roadmap" aligned to the spec was never released as stable (commons.apache.org).
  - PySCXML: Python 2.6/2.7 only, stale (jroxendal/PySCXML).
  - scxml4py (Open-MBEE): Python, niche (MBSE/systems engineering).
  - Qt SCXML: maintained as part of the Qt framework (5.15, 6.x) — the most actively maintained mainstream engine.
  - Rust `scxml` crate (GnomesOfZurich): newer, document model + XState v5 import/export.
- *Interpretation:* SCXML has been **largely superseded for web/UI state management by XState** (JSON-based, far more popular and actively developed). SCXML persists in its original and adjacent niches: voice/IVR (its origin), automotive HMI (Qt, NVIDIA), embedded (uSCXML transpiles to ANSI-C / Arduino / VHDL), and MBSE (Open-MBEE). The **specification is stable and sound; the weakness is the implementation and tooling ecosystem.**

## Findings

1. **Independent artefact lifecycles are well-supported in principle.** SCXML's per-document interpreter model lets each artefact run its own statechart instance, with independent state, events, and datamodel, and different versions can coexist. (Observation, high confidence.)
2. **Runtime inspection is available** in all major engines via configuration/status accessors and state-change listeners, though rich visual debuggers are mostly commercial. (Observation, high confidence.)
3. **Versioning is trivial at the definition level** (XML text) and multi-version co-execution follows from independent instances. (Observation + interpretation, high confidence.)
4. **Hierarchy is a first-class, spec-guaranteed feature**, fully delivered by uSCXML and partially by others. (Observation, high confidence.)
5. **Persistence of full runtime state is not standardized and is partial/implementation-specific**, with a known hard limitation around serializing embedded script-engine datamodels. (Observation, high confidence on the limitation; medium on the practical ceiling.)
6. **Composition is possible** via embedding as a library and via `<invoke>`/`<send>`, so SCXML does not monopolise the lifecycle — but it offers no native cross-artefact orchestration layer. (Observation + interpretation, medium-high confidence.)
7. **The ecosystem is stable-but-stale**: a solid 2015 W3C standard with fragmented, mostly unmaintained engines, increasingly overshadowed by XState for new web work. (Observation + interpretation, medium-high confidence.)

## Rejected options

- **PySCXML as a primary engine** — Python 2.6/2.7 only and stale; unsuitable for a modern execution engine. (Considered, ruled out on maintenance grounds.)
- **Apache Commons SCXML as a primary engine** — still at v0.9 (2015) with an unfinished 2.0 roadmap; partial spec compliance. (Considered, ruled out on maturity grounds.)
- **Treating SCXML as a full workflow-orchestration layer** — SCXML models a single statechart's lifecycle; it has no native concept of coordinating many heterogeneous artefacts' lifecycles. It would need to be embedded within or invoked by a separate orchestration layer. (Considered, ruled out as a category mismatch.)

## Unknowns

- **Multi-instance overhead ceiling:** No published data on memory/throughput for running thousands of concurrent SCXML interpreter instances. Linear-scaling assumption is unverified.
- **Practical persistence fidelity:** Whether scion-scxml's monitor-based serialization (or any engine's) reliably restores *all* execution state (including in-flight timers, queued external events, and script-engine closures) across process restarts. uSCXML's own issue #93 suggests script datamodel state is the hard blocker.
- **Non-programmer authoring reality:** Whether existing free visual editors (ScxmlEditor, Qt) let a non-programmer produce *correct* non-trivial SCXML without understanding statechart semantics.
- **Future of the standard:** Whether W3C will ever publish a SCXML 2.0; the 2025 editor's-copy repo gives no signal of active revision.

## Confidence

**Medium-High.** The core claims — independent instances, runtime inspection, versionability, native hierarchy, composition via invoke/embedding, and a stable-but-stale ecosystem — are directly supported by the W3C spec and multiple implementation READMEs/docs (high confidence). Confidence is capped at Medium-High rather than High because: (a) full-state persistence is only partially evidenced and has a documented hard limitation; (b) multi-instance overhead is characterized by assumption, not measurement; and (c) the "non-programmer usability" of visual tooling is inferred, not demonstrated.

## References

- W3C SCXML 1.0 Recommendation (1 Sep 2015): https://www.w3.org/TR/scxml/
- W3C SCXML status / Recommendation notice: https://www.w3.org/TR/scxml/ (Status of this Document)
- SCXML Serialization (Appendix B.2.9): https://www.w3.org/TR/scxml/#serialize
- scion-core (jbeard4/SCION-CORE): https://github.com/jbeard4/SCION-CORE
- SCION-SCXML ecosystem (GitLab): https://gitlab.com/scion-scxml
- SCION-SCXML state-machine monitor PoC: https://gitlab.com/scion-scxml/multilevel-state-machine-monitor-proof-of-concept
- uSCXML (tklab-tud/uscxml): https://github.com/tklab-tud/uscxml
- uSCXML serialize issue #93: https://github.com/tklab-tud/uscxml/issues/93
- uSCXML Interpreter class reference: https://tklab-tud.github.io/uscxml/classuscxml_1_1_interpreter.html
- PySCXML (jroxendal): https://github.com/jroxendal/PySCXML
- PyBlendSCXML (alexzhornyak): https://github.com/alexzhornyak/PyBlendSCXML
- scxml4py (Open-MBEE): https://github.com/Open-MBEE/scxml4py
- Apache Commons SCXML: https://commons.apache.org/proper/commons-scxml/
- Qt SCXML: https://doc.qt.io/qt-5/qtscxml-index.html
- Rust `scxml` crate (GnomesOfZurich): https://docs.rs/scxml ; live editor: https://gnomesofzurich.github.io/scxml/
- itemis CREATE SCXML domain: https://www.itemis.com/en/products/itemis-create/documentation/user-guide/scxml_integration
- "Taking SCXML to the next level" (itemis/YAKINDU blog): https://medium.com/@andreasmuelder/taking-scxml-to-the-next-level-25c556ce758f
- SCXML tutorial & W3C compliance table (alexzhornyak): https://alexzhornyak.github.io/SCXML-tutorial/
- NVIDIA UI Composer SCXML white paper (EICS 2014): https://phrogz.net/developing-user-interfaces-using-scxml-statecharts
- SCXML Wikipedia: https://en.wikipedia.org/wiki/SCXML
- w3c/scxml editor's-copy repo: https://github.com/w3c/scxml
