---
title: Skill and Review Design History
version: 2026-11-24.1
program: ASES
layer: Research
document_type: Synthesis
status: Historical
authority: Derived
canonical_repository: ases
last_updated: 2026-11-24
---

# Skill and review design history

This is a map of earlier reasoning and rejected/retired operational approaches, not an additional skill collection. Current entrypoints: [skills/current](../../skills/current/README.md), [AI Orchestration Guide](../methodology/AI%20Orchestration%20Guide.md#review-modes-and-provenance), [Clean Room Execution Guide](../methodology/Clean%20Room%20Execution%20Guide.md), [bounded-build method](../methodology/ASES%20Bounded%20Project%20Build%20Method.md).

## Prompt design and review evolution

| Historical source | Decision, reasoning or rejected path | Current home |
| --- | --- | --- |
| [Compact Prompt 0.1 draft](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/compact-prompt/SKILL.md), [0.5 draft](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/prompt/SKILL.md) and [earlier Library variant](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/compact-prompt/archive/Prompt-Skill-older.md) | Prompt compression is source selection, not brevity alone. Earlier v0.1 permitted self-identity disclosure in some cases; v0.5 explicitly rejected that practice, separated caller configuration from receiver prompts, preserved established routes and minimized anchoring. | Current compact-prompt and agent-launch; retain exact variants for comparative study, not alternate active prompts. |
| [Compile Build draft](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/compile-build/SKILL.md) and [Strategy-to-Builder derivation](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/docs/research/pre-build-compilation/Strategy-to-Builder%20Integration%20Packet%20Method%20-%20Derivation.md) | Compile evidence-supported decisions before builder execution; avoid premature freeze and needless re-research. | Canonical bounded-build method and current compile-build skill. |
| [Workflow orchestration draft](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/workflow-orchestration/SKILL.md) | Smallest evidence-to-decision loop; isolate shared state, sequence dependencies, verify observable results; old VPS placement rules are not current. | Current workflow-orchestration and task-scoped method. |
| [Connector draft](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/custom-mcp-connector/SKILL.md) | September UI evidence and October lifecycle diagnostic profile; real client-originated calls rather than UI/CLI assumptions; no new tunnel/proxy solely due to navigation confusion. | Current custom-mcp skill and [project-local operational runbook](https://github.com/rock-solid-sites/ases-plugins/blob/main/docs/CHATGPT-MCP-CONNECTION-RUNBOOK.md). Historical Strategy Code Graph/IT3812 route is not a current setup. |
| [ATProto redirect](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/atproto-reader/SKILL.md) | Separate project ownership; the old entry was a pointer, not the tool contract. | [RSS Tools MCP registry](https://github.com/rock-solid-sites/rss-tools/blob/main/mcp/REGISTRY.md). |
| [Ontology specialist proposal](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/ontology-reviewer/Ontology-Reviewer-Role-Proposal.md), [role specification](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/ontology-reviewer/Ontology-Reviewer-Role.md), [ontological connection](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/skills/ontology-reviewer/Ontological-Connection-to-Review-Skill.md) and their archived earlier variants | Review domain and epistemic mode are independent; rejected one generic ontology review shape. Exploratory criticism can use design history; post-build conformance isolates process history. Cross-family provenance addresses correlated blind spots; same-family acceptance is distinct. Routing strengths/panel sizes, automated triggers and specialist role adoption remain hypotheses. | Current AI Orchestration Guide and Clean Room Execution Guide; not a new required role, ontology engine or launch service. See also [full proposal in the role record](../roles/Ontology-Reviewer.md). |

The role proposal's benchmark idea remains useful: include known conceptual defects and clean controls, compare exploratory and conformance results separately, measure false positives, canonical fidelity, context cost, model-family sensitivity and unjustified ontology invention. Do not claim the benchmark ran or a role was adopted. The task-scoped information decision rejects requiring a universal knowledge resolver or fixed startup context; this historical review design does not supersede it.

## Pinned-copy packaging versus current source retrieval

The [original v0.1.0 plugin source README](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/plugins/ases-workflow/README.md), [dispatcher](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/plugins/ases-workflow/dispatcher/SKILL.md), [source hash manifest](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/plugins/ases-workflow/sources.json), [checker](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/plugins/ases-workflow/check_versions.py) and [scheduled drift workflow](https://github.com/rock-solid-sites/ASES/blob/129761e20d70baba3090946e7acb55904d01ceb9/.github/workflows/ases-workflow-skill-drift.yml) implemented a pinned-copy release comparison. It was useful when installed packages held historical skill copies. The current ASES Workflow convention instead fetches the read-only current index and task-relevant current sources at use time. Ordinary Markdown updates do not require republishing the dispatcher. The old checker targeted retired skill paths; scheduling it would report an obsolete packaging contract rather than test actual current skill invocation. It is archived, not enabled. A future packaged adapter may need independent release integrity verification; this disposition is not a rejection of hashes or reproducible snapshots generally.

Current behavioral verification remains WNASES-23: automatic skill selection, actual retrieval and application in genuinely fresh chats. A successful install, source-tree cleanup, or a passing old hash check cannot establish those behaviors.

## Exact archival source

Pre-reorganization snapshot: [ASES 129761e20d70](https://github.com/rock-solid-sites/ASES/tree/129761e20d70baba3090946e7acb55904d01ceb9). The archived [source directory](skill-review-source-2026/) retains original tracked blob content and mode; old skill entry filenames end in .txt, and the former scheduled workflow is outside the GitHub workflow discovery path. Original repository layout and links remain reproducible at the pinned source. Do not execute archived code or treat earlier labels as current authority.

For the historical harness setup, permission failures and configuration experiments see [Harness Setup and Permission Design History](Harness%20Setup%20and%20Permission%20Design%20History.md).
