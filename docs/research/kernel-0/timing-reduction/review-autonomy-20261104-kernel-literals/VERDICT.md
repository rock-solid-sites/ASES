# First verdict: literal RTL boundary vectors

**Verdict: no wrong expected word found in the 21 sequential literals.** The selected transitions and outcome bits independently follow from the documented encoding and finite proposal table, with the declared independent profile and reset/valid edge rules. The retained simulator output reports the reference passing all 21 cycles and each of two specific mutants failing at a discriminating edge. This is evidence-based, conditional on the recorded simulator run and source identity, not an independent simulator rerun or complete correspondence proof. This is a same-family operational review.

## Basis and arithmetic

Review pin: `50e5bc151b3d08ed84df55bc452f8766afa2090e`. Before this verdict I read the finite-model proposal table, the direct-RTL encoding and synchronous boundary description, the literal vectors, runner, raw and stderr, RTL and sequence testbench. I did not read the Round2 result or preregistration, or earlier Kernel reviewers. A standalone decoder ([decode.py](decode.py)) uses only integer masks/shifts and JSON/hash library functions; it does not import or invoke a shared Python oracle or codec. Its complete row-by-row output and exit 0 are retained alongside it. `resolved/committed` below are registered output bits. State bit 3 is displayed as 0 even in the absent state; semantically that state has no content.

Numbering is zero-based, as in `sequence_tb.v` and the raw failures:

| Rows | Independent calculation and expected result |
| --- | --- |
| 0–1 | Reset gives `000000, 0/0`; idle retains it with `0/0`, regardless of malformed `7fff`. |
| 2–3 | Establish sets bit 0: `000001`; management grant to fresh a0 sets issued bit 4 and rights bits 8–10 to 7: `000001 + 000010 + 000700 = 000711`, each `1/1`. |
| 4–6 | a0 has content right: accepting 1 adds `000008` → `000719`. Delegate x right to fresh a3 adds issued `000080`, a3 rights `020000`, parent-a0 `100000` → `120799`. Restrict a0 to zero removes `000700`, cascades away `020000` and `100000`, retaining issued a0/a3 and content → `000099`; all `1/1`. |
| 7–9 | Regrant a0 denied because issued bit 4 remains: `000099, 1/0`. Grant fresh a1 x right adds issued `000020` and rights `000800` → `0008b9, 1/1`; a1 set x to 1 adds bit 1 → `0008bb, 1/1`. |
| 10–11 | Resume with content 0 mismatches retained 1: unchanged `0008bb, 1/0`. Resume with 1 has x right and matches: x is already 1, so committed stutter `0008bb, 1/1`. |
| 12–15 | False-authentic a1 flip denies; authentic actor 7 flip is malformed and denied; both preserve `0008bb, 1/0`. Valid=0 preserves `0008bb, 0/0`. Valid authentic a1 flip clears x bit → `0008b9, 1/1`. |
| 16–20 | Reset takes precedence over simultaneous valid flip → `000000, 0/0`. Flip and grant while absent each deny → `000000, 1/0`. Establish → `000001, 1/1`; fresh grant after reset → `000711, 1/1`. |

The finite table supplies grant freshness, restriction cascade, content and resume guards; the direct RTL description supplies the bit layout, valid-gated output behavior and reset precedence. Reset is trusted initialization, so clearing issuance there does not contradict retaining it during operation. The malformed actor-7 vector is outside the compared 148-template model alphabet; its denial is an RTL input-boundary check rather than a finite-model correspondence case. No physical content bytes are tested by the single bounded content bit.

## Recorded execution and mutation evidence

The runner compiles the same literal vectors and `sequence_tb.v` against a reference and two source-text mutations, without importing an oracle. The testbench reads six hexadecimal fields per edge, checks pre-edge state stability after the first edge, then checks state, resolved and committed after the rising edge. Its defaults are `COUPLED=0, EXCLUSIVE=0`. Raw says reference compile and simulation exit 0, `PASS sequential cycles=21`; outer stderr is empty. The raw source revision is `d1b6099517389c3aa8b2d4fd89760a459fe17159`, not the review pin; all six embedded source hashes match the pinned checkout, and the raw literal vector string exactly matches the pinned vector file. This does not identify every file of the historical checkout. Raw identifies Icarus runtime 12.0 and tool, package, RTL and binary hashes; these are recorded provenance, not independent attestation of the historical tools.

At row 6, the issued-bit-erasure mutant records `000089` against `000099` with matching `1/1`: the `0x10` difference is exactly a0's issued bit. At row 16, the reset-precedence mutant records `0008bb, 1/1` against `000000, 0/0`: from `0008b9`, it executes the valid a1 flip instead of reset. Both compile exits are 0 and simulation exits 1, with concrete `$fatal` output in the raw. The mutations test these two distinctions; they do not prove the absence of other defects.

Reproducible source/raw arithmetic check, run from the pinned checkout:

`python3 docs/research/kernel-0/timing-reduction/review-autonomy-20261104-kernel-literals/decode.py > docs/research/kernel-0/timing-reduction/review-autonomy-20261104-kernel-literals/decode.stdout.txt 2> docs/research/kernel-0/timing-reduction/review-autonomy-20261104-kernel-literals/decode.stderr.txt`

Exit 0; stdout, stderr and exit are retained. No simulator rerun was necessary to resolve a discrepancy. Raw SHA-256 `9bca4d2e4f90a3110b523a3178b9e99dbc9a0888d4be70f7c8d09b8573f88751`; vector SHA-256 `ec5d693543aaeb357cd11686472b54732337cd410e93609a2058f925f9099805`.

**Not tested:** physical timing, setup/hold, glitches, clock or reset integrity, all other vectors and profiles, complete RTL/model correspondence, or the separate Kernel-contract investigation. The digital test assumes a trusted reset and authenticity observation.
