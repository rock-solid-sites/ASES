---
title: Resource Console v0.1 — Research Index
program: Tooling
layer: Research
document_type: Reference
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/requirements/Resource Console v0.1 Requirements.md
related_documents:
  - docs/architecture/Resource Console v0.1 Design and Contracts.md
  - docs/research/Resource Router Cross-Conversation Integration Ledger 2026-11-03.md
consumed_by: []
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-11-06
---

# Resource Console v0.1

**Experimental specifications, not a deployed app or adopted Kernel/Execution Engine policy.**

## Read in order

1. [Requirements](../../requirements/Resource%20Console%20v0.1%20Requirements.md): observable behavior, authority boundary, acceptance.
2. [Design and Contracts](../../architecture/Resource%20Console%20v0.1%20Design%20and%20Contracts.md): source reuse map, on-demand session model, UI/API projection, unresolved implementation gates.
3. [Verification Matrix](verification-matrix.md): regression, fault-injection, security, and live host measurements. All planned tests are **NOT RUN**.
4. [Bounded Implementation Packet](implementation-packet.md): frozen behavior and residual builder task; realization decisions remain conditional on live evidence.
5. [Snapshot schema](../../../research/resource-console/contracts/snapshot.v1.schema.json) and [synthetic fixture](../../../research/resource-console/contracts/snapshot.v1.example.json): executable machine-readable read contract draft; not production usage data.

## Explicit exclusions

The console is read-only regarding resource/provider/solver/kernel/agent state. It may only start or end its own transient monitoring session. It cannot promote observations to policy, entitlement, spending permission, or Kernel authority. The Engine and Observer remain future separate consumers; no Work Unit implementation exists here. Account-specific secrets and private usage must not enter this public repository.

## Source status

Existing provider inventories, old opportunities, and mock resource-control work are inputs with different authority levels. The v0.1 schema is a **derived projection**, not a replacement for any of these source registries or ledgers.
