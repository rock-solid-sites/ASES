# Synthesis: Beds24 Booking System Evolution
## A Cross-Architecture Project History and Methodological Synthesis

**Date:** 2026-06-23  
**Author:** OpenCode (Principal/Orchestrator Agent)  
**Type:** Integration, Analysis  
**Status:** Complete  
**Related Findings:** `findings/2026-06-23-beds24-plugin-evidence.md`  
**Crosslink Context:** Session #2 Active  

---

## 1. Executive Summary

The Beds24 Booking System represents a cornerstone empirical case study for the ASES project. Over an intensive two-month developmental arc, the system completed two radical architectural paradigm shifts:
1.  **Phase 1 (The Predecessor Era):** A direct, client-side CSS/JS overlay injected directly into Beds24’s SaaS-hosted checkout interface.
2.  **Phase 2 (The WordPress Plugin Era):** A PHP-based WordPress plugin utilizing the Beds24 API v2 to decouple *discovery* (WordPress-native room grids and cart) from *transactions* (embedded checkout iframe).
3.  **Phase 3 (The Astro Integration Era):** A modern, statically generated, serverless edge-computed Astro module (`beds24-astro-module`) deployed live on Cloudflare Pages and Workers.

This synthesis integrates the historical timeline, technical hurdles, and the 29 codified "Retrospective Rules" of the project. It maps the system's evolution to the six layers of the **Evidence-Driven Organizational System (EDASES)** architecture and demonstrates how this timeline provides conclusive validation for the **Progressive Externalization (AH-002)** hypothesis.

---

## 2. The Architectural Inception (Predecessor Era: April 19 – May 6, 2026)

### 2.1 The Goal & The Strategy
The project began as an attempt to restyle the default, unpolished Beds24 checkout widget for the *Chill Zone* property (ID `271142`). The initial strategy adopted a low-overhead "overlay" approach: injecting custom Javascript and CSS files directly into Beds24's administrative console to override their default layout (Layout 6) in the guest's browser.

### 2.2 The Platform Constraints (Failure Modes)
This Phase immediately encountered severe, undocumented silent failures inherent to Beds24’s proprietary administrative interface:
*   **The 2,000-Character `customhead` Limit:** The "Insert in HTML `<HEAD>` bottom" text field silently truncated saves at exactly 2,000 characters without raising DOM or server-side error validation. Long compiled stylesheets were silently cut in half, breaking rendering.
*   **Script/Style Tag Stripping:** Programs attempting to perform automated `POST` updates to Beds24's custom administrative fields found that script and style tags were programmatically stripped by Beds24's server firewalls on save, forcing a manual browser-based paste pipeline.
*   **Non-ASCII Destruction:** The database silently stripped literal emojis and non-ASCII characters from script fields, necessitating the discovery and adoption of Javascript Unicode escapes (e.g., `\uD83D\uDECF` for bed emojis).
*   **Specificity & Caching Wars:** Injecting overrides on top of Beds24’s native markup triggered a fragile styling war against their internal CSS specificity. Compounding this, the cloud servers used strict caching layers that ignored file-purge commands, forcing developers to continuously rotate file names to bypass caches.

### 2.3 Hard-Won Lessons
Faced with these hidden platform failure modes, the team established its core meta-cognitive operational rules, primarily:
*   **Rule #1: Measurements vs. Inferences:** Every claim about platform behavior must be empirically tested in a live browser session (via DevTools Network/DOM panels) rather than inferred from prior documentation.
*   **Rule #2: Cheapest Falsifying Test First:** Before writing complex code, execute the absolute cheapest test that can prove the core premise wrong.
*   **Rule #3: Verify Saves Before Building:** Always reload administrative pages after a write to confirm persistence.

---

## 3. The WordPress Decoupled Shift (WordPress Era: May 7 – May 16, 2026)

### 3.1 The Strategic Pivot
Recognizing that styling Beds24 in-place was a losing battle due to specificity conflicts, the project executed a fundamental architectural pivot to **Option 2 (WordPress decoupled plugin)**. 

