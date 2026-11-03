# F4 selected sink acceptance cut (preregistered)

Date: 2026-11-03 UTC. This is a follow-on at the T18 disposable sink boundary, not a new runtime or a general Phase I failure campaign.

## Prior-art check and selected gap

The pinned `docs/research/kernel-0/kernel0_effect_experiment.py` already kills and cold-restarts the source across received/validated/prepared/durable/before-ACK stages and the sink after prepared versus accepted. It records a duplicate on retry after accepted sink state with a lost reply. Those cuts are not repeated here. The selected residual discriminator is concrete failure sensitivity of the journal's ordering rule: an effect is committed only after the journal append has completed and `fsync` returned; the acknowledgment must follow that boundary. In particular, this experiment includes an intentionally unsafe early-ACK control and independently cold-reads each recovered journal in a fresh process.

## Hypothesis and permitted recovery outcomes

The acceptance boundary is one append-only effect record, flushed with `fsync` before a success reply. No effect is recorded before that boundary.

- **Before accept:** kill the sink after request arrival but before the effect record. Caller has no success acknowledgment; cold recovery finds zero effects.
- **Accepted before ACK:** let the sink append and `fsync` the exact payload record, pause before reply, kill/reap the sink. Caller has no success acknowledgment; cold recovery finds one exact accepted effect and its independently recomputed payload hash. This is an unknown caller outcome, not a denial. The probe does not retry this request, so the expected duplicate count remains one. A permissive retry could duplicate; that is not suppressed or promised away.
- **Uninterrupted positive control:** accept, receive success acknowledgment, stop the sink, and cold-recover one exact effect.
- **Unsafe early-ACK mutation:** acknowledge after request arrival but before the effect record, pause and kill the sink. Caller observed success; cold recovery finds zero effects. This is the intended failing control against T07 no-early-success.

The fresh recovery process has only the journal path; it receives no in-memory sink state or expected payload. It validates complete JSONL framing, sequence continuity, effect fields, payload bytes, and SHA-256. A malformed/truncated line must fail recovery rather than be treated as an empty log.

## Bounds and safety

All traffic uses a new local HTTP sink child on `127.0.0.1` and an ephemeral port. Each case gets a separate temporary directory and one unique payload. The runner imposes finite startup, barrier, client and recovery timeouts, kills and reaps every child, and writes only these results into the repository. No external network, credentials, privileged host policy, production sink, or user data is involved.

The test establishes process-death behavior after an `fsync` call on this host only. It does not simulate kernel panic, power loss, device-cache behavior, filesystem corruption, rollback, F3 conformance, host confinement, or arbitrary storage/sink correctness.

## Observation lock

The experiment code and output are absent at this commit. Commands, raw exit status, acknowledgment observations and recovered bytes/hashes will be recorded without changing these hypotheses after execution.
