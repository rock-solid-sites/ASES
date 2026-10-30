# L5 source and claim audit — clean-room review packet

**Prepared:** 2026-10-30. **Status:** audit instructions only; no independent audit executed.  
**Review target:** `rock-solid-sites/ASES@fb34deca9ea8c1bf04ec808052b39d7521040290`.  
**Mode:** reviewer/source falsification; read-only target, separate report branch. Not permission to implement L6/L7 or to declare F5 complete.

## Claim to investigate

For one selected host profile, a trusted authority H mediates read and write requests from a worker over a single inherited socket endpoint. With local read/write rights on child C, a read-only old parent P and a read/write new parent Q, a sealed P→Q move preserves the old effective read-only ceiling. After separately authorized activation, read of accepted content x succeeds and a protected write is refused. A positive configuration allows the same mediated write; a weakened move that drops the restriction allows a forbidden write and must be detected. Accepted content must remain unchanged. The claim is **bounded source/host evidence**, not general source identity, filesystem confinement, storage crash durability, correct arbitrary moves, or full F3/F5 closure.

## Exact material for the reviewer

Read these pinned artifacts, and no builder reports or earlier reviews unless essential:
- `research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_write.py`
- `research/phase-i-protected-work-unit-f3/lifecycle/l5/verify_l5_write.py`
- `research/phase-i-protected-work-unit-f3/lifecycle/l5/l5-write-raw.json`
- direct code dependencies (including `lifecycle/l1/l1.py`) only as needed for the supported host claim.
- Canonical semantics: `docs/architecture/core-substrate/Phase-I-Verification.md`, T11 and F3 acceptance; `Phase-I-Closure.md` §7 required move, activation, accepted content and effect semantics (at `codex/execution-engine-roadmap`).

Do not read `l5/RESULT.md`, the obstruction report, the original implementation packet, agent conversations, or prior critiques as framing material before an independent verdict.

## Required independent checks

1. **Nonvacuous discriminator.** Compare the safe, positive and weakened cases; show from actual code and event data that they use one write operation and that an authorized write really has a visible effect.
2. **Accepted-byte provenance.** Trace exactly how the handler obtains x when the request is served. Does an observed `read_x` response depend on the accepted object that existed after the move, or can an independent stored-object loss/modification leave the reply unchanged? Distinguish immutable content checks from actual post-move storage reads.
3. **Move and activation effects.** Show how P, C, Q, old full-path restrictions, latent ceilings, sealed state, authority to initiate move/activation and the published whole record are established. Determine what the test demonstrates about atomic publication and what it does **not** demonstrate about live/concurrent transitions, authorization and crash recovery.
4. **Currentness and peer.** Identify actual source of the `W1` ingress assertion; determine whether an arbitrary holder of the socket could submit the same request. Report the trust assumption rather than broadening the supported profile.
5. **External effect ordering.** Trace `write` authorization, object write, visibility and acknowledgment. Distinguish process-level observed ordering from fsync/power-loss durability, sink contracts and lost-reply behavior.
6. **Verifier independence.** Compare the verifier's fields and logic against the implementer's labels and recorded data. Alter disposable copies of raw evidence in small, defined ways (e.g., read bytes, latent ceiling, route decision, missing effect) and record whether the independent oracle catches them; do not alter original committed observations.
7. **Coverage and regressions.** Check differences against the verified F3 L1–L4 base; determine whether the experiment exercises a continuous historical Work Unit from L4 or a new stand-alone fixture initialized from an L4 accepted object. Unsupported routes, descendants and physical OS trust must be identified separately.
8. **Outcome.** Classify each claimed property `supported`, `partial`, `unsupported`, or `contradicted`, with exact source lines, raw fields, trace and a reproducible command. Never infer full F3 completion.

## Execution policy and report

Execute **exclusively on the existing Ubuntu VPS using SSH**. Use a separate review worktree/branch (e.g. `review/phase-i-f3-l5-source-audit-20261030`) based on pinned F3 commit. Keep `main`, builder worktrees, F1/F2 branches, and `exp1/run/` and recovery snapshots untouched. Limit concurrent memory-heavy operations; no paid model fallback.

If running a genuine clean-room review, select a reviewer from a **different model family than the builder** and disclose model ID, exact supplied context and isolated session. A Luna-only checker may be a useful technical verification but is **not** cross-family F5. Review must first be read-only and not repair the target under review. If a needed check fails, provide a minimal proposed follow-up repair rather than silently rewriting the fixture.

Commit meaningful reviewer-generated notes/checks at least every five minutes during active editing, push the review branch to origin, verify its final remote SHA, and report the exact verdict, commands, hashes, limitations and smallest follow-up. If SSH is inaccessible, stop and report the blocker; do not use a local/cloud development fallback.
