# Phase I F1 targeted run record

Status: PARTIAL; bounded finite evidence only. No unbounded proof claim.

Source SHA-256 after the two narrowly scoped corrections: 265c4eb0e2105452a6aadf562a83b4ee1e343d600350c0c081cacad7d9843c68.

Environment: Python 3.11; VPS worktree only; 1,000,000-KiB virtual-memory cap; 120-second timeout per small check; explicit 10,000-state cap for the context exploration.

Syntax: python3 -m py_compile docs/research/phase-i-f1/phase_i_f1_model.py — PASS.

Before correction, bounded context engine-loss-and-recovery reached the counterexample (stop, activate_image): image became mounted while engine enforcement stayed down, violating C6. The activation effect now sets engine and image together. Rerun: 16 reachable states, 78 committed transitions, 0 invariant violations.

Initial grant witness inspection found every grant denied because WU.latent defaulted to an empty tuple interpreted as no rights. The state default now explicitly carries NET and SINK RW latent ceilings as a trusted initial premise. This premise needs design/plan mapping and is not derived from the finite run.

Witness run: 10 named histories; 7 committed every event. WT-02, WT-03, WT-04, WT-05, WT-06, WT-08, WT-10 committed. WT-01 lacks a grant on the full ancestor path; WT-07 exposes a reversed pending-ack guard; WT-09 has an inconsistent delegation fixture. These are not successful witnesses and remain open.

A previous all-context invocation used timeout 120s and a 1,800,000-KiB virtual-memory cap, then terminated with MemoryError before producing output. It is incomplete and is not counted as a bounded result. The combined all-context driver has no per-context CLI and retains expanded state paths, so further exhaustive runs are paused pending bounded exploration/reporting changes.

Not tested: C1-C13 and A-L complete mapping, capacity/content/sink/derivation/concurrency obligations, intended destructive mutant validity, independent review, implementation refinement, power-loss/host assumptions, and any unbounded theorem.
