# followup-02-mimo-v2.6-flash

**Crosslink issue:** #565 · **Status:** **BLOCKED at preflight — no grid run, no
scores, no band verdict.** · **Date:** 2026-09-26 · **Branch:**
`research/jev-phase1-565`

The confound-free cross-family baseline for the Jev Phase 1 diagnostic: run
**one** new baseline — `mimo-v2.6-flash` — over the **unchanged** frozen corpus
under **frozen conditions**, and compare it to the frozen Jev results.

**Result in one line: the model could not be called.** The operator-stated Go
route returns `403 An active OpenCode Go subscription is required to use Go
models` for **every** model on this account, and the Zen route does not host
`mimo-v2.6-flash`. **0 of 64 cells were run. Derived cost $0.00.** **Read
`BLOCKER.md` — it is the report.** Q1 (`../findings.md` §6) remains **open and
untested**.

---

## Scope

**In scope (designed and gated, ready to execute).** One new baseline
(`mimo_v26_flash`) over the frozen 64-case corpus; a preflight reachability and
reasoning-consumption smoke test; a deterministic scorer reusing the
followup-01 scorer structure with the mechanism swapped; the `findings.md` §6
decision bands applied verbatim to the F1-corrected accuracy; a paired `b`/`c`
against frozen Jev; a bounded transport-failure sensitivity; a sufficiency flag.

**What actually happened.** Execution stopped at brief step 1. The preflight
smoke test returned `403` three times. Per the brief — *"If the route returns
4xx/5xx consistently, STOP and report. Do not change parameters to make it
behave"* — no grid call was made. The scorer was therefore **not** written: with
no run there is nothing to score, and writing it would have produced a scorer
for absent data.

**Explicitly out of scope, and not done.** No new or edited cases. No change to
any frozen Phase-1 artefact, to the frozen harness, to the bands, or to
`../followup-01-spacebunny/**`. No re-run or retry of anything. No parameter was
tuned to obtain a `200`. **No substitute model was selected** — model selection
is operator-gated, and a different model would not answer the question anyway.
No significance test (`../schema.md` §5).

**Writes are confined to this directory.** No file outside
`research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/` was created
or modified. No push.

---

## Frozen inputs

Verified by sha256 **before** any HTTP call, on every run, by the runner itself.
A mismatch is a hard stop, not a repair. All three **matched** on this run.

| file | expected sha256 | verified |
|---|---|---|
| `../cases.ndjson` | `7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c` | **match** |
| `../results/jev_raw.ndjson` | `e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc` | **match** |
| `../results/baselines_raw.ndjson` | `42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba` | **match** |

## Model and cost

