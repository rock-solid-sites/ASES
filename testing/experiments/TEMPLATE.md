---
title: Empirical Testing Experiment Card — Template
program: EDASES
layer: Research
document_type: Research Protocol
status: Draft
authority: Experimental
canonical_repository: ases
depends_on:
  - testing/README.md
last_updated: 2026-11-19
---

# Experiment card — copy and fill only when there is a real test

**Status:** HYPOTHESIS / EXECUTED / REPRODUCED / REJECTED / BLOCKED (choose one). This is a noncanonical research record, not a new execution gate.

**Question / value of learning:** What future testing decision changes based on this result?

**Object and authority:** Owner repo, source SHA or version, actual shipped vs experimental target, claim source, affected interface/trust boundary. Do not silently convert product policy proposals into guarantees.

**Falsifiable claim:** State the forbidden condition and the independent observations that would discriminate. Record untestable/ambiguous claims explicitly.

**Baseline and method:** Cheapest relevant deterministic control; added property/history/crash/browser/reviewer technique; why extra machinery is warranted, expected cost and bounded stop condition.

**Instrument validation:** Independent oracle, good/bad controls where constructible, test-only mutants distinguished from actual product, semantic branch/transition categories and minimum sensitivity check.

**Observed result:** Exact outcome classification (including BLOCKED, REJECTED_ORACLE or NO_DISCREPANCY), minimal case/trace, source+CI/command pointer, cost/latency if measured. No inferred results or green-run-only claim.

**Lesson and transfer:** Which assumption failed? What precise new practice should another project adopt? What different project/claim has tested transferability?

**What was not tested / disposition:** Out-of-scope authority, unverified environments or interfaces, independent reviewer state; retain/modify/reject method, linked Work Notes task if follow-up remains.

Store domain fixtures, runtime code and bulky logs in their owning repos. Avoid reconstructing a session chronology.
