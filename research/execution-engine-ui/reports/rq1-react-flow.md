# RQ1 — React Flow

## Question

Can existing graph frameworks represent engineering artefacts and their relationships without substantial customization? This report investigates **React Flow** (`@xyflow/react`, https://reactflow.dev) as a candidate against that question.

## Scope

**Investigated:**
- Node content flexibility (custom nodes, expandable/complex content)
- Performance characteristics at scale (5k+ nodes), including documented benchmarks and degradation points
- Incremental rendering behaviour (changed-only vs. full re-render)
- Hierarchical / nested / compound graph support
- Viewport-based virtualization
- Maintenance activity, release cadence, community size, backing
- Composability with an external state/lifecycle layer (specifically XState)
- Dependency and competitive relationships with ElkJS, Rete.js, and other graph libraries

**Excluded:**
- Hands-on benchmarking (no code executed; this is a literature/evidence review)
- React Flow Pro paid examples beyond noting their existence and what free API covers
- Svelte Flow (sibling library in the same monorepo) except where it informs maintenance
- Detailed API tutorial content beyond what is needed to answer RQ1

## Evidence

### 1. Expandable / complex node content
- **Observation:** React Flow's own custom-nodes guide states: "Within your custom nodes you can render everything you want. You can define multiple source and target handles and render form inputs or charts for example." Nodes are ordinary React components (`reactflow.dev/learn/advanced-use/custom-nodes`).
- **Observation:** React Flow ships `NodeToolbar`, `NodeResizer`, `Panel`, `MiniMap`, `Controls`, `Background` components (`reactflow.dev`).
- **Interpretation:** Because a node is an arbitrary React component, embedding metadata, status indicators, or a project-management-style view inside a node is feasible without framework-level customization. The "customization" required is ordinary React component authoring, not library extension.

### 2. Performance at 5k+ nodes
- **Observation:** The official Performance guide (`reactflow.dev/learn/advanced-use/performance`) documents optimization strategies (memoization via `React.memo`/`useCallback`/`useMemo`, avoiding reading the full `nodes`/`edges` arrays in components, collapsing large node trees via the `hidden` property, simplifying CSS). It does **not** publish a benchmark number for 5k+ nodes.
- **Observation:** A third-party optimization write-up (Synergy Codes) bases its guidance on a project of **100 nodes** (60 FPS baseline); it is not a 5k benchmark (`synergycodes.com`, `medium.com/@lukasz.jazwa`).
- **Observation:** React Flow renders nodes as **HTML/DOM elements** (not Canvas/WebGL). A comparative study (`naranyala/comparative-react-tree-graph-lib`) rates HTML rendering as the "slowest rendering" engine and notes SVG performance "drops after ≈1k nodes."
- **Observation:** A commercial blog (`visualflow.dev`, "Architecting for Massive Scale", 2026) claims React Flow can handle **10,000 nodes** using `onlyRenderVisibleElements` plus Level-of-Detail (LOD) / semantic zoom, but this is a paid-template promotion and is therefore treated as a lower-confidence claim.
- **Interpretation:** There is **no official documented benchmark at 5k+ nodes**. The available evidence indicates that at 5k+ nodes, the default mode (all nodes in the DOM) will degrade, and that virtualization + LOD are the expected mitigations. The precise degradation threshold is undocumented.

### 3. Incremental rendering
- **Observation:** React Flow's older README/feature list states "Only nodes that have changed are re-rendered" and "only those that are in the viewport are displayed" (historical `react-flow-renderer` README). The current docs emphasize React's virtual DOM redraws only changed components.
- **Observation:** By default React Flow renders **every** node into the DOM even when off-screen (`dev.to/usman_abdur_rehman`, `visualflow.dev`). Viewport culling is opt-in.
- **Interpretation:** React Flow performs *changed-node* incremental rendering by default, but *not* viewport-based culling by default. "Incremental rendering" in the RQ sense (only visible elements) requires enabling `onlyRenderVisibleElements`.

### 4. Hierarchical / nested graphs
- **Observation:** React Flow supports **Sub Flows**: a node becomes a parent by assigning its id to a child's `parentId` (renamed from `parentNode` in v11.11). Children are positioned *relative* to the parent and move with it; `extent: 'parent'` constrains children inside the parent (`reactflow.dev/learn/layouting/sub-flows`).
- **Observation:** The `group` node type is a convenience parent with no handles. Edges connected to a parented node render above other nodes.
- **Observation:** Expand/collapse of subtrees is demonstrated via a `useExpandCollapse` hook (React Flow **Pro**, paid) and via the free `isHidden` node property (`reactflow.dev/examples/layout/expand-collapse`; `reactflow.dev/docs/examples/hidden`).
- **Observation (important nuance):** In xyflow discussion #1024, a maintainer explains they *deliberately avoided* nesting child nodes inside the parent's DOM `<div>` (it caused z-index/positioning issues); children are positioned relatively but are not nested markup-wise.
- **Interpretation:** Parent-child / hierarchical structures are representable, but React Flow does **not** provide true "compound nodes" in the graph-theory sense (nested DOM containers). It provides relative positioning + grouping + collapse, which covers most engineering-artefact hierarchy needs but is not a native compound-graph data model.

### 5. Virtualization
- **Observation:** The official API reference documents the `onlyRenderVisibleElements` boolean prop: "You can enable this optimisation to instruct React Flow to only render nodes and edges that would be visible in the viewport. This might improve performance when you have a large number of nodes and edges but also adds an overhead." Default: `false` (`reactflow.dev/api-reference/react-flow`).
- **Observation:** A known limitation (per `visualflow.dev`): when the user zooms fully out, *every* node becomes visible, bypassing virtualization and re-introducing the full-DOM cost. Mitigation is semantic zoom / LOD (swap complex nodes for lightweight placeholders below a zoom threshold).
- **Interpretation:** Viewport-based virtualization is a **built-in, first-class prop** — not a custom build. It is opt-in and has an acknowledged overhead and a zoom-out edge case.

### 6. Maintenance activity
- **Observation:** `reactflow.dev` homepage reports **37.6k GitHub stars**, **8.59M weekly npm installs**, **MIT license**.
- **Observation:** Homepage shows recent releases "React Flow 12.11.2" (~2 days before capture), 12.11.1, 12.11.0 — indicating an active release cadence (mid-2026).
- **Observation:** Maintained by the **xyflow team** (webkid, Berlin), described as a "full-time project" since 2019; a commercial "React Flow Pro" offering funds development (`github.com/xyflow/xyflow`, `reactflow.dev`).
- **Observation:** The `xyflow` monorepo hosts React Flow 12 (`@xyflow/react`), React Flow 11 (`reactflow`), Svelte Flow (`@xyflow/svelte`), and shared `@xyflow/system`; releases use changesets.
- **Interpretation:** React Flow is actively maintained, widely adopted, and has sustainable (commercially-backed) stewardship. Confidence in maintenance health: **High**.

### 7. Composition with an external state/lifecycle layer (XState)
- **Observation:** React Flow is a React component driven by `nodes`/`edges` props. It supports both uncontrolled state (internal) and controlled state. Its State Management guide explicitly shows use with **Zustand, Redux, Recoil, and Jotai** (`reactflow.dev/learn/advanced-use/state-management`).
- **Observation:** React Flow uses **Zustand internally** for its own store but does **not** impose app-wide state ownership (`reactflow.dev` state-management guide; npm credits list Zustand as "internal state management").
- **Observation:** XState is framework-agnostic; `@xstate/react` provides `useMachine`/`useActor`/`useSelector` hooks (`stately.ai/docs`). React Flow is simply a view that can be fed nodes/edges derived from XState actor state.
- **Interpretation:** React Flow does **not** assume ownership of the full application lifecycle. It is a rendering/interaction layer that composes cleanly with an external state machine. XState can own lifecycle/state and supply React Flow's `nodes`/`edges`. **Assumption:** the integration is straightforward, but no *official* React Flow + XState paired example was found in this review, so the exact wiring pattern is inferred rather than documented.

### 8. Dependencies and relationships with other graph libraries
- **Observation:** React Flow's npm credits list internal dependencies: **d3-zoom** (zoom/pan/drag of canvas), **d3-drag** (node dragging), **zustand** (internal state). It does **not** depend on ElkJS or Rete.js (`npmjs.com/package/reactflow`).
- **Observation:** React Flow has **no built-in layout engine**. Its layouting docs recommend third-party libraries — **Dagre, D3-Hierarchy, D3-Force, ELK** — and provide official ElkJS and Dagre integration examples (`reactflow.dev/learn/layouting/layouting`, `/examples/layout/elkjs`).
- **Observation:** Rete.js is described as "a framework for creating visual interfaces and workflows... visualization... and processing graphs based on dataflow and control flow" — i.e. a peer/alternative, not a dependency (`libhunt.com/compare-react-flow-vs-rete`).
- **Interpretation:** React Flow is a **rendering + interaction layer**. It is *complementary* to ElkJS (layout delegated outward), not dependent on or competing with it. It *overlaps/competes* with Rete.js at the "visual node editor" level, but Rete.js is a broader dataflow framework whereas React Flow is a focused view component.

## Findings

1. **Node content is highly flexible.** Nodes are React components, so representing rich engineering-artefact content (metadata, status, PM-style views) requires only ordinary component authoring — not library customization. (Addresses RQ "without substantial customization": **yes** for content.)
2. **Hierarchical structures are representable** via Sub Flows (`parentId`, `group`, `extent:'parent'`, `isHidden` collapse), but React Flow is **not** a native compound-graph model — children are relatively positioned, not DOM-nested. This covers most hierarchy needs but is a modelling limitation to note.
3. **Virtualization is built-in** (`onlyRenderVisibleElements`) and first-class, but opt-in, carries overhead, and is defeated when fully zoomed out (mitigated by LOD).
4. **No official 5k+ benchmark exists.** Evidence (DOM/HTML rendering, third-party 100-node tests, a biased 10k commercial claim) indicates default mode degrades at scale and that virtualization + LOD are the expected path. The exact degradation threshold is undocumented.
5. **Maintenance health is strong** (37.6k stars, 8.59M weekly installs, MIT, active 12.11.x releases, commercially-backed xyflow team).
6. **Composition is clean.** React Flow does not own app lifecycle; it composes with external state (Zustand/Redux/Recoil/Jotai documented; XState feasible by inference). It is a view layer, not a full app framework.
7. **Dependency posture is favourable for RQ:** React Flow depends only on d3-zoom/d3-drag/zustand; layout is delegated to external libs (ElkJS etc.), so it neither depends on nor conflicts with them.

**Overall read on RQ1:** React Flow can represent engineering artefacts and their relationships with **low-to-moderate customization** for content, hierarchy, and interaction. The principal caveats are (a) no native compound-graph data model, and (b) performance at 5k+ nodes requires deliberate use of built-in virtualization/LOD rather than working out-of-the-box. It does **not** require substantial customization to *represent* the artefacts; it may require performance engineering to *scale* to 5k+.

## Rejected options

- **Treating React Flow as a full application framework.** Rejected: evidence shows it is a focused view component that explicitly defers state and layout to external layers; it does not assume app lifecycle ownership.
- **Assuming React Flow has a built-in layout engine.** Rejected: docs explicitly delegate layout to Dagre/ELK/D3 and provide integration examples; no internal auto-layout.
- **Relying on the 10k-node claim as established fact.** Rejected: the only 10k figure found originates from a paid-template promotional blog and is not an independent benchmark; treated as low-confidence.
- **Assuming native compound/ nested-DOM nodes.** Rejected: maintainer discussion #1024 confirms children are relatively positioned, not DOM-nested.

## Unknowns

- **Exact performance threshold at 5k+ nodes** under default vs. virtualized modes — no official or independent benchmark located.
- **Behaviour of `onlyRenderVisibleElements` overhead** in practice (the docs acknowledge overhead but give no magnitude).
- **Whether React Flow + XState is a documented, vetted integration pattern** — inferred feasible, but no official example found in this review.
- **Compound-graph semantics** (e.g., edges crossing hierarchy levels, multi-level grouping) beyond the basic `parentId`/`extent` model — not fully explored here.
- **Bundle-size / runtime cost of complex custom nodes** at scale (CSS animations, heavy components) — acknowledged as a factor but not quantified.

## Confidence

**Medium-High** for the structural/composition/maintenance findings (well-supported by official docs, API reference, and repo metadata).

**Medium** for the performance-at-scale findings, because the key claim (5k+ behaviour) lacks an official benchmark and rests on inference from rendering-engine characteristics plus one biased commercial source.

Justification: The question "can it represent artefacts and relationships without substantial customization" is answered with reasonable confidence as *yes for representation, with performance engineering required at scale*. The uncertainty is concentrated in quantitative performance, not in capability.

## References

- React Flow homepage — https://reactflow.dev/ (stars, installs, license, recent releases)
- React Flow custom nodes guide — https://reactflow.dev/learn/advanced-use/custom-nodes
- React Flow Performance guide — https://reactflow.dev/learn/advanced-use/performance
- React Flow State Management guide — https://reactflow.dev/learn/advanced-use/state-management
- React Flow Sub Flows (hierarchy) — https://reactflow.dev/learn/layouting/sub-flows
- React Flow API Reference (`onlyRenderVisibleElements`, `ReactFlow` props) — https://reactflow.dev/api-reference/react-flow
- React Flow Layouting (Dagre/ELK/D3) — https://reactflow.dev/learn/layouting/layouting
- React Flow ElkJS example — https://reactflow.dev/examples/layout/elkjs
- React Flow Expand & Collapse (Pro) example — https://reactflow.dev/examples/layout/expand-collapse
- xyflow monorepo / maintenance — https://github.com/xyflow/xyflow
- xyflow discussion #1024 (nested flows / no nested DOM) — https://github.com/xyflow/xyflow/discussions/1024
- xyflow discussion #2703 (virtualization prop) — https://github.com/xyflow/xyflow/discussions/2703
- xyflow discussion #4975 (performance with many nodes) — https://github.com/xyflow/xyflow/discussions/4975
- React Flow npm credits (d3-zoom, d3-drag, zustand) — https://www.npmjs.com/package/reactflow
- Synergy Codes — Optimize React Flow Performance — https://www.synergycodes.com/webbook/guide-to-optimize-react-flow-project-performance
- VisualFlow — Architecting for Massive Scale in React Flow (commercial, 10k claim) — https://www.visualflow.dev/blogs/scale-studio-pro
- Comparative React tree/graph library study (rendering engines) — https://github.com/naranyala/react-tree-graph-comparison
- XState React docs — https://stately.ai/docs/xstate-react
- React Flow vs Rete.js (libhunt) — https://www.libhunt.com/compare-react-flow-vs-rete
