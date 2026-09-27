# followup-05 — Muse Spark probe (operator-directed availability + fitness test)

- **Issue:** #565 · **Date:** 2026-09-27 · **Status:** complete
- **Model:** `opencode/muse-spark-1.3-contributor-free` · family `muse-free` ·
  cost 0/0/0 · route `zen` · ctx 1,048,576
- **Why:** operator directed "Test Muse Spark" after the `space-bunny` subagent
  proved unreachable. Muse Spark was the one free Zen model in the census with
  both a large context and no recorded failure.

## 0. Retention term, recorded before use

Per `RECONNAISSANCE.md` §5.4, **Muse Spark Contributor explicitly trains on
prompts.** This is a stronger term than the Big Pickle / MiMo / Ling / Nemotron
free tiers, which *may* use data for improvement. Consequences:

- Both tests below ran on **synthetic research artefacts only** — the frozen
  corpus (explicitly `contains_personal_content: false`,
  `contains_secrets: false`) and derived metrics. No secrets, no personal
  content, no live repo or session content.
- If Muse Spark is later used on anything touching real repository or session
  content, that is a **separate decision requiring its own approval**, not a
  continuation of this probe.

## 1. Test 1 — output contract on real frozen cases

The gate `ling-3.0-flash-fin-free` failed (24/64, prose output plus a false
self-claim of NDJSON compliance). Same gate, same route, same prompt template.

Subset: 6 cases, deliberately including the two cells that carry the most
evidentiary weight — `c-p4b` (the known D2 ground-truth defect) and `c-p6a`
(the transport-unstable cell from §5.1 of `COMPARISON.md`).

| check | result |
|---|---|
| exit / wall | 0 / 37 s |
| output format | clean NDJSON, **no code fence, no prose leakage, no reasoning in the answer stream** |
| count / duplicates / completeness | 6 / 0 / all present |
| **frozen `parse_general()`** | **6/6 accepted** |

| case | type | pred | gt | |
|---|---|---|---|---|
| `a-dist1` | noul | no | no | OK |
| `d-01` | choice | build | build | OK |
| `a-h04` | score | low | low | OK |
| `a-e01` | noul | yes | yes | OK |
| `c-p4b` | noul | yes | no | MISMATCH |
| `c-p6a` | noul | yes | yes | OK |

5/6. The sole error is `c-p4b` — the same cell `big-pickle` and `mimo` also
fail, and the cell D2 F1 identified as not derivable from model-visible text.

**Verdict: passes.** The output contract that `ling` could not hold is held
cleanly, and the judgment profile matches the other scored arms.

## 2. Test 2 — blind derivation competence (the fitness question for a verifier)

Output-contract compliance is necessary but not sufficient. The verifier's
actual job is re-deriving numbers from raw evidence. So: Muse Spark was given
`staging/big-pickle/results/scored.ndjson` and asked to derive seven quantities,
**without being shown any of this project's conclusions.** It was explicitly
forbidden from reading `COMPARISON.md`, `SMOKE.md`, `RECON.md`, `out/band-*.json`
and `findings.md` §6, and was told to report the method used for each figure.

It was told nothing about the expected answers. It was read-only.

### Result: every requested figure correct

| # | quantity | Muse Spark | independently confirmed |
|---|---|---|---|
| 1 | total lines / per mechanism | 320; 64 each | ✅ |
| 2 | `general_model` usable / typed_error | 64/64; 0/64 | ✅ |
| 3 | answerable n, correct, accuracy | 50, 49, 49/50 | ✅ |
| 4 | paired b / c / ties vs `jev` | **0 / 0 / 50** | ✅ |
| 5 | answerable errors | `c-p4b` only | ✅ |
| 6 | unanswerable answered | `general_model` 14/14, `jev` 14/14 | ✅ |
| 7 | label diffs vs `jev` | 4, all unanswerable: `b-a01`, `b-a05`, `b-i01`, `b-i03` | ✅ |

### It also volunteered cross-checks nobody asked for, and they were all correct

| volunteered | Muse Spark | confirmed |
|---|---|---|
| file-wide answerable / correct | 250 / 188 | ✅ |
| `prior` correct on answerable | 22/50 = 0.440 | ✅ |
| `rule` correct on answerable | 39/50 = **0.780** | ✅ matches Phase-1 "rule 78.0%" |
| `lexical` correct on answerable | 29/50 = **0.580** | ✅ matches Phase-1 "lexical 58.0%" |
| `jev` correct on answerable | 49/50 = 0.980 | ✅ |
| `answerable` flag consistent across mechanisms | 64 ids, 0 inconsistencies | ✅ |

Those two Phase-1 figures (`rule` 0.780, `lexical` 0.580) were published in
`PHASE1-VERDICT.md` §1.1 from an entirely separate run, and this model
reproduced them from `scored.ndjson` without being told them. That is a
non-trivial consistency result, not a coincidence of arithmetic.

It also correctly reported the *direction* of the finding, unprompted:
"there is no answerable case where jev is right and general_model is wrong."

## 3. What this probe does NOT establish

- **Derivation competence is not judgement.** Test 2 asked "can you reproduce
  these numbers". It did not ask the harder verifier questions: is the `c-p6a`
  fragility claim (`COMPARISON.md` §5.1) actually right; was staging a per-arm
  grid a legitimate substitution of the `general_model` mechanism or a quiet
  change of the instrument; is anything in `COMPARISON.md` overstated relative
  to what n=50 supports. Those require adversarial reading, not arithmetic.
- **n=1 model, n=1 probe, one easy slice.** A 6-case contract test and a
  single-file derivation are a low bar. They are enough to clear the
  availability and basic-competence gates, not enough to constitute the
  verification of record.
- **Independence is structural, not proven.** `muse-free` is a different family
  from this analysis's author and from `big-pickle` (the arm under test), which
  is what the policy requires. Whether it is independent *in practice* — i.e.
  whether it will actually dissent — is not testable in advance and is exactly
  what the real verification would reveal.
- **The training-on-prompts term is unresolved for any wider use.** See §0.

## 4. Next step

`followup-05`'s `COMPARISON.md` still has **no verification of record**. Muse
Spark clears the two gates above and is a defensible candidate, but promoting it
to verifier of record is an operator decision, not an inference from this probe.
