---
title: GitLab Pipeline Schedule Control - Agent Entry
program: Tooling
layer: Requirements
document_type: Requirements Specification
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - AGENTS.md
  - docs/standards/Documentation Standard.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
  - skills/custom-mcp-connector/SKILL.md
related_documents:
  - plugins/README.md
  - research/testing-assurance-pilot/scheduler-clock/EVIDENCE-CLASSIFICATION.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md
consumed_by:
  - subsequent GitLab schedule integration research, implementation, and assurance tasks
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-03
---

# GitLab Pipeline Schedule Control — machine-oriented entry

## Classification and ownership

- `kind`: capability-gap dossier and prospective integration requirements; **not** installed software, deployment instruction, approved architecture, or adopted global methodology.
- `operator_decision`: GitLab pipelines and recurring schedules must be manageable from an ordinary ChatGPT conversation; using the GitLab web dashboard repeatedly is unacceptable. A website visit is permitted as a one-time discriminating diagnostic or irreducible identity/consent step.
- `repository_exception`: the operator explicitly directed these **planning documents** into `rock-solid-sites/ASES/plugins/gitlab-schedule-control/`. `plugins/README.md` states that canonical custom MCP source, connector records, and runtime documentation have moved to [rock-solid-sites/rss-tools/mcp](https://github.com/rock-solid-sites/rss-tools/tree/main/mcp). Therefore **do not implement, duplicate, or deploy runtime connector source in this ASES folder**; use it for reasoning provenance and place eventual connector source/operational records in the canonical tools repository.
- `current_state`: design-only; no new credentials, schedules, pipelines, plugin registrations, MCP servers, infrastructure, or production settings are authorized by this dossier.

## Read in order

1. [DIAGNOSIS.md](DIAGNOSIS.md) — observation/interpretation boundary, precise GitLab failure surface, prior verified controls, unresolved schedule existence, discriminating tests.
2. [CAPABILITY-AND-OPTIONS.md](CAPABILITY-AND-OPTIONS.md) — requirements, MCP semantics and candidate architectures, security constraints, tool/API contracts, falsifiable acceptance tests, research decision gates.
3. [scheduler experiment evidence](../../research/testing-assurance-pilot/scheduler-clock/EVIDENCE-CLASSIFICATION.md) — definition of `CONFIGURATION_UNVERIFIED`, unobserved run, slot attribution, evidence quality.
4. [ASES connector diagnostic skill](../../skills/custom-mcp-connector/SKILL.md) — real ChatGPT client capability, registration, transport, identity, tool discovery, actual invocation and backend corroboration.
5. [canonical realization-selection method](../../docs/methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md) — exclude unsafe or unqualified realizations, minimize privileged authority/trusted base.

## Required outcome

`ChatGPT conversational intent -> discovered and authorized tool -> GitLab schedule object CRUD/state -> authoritative GitLab readback -> resulting schedule-triggered pipeline -> evidence with typed provenance`.

A green API-triggered pipeline is **not** confirmation of a working schedule. A tool registered in a plugin is **not** proof the current ChatGPT client can invoke it. Never invent a schedule activation or expected-slot denominator.

## Explicit non-goals

- Fixing GitHub's upstream native cron-delivery lateness.
- Replacing existing GitLab repository/issue/pipeline tools without evidence the replacement is needed.
- Modifying Trip'n production monitoring or Cloudflare-to-GitHub dispatch.
- Making a public or multi-tenant integration before a bounded, independently verified private canary.
- Collecting user GitLab tokens in chat, storing tokens in repository artifacts, or granting generic remote shell execution.

## Provenance pointers

- ASES [scheduler readback repair](../../research/testing-assurance-pilot/scheduler-clock/REPAIR-2026-11-03.md) and [PR #6](https://github.com/rock-solid-sites/ASES/pull/6), which fixed a separate GitHub observer route and lateness arithmetic.
- Official [GitLab pipeline schedules REST API](https://docs.gitlab.com/api/pipeline_schedules/).
- Official [GitLab MCP tool inventory](https://docs.gitlab.com/user/model_context_protocol/mcp_server_tools/) and [CI job-token endpoint limitations](https://docs.gitlab.com/ci/jobs/ci_job_token/).

## Instruction to successor agent

Do not restate this as a completed connector. Start with read-only verification of schedule existence and provider capabilities, then evaluate the smallest secure route that actually works **in ChatGPT**. Preserve `WHY` / `WHAT` / `HOW CERTAIN` / `WHAT-NOT-TESTED` per `AGENTS.md`. Record conflicting new evidence, avoid copying a historical claim forward unexamined, and use an authorized development branch for implementation.