The core breakthrough was separating the user's booking journey into two distinct halves:
1.  **The Discovery Half (WordPress-owned):** WordPress Custom Post Types (`beds24_room`) and custom taxonomies (`beds24_amenity`) stored room content, descriptions, photo paths, and metadata. The frontend rendered a highly polished search form, live room grids, and a multi-room cart accumulator utilizing cached API pricing data.
2.  **The Transaction Half (Beds24-owned):** When the guest clicks "Confirm Booking," the plugin constructs a multi-room prepopulated URL and transitions the guest into a full-height, styled Beds24 `booking3.php` iframe.

### 3.2 Technical Implementation & Hurdles
*   **The API Client:** Built `class-beds24-api-client.php` to manage the Beds24 v2 API authentication lifecycle: Invite Code (one-time header setup) → Refresh Token (stored in `wp_options`) → Access Token (cached daily in WordPress transients).
*   **The Chrome Flex Bug:** Discovered that Chrome’s User Agent stylesheet treats hidden flex elements differently than Firefox. Autor CSS rules for `display: flex` overrode the HTML `[hidden]` attribute, preventing the cart from hiding. Resolved by writing a global override: `[hidden] { display: none !important; }`.
*   **Empty Iframe Load Loops:** Discovered that rendering a blank iframe with `src=""` in Chrome triggers a loop where Chrome attempts to load the parent WordPress document inside the iframe container. Resolved by completely removing the `src` attribute from the HTML template.
*   **WordPress Symlink Restrictions:** When deploying to aaPanel-hosted staging environments, PHP failed to follow symlinks from the git working directory because of aaPanel's strict `open_basedir` PHP restriction. The team had to abandon symlinks and adopt a copy-based deployment script.
*   **Multi-Room URL Discoveries:** Live browser inspection (Session 13) revealed undocumented multi-room parameters: `sr1-{id}=1` and `naa1-1-{id}=N` (pre-selecting quantities). This allowed the cart to bypass Beds24's official, single-room iframe guides entirely.

### 3.3 The Styling Contract
To unify the visual theme, the plugin read tokens from the active theme's `theme.json` (falling back to admin settings), and emitted `--beds24-*` CSS custom properties on site. It also ran a backend PHP generator (`iframe-css-generator.php`) that compiled these tokens into a single static CSS sheet, which the operator manually copy-pasted into Beds24's `bookingcss` field, perfectly styling the checkout iframe.

---

## 4. The Serverless Edge Maturation (Astro Era: Post-WordPress)

### 4.1 The Final Evolution
The ultimate phase of the Beds24 booking system bypassed the database bloat and server maintenance of WordPress, porting the entire architecture into an Astro Static-Site Integration (`beds24-astro-module`) deployed live on **Cloudflare Pages and Workers**.

### 4.2 Decoupled Declarative Content (`rooms.json`)
The WordPress MySQL database was completely retired. All room descriptions, photo paths, and amenity tags were externalized into a flat, versioned, declarative JSON file (`content/chill-zone/rooms.json`) stored in the static site's project root:

```json
{
  "567218": {
    "title": "Deluxe King Suite",
    "description": "Spacious premium suite with a king-sized bed, ensuite bathroom and panoramic views.",
    "photo": "/content/chill-zone/images/suite.png",
    "photoAlt": "Bright suite with king bed and city view",
    "displayOrder": 1,
    "tags": [
      { "type": "preset", "preset": "sleeps-2" },
      { "type": "preset", "preset": "ensuite" }
    ]
  }
}
```

### 4.3 Three-Tier Edge Cache Hierarchy (`beds24-client.ts`)
To operate efficiently in a serverless Worker context without exceeding Beds24 rate limits (100 credits per 5 mins), the TypeScript client implements a multi-layer cache:
1.  **In-Memory Cache:** Maps tokens and room-types per Worker instance (cleared on cold start).
2.  **Cloudflare Key-Value (KV) Cache:** Persists token structures (`token:chill-zone`) and room-types (`roomtypes:chill-zone`) globally across edge nodes, avoiding redundant API calls.
3.  **Live API Query:** Fires only on a complete cache miss, writing results back into KV with short TTLs.

