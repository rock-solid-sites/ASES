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


# Frozen Phase 2 packet

Exact tree: `788c34ae267d4f274e06150610924deac24bf437`. Include base semantics/obligations, Phase 1 profile and
all source files named by `Kernel-0-External-Effects-experiment-results.json`,
plus `Kernel-0-External-Effects.md`, `kernel0_effect_model.py`, its model results
and `kernel0_effect_experiment.py`. This is a packet, not a review verdict.

Review prompt: Try to cause a sink consequence without a committed matching
obligation, lose a committed obligation across declared failures, or authorize
an old-evidence decision after revocation. Challenge the monotone-slot assumption,
mediator trust, temporal witnesses, and interpretation of irreversible acceptance
versus visibility. Do not assess it against an unclaimed exactly-once or
sink-current contract; explain separately which stronger claims its traces refute.


# Frozen Phase 3 packet

Exact tree: `018fc72daa9a5b902f1b6140fbf5e033aee85ac5`. Include base semantics/obligations, the three phase
reports, `kernel0_composition_model.py` and `Kernel-0-Composition-results.json`.
Review prompt: determine whether any allegedly independent operation has a hidden
cross-domain guard/invariant dependency; attack domain scope, parallel-step
commutativity and recovery after a joint commitment. Distinguish invariant
preservation from exact whole-effect refinement. The result is model-only;
physical split-store recovery is explicitly unproved.
