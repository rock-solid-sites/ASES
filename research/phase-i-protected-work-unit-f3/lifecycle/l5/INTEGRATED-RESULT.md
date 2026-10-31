# Bounded L5 lifecycle integration result

**Status: PASS for the recorded bounded host witness.** This is not a full F3/F5 closure claim.

## Implementation and observations

`l5_integrated.py` runs the unmodified L4 harness three times in disposable copies, starting every case with L4's actual protected store, current selector, accepted-content objects, identity/provenance and H2 recovery/management lifecycle. Each case validates L4's final raw readback, then adds the L5 P/C/Q/D graph to that current protected record. D is a dependent child of C. The L5 authority commits whole JSON selectors by same-filesystem atomic replacement.

The permission evaluator validates the fixed graph structure, IDs, parent references, cycles, permission vocabulary and latent-ceiling shape, then intersects local grants, all ancestor grants and all retained ceilings. The move is handled through a separate manager socket using L4's `authorize_*` management operation pattern. The authorized sealed move records P→Q and includes C and dependent D; a second, separately authorized `authorize_activate` request publishes the new ingress. An unauthorized move request is denied without state change. Reads are served only after resolving accepted-object paths under protected storage and verifying bytes, size and SHA-256 against the accepted metadata.

- **Positive:** a concrete D write is committed under a P read/write parent.
- **Safe move:** C and D start below read-only P, move sealed beneath read/write Q, and are separately activated. The verified accepted x read succeeds; D write is denied and creates no effect. C and D both retain the old effective `{read}` ceiling.
- **Weakened control:** deleting the retained ceilings makes the same post-move D write succeed and creates a concrete effect.
- **Adversarial structure checks:** a cycle, dangling parent and unknown permission are each rejected.
- All three L4 runs passed, and accepted x remained byte-identical with its L4 hash in all cases.

The independent verifier checks raw observations, embedded and separately retained L4 evidence, content hashes, move/activation records, D dependency, each discriminator outcome and the intended structure rejections.

## Reproduction on IT3812

Run from `~/reviews/f3-l5-lifecycle-integration-20261031`:

```sh
cd research/phase-i-protected-work-unit-f3/lifecycle/l5
python3 -m py_compile l5_integrated.py verify_l5_integrated.py
timeout 90s bash -c 'ulimit -v 524288; python3 l5_integrated.py > l5-integrated-raw.json'
python3 verify_l5_integrated.py
```

The retained result is `l5-integrated-raw.json`; per-case L4 outputs are `l5-integrated-l4-{positive,safe,weakened}.json`. The original L5 write/move discriminator was also rerun from a disposable lifecycle copy, without replacing its baseline raw artifact. Its output and 9-check verifier trace are retained as `l5-baseline-discriminator-raw.json`, `l5-baseline-discriminator-verifier.txt`, and `l5-baseline-l4-raw.json`.

## Limits and unresolved provenance

This is one local trusted mediator, one test manager credential and disposable local files. The shared test credential does not establish physical manager identity or production authentication. The observation does not test hostile peers/descendants, descriptor passing, network, alternate mounts/aliases, concurrent races, partial policy enforcement, filesystem crash/power-loss durability, rollback, host administration, or real external sinks. Atomic replacement is not an fsync/durability claim. Existing L1–L4 sources are unchanged; L4 is exercised from isolated copies.

The supplied governing hash `5c03a425fd5627c3764806292b8c5cb653498f4f` resolves in `rock-solid-sites/ASES` to an unrelated documentation recategorization commit (`docs: recategorize reusable decisional provenance research`), not the T11/Closure §7 source. The applicable T11 text was located in the fetched lifecycle planning branch at `415a03fe6` (`Phase-I-Verification.md`, T11); Closure §7's move and activation requirements were checked there as well. Exact provenance of the user-supplied governing pin remains unresolved and should be corrected before treating this as a fully pinned normative implementation.

The approved `codex-pgs2` route was invoked with `glm-5.3-flash` and the required Phoenix Grove provider overrides. It returned HTTP 402 (daily allowance exhausted; refill reported as `2026-11-01T00:10:12.395781+00:00`). No alternate model/provider was used. Raw launcher stderr/stdout are retained in `delegation-codex-pgs2-402.*.txt`; implementation proceeded directly in this isolated worktree.

No L6/L7, removal/disposition, complete F3, F5, general-purpose runtime, or production security closure is inferred.
