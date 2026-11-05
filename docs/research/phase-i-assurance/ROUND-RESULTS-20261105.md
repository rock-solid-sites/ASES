# Phase I chat-track assurance round — 2026-11-05

Status: experimental research evidence, NOT adopted ASES policy and NOT general correctness certification.

## Baseline and result

- Draft PR: https://github.com/rock-solid-sites/ASES/pull/8
- Full 20-job CI result: https://github.com/rock-solid-sites/ASES/actions/runs/42112410341 — 20/20 successful.
- Artifacts: 20 GitHub Actions artifacts reported at run completion, **30-day** platform retention (expiry around 2026-12-05); no independently verified off-provider archive.
- All changes isolated to `research/phase-i-ci-assurance-20261105`; original six source cases remain exact-SHA pinned.
- Six original process/SQLite replay jobs, six checker mutation audits, four bounded abstract model checks (F1, F3 L5, F3 L6, F4), three independently written concrete observation projections, one evidence-contract job.
- A green workflow is evidence of execution and selected self-checks, not proof of a generic F1/F3/F4 invariant.

## Bounded models (distinct abstract states, not implementation states)

| Model | Bound | States | Deliberately faulty variants found |
|---|---:|---:|---|
| F1 content/opaque evidence | 7 transitions | 181 | split COMMIT, premature ACK, misbound evidence |
| F3 L5 whole-move cut | 8 transitions | 10 | split publication, bypassed descendant ceiling |
| F3 L6 inventory | 8 transitions | 18 | detached scan |
| F4 local/published/ACK cut | 7 transitions | see run JSON | premature ACK |

All abstract control models passed their own bounded invariants; mutants produced traces exposing the specified violations. Positive neighboring schedules were also tested. Model construction and safety predicates are authored in this research track; their claimed oracle independence **has not** been formally qualified by a clean-room model reviewer.

## Independent concrete-observation projection

`concrete_projection.py` is separately implemented and never imports a pinned case's `check.py`. Each job regenerates raw evidence by executing the original SHA-pinned `probe.py`, then examines:

- **F1:** independent SQLite reader's raw view and opaque observation hashes, content/observation binding, recovery without original observation tuple, pre-commit old state and split-commit mismatch. Two different opaque observation worlds share identical content view; the model must distinguish the evidence.
- **F3 L5:** selected record bytes and CURRENT selector, actual post-kill cold selection, retained descendant ceilings and denied/accepted D writes. Split selected record with omitted ceiling is a counterexample, not a passing protected move.
- **F3 L6:** physical files and durable dependencies, held SQLite transaction vs detached inventory scan, creator result and removed unit state. Guarded exclusion and creator-first denial are positive neighbors; detached scan is a stranding counterexample.

Total target-specific recorded cases inspected by these independent projections: F1 5, F3 L5 6, F3 L6 3. Each projection rejects separate corrupt-byte and semantic-evidence controls. This establishes **selected trace consistency**, not a full refinement or linearizability proof across all execution histories.

## Evidence qualifications

- Six original checker mutation audits cover known semantic/evidence corruptions, not all faulty checker implementations.
- The evidence contract has 22 regression tests covering hashes, path traversal, symlinks, duplicate entries, booleans-as-size, tampering, failure classifications, independent controls and false archive assertions.
- Six replay jobs now hash per-case evidence in a case-scoped manifest, verify listed file readback, and bind PASS/FAIL to the actual test-step outcome. The manifest is **not self-hashed**; artifacts remaining outside its scope and GitHub artifact upload failures are separate concerns.
- `classify` is a conservative metadata classifier: no case is automatically ACCEPTED; claim quality requires explicit controls; archive completeness remains false without an independently implemented off-provider verification mechanism.
- Upload to GitHub Actions with 30-day retention is **not** durable evidence retention. Preserve ZIP exports and manifests in independently controlled storage and test retrieval before upgrading archive qualification.
- Distinguish a probe/checker failure, contradicting the claim, inconclusive execution, checker weakness, and missing/unverified archive.

