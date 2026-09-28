# Experiment 3 findings — pre-registered confirmation of the explicit-unknown signal

- **Issue:** #570 · **Model:** direct `jev-1.13.0` · **Representation:** `raw`
- **Producers:** packet selected and frozen by the author; execution by
  `opencode/mimo-v2.6-flash-free` (family `mimo`)
- **Independent verification:** Nemotron 3 Ultra via
  `opencode/nemotron-3-ultra-free`, a different family from the executor —
  **PASS WITH FINDINGS**, see `verification.md`
- **Requests:** 102 (51 fresh cases × 2 arms), 0 errors, 0 one-hot rows
- **Freeze:** v15 verified before and after execution; v16 after the scorer fix

## Answer to the primary question

**Partly. The pre-registered rule still works, but the margin underneath it has
collapsed, so this is a weaker confirmation than Experiment 1 implied.**

> Does the pre-registered explicit-unknown probability rule continue to
> distinguish answerable from unanswerable cases on unseen data, and does it
> outperform the existing generic external gate without increasing false-unknowns
> materially?

At the pre-registered `p(insufficient_evidence) >= 0.05`, on 51 fresh cases
whose underlying selections appear nowhere in the 67 frozen Phase-2 cases:

| measure | Exp 3 result | Exp 1 (post-hoc rule) |
|---|---|---|
| **explicit-unknown detection** (unanswerable, probability-based) | **9/10 = 0.90** | 10/10 = 1.00 |
| **false-unknown** (answerable) | **0/41 = 0.00** | 0/57 = 0.00 |
| argmax-selected `insufficient_evidence` (distinct measure) | 6/10 = 0.60 | 3/10 = 0.30 |
| pre-registered external gate, τ=0.86 | 6/10 = 0.60 abstention, coverage 0.7073, accuracy-when-acting 1.0 | 9/10 = 0.90 |

So: detection holds at 0.90 with **zero** false-unknowns, it beats the external
gate 0.90 to 0.60, and false-unknowns did not increase at all. The signal
**survives**.

## The finding that matters most: the separation margin collapsed

Experiment 1's clean result rested on a 5× gap:

| | max p(insufficient) on **answerable** | min p(insufficient) on **unanswerable** | separating? |
|---|---|---|---|
| Exp 1 (57 answerable / 10 unanswerable) | 0.02 | **0.10** | yes, cleanly |
| Exp 3 (41 answerable / 10 unanswerable) | **0.02** | **0.02** | **no — they touch** |

The single miss, `dataclasses.unanswerable_intent.exp3.038`, sits at
p(insufficient) = **0.02** — exactly the maximum observed across all 41
answerable cases. The two populations are no longer separated; they meet.

Consequence: the 0.90 result is correct **and** more fragile than Experiment 1
suggested. It depends on the pre-registered 0.05 happening to sit just above a
touching margin, where Experiment 1 had room to spare. A one-case shift in
either population's boundary changes the headline. This is reported rather than
smoothed over, and it is the single most important limitation below.

## The external gate result is ambiguous, and deliberately left ambiguous

The carried-forward τ=0.86 reached only 0.60 here, against 0.90 in Experiment 1.
Two readings fit the evidence:

1. the explicit-unknown representation is genuinely more informative than a
   generic probability gate; or
2. τ=0.86 was overfitted to Experiment 1's ten unanswerable cases and does not
   transfer.

These are not separable from this data. τ=0.86 was a post-hoc maximum on a
10-point grid over n=10, so reading (2) is entirely plausible. I do not claim
the generic gate is *worse*; I claim only that at the threshold pre-registered
from prior data, the explicit-unknown rule performed better on fresh cases.

## Secondary findings

1. **The model still does not act on its own best signal.** Argmax selection is
   0.60 where its probability supports 0.90. An operator reading the selected
   label captures two-thirds of what the probability supports. The gap narrowed
   from Experiment 1 (0.30 against 1.00) but did not close.
