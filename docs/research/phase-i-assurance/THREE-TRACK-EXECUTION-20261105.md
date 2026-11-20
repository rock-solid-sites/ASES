# Three-track Phase I assurance orchestration (experimental, 2026-11-05)

Status: proposed operating arrangement for the research branch; not an adopted ASES-wide policy.

## Shared objective
Test and where possible formally prove frozen Phase I claims. Distinguish theorem/model proof, executable implementation tests, refinement evidence, and untested environmental assumptions. No finite suite implies universal correctness.

## Track A — ChatGPT + GitHub Actions
Owns the common evidence contract, CI configuration, test matrix, reproducibility, checker mutation and qualification, cross-track evidence review, and contradiction ledger. The existing six SHA-pinned replays and F1/F4 checker mutations are first examples. Use GitHub Actions for non-secret bounded workloads. This track is **not** the formal independent reviewer of artifacts it authored.

## Track B — Sol / Codex Cloud
Reserve for high-value reasoning: formal invariant/specification extraction, refinement mapping between abstract model and executable implementation, model-checker counterexample interpretation, architecture-level trust-boundary failures, and independently conceived integration scenarios. Do not consume Sol time on routine repeated CI runs or copying evidence.

## Track C — cheap agents / isolated remote compute
OpenCode and Phoenix Grove models can generate hypothesis-driven automata/property-based/fuzz/differential scenarios on disposable GitHub Codespaces or Modal workers. Use a fixed claim and source SHA, bounded CPU/time/memory, deterministic seeds and minimized counterexamples. Agents are untrusted builders of tests and cannot certify their own correctness. Verify actual provider availability, credentials, usage quotas and environment launch before claiming a worker is operational. Avoid agent-generated executable instructions on privileged hosts or access to production secrets.

## Work packets
Each packet must specify: claim ID, frozen source/spec SHA, prior evidence IDs, competing hypotheses, expected falsifier, exact executable interface, permitted mutations and environments, CPU/time budget, independent checker requirements, artifact manifest, stop conditions and next handoff. One track owns changes to any shared source file; parallel agents work on disjoint branches/worktrees. Integrate only after independent review and conflict resolution.

Initial packets:
- A1 (chat): run F1/F4 checker mutation audits; expand to remaining checkers and collect durable evidence.
- A2 (chat): portable manifest and archive-failure self-tests; second CI provider reproduction when accessible.
- B1 (Sol): F1/F3/F4 integration proof obligations, explicit abstract-to-native refinement, ambiguous ACK and currentness assumptions.
- B2 (Sol): Kernel-0 formal model/toolchain trust, temporal induction premise analysis and proof gaps.
- C1 (cheap): derive independent state-machine model for F3 L5/L6 transitions; enumerate bounded interleavings and minimize counterexamples.
- C2 (cheap): independently generate property-based F1 atomicity/crash-boundary tests with synthetic SQLite stores; distinguish durable commit from native resource visibility.
- C3 (cheap): generate F4 competing-writer, receipt-loss and rollback histories; compare implementation to a separately written reference model.

## Evidence contract and conflict handling
Use the proposed ASES Testing and Assurance Method as a **pilot**, not global policy. Separate execution status, claim conclusion, evidence quality, archival completeness, and authorized acceptance. Preserve raw evidence, before-run reasoning, source/toolchain versions, exact seeds, and negative controls. Cross-provider replay proves reproducibility, not oracle independence. Do not let an agent see another agent's conclusions before a designated clean-room review. Never silently turn an unproved assumption into an invariant.

## Resource allocation
GitHub Actions: baseline deterministic CI, matrix runs and repeatable bounded fault tests.
Codespaces: interactive agent development, reproducible small/medium model exploration and fuzzing.
Modal: disposable parallel compute and scalable parameter sweeps once actual account/CLI/API launch is confirmed.
Codex Cloud: scarce reasoning and difficult independent investigations.
Cheap model API: generate test cases, review hypotheses and analyze minimized traces; execute generated code only in isolated ephemeral environments with pinned inputs.

Record actual resource use (runner minutes, CPU-hours, storage, model tokens/cost when available) for the future resource solver. Model output volume is not itself a correctness metric. Prefer independent discriminating coverage and proof-obligation closure over repetition counts.

## Acceptance milestones
1. Each packet has a frozen claim and executable acceptance surface.
2. Independent checker self-tests reject planted invalid traces and accept valid neighbors.
3. Baseline, perturbation and recovery evidence are distinguishable.
4. Formal proof certificates/logs are preserved with model, assumptions, version and abstraction boundaries.
5. All unresolved gaps have owners, evidence links and explicit NOT_TESTED classifications.
6. Evidence is archived outside CI provider and archive integrity is checked; until then archival qualification remains incomplete.
7. Only an authorized decision can accept a claim or promote a proposal.
