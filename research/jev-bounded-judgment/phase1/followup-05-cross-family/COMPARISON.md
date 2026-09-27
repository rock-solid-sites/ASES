# followup-05 — cross-family general-model arms: result

- **Issue:** #565 · **Date:** 2026-09-27 · **Branch:** `research/jev-phase1-565`
- **Pre-dispatch record:** `RECON.md` · **smoke record:** `SMOKE.md`
- **Corpus:** frozen and unmodified, `sha256 7dd4698f…f558c`, asserted before and
  after every run
- **Scorer:** `harness/score.py` **unmodified**, run once per arm via
  `--phase1-dir`; 320/320 cells complete in both scored arms, 0 routing
  mismatches, 0 confidence mismatches, 0 secret-scan hits
- **Credential scan:** 139 files, 0 hits across 14 credential values
  (full / first-20 / last-20) plus an `sk-` pattern sweep

---

## 1. What ran, what did not

| arm | model | role | outcome |
|---|---|---|---|
| Longcat 2.5 Preview | `opencode-go/longcat-2.5-preview-free` | cross-family | **0/64 — 403, no Go entitlement** (`SMOKE.md` §1) |
| Ling 3.0 Flash | `opencode/ling-3.0-flash-fin-free` | cross-family | **24/64 — output-contract failure** (§3) |
| Big Pickle | `opencode/big-pickle` | cross-family | **64/64 — scored** (§4) |
| MiMo V2.6 Flash | `opencode/mimo-v2.6-flash-free` | transport control | **64/64 — scored** (§5) |

**One of the two cross-family arms produced a scoreable grid.** The programme-
level verdict therefore cannot satisfy the two-arm rule fixed in `SMOKE.md` §5
and is **inconclusive by construction** (§6). That is a statement about the
experiment's power, not about Jev.

## 2. Reproducibility check (free, unplanned)

`big-pickle` was run twice over the identical frozen corpus with different
batching — 16 cases/invocation, then 8. All 64 answer strings are
**byte-identical**. Answers are stable across batching for this arm.

This is a single-arm, single-corpus observation. It is evidence of
determinism-under-batching for one model, not a general stability claim.

## 3. `ling` — negative result: the output contract is not honoured

`ling` answered **24 of 64** cases. Chunks 00–02 conformed; chunks 03–07 all
failed validation, and the failure is **not** a transport fault — every one
exited 0 with a completed response.

The model produced markdown prose containing its reasoning and bolded
answers, then asserted compliance it did not achieve:

> *"The NDJSON output above contains one line per case in order…"* — chunk 03

> *"The NDJSON output is complete with all 8 cases answered…"* — chunk 05

Zero parseable `{"case_id", "content"}` objects existed in any text block of
any failing chunk. Chunk 03's prose covered only 6 of 8 cases.

**A prose parser was deliberately not written.** Extracting `→ **NO**` from
markdown would have been a parsing surface invented *after* seeing which chunks
failed, it is ambiguous for the `choice` type (chunk 07 used backticks, e.g.
`` `opt_w1e6` ``), and it would convert a compliance failure into a pass. Its
judgments look plausible in the prose; that is not a measurement.

**Why this matters beyond this arm.** A comparator that cannot reliably emit a
one-token answer cannot serve as a bounded-judgment baseline at all: the
mechanism under test is the ability to return a machine-actionable decision. A
model that answers correctly in prose but cannot commit to a token has failed
the property being evaluated, regardless of its reasoning quality.

`ling` is reported as 40 unscoreable cells. Those cells were **attempted** and
produced non-conforming output, so recording them as `not_attempted` would be
false; recording them as parse errors would require inventing labels. They are
left **unscored and reported as a shortfall** — `score.py` correctly refuses to
score a partial grid rather than silently absorbing the gap.

## 4. `big-pickle` — the cross-family result

Frozen scorer, complete 320-cell grid:

