---

title: Combined Static Verification Server — Session Retrospective
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Finding
canonical_repository: edases
depends_on:

* Documentation Standard

consumed_by:

* Future agent sessions
* #168

related_documents: []

supersedes: []

## last_updated: 2026-08-04

> Provenance: Primary source: tripn-astro docs/combined-verify-server-retrospective.md (2026-08-04). Intake: ASES #168 — live-localhost verification convention.

# Combined Static Verification Server — Session Retrospective

## What we were trying to do

We needed to visually verify the Properties dropdown work across all 5 TripN sites (Landing, OG, Pink Bubble, Chill Zone, Seaside) in a browser. The initial approach used `astro dev` per site, but that repeatedly failed: dev-server HMR websockets broke on operator disconnects, the base-path URL structure confused the browser (e.g. the OG site serves at /original/, not /, so opening the root showed an Astro 404 page that looked blank), and every reconnect risked a stale tab. We spent more time fighting the server than reviewing code.

## What problems we encountered

1. `astro dev` + HMR is fragile across disconnects — the operator got disconnected multiple times and the tab stopped loading even though the process was alive.
2. Base-path confusion — each site deploys under a subfolder (/original/, /pink-bubble/, /chill-zone/, /seaside/), so the dev server only serves a site at its base path; the root URL shows a near-black 404 page that reads as "blank".
3. The combined build (`scripts/build-combined.mjs`) was initially mis-built or not assembled — landing-page/dist/ contained only the landing output, so /original/ 404'd.
4. The Bash tool kills background processes on timeout — bare `command &` doesn't survive a tool call, so naive dev-server launches died (documented in the astro-dev-server-persistence and bash-tool-background-process-gotcha knowledge pages).

## What options were considered

1. `astro dev` per site (tried first) — HMR, but fragile across disconnects and base-path confusion.
2. `astro preview` (per site) — serves the built dist, more stable than dev, no HMR websocket, but still one site at a time and base-path matters.
3. Combined static serve (chosen) — run `scripts/build-combined.mjs` once to assemble all 5 sites into landing-page/dist/<subpath>/, then serve that directory with a plain static server (`python3 -m http.server`) in a tmux session. This gives all sites at their real production URLs from one server, no HMR, no base-path guessing, and survives disconnects.

## What we ended up doing and why

We chose the combined static serve. The operator merges all dropdown feature branches into a verification branch (feature/verify-nav-dropdowns) — the merge must be done by the operator because the crosslink guard hard-blocks git mutations (checkout/merge/push) for all agents; read-only git is allowed. Then a Task-tool builder runs `node scripts/build-combined.mjs` (which builds each of the 5 sites and assembles them into landing-page/dist/<subpath>/), restarts a tmux session `combined-verify` serving that directory on port 8080 via `python3 -m http.server`, and verifies all 5 subpaths return 200 plus the dropdown HTML is present. The operator then clicks through http://localhost:8080/ and the subpaths, delivering per-site design notes; we batch those changes, the operator commits them (agents can commit with an active issue; push is operator-only), and the builder rebuilds once for the next verification pass.

Why: it is production-faithful (real subpath URLs), stable across disconnects (no HMR), and gives one URL to remember instead of fighting per-site base paths. Trade-offs: each change round requires a full combined rebuild (~30s), and the git integration step (merging branches) must be done by the operator because of the guard.

## Key lessons

- Use tmux (not bare backgrounding) for any long-lived server process.
- Check the base path — a site served at the wrong URL can look like a blank 404.
- Verify the combined build actually assembled all subfolders before serving.
- The static-serve approach eliminated the reconnect/base-path failures that plagued `astro dev`.
