---
title: Independent Bounded Sequential RTL Correspondence Review
program: EDASES
layer: Research
document_type: Review Record
status: Complete
authority: Evidence
canonical_repository: ASES
reviewed_commit: b00d4fe0d
review_branch: review/autonomy-20261103-rtl-check
review_date: 2026-11-03
---

# Independent bounded sequential RTL correspondence review

## First verdict

The preserved first verdict was:

> Judgment: source supports the fixed bounded correspondence claim for the emitted cases in both sequential harnesses. The testbench applies each vector to the actual sequential RTL and compares the complete encoded state, resolved, and committed on every clock edge; scripts demand the exact PASS cycle count. The short-sequence script explicitly labels a case-cap stop incomplete and does not simulate it. This does not establish exhaustive reachable-state correspondence or Kernel-0 contract realization conformance.
>
> Falsifiers selected: corrupted expected state, corrupted acknowledgement, and a cap-truncated generated run. Full bounded runs were started after this verdict; raw outputs are kept under `/tmp/ases-rtl-independent-check`.

The verdict was preserved in `/tmp/ases-rtl-independent-check/first-verdict.txt` (SHA-256 `0190f66ea8e275f0e996999d7b49f42869a87f11f9d9b0e39c8a9163be10ff8d`).

Chronology note: before recording that verdict, I had run the reachable-sequence harness in this review's isolated `/tmp` directory and viewed the final 2,000 bytes of that run's stdout, including a tail of its JSON status and hashes. This was my own current-run evidence, not a pre-existing builder log. I had not opened any repository result, preregistration, checkpoint, or prior-review documents. The first verdict is preserved as written; this was a fresh-context, same-family review with limited same-run output exposure, not a fully output-blind verdict.

## Finding and bounded evidence

I reviewed only the repository orientation and Kernel-0 abstract semantics/verification obligations as context, then the new sequential sequence generators, the frozen direct RTL, its sequence testbench and codec, and the frozen finite-model oracle. The target scripts were added after base `0ff7aaca0`; the checkout was pinned at `b00d4fe0d` in a clean, separate worktree.

The testbench checks the full 22-bit state plus `resolved` and `committed` on every rising edge. Its failure is immediate and identifies the vector index. The generators encode oracle outputs after each resolved request, count vector lines and cases, and require the simulator's `PASS sequential cycles=N` to equal that count. The short-sequence cap exits with status 2, reports `status: incomplete`, the exact next action tuple, and `simulation: not_run`.

I reran isolated copies of both scripts with their source imports pinned to the reviewed checkout and their output directories redirected to `/tmp/ases-rtl-independent-check`. The only harness changes were those path redirects; RTL, oracle, codecs, and generated vectors were otherwise unchanged.

| Run | Result |
| --- | --- |
| `rtl_reachable_sequences.py` | 47 cycles across independent (18) and coupled (29) profiles; both positive simulations passed at their exact cycle counts. Each deliberate bad-output file failed at its first differing vector (`sequence=0`). |
| `rtl_short_sequences.py` | 432 cases and 2,592 cycles: 216 cases / 1,296 cycles per independent and coupled profile. Both positive simulations passed at exactly 1,296 cycles. Each script-generated negative vector failed at `sequence=1`. |
| `rtl_short_sequences.py --case-cap 1` | Exit 2, explicit incomplete status, one completed case, next action identified, simulation not run. |
| Mid-sequence state mutation | Exit 1 at `sequence=7`; full state mismatch was reported. |
| Mid-sequence acknowledgement mutation | Exit 1 at `sequence=7`; `resolved` mismatch was reported while state and `committed` still matched. |

The tool was the project-local Icarus Verilog 12.0 (`iverilog` and `vvp`) under `/tmp/ases-kernel-rtl-tool/root/usr`, using the bundled Icarus libraries. No install or host configuration change was made. Both scripts' before/after source hashes matched. The complete JSON stdout captures, including manifests, simulator command lines, and source hashes, are preserved in `/tmp/ases-rtl-independent-check`.

## Reproduction record

The effective command sequence was:

```sh
mkdir -p /tmp/ases-rtl-independent-check
# For each reviewed Python script, copy it to /tmp and change only:
#   HERE=Path(__file__).resolve().parents[1]
# to the absolute reviewed `.../timing-reduction` path, and redirect its
# WORK path to a unique child of /tmp/ases-rtl-independent-check.
ulimit -v 1048576
timeout 30s python3 -u /tmp/ases-rtl-independent-check/rtl_reachable_sequences.py
timeout 30s python3 -u /tmp/ases-rtl-independent-check/rtl_short_sequences.py
timeout 10s python3 -u /tmp/ases-rtl-independent-check/rtl_short_sequences.py --case-cap 1
timeout 10s /tmp/ases-kernel-rtl-tool/root/usr/bin/vvp \
  /tmp/ases-rtl-independent-check/short/independent.vvp \
  +vectors=/tmp/ases-rtl-independent-check/bad-state.vectors
timeout 10s /tmp/ases-kernel-rtl-tool/root/usr/bin/vvp \
  /tmp/ases-rtl-independent-check/short/independent.vvp \
  +vectors=/tmp/ases-rtl-independent-check/bad-ack.vectors
```

The copied scripts and the two mutated vector files are retained in that temporary directory. Each mutation flips one bit in vector 7 of the independent short-sequence vector stream, respectively the expected state word and expected `resolved` bit. Raw output SHA-256 values:

| Artifact | SHA-256 |
| --- | --- |
| `reachable.stdout` | `4508b9e2d3fca7499ce765f5a9112e8bd112f456bfec2e0da36cac8a38fc092f` |
| `short.stdout` | `1a5ac52685f2cebd253a4be32ef5a836a442abc0687da4d2a3c0aceec2ccb975` |
| `cap.stdout` | `1022298f167901cafe0d09511adcb522725c237d2b29ba1388721d76b4056cc5` |
| `bad-state.stdout` | `ed2a05cfa8d123d4cf986d6ce8b0e64b01f19709f8b16b59bd2c4e9753777fc0` |
| `bad-ack.stdout` | `222c9107ffc9d6a9d82fcc5dd2cf0b91c902460502baae6f184bd0098568d06f` |

Reviewed-source SHA-256 values:

| Source | SHA-256 |
| --- | --- |
| `rtl_reachable_sequences.py` | `4c6ed12d9c5a44219f6c26da5f708e58af973bdf30e53edd7ba4926bfb908b0d` |
| `rtl_short_sequences.py` | `44bc23d269dca7806488172fb8a67a71d0fd0f28c3f5b11b9f533d2551660e30` |
| `direct-rtl/kernel0.v` | `1263db8957756be80f1e1e92d8f5dcd3f20d22ef01c070af64f3daec2ac0e0a6` |
| `direct-rtl/sequence_tb.v` | `c80f95850a0a21247281f3c8c70492c8aae8f673d1b3b01c0ed2126ce8116b8c` |
| `direct-rtl/correspondence.py` | `e80d70593358fbd42c07dc880ce635cecc265caf4389b819d09c8e6bdaaeac0c` |
| `kernel0_finite_model.py` | `c9c429b0400df6e044d30b71befaeb810657430372fb1088f9e62631c8965083` |

## Scope and next discriminator

This supports bounded cycle-by-cycle correspondence for the vectors emitted by these two scripts in the independent and coupled profiles. It does not establish exhaustive reachable-state coverage, the exclusive profile, cross-family model provenance, timing closure, or general Kernel-0 realization conformance. The highest-value next discriminator is the same sequential generated-vector check for the exclusive profile, with per-profile case and cycle totals required to match the simulator's count.
