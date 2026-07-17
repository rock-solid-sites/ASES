# RQ1 — Cytoscape.js

## Question

Can existing graph frameworks represent engineering artefacts and their relationships without substantial customization? This report investigates Cytoscape.js specifically: can it represent engineering artefacts (nodes with rich, expandable content, metadata, status indicators), scale to 5k+ nodes, render incrementally, model hierarchical structures, virtualize the viewport, and compose cleanly with a separate state-management/lifecycle layer — and does its bioinformatics heritage impose conflicting assumptions?

## Scope

**Investigated (via official docs, source-adjacent material, and community reports):**

- Node content customization: canvas-based styling vs. HTML overlay approaches.
- Performance characteristics at 5k+ nodes and documented optimization strategies.
- Incremental / viewport-based rendering and lazy-loading capabilities.
- Hierarchical graph support (compound nodes, parent-child relationships).
- Viewport virtualization.
- Maintenance activity (release cadence, open issues, community size).
- Composition with external state management / application lifecycle.
- Bioinformatics heritage and its assumptions.

**Excluded:**

- Hands-on benchmarking (no local execution; claims rely on published perf pages, maintainer statements, and user reports).
- Deep source-code audit of the renderer internals beyond what is documented.
- Comparison against other frameworks (that is the remit of sibling RQ1 reports, not this one).
- React/Vue/Angular integration specifics beyond the general composition question.

## Evidence

### 1. Expandable node content

- **Observation:** Cytoscape.js nodes are drawn on a `<canvas>` (or WebGL) and are styled declaratively via a stylesheet. Native node visuals include shape, background-color, multiple `background-image`s (up to several layered images), `background-image-opacity`, pie-chart properties, gradients, borders, and text labels with wrapping/ellipsis (`js.cytoscape.org` style docs; CX2 Visual Styles spec, cytoscape.org/cx).
- **Observation:** Rich, interactive HTML content is provided through *extensions that overlay the canvas*, not through native canvas drawing:
  - `cytoscape-popper` (first-party, v4.0.1 published Aug 2024, MIT) positions arbitrary DOM `<div>`s relative to graph elements for tooltips/overlays (github.com/cytoscape/cytoscape.js-popper).
  - `cytoscape-node-html-label` (community, ~108 GitHub stars, MIT) renders arbitrary HTML templates *inside* nodes via `cy.nodeHtmlLabel([{ tpl: data => '...' }])`, with an `enablePointerEvents` flag for clickable content (github.com/kaluginserg/cytoscape-node-html-label).
  - `cytoscape.js-layers` (community) provides SVG/canvas/HTML layer abstractions on top of the core renderer (github.com/sgratzl/cytoscape.js-layers).
- **Observation:** "Expandable" node behaviour (showing/hiding children or detail) is achieved by manipulating the graph model (`cy.add`/`cy.remove`, `eles.move()`) or via the `cytoscape.js-view-utilities` extension (`hide`/`show`/`showHiddenNeighbors`) — there is no native "expandable node widget" (Stack Overflow "Expand nodes on click", 2020; view-utilities README).
- **Interpretation:** A project-management-style view, metadata panel, or status indicators *can* be rendered on/around nodes using the HTML-overlay extensions, but they live in a separate DOM layer that must be kept in sync with the canvas (position, zoom, show/hide). The canvas node itself remains a styled primitive; deep interactive content is an overlay concern, not a first-class node capability.

### 2. Performance at 5k+ nodes

- **Observation:** The official performance test page (`cytoscape.github.io/js-perf`) ships datasets of 6,000 (`wgcna-modules-child-child`), 6,400 (`tcga-colorectal-cancer`), 10,000 (`nb-groups`), and 20,000 (`nb-groups`) elements, indicating the library is exercised at and beyond 5k nodes (cytoscape/js-perf repo).
- **Observation:** The documentation states performance is "O(n) for most operations" and lists degradation factors: graph size, rich visual styles (gradients, dashed lines, multiple background images), edge rendering (bezier curves, arrows), display density (Retina `devicePixelRatio=2` → 4× pixels), and canvas area (`js.cytoscape.org` performance section; DeepWiki performance-optimization doc).
- **Observation:** A user report (Stack Overflow, 2018) describes ~5,000 nodes + ~5,000 edges *without* preset positions taking >15s for an Euler layout, after which the browser became unresponsive. Maintainer guidance points to the performance-optimization section rather than a fix.
- **Observation:** Documented optimization strategies include: use `haystack` (straight) edges, solid (not dashed/dotted) edges, omit arrows, use opaque edges, simplify node shapes (ellipse/rectangle fastest; star/custom-polygon slowest), avoid compound/edge selectors, set `pixelRatio: 1`, `hideEdgesOnViewport: true`, `textureOnViewport: true`, limit simultaneous `overlay-opacity`, and recycle large instances instead of `cy.destroy()` (`js.cytoscape.org`; DeepWiki).
- **Observation:** A WebGL renderer preview shipped in v3.31 (Jan 2025 blog post) uses GPU acceleration, texture atlases, and batching (max 2048 elements/batch) to improve frame rate on large networks; it is explicitly described as a "preview" and as a mode of the canvas renderer, reusing canvas drawing/event code (blog.js.cytoscape.org/2025/01/13/webgl-preview; DeepWiki WebGL Renderer).
- **Interpretation:** 5k nodes is within the tested envelope, but acceptable interactivity depends on applying the documented optimizations and, for layout, on supplying preset positions. The dominant cost at 5k+ is often *layout* (force-directed/physics simulation) rather than raw rendering; the WebGL renderer addresses rendering FPS but was still preview-stage as of early 2025.

