# Findings: Evidence from the Beds24 Booking Plugin Documentation

**Date:** 2026-06-23
**Evaluator:** OpenCode (Principal/Orchestrator Agent)
**Source / Location:** `/home/claude-code/beds24-booking-plugin/` and `/home/claude-code/projects/tripn-astro/vendor/beds24-astro-module/` (Analysis of WordPress legacy and modern Astro serverless codebases)
**Confidence Level:** Validated (derived from extensive documentation review, verified historical session logs, and live code audits)

---

## 1. Overview

The Beds24 Booking Plugin began as a real-world, production-grade WordPress plugin that implemented a decoupled booking flow, separating **discovery** (rendered directly via WordPress using cached Beds24 API v2 data) from **transactions** (rendered in an embedded Beds24 iframe). 

Following the WordPress implementation, the project completed a **total architectural pivot to Astro** (`beds24-astro-module` integration), converting the plugin into a highly optimized, statically generated, and serverless edge-computed web application deployed live on Cloudflare Pages and Workers. 

Analyzing these codebases across both phases yields critical empirical evidence regarding multi-layer alignment and progressive externalization in AI-assisted software engineering systems.

---

## 2. Supporting Observations (Evidence)

*   **OBS-01 — Discovery-Transaction Boundary (Principal Decision):** The plugin limits its scope to search, room results, card rendering, and cart compilation, handing off actual booking and payments to Beds24's secure, iframe-rendered `booking3.php` to completely avoid PCI/Stripe scope. (Source: `docs/architecture.md`, `docs/architecture-pivot-decision.md`) `[verified-directly]`
*   **OBS-02 — Multi-Layer Token Resolution (Knowledge Layer):** Style tokens are resolved across three layers: `theme.json` (primary theme) → plugin settings (admin UI overrides) → built-in fallback defaults. These are emitted as `--beds24-*` CSS custom properties on site and as compiled CSS for the iframe. (Source: `docs/styling-contract.md`, `plugin/includes/theme-json-reader.php`) `[verified-directly]`
*   **OBS-03 — Undocumented API Discovery (Verification Output):** The multi-room URL parameters (`sr1-{id}`) and (`naa1-1-{id}`) used to prepopulate Beds24's cart are undocumented in the official wiki; they were discovered through empirical browser-session inspection and validated in Session 13. (Source: `docs/reference/beds24-api-v2/README.md`, `docs/session-handoff-13.md`) `[verified-directly]`
*   **OBS-04 — Knowledge Portability over Code (Historical Fact):** The predecessor project's code was completely discarded during the pivot to WordPress, but its *entire database of rules and platform constraints* (the 27 retrospective entries) was ported intact and served as the design basis for the new plugin. (Source: `docs/retrospective.md`, `docs/session-handoff-1.md`) `[verified-directly]`
*   **OBS-05 — Five-Level Verification Hierarchy (Verification Rule):** The retrospective codifies a rigorous, hierarchical verification protocol: file existence → persistence confirmation → reference chain loading → computed behavioral correctness → cross-document consistency checks. (Source: `docs/retrospective.md`) `[verified-directly]`
*   **OBS-06 — Silent Platform Failure (Platform Constraint):** The Beds24 `customhead` injection field silently truncates saves at 2,000 characters without displaying DOM errors, a failure discovered through computed CSS style verification in Session 25. (Source: `docs/retrospective.md`, `docs/session-handoff-25.md`) `[verified-directly]`
*   **OBS-07 — "Write Up to the Gate" Security (Process Rule):** The protocol for managing API keys and secrets requires agents to write code and commands up to the gating execution point, leaving the actual secret substitution and execution to the human operator. (Source: `docs/retrospective.md`, `user/code-session-prompts/SKILL.md`) `[verified-directly]`
*   **OBS-08 — Serverless Cold-Start & Credit Cache Hierarchy (Execution Layer):** To optimize response latency and preserve Beds24 API rate limit credits (100 credits per 5 mins), the Astro module implements a three-tier cache hierarchy: (1) In-memory `Map` per Worker instance, (2) Cloudflare KV cross-instance caching, and (3) live Beds24 API v2 calls on complete miss. (Source: `vendor/beds24-astro-module/src/lib/beds24-client.ts`) `[verified-directly]`
*   **OBS-09 — Structural Schema Validation at Build-time (Verification Layer):** The Astro module programmatically enforces strict schemas, tag presets, image dimension limits, and Unicode grapheme cluster counts (using `Intl.Segmenter` to ensure emoji icons are single characters) using a local TypeScript/Zod validation script during builds. (Source: `vendor/beds24-astro-module/scripts/validate.ts`) `[verified-directly]`
*   **OBS-10 — Decoupled Content Declarative Model (Knowledge Layer):** Content-management was completely decoupled from WordPress MySQL by externalizing all room descriptions, orders, photo paths, and tags into versioned, flat, declarative JSON files (`rooms.json`) in the project root. (Source: `vendor/beds24-astro-module/content/chill-zone/rooms.json`) `[verified-directly]`