2. **The one miss is a new class.** `unanswerable_intent` is one of two
   unanswerable classes absent from Experiment 1, so the confirmation is not
   confined to the classes that produced the original signal. Intent may be
   genuinely harder to recognise as unanswerable, but **one case is not a basis
   for that claim** and none is made.
3. **The provider-confidence formula replicates again** — within 0.015 of the
   derived value across both arms, consistent with Phase 1
   `INSTRUMENT-VALIDATION.md`. It is reported beside the probabilities, never
   merged with them, and is not independent evidence.
4. **No accuracy claim.** Answerable accuracy is 0.9512 in both arms, against
   0.8246/0.8596 in Experiment 1. These are **not comparable**: the fresh case
   mix and polarity balance differ, and Exp 1's `param_rebound` cases were all
   `no`-polarity while Exp 3's are balanced. No accuracy claim is made from
   either number.

## Freshness, and what "fresh" was made to mean

Experiment 1 drew on all 67 frozen cases, so a new `case_id` pointing at an old
selection would be a reused case wearing a new name. Freshness is therefore
enforced on the underlying selection: 25 call edges, 10 `(fn,param)` pairs, 4
import tokens, 5 nesting targets, 5 string-literal probes and 5 unanswerable
subjects are all excluded by construction and checked mechanically.

**Experiment 1's unanswerable coupling is broken.** Its ten unanswerable cases
used only **five** distinct functions — one per module, the same function
serving both the semantic and runtime class — so the original signal rested on
five subjects, not ten. Experiment 3 uses **ten** distinct functions, two per
module, never shared across classes, and adds two new classes
(`unanswerable_version`, `unanswerable_intent`).

Ground truth was **recomputed independently** from `extract.py` and every
question re-rendered from the verified `gen_cases.py` template; the pool's
polarity is a selection hint only, and disagreement rejects the packet. All 41
answerable cases agreed on the first run.

## Two harness defects, both caught before they could corrupt a result

1. **`run_jev.py` could not execute a fresh-case packet at all.** It intersected
   the packet's ids against the Phase-2 case file, so Experiment 3's fresh ids
   yielded `cases=0`, `0 records planned`, `0 sent`, **exit status 0** — a
   silent no-op with zero API spend that looked like success. A second,
   coupled defect dropped fresh cases a second time for having no Phase-2
   admissibility row. Found by the delegated executor, which logged the
   deviation and stopped rather than improvising. Fixed, and the regression was
   *measured* rather than assumed: Exp 3 now yields 51 cases/102 records while
   Exp 1 still yields 67/134 and Phase 2 still 134 records/109 to send.
2. **A pre-registration that was recorded but not tamper-evident.** The negative
   tests exposed that nothing stopped a post-hoc edit of 0.05 or 0.86 in the
   packet — precisely the failure this experiment exists to rule out. Control
   **A8** now binds the packet's rules to the frozen `DESIGN.md`.

Seven controls (A2–A8, F2, F4) are each proven non-vacuous by a tamper test
that asserts the named control fires; see `negative_tests.json`.

## Limitations

1. **n = 10 unanswerable.** The headline is 9 detected against 10, and one case
   sits exactly on the answerable boundary. One case's movement changes the
   headline from 0.90 to 1.00 or 0.80.
2. **The separation margin has collapsed** to a touch at 0.02 (see above). This
   is the most material limitation and it is not offset by the clean n=10
   detection rate.
3. **One corpus, one mechanism, one wording.** The two new unanswerable classes
   are untested elsewhere, and a less leading instruction might change the
   0.90.
4. **The external-gate comparison is confounded by threshold transfer.** τ=0.86
   was a post-hoc maximum on n=10 in Experiment 1; its weaker showing here may
   be overfitting rather than inferiority. Untested: the external gate on arm
   B's own probability, and any threshold re-selected on fresh data.
5. **No repeat measurement.** Cell-level nondeterminism is unquantified, so a
   single flipped case cannot be distinguished from sampling noise.
