# followup-02-mimo-v2.6-flash

**Crosslink issue:** #565 · **Status:** **COMPLETE — 64/64 cells, 0 transport
failures, band verdict REFUTES a Jev niche.** · **Run:** 2026-09-26 · **Branch:**
`research/jev-phase1-565`

The confound-free cross-family baseline for the Jev Phase 1 diagnostic: run
**one** new baseline — `mimo-v2.6-flash` — over the **unchanged** frozen corpus
under **frozen conditions**, and compare it to the frozen Jev results.

**Result in one line: a cross-family cheap general model matched Jev.** 97.9%
against Jev's 100.0% on the F1-corrected answerable set, disagreeing on exactly
one cell and never ahead of Jev on any. The pre-registered band in `findings.md`
§6 lands on **REFUTES a Jev niche**, with both arms firing. Derived cost
**$0.00187012** — the first non-zero cost in Phase 1. **Read `comparison.md`**;
`BLOCKER.md` holds the original blocked record plus the appended **Resolution**.

| | value |
|---|---|
| grid cells run | **64 / 64** |
| transport failures | **0 / 64** (all HTTP 200, `finish_reason: stop`) |
| raw answerable accuracy (n=50) | **48/50 = 96.0%** |
| F1-corrected answerable accuracy (n=48) | **47/48 = 97.9%** |
| paired vs Jev — raw (`b`/`c`/ties) | **0 / 1 / 49** |
| paired vs Jev — corrected (`b`/`c`/ties) | **0 / 1 / 47** |
| **band verdict (F1-corrected)** | **REFUTES a Jev niche** |
| sufficiency flag | **not triggered** (50/50 usable; rule fires below 40) |
| derived cost | **$0.00187012** |

**The verdict is one cell wide.** At `k = 2` extra answerable errors the band
flips to "supports a Jev niche", and the raw-GT 96.0% sits exactly on the
refute floor. Read `comparison.md` §7 before quoting the verdict alone.

---

## Scope

