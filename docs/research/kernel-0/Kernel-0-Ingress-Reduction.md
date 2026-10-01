---
title: Kernel-0 Fixed Ingress Assumption Reduction
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 576
last_updated: 2026-10-01
depends_on:
  - Kernel-0-Abstract-Semantics.md
  - Kernel-0-Verification-Obligations.md
  - Kernel-0-Direct-RTL-Experiment.md
  - Kernel-0-Direct-RTL-Result.md
  - Kernel-0-Finite-Model.md
  - Kernel-0-Re-Minimization.md
consumed_by:
  - Kernel-0 realization assumption assessment
implements: []
implemented_by: []
supersedes: []
---

# Bounded experiment protocol and result

Baseline: `c03bf1c470e54f51c299cb3347c547eeeae0e5ce`, branch
`codex/kernel-0-direct-rtl-00086d17`. Work is isolated on
`codex/kernel-0-ingress-reduction-c03bf1c`. All governing inputs and the entire
direct RTL artifact remain byte-for-byte unchanged. This is a research witness,
not a new Kernel definition or execution-engine architecture.

## Decision recorded before implementation

Test one reduction: eliminate the runtime ingress authenticity verdict and
caller-carried authority label by fixed, separately protected context/management
ports. Keep the synchronous timing contract. This replaces an unspecified
per-request classifier with fixed gates and an explicit static port-access
premise. It does not eliminate trustworthy origin, prove physical isolation,
or claim a universally weaker physical trust boundary.

Before implementation, `ingress-reduction/preflight.py` tests whether removing
all trustworthy distinctions is possible. After establishment, grant a0 and
replace a0 with a1. The same work payload must deny on a0 and commit on a1.
If both callers can present the same current-authority observation, a fixed
decision cannot deliver both required outcomes. Always-deny loses the bounded
model's non-vacuity. The minimum residual requirement is one non-confusable
admission observation, here realized as exclusive access to fixed lanes.

Synchronous timing supplies whole-envelope association, current-view validation,
whole-state publication, and a common order for interacting commitments. Removing
it from the existing circuit without replacement permits a valid but wrong
intermediate state: an independent-profile pair `(0,0)->(1,1)` can expose `(1,0)`.
A torn request between pair values 0 and 3 can also encode valid value 1. Neither
is rejected merely by checking the state invariant. These are abstract cut
witnesses, not simulations of analog behavior. A global periodic clock is not a
semantic requirement; coherent completion and observation are. A clockless
replacement would need a separate whole-envelope capture/completion protocol,
retained state and timing/observation refinement. Merely adding a handshake or
independent bit synchronizers would not establish that refinement. It is not
the selected experiment.

## Boundary and stopping rule

Five input lanes are permanently associated with a0, a1, a2, a3 and manager.
Each has only an 11-bit effect payload and a valid signal. The port number does
not itself confer rights: the unchanged Kernel state still decides eligibility.
Only an exactly-one-valid edge submits a proposal. Zero or several valid lanes
means no submission, no resolution and no state change. Sources may retry;
there is no fairness, simultaneous-source service or buffering guarantee.

No processor, interpreter, program store, mutable routing table, new authority
state, scheduler, arbiter with priority, or runtime controller will be added.
Stop after explicit baseline correspondence, bounded oracle regression, clocked
attack/continuation traces, synthesis and checker-sensitivity evidence succeed;
or preserve a concrete obstruction if they fail. Physical isolation and timing
remain outside this digital experiment. Do not undertake a second reduction.

Results and the final mechanism ledger will be appended after verification.
