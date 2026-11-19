---
title: ASES Empirical Testing Laboratory
program: EDASES
layer: Research
document_type: Research Framework
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
related_documents:
  - docs/research/Guarantee-Driven Testing and Goal-Substitution Resistance.md
  - docs/methodology/ASES Bounded Project Build Method.md
last_updated: 2026-11-19
---

# Empirical testing laboratory

**Purpose:** improve how software is tested by running bounded experiments, falsifying claims, comparing techniques and carrying forward lessons that change future engineering. This directory is a **research workbench**, not a new canonical testing standard, a chronology of agent activity, or a replacement for executable test suites.

## Authority and navigation

- **Active authority:** [Constraint-Driven Realization and Assurance Selection Method](../docs/methodology/Implementation%20Realization%20and%20Assurance%20Selection%20Method.md) and [ASES Bounded Project Build Method](../docs/methodology/ASES%20Bounded%20Project%20Build%20Method.md). Consult relevant VSDD and project-specific acceptance requirements. A passing experiment does not change them.
- **Research foundation:** [Guarantee-Driven Testing and Goal-Substitution Resistance](../docs/research/Guarantee-Driven%20Testing%20and%20Goal-Substitution%20Resistance.md), still experimental. Its object → attributable claim → evidential criterion → technique ordering remains the starting constraint.
- **Proposals not adopted:** [Testing and Assurance Method proposal, draft PR #4](https://github.com/rock-solid-sites/ASES/pull/4) and [cross-project property/stateful pilot, draft PR #58](https://github.com/rock-solid-sites/ASES/pull/58). They are evidence to review, not active instructions. Do not copy or install a second skill.
- **This workbench:** [selection candidate](methods/selection-candidate.md), [experiment card](experiments/TEMPLATE.md), [November 2026 bounded experiment](experiments/2026-11-cross-project-pilot.md), [transferable lessons](lessons/2026-11-cross-project-lessons.md), and [minimal counterexample index](counterexamples/README.md).
- **Execution tracking:** Work Notes `WNASES-14` is the setup task; `WNASES-10` is the independent methodological review/promotion gate. Projektor retains human roadmap and decisions.

## Proposed empirical loop (experimental, not mandated)

1. **Identify the actual object and authority.** Pin source and whether it is shipped behavior, an experimental candidate, a test fixture, or a third-party contract. Derive a falsifiable claim before choosing a fashionable tool.
2. **Choose the cheapest discriminating test.** Use a plain assertion if it separates good and bad outcomes; move to generated inputs, stateful histories, concurrent processes, injected failures, external interfaces, or independent reviewers only for a missing evidential dimension.
3. **Qualify the instrument.** Where legitimately constructible, show one compliant control passes and one deliberately violating control fails for the intended reason. Challenge the oracle itself.
4. **Execute under bounded authority.** Preserve source and dependency versions, command/seed or operation trace, environment and verified outcome. No live booking, settlement, deployment or privileged action without separate approval.
5. **Classify before repairing.** A failure may be an implementation defect, invalid oracle, unavailable provider, flaky execution, untestable claim, or incomplete evidence. Never change a requirement to make a test green.
6. **Keep the smallest reusable result.** Retain a minimal replay or source-pinned counterexample, independent verification, changed practice, what was *not* verified, and a source link. Discard duplicative logs and chronology unless needed for a real audit or reproducibility.
7. **Review and test transfer.** Try the technique on a materially different object; compare marginal detection value and cost to the deterministic baseline. Promote only through an independently reviewed update to the *existing* canonical method; supersede conflicting instructions rather than layering them.

## Record and retention rules

A useful experiment card contains: **object/claim authority; potential falsifier; isolated controls and oracle; actual source/CI evidence; result classification; changed practice; boundary/unknown; next discrimination**. See the [card template](experiments/TEMPLATE.md). Accept **NO_DISCREPANCY**, **CONFIRMED_DISCREPANCY**, **INCONCLUSIVE**, **BLOCKED**, **UNTESTABLE**, and **REJECTED_ORACLE** as legitimate outcomes—tests or defect counts are not goals.

Project-specific production and experimental tests remain with their owner (for example, HMS and Trip'n). This workbench references the minimal code/evidence rather than copying it. A `tools/` directory is intentionally absent until repeated experiments justify a maintained reusable tool. Do not add empty directories, bulk generated histories, expired artifact copies, or overlapping active skills merely to make the lab look comprehensive.

**Iteration criterion:** a proposed addition must improve discrimination, reduce unjustified confidence or cost, resolve a known failure mode, or retire an ineffective technique. New results that do none of these do not need a permanent entry.