| quantity | value |
|---|---|
| answerable cases | 50 |
| correct | **49** |
| errors | 1 (`c-p4b`) |
| accuracy | **0.980** |
| unusable cells | **0** of 64 |
| typed errors | **0** |
| paired McNemar vs Jev | **b=0, c=0, ties=50** |
| per-area accuracy | A 22/22 · C 15/16 · D 12/12 |
| **pre-registered band** | **Jev's tier UNSUPPORTED** |

`big-pickle` and Jev produce the **same label on all 50 answerable cases**.
There is no cell where either is right and the other wrong.

The single error is `c-p4b` — the known ground-truth defect from D2 F1, whose
"truth is not derivable from model-visible text". It is the same cell the
Phase-1 verdict identifies. Both mechanisms fail it; it is not evidence about
either.

`big-pickle` differs from Jev on exactly 4 of 64 labels, and **all four are
unanswerable area-B cases** (`b-a01`, `b-a05`, `b-i01`, `b-i03`;
`answerable=false`, `abstain_expected=true`). Jev answered all four "yes";
`big-pickle` answered all four "no". Neither is scored, and the Phase-1 finding
that no mechanism abstains is reproduced: all three mechanisms emitted a label
on **14/14** unanswerable cases.

## 5. The transport control — the framing confound, measured

`mimo` is the same model followup-02 measured over direct HTTP. Re-run through
the agent route, on the same corpus with the same frozen prompt construction:

| | direct HTTP (followup-02) | agent route (followup-05) |
|---|---|---|
| answerable accuracy | 48/50 = 0.960 | 49/50 = 0.980 |
| label flips | — | **1 of 64** (`c-p6a`: `no` → `yes`) |
| cells correct only in this run | — | 1 (`c-p6a`) |
| cells correct only in the other | **0** | — |

**The agent-routing confound is 1 cell in 64 (1.6%), and it favours the agent
route.** The confound declared in `RECON.md` §4 is therefore empirically small,
and it does not plausibly manufacture `big-pickle`'s result.

### 5.1 A fragility this control exposed

`c-p6a` is not a random cell. In followup-02 it was **the single discordant
cell** — the one that produced the documented `c=1`, which was half of that
run's pre-registered refutation band (`acc ≥ 96% and c ≤ 1`).

The same model, on the same corpus, with the same prompt, flips that cell
under a different transport. So the `c ≤ 1` criterion was satisfied by a
one-cell margin on a cell that **is not stable across transport**.

* **WHY this matters:** the band in `findings.md` §6 was calibrated against the
  noise the Phase-1 sample already documents, but the transport axis was never
  part of that noise model.
* **WHAT the basis is:** one model, one corpus, two transports, 1/64 flip, and
  the flipped cell is the one the earlier band turned on.
* **HOW CERTAIN:** evidence-based for "this cell is transport-unstable";
  **guess** for how much such instability exists in general. n=1 cell, n=1 model.
* **WHAT-NOT-TESTED:** transport stability of any other cell; whether the same
  cell flips under other framings; whether a different corpus would show the
  same. The `b=0, c=0` result for `big-pickle` rests on 50/50 agreement and is
  *not* affected by this, because it never depended on a single discordant cell.

## 6. Verdict

**Programme-level: INCONCLUSIVE, by construction.** The two-arm agreement rule
(`SMOKE.md` §5) cannot be satisfied with one scorable cross-family arm. This is
reported rather than resolved by privileging the arm that did score.

**Arm-level, for `big-pickle` alone: Jev's tier UNSUPPORTED** on the
pre-registered bands — 0.980 accuracy, `c=0`.

**Direction of evidence.** Four independent comparisons now point the same way:

| comparison | family relation | result |
|---|---|---|
| followup-01 `space-bunny-free` | corpus-author family (weaker test) | 49/50 raw, 48/48 corrected, b=0/c=0 |
| followup-02 `mimo-v2.6-flash` | cross-family, direct HTTP | 48/50 raw, 47/48 corrected, c=1 |
| followup-05 `mimo-v2.6-flash` | cross-family, agent route | 49/50, b=0/c=0 |
| followup-05 `big-pickle` | cross-family, agent route | 49/50, b=0/c=0 |