**In scope (executed).** One new baseline (`mimo_v26_flash`) over the frozen
64-case corpus; a preflight credential-resolution and reachability smoke test;
a deterministic scorer reusing the followup-01 scorer structure and the frozen
`score.py` helpers with the mechanism swapped; the `findings.md` §6 decision
bands applied verbatim to the F1-corrected accuracy; a paired `b`/`c` against
frozen Jev; a bounded transport-failure sensitivity; a pre-registered
sufficiency flag; a reasoning-token and cost account; the §6 item-4 free rider
(the model's own typed-error count, replacing the lucky 1/64).

**Explicitly out of scope, and not done.** No new or edited cases. No change to
any frozen Phase-1 artefact, to the frozen harness (`harness/common.py`,
`harness/score.py`, `harness/run_baselines.py`), to the bands, or to
`../followup-01-spacebunny/**`. No re-run or retry of any grid cell — N=1, zero
retries, and the transport substitution changed nothing about that. No parameter
was tuned: `max_tokens` stayed 256, `temperature` stayed 0. No significance test
(`../schema.md` §5).

**Writes are confined to this directory.** No file outside
`research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/` was created
or modified. No push.

---

## Frozen inputs

Verified by sha256 **before** any HTTP call, on every run, by the runner itself,
and again before scoring. A mismatch is a hard stop, not a repair. All three
**matched** on this run.

| file | expected sha256 | verified |
|---|---|---|
| `../cases.ndjson` | `7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c` | **match** |
| `../results/jev_raw.ndjson` | `e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc` | **match** |
| `../results/baselines_raw.ndjson` | `42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba` | **match** |

## Model, route, and cost

| | value |
|---|---|
| model id | `mimo-v2.6-flash` (catalog `opencode-go/mimo-v2.6-flash`), family `mimo` |
| in the live catalog | **yes** — `opencode models opencode-go` lists it |
| context / output limit | 1,048,576 / 131,072 · temperature supported · reasoning true |
| endpoint | `POST https://opencode.ai/zen/go/v1/chat/completions` → **200** |
| route note | the Zen route the frozen `general_model` used returns `400 Model is unavailable` for this model, so the route change is forced by the model |
| credential source used | **`auth.json#opencode-go`** (label only; value never recorded) |
| cost per million tokens | input **0.14** · output **0.28** · cache read **0.0028** · cache write **0.00** |
| derived cost of this experiment | **$0.00187012** |

**Why this model.** `../findings.md` §6 Q1 asks whether Jev's non-advantage is a
property of cheap general models or of one family reading one family's prose.
`../findings.md` §4 L1 records that followup-01's `space-bunny-free` is the same
family as the corpus author, the harness author, the `GEN_SYS` author and the
verifier — a confound that can only **inflate** the baseline, and the reason
followup-01's verdict was not the answer to Q1. MiMo is a different family from
**both** Jev and the corpus author, so this run is the confound-free test Q1
asks for.

## Credential and transport (the two things a reproduction needs)

Both are recorded in full in `BLOCKER.md` §R2–R5. In short:

1. **`$OPENCODE_GO_API_KEY` has no Go entitlement** — the Go route returns 403
   for every model, the frozen one included. The subscribed credential is in the
   OpenCode CLI store, `~/.local/share/opencode/auth.json` → `opencode-go.key`.
   The runner tries the environment variable first and falls back **only** on
   that account-level entitlement 403. The value reaches curl on **stdin** via
   `curl -K -`, so it is in neither `argv` nor any file; only the source **label**
   is recorded.
2. **`urllib` is Cloudflare-rejected** (403, code 1010) with this credential,
   while `curl` is served normally. The runner therefore uses a `curl`
   subprocess. The frozen `harness/common.py` is **unmodified**.
3. **`x-opencode-session` is required** — the route answers `400 MissingSessionID`
   without it. The runner generates one UUID4 per run and records it (it is not a
   secret).

## Frozen conditions

| | value |
|---|---|
| prompt | `GEN_SYS` + request shape **imported** from `../harness/run_baselines.py`, not re-implemented |
| `max_tokens` / `temperature` | 256 / 0 — as frozen, not tuned |
| attempts per cell | **1** (`max_attempts=1`) |
| retries | **0** |
| cases | 64, unchanged |
| permitted differences from the frozen run | the `model` field; the route; the `x-opencode-session` header; the HTTP client (curl, not urllib) — none of which touches the hashed request body |

**Frozen-condition check — verified 64/64 on this run.** For every case, the
request rebuilt with the **frozen** model id `space-bunny-free` is hash-equal
*and* body-equal to the frozen `general_model` row. Independently, normalising
the `model` field of the request actually sent back to `space-bunny-free`
reproduces those same bytes, so the request differs from the frozen one **in the
model value and nothing else**.

---

## Reproduce

Python 3.10+, **standard library only** plus the `curl` binary. No install step.
Steps 1–2 make zero HTTP calls. Steps 3–5 make paid calls.

### 1. Verify the gates — zero HTTP calls

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/run_mimo.py --check-only
```

Expected: `3` frozen digests OK, `64/64` requests identical, both credential
sources listed as available (labels only), a generated `x-opencode-session`, and
`--check-only, no call made`.

### 2. Run the scorer — zero HTTP calls, from the committed raw rows

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/score_mimo.py
```

Expected: 3 frozen digests OK, `comparison.json` / `paired.ndjson` (64 rows) /
`manifest.json` rewritten. This is the deterministic step — it reads
`results/mimo_raw.ndjson` and makes no calls.

### 3. Confirm the scorer is deterministic

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/score_mimo.py --self-check
```

Expected: `DETERMINISM: IDENTICAL` — `comparison.json`, `paired.ndjson` and
`manifest.json` byte-identical across two scoring passes from the same inputs.

### 4. Re-run the preflight — 2 throwaway non-corpus calls (1 is rejected)

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/run_mimo.py --preflight-only
```

Expected: `env:OPENCODE_GO_API_KEY` → `http_status=403` (abandoned as
`entitlement_403`), `auth.json#opencode-go` → `http_status=200`,
`credential_source_selected='auth.json#opencode-go'`, `route_reachable=True`,
`max_tokens_consumed_by_reasoning=False`. `results/preflight.json` is rewritten.
Both calls are non-corpus throwaways: the smoke state contains no token from
`cases.ndjson`, so it can never be mistaken for a grid cell. Cost: ~$0.0000147.

### 5. Run the grid — 64 paid calls, N=1, no retries

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/run_mimo.py
```

Refuses to start unless a recorded preflight shows the route reachable. Writes
`results/mimo_raw.ndjson` (64 rows) and `results/run_session.json`. Cost on this
run: **$0.00185542**.

**This step re-sends the 64 cells.** It is a fresh N=1 sample, not a
reproduction of the committed rows: `findings.md` §4 L3 records that reasoning
length is non-deterministic even at `temperature 0`, and this run's worst cell
spent 245 of its 256 output tokens on reasoning (§4 of `comparison.md`), so a
re-run can differ. Do not run it to "confirm" the numbers — run step 2 or 3,
which read the committed rows.

### Pinning the session header

Both `run_mimo.py` and `score_mimo.py` accept pins for byte-reproducible
artefacts:

```bash
python3 .../harness/run_mimo.py --session-id 00000000-0000-4000-8000-000000000000
python3 .../harness/score_mimo.py --generated-utc 2026-09-26T00:00:00Z --commit <sha>
```

---

## Layout

| path | what |
|---|---|
| `harness/run_mimo.py` | runner (v1.1.0). 3 pre-call gates, credential resolution, curl transport, `max_attempts=1`, no retries. |
| `harness/score_mimo.py` | scorer (v1.0.0). Reuses the frozen `score.py` helpers and hard-stops on any disagreement with them. |
| `harness/route_diagnostics.py` | the 6-probe reachability matrix from the blocked attempt; retained as the record of *which* blocker it was. |
| `results/mimo_raw.ndjson` | 64 raw rows, `mechanism: mimo_v26_flash`, full `usage` with reasoning tokens. |
| `results/paired.ndjson` | 64 rows: both verdicts per cell, raw + corrected, transport flags, usage. |
| `results/comparison.json` | every figure, machine-readable, with the frozen-scorer cross-checks. |
| `results/manifest.json` | digests, model record, credential source label, session header, cost, error counts. |
| `results/preflight.json` | the step-1 smoke test: env key 403 (abandoned), store key 200. |
| `results/run_session.json` | the per-run `x-opencode-session` UUID and credential source label. |
| `results/route_diagnostics.json` | the pre-unblock reachability matrix. |
| `comparison.md` | **the report.** Read this one. |
| `BLOCKER.md` | the original blocked record, plus the appended **Resolution** (§R1–R8). |
| `README.md` | this file. |

---

## How to read a number from here

1. **The verdict is one cell wide, and the file says so.** `k = 2` extra errors
   flips it; raw-GT 96.0% is exactly on the refute floor. Quote the paired table
   with the verdict, never the verdict alone (`comparison.md` §7).
2. **Q1 is answered, and the answer is that the premise fails on this corpus.**
   Per `../findings.md` §6, the correct next step after a refute is to drop the
   Jev tier from the hypothesis and spend budget on a non-synthetic evaluation
   (Q4) — not to commission Q2.
3. **Q4 is not answered by this.** 30 synthetic templates, one author family
   (L2); two families are now represented, not thirty. `comparison.md` §10.
4. **The abstention failure mode is untouched.** MiMo answered 14/14 unanswerable
   raw and 16/16 corrected — false-confidence rate 1.00, same as every other
   mechanism. Q6 stands: no mechanism here can express abstention, so area B is
   unmeasurable by construction and a Jev tier's value cannot be demonstrated on
   abstention with this harness.
5. **The reasoning margin is a live replication risk, not a resolved property.**
   92.4% of the output budget went to reasoning; the worst cell answered in 3
   tokens. Read the sufficiency flag first on any re-run.
6. **Phase 1 and followup-01 are unaffected.** Nothing here revises them; the
   frozen files are byte-identical.
7. **No significance test is claimed** (`../schema.md` §5). n=64, and the
   decision rests on 1 discordant cell.
