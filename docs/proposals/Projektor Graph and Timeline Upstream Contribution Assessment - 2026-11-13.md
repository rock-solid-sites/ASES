---
title: Projektor Graph and Timeline Upstream Contribution Assessment
program: ASES
layer: Requirements
document_type: Design Document
status: Draft
authority: Derived
canonical_repository: ases
depends_on:
  - docs/methodology/Software Customization and Upstream Compatibility Method.md
related_documents:
  - docs/methodology/ASES Bounded Project Build Method.md
consumed_by:
  - Projektor integration planning
last_updated: 2026-11-13
---

# Projektor: Graph and Timeline as potential upstream features

## Local reconciliation: current ownership and portability (2026-11-26)

Retain the original Graph-first, Timeline-separate recommendation as a candidate contribution strategy, not an upstream submission or accepted feature. The [workspace trial reconciliation](2026-11-02-testing-debugging-ontology/projektor-workspace-trial-plan-2026-11-05.md#local-reconciliation-workspace-trial-and-subsequent-evidence-2026-11-26) distinguishes actual use from unresolved UI, permissions, restore and upgrade qualification.

The November 10 PJDEV-2 baseline established existing read-only issue/wiki relationship traversal, including cross-project edges within one workspace, not a generic semantic graph. PJDEV-9/12/14/16/19 retain Graph, Canvas export, mocked browser coverage and shell/navigation scope; the recorded static prototypes and user feedback are not proof of native source integration or authenticated mobile acceptance. PJDEV-20 defines Portfolio → Project → recursively nested Subproject → Issue (no synthetic hub and no silent flat-record migration); PJDEV-21 distinguishes sourced first-discussed/proposed/work-start milestones from issue activity and PJDEV-18 separately covers actual planned dates. PJDEV-5/15 saved views, PJDEV-25 external dependency references and PJDEV-7/13 CLI/discovery remain distinct owner questions. Work Notes operational records must not be mirrored as human planning data or treated as same-system issue links.

The later [canonical customization method](../methodology/Software%20Customization%20and%20Upstream%20Compatibility%20Method.md) favors supported configuration/interfaces, isolated removable extensions, small generally useful upstream contributions and the latest stable release subject to actual upgrade acceptance. Existing local release overlays are not maintainable upstream deliverables; no copied app shell, arbitrary schema, permanent fork or native migration follows. PJDEV-26 still tracks clean upgrade/restore; current deployment and upstream submission/acceptance were not independently verified. The older roadmap's contribution wording must not be read as a requirement to build a substantial feature before discussing it with maintainers. Distinguish early scoped discussion from submission of tested code. Do not reopen historical surveys or launch implementation in this reconciliation. Local private policies and ASES's task-scoped information method remain independent of upstream product governance.

## Decision (proposal, not a submission)

**Propose a small read-only work-relationship graph upstream first. Discuss Timeline separately, with an upstream-native, evidence-backed scope.** Do not submit the existing local overlay as-is and do not make either feature a prerequisite for a clean Projektor installation.

The question is upstream usefulness, not whether our current prototype can be transplanted. A successful contribution should become part of ordinary Projektor releases, eliminating an upgrade-sensitive private patch.

## Checked upstream basis

- On 2026-11-13, latest published release: [v0.11.1](https://github.com/TAJD/projektor/releases/tag/v0.11.1) (November 11). The main branch was newer (checked commit 84c45b9d27426e2ae7c6bd68ac8706d9fc5348ba); released and unreleased features must not be conflated.
- [Design principles](https://github.com/TAJD/projektor/blob/main/apps/docs/src/content/docs/philosophy/design-principles.md) cover capturing/planning work, readiness/dependencies, recording evidence and visualizing work flow. Features should support humans on the web and agents over MCP, fleet-safe data and coordination rather than agent execution.
- Existing primitives: issue links, epics, projects, wiki links/backlinks, flow metrics and native Kanban. The [wiki link graph/backlinks change, PR #170](https://github.com/TAJD/projektor/pull/170), merged July 31, demonstrates a first-party relationship model with MCP/REST parity. It does not establish that a graphical canvas viewer already exists.
- [CONTRIBUTING.md](https://github.com/TAJD/projektor/blob/main/CONTRIBUTING.md) asks contributors to discuss larger features in an issue before coding. Public issue searches returned no matching open Graph/Timeline discussions, but Projektor's own internal wiki may contain planning not exposed on GitHub. No maintainer acceptance has been obtained.
- Local prototypes examined: the related-graph visualization reads authorized project, issue-link and wiki relationships and can export Canvas. Our timeline combines tracked issues with optional specialized historical milestone evidence drawn from project wiki records. They are exploratory local implementations, not portable upstream deliverables.

## Candidate A — work relationship Graph

**Fit: high, subject to maintainer interest.**

A read-only graph could display existing issue dependencies, parent/child epics, project membership and wiki backlinks. This helps human operators and agents see blockers and related specifications across modules. Start with existing authorization-checked data; do not add a schema solely for a visualization.

**Small first feature:** from an Issue or Epic, open an accessible related-work view of directly connected work items, including status, labels and native deep links. Bound expansion and pagination, handle forbidden or missing nodes, and provide a usable keyboard/text listing. Use existing REST and MCP relationships before proposing a new graph API.

Exclude our local workspace routing, DOM/nav overlays, Portfolio terminology, site branding and wide Canvas export from this first proposal. They are separate deployment preferences or optional features. The upstream PR should be normal source with ordinary build/tests, not a patch to release bundles.

## Candidate B — project Timeline

**Fit: plausible for work events and roadmap; uncertain for our historical-evidence view.**

Projektor already records lifecycle and flow information. Our local timeline additionally asks when a Project was first discussed, proposed or begun, using manually curated sources in a special wiki format. These dates cannot be inferred from project creation, and the extra convention is specific to our practice unless upstream expressly adopts it.

**Small upstream-shaped proposal:** a per-project or per-Epic chronology of verifiable status changes, milestones, sprint events and recorded issue activity, wherever existing data supports it. Do not invent pre-tracker history, treat creation dates as inception, or introduce new tables/wiki formats without first demonstrating the need. The upstream maintainer should decide whether a roadmap, activity history or historical evidence register fits their scope: these are distinct features.

## Contribution route

Discuss **Graph** with the maintainer first through a small issue. Show one focused Issue-centered example, the existing data services it consumes, and the accessibility/workspace-scoping approach. Ask about roadmap fit and preferred component placement before developing a substantial upstream PR.

Discuss **Timeline separately**, after deciding whether the intended view concerns activity, milestones, dependencies or long-term historical evidence. Show grounded events with unknown dates clearly unknown. No unsolicited large PR or schema migration.

If declined, keep any local feature only if a supported extension can provide it without altering upstream release artifacts or creating a permanent fork; otherwise defer it. Reliable clean upstream core workflows outrank optional visualizations.

## Status

**Assessment recorded only; no upstream issue or PR created; no production changes.** Neither capability is approved upstream and neither existing prototype is certified portable. Reassess on relevant upstream changes or maintainer feedback.
