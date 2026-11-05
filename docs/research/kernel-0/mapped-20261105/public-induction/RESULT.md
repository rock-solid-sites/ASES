# Direct reset-based public induction completed

Initial source46381dc attempted the frozen option combination; both induction jobs
exited1 before proof because Yosys rejects `-prove-skip` with `-tempinduct`. Initial
source/raw/stderr/result and a successful semantic no-reset negative control remain
in this directory. This is harness-interface failure, not product counterexample.

Preregistered correctionad6609a adds a one-bit assurance-only monitor, initially0,
permanently armed after a sampled reset. Property is no public-output difference while
armed. Product source and mapped circuits unchanged; product registers independently
arbitrary initially. No new synthesis or repeated no-reset/mutation control.

Both original and compact direct public-output miters completed actual base case and
temporal induction at length1, within fixed maxsteps4. Total corrected run3.562 seconds.
Tool logs contain exactly one initial constraint, `armed=0`; there is no product initial
state equality or zero assumption. Reset is constrained at first abstract clock step,
all later proposal/valid/reset inputs arbitrary. Under this two-state synchronous model
and trusted toolchain, the retained mapped circuits preserve RTL state/resolved/committed
after that reset for arbitrary-length histories. Maxsteps4 bounds proof search, not
history length once induction succeeds. This closes the prior internal matching-point
initialization linkage gap for this selected source/mapped pair.

The no-reset compact miter finds differing public outputs from arbitrary independent
initial register states. It is an explicit premise control, not reachable-after-reset
misbehavior. Prior post-mapping committed mutation also has a saved semantic witness.
Artifact audit checks source/netlist pins and stability, raw/script digests, actual
induction/base markers, initialization constraints and controls; missing proof is
INCOMPLETE, contradictory exit VIOLATION.

Reproduce corrected proof only:
`timeout 100 python3 docs/research/kernel-0/mapped-20261105/public-induction/corrected_run.py`
then `python3 docs/research/kernel-0/mapped-20261105/public-induction/audit.py`.
Initial incompatible command is retained for diagnosis, not a recommended primary run.

This is source-to-newly-mapped logical correspondence, using shared Yosys/SAT tooling.
It does not independently establish original semantic correctness, physical timing,
analog/clock hazards, resetless startup, machine power-loss continuity, arbitrary
hardware-fault behavior, other policy profiles, minimum encoding or universal Kernel
closure. The monitor is assurance scaffolding, not a new product bit/Kernel primitive.
Next useful experiment should change the obligation/boundary rather than mapping
another identical profile or extending an already inductive history bound.
