---
title: Tools Distribution Architecture — Synthesis of One-Shot Reviews
program: EDASES
layer: Research
document_type: Synthesis
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - docs/research/tools-distribution-architecture-review-input.md
  - docs/research/Tools Distribution Architecture Reviews.md
  - docs/research/agent-tooling-and-permission-enforcement-reviewed.md

consumed_by:
  - Tools/monorepo drift remediation planning (#365 and descendants)
  - Execution-engine UI research programme (tooling distribution decisions)

supersedes: []
last_updated: 2026-08-15
---

# Tools Distribution Architecture — Synthesis of One-Shot Reviews

> **Local research reconciliation, 2026-11-24 — shared artifact ownership and drift only.** The August review synthesis remains a research record of the then-existing tooling fleet, not a current universal installation or migration contract. Its original text and EDASES ownership remain intact; upstream currency is unverified. The following disposition concerns only artifact ownership, source authority and distribution direction. Provider visibility and specific migration/fix results require separate review.

## Question: how can independently evolving consumers share tooling without creating competing authorities?

The [original briefing](tools-distribution-architecture-review-input.md) records dated filesystem observations: divergent guard-plugin copies, wrappers and model-plugin copies, stale generated cache/whitelist data, and init-deployed snapshots. The intended warehouse copy was sometimes older than the live copy. All seven later reviews converge on a more precise diagnosis than "copying is bad": **multiple independently writable copies with ambiguous authority and no verified propagation**. The single-copy precedent is useful observational evidence, not a controlled demonstration that every shared artifact must use one physical copy.

| Original alternative | Decision and scope retained |
| --- | --- |
| A — embed every artifact in the Crosslink binary | Rejected as a universal distribution mechanism: ownership/release-cadence coupling, and actual init-snapshot drift contradicting its claimed structural immunity. Embedding genuinely product-owned resources is a distinct design choice. |
| B — immutable versioned bundles | Full packaging/release machinery judged disproportionate to the then-small fleet; reviewers retained lightweight source pinning, generated-artifact discipline and integrity checks. This was a scale-sensitive judgment, not rejection of versioned releases for all software. |
| C — reference consumption/symlinks | Attractive for avoiding independently editable copies, conditional on actual consumer loading, resolution and permission tests. Not an established guard-plugin loading result. |
| D — artifact-specific locus | Seven reviews favored separating machine-level shared tooling, per-project materializations and locally owned policies. Useful conceptual distinction; the old physical loci are not required across current cloud/desktop/harness environments. |
| E — interim sync and drift checks | Stabilization/transition, not the intended end state. Do not revive the historical sync script and warning/promotion machinery simply to preserve this finding. |
| F — live copy as authority | GLM's proposed direction was not selected. The [operator-confirmed amendment](Tools%20Distribution%20Architecture%20Decision%20Test%20Framework.md) settled Tools→consumers for that environment, with one-time reverse seeding of newer live material. The historical live-origin edit audit was confounded by the dormant warehouse and cannot choose a direction. |

### Present applicability

- **ASES methodology and operational instructions:** the [task-scoped information method](../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) governs source ownership, revision, applicability and consumer selection. The [current skills index](../../skills/current/README.md) declares ASES main/current as the operational source and uses read-only retrieval at invocation. The earlier [pinned-copy skill packaging experiment](../historical/Skill%20and%20Review%20Design%20History.md) is historical. Direct retrieval is a different mechanism, not evidence that all materialized configuration can or should be replaced by HTTP reads. Actual fresh-chat selection and application remain separately tracked (WNASES-23).
- **Shared executable tooling and installed configurations:** the [customization and upstream compatibility method](../methodology/Software%20Customization%20and%20Upstream%20Compatibility%20Method.md) favors traceable upstream releases, supported configuration/extensions and isolated local differences. A project-owned override must not be mistaken for an upstream edit. Installable artifacts may need tested materialization, version pinning and rollback; do not silently switch mechanism or overwrite a local difference. The August forward-distribution D1 check was unrun in the amendment; actual current fleet convergence, deployment identity and loading are unverified here.
- **Unresolved research question:** which combination of source-reference retrieval, generated materialization, pinned release distribution and local extension gives the best authority integrity, freshness, reproducibility and maintenance cost for a particular consumer and artifact type? Distinguish integrity of bytes from actual instruction selection/application or runtime enforcement. The independently scoped synthetic shared/project-local policy-publication pilot (WNASES-18) concerns exact import, extension, override and drift behavior; it does not establish live fleet distribution or reopen the accepted task-scoped ADR.

### Subject and owner separation

The underlying shared-tool distribution and configuration-maintenance question is a **cross-project / independent software-tooling research subject**, not automatically an ASES subsystem or an Engine requirement. Retain this classification for later topic-grouping work; exact primary owner/grouping for the general subject is unresolved. The historical Tools warehouse was explicitly a sibling library, not an EDASES/ASES/Engine abstraction layer. Its historical deployment target is not proof of present ownership of every artifact. ASES owns its methodology and current skills; a shared tool's implementation/release belongs to its actual owner repository, and the consuming project owns its local policies and acceptance evidence (the briefing's Trip'n example is a separate project). Shared learning may be linked back to ASES without transferring source authority. Do not create a new project, universal warehouse or migration issue from this note.

**Source cutoff:** [ASES fec55fd6](https://github.com/rock-solid-sites/ASES/tree/fec55fd6a255b7f6122725fe1ec44d31a36e0167). The seven original reviews and this synthesis are preserved; no distribution tests, migrations, model calls or external-project changes were performed in this reconciliation. Do not infer that all D1–D7 questions share this disposition.

## Preserved August synthesis

The full [original August synthesis](https://github.com/rock-solid-sites/ASES/blob/8df7d19343c12b9b999aca677b940c4f89418ee6/docs/research/Tools%20Distribution%20Architecture%20Synthesis.md#preserved-august-synthesis) retains all seven reviewer identities, evidence spans, convergence/divergence, alternative assessments, decision points and limitations exactly. It is historical research, not a current tooling or provider configuration. The local applicability and ownership crosswalk above is the current discovery surface.
