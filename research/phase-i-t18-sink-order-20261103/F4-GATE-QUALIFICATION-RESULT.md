# Retained F4 gates — Round 2

Executed the preregistration at 962785f against unchanged run.py (SHA-256 63d52186d3cd4cb64ad471b6b017a3406506930fb926be3e0da648e03de21b23). Source and original raw files preserved. New harness is a disposable Python observation test, not a maintained runtime. Hypotheses/predictions are in F4-GATE-QUALIFICATION-PREREGISTRATION.md.

Four sequential one-request processes: uninterrupted yields 201 and one exact record; preaccept yields no HTTP reply and MISSING journal; accepted-before-ACK yields no HTTP reply and one exact record; early-ACK control yields 201 and MISSING journal. Live and post-SIGKILL fresh-reader subprocesses agree in each case. All sink exits -9, all client exits 0. Empty existing file is separately EMPTY; truncated and malformed files REFUSED. Missing is no longer relabeled empty.

Retained status snapshots show named gates and event sequence. Accepted gate seq 2 points to effect seq 1, observed before kill. Source emits that gate after append/fsync return, and separate live reader verifies matching bytes before kill. This is source-plus-observation evidence, not syscall tracing, actual power loss, or a universal durability guarantee. No reply is unknown to caller, not denial. File absence in the selected preaccept/early-ACK histories is observed; missing metadata in old logs remains missing, not retroactively supplied.

Commands (repository root), both exited 0:

```
timeout 30 python3 research/phase-i-t18-sink-order-20261103/f4_gate_qualification.py > research/phase-i-t18-sink-order-20261103/round2-f4-gates.raw.json
python3 research/phase-i-t18-sink-order-20261103/check_f4_gates.py > research/phase-i-t18-sink-order-20261103/round2-f4-gates.check.json
```

Checker reconstructs records/digests/payloads, reconciles gate/effect/ACK/file observations, and rejects missing-gate, missing-file-observation, missing-client and truncated-journal controls. Producer booleans are not consumed. Same coordinator check, not independent review. Environment/executable identity and hashes in raw; manifest retained separately. Gate snapshots are not ACK packet timestamps; no fsync syscall trace, directory-fsync evidence, host loss, device-cache test, retries/exactly-once or F3 route. Frozen F2 T07 power-loss and full F4 remain open. Next: original detached mutant post-send, then isolated fixed-claim review.
