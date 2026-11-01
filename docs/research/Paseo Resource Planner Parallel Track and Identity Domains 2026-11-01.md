---
title: Paseo Resource Planner Parallel Track and Identity Domains — 2026-11-01
program: EDASES
layer: Research
document_type: Design Record
status: Draft
authority: Experimental
canonical_repository: edases
depends_on:
  - docs/research/Paseo Live Conversations and Resource Planning 2026-10-31.md
  - docs/research/Paseo Conversation-First Integration Roadmap 2026-10-31.md
related_documents:
  - docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md
  - docs/research/Paseo Role Capability Matrix.md
last_updated: 2026-11-01
---

# Resource-planner parallel track and three distinct identity domains

## Operator decisions and scope correction

On 2026-11-01 the operator authorized **starting development of the advisory resource calculator concurrently with the Paseo/VPS integration work**, instead of treating all work on the calculator as blocked until live strategic-chat grouping and session linkage are complete. This is a revision to the implementation timetable, **not** a change to the first user-facing Paseo milestone: original live ChatGPT and DeepSeek conversations remain the top-level organizing goal.

The operator also corrected a previously inferred identity mapping. **HMS and Trip'n are separate identities and projects.** A GitHub account named **\`tripn-chill-zone\` already exists and hosts the Trip'n production site**. Production ownership/access must not be transferred, conflated with HMS, or modified by routing-calculator experiments. Dedicated future GitHub identities and corresponding provider-account separation are intended for at least ASES and HMS, and Trip'n should remain under its own account/identity.

| Identity domain key | Project | GitHub identity | State |
| --- | --- | --- | --- |
| \`ases\` | ASES / EDASES development | Dedicated identity: name TBD; current ASES research repo under \`rock-solid-sites\` | **Future dedicated identity planned** |
| \`hms\` | Hospitality Management Suite | Dedicated identity: name TBD | **Future dedicated identity planned** |
| \`tripn\` | Trip'n production sites and work | \`tripn-chill-zone\` | **Existing production account** |

A shared Paseo user interface, server or work-graph view **does not** imply a shared provider account, permission set, quota or production authority. HMS-related tooling may be technically reusable for Trip'n without owning Trip'n's credentials or GitHub identity.

## Identity-aware routing model

Separate four distinct entities:

1. **Project identity/domain:** organizational, provenance and policy boundary for ASES, HMS or Trip'n.
2. **Platform account:** GitHub, Codespaces, Modal, cloud VPS, model-provider billing account etc.; belongs to a domain. The same vendor can have multiple accounts, where vendor rules allow.
3. **Resource:** concrete provider machine, hosted agent session, model allowance, storage bucket, quota window or verified credential route within an account. Resources must reference a specific owning account; free allowances are never inferred to be transferable.
4. **Stage/plan:** candidate placement linked to its project identity, with explicit scope, data class, branch/revision and evidence.

**Fail closed:** Without an explicit, narrowly scoped and revocable grant, no stage may consume a different domain's cloud compute credits, model tokens, source access, secrets or GitHub Actions capacity. Intentional shared infrastructure needs a separate permission contract and per-domain accounting; it must not be implemented by casually adding a second project's account to the candidate list.

Provider terms may prohibit or limit multiple accounts or multiple free-tier benefits. Registering distinct project domains in our **internal** model is permitted even when a provider ultimately requires an organization, subaccount, billing project or shared payment umbrella. Eligibility and legitimate account availability must be verified before activating separate accounts; do not assume duplicate promotional credits or signup eligibility.

## What can start immediately

**Independent, read-only prototype:** create a small typed resource/identity/work-graph library and test fixture, with no live provider access. Its purpose is to validate the data model, reject cross-domain resource assignments and compare **whole-graph** alternatives. It returns proposals to an operator or whichever authorized orchestrator is selected, not launch decisions.

**Prototyped on feature branch:** \`tools/resource-planner/\` contains strict TypeScript, a JSON input CLI and Node test suite. Initial coverage demonstrates the isolation of ASES, HMS and Trip'n; rejection of unknown/unverified resources; production data-class restriction; budget caps; whole-graph setup/transfer trade-offs; reviewer independence and replanning after observed stages. The fixture's sample provider accounts/resources are **synthetic** and marked as such: the sample's \`availability: verified\` is internal test input, not live cloud capacity.

**Integration can mature independently:** Paseo/OpenCode integration work later supplies current account balances, model routes, token/TPS logs, cost units, provider permissions, session lifecycle and execution observations. Do not assume the prototype can run OpenCode in Codex Cloud or access an existing production account.

## Deliberate prototype limitations

The initial algorithm is an exhaustive **assignment** search for small graphs (bounded, fails closed on size), with deterministic topological resource scheduling. It does not guarantee globally optimal intra-resource stage order, support simultaneous stages sharing machine cores, include model-route optimization, real multi-currency credits, account-wide concurrency, implicit cross-project grants, live quota observations, interval uncertainty or cloud launches. A production planner would require these checks and stronger adversarial review before use.

No provider login, GitHub account creation, production code migration, remote session launch or spending is authorized by this research note.

## Revised parallel roadmap

| Track | Now | After observed integration evidence |
| --- | --- | --- |
| VPS runbook | Finalize access, isolation, recovery, emergency stop and resource baseline | Choose/reconfigure permanent coordination host |
| Paseo tool/model integration | Validate current agent sessions, CLI/provider profiles, usage, log and stop features | Join live execution observations to planner |
| Original strategy chats in Paseo | Test native browser continuity and organize original live links | Link strategic decisions to execution sessions |
| **Resource calculator** | **Start independent typed model, identity-scoped registry, tests and example proposals now** | Connect to verified accounts, telemetry and project groups; improve scheduling and provider adapters |
| Identity provisioning | Record three domains and existing Trip'n account; do not create accounts by inference | Verify provider rules, establish separate legitimate accounts and least-privilege scoped grants |

## Acceptance criteria for the parallel prototype

- ASES routes cannot consume HMS or Trip'n model/compute allowances even if those appear cheaper.
- HMS proposals cannot select Trip'n's production host or identity.
- Trip'n production proposals can use only explicitly production-eligible resources belonging to Trip'n's domain (under separate authorization; fixture eligibility is not live authorization).
- An incomplete/historical/unverified account-resource catalog is not silently treated as live capacity.
- Stage independence and whole-graph transfer/setup/reuse economics are visible in plan alternatives.
- Replanning preserves completed observed results and does not overwrite their original resource assignments.
- The calculator performs **no launches, account creation, secrets access, billing actions, merges or deployments**.

## References

- \`tools/resource-planner/README.md\` and \`tools/resource-planner/planner.ts\`
- \`docs/research/Paseo Conversation-First Integration Roadmap 2026-10-31.md\`
- \`docs/research/Paseo Cloud Execution Environment Registry 2026-10-31.md\`
- \`docs/research/Paseo Role Capability Matrix.md\`
