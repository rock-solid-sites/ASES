# followup-01-spacebunny

**Crosslink issue:** #565 · **Status:** complete — one baseline run, scored,
reported. · **Run:** 2026-09-26 · **Branch:** `research/jev-phase1-565`

A single bounded follow-up experiment to the completed Jev Phase 1 diagnostic
(`../`): run **one** new baseline — `space-bunny-free` — over the **unchanged**
frozen corpus under **frozen conditions**, and compare it to the frozen Jev
results. Nothing else was changed: no new cases, no prompt tuning, no
temperature change, no re-authoring, no re-run of anything.

**Result in one line:** spacebunny ties Jev exactly — 0 discordant cells in 48
paired answerable cells — and the pre-registered band lands on **REFUTES a Jev
niche**, on a **2-cell margin**, with one such cell observed flipping between
two runs of this same mechanism. **Read `comparison.md` §6 and §7 before
quoting any number.** The short version of §7: this is a same-family replicate,
not the cross-family test that `../findings.md` §6 pre-registered, so it does
**not** resolve Q1.

---

## Scope

**In scope.** One new baseline (`spacebunny`) over the frozen 64-case corpus;
deterministic scoring against frozen ground truth; a paired comparison with the
frozen Jev run; the `findings.md` §6 decision bands applied verbatim; a bounded
transport-failure sensitivity.

**Explicitly out of scope, and not done.** No new or edited cases. No change to
the harness, the scorer, the bands, or any frozen Phase-1 artefact. No re-run
or retry of the baseline. No significance test (`../schema.md` §5). No
escalation/confidence analysis — `spacebunny` is hard-decoded to confidence 1.0
by construction, so its threshold behaviour is an encoding artefact
(`../findings.md` §4 L7) and is not measured. No cross-family model: that is a
different experiment and is operator-gated.

**Writes are confined to this directory.** No file outside
`research/jev-bounded-judgment/phase1/followup-01-spacebunny/` was created or
modified. No push.

---

## Frozen inputs

Verified by sha256 **before** any HTTP call, on every run, by the runner itself.
A mismatch is a hard stop, not a repair.

| file | sha256 |
|---|---|
| `../cases.ndjson` | `7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c` |
| `../results/jev_raw.ndjson` | `e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc` |
| `../results/baselines_raw.ndjson` | `42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba` |

## Frozen conditions

| | value |
|---|---|
| model | `space-bunny-free` (`opencode-go/space-bunny-free`), cost 0/0/0/0, context 1,048,576, catalog refreshed 2026-09-26 |
| endpoint | `POST https://opencode.ai/zen/v1/chat/completions` — the disclosed Zen route, identical to the frozen `general_model` route |
| prompt | `GEN_SYS` + request shape **imported** from `../harness/run_baselines.py`, not re-implemented |
| `max_tokens` / `temperature` | 256 / 0 — as frozen |
| attempts per cell | **1** (`max_attempts=1`) |
| retries | **0** |
| cases | 64, unchanged |

**Frozen-condition check.** For every one of the 64 cases, the rebuilt request
must hash-equal the frozen `general_model` row's `request_hash` **and** body-equal
its `request_body`. Verified 64/64. A mismatch is a redesign trigger: the run
would be abandoned, not adjusted. Independent corroboration: total input tokens
were **16527 in both this run and the frozen run** — identical to the unit.

**One disclosed transport-level difference:** the `x-opencode-session`
provenance header is `jev-phase1-followup-01-spacebunny-20260926` rather than
the frozen run's id, so the two runs stay separable in provider telemetry. It is
a header, not part of the hashed body, and does not enter the prompt.

---

## Reproduce

Python 3.10+, **standard library only**. No install step, no network for
scoring. `OPENCODE_GO_API_KEY` must be set and non-empty for the runner; its
value is never printed or recorded.

All commands are relative to the repository root and were **tested in a clean
clone** of `research/jev-phase1-565`; the scoring outputs reproduced
**byte-identically** (`comparison.json` `c1808199…`, `paired.ndjson` `23c016f5…`,
`manifest.json` `07b3c98a…`).

### 1. Verify the gates — zero HTTP calls