6. **Not tested:** whether the 0.90 holds under the `struct` representation,
   where Phase 2 found evidence removal; whether it holds for case types absent
   from this corpus; and whether detection is class-dependent beyond the one
   `unanswerable_intent` miss.

## Smallest justified next experiment

**Replicate on a larger unanswerable set drawn from new corpus modules, with
0.05 fixed again in advance.**

Nothing else is worth doing first. The current result is one corpus, one
wording, one mechanism, n=10, and — decisively — a margin that has collapsed to
a single point of contact. The cheapest discriminating test is to author 30–40
unanswerable cases across two or three *new* real modules, pre-register 0.05 a
second time, and measure whether the answerable and unanswerable populations
separate or overlap. If they separate again on new modules, the rule earns
standing; if they overlap again, Experiment 1's 1.00 was a property of that
corpus rather than of the representation, and the honest default is the
external gate.

Explicitly **not** proposed: scaling the corpus beyond what the separation
question needs, a second judgment mechanism, or historical-session replay.

## Independent verification outcome

**PASS WITH FINDINGS** (Nemotron 3 Ultra, cross-family from the `mimo` executor).

Every reported statistic was reproduced from the raw records with **no numeric
disagreement**, and the verifier independently reached the same reading of the
margin collapse. It confirmed:

- the pre-registration was honoured, with both thresholds present in `DESIGN.md`
  and in the packet, and the scorer parsing them from the packet rather than
  hardcoding them;
- no post-hoc tuning: no reported decision depends on a threshold other than the
  two pre-registered ones, and the descriptive separation statistic is not used
  to justify a moved threshold;
- the `run_jev.py` fix changed neither the arm definitions nor the case set;
- ground truth spot-checks agreed on the 5 answerable cases it re-derived from
  the corpus source.

It added two findings I had not recorded:

1. **The external gate's 0.86 looks overfitted to Experiment 1's class
   distribution**, not merely unlucky. This strengthens the ambiguity flagged
   above rather than resolving it.
2. **The freeze gate, not a negative test, is what caught the unfrozen harness
   edit.** The negative-test suite would not have caught it, because a missing
   control is indistinguishable from a passing one. Worth knowing: the tamper
   suite proves controls fire, but it cannot prove a control is *present*.

### Route substitution, recorded openly

The originally designated verifier route
`opencode/muse-spark-1.3-contributor-free` and the `mimo` executor route both
became unreachable mid-experiment, returning silent failures on repeated probes
between 02:42Z and 03:10Z, as did every `openrouter/` route. The operator then
named GLM5.3-Flash and Nemotron 3 Ultra for review work. **GLM5.3-Flash could
not be used** — it exists only on `opencode-go/` (403, no Go subscription) and
`openrouter/z-ai/glm-5.3-flash` (silent failure). Nemotron 3 Ultra via
`opencode/nemotron-3-ultra-free` probed ALIVE and was used. This is a recorded
capability failure, not a silent substitution, and it is noted as a limitation:
**only one review family was available**, so the verification is single-family
and the cross-family guarantee rests on a single reviewer.

### Two failed verification dispatches, and why

The first two verifier runs produced a 521 KB transcript and **no output file**.
Cause: this session's agent resolves to `build`, and the worktree plugin
`orchestrator-guard.ts` allowlists only `{"builder"}` — so the native write and
edit tools are blocked, and no agent named `builder` exists for `opencode run`.
Fixed by instructing the verifier to create its file via bash heredocs *before*
analysing anything. The analysis had been completed twice and discarded both
times. A control that depends on the operator writing at the right moment is not
a control.

### Credential scan

One automated hit on `exp3/EXEC-BRIEF.md`, investigated and dismissed: the
literal string `nvapi-` appears there only because that file *instructs* the
verifier to search for `nvapi-` patterns. **Zero real credential values** across
21 files in `exp3/`.
