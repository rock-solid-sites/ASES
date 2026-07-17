# RQ1 — JointJS

## Question

Can existing graph frameworks represent engineering artefacts and their relationships without substantial customization? This report investigates JointJS specifically: can it represent engineering artefacts (nodes with rich, expandable content, metadata, status indicators), scale to 5k+ nodes, render incrementally, model hierarchical structures, virtualize the viewport, and compose cleanly with a separate state-management/lifecycle layer — and does its ~2013-era architecture impose conflicting assumptions for modern React/framework-based development?

## Scope

**Investigated (via official docs, published performance articles, release notes, the open-source repository, and community reports):**

- Node content customization: SVG `markup`/`attrs` approach, content-driven elements, `foreignObject` HTML-in-SVG, and the HTML-overlay (custom view) approach.
- Performance characteristics at 5k+ nodes and documented optimization strategies.
- Incremental / viewport-based rendering and lazy-loading capabilities.
- Hierarchical graph support (compound nodes, parent-child relationships, embedding).
- Viewport virtualization (core `viewport()` callback, `viewManagement`, and the commercial `PaperScroller.virtualRendering`).
- Maintenance activity (release cadence, open issues, community size, corporate backing), distinguishing JointJS (open source, MPL-2.0) from JointJS+/Rappid (commercial).
- Composition with external state management / application lifecycle (Graph-as-model, `@joint/react`).
- Whether the architecture reflects older (pre-4.0) assumptions that conflict with modern framework-based development.

**Excluded:**

- Hands-on benchmarking (no local execution; claims rely on published perf pages, maintainer statements, and user reports).
- Deep source-code audit of the renderer internals beyond what is documented.
- Comparison against other frameworks (that is the remit of sibling RQ1 reports, not this one).
- Detailed API tutorial reproduction.

## Evidence

### 1. Expandable node content

