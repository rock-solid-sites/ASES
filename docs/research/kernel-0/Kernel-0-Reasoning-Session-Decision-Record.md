---
title: Kernel-0 Reasoning Session Decision Record
program: EDASES
layer: Research
document_type: Decision Record
status: Active
authority: Derived
canonical_repository: ASES
last_updated: 2026-09-26
---

# Kernel-0 Reasoning Session — Decision Record

## Purpose

Record how the current Kernel-0 reasoning program should be run without contaminating the derivation itself.

This document is orchestration guidance. It should not be supplied to the first open frontier-reasoning pass.

## Current phase

The immediate problem is primarily a reasoning and reduction problem, not a building task.

Implementation follows only after the semantic target is stable enough that realization comparisons become meaningful.

## Evidence preparation

The primary neutral input is `Kernel-0-Evidence-Packet.md`.

It contains settled requirements and boundaries while deliberately avoiding:

- candidate primitive vocabularies;
- preferred decompositions;
- implementation choices;
- anticipated answers;
- long lists of known counterexamples;
- directions about where a conceptual failure is expected.

Historical designs remain available as provenance and mechanism sources but are not part of the initial reasoning frame.

## Orchestration roles

Sol is the default orchestrator and synthesizer for this program.

Use Sol for:

- source reconciliation and provenance checks;
- requirement bookkeeping;
- synthesis;
- comparison with known historical cases;
- ordinary design reasoning;
- deciding when a question has become sufficiently bounded for a targeted investigation;
- maintaining project documents.

Cheaper bounded subagents may be used for retrieval or narrow factual checks where useful.

Astra is reserved for genuinely frontier-level reasoning where an open answer could materially change the architecture.

## First Astra pass

Invoke Astra after Sol has verified that the evidence packet faithfully represents the settled project requirements.

The first Astra pass is open derivation.

Supply:

- `Kernel-0-Evidence-Packet.md`;
- a compact task instruction.

Do not supply:

- this decision record;
- historical candidate primitive lists;
- a checklist of expected failure modes;
- a proposed Kernel-0 schema;
- known reviewer conclusions;
- a preferred decomposition;
- a preferred software or processorless realization.

The purpose is to discover what model Astra derives from the requirements with minimal anchoring, including distinctions or problems not already anticipated.

## Sol reconciliation

After the first Astra result, Sol reconciles it against the evidence packet and relevant project evidence.

At this stage it is appropriate to use known requirements and historical counterexamples systematically.

Distinguish:

- conclusions supported by the evidence;
- genuinely new useful distinctions;
- unnecessary added structure;
- requirements the proposal cannot represent;
- unsupported assumptions;
- unresolved contradictions.

A concrete Kernel-0 candidate should emerge only after this reconciliation.

## Work Unit adequacy test

Test the reconciled candidate against the Work Unit as the first demanding architectural consumer.

Do not assume Work Unit, Attachment Point, or Execution are themselves Kernel-0 objects.

The question is whether their settled guarantees can be supported without unnecessarily enlarging Kernel-0.

## Later Astra pass

Invoke Astra again only when there is a concrete reconciled candidate worth attacking.

Keep the prompt sparse and open. Ask Astra to falsify, reduce, or expose missing assumptions in the candidate without telling it which known defect classes to search for.

Known regression cases should be verified separately rather than used to define Astra's search space.

## Prior-art and mechanism research

Do not reopen broad kernel, OS, verification, or hardware surveys during the initial derivation.

If reduction leaves a concrete unresolved semantic question and prior art could materially answer it, perform a narrow mechanism-level search targeted to that question.

## Realization boundary

Do not select a language, compiler, ISA, operating system, verified software stack, processorless implementation, FPGA/RTL design, or other realization during the initial derivation.

Realization alternatives are a separate comparison after Kernel-0 semantics survive reasoning and adequacy review.

The later minimal-TCB / processorless direction is important as a realization hypothesis because it may remove assumptions from the trusted path. It is not a semantic premise for Kernel-0.

## Prompting policy

Follow `skills/prompt/SKILL.md`.

In particular:

- stable meaning belongs in project context;
- the task prompt should contain only the current delta;
- avoid unnecessary concept introduction;
- avoid telling an open reviewer where a problem is expected;
- expose genuine ambiguity rather than resolving it through prompt prose;
- use a clear completion condition without prescribing the reasoning path.

## Intended progression

```text
evidence verification
    ↓
open Astra derivation
    ↓
Sol reconciliation
    ↓
Kernel-0 candidate
    ↓
Work Unit adequacy test
    ↓
open Astra falsification / reduction
    ↓
revised semantic candidate
    ↓
realization comparison
```

This is a research progression, not a mandatory bureaucracy. Skip a step when its purpose is already satisfied by stronger evidence.

## Reasoning-phase stopping condition

The current phase is complete when there is a Kernel-0 candidate for which:

- retained distinctions have explicit necessity arguments;
- claimed guarantees are representable and testable;
- the relationship to the Work Unit is understood;
- material uncertainty is explicit;
- no implementation choice is being used to hide an unresolved semantic question.

If the evidence does not justify a unique model, record the competing models and the smallest experiment or reasoning question that discriminates among them.
