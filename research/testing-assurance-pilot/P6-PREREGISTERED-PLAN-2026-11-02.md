---
title: EDASES P6 — Evidence Semantic Separation and Instrument Qualification
program: EDASES
document_type: Preregistered Experiment Plan
status: Frozen Before New Test Execution
date: 2026-11-02
authority: Experimental
---

# P6 — Test whether the evidence record itself resists unsupported conclusions

This is an **experimental evidence-contract qualification**, not a global policy or a new phase. It reuses the *original immutable P5 CI ZIPs*, including the run with a bad test fixture. It must not edit either earlier P5 plan, implementation, or historical record.

## Why this experiment

P5's first CI job failed its assertions, but later inspection showed a claimed over-cap fixture (`charge_cents=50`, `spend_cap_cents=80`, empty journal) was actually allowed. The runner correctly executed an invalid expectation; the execution failure alone did **not** establish a product defect. Subsequent successful CI corrected the fixture to `charge_cents=90`. Both original job ZIPs were independently stored in ASES.

A proposal about the ontology of testing, debugging and decisions should be tested against this real episode before defining its vocabulary as canonical.

## Fixed objects, frozen hypotheses and controls

Objects: P5 failed source job `17650922007` (pipeline `3015831687`), corrected source job `17650933508` (pipeline `3015833489`), the original artifact hashes fixed in `evidence/P5-ARCHIVES-MANIFEST-2026-11-02.json`, and the original P5 plan and sources.

Prospective hypotheses (falsify if contrary output is observed):

1. An independent, source-neutral record model can distinguish at least **run execution**, **test assertion**, **instrument/oracle qualification**, **claim interpretation**, **archive integrity**, and **authorized decision** without a single overloaded `status` and without falsely representing human approval.
2. The two original P5 artifacts can be reloaded **byte-for-byte**, individually rehashed and checked against their retained manifest. The failed run must remain failed in the raw result rather than be overwritten by the later diagnostic.
3. The `charge=50, cap=80, empty-journal` expected DENY is contradictory to the frozen admission rule; `charge=90, cap=80` is a legitimate over-cap denial. Distinguish a test-oracle correction from a changed product rule, including what was observed versus what was inferred.
4. Ordinary source-derived validation should reject negative controls: unauthorized decision, a missing event linkage, missing required archive verification fields, invalid enum, fabricated independent reviewer, conflated assertion and product defect, and an archive integrity misclaim.
5. Positive controls for a valid failed run and a valid successful run remain accepted; an intentionally failed test is a **valid observation** when represented honestly.
6. Output includes exact source pointers, deterministic reconstruction, local execution cost, archive status and unresolved independence. The complete source artifacts remain readable; copied result objects are derivatives, not substitutes.

## Selected method and bounded execution

Use a lightweight **typed event envelope**, not a new database. Each event has a stable ID, kind, attributable source, links to object/run/claim and a typed payload. Immutable observations and later interpretations are separate append-only events. Keep policy adoption and human acceptance **NOT_RECORDED** until a real authorized decision exists.

Use the Python standard library to replay P5's two ZIPs and recompute SHA-256; add a local schema validator with explicitly implemented constraints (do **not** claim it is an exhaustive JSON Schema validator). Run deterministic positive/negative fixtures against the validator. Where a later test asserts a new interpretation, attribute it as a **research interpretation**, not as an independent reviewer or source fact.

No agents, providers, resource budgets or production systems will be launched/changed for this pilot. A Python-only isolated GitLab CI run is an eligible low-cost verification route; do not run Rust/Haskell builds again just to test the evidence representation.

## Method evaluation and acceptance

Measure: invalid records rejected by the correct reason, valid controls accepted, source artifact SHA matching, fidelity of original red and corrected green chronology, elapsed test time and output bytes. A green schema check is not evidence of correctness of all possible future records. A negative control accidentally passing is a method defect.

Record setup/instrument errors as ERROR, assertion mismatches separately, interpretation/claim as SUPPORTED_WITHIN_SCOPE or UNRESOLVED as justified, archive status separately, and operator decision as NOT_RECORDED. Do not silently change canonical AGENTS, VSDD, Orchestrator, Ontology Reviewer, the testing proposal or resource-solver specification.

**Promotion: DEFER**, pending real independent source-first review, additional unlike records, cost evaluation and authority reconciliation. A prospective clean-room review must not be simulated using this same conversation.
