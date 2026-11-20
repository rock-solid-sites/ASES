---
title: Agent Information Topology - ASES Instruction Entry-Point Audit - 2026-11-20
program: ASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
related_documents:
  - research/agent-information-topology/policy-publication-baseline/DESIGN-AND-DECISION-BOUNDARIES.md
  - skills/current/README.md
last_updated: 2026-11-20
---

# Instruction entry-point audit: competing ASES document routes

**Source observation revision:** [rock-solid-sites/ASES@1a88b244](https://github.com/rock-solid-sites/ASES/tree/1a88b244eacb6224f2e4ed69ddaba1781b3f4763) (2026-11-20). No agent model, filesystem discovery or network-config runtime test was executed for this audit. File content is observed; runtime instruction loading and actual model compliance remain **UNVERIFIED**.

## Finding

The current Skills MCP/ChatGPT dispatcher defines a read-only **HTTPS, selective retrieval** of [`skills/current/README.md`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/skills/current/README.md). Other repository entry points contain incompatible or obsolete guidance about retrieval, commands, launch models, and rule authority. These contradictions do **not** imply every harness loads every file.

| Observed source | Specific dated/source fact | Consequence if loaded | Disposition |
| --- | --- | --- | --- |
| [`skills/current/README.md`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/skills/current/README.md) | Specifies current skill index, selective read-only HTTPS GET; do not invoke a write-capable GitHub connector merely to read instructions | Defines the **current ChatGPT Skills MCP retrieval convention**, not an automatic hook or authorization to load every skill | **Current source** for installed dispatcher; verify live fetch and commit when available |
| [`skills/README.md`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/skills/README.md) | Intro says the same dispatcher should fetch `SKILL.md` via the **GitHub connector**, conflicting with current read-only HTTP convention | Reader may call the wrong higher-privilege tool or bypass intended dispatcher path | **Safe navigation fix**: change one sentence to link and honor current index; do not alter current skill contents |
| [`AGENTS.md`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/AGENTS.md) | Top references 2026-10-31 `Agent Model Launch Routes.md` for *any launch*. Its model-discipline section labels that dated runbook "authoritative" | Model/host selection can follow historical environment details instead of verified current route, unless agent also consumes the newer launcher skill | **Propose narrow routing correction**, after frozen WNASES-18/19 first-pass comparisons; do not alter active agent instructions in this research PR |
| [`SESSION-START.md`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/SESSION-START.md) | Every-session entrypoint still mandates `crosslink session last-handoff` and treats live `crosslink` as authoritative. Its model hard rules explicitly say to fall back to *paid Go* on free Zen rate-limit symptoms | Historical execution assumptions and a permitted fallback conflict with the current exact-route/no-silent-substitution rule | **High-priority proposed correction** to link current launch skill; preserve older operational forensics as history, not as current commands |
| [`docs/ORCHESTRATOR.md`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/docs/ORCHESTRATOR.md) | "Current Deployment" describes four OpenCode roles, runtime model IDs, old Crosslink/Paseo coordination; later section explicitly states historical Crosslink guard not in use | Competing current/historical blocks within a single document can cause agent to treat planned architecture as deployed | **Audit and label dated deployment paragraphs** before rewriting role contract; no production change authorized |
| [`.opencode/opencode.json`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/.opencode/opencode.json) | Explicitly points at `SESSION-START.md`, four historic plugin paths, and filesystem MCP with retired absolute host path | Provides a **potential** separate load path to obsolete session rules, but effective behavior depends on tested OpenCode version and its configuration resolution | Exposure experiment belongs to WNASES-19; do not assume the model received all of these sources |
| [`.mcp.json`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/.mcp.json) | Three server definitions use `.claude/mcp/` Crosslink-era scripts | Legacy path could still be discoverable to some launchers; presence alone does not prove execution | No deletion/config edits in document pilot; investigate loading separately |
| [`docs/methodology/Agent Model Launch Routes.md`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/docs/methodology/Agent%20Model%20Launch%20Routes.md) | Metadata says "Active (dated environment snapshot)" and prose describes unavailable IT3812 VPS, dated model routes, and 2026-10-31 verification | A consumer relying on its "active" label may mistake a historical route for one currently authorized and connected | Designate historical *environment snapshot* explicitly, keep compatibility evidence accessible |
| [`skills/README.md` legacy paths](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/skills/README.md) | Older skill sources intentionally remain available outside `skills/current` | Historical material may remain discoverable by agents other than the installed ChatGPT dispatcher | Keep distinct "preserved on disk" vs "installed/auto-discoverable" claims; only WNASES-19 can test actual auto-exposure |
| [`plugins/ases-workflow/sources.json`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/plugins/ases-workflow/sources.json) + [drift workflow](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/.github/workflows/ases-workflow-skill-drift.yml) | The manifest pins `skills/compile-build`, `skills/custom-mcp-connector`, `skills/prompt` and `skills/workflow-orchestration`—**not** the six `skills/current/` entries; weekly [`plugins/ases-workflow/check_versions.py`](https://github.com/rock-solid-sites/ASES/blob/1a88b244eacb6224f2e4ed69ddaba1781b3f4763/plugins/ases-workflow/check_versions.py) reads that legacy manifest | A passing historical-bundle drift check **does not certify currency** of the active ChatGPT Skills MCP dispatcher or its current six source files | **Coverage defect**: add separate source-pinned current-skills monitoring or explicitly scope existing check as legacy; first verify what asset the checker is intended to protect |

## Target document and agent-instruction topology

1. **Canonical policy and methodology**: explicitly reviewed ASES rules at known revision and authority. EDASES research is *not* promoted solely because linked or indexed.
2. **Operational skill index**: `skills/current/README.md` is an *entrypoint*, not a universal auto-loaded body. Request selects the minimal matching skill.
3. **Project-local effective instructions**: policy imports plus project-owned overrides/extensions, with reviewed source pin and clear generated/local-file ownership. A completed synthetic publication test does not show actual harness exposure.
4. **Harness-specific discovery**: root/nested `AGENTS.md`, runtime config, installed/global skills and tools are independently measured; avoid declaring old files safe merely because their filenames suggest retirement.
5. **Evidence/operational state**: GitHub reports source and test evidence, Work Notes tracks execution, Projektor tracks human decisions. Indexing does not confer authority.

Do not treat `source authority` = `file present` = `agent loaded` = `agent obeyed` as interchangeable conditions.

## Proposed minimal remediation order

**A. Correct harmless navigation contradiction now.** In `skills/README.md`, replace GitHub connector retrieval instruction with the read-only HTTPS current index. This is not an active AGENTS policy edit.

**B. Reconcile publication/drift coverage.** Verify installed dispatcher and weekly drift check are designed for the same asset set. Decide whether to monitor six current `SKILL.md` files plus index, or explicitly keep the old manifest for legacy packaged skills and add a separate current check. Do not falsely call legacy check "current skills synchronized."

**C. Frozen independent pilots before active routing edits.** Keep [WNASES-18 / PR #64](https://github.com/rock-solid-sites/ASES/pull/64) separate from [WNASES-19 / PR #63](https://github.com/rock-solid-sites/ASES/pull/63) until the experimental evidence is reconciled. A Codex environment failure remains a blocker to *independent Luna execution*, not to offline document inspection.

**D. Minimal active entrypoint changes after evidence review.** Update `AGENTS.md` and `SESSION-START.md` to route launch/model decisions to the current skill and classify old Crosslink/IT3812 instructions as historical; avoid wholesale rewrites, inherited model defaults, live credential changes and a new Resource Solver.

**E. Harness-specific exposure check.** Validate no conflicting root/global/nested rules enter the target model request without an explicit retrieval path. That remains unverified unless measured.

## WHAT-NOT-TESTED

No new Codex/OpenCode/model execution; no real agent bootstrap; no per-request prompt capture; no live user-level/global skill listing; no multi-repo publication or policy merge; no active instruction/agent-config changes; no authenticated provider checks; no assumption that the older Tools or Crosslink machinery is currently deployed. The source snapshot is dated: recheck against current `main` before making active operational modifications. All table consequences are conditional on a harness actually loading the identified source.
