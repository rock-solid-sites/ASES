---
title: Kernel-0 Assurance Frozen Review Packets
program: EDASES
layer: Research
document_type: Research Protocol
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 567
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
consumed_by:
  - Independent Kernel-0 assurance reviewers
---

# Frozen Phase 1 packet

Exact tree: `1149fb124d7306f834fb7e9383ccaf7c79c5b7fa`. Extract only the files below from that commit; subsequent
branch changes do not change this packet. Source digests are in the two result
files. This index is not a completed independent review.

- Kernel-0-Abstract-Semantics.md; Kernel-0-Verification-Obligations.md
- Kernel-0-Crash-Recovery.md
- kernel0_finite_model.py; kernel0_service.py
- kernel0_recovery_model.py; kernel0_recovery_service.py; kernel0_recovery_check.py
- Kernel-0-Crash-Recovery-model-results.json
- Kernel-0-Crash-Recovery-experiment-results.json

All paths are relative to `docs/research/kernel-0/`.

Review prompt: Independently try to falsify the declared process-loss profile.
Derive required observations before reading the report's conclusions. Check that
all erased state is absent from recovery input; stale producer association cannot
be reconstructed by assertion; acknowledgement/publication cannot precede the
recoverable commitment; retained content is usable; and the model's ghost oracle
never supplies implementation state. Attack whole-effect/currentness correspondence,
not just state invariants. Separate a violation inside the profile from an exposed
trust assumption. Challenge bounded model adequacy and non-vacuity. Return the
shortest reproducible counterexample, or a bounded NOT FALSIFIED result stating
what was actually tested. No passing self-review is independent evidence.

WHY: storage/binding mediation remain assurance-sensitive. WHAT: exact source and
evidence tree above. HOW CERTAIN: packet ready, review not performed.
WHAT-NOT-TESTED: independent judgment and whole-stack formal refinement.
