# Preserve option failure; correct only the property monitor

Source46381dc ran3 jobs. Original/compact induction jobs exited1 BEFORE any SAT
proof: `Options -prove-skip and -tempinduct don't work with each other. Use -seq
instead of -prove-skip.` These are harness/tool-interface failures, not counterexamples
or passing proofs. No-reset bounded control completed semantic FAIL with a concrete
WaveJSON/VCD model, as predicted. Initial source/raw/result/stderr remain unchanged.

Before further execution, replace skip option with an explicit one-bit ASSURANCE
monitor, initialized0, set permanently1 after a sampled reset. Property is
`armed && raw_public_output_difference == 0`. Monitor initialization is explicit;
product registers remain independently arbitrary initially. Keep reset asserted at
step1 and all subsequent inputs arbitrary. It directly activates comparison AFTER
the first reset, rather than assuming original/mapped private register equality.
Monitor is scaffolding, not a product state bit or Kernel primitive.

Same -seq2/-tempinduct/-maxsteps4 and45s/512MiB/40sCPU bounds; two corrected proof jobs
only, no repeat of no-reset control or synthesis/mapping. Require actual base and
induction success, inspect initialization constraints to exclude accidental product
register initialization. New result/raw files under corrected/ preserve initial jobs.
Source and monitor committed before execution. On unresolved failure retain limits;
do not inflate bounds or infer correctness. Shared tool/two-state clock model limits
remain as in original packet.