Not one of them has produced a cell where Jev is right and a free cross-family
general model is wrong, at any point in this programme. That convergence is
worth stating — while being clear that it is four measurements of a *tie*, not
four measurements of Jev's inferiority.

**The brief's original question is now answered in the negative, with the
qualifier that it was answered on a synthetic template corpus.** Phase 1 left
it "untested" because the single comparator was confounded and the decisive
margin was one cell. The confound is now removed (a genuinely cross-family
arm), the margin is now 50/50 agreement rather than one cell, and the
convergence across four comparisons is consistent.

**This does not establish that Jev has no place in the hierarchy.** The
operational case from followup-04 — 13.2× median latency, 70.8× p99, flat
concurrency scaling, 0 failures in 238 calls, 1.70× cheaper per correct
decision — is untouched by this followup and is unaffected by a capability
tie. A bounded-judgment tier justified on latency and reliability is a
different claim from one justified on accuracy, and only the accuracy claim is
addressed here.

## 7. What this followup does not establish

- **Q2** (unanswerable-confidence tail past 0.90) — untouched; the 0.04 margin
  stands. Reinforced negatively: all mechanisms still answer every unanswerable
  case.
- **Q3** (is the graded distribution usable as a probability) — untouched.
  `big-pickle` emits one-hot vectors, as MiMo did, so this followup adds no
  calibration evidence on either side.
- **Q4** (does any of this survive outside a template corpus) — **untouched and
  now the binding limitation.** Every number is on 64 synthetic cases from 30
  templates authored by one family.
- **Q6** (can the harness express abstention) — untouched. `abstained` remains
  hard-coded `false`; all three mechanisms answered 14/14 unanswerable cases.
- **No significance test.** n=50 answerable. Per `findings.md` §6 a 1–2 cell
  difference is inside documented noise; a 50/50 agreement is outside it, but
  that is a statement about this sample.
- **Family variance is not characterised.** Two arms were requested; one was
  structurally unavailable and one failed its output contract. The pre-registered
  multi-arm rule (report each arm, report the spread) could not be exercised
  beyond a single arm. Whether free general models are *uniformly* this strong,
  or whether `big-pickle` is an outlier, is **unknown**.
- **Latency and cost were not measured** for these arms. `latency_ms` and
  `usage` are recorded as `null` by design: per-case latency is not
  individually observable when 8 cases share an invocation, and agent-route wall
  clock is not comparable to the direct-HTTP arms (`RECON.md` §4). Nothing here
  bears on the operational axis.
- **Two arm-level confounders remain unquantified:** batching (8 cases per
  invocation — a free-model compliance concession, and its influence on answers
  is untested) and the agent system prompt (cannot be suppressed through this
  route). `big-pickle`'s 16-vs-8 byte-identical result bounds the first for that
  one arm and says nothing about the second.

## 8. Provenance index

| Claim | Artefact |
|---|---|
| corpus unmodified | `sha256 7dd4698f…f558c`, asserted pre/post in `smoke/run_arm.py`, `smoke/stage_arm.py` |
| longcat 403 | `out-chunk16-record/` + `SMOKE.md` §1 |
| ling 24/64, prose + false compliance claim | `out/runlog-ling.json`, `out/events-ling-0[3-7].jsonl`, `SMOKE.md` §3 |
| big-pickle 49/50, b=0/c=0 | `out/band-big-pickle.json`, `staging/big-pickle/results/{scored.ndjson,metrics.json}` |
| mimo 49/50 agent route | `out/band-mimo.json`, `staging/mimo/results/{scored.ndjson,metrics.json}` |
| transport effect 1/64 | `followup-02-mimo-v2.6-flash/results/mimo_raw.ndjson` vs `staging/mimo/results/scored.ndjson` |
| 16-vs-8 byte-identical | `out-chunk16-record/answers-big-pickle.ndjson` vs `out/answers-big-pickle.ndjson` |
| 0 credential hits | 139-file scan, 14 values × 3 variants, 0 hits |

Raw model answers, per-chunk event streams, run logs, and both complete
per-arm grids are retained in this directory. Nothing was reduced to pass/fail
and no failed result was discarded.