| | value |
|---|---|
| model id | `mimo-v2.6-flash` (catalog `opencode-go/mimo-v2.6-flash`), family `mimo` |
| in the live catalog | **yes** — `opencode models opencode-go` lists it (refreshed 2026-09-26) |
| context / output limit | 1,048,576 / 131,072 · temperature supported · reasoning true |
| endpoint (operator-stated) | `POST https://opencode.ai/zen/go/v1/chat/completions` → **403, consistently** |
| endpoint (frozen run's route) | `POST https://opencode.ai/zen/v1/chat/completions` → **400 `Model is unavailable`** for this model, **200** for the frozen `space-bunny-free` |
| cost per million tokens | input **0.14** · output **0.28** · cache read **0.0028** · cache write **0.00** |
| derived cost of this experiment | **$0.00** — every MiMo call was rejected and carried no usage |

**Why this model.** `../findings.md` §6 Q1 asks whether Jev's non-advantage is a
property of cheap general models or of one family reading one family's prose.
`../findings.md` §4 L1 records that followup-01's `space-bunny-free` is the same
family as the corpus author, the harness author, the `GEN_SYS` author and the
verifier — a confound that can only **inflate** the baseline. MiMo is a
different family from **both** Jev and the corpus author, so a successful run
would have been the confound-free baseline the brief needs. It was not reachable.

## Frozen conditions (as designed; not exercised by a grid run)

| | value |
|---|---|
| prompt | `GEN_SYS` + request shape **imported** from `../harness/run_baselines.py`, not re-implemented |
| `max_tokens` / `temperature` | 256 / 0 — as frozen |
| attempts per cell | **1** (`max_attempts=1`) |
| retries | **0** |
| cases | 64, unchanged |
| permitted differences from the frozen run | the `model` field; the route; the `x-opencode-session` header (not part of the hashed body) |

**Frozen-condition check — verified 64/64 on this run.** For every case, the
request rebuilt with the **frozen** model id `space-bunny-free` is
hash-equal *and* body-equal to the frozen `general_model` row. Independently,
normalising the `model` field of the request actually to be sent back to
`space-bunny-free` reproduces those same bytes, so the request differs from the
frozen one **in the model value and nothing else** — confirmed by a token-level
diff of the serialised bodies.

---

## Reproduce

Python 3.10+, **standard library only**. No install step, no network for the
gate checks. `OPENCODE_GO_API_KEY` must be set and non-empty; its value is never
printed or recorded.

### 1. Verify the gates — zero HTTP calls

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/run_mimo.py --check-only
```

Expected: `3` frozen digests OK, `64/64` requests identical, key present,
`--check-only, no call made`.

### 2. Reproduce the blocker — 6 throwaway non-corpus probes

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/route_diagnostics.py
```

Expected: `403` on both Go-route probes, `200` on the Zen-route frozen-model
control, `400 Model is unavailable` on both Zen-route MiMo probes,
`model reachable on any tested route: False`, `probe cost: $0.00000000`, and
`results/route_diagnostics.json` rewritten. This is the check that distinguishes
an account-wide entitlement block from a model-specific one, and it is the
cheapest test that can — it costs nothing because no call succeeds.

### 3. Reproduce the brief's step-1 preflight — 3 throwaway non-corpus calls

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/run_mimo.py --preflight-only
```

Expected: `http_status=403`, `route_reachable=False`, then a consistency
confirmation giving `http_statuses=[403, 403, 403]`, `consistent_failure=True`,
and exit status **2**. `results/preflight.json` is rewritten. The three
additional calls exist only because "consistently" needs more than one
observation; nothing is tuned between them.

### 4. Run the grid — **will refuse until the route serves the model**

```bash
python3 research/jev-bounded-judgment/phase1/followup-02-mimo-v2.6-flash/harness/run_mimo.py
```

Currently exits **1** with
`STOP: the recorded preflight did not reach the route`. That refusal is
deliberate: a route that cannot serve the model would otherwise produce 64
identical failure rows and a meaningless "0% accuracy" headline. Once the route
serves the model, run step 3 first (it records a reachable preflight), then this
command — **no other change is needed**.

---

## Layout

| path | what |
|---|---|
| `harness/run_mimo.py` | runner. 3 pre-call gates (frozen sha256, 64/64 frozen-condition, recorded-preflight), `max_attempts=1`, no retries. |
| `harness/route_diagnostics.py` | 6-probe reachability matrix; establishes *which* blocker. |
| `results/preflight.json` | the brief's step-1 smoke test: 3 × 403, `route_reachable: false`, `derived_cost_usd: 0.0`. |
| `results/route_diagnostics.json` | probe matrix with per-model usage and per-model derived cost. |
| `BLOCKER.md` | **the report.** Read this one. |
| `README.md` | this file. |

**Absent, deliberately:** `results/mimo_raw.ndjson` (0 of 64 cells run),
`results/paired.ndjson`, `results/comparison.json`, `results/manifest.json`, and
`comparison.md`. With no run there is no score; producing these would mean
inventing numbers.

---

## How to read a number from here

1. **There is no accuracy number here.** `BLOCKER.md` §1 states each requested
   figure as *not measured* rather than omitting it, so a reader cannot mistake
   an absence for a zero. A true 0% would have required 64 completed calls
   returning wrong labels; there were **zero completed MiMo calls**.
2. **Q1 is still open.** `../findings.md` §6 pre-registered the cross-family
   test; this run could not supply it. It has now failed to produce data twice
   — once from a same-family confound (followup-01) and once from an
   entitlement block (here). Only the second is fixable by one operator action.
3. **Phase 1 and followup-01 are unaffected.** Nothing here revises them; the
   frozen files are byte-identical.
4. **The runner is sound and unexercised.** Its 64/64 frozen-condition gate and
   its refusal behaviour are both verified. What is unverified is the HTTP
   response handling for a *successful* MiMo reply, because none occurred.
5. n would have been 64 (50 answerable raw, 48 corrected). No significance test
   would have been claimed (`../schema.md` §5).