### 4.4 Automated Build Validation (`scripts/validate.ts`)
Verification was moved from post-deploy manual checks to **pre-deploy automated compilation gates**. A custom TypeScript script using `Zod` and `image-size` executes during every site build:
*   **Image Dimensions & Formats:** Asserts that every room photo exists on disk, is in an accepted format (WebP/JPG/PNG), is under 500KB, meets resolution bounds (`400x300` to `2000x1500`), and adheres to landscape aspect ratios (between `4:3` and `16:9`).
*   **Grapheme Segmentation:** Programmatically segments custom tag emojis using `Intl.Segmenter` to ensure that custom icons are strictly a single grapheme cluster (guarding against corrupt rendering).
*   **Tag Presets Consistency:** Matches all room tags against a central presets schema (`config/tag-presets.ts`) and alerts operators if a property exceeds three custom tags, suggesting they should be promoted to reusable presets.

---

## 5. Methodological Synthesis: EDASES Layer Mapping

The evolution of the Beds24 booking system provides a clear blueprint for mapping real-world software engineering to the six layers of the **Evidence-Driven Organizational System (EDASES)**:

```
  +-----------------------------------------------------------------------------------+
  |                                 EDASES LAYERS                                     |
  +-----------------------------------------------------------------------------------+
  | PRINCIPAL LAYER      | Decoupled boundary (Discovery vs. Transaction), anti-scope |
  +----------------------+------------------------------------------------------------+
  | ORGANIZATIONAL LAYER | WP-Admin Content Editors vs. Beds24 Financial Rails        |
  +----------------------+------------------------------------------------------------+
  | KNOWLEDGE LAYER      | Retrospective Rules, rooms.json, tag-presets.ts            |
  +----------------------+------------------------------------------------------------+
  | CAPABILITY LAYER     | TypeScript API Client, Cloudflare Workers, Astro Modules   |
  +----------------------+------------------------------------------------------------+
  | VERIFICATION LAYER   | Zod Build Gates, Segmenter, Image-Size aspect ratios, KV   |
  +----------------------+------------------------------------------------------------+
  | EXECUTION LAYER      | Cloudflare Pages, Vite Assets, static HTML, viewScript JS  |
  +-----------------------------------------------------------------------------------+
```

### 5.1 Principal Layer
*   **Role:** The boundary of oversight, constraints, and structural intent.
*   **Beds24 Evidence:** The discovery-transaction split is a principal-level design contract. The system strictly bounded its scope to discovery, refusing to write code that touched payment processing, Stripe, or booking creation APIs. This "anti-scope covenant" protected the business from security liability and kept the capability surface lightweight.

### 5.2 Organizational Layer
*   **Role:** Separation of human workflows, operational roles, and platform ownership.
*   **Beds24 Evidence:** Operators manage content (room names, descriptions, and photos) inside their primary workspace (originally WordPress, now a static git-backed repository), completely avoiding Beds24’s difficult administrative panel. Meanwhile, Beds24 continues to securely host transaction details, financial records, and emails—leveraging the organizational strength of each platform without crossing scopes.

### 5.3 Knowledge Layer
*   **Role:** Explicit preservation of lessons, rules, static schemas, and configurations.
*   **Beds24 Evidence:** The 29 active retrospective rules represent a compiled, living repository of system knowledge. By storing styling variables inside a declarative contract (`styling-contract.md`) and room data inside versioned JSON (`rooms.json`), the knowledge base became fully portable and survive the total disposal of the PHP codebase during the Astro pivot.

### 5.4 Capability Layer
*   **Role:** Pluggable, modular code libraries, API clients, and execution frameworks.
*   **Beds24 Evidence:** The `Beds24_API_Client` (PHP) and subsequent `getAccessToken`/`getRoomTypes` (TypeScript/Astro) utilities are isolated, modular capabilities. They wrap specific external service boundaries, handling rate limits, error logging, and caching internally while presenting a clean interface to the rest of the application.

