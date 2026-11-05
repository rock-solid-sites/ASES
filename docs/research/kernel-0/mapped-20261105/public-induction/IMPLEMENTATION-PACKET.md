# Direct public-output temporal induction

Freeze from `d871eead1ead6c08a43cbea0a597549580226e2f` after the preceding seven jobs,
before this extension. Their equiv_induct results plus public-output bounded reset
base did not independently link every internal equivalence point's initialization.
Use the already retained original/compact mapped circuits and public-only output
miters, without re-synthesis, to avoid that linkage assumption.

Two direct SAT temporal-induction jobs: original and compact source versus retained
mapped circuit, trigger is any public state/resolved/committed difference. Explicit
reset at first abstract synchronous step; initial two-state registers unconstrained;
skip comparison only at step1 before that reset takes effect. All proposal/valid/reset
inputs thereafter arbitrary. `sat -seq 2 -tempinduct -maxsteps 4 -set-at 1 reset 1
-prove trigger 0 -prove-skip 1 -show-inputs -show-outputs -verify`. Require tool's
induction success, not just bounded SAT success, or record failure/timeout/inconclusive.
Maximum4 is an induction-search bound, not an execution-history bound on a successful
inductive result. Do not silently increase it or add internal equality assumptions.

Control: same compact miter without initial reset, bounded2 steps, must find a concrete
public-output mismatch between independently arbitrary initial register states. This
tests necessity of the miter's initialization premise; it is not a reachable-after-reset
product defect. Compile/SAT failure only counts if actual semantic model retained.
Prior post-mapping mutation counterexample already tests non-vacuity; no repeated run.

Reuse pinned native Yosys/ABC identity and prior measurement helper, <=45s/512MiB/40sCPU
per job, sequential3 jobs, whole<=150s. Retain exact source/netlist/miter hashes before/
after, tool argv/scripts/exits/raw models and metrics. Source committed before execution.
Same toolchain/two-state clock-edge/policy-input assumptions; no original semantic
oracle independence, hardware power-loss/analog/physical timing/canonical closure.
Next discriminator is a different unverified boundary if proof succeeds; inspect a
concrete mismatch before repair and preserve scope if fixed bound is inconclusive.