```bash
python3 research/jev-bounded-judgment/phase1/followup-01-spacebunny/harness/run_spacebunny.py --check-only
```

Expected: `3` frozen digests OK, `64/64` requests identical, key present, and
`--check-only, no call made`.

### 2. Re-score the committed raw run — deterministic, no network

```bash
python3 research/jev-bounded-judgment/phase1/followup-01-spacebunny/harness/score_followup.py --self-check
```

Expected: `DETERMINISM: IDENTICAL`. Pin the two wall-clock-derived fields to
reproduce the committed bytes exactly from any clone:

```bash
python3 research/jev-bounded-judgment/phase1/followup-01-spacebunny/harness/score_followup.py \
  --self-check \
  --generated-utc 2026-09-26T04:58:49Z \
  --commit f4ad24acf6c6a2467445ba8d242aaf0895594769
```

This is the exact command used to verify the clean clone. `--commit` pins the
manifest's `commit` field to the commit that carries the **raw evidence being
scored** (`f4ad24ac`, the raw run); the scorer itself lands in the next commit,
so it cannot hash itself.

### 3. Re-run the baseline — 64 live calls, **not** part of reproduction

```bash
python3 research/jev-bounded-judgment/phase1/followup-01-spacebunny/harness/run_spacebunny.py
```

**Do not run this to reproduce the numbers.** The run is N=1 per cell with zero
retries, on a free-tier unpinned endpoint, and `comparison.md` §6.1 shows two
labels and one transport failure do **not** reproduce between samples. Re-running
replaces a recorded sample with a new one; it does not verify anything. The raw
run is committed and is the evidence; the scorer is what reproduces.

To point the same protocol at a different model (the cross-family test
`../findings.md` §6 asks for) requires only changing the model id in
`run_spacebunny.py`'s `GENERAL_MODEL` import — but that is an operator-gated
model selection per `AGENTS.md`, and the frozen-condition gate will refuse any
change to the request itself.

---

## Layout

| path | what |
|---|---|
| `harness/run_spacebunny.py` | runner. 4 pre-call gates; `max_attempts=1`; no retries. |
| `harness/score_followup.py` | scorer. stdlib only; reuses `../harness/common.py` + `../harness/score.py` (`build_cell`, `_acc`, `_paired_gain`, `load_cases`, …). |
| `results/spacebunny_raw.ndjson` | 64 rows, same row format as `../results/baselines_raw.ndjson`; verbatim raw responses, `http_status`, `latency_ms`, `usage`, `typed_error`, `timestamp_utc`, `model_id`, `endpoint`, `request_hash`/`request_body`. |
| `results/paired.ndjson` | 64 rows: per case, Jev and spacebunny verdicts, transport flags, raw **and** F1-corrected correctness. |
| `results/comparison.json` | every number with its denominator, plus the band evaluation, the flip margin, and the replicate-stability block. |
| `results/manifest.json` | frozen hashes, model id, endpoint, conditions, commit, timestamps, error counts, output digests, secrets declaration. |
| `comparison.md` | **the report.** Read this one. |

---

## How to read a number from here

1. **The denominators are in the artefact.** Every accuracy block carries
   `n_answerable`, `n_usable_in_answerable`, `n_transport_failures_in_answerable`
   and `n_correct`. Transport failures are excluded from semantic denominators
   and reported separately, per the brief.
2. **Raw and F1-corrected are both reported**, and the correction
   (`../verification.md` §2 F1: `c-p4a`+`c-p4b` → unanswerable, answerable
   50 → 48) is applied **identically to all three mechanisms**.
3. **The band verdict has a 2-cell margin** (`comparison.md` §6.2). One such
   flip was observed between two runs of this mechanism.
4. **The confound runs one way.** Space Bunny is a different family from Jev but
   the **same** family as the corpus author, harness author, prompt author and
   verifier (`../findings.md` §4 L1). It can only **inflate this baseline**. The
   tie is an upper bound on the baseline's real standing.
5. **This is not the Q1 experiment.** `../findings.md` §6 pre-registered it for
   a **cross-family** model. This run is a same-family replicate. Q1 is still
   open.
6. n=64, one run, N=1 per cell, free-tier unpinned models. No significance test
   is claimed anywhere (`../schema.md` §5).