## Unclosed proof obligations and next experiments

1. **Refinement:** derive observation maps between each abstract machine and concrete SQLite/journal/native-file behavior; prove or counterexample-search all transitions (not just selected final states).
2. **Native/concurrent faults:** uncooperative writers, multihost/root reuse, inode replacement, concurrent crash/kill windows, partial writes, fsync and real power interruption. A cooperative `flock` test cannot certify confinement.
3. **Authority/freshness:** separately rooted nonrollback witness, compromised/stale current cut, history monotonicity, key/lease/authority rollover and loss of publication receipt.
4. **Cross-component integration:** F1 accepted evidence consumed by F3 lifecycle and F4 publication/receipt behavior, with one causal trace and common typed identity across boundaries.
5. **Test oracle qualification:** independent clean-room spec and positive/negative controls. Reusing assertions or generated traces between teams can falsely multiply confidence.
6. **Evidence preservation:** off-provider encrypted archive, checksum verification on export and restore, retention policy and provenance linking to run/job/source SHA, with measured cost.
7. **Machine/environment diversity:** second CI executor / Python and SQLite versions / persistent filesystem; same checker repeated on another platform proves portability, not independence.
8. **Proof language:** map each abstract invariant to explicit preconditions, observable outputs, environmental assumptions, excluded faults and a falsifier. No empirical test count substitutes for proof of unbounded behavior.

The three-track handoff plan remains in `THREE-TRACK-EXECUTION-20261105.md`. Prefer economical GitHub Actions for deterministic small work before assigning long-running exhaustive searches to Codex Cloud or OpenCode/Modal. Keep failures and rejected controls, not just green summaries.

### Event-by-event refinement addendum (2026-11-05 23:30 UTC)

- Latest experimental workflow: https://github.com/rock-solid-sites/ASES/actions/runs/42128710686 — **20/20 successful** at commit `7f79bf1579fc81c289ff80aa7760c3dfe1ddefd6`.
- `trace_refinement.py` now reconstructs F1 SQL BEGIN/UPDATE/INSERT/COMMIT/crash/recovery, F3 L5 selected-record/cold recovery/activation/write, and F3 L6 competing creator/removal with process/SQLite event ordering. It rejects six planted invalid-history mutations per family; retained split-commit, split-selector, and detached-scan cases are counterexamples, not successful safe histories.
- `f4_trace_refinement.py` independently examines event-by-event F4 journal bytes, publication revisions, remote witness exchange, local acknowledged effects and obligations, receipt loss vs actual rejection, and cold-start cut refusal. Six invalid-history controls each for cut and receipt traces.
- Early F3 L5 and F4 extension CI runs failed because of newly introduced **refinement-checker schema mistakes** (timestamp wrapper, HTTP body location, obligation 201 subtype, and lost-receipt remote revision gap); fixed and rerun green. Preserve these failed-run artifacts as checker-debugging evidence.
- A chat-local evidence export contains 20 latest-run artifacts and six selected prior failure diagnostics. **26 ZIPs, 122 internal files, clean temporary-directory restore verified** with SHA256 for all members. Ten embedded replay manifests verifiable from downloaded bytes; eight F4 refinement outputs were generated after their original replay manifests, and two evidence-contract manifests reference repository source code outside their uploaded ZIP scope. The outer export manifest hashes all 122 internal files.
- **Not archived externally**: the export is still unencrypted and user-side persistent placement/restore has not been verified. Current GitHub artifacts remain subject to 30-day retention, and there is no authenticated IDrive e2 backup in this workflow.
- Next: hash F4 refinement files after they are generated (do not finalize case manifest prematurely), bundle all source artifacts in GitHub Actions, establish customer-controlled off-provider encryption+upload+restore, and perform full F1–F4 integrated refinement. None of these green results establishes universal correctness or nonrollback witness safety.