- **Observation:** JointJS elements are SVG by default. Custom shapes are defined through `markup` (SVG node tree) and `attrs` (attribute bindings), via `dia.Element.define(...)` (docs.jointjs.com/learn/features/customizing-shapes). This supports arbitrary SVG content (rects, text, paths, gradients, images).
- **Observation:** "Content-driven elements" are supported: a custom element can derive its `width`/`height` from its content (e.g. label text length, image dimensions) rather than fixing size (resources.jointjs.com/tutorial/content-driven-element). This is a documented, first-class pattern.
- **Observation:** HTML content inside nodes is supported two ways:
  - **`foreignObject`** — embedding XHTML inside the SVG `markup` via `joint.util.svg` template literals; interactive inputs, forms, and CSS are possible (docs.jointjs.com/learn/features/customizing-shapes/html-inside-shapes, v4.2). A special `props` attribute lets model state drive DOM properties (e.g. an `<input>`'s `value`).
  - **HTML overlay** — a custom `ElementView` renders an HTML `<div>` positioned to follow the underlying SVG element; the tutorial notes this is the classic technique and that `foreignObject` "is however problematic due to a poor browser support" but "seems to be the right way of combining HTML with SVG in the future" (resources.jointjs.com/tutorials/html-elements.html).
- **Observation:** Collapse/expand of container nodes is a documented demo ("Container Collapse/Expand") built on embedding + the Paper `viewport` option (www.jointjs.com/demos/container-collapse-expand; docs.jointjs.com/learn/features/containers-and-grouping).
- **Interpretation:** Rich, expandable node content (metadata, status indicators, project-management-style cards, forms) is achievable through intended mechanisms (markup, foreignObject, or HTML overlay). This is configuration/custom-shape authoring rather than forking the library, but it is *not* zero-effort: each artefact type requires a custom element definition. The HTML-overlay path in particular requires manual position syncing between the SVG element and the DOM div, which reflects a pre-framework integration pattern.

### 2. Performance at 5k+ nodes

- **Observation:** A published stress test (open-source JointJS, no tuning) reports: 600 nodes → 647 DOM elements, smooth; 10,000 nodes → 1,156 DOM elements, smooth; 100 video cards → 6,000 DOM elements, smooth; 170 video cards + links → 11,000 DOM elements, "smooth, with a single dropped frame" (www.jointjs.com/blog/jointjs-performance-overview-testing-diagrams-with-100-000-nodes, 2026).
- **Observation:** The same article states that with optimization (virtual rendering + view management) a 50,000-card / 100,000-cell diagram "rendered as needed" and stayed "smooth without visible jank."
- **Observation:** A vendor comparison (Synergy Codes, pro-GoJS) reports JointJS+ loading 10,000 objects in "more than two seconds at about 20 fps … 4.8 seconds," versus GoJS "<2 seconds at 60 fps" (www.synergycodes.com/blog/jointjs-alternative-performance-comparison…). This is a biased source but is a concrete data point for the open-source-vs-canvas gap.
- **Observation:** A 2019 GitHub issue reports `graph.fromJSON()` with ~1,000 elements freezing the browser ~20s — but the maintainer's reply attributes this to misuse (Manhattan router and jumpover connector "not meant to be used with large graphs") and an invalid JSON; the recommended fixes are configuration (`async: true`, `sorting: APPROX`), not code changes (github.com/clientIO/joint/issues/1131).
- **Observation:** A maintainer Google Groups post claims applications rendering ">10,000 elements and links (80,000+ SVG DOM elements) very fast and with instant interaction" (groups.google.com/g/jointjs/c/dbdOrINRG8o).
- **Observation:** The same perf article notes SVG "may degrade if tens of thousands of elements are all rendered at the same time," and that the demo's workaround for far-zoom (showing thousands of elements at once) is to "automatically switch the rendering layer from SVG to canvas."
- **Interpretation:** 5k+ nodes is within JointJS's comfortable range *provided* virtualization is enabled. Naive full-graph rendering of tens of thousands of simultaneous DOM nodes degrades, and SVG specifically struggles when zoomed out to show everything at once. The degradation point is configuration-dependent, not a hard ceiling. The canvas-fallback workaround indicates the maintainers themselves acknowledge SVG's limits at extreme scale.

### 3. Incremental rendering

- **Observation:** The Paper `async: true` option enables asynchronous rendering in batches across animation frames, so adding large numbers of cells "doesn't block the UI" (docs.jointjs.com/api/dia/Paper, v4.x).
- **Observation:** The Paper `viewport()` callback determines per-view whether a view should be attached to the DOM; views for which it returns `false` are detached. Docs state this "dramatically improves rendering times of huge papers (thousands of views) and improves smoothness of user interaction" (docs.jointjs.com/api/dia/Paper).
- **Observation:** The `autoFreeze` option puts the paper into a frozen (idle) state when there are no scheduled view updates, "reducing CPU usage by stopping the rendering loop when it is not needed," and auto-exits on new updates (docs.jointjs.com/api/dia/Paper, v4.1+).
- **Observation:** In v4.2, view instantiation was deferred "until the moment the view is actually needed — for example, when it becomes visible on the screen or when a collapsed branch is expanded," and unneeded views "can also be disposed, freeing resources" (www.jointjs.com/blog/releasing-4-2, 2025-11). New `viewManagement` option and `disposeHiddenCellViews()`/`isCellVisible()` methods were added (v4.2.0 changelog).
- **Interpretation:** JointJS does *not* render the entire graph by default in a naive sense — it supports incremental, viewport-gated, and deferred rendering through `async`, `viewport()`, `autoFreeze`, and (v4.2+) `viewManagement`. These are opt-in options, not deep customization.

### 4. Hierarchical graphs

- **Observation:** JointJS provides first-class embedding: `cell.embed()` / `cell.unembed()`, plus `embeds` and `parent` model attributes forming a parent-child hierarchy (docs.jointjs.com/learn/features/diagram-basics/elements; resources.jointjs.com/tutorial/hierarchy).
- **Observation:** When a parent is moved, all embedded children move with it; links can also be embedded (their vertices move with the parent). `validateEmbedding()` on the Paper controls what may embed what (docs.jointjs.com/learn/features/containers-and-grouping).
- **Observation:** Rich hierarchy traversal API exists: `getParentCell()`, `getAncestors()`, `getEmbeddedCells({ deep, breadthFirst })`, `fitParent()`, `fitToChildren()`, `link.reparent()`, `graph.getCommonAncestor()`, `graph.transferCellEmbeds()` (same source).
- **Observation:** A "Hierarchical Diagrams" demo and a "Container Collapse/Expand" demo show inserting elements into containers, drop-to-embed, embedding validation, and collapse/expand (www.jointjs.com/demos/hierarchical-diagrams; /demos/container-collapse-expand).
- **Interpretation:** Hierarchical / compound structures are a native, well-supported capability — directly relevant to representing engineering artefacts nested within parent artefacts. No substantial customization is required; it is core functionality.

### 5. Virtualization

- **Observation:** Viewport-based virtualization is available in the open-source core via the Paper `viewport()` callback (hide/detach off-screen views) and, since v4.2, the `viewManagement` option plus deferred view instantiation and disposal (docs.jointjs.com/api/dia/Paper; v4.2.0 changelog).
- **Observation:** A turnkey `virtualRendering` boolean option exists on `ui.PaperScroller` — a UI component in the **commercial** `@joint/plus` (JointJS+) package (docs.jointjs.com/api/ui/PaperScroller/#virtualrendering; referenced in the 100k-nodes article). The article frames it as "as simple as flipping boolean attributes to true."
- **Interpretation:** The *building blocks* of viewport virtualization ship in the free core; the *convenience flag* (`virtualRendering`) is part of the paid JointJS+ `PaperScroller`. For an open-source-only deployment, virtualization is achievable but requires wiring the `viewport()`/`viewManagement` options yourself rather than flipping one switch. This is a meaningful open-source/commercial boundary for RQ1.

### 6. Maintenance activity

- **Observation:** Release cadence is active and recent. v4.0.0 (Jan 2024) removed jQuery/Backbone/Lodash; v4.1.x (2024); v4.2.0 (2025-11-10) added Layers API, deferred view management, ELK/MSAGL layouts; v4.2.5 (2026-06-11); v4.3 (2026-07) added tree-shaking, npm distribution for JointJS+, HTML magnets/highlighters, and the production `@joint/react` integration (github.com/clientIO/joint/releases; www.jointjs.com/blog/introducing-jointjs-4-3).
- **Observation:** The repository `clientIO/joint` shows ~5.2k–5.3k GitHub stars and ~880 forks; the org is client IO s.r.o., Prague, founded around the project; founders David Durman (CEO) and Roman Brückner (CTO) (github.com/clientIO/joint; www.client.io).
- **Observation:** JointJS (open source) is licensed MPL-2.0 and "does not include JointJS+" (www.jointjs.com/license). JointJS+ (formerly Rappid, rebranded 2022) is the commercial extension adding 40+ UI components, automatic layouts, and support, sold per-developer (www.jointjs.com/comparison; /blog/new-brand-to-be-revealed-jointjsplus-replaces-rappid; /pricing).
- **Observation:** `@joint/react` (open source) reached a production release alongside v4.3 (2026-07) (www.jointjs.com/blog/introducing-jointjs-for-react; npmjs.com/package/@joint/react).
- **Interpretation:** The project is actively maintained with corporate backing and a recent, accelerating release pace (4.0 → 4.3 within ~2.5 years, including a major React integration). The open-source core is healthy; the commercial tier funds development. Community size (5k stars) is moderate relative to React Flow or D3, but the project is long-lived and stable.

### 7. Composition with state management / lifecycle

- **Observation:** JointJS separates model and view: `dia.Graph` (the data model / single source of truth) and `dia.Paper` (the SVG renderer). The Graph emits change events; the Paper subscribes and renders (core architecture, docs.jointjs.com).
- **Observation:** `@joint/react` wraps the core: `GraphProvider` holds the `dia.Graph` instance; it uses `useSyncExternalStore` to listen to graph changes so "Diagram state is React state" (npmjs.com/package/@joint/react; react.jointjs.com). `renderElement` turns each node's `data` slice into a React component, and re-runs "ONLY when `data` changes, not when `position`/`size`/`angle` … update" — position/size are applied by JointJS's view layer without re-invoking React. A fully controlled mode is described as "under development."
- **Observation:** The classic HTML-overlay integration (custom `ElementView` syncing a DOM div to element position) is framework-agnostic and predates React; it is the documented way to embed interactive HTML in any host app (resources.jointjs.com/tutorials/html-elements.html).
- **Interpretation:** The Graph model is decoupled enough to be driven by an external store/lifecycle layer — `@joint/react` demonstrates this via `useSyncExternalStore`. However, the Paper owns its own render loop (`async` loop, `frozen`/`autoFreeze` states), so JointJS does *not* fully surrender the rendering lifecycle; it exposes hooks (freeze/unfreeze, viewport, viewManagement) rather than ceding control. Composition is clean at the model layer and workable at the view layer, but the Paper is not a pure controlled component by default.

### 8. Architecture heritage and modern-framework fit

- **Observation:** Pre-4.0 (i.e. 2013–2023), JointJS depended on **jQuery, Backbone, and Lodash** — an MVC-framework-era stack. v4.0 (Jan 2024) removed all three external dependencies, "absorbing a streamlined version of Backbone," and dropped bundled CSS (github.com/clientIO/joint/blob/master/CHANGELOG; /discussions/2476; /blog/introducing-version-4).
- **Observation:** Even post-4.0, internal `mvc.Model` / `mvc.View` / `mvc.Collection` namespaces and a Backbone-style change-event model (`change:attribute`, `on('change:...')`) remain (v4.0/v4.2 changelogs reference `mvc.View`, `mvc.Collection` using a Map; `dia.Cell` change events).
- **Observation:** The HTML-overlay pattern requires manually keeping a DOM div in sync with the SVG element's transform — a workaround born before reactive frameworks (resources.jointjs.com/tutorials/html-elements.html).
- **Interpretation:** The *dependency* heritage (jQuery/Backbone) was excised in v4.0, so modern bundle/tooling integration is no longer blocked by those assumptions. But the *mental model* still reflects an MVC/event-emitter era: you subscribe to model change events rather than holding a reactive snapshot, unless you adopt `@joint/react`. For a React-centric execution engine, the native fit is "good with the React wrapper, acceptable without it." The architecture is mature and stable rather than modern-reactive, which is a soft (not blocking) conflict with framework-based development.

## Findings

1. **Expandable node content:** Achievable via intended mechanisms (SVG `markup`/`attrs`, content-driven sizing, `foreignObject`, or HTML overlay). Each artefact type needs a custom element definition — authoring effort, not library forking. The HTML-overlay path needs manual position syncing.
2. **Performance at 5k+:** Comfortable at 5k–11k DOM nodes with no tuning; 100k cells feasible with virtualization. SVG degrades when *all* nodes are visible at once (e.g. far zoom); the maintainers' own workaround is an SVG→canvas switch.
3. **Incremental rendering:** Supported via `async`, `viewport()`, `autoFreeze`, and (v4.2+) `viewManagement` with deferred instantiation/disposal. Opt-in options, not deep customization.
4. **Hierarchical graphs:** First-class via embedding (`embed`/`embeds`/`parent`), traversal API, and collapse/expand demos. Directly supports nested engineering artefacts.
5. **Virtualization:** Core provides `viewport()` + `viewManagement`; the one-flag `virtualRendering` convenience is in the commercial `PaperScroller`. Open-source-only deployments can virtualize but must wire it themselves.
6. **Maintenance:** Actively maintained, corporate-backed (client IO s.r.o.), recent accelerating cadence (4.0→4.3 in ~2.5 yrs), MPL-2.0 open core + commercial JointJS+ tier. Moderate community (~5.2k stars).
7. **Composition:** Graph model is decoupled and drivable externally (`@joint/react` uses `useSyncExternalStore`); Paper owns its render loop but exposes freeze/viewport/viewManagement hooks. Clean at model layer, workable at view layer, not a pure controlled component by default.
8. **Architecture heritage:** jQuery/Backbone/Lodash removed in v4.0, but a Backbone-style event model and the HTML-overlay sync pattern remain. Mature/stable rather than modern-reactive; soft conflict with React-centric development, mitigated by `@joint/react`.

**Answer to RQ1 (JointJS):** JointJS *can* represent engineering artefacts and their relationships without substantial customization for the core requirements — hierarchical nesting, rich/expandable node content, and 5k+ scale are all supported through intended, documented mechanisms. The principal caveats are: (a) rich interactive node content requires per-type custom element authoring; (b) 5k+ performance depends on enabling virtualization options (configuration, not forking); (c) the most convenient virtualization flag is commercial; and (d) the MVC/event-emitter heritage is a soft mismatch with reactive frameworks unless the `@joint/react` wrapper is adopted. None of these constitute "substantial customization" of the library itself.

## Rejected options

- **Canvas-only rendering assumption:** Considered whether JointJS's SVG base fundamentally disqualifies it at 5k+. Rejected as too strong — evidence shows 11k DOM nodes smooth untuned and 100k with virtualization; degradation is at the "all-visible-at-once" extreme, addressable via viewport virtualization and the documented SVG→canvas fallback.
- **Treating JointJS+ features as open-source:** Initially noted "virtual rendering" as a core feature; corrected after finding `virtualRendering` lives on the commercial `ui.PaperScroller`, while core offers `viewport()`/`viewManagement`. The open-source/commercial boundary is preserved in the findings.
- **Assuming jQuery dependency still blocks modern tooling:** Rejected — v4.0 (2024) removed jQuery/Backbone/Lodash; the blocker is gone, leaving only a stylistic (event-model) heritage.

## Unknowns

- **Exact 5k-node FPS under typical engineering-artefact node complexity** (heavy `foreignObject`/HTML content per node) is not benchmarked in published material; the 11k-node test used relatively light cards.
- **Behaviour of `foreignObject` HTML content under the `viewport()` virtualization** (detaching/reattaching DOM, event re-binding) is not explicitly documented; potential interaction cost unknown.
- **Maturity/stability of `@joint/react`** — it reached production release only with v4.3 (2026-07); long-term API stability is unproven at time of writing.
- **Real-world maintenance burden of the HTML-overlay sync pattern** at scale (manual position syncing per node) is not quantified.
- **Open-issue/bug backlog health** was not directly measured (issue counts, median close time); only release cadence and stars were observed.

## Confidence

**Medium-High.**

- High confidence on: hierarchical support (explicit API + demos), incremental rendering options (documented in Paper API), maintenance cadence and licensing (release notes, repo metadata), and the v4.0 dependency removal (changelog).
- Medium confidence on: real-world 5k+ performance with *complex* artefact nodes (published benchmarks use light cards; SVG→canvas fallback is the maintainers' own admission of a limit), and on the open-source virtualization boundary (core provides building blocks but the turnkey flag is commercial).
- The core RQ1 question — "without substantial customization" — is answered with reasonable confidence: the required capabilities exist as intended, documented mechanisms; the qualifications are configuration/authoring effort and one commercial-feature boundary, not library modification.

## References

- JointJS performance overview (100k nodes): https://www.jointjs.com/blog/jointjs-performance-overview-testing-diagrams-with-100-000-nodes
- HTML inside shapes (foreignObject): https://docs.jointjs.com/learn/features/customizing-shapes/html-inside-shapes/
- Content-driven element tutorial: https://resources.jointjs.com/tutorial/content-driven-element
- HTML elements (overlay) tutorial: https://resources.jointjs.com/tutorials/html-elements.html
- Containers & Grouping (embedding/hierarchy): https://docs.jointjs.com/learn/features/containers-and-grouping/
- Hierarchy tutorial: https://resources.jointjs.com/tutorial/hierarchy
- Container Collapse/Expand demo: https://www.jointjs.com/demos/container-collapse-expand
- Hierarchical Diagrams demo: https://www.jointjs.com/demos/hierarchical-diagrams
- Paper API (async, viewport, autoFreeze, viewManagement, frozen): https://docs.jointjs.com/api/dia/Paper/
- PaperScroller virtualRendering (commercial): https://docs.jointjs.com/api/ui/PaperScroller/#virtualrendering
- Release v4.2.0 changelog: https://github.com/clientIO/joint/releases/tag/v4.2.0
- Releasing 4.2 (deferred view management): https://www.jointjs.com/blog/releasing-4-2
- Introducing JointJS 4.3 / React: https://www.jointjs.com/blog/introducing-jointjs-4-3 ; https://www.jointjs.com/blog/introducing-jointjs-for-react
- @joint/react npm: https://www.npmjs.com/package/@joint/react
- JointJS React integration docs: https://docs.jointjs.com/learn/integration/react/
- Introducing version 4 (dependency-free): https://www.jointjs.com/blog/introducing-version-4
- CHANGELOG (jQuery/Backbone/Lodash removal): https://github.com/clientIO/joint/blob/master/CHANGELOG
- GitHub repo (stars/forks): https://github.com/clientIO/joint
- Licensing (MPL-2.0, JointJS vs JointJS+): https://www.jointjs.com/license
- JointJS+ vs Rappid rebrand: https://www.jointjs.com/blog/new-brand-to-be-revealed-jointjsplus-replaces-rappid
- JointJS+ comparison/pricing: https://www.jointjs.com/comparison ; https://www.jointjs.com/pricing
- Synergy Codes GoJS vs JointJS+ perf comparison (biased source): https://www.synergycodes.com/blog/jointjs-alternative-performance-comparison-on-the-interactive-diagram-with-thousands-of-objects-using-gojs
- GitHub issue #1131 (large-JSON freeze, maintainer reply): https://github.com/clientIO/joint/issues/1131
- SVG vs Canvas (JointJS rationale): https://www.jointjs.com/blog/svg-versus-canvas
