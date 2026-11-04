# Competing claims across uncommitted/committed writer death

Preregistration 2b3014e. Three finite schedules, two actual processes and SQLite DELETE/FULL per schedule, same selected capacity-one guard/effect logic as the prior prototype plus stage messages and a pre-COMMIT gate. This is a new instrumented prototype, not unchanged holder realization or external resource enforcement.

* A killed before COMMIT: independent pre-cut reader sees zero claims/effects; B attempted BEGIN before A kill and acquires only after kill; B commits/ACKs; final read-only connection sees B only.
* A killed after COMMIT, before ACK: independent reader sees A; B attempted BEGIN while A uncommitted, later acquires after kill and denies; final reader sees A only. A has no ACK event; its committed effect is preserved rather than treated as denied/reusable capacity.
* Detached weakened control: B reads count0 while A uncommitted, A commits then dies without ACK; B commits based on stale count0, ACKs; final reader sees A and B, violating capacity-one.

Final cold observations integrity ok, claims/effects identical. All A exits -9, all B exits 0, child stderr empty. Raw retains events with process IDs/monotonic times, supervisor kill/reap bounds, precommit/cut/pre-B-ACK/final database observations and source/executable hashes. Begins/commit observations are instrumentation, not syscall traces. No timing stress/all schedules, actual resource use, F3, power loss or F1 closure.

Attempt 1 exited 1 with supervisor event timeout: TextIOWrapper.readline read ahead into its buffer while select checked only the underlying fd, so next event could be buffered but select saw no fd readiness. This is a harness failure, not a product timeout. Exact failed source/stdout(empty)/stderr preserved as attempt1 files; finally blocks killed/reaped owned children. Corrected transport to unbuffered binary pipes (as the inherited competition helper uses). Final command `timeout 30 python3 docs/research/phase-i-f1/round2_capacity_cuts.py > docs/research/phase-i-f1/round2-capacity-cuts.raw.json 2> docs/research/phase-i-f1/round2-capacity-cuts.stderr.txt` exits 0, stderr empty. No prior successful evidence rewritten.

This adds rollback-versus-lost-ACK competition evidence, not more instances of the two original completed-writer schedules. Next: inspect full-model timeout by phase/context with bounded progress, or test actual guarded external acceptance rather than expanding this tiny SQLite prototype.
