# Cold serving restart discriminates lost acknowledged sink authority

Baseline e0d51e7 preserves exact retained bytes before/after killing/restarting real sink-ordered server. Nevertheless startup resets version1 and empty in-memory events/obligations: acknowledged replacement2 is forgotten; old1 request after restart accepts201, current2 denies409; exact previously committed q denies409. This is a counterexample to the newly selected serving-recovery extension. Prior journal-reader/process-loss observations remain valid in their narrower scope.

Repair on this continuation only adds explicit recover-ordered startup that reads validated durable records before ready, reconstructs version, exact obligations and prior effects, and advances sequence above last retained durable event. Fresh sink-ordered refuses an existing journal; recovery refuses missing/empty/truncated/unsupported material rather than rebootstrap. Baseline cross-layer/write-count branch histories remain unchanged.

Fixed original schedules recover version2; stale1 denies409/no stale effect, current2 accepts201, exact q delivers201 with matching payload/digest committed before replacement. Both original/current positive requests before kill remain accepted. Each old/new sink killed/reaped-9. This is actual serving restart from journal, not an oracle injecting memory state. Boot authority1, correct current journal/root supplied by trusted supervisor and same-live-host filesystem survival remain premises. A genuine obsolete authentic journal would still reconstruct old authority; no nonrollback extension established.

Ten cold negative controls refuse before ready: missing file, empty file, truncated record, wrong replacement continuity, unknown event, duplicate/nonincreasing durable sequence, wrong obligation hash, effect with missing prior obligation, duplicate JSON key, and implicit fresh mode on existing state. Raw retains exact mutated bytes/hash/process exit/stdout/stderr. All exits1, no ready output. A genuine live denial creates diagnostic seq2 absent from journal; restored durable seqs1/3/4 remain1/3/4, then new commitseq5. No missing event is invented. Unretained diagnostic suffixes cannot be reconstructed; these sequence values are not a proof of unique global process-event IDs across restart.

Write-count short/zero regressions also pass on repaired source. Legacy f4 mode is not silently reclassified as ordered recovery. Parser handles only the named bounded ordered profile, journal<=64KiB, unique JSON keys and monotonically increasing durable IDs; not arbitrary JSON/schema/formal verification. No retries or dedup/exactly-once, fsync syscall/power-loss/storage-cache proof, external nonrollback authority, F3 native confinement, frozen F2 bootstrap completion, all-interleavings or full F4 claim.

Commands from repository root, all wrapper exits0 and stderr files empty:

```
timeout 30 python3 research/phase-i-t18-sink-order-20261103/sink-recovery/probe.py baseline
timeout 30 python3 research/phase-i-t18-sink-order-20261103/sink-recovery/probe.py fixed
timeout 30 python3 research/phase-i-t18-sink-order-20261103/sink-recovery/controls.py
timeout 30 python3 research/phase-i-t18-sink-order-20261103/short-write/probe.py fixed
```

Baseline command was executed/committed before repair; after repair replay it at e0d51e7, not current source. Raw source hashes plus index implementation pin identify executed bytes; execution_base_sha is invocation HEAD, possibly before source commit. No old outputs rewritten. Next: independent check of replay validation and missing authority/identity metadata; then a selected external authority/sink implementation or explicit root/currentness guard rather than universalizing this fixture.
