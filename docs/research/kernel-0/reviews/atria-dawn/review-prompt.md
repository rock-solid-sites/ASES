Conduct a clean-room post-build review of the supplied Kernel-0 realization.

The packet contains, and is limited to, the current Kernel-0 abstract semantics, verification obligations, finite-model specification and executable model, concrete service, and verification harness.

Treat the packet as the complete review context.

**Claim:** `kernel0_service.py` realizes the supplied Kernel-0 semantics within the finite executor-loss profile represented by the supplied model.

The claim assumes trusted bootstrap and initial management authority; the fixed finite policy and bounds represented by the model; correct Python/standard-library and lock behavior; Unix process, descriptor-isolation and stream-delivery behavior; and a service that remains alive with its memory intact.

It does not claim service crash/restart or storage-corruption safety, arbitrary protected external effects, unbounded identities/content/delegation, progress or fairness, exactly-once processing, exclusion of an old physical producer that obtains genuinely new current authority, or protection against compromise of the trusted runtime/OS boundary.

Try to falsify the claim.

Treat the service and verification harness as separate objects of scrutiny. Passing tests count as evidence only to the extent their oracle and abstraction are sound. Use the supplied semantics as the contract rather than substituting a preferred architecture or stronger guarantee.

Prefer a decisive concrete trace or source-level argument over a checklist of possible concerns. Distinguish any material finding as a semantic/model defect, realization/conformance defect, verification/oracle defect, undeclared trusted assumption, or behavior already outside the claim.

Return **FALSIFIED** if you can substantiate a defect in the stated claim; otherwise return **NOT FALSIFIED**. Give the minimum evidence supporting the conclusion and state any material unresolved uncertainty.