---

## 3. Interpreted Findings

### FIN-01 — The Knowledge Layer is more durable and valuable than the Execution Layer
*Confidence: Validated*
*Supporting Evidence: OBS-04*
The complete disposal of the predecessor project's codebase alongside the 100% preservation and utility of its retrospective knowledge base proves that **structured system knowledge is a more durable asset than functional code**. In AI-assisted workflows, code can be regenerated in minutes once the exact system constraints (such as platform quirks and CSS selectors) are codified. The knowledge base is the real intellectual IP.

### FIN-02 — Multi-layer token resolution demonstrates Progressive Externalization (AH-002)
*Confidence: Validated*
*Supporting Evidence: OBS-02, OBS-10*
The styling contract and `rooms.json` map dynamic, user-configured design assets across a progressive execution boundary: reading external theme tokens, then overriding them via local settings, and compiling them. In the Astro phase, content is fully externalized into structured JSON, keeping the rendering layer entirely decoupled and stateless.

### FIN-03 — Explicit anti-scope covenants protect the Capability and Principal Layers
*Confidence: Supported*
*Supporting Evidence: OBS-01*
Explicitly documenting what a system **does not do** (the anti-scope covenants) is a load-bearing architectural constraint. In the Beds24 plugin, refusing to touch credit card or booking-write APIs permanently bounded the system's security, compliance, and testing surface, preventing capability creep.

### FIN-04 — Silent failures in third-party environments necessitate computed-style verification
*Confidence: Validated*
*Supporting Evidence: OBS-05, OBS-06*
Because SaaS platforms and hosting providers (like Beds24 or aaPanel) fail silently (e.g., truncating headers, blocking symlinks via `open_basedir`), verification must extend to *computed behavior* (testing computed CSS variables, checking actual HTTP response payloads) rather than relying on write confirmation.

### FIN-05 — "Write up to the gate" secures multi-agent and human-in-the-loop task routing
*Confidence: Supported*
*Supporting Evidence: OBS-07*
Stopping execution precisely before a secret or critical boundary is crossed and passing a copy-paste instruction to the operator enables secure collaboration in trust-bounded environments. This is a highly effective, low-overhead pattern for human-in-the-loop validation in the Capability Layer.

### FIN-06 — Serverless edge execution completes progressive externalization of organizations
*Confidence: Validated*
*Supporting Evidence: OBS-08, OBS-10*
Decoupling the discovery layer from both database bloat (WordPress MySQL replaced by static JSON and Cloudflare KV) and execution servers (PHP replaced by serverless Cloudflare Pages/Workers) eliminates performance bottleneck, database bloat, and server maintenance overhead, showing the ultimate maturation of the EDASES architecture.

---

## 4. Relevancy to EDASES & Project Position

These findings directly validate several core EDASES assumptions from `Research Addendum 01`:
1.  **AH-002 (Progressive Externalization):** The styling contract is a concrete, working implementation of styling externalization.
2.  **Capability Layer Isolation:** Bounding the plugin from payment/booking creation shows how strict interface constraints insulate agents from high-risk execution paths.
3.  **Primacy of the Knowledge Layer:** Validates our architectural pivot where the agent's primary output shifts from raw lines of code to structured, auditable decision and constraint ledgers.
