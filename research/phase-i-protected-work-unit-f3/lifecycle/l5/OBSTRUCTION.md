# L5 disposition — concrete obstruction in the selected read-only profile

Status: **STOP at L5; the gate is not passed.** This is the first unsatisfied lifecycle obligation after L1–L4 passes. No move was performed, and L6/L7 were not attempted.

## Reproduction

- F3 HEAD entering L5: `400eb691c8f4911eacc51c7d6fd7096f38f48f38`.
- Packet @ `415a03fe660f902cfffed6662d1a5982416ee9da`.
- Compile: `python3 -m py_compile research/phase-i-protected-work-unit-f3/lifecycle/l5/probe.py` — PASS.
- Probe: `timeout 20s bash -c 'ulimit -v 524288; python3 research/phase-i-protected-work-unit-f3/lifecycle/l5/probe.py > research/phase-i-protected-work-unit-f3/lifecycle/l5/raw-run.json'` — exit 0, `pass_obstruction=true`.
- Probe SHA-256: `d72b688809b54ff14845e40df6734d205267b5dbb1d4f33ff5341b4e3ca6d8fd`.
- Raw probe SHA-256: `b425fe580bceabc0406cb1baab580af1d8d028fdf4d0c587f1913175bd2bc836`.

The probe read, without modifying, L4's current `record-000006.json`: P and C have only `read` grants, current ingress is W2, accepted x/y are retained, and Q does not exist. Inspection of the actual H2 handler in `lifecycle/l4/l4.py` finds only `read_x`, `read_candidate_y`, `accept_y`, and `read_y`; it has no mediated write operation. A confined worker's direct `O_WRONLY` open of the accepted object returned `EACCES`/errno 13 under Landlock. That denial is unconditional path confinement; it does not pass through an authorization decision whose result can distinguish the old P ceiling from Q's permissions.

The frozen L5 discriminator requires a previously prohibited write/use to remain denied after C is sealed and moved under a more permissive Q, while a permitted read succeeds. With the explicitly selected **read-only mediator** profile and no local/child write grant or write-capable mediator route, any post-move write denial would be vacuous with respect to latent-right preservation. A metadata-only move and comparison of sealed/no-rights states would repeat the exact insufficient observation warned against by the packet. Making this discriminator meaningful would require selecting and testing a concrete write-capable attachment/effect route or changing the declared profile; neither is part of the currently frozen read-only profile, so no such route was invented.

L4 already provides a positive post-recovery read of x and y after explicit W2 activation, but **not after relocation**. The direct `O_WRONLY` denial is retained only as route evidence; it is not counted as the L5 latent-ceiling control. P→Q move, post-move read, and post-move write/use checks remain untested. L6 disposition/removal and L7 mutations remain untested.

## Route conclusion and restart cursor

For the supported path, H mediates immutable reads and acceptance; Landlock blocks the worker's direct protected-file path. Open/inherited target FDs are not passed; SCM_RIGHTS, hostile descendants, network isolation, credentials, mappings, alternate mounts/aliases and administrative policy mutation remain outside/unverified as stated in L1/L3/L4. There is no enabled write-capable protected route whose authorization could be tested across the move.

**Precise stop:** the selected read-only attachment cannot supply the indispensable L5 post-activation latent-write discriminator. Resume only with an explicitly selected, concrete write-capable supported attachment/effect path and corresponding current grants/ancestor ceilings, or record L5 as unsupported/not-tested under this read-only profile. No F3 closure claim. D3/quiescence and F4 whole-history remain separate and unproven.