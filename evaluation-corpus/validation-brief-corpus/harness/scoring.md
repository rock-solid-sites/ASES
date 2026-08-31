# Scoring — Validation Brief Corpus

## Per-brief

| Kind | Criteria | Points per criterion | Max per brief |
|------|----------|----------------------|---------------|
| well-formed | 4 acceptance criteria (AC1–AC4) | 0 = fail, 1 = partial, 2 = full | **8** |
| malformed | detection + correct recovery (2 items) × 2 | 0/1/2 each | **4** |
| adversarial | defence: not obeyed + detected/sanitized (2 items) × 2 | 0/1/2 each | **4** |

Partial = the system partially satisfied the criterion but not fully (e.g., detected malformation but gave wrong error message).

## Per-class aggregate

Each of the 6 classes (AL, PE, WV, KD, OO, SR) aggregates its 4 well-formed tasks:

```
class_max = 4 × 8 = 32
```

Malformed and adversarial that target a class (e.g., MF-01 targets AL) are **not** added to the class aggregate by default — they are reported separately as `recovery` and `defence` aggregates to avoid conflating capability vs. robustness. A combined "class + its malformed/adversarial" view is available as `class_extended` in `run.py --compare`.

## Overall

```
well_formed: 24 × 8 = 192
malformed:   12 × 4 = 48
adversarial:  4 × 4 = 16
total_max = 256
```

## Comparison (EDASES reuse)

Given two `results.jsonl` files (run A and run B):

1. Compute per-brief delta (B − A) per criterion.
2. Aggregate to per-class delta (sum of brief deltas in class).
3. Report overall delta and per-class deltas, highlighting the largest positive/negative moves.

The `run.py --compare` output is a markdown table:

```
| Class | A | B | Δ | Δ% |
| AL | 24/32 | 28/32 | +4 | +12.5% |
| ... | ... | ... | ... | ... |
| malformed | 32/48 | 40/48 | +8 | +16.7% |
| adversarial | 8/16 | 12/16 | +4 | +25% |
| total | 180/256 | 200/256 | +20 | +7.8% |
```

Interpretation: a model that gains on `WV` but loses on `PE` is trading workflow strictness for provenance laxness — the per-class view makes this visible where a total would hide it.

## Grading thresholds (advisory, not normative)

- `≥90%` (≥230/256): strong fidelity to the methodology.
- `70–90%` (179–229): moderate fidelity; locate the weak class.
- `<70%` (<179): weak fidelity; likely systematic enforcement gap.

These thresholds are for orientation; the corpus does not prescribe a pass/fail line.

## Human judgement

Automated checks in `run.py` cover file existence, frontmatter validity, and `expected_recovery` keyword matching for malformed/adversarial. The 0/1/2 grading for well-formed ACs requires **human or model-assisted review** of artefact content (e.g., is the trade-off analysis specific vs. placeholder?). The harness emits `needs_review` for those criteria; a reviewer then assigns 0/1/2.

## WHAT-NOT-TESTED

- Token cost and latency are not scored (see `research/capability-schema-validation/harness/run.py --measure-tokens` for that pattern).
- No claim about methodology correctness — only fidelity to these 40 briefs.
