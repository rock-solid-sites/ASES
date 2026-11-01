# Provider registry v0 — implementation handoff

Date: 2026-11-01. Status: experimental schema, not activated for scheduling.

## Survey coverage

The candidate inventory was reconstructed from the October 28–31 VPS value and remote-development surveys and subsequent November 1 comparison. It includes HOSTKEY, Codespaces, Actions, Codex Cloud, Jules, Cloud Shell, Modal, E2B, Daytona, Vercel Sandbox, Cloudflare Sandbox/Workers/Pages/Containers, Railway, Cline Cloud, CodeSandbox, Replit, GitLab Workspaces, Cursor Background Agents, DevPod, Coder, Bunnyshell, Eclipse Che, Devbox, and historical Codeanywhere/Gitpod/Ona. Also reserve categories for local machines, inference-only, billing-only and storage-only providers. Candidate inventory is not account verification.

## Extensibility decision

The strict versioned envelope identifies provider, revision, lifecycle, products, typed meters, provenance-stamped facts and cross-product relationships. Products use generic capability records with open-ended `type` and `parameters`; unknown execution semantics can be represented without inventing a VM. A product can be `other` until its semantics have a reviewed adapter. Provider-specific metadata lives in namespaced extensions; extensions **must not** override safety-critical core fields.

Meter identity includes an explicit unit, measurement basis and accounting period. No conversion between active CPU, wall time, core hours, memory-hours, storage, model tokens or currency is implicit. Supported configurations are enumerated, but opaque managed runtimes can omit them. Account entitlements, observed balances, provider billing data and prices must be separately sourced and timestamped.

## Committed research artifacts

- `research/provider-registry/manifest_v0.py`: strict Python envelope validator.
- `research/provider-registry/test_manifest_v0.py`: 18 contract tests including malformed core fields, duplicate IDs, unknown facts, provenance, and a fictional quantum execution type.
- `research/provider-registry/candidate_inventory_v0.json`: survey-derived inventory with no fabricated quotas.

## Verification status

The files are committed, but **these 18 tests have not yet been executed**. The working container could not resolve raw.githubusercontent.com, so a clean-checkout execution was not available during this turn. They must not be represented as green or red–green verified. The next step is running the tests in a checked-out repository, recording a behavioral RED baseline for each new guard, and applying targeted mutations. Add cross-reference validation for product relationships, pricing semantics, capability adapter contracts, lifecycle transition rules and account-scoped entitlements before any scheduler integration.

## Source checks

- https://docs.github.com/en/billing/concepts/product-billing/github-codespaces
- https://docs.github.com/en/codespaces/about-codespaces/understanding-the-codespace-lifecycle
- https://vercel.com/kb/guide/vercel-sandbox-vs-e2b
- https://developers.cloudflare.com/sandbox/platform/pricing/
- https://developers.cloudflare.com/sandbox/
- https://sandbox-sdk.app/docs/providers

The independent Sandbox SDK comparison illustrates adapter-level variation, but its catalog is not itself an authoritative provider contract. Official vendor documentation and account APIs remain the authority for admission-critical facts.