### 5.5 Verification Layer
*   **Role:** Build-time validation, sanity testing, and computed-style audits.
*   **Beds24 Evidence:** The transition from manual post-deploy browser inspections to the automated `npm run validate` build gate is a monumental maturation of the Verification Layer. By using Zod schema checks, grapheme segmentation, and image aspect ratio audits, the system guarantees 100% data consistency before a single static file is deployed.

### 5.6 Execution Layer
*   **Role:** The physical deployment substrate, runtime environments, and asset pipelines.
*   **Beds24 Evidence:** The runtime execution moved from local Laragon DDEV stacks and staging VPS environments to serverless Cloudflare Workers and statically cached Vite assets. Frontend execution is kept lightweight via a zero-dependency plain-JS state store in `booking-flow.js`, maintaining maximum compatibility and zero performance overhead.

---

## 6. Validation of the Progressive Externalization (AH-002) Hypothesis

The primary thesis of **Progressive Externalization (AH-002)** is that *as software engineering organizations mature, their operational structures, configurations, visual tokens, and content are progressively extracted from code execution blocks into versioned, declarative specifications*. 

The Beds24 Booking System evolution provides an empirical proof of this hypothesis across three dimensions:

### 1. The Content Vector (MySQL → Static Declarative JSON)
In the WordPress Era, room content and amenity taxonomies lived inside a dynamic, stateful relational database (MySQL), accessible only via in-process PHP execution. During the Astro pivot, this database dependency was completely externalized. Content became a flat, versioned JSON file (`rooms.json`), validating that complex database schemas can be progressively extracted into light, declarative static assets.

### 2. The Styling Vector (Hardcoded CSS → theme.json Token Contracts)
Initial restyling attempts used hardcoded, high-specificity CSS overrides directly targeted at Beds24's elements. Maturation forced the creation of a three-layer "styling contract" where design tokens were extracted from WordPress `theme.json` or Astro stylesheets, mapped to a canonical list of ~30 CSS custom properties, and compiled. The code no longer hardcodes any aesthetic values; the design exists entirely as a declarative contract.

### 3. The Verification Vector (Manual Inspection → Zod Build Gates)
Early deployment verification was highly manual and required human visual reviews of viewports. In the final Astro phase, these visual constraints were translated into declarative rules: aspect ratio ranges (1.33 to 1.78), file size limits (500KB), and single-character emoji segments. These rules are compiled into a Zod validation script, translating human visual "intent" into rigid, automated build-time gates.

---

## 7. Chronological Reference Map of Project Documents

For future engineering sessions, the following historical records must be maintained as active reference materials:

| Document | Location | Role in System |
|---|---|---|
| **Live Astro Integration Code** | `/home/claude-code/projects/tripn-astro/vendor/beds24-astro-module/` | The active, working, production-grade serverless codebase. |
| **Active Build Validation Script** | `vendor/beds24-astro-module/scripts/validate.ts` | The build gate validating Zod schemas, images, aspect ratios, and tags. |
| **Declarative Room Content** | `vendor/beds24-astro-module/content/chill-zone/rooms.json` | The static, versioned JSON data model for room results. |
| **Tag Presets Definition** | `vendor/beds24-astro-module/config/tag-presets.ts` | Central schema matching preset amenity tag keys to icons and labels. |
| **API Client Utilities** | `vendor/beds24-astro-module/src/lib/beds24-client.ts` | TypeScript token acquisition, Map, and Cloudflare KV cache logic. |
| **Astro Build Philosophy** | `BUILD.md` (in `tripn-astro`) | Project build spec, design system rules, and session review gates. |
| **Historical WordPress Code** | `/home/claude-code/beds24-booking-plugin-deploy/` | Deprecated PHP/WordPress codebase (maintained strictly as historical reference). |
| **Historical Session Handoffs** | `/home/claude-code/beds24-booking-plugin/docs/` | Chronological session-by-session log files (Sessions 1 to 25). |
| **Master Retrospective Log** | `docs/retrospective.md` (in plugin repo) | The living, append-only database of 29 Active Rules and failures. |
