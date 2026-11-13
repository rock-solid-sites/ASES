---
title: Software Customization and Upstream Compatibility Method
program: ASES
layer: Methodology
document_type: Methodology Specification
status: Active
authority: Canonical
canonical_repository: ases
depends_on:
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
related_documents:
  - docs/standards/Documentation Standard.md
  - docs/methodology/State-Model Applicability and Reuse Method.md
consumed_by:
  - AGENTS.md
  - third-party software integration and upgrade workflows
  - forks, plugins, extensions and connectors maintained under ASES
last_updated: 2026-11-13
---

# Software Customization and Upstream Compatibility Method

## Purpose and governing decision

**Customize software without losing the ability to consume upstream improvements promptly.** The normal target is the **latest stable published upstream release**, including its new features, fixes, security updates and data migrations. A private integration is not successful if it works today but makes ordinary upstream releases prohibitively difficult to adopt.

This governs forks, patches, plugins, connectors, themes, adapted open-source applications, internal software integrations and deployment-specific overrides. It supplements the bounded-build, upstream-awareness, realization-selection and evidence rules; it is not a new software architecture or a mandate to deploy unverified releases automatically.

**Default:** keep the upstream application unmodified, express local needs through documented configuration or stable extension interfaces, and treat upstream code as replaceable. A temporary older version is an explicit exception, with a known blocker and a next review condition—not an implicit maintenance plan.

## Decision procedure: smallest difference from upstream

Before implementing a customization:

1. **Identify the actually deployed version** and the latest stable published release; inspect newer upstream source, release notes, existing configuration, documented extension points, relevant issues and proposed changes. A current main branch is not automatically a released or safe production build.
2. **Reproduce the missing user-facing behavior** against an unmodified release in an isolated installation. Distinguish genuinely absent functionality from misunderstood options, wrong configuration, stale data, a deployment defect or a broken test assumption.
3. **Ask whether the customization is necessary.** Remove obsolete overrides, unused components and duplicate abstractions before adding anything.
4. **Choose the lowest-maintenance mechanism that meets the requirement:**
   - supported settings, UI options, APIs or existing native functionality;
   - a narrowly scoped upstream fix/feature contribution when it benefits upstream users;
   - a separately versioned plugin/extension using supported interfaces;
   - a bounded, explicitly tracked source patch, only when the above are inadequate.
5. **Keep the modification isolated.** Do not edit downloaded/minified release bundles, monkey-patch private application APIs, rely on repeated DOM rewriting, or replace upstream migration logic as routine integration mechanisms. An exceptional workaround requires a demonstrated necessity, owner, regression test and removal condition.
6. **Prefer the smallest final difference.** A successful prototype is not automatically a maintainable dependency. Delete exploratory scripts and temporary UI shims once the validated mechanism is available.

Upstream-first does **not** mean every local preference should be submitted upstream. Submit broadly useful capabilities; keep branding, private workflows, secrets and narrowly local policies in configuration or extensions. For substantial changes, discuss scope with maintainers before writing a large PR; acceptance is not guaranteed.

## Source, configuration and data boundaries

The integration should have three clearly separated parts:

- **Upstream product:** a verifiable official release or a traceable source checkout, never an undocumented copy of a modified compiled bundle.
- **Local configuration/extension:** deployed independently, with a short record of its purpose, supported interface and removal/upgrade method.
- **User data:** backed up independently and portable through supported export/import or migration mechanisms, with preserved identities, relationships, authorization rules and content.

**Never confuse copying records with copying a working database.** Table contents alone may omit indexes, constraints, triggers, defaults, views, generated structures, permissions or schema-version state. A migration ledger is not evidence that migration effects actually occurred. Build the destination schema with the destination release's authoritative migrations, import canonical data only after checking compatibility, and verify actual constraints and real application queries. Preserve a recoverable original before destructive or irreversible transformations.

Use new databases/deployments for upgrade rehearsal when practical. Do not mutate production or broaden access merely to make a test pass.

## Upgrade procedure and proportionate evidence

