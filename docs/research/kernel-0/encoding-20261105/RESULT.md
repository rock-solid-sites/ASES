# Four fewer register bits cost more mapped logic in this candidate

Frozen packetc8f1c6f. Experimental compact register has18 authoritative bits plus2 response bits, retaining the same decoded22-bit state interface. Reuses unchanged frozen kernel0_step. SAT proves shape-constrained codec identity and independent-profile compact-step/original-step successor and commitment equality for all valid18-bit position codes and15-bit proposal inputs. All21 independent literal cycles pass. Decoder-offset mutation fails codec SAT and literal cycle8 for intended semantic mismatch, compile steps succeed.

Same-host/same-flow native Yosys0.23 and ABC1.01, independent profile:

| Measure | Original | Compact |
|---|---:|---:|
| Flip-flop cells |24|20|
| Combinational basic cells |675|784|
| Total basic cells |699|804|
| Longest combinational path, cell levels |22|32|
| Latches / memories |0 /0|0 /0|
| Synthesis wall seconds |1.973|2.200|
| Child-lifetime peak RSS KiB |74688|87852|

This falsifies “smaller state is cheaper/faster” for this one encoder/decoder under this flow:4 fewer state bits add109 combinational cells and10 cell levels. It does not prove compressed encodings generally worse or original encoding optimal. No improvement claim, optimization loop or canonical adoption. Conditional18-bit sufficiency is not minimality.

Counts/levels are technology-independent basic-gate proxies, NOT physical delay, area, FPGA LUTs, power, timing closure or clock frequency. Historical0.9 synthesis figures are not directly compared; both new rows use0.23/identical flow. SAT checks source-level representation refinement, not an independent proof of original semantics or post-ABC netlist equivalence. Original trusted reset/stable proposal assumptions remain, and reserved codes are outside reachable/legal representation; hardware-fault guarantees untested. Coupled/exclusive profiles not run.

Command: timeout180 python3 docs/research/kernel-0/encoding-20261105/run.py, stdout/stderr in this directory. Wrapper exits0, stderr empty; run elapsed5.355s. Every tool job records actual argv/script/stdout/stderr hashes, exit, wall and Linux wait4 peak RSS; 45s/512MiB per job, no timeout. Peak may include pre-exec Python image/collected child resources, not aggregate simultaneous process memory. Proof/mutant control exits0/0/1; good/bad literal simulations0/1. Netlist hashes retained; generated netlists are disposable, statistics/logs/scripts retained.

Initial runner attempt exited1 before any measured Yosys job because /usr/bin/time was absent (shell time was a builtin). Exact failed source/stdout/stderr and generated script preserved. Replaced only optional measurement wrapper with native wait4/monotonic measurement and explicit child timeout/reaping, kept same compiler/synthesis/model route. Preliminary standalone codec proof output retained in setup; its numeric exit was not separately captured, so final recorded job is the execution evidence for acceptance. This is setup/harness failure, not RTL defect.

Package URLs/hashes in packet, executable/version/source/table/script/binary hashes in result.json; source hashes stable before/after. No system tool install. Next: bounded independent audit of encoding proof domain/resource interpretation; do not infer physical timing or run additional candidates without a new discriminating hypothesis.