### 3. Incremental rendering

- **Observation:** The canvas renderer draws all graph elements back-to-front each frame according to z-order; it is single-threaded JavaScript (WebGL preview blog, 2025).
- **Observation:** There is **no documented viewport-based virtualization** (culling of off-screen elements) in the Cytoscape.js core. The Level-of-Detail (LOD) behaviour that hides labels above ~200 visible nodes and switches to coarse LOD above ~4000 rendered elements is a feature of the **Cytoscape desktop application**, not Cytoscape.js (manual.cytoscape.org Rendering Engine; contrast with the .js docs which contain no equivalent LOD section).
- **Observation:** Lazy-loading / incremental population is performed by the *application* through model manipulation: adding/removing elements, or the `view-utilities` extension's hide/show, or expand-on-click patterns (Stack Overflow "Expand nodes on click", 2020).
- **Interpretation:** Cytoscape.js renders the full in-memory model each frame and does not natively virtualize by viewport. Incremental rendering must be implemented at the application layer (show/hide, add/remove, or external paging).

### 4. Hierarchical graphs

- **Observation:** Compound nodes are a native feature: a node contains child nodes via the `parent` field in `data`; the parent's dimensions are inferred from its descendants (it has no independent position/size). API includes `node.isParent()`, `node.parent()`, `node.children()`, `node.ancestors()`, and selectors `:parent`, `:child`, `:orphan`, `>` (child), ` ` (descendant) (`js.cytoscape.org` compound-nodes section).
- **Observation:** The compound model is a **disjoint hierarchy** — a node may have only **one** direct parent. Multiple-parent nodes are explicitly *not* supported (Stack Overflow "Compound nodes with multiple parent", 2018, accepted answer; corroborated by the docs' single-`parent`-field model).
- **Observation:** Several layouts support compounds: `breadthfirst`, `dagre` (DAG), and `cose-bilkent`. A long-standing request to run *different* layouts inside vs. outside compound nodes remains unmet (issue #2183, open/recurring 2018–2023).
- **Interpretation:** Nested/hierarchical engineering structures (e.g., system → subsystem → component) map cleanly onto compound nodes, *provided* the hierarchy is tree-shaped (single parent). Cross-cutting containment (an artefact belonging to two parents) is not representable natively and would require a modelling workaround.

### 5. Virtualization

- **Observation:** As established in §3, Cytoscape.js core has no viewport-based virtualization; the desktop LOD mechanism does not exist in .js. The WebGL renderer batches draw calls but still processes the full element set.
- **Interpretation:** Viewport virtualization is **not** a built-in capability and would have to be built by the application (e.g., show/hide by viewport, or external data paging). This is a gap relative to the RQ's "incremental rendering / virtualization" expectation.

### 6. Maintenance activity

- **Observation:** Latest tagged releases: v3.34.0 (2025-06-02) and v3.33.4 (2025-05-19) on GitHub; npm shows v3.34.0 "published 12 days ago" relative to the search snapshot (github.com/cytoscape/cytoscape.js/releases; npmjs.com/package/cytoscape).
- **Observation:** The README states "Feature releases are made monthly, while patch releases are made weekly" and the factsheet repeats "Weekly patch release cadence / Monthly feature release cadence" (`js.cytoscape.org`; GitHub README).
- **Observation:** Repository metrics: ~11.1k GitHub stars, ~1.7k forks, 11 open issues, 2 open PRs, active Discussions tab (github.com/cytoscape/cytoscape.js). npm: 268 published versions, 0 dependencies, ~438–445 dependents (npmjs.com/package/cytoscape; libraries.io).
- **Observation:** The project was published in *Oxford Bioinformatics* (2016, 32(2):309–311; 2023 update, 39(1):btad031) and originated at the University of Toronto Donnelly Centre / Bader lab (README; citation section).
- **Interpretation:** Cytoscape.js is actively maintained with a recent release cadence, a large and healthy community, and a stable dependency footprint. Maintenance risk is low.

### 7. Composition

- **Observation:** Cytoscape.js is instantiated as a library against a host-provided container `<div>` (`cytoscape({ container, elements, style, layout })`) and is destroyed by the host (`cy.destroy()`). It exposes its own event model (`cy.on('tap', 'node', ...)`) and full JSON serialization (`cy.json()` / `cy.add(json)`) (`js.cytoscape.org` Getting Started; README).
- **Observation:** It is routinely embedded inside larger frameworks (React/Vue/Angular wrappers exist in the community) and used headlessly on Node.js for graph analysis (README; factsheet).
- **Observation:** The graph model lives *inside* the Cytoscape instance; the host application is responsible for its own state management and for bridging changes into/out of the instance via `add`/`remove`/`update`/`json` (implied by the API surface and the "optional renderer" framing in the README: "contains a graph theory model and an optional renderer").
- **Interpretation:** Cytoscape.js does **not** assume ownership of the full application lifecycle — it is a rendering + graph-theory library that composes into a host app. The integration cost is the bidirectional sync between the host's state store and Cytoscape's internal model; this is a known, bounded integration task rather than a lifecycle conflict.

### Bioinformatics heritage — potential conflicts

- **Observation:** Cytoscape.js is the successor to Cytoscape Web and a JS port of the Cytoscape desktop bioinformatics tool; its docs frame it around "biological data or social networks" and it is authored by a bioinformatics lab (README; `js.cytoscape.org` About).
- **Observation:** The compound-graph model is a *disjoint* (single-parent) hierarchy — a model that fits biological pathway/container containment but not general DAGs (see §4).
- **Observation:** The desktop product's style system is oriented toward biological visualisation (pie charts / bar charts / heatmaps as "custom graphics" mapped from expression columns; manual.cytoscape.org Styles). In .js, pie-chart node properties exist but a maintainer note states they "will be removed in v4" and recommends generating chart images externally (issue #2671).
- **Observation:** The core data model is generic graph theory: nodes/edges carry arbitrary `data` key–value attributes and arbitrary `classes`; there is no hardcoded biology schema (factsheet; style/data docs).
- **Interpretation:** The heritage manifests mainly in (a) framing/marketing language, (b) the single-parent compound limitation, and (c) bioinformatics-flavoured style conveniences. The underlying model is domain-agnostic and imposes no content-level bioinformatics constraint on engineering artefacts. The principal heritage-derived limitation relevant to engineering artefacts is the disjoint-hierarchy compound model; the lack of built-in PM/status/workflow semantics is expected of any generic graph library and is an app-layer concern, not a bioinformatics assumption.

## Findings

1. **Node content:** Rich, expandable, interactive node content is achievable via HTML-overlay extensions (`cytoscape-popper`, `cytoscape-node-html-label`, `cytoscape.js-layers`), but it is a DOM overlay layer kept in sync with the canvas — not native node content. Native canvas node styling is limited to shapes, images, pie charts, gradients, and text.
2. **Performance:** 5k+ nodes is within the tested range, but smooth interactivity requires applying documented optimizations and (for layout) preset positions. The WebGL renderer (preview since v3.31) improves rendering FPS on large graphs but was not yet stable as of early 2025. Layout, not rendering, is typically the bottleneck at 5k+.
3. **Incremental rendering / virtualization:** Not provided by core. The renderer draws the full in-memory model each frame; the desktop LOD feature does not exist in .js. Incremental/lazy behaviour must be implemented at the application layer.
4. **Hierarchy:** Compound nodes give first-class nested/hierarchical support, but only as a tree (single parent per node). Multi-parent containment is unsupported natively.
5. **Maintenance:** Actively maintained (monthly feature / weekly patch releases; v3.34.0 in mid-2025), large community (~11k stars), zero runtime dependencies, broad production adoption.
6. **Composition:** Composes cleanly as a library; does not own app lifecycle. Integration cost is the bounded sync between host state and Cytoscape's internal model.
7. **Heritage:** Domain-agnostic at the data level; the only heritage-derived modelling constraint relevant here is the disjoint (single-parent) compound hierarchy. No bioinformatics content schema is imposed on artefacts.

**Answer to RQ1 (for Cytoscape.js):** Engineering artefacts and relationships *can* be represented, but **not without substantial customization** in two specific areas — (a) rich/expandable node content requires HTML-overlay extensions and ongoing canvas↔DOM synchronisation, and (b) incremental rendering / viewport virtualization and multi-parent hierarchy are not native and must be built by the application. The base graph model, styling, hierarchy (tree-shaped), performance envelope at 5k+, and composition story are adequate with only light customization.

## Rejected options

- **Relying on native canvas node styling for rich PM views:** rejected — canvas primitives (shapes/images/pie/text) cannot host interactive widgets, metadata forms, or status dashboards; HTML overlays are required.
- **Assuming desktop LOD applies to .js:** rejected — the Level-of-Detail auto-simplification is a Cytoscape *desktop* feature; it is absent from Cytoscape.js and must not be counted as available virtualization.
- **Treating WebGL renderer as production-ready for the 5k+ requirement:** rejected for confidence purposes — it is documented as a "preview" (v3.31, Jan 2025) and its stability/feature parity at the time of writing is unverified here.
- **Modelling multi-parent engineering containment via compound nodes:** rejected — compound nodes enforce a single parent; a DAG-of-parents requires an application-level modelling workaround.

## Unknowns

- Exact, reproducible FPS / layout-time numbers for 5k+ engineering-style graphs on target hardware (no local benchmark run; figures are from a 2018 user report and the official perf datasets, which are biology/social networks).
- Stability and feature parity of the WebGL renderer as of the latest release (preview status noted; not re-verified against v3.34).
- Real-world behaviour of HTML-overlay extensions (`cytoscape-node-html-label`) at 5k+ nodes regarding DOM-node count and sync overhead (the extension claims "optimised for high number of nodes" but no quantified threshold was found).
- Whether the host application's state-sync overhead (add/remove/update per change) becomes the dominant cost at 5k+ nodes under frequent updates — not measured here.
- Precise timeline/impact of the planned removal of pie-chart node properties in v4 (issue #2671) on any chart-in-node approach.

## Confidence

**Medium.**

Justification: The structural capabilities (compound nodes, canvas styling, HTML-overlay extensions, composition model, maintenance status, disjoint-hierarchy limitation, absence of native virtualization) are well evidenced by official documentation, the source repo, and first-/third-party extensions, and are stated with corresponding confidence. The performance characterisation at 5k+ is evidenced but rests partly on a single dated user report and official datasets that are not engineering-artefact graphs; the WebGL renderer's production readiness is explicitly preview-stage. Therefore the *capability* conclusions are high-confidence, while the *quantitative performance* and *large-scale overlay* conclusions are medium-confidence. No implementation is recommended.

## References

- Cytoscape.js official documentation — https://js.cytoscape.org (factsheet, compound-nodes, style/background-image, performance sections; Getting Started; About)
- Cytoscape.js GitHub repository — https://github.com/cytoscape/cytoscape.js (releases v3.34.0 / v3.33.4; README cadence; star/fork/issue counts)
- npm package `cytoscape` — https://www.npmjs.com/package/cytoscape (v3.34.0, 0 deps, ~438–445 dependents, 268 versions)
- Cytoscape.js performance test page / repo — https://cytoscape.github.io/js-perf and https://github.com/cytoscape/js-perf (datasets: 6k, 6.4k, 10k, 20k elements)
- DeepWiki performance & WebGL docs — https://deepwiki.com/cytoscape/cytoscape.js/8-performance-optimization and /4.2-webgl-renderer
- WebGL Renderer Preview (blog) — https://blog.js.cytoscape.org/2025/01/13/webgl-preview/
- cytoscape-popper (first-party HTML overlay) — https://github.com/cytoscape/cytoscape.js-popper (v4.0.1, Aug 2024)
- cytoscape-node-html-label (community HTML-in-node) — https://github.com/kaluginserg/cytoscape-node-html-label (~108 stars)
- cytoscape.js-layers (SVG/canvas/HTML layers) — https://github.com/sgratzl/cytoscape.js-layers
- cytoscape.js-view-utilities (hide/show) — https://github.com/iVis-at-Bilkent/cytoscape.js-view-utilities
- Stack Overflow: "Performance and layouts of Cytoscape.js" (5k nodes, >15s Euler) — https://stackoverflow.com/questions/50344455/
- Stack Overflow: "Compound nodes with multiple parent" (single-parent limitation) — https://stackoverflow.com/questions/53361832/
- Stack Overflow: "Expand nodes on click" (overlay/hide-show approach) — https://stackoverflow.com/questions/64351388/
- Cytoscape desktop Rendering Engine (LOD — desktop only, not .js) — https://manual.cytoscape.org/en/stable/Rendering_Engine.html
- Cytoscape desktop Styles (bio-flavoured charts/custom graphics) — https://manual.cytoscape.org/en/stable/Styles.html
- Pie-chart removal note (v4) — Cytoscape.js issue #2671 — https://github.com/cytoscape/cytoscape.js/issues/2671
- Different-layout-within-compound request — issue #2183 — https://github.com/cytoscape/cytoscape.js/issues/2183
- Citation: Franz M, Lopes CT, et al. "Cytoscape.js: a graph theory library for visualisation and analysis." *Bioinformatics* 2016;32(2):309–311 (and 2023 update 39(1):btad031).