An upgrade should normally be a bounded operational operation, **not a new software project**:

1. Compare the installed and latest stable releases; list only relevant breaking changes and our small local differences. Check whether upstream now supersedes each difference; remove it when possible.
2. Obtain a recoverable backup and identify rollback, then bring up the clean current release using its native deployment and migration path.
3. Validate the smallest real, authenticated workflows that could disprove success: log in, see representative existing data, navigate to and interact with core features, perform a reversible authorized write if appropriate, and verify required connectors. Check data integrity and permission boundaries where relevant.
4. Apply only still-necessary local configuration/extensions; test their actual user-visible effect after each addition. Do not start with the entire old patch stack.
5. Promote after user-relevant gates pass. On failure, stop promotion, record the simplest discriminating reproduction and repair that narrow defect. Treat mocked browser tests, unit tests, SQL integrity checks and passing CI as supporting evidence **not substitutes** for live acceptance.

Verification should be *proportional*: tests should address actual failure risks and be cheap enough to run on routine releases. It is a failure of the method to build an expansive test framework while basic navigation or login has never been exercised.

## Lightweight customization register

For each ongoing non-native difference, retain one compact entry identifying:

| Field | Record |
| --- | --- |
| Need | User-visible result unavailable upstream |
| Mechanism | Config, extension, upstream PR, or justified local patch |
| Version/interface | Current upstream release and exact supported boundary |
| Portability | How to take the next release without rebuilding the feature |
| Exit condition | Upstream replacement, removed requirement, or accepted contribution |
| Evidence | One relevant working live check and any specific negative gate |

Keep the register next to the affected integration. Do not create a centralized service or rich governance database solely to maintain it. Revisit entries when upgrading and when upstream provides the missing capability.

A temporary version pin or fork must additionally record the precise incompatibility, available workaround, exposure/security consequences, and next decision/retest trigger. “Our patches are hard to port” is a defect to fix, not a valid indefinite pin.

## Contribution versus private extension

Favor upstream when a feature aligns with the product's scope, generalizes beyond our workflow, respects its security/data model, and can be tested and maintained alongside other first-party features. Start with the smallest demonstrable capability and the maintainer's preferred discussion route. A contribution should not be framed as entitlement to merge; maintain a removable local version only if its ongoing cost is justified.

Choose a local extension when the feature is highly specific, experimental, optional in a way upstream does not want to support, or can be implemented through stable public APIs without changing core behavior. A permanent fork is a separate conscious product decision, carrying an explicit resynchronization/merge strategy; it must not arise accidentally from accumulated patches.

## Failure cases informing the method

- **Crosslink and OpenCode:** retained older forks/customizations obstructed access to upstream features. The prevention rule is to treat upstream currency as a requirement and challenge every local divergence on every significant upstream change, instead of reflexively repairing an aging fork.
- **Projektor (November 2026):** an apparently simple upgrade to v0.11.1 grew into modified Worker bundles, DOM overlays, multiple staging-only workarounds and misleading green tests. A database copy omitted indexes needed by authentication, despite passing integrity checks. A sidebar DOM observer repeatedly moved links and impeded interaction, despite earlier browser smoke tests. Corrective approach: clean official release, fresh upstream schema, data-only import with constraint checks, the smallest live acceptance pass, and only then justified portable customizations.
- **General pattern:** preserving a workaround becomes the project, while the original product and upstream improvements become secondary. Re-evaluate the need and delete divergence before expanding infrastructure to support it.

These examples are lessons about our integration choices; they are not evidence that upstream software itself is deficient.

## Standing rule and exceptions

At the start of work involving a third-party application, verify upstream release and relevant changes. On each subsequent upgrade, first try a clean supported path. **Stay current by default, but never deploy untested code or perform automatic destructive migrations.** If a release cannot safely be adopted, keep the known-working version temporarily, record a falsifiable blocker and the cheapest retest path, and prioritize removing the blocker.

No production cutover, OAuth reauthorization, secrets movement or connected-client handoff is authorized solely by this policy.
