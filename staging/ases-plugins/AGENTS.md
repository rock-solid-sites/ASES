# Agent operating contract — ASES Plugins

Read `README.md`, `DESIGN-AND-ASSURANCE.md` and `INVENTORY-AND-MIGRATION.md` before changing a plugin, skill, connector or release. Follow canonical ASES bounded-build, state-model applicability, constraint-driven realization and relevant VSDD verification methods by reference. This file is a local application profile, not a replacement methodology.

## Before implementation

Start with the exact user-visible outcome and work backward to the mechanisms required for that outcome. Inventory every transition and dependency: user intent, plugin eligibility, discovery, activation, selection, skill loading, action execution, observable result and conformance. For MCPs add registration, transport, authentication, authorization, tool discovery, backend invocation and security boundaries. Record mechanism, owner, evidence, missing pieces and cheapest discriminating test. Do not confuse installed, callable, selected and correctly applied.

Assess state-model applicability by component (PRIMARY, SUPPLEMENTARY, NOT APPLICABLE, UNRESOLVED). When useful, distinguish requested, authoritative and observed state, legal/forbidden transitions, failures and recovery. Model correctness never substitutes for implementation conformance.

Derive non-negotiable safety, correctness, security, resource, performance and operational constraints before selecting languages, architectures or vendors. Exclude demonstrated failures, hold unsupported options UNRESOLVED and avoid anchoring on a list of approved implementations. Reuse existing mechanisms where their behavior is evidenced; reject needless components.

## Execution

Use the smallest bounded change that can close a verified gap. Inspect the exact installed tool schema and current client surface; old screenshots and CLI success are not proof of ChatGPT functionality. Keep tests and production changes isolated. Prefer harmless read-only canaries before authorized disposable writes. Preserve existing accounts, routes, permissions and deployments. Never place secrets, bearer tokens or tunnel credentials in Git or logs.

Commit cohesive work frequently. Push a working branch at the end of a session. User decisions in strategy are authoritative unless they conflict with a demonstrated safety constraint or are materially ambiguous. Report evidence, unresolved issues and exact next action; do not claim completion on unrun checks. No automatic silent plugin upgrades.

## Required release gates

- User-facing trigger works in a fresh ChatGPT conversation without explicitly naming the skill.
- Correct plugin/skill/tool is actually selected, not merely present or manually loadable.
- Output or external effect satisfies the domain-level acceptance criteria.
- Negative tests include omitted selection, wrong selection, stale version, failed auth/transport, partial execution and misleading success.
- Version, source commit/hashes, compatible client, release identity and rollback path are recorded.
- Independent review addresses the implemented claim with minimal clean-room context.
- A failure leaves the release BLOCKED/UNVERIFIED, not accepted by proxy.

Do not migrate or retire a connector until its new path passes the same end-to-end contract as the old one.
