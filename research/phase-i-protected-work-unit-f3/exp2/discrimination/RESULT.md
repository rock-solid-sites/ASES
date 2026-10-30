# Landlock discrimination result (2026-10-30)

Executed `landlock_discrimination.py` once from its disposable `exp2/discrimination/` directory with an eight-second outer timeout. The supervisor created one fixture and a symlink alias, opened one descriptor for deliberate inheritance, launched a sibling mediator, then launched the confined child. The child ran as the same unprivileged UID as the availability probe and entered an ABI-1 ruleset handling `read_file` and `read_dir` with no allow rules. The mediator was not placed under the child's ruleset; it handled one request by opening the fixture, reading it, closing that per-operation descriptor, and returning the bytes over a socketpair. Both test subprocesses exited normally and were reaped by the supervisor.

Observed worker JSON:

```json
{"direct_target":{"detail":"Permission denied","errno":13,"result":"denied"},"landlock_restrict":"entered ABI-1 empty read_file/read_dir policy","per_operation_mediator":"OK landlock-disposable-attachment","retained_preopened_fd":{"bytes":"b'landlock-disposable-attachment\\n'","result":"readable"},"symlink_alias":{"detail":"Permission denied","errno":13,"result":"denied"}}
```

This single test demonstrates that the tested Landlock policy denied fresh direct opens of the target and its in-tree symlink alias, while an out-of-policy sibling could perform a fresh mediated open. It also demonstrates the obstruction: an already-open descriptor inherited by the restricted child remained readable after restriction. Landlock path restrictions therefore did not revoke that retained handle. The mediator's returned bytes are also available to the child; this is mediation of a new operation, not revocation or erasure of returned data.

The alias test covers only this one in-tree symlink, not all aliasing/races or descriptors. This is not a general path-confinement guarantee, a complete trusted-boundary/bypass inventory, or F3 acceptance. No privileged action or host-policy change was needed. Because retained-handle access survives, stop broadening this mechanism probe as directed; do not build a proxy/bodyguard/runtime or start lifecycle implementation. Reconcile future lifecycle work with B's partial F1 model first. F5 independent review remains outstanding.