# Retained mapped-circuit checks

Executed frozen runner `f912b05` once,10.101 seconds total. All seven sequential tool
jobs completed within45s/512MiB, without timeout. Reproduce:

```sh
timeout 180 python3 docs/research/kernel-0/mapped-20261105/run.py
python3 docs/research/kernel-0/mapped-20261105/audit.py
```

Newly generated original and compact independent-profile post-ABC Verilog circuits
are retained, with exact digests in `result.json`. These are new executions of the
same flow; historical disposed netlists are not retrospectively certified.

* Original: all46 Yosys equivalence points proved, zero unproved; separate public-output
  SAT reset-base check succeeds at abstract synchronous steps2..4 after reset asserted
  at step1, with arbitrary proposal/valid/reset thereafter.
* Compact: all60 points proved, zero unproved; the same independent output miter and
  reset-base check succeeds. Source and mapped public state/resolved/committed agree
  throughout the declared bounded base, including arbitrary reset/valid collisions.
* Post-mapping committed-output mutation compiles and produces a semantic SAT failure,
  exit1, with complete WaveJSON/VCD model. Steps2 and3 have valid1/gold committed0/
  mutated committed1; reset is1 at step2 and0 at step3. Initial unreset state divergence
  at step1 is intentionally excluded from the proof condition, not a product failure.

`equiv_induct` proves convergence after equal matched histories, not unconditional
initial synchronization. The public-output reset-base result is recorded separately;
we do not claim a separately established initialization relation for every internal
matching point or an independent unbounded/full-semantics proof from these two logs.
Next cheapest discriminator is a direct public-output temporal induction miter with
explicit reset base, avoiding that linkage premise, under one fixed small bound.

Artifact audit verifies pinned source hashes, source stability, raw/script/netlist
digests, job exits/limits and concrete mutation model. Missing circuit manifest is
INCOMPLETE; contradictory proof exit is VIOLATION. Its first attempt expected a full
text counterexample table, but Yosys's buffered text ended mid-row on `-verify` failure.
The complete independently written WaveJSON model was already present. Original audit
source/stderr retained as `audit-attempt1.*`; corrected parser re-audited the same raw
artifacts, without repeating any synthesis or proof. This was a harness assumption,
not a mapped circuit defect or missing complete machine-readable model.

Tools/source/compiler/formal engine remain trusted and shared. Logical cell mapping
correspondence does not establish physical delay/area, frequency, analog behavior,
resetless startup, arbitrary hardware-fault tolerance, coupled/exclusive profiles,
minimality or universal Kernel semantics. Original semantic correctness still depends
on prior correspondence evidence. No canonical implementation or policy changed.
