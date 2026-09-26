# Followup-03 — independent verification

*Verifier: fresh session, no builder context. Issue **#565**. Verified at
`HEAD = 4e45187c11c696d7a7914ec8dc441a55f2280914`, branch `research/jev-phase1-565`,
worktree `/home/claude-code/projects/ASES/.worktrees/jev-phase1`.*

*Subject: `followup-03-operational/` — operational comparison of Jev 1.13
(free) vs MiMo V2.6 Flash (`README.md`, `comparison.md`, `subset.json`,
`harness/{run_ops,jev_ratelimit_probe,analyze_ops}.py`, `results/*`).*

*Read-only with respect to the repository. The only repository file this
verification writes is this document. All scratch — including an isolated copy
of `phase1/` used to re-run the harness — lives in
`/tmp/opencode/jev-phase1-followup3-verify/`. No push. No fix applied to any
fault found below.*

---

## Verdict

**The measured content is sound and reproducible. The classification layer is
not.** Every headline number in `comparison.md` that I could recompute from the
raw NDJSON reproduced **exactly** (24 of 24 statistic groups, 0 numeric
differences), the frozen-condition gate is real, no fabricated row was
detectable, no credential value is present in any artefact or in the git
history, and the live re-sample confirms reachability, label stability and
latency order of magnitude for both mechanisms.

The faults are in what the document *claims* those numbers show. Three are
material:

1. The claim that the study **"exhausted" the Jev quota "inside 197 calls"** is
   not supported by the evidence: the **first** call of the Jev window was
   already refused, so the window contains no observed transition from available
   to exhausted. It is labelled ESTABLISHED in three places.
2. The claim that the **403 phase "masks the cap"** is an inference presented as
   ESTABLISHED; the 403 body names no cap, and no discriminating test was run.
3. **Two interface statistics in `summary.json` are wrong**, and they point in
   opposite directions: the Jev-side probability-availability statistic is a
   never-computed `0/0` printed verbatim in the findings, and the MiMo-side
   statistic counts the harness's own 0/1 synthesis as "probabilities exposed on
   234 calls". The report's own §4/§7 interface claim is *true* — but no
   statistic in the deterministic summary supports it.

Plus one moderate arithmetic fault: the **transport-vs-service decomposition
double-counts DNS and TCP**, because curl's `-w` phase counters are cumulative.
The identity the report presents as exact is off by 3.19 ms on the mean and its
shares sum to 100.05% against a printed "100%".

**17 findings: 3 material, 3 moderate, 11 minor.** None overturns the study's
conclusion that the Jev/MiMo pair could not be measured as a matched pair, and
none changes a reported figure that `comparison.md` actually prints. Three
defects sit in `summary.json` only and are latent there.

---

## PASS/FAIL table

| # | Check | Result | One-line basis |
|---|---|---|---|
| 1 | Frozen-input integrity | **PASS** | Both frozen digests match; the 8 followup-03 commits add only new files under `followup-03-operational/`; no `phase1/`, `followup-01` or `followup-02` file modified. |
| 2 | Subset integrity | **PASS** (2 minor faults) | Independent re-implementation of `STRAT-OPS-v1` from the rule text reproduces the selection order, the 16-step trace and the canonical order exactly; F1 correction re-derived to `{c-p4a, c-p4b}`; no case text carried or altered. Faults: F12, F14. |
| 3 | Raw measurement integrity | **PASS** (5 minor faults) | Call counts match the recorded design exactly; `{(attempts, retries)} == {(1, 0)}` on all 486 rows + 6 transport probes; 0 curl phase-order violations; 0 rows with `num_connects > 1`; both frozen-condition gates reproduce 64/64 and 232/232. Faults: F3, F4, F10, F13, F14. |
| 4 | Independent recomputation | **PASS** | 0 numeric differences across 24 statistic groups recomputed from raw NDJSON without importing `analyze_ops.py`; 2 arithmetic faults found in the *definitions* (F5, F6). |
| 5 | Live sanity re-sample | **PASS** | 6 calls per mechanism. MiMo 6/6 HTTP 200, labels identical to the committed modal labels, latency 3.18–11.84 s vs committed median 4.04 s / p95 15.96 s. Jev 6/6 HTTP 429 `FreeUsageLimitError`. |
| 6 | Concurrency spot-check (C=4) | **PASS** | MiMo 12/12 HTTP 200, 0 errors, 0×429, makespan 63.73 s vs committed 70.28 s (same regime). Jev 12/12 HTTP 429 — reproduces the refusal, and reproduces the "reads as a speedup" trap the harness documented. |
| 7 | Classification audit | **FAIL** | F1, F2, F9 are mislabelled; F5 breaks the transport/service separation as specified; F3+F4 leave the ESTABLISHED interface claim unsupported by any statistic. Accuracy *is* correctly presented as a control, not the outcome. |
| 8 | Limitations & unverifiable claims | **PASS** (1 omission) | Limitations are stated and mostly correct (F8 misstates one). Undisclosed: F15 (free-tier serving priority as a confound on the one ratio favouring Jev). 10 claims are unverifiable; listed explicitly below. |

---

## 1. Frozen-input integrity — PASS

```
$ sha256sum cases.ndjson results/jev_raw.ndjson
7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c  cases.ndjson
e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc  results/jev_raw.ndjson
```

Both match the digests recorded in `subset.json.gate_at_freeze`,
`run_ops.FROZEN_INPUTS`, `summary.json.frozen_inputs_verified` and the README
(`7dd4698f…f558c`, `e17ae014…82d3bc`).

Scope of the 8 followup-03 commits (`a1a1c93a..HEAD`), 12 files, 7400
insertions, **0 deletions**:

```
followup-03-operational/README.md                        313 +
followup-03-operational/comparison.md                    312 +
followup-03-operational/subset.json                      541 +
followup-03-operational/harness/analyze_ops.py          1837 +
followup-03-operational/harness/jev_ratelimit_probe.py  253 +
followup-03-operational/harness/run_ops.py              1641 +
followup-03-operational/results/concurrency_defect_401.ndjson   36 +
followup-03-operational/results/jev_ops_raw.ndjson            197 +
followup-03-operational/results/jev_ratelimit_probes.ndjson     10 +
followup-03-operational/results/mimo_ops_raw.ndjson           243 +
followup-03-operational/results/summary.json                1887 +
followup-03-operational/results/transport_probe.json          130 +
```

`git diff --name-only a1a1c93a..HEAD` filtered to exclude
`followup-03-operational` returns **nothing**: no `phase1/`, `followup-01` or
`followup-02` file was touched. Working tree is clean apart from two Crosslink
bookkeeping entries (`.crosslink/.last-hydrated-ref` modified,
`.crosslink/agents-hygiene.json` untracked) — not study files. The three
`__pycache__/*.pyc` files on disk are gitignored and uncommitted.

## 2. Subset integrity — PASS

I re-implemented `STRAT-OPS-v1` **from the rule text recorded in
`subset.json`**, not by importing `run_ops.py`
(`/tmp/…/repro_subset.py`):

```
REPRODUCED n = 16
order match : True          # case_ids_in_selection_order
trace match : True          # all 16 selection_trace steps, in order
canonical   : True          # case_ids_canonical_order
coverage    : {"by_area": {"A": 7, "B": 4, "C": 2, "D": 3},
               "by_question_type": {"choice": 3, "noul": 12, "score": 1},
               "complete_contrastive_pairs": ["a-m07", "b-a02", "cp1"],
               "n_control_variants": 4, "n_unanswerable": 5}   == committed
constraints : all True (n in 12..16; areas A-D; all 3 qtypes;
                         unanswerable 5 >= 3; control variants 4 >= 1;
                         complete contrastive pairs 3 >= 1)
contrastive pair chosen by S7: a-m07 == recorded a-m07
derived F1 member ids: ['c-p4a', 'c-p4b'] == recorded ['c-p4a', 'c-p4b']
case-text/GT projections altered: NONE
subset entries carrying state text: NONE
```

Coverage requirements all met with margin: areas A/B/C/D = 7/4/2/3;
noul 12 / choice 3 / score 1; 5 unanswerable (≥3); 4 control variants (≥1);
**3** complete contrastive pairs (`a-m07`, `b-a02`, `cp1`) against a
requirement of 1. The S7 rule is reproducible from the corpus: pair `a-h01` is
excluded (member `a-miss1` unanswerable), `a-m01` is excluded (member `a-dist1`
already taken by S6), so `a-m07` is first by ascending `pair_id`.

**F1 correction** (`cp4`): I re-derived the member set mechanically — real
2-member pairs with both members answerable, then an anchor-token test for
derivability outside the pair — and got exactly `['c-p4a','c-p4b']`, the ids
`verification.md` §2 F1 names. It is a **verified no-op on this subset** (no
`cp4` member selected), so `answerable_after_f1 == answerable_frozen` for all 16
cases and `gt_answer_after_f1 == gt_answer` for all 16 — which is why every
`subset.json.cases[*]` projection is byte-identical to a fresh projection of
`cases.ndjson`. No case text is altered, and none is carried.

**Semantic scoring** uses the frozen ground truth with the F1 correction
applied by the same function followup-02 uses (`run_ops.f1_corrected_cases`,
carrying `F1_PAIR_ID`/`F1_MEMBER_IDS` with the §2 F1 comment). I re-scored the
warm block independently and reproduced `108/108` control and `132/132`
all-answerable.

## 3. Raw measurement integrity — PASS

### Call counts vs the recorded design

| file | rows | breakdown | design |
|---|---|---|---|
| `jev_ops_raw.ndjson` | 197 | warm 192 + warmup 5, all `block=null` | 16×12 = 192 warm + 5 warm-up ✔ |
| `mimo_ops_raw.ndjson` | 243 | `block=null` 11 (warmup 5 + warm 6, aborted) + `block=resume1` 232 (warm 192 + idle 3 + concurrency 36 + interface_probe 1) | ✔ |
| `concurrency_defect_401.ndjson` | 36 | 12 each at C=1/4/8, all HTTP 401, `$0.00`, 0 tokens | ✔ |
| `jev_ratelimit_probes.ndjson` | 10 | all 429 | 10 max ✔ |
| `transport_probe.json` | 6 | 3 per mechanism, HTTP 404 | 3 per mechanism ✔ |

Warm reps per case: 15 cases × 12, `b-a03` × 3 usable (+9 `empty_content`) = 12
attempts. Concurrency levels `{1:12, 4:12, 8:12}`, block `resume1`, 6 cases ×
2 reps, dispatch order case-major over the first 6 canonical ids, identical
across all three levels.

### N = 1, no retries

`{(attempts, retries)} == {(1, 0)}` across all 486 grid/probe/defect rows. No
retry path exists in the call path: `MAX_ATTEMPTS = 1`, `RETRIES = 0`, one
`subprocess` per call, `communicate()` once, no loop.

### Timing internal consistency

* 0 rows violate curl phase monotonicity
  (`namelookup ≤ connect ≤ appconnect ≤ pretransfer ≤ starttransfer ≤ total`)
  across all four raw files.
* 0 rows have `num_connects > 1` — the "one process per call, no connection
  reuse" claim is **checkable and checks out**, exactly as the harness says it
  would be.
* 0 warm rows have `wall_ms_including_process_spawn < time_total × 1000`.
* Process-spawn overhead is separable and small: mean 15.48 ms
  (sum 1,095,803.8 ms vs sum `time_total` 1,092,970.61 ms), which is why
  "including curl process spawn" and excluding it give the same 0.167 calls/sec.
* No call approached the recorded 90 s timeout (max `time_total` 65.296 s).
* `bytes` equals the **byte** length of `raw_response` on every MiMo row
  (0 mismatches). The apparent 2/4/6/8/10-character deltas against
  `len(str)` are multi-byte UTF-8 in the bodies — a positive authenticity
  signal, not an inconsistency.

### HTTP statuses and typed errors

Reproduced exactly, including the 9 `empty_content` rows: all 9 are HTTP 200
with `finish_reason: "length"`, `content: null`, `completion_tokens: 256` and a
1214–1254-character `reasoning_content` — i.e. the README's explanation
("reasoning consumed the whole 256-token budget") is confirmed from the raw
bodies, and all 9 are the single case `b-a03`. They consumed 3,186 tokens and
`$0.0007686` of real spend that the reported per-call cost excludes (§7 F-note
below).

### No fabricated rows — what I could and could not establish

Positive checks, all passing: `usage_flat` equals `usage` equals the values
inside `raw_response.usage` on every row (including
`completion_tokens_details.reasoning_tokens`); `raw_response.model` equals
`row.model_id` on all 200s; `derived_cost_usd` equals usage × rates on every row
of every file (0 disagreements); timestamps are non-decreasing in file order
within every phase; no duplicate
`(mechanism, phase, case, repeat, concurrency, block, probe)` key; the warm block
runs case-major in ascending case id with repeats 1..12 contiguous per case,
which is a strong structural signature of a real sequential run.

What this cannot establish: that any row corresponds to an actual HTTP
exchange. There is no server-side log, no signed receipt and no independent
witness. I record this as unverifiable, not as a pass.

### No credential values anywhere

I compared the **live values** of both credentials (read from
`$OPENCODE_GO_API_KEY` and `~/.local/share/opencode/auth.json#opencode-go.key`;
values never printed, never written to any artefact) against every byte of every
file under `followup-03-operational/` (12 files) and against 1,511,428 bytes of
`git log -p --all` for that path:

```
live secret values present in any followup-03 artefact: NONE
live secret values present in the followup-03 git history: NONE
secret values in __pycache__/*.pyc:                      NONE
```

Only the source **label** is recorded, as documented: `auth.json#opencode-go`
(279 rows), `env:OPENCODE_GO_API_KEY` (207 rows), `secrets_recorded: false` on
all 486. The three "suspicious pattern" hits are the source line
`cfg = 'header = "Authorization: Bearer %s"\n' % api_key` in `run_ops.py` — the
construction, not a value. The stdin-config mechanism is real: `curl --config -`
with the token piped, never in argv.

### Frozen-condition gate — reproducible

I rebuilt every request body from the **frozen** harness builders
(`harness/run_jev.build_request`, `harness/run_baselines.build_general_request`)
and compared hashes:

```
Jev ops request-hash mismatches vs frozen builder:            NONE (197/197)
Jev frozen-window gate: 64/64 request_body == and request_hash ==
MiMo grid rows: 232/232 hash == frozen builder with `model` swapped to
                'mimo-v2.6-flash' — the ONE permitted difference
MiMo frozen general gate: 64/64 identical with the frozen model id
```

The single MiMo hash mismatch in the whole file is the labelled
`phase: interface_probe` row, which adds `logprobs` by design and is outside
every grid statistic. `request_fields` on the Jev rows is exactly
`['model','questions','state']`; on the MiMo grid rows exactly
`['max_tokens','messages','model','temperature']`.

## 4. Independent recomputation — PASS, 0 numeric differences

`analyze_ops.py` was **not imported**. Percentile convention taken from the
report's own statement ("nearest-rank, no interpolation"), implemented as
`ceil(p/100 · n)`.

| statistic | committed | mine | |
|---|---|---|---|
| warm `time_total` n/mean/median/p90/p95/p99/min/max/sd/sum | 183 / 5972.517 / 4035.47 / 12473.074 / 15955.571 / 27609.554 / 1217.15 / 60607.853 / 6402.992 / 1092970.61 | identical | MATCH |
| warm time-to-first-byte (all 9 fields) | 198.491 median, sd 12.4932 | identical | MATCH |
| transport, service+transfer, setup-to-TLS, post-first-byte (all 9 fields each) | — | identical | MATCH |
| within-case spread, all 16 cases × 7 fields | min range 3629.657, max 59209.437 | identical | MATCH |
| sequential throughput | 0.1674 / 0.1670 calls-per-sec, sum 1092970.61 ms | identical | MATCH |
| concurrency C=1/4/8: makespan, sum, p50, mean, throughput, 429s, errors | 47718.8 / 70279.3 / 58915.4 ms | identical | MATCH |
| scaling ratios and p50 ratios | 0.6787 / 0.8099; 2.0593 / 1.7946 | identical | MATCH |
| stability: 16 per-case flip rates, mean 0.0208, max 0.3333, mean modal 0.9792, 15/16 stable | — | identical | MATCH |
| tokens: 6 classes, totals and per-call | 27953 / 6976 / 6286 / 34929 | identical | MATCH |
| cost from usage × rates | $0.0058667 total, $0.000026 per call | identical | MATCH |
| warm-only cost per correct control decision | 4.54793e-05 | identical | MATCH |
| correct decisions per dollar | 21988.0253 | 21988.045 (from unrounded) | rounding, see F-note |
| Pearson r (total vs output tokens) | 0.3935 | 0.3935 | MATCH |
| cross-window ratios (3) | 2.8108 / 0.9358 / 0.1454 | identical | MATCH |
| frozen Jev latency (9 fields) + token means | 586.8 median, 353.9219 / 29.4062 | identical | MATCH |
| Jev cap: 197 calls, 0 usable, 0 tokens, both segments | 125×403 then 72×429 | identical | MATCH |
| probe series: 10 rows, gaps, min gap 60.0 s | identical | MATCH | |
| idle-gap probe (6 fields + 2 ratios) | 3357.016 / 0.8319 / 0.42 | identical | MATCH |
| `probability_availability` | 0/0, 0/0, 0/0 | 0/0, 0/0, 0/0 | MATCH — and see **F3** |

`21988.0253` vs my `21988.045` is not a discrepancy: the committed value is
`round(1/round(0.00491176/108, 6), 4)`. The underlying
`4.54792593e-05` reproduces exactly.

**Determinism claim verified.** I copied `phase1/` to `/tmp` and ran
`python3 harness/analyze_ops.py --check` there (so the repository was never
touched):

```
determinism: OK (two in-process builds byte-identical)
summary.json    -> sha256 0236086c2823b575ba0d2bbdcf68e1fda7a062e380e2425beac9d2c9dd2cab07
comparison.md   -> sha256 e95fe967e4357c9cec5d155ccbe88d2f4849f8f58d8aee14c597068ede680c99
```

Both hashes equal the committed files' hashes. `comparison.md` is genuinely
machine-rendered, so the prose findings are the analyzer's output and cannot
drift from the raw data silently.

## 5. Live sanity re-sample — PASS

Conditions as documented: the same frozen request shapes (harness `run_one` →
`build_call_body`, verified against the frozen digests at load), sequential,
one attempt, zero retries, `curl`, one process per call, no connection reuse,
credential resolved at runtime and handed to curl on stdin. Run from the `/tmp`
copy; all rows written to `/tmp`; **no credential value printed or stored**.

Frozen gate at load: `cases.ndjson` match, `jev_raw.ndjson` match, Jev request
gate 64/64, general request gate 64/64, both credentials resolvable.

### MiMo V2.6 Flash — 6/6 reachable, labels identical, latency in-regime

| case | HTTP | label | `time_total` | `time_starttransfer` | tok in/out |
|---|---|---|---|---|---|
| a-dist1 | 200 | `no` | 6.430 s | 0.213 s | 160 / 23 |
| a-e01 | 200 | `yes` | 5.717 s | 0.226 s | 104 / 9 |
| a-e02 | 200 | `no` | 5.867 s | 0.195 s | 76 / 22 |
| a-h04 | 200 | `low` | 11.842 s | 0.191 s | 125 / 30 |
| a-m07 | 200 | `no` | 5.986 s | 0.217 s | 104 / 24 |
| a-miss1 | 200 | `no` | 3.175 s | 0.220 s | 100 / 87 |

* **Label stability: 6/6 identical to the committed modal labels** for these
  cases (all six are 12/12 stable in the committed warm block). 0 disagreements.
* **Latency order of magnitude: confirmed.** Range 3.18–11.84 s sits inside the
  committed warm distribution (min 1.22 s, median 4.04 s, p95 15.96 s,
  max 60.61 s) and well below the committed per-case maxima
  (a-miss1 18.4 s, a-h04 8.3 s, a-m07 13.7 s).
* **`time_starttransfer` 0.19–0.23 s on every call, including the 11.8 s one** —
  an independent confirmation of the report's sharpest MiMo-side methodological
  point (§1.1: first byte is not a model signal).
* **Label variance, stated explicitly:** with n=1 per case there is no flip rate
  in this re-sample; the stability statement above is a *concordance* check
  against the committed 12-rep modal labels, not a replication of the flip-rate
  estimate. 6 observations cannot resolve a 0.02 flip rate. The committed
  stability figures stand on their own 183 observations, which I recomputed.

### Jev 1.13 free — 6/6 refused, same named cause

| case | HTTP | typed_error | `time_total` | body |
|---|---|---|---|---|
| a-dist1, a-e01, a-e02, a-h04, a-m07, a-miss1 | **429** ×6 | `http_429` | 0.437–0.541 s | `{"type":"error","error":{"type":"FreeUsageLimitError","message":"Rate limit exceeded. Please try again later."}}` |

Identical on all six, 0 tokens, 0 usable answers. This is a **different window**
(2026-09-26 ≈14:2xZ) from both the study window and the probe series, so it
confirms the refusal is persistent and not a transient, and it independently
confirms the named error type. It does **not** reproduce the 403 phase — see
F1 for why that phase is not reproducible evidence of exhaustion.

## 6. Concurrency spot-check, C=4 — PASS

Same dispatch rule as `cmd_concurrency` (max C in flight, FIFO `pop(0)`, makespan
from `time.monotonic()` at first dispatch to last completion), the fixed 12-call
block, 1 attempt, 0 retries, `curl_argv_for` including `--config -`.

| | committed (13:54–13:56Z) | mine (≈14:3xZ) | reading |
|---|---|---|---|
| MiMo makespan | 70,279.3 ms | **63,731.1 ms** | same regime, 9% faster; committed max was 70,279 ms of a 47.7 s (C=1) / 58.9 s (C=8) envelope |
| MiMo statuses | 12× 200 | **12× 200** | ✔ |
| MiMo 429 / typed errors | 0 / 0 | **0 / 0** | ✔ |
| MiMo p50 / mean `time_total` | 5681.5 / 5848.3 ms | 2718.8 / 5303.1 ms | mine faster per call; within the 1.79–2.06× C=1 ratio band |
| MiMo throughput | 0.1707 calls/sec | 0.1883 calls/sec | consistent |
| MiMo block cost | — | $0.00028784 | ≈ $0.000024/call ✔ |
| Jev makespan | not run | 6,270.4 ms | **this is the trap, not a result** |
| Jev statuses | 197/197 refused | **12× 429, 0× 2xx, 12 typed errors** | ✔ |
| Jev throughput | — | 1.9138 calls/sec | *meaningless*: no inference occurred |

`makespan ≥ Σ time_total` holds for both blocks, and all 12 rows of a block
carry one identical `block_makespan_ms` — internally consistent.

Two observations worth recording. First, the Jev block "runs 11× faster than
C=1" and that number is **worthless**: 0 successes *and* 0 successes' worth of
work. This is exactly the failure mode the harness documents for its own
`--config -` bug (`2xx=0 http429=0 errors=12` reading as a speedup), reproduced
here from a *different* cause. Any future reader of a Jev concurrency number
must check the 2xx count first; the report never had to make that check because
it never ran the block, and says so. Second, my MiMo p50 is roughly half the
committed C=4 p50 while the makespan is only 9% lower (mine 0.907× the
committed makespan) — consistent with per-call variance on a route the report
itself shows has a 43× within-case spread, not with a change in behaviour. My
C=4 block's own tail reached 21.4 s, again inside the committed per-case maxima.

## 7. Classification audit — FAIL

Every claim in `comparison.md`, checked against the evidence.

### Claims whose label and evidence both hold

* §1.1 MiMo warm latency distribution, all 7 statistics, the 16-case within-case
  spread table, the repeat-to-repeat range 3,630–59,209 ms, Pearson r = 0.394 —
  **ESTABLISHED, correct.** This is the strongest part of the document.
* §1.1 "`time_starttransfer` is not a model signal" — **ESTABLISHED, correct**,
  and independently reconfirmed by my live re-sample (0.19–0.23 s first byte on
  a 3.2 s call and on an 11.8 s call). The supporting numbers (median 198.49 vs
  TLS 198.29; SD 12.49 vs 6402.99) reproduce exactly.
* §1.2 sequential throughput, the C=1/4/8 table, the scaling reading, and the
  "no client-side concurrency benefit" conclusion — **ESTABLISHED, correct**,
  with the right NOT-TESTED caveat. 0 errors and 0×429 at every level means the
  fall from 0.252 to 0.171 calls/sec cannot be a cap; that inference is sound.
* §1.2a idle-gap probe — numbers exact, and the refusal to claim a cold start
  ("not observed", not "small") is the right call, with an explicit
  WHAT-NOT-TESTED. (The stated gap length is wrong: F8.)
* §1.3 label stability, all 16 rows including the reasoning-token min–max —
  **ESTABLISHED, correct.**
* §1.6 the probe protocol (≤10, ≥60 s apart, 1 attempt, 0 retries, early stop)
  and the outcome (10 probes, 0 usable) — **ESTABLISHED, correct.** (Gap values
  misprinted: F10.)
* §2 UNRESOLVED list — every item genuinely unresolved, none filled by estimate,
  and `jev_current_window_stability` correctly records that the frozen window's
  1-call-per-case design makes a flip rate *uncomputable* (I verified: all 64
  frozen cases have exactly 1 row).
* §3.2 MiMo rates labelled a pricing/entitlement fact and never used for a
  structural claim — **correct, and I checked**: no latency, throughput, token or
  stability statement in §1 or §2 uses a price. The only price inside the
  ESTABLISHED section is §1.7's `$0.00 (free tier)`, correctly caveated.
* §3.3 matched-error — **correct**: Jev's error level is unmeasurable (0 of 197
  returned an answer), so no matched-error ratio is reported and none should be
  inferred.
* §3.5 network overhead refused attribution to either model — **correct**, and
  the guard is well placed.
* Cost maths as printed: $0.000026 per call over 222 calls, $0.000045 per correct
  control decision over 108 correct decisions **in the warm block**, 21,988.0
  correct decisions per dollar, MiMo control error rate 0.0000 over 108 — all
  **correct and internally consistent**, each with its denominator stated.
* **Undefined-Jev-per-dollar handling — correct and well done.** `$0.00` per call,
  `$0.00` per correct decision, and per-dollar **UNDEFINED** with the explicit
  reasoning "not 'infinite' and not 'best': the ratio has no value because its
  denominator is zero", plus the conditional form of the statement. This is the
  handling the brief asked for and it is right.
* **Accuracy as a control, not the outcome — correct.** Accuracy appears only as
  (a) a normalisation term (`correct control decisions/sec`), (b) a stability
  reference (control error rate 0.0000), and (c) a stated scope exclusion
  ("does not re-derive the semantic benchmark"). The outcome is operational. No
  accuracy number is offered as a result.

### Claims that fail

**F1 — MATERIAL. "Exhausting inside 197 calls" is not supported by the evidence
and is labelled ESTABLISHED in three places.**

The first call of the Jev window was already refused:

```
row 1   warmup rep 1  a-h04  HTTP 403  http_4xx  2026-09-26T06:34:53Z
row 2   warmup rep 2  d-01   HTTP 403  http_4xx  2026-09-26T06:34:54Z
...
row 197 warm  rep 12  <case> HTTP 429  http_429  2026-09-26T06:36:35Z
any 200 anywhere in the file: False
file order == timestamp order: True
```

Every one of the 197 calls was a refusal, starting with the first. The window
therefore contains **no observed transition from available to exhausted**: it
cannot show the study's load consuming an allowance, because no call in it ever
succeeded. What the window does show is (i) the free tier refused everything
from the first call, and (ii) the *error surface* changed at call 125 from
`server_error`/parse-error to the named `FreeUsageLimitError`.

Affected text, all under ESTABLISHED or the headline:

* headline table: `| Availability under load | sustained | **exhausted inside
  197 calls** |`
* §3.1: "while quota exists Jev costs $0 per call, and **this study measured
  quota exhausting inside 197 calls**"
* §7: "it is unavailable under sustained sequential load, **exhausting inside
  197 calls in ~100 seconds**, and it **masks that exhaustion** behind 125
  consecutive 403s before it will name it"
* README headline: "it masks that exhaustion behind 125 consecutive 403s"

The availability *failure* is established and I confirm it live (§5: 6/6 still
429 `FreeUsageLimitError`, hours later). The exhaustion-as-caused-by-this-load
is not, and F1 makes §2's already-honest admission sharper: since the window
never observed an available state, it cannot distinguish a daily quota from a
per-minute leaky bucket by *any* amount of evidence.

**F2 — MATERIAL. "The 403 phase masks the cap" is an inference labelled
ESTABLISHED.**

The 403 body, identical on all 125 rows:

```json
{"error":{"code":"server_error","type":"server_error",
          "message":"Upstream response was not valid JSON"}}
```

It names no cap, no quota, no tier, no limit. §1.5 states "The 403 phase **masks
the cap** behind an upstream parse error" and §3.4 states "The 403 phase is a
serving policy (**error masking**)" — both as established fact, both in the
ESTABLISHED / ARTEFACT sections. The report itself supplies the counter-evidence
in the same paragraph ("The 429 body names the cause; the 403 body does not") and
then does not act on it.

The masking reading is *plausible* — a gateway surfacing a non-JSON upstream
error immediately before a named free-tier limit is exactly what masking looks
like — but it is not established, and no test in this study discriminates it
from (a) an unrelated upstream outage that later resolved into a rate-limit
response, or (b) a gateway-side parse failure with an independent cause. The
honest classification is inference-favoured, listed as such.

**F3 — MATERIAL. `frozen_window.probability_availability` is a never-computed
`0/0`, and §1.7 prints it as a measurement.**

`summary.json` reports `{"noul_scalar": 0, "noul_total": 0,
"choice_distribution": 0, "choice_total": 0, "score_distribution": 0,
"score_total": 0}`, and §1.7 renders it: "probability availability: noul scalar
exposed on 0/0 noul calls; choice distribution on 0/0; score distribution on
0/0". §1.7 therefore contradicts §4 and §7 of the same document, which assert
Jev's distributions are available.

Root cause, `harness/analyze_ops.py:849`:

```python
qtype = (r.get("prediction") or {}).get("type")
```

The frozen rows carry the question type at `parsed.type`; their `prediction`
dict has keys `label, probabilities, score, max_prob, confidence_reported,
confidence_formula, normalised, prob_sum` and **no `type` key** (I verified on
all 64). So `qtype` is always `None` and no counter can ever increment. The
statistic is not wrong, it is absent.

The true figures, from my own scan of the frozen `raw_response` bodies:

| question type | n | Jev API answer | what it carries |
|---|---|---|---|
| noul | 50 | `"noul": <scalar>` | scalar `P(no)`, no distribution |
| choice | 12 | `"probabilities": {…6 option keys…}` + `confidence` | full distribution |
| score | 2 | `"probabilities": {"0":…,"1":…,"2":…}` + `legend` + `confidence` | distribution + legend |

i.e. **scalar noul on 50/50, distribution on 14/14, legend on 2/2** — which
confirms §4/§7's prose is *true*, and simultaneously shows that the statistic
which exists to support it was never computed.

**F4 — MATERIAL. `interface_probe.mimo.probabilities_exposed_under_frozen_conditions
= 234` counts the harness's own synthesis, and asserts the opposite of §4/§7.**

Verified from the raw rows:

```
usable mimo rows:                                    234
rows whose raw_response contains 'logprobs':           0
rows whose raw_response JSON has a 'logprobs' key:     0
rows with non-degenerate parsed_probabilities:         0
distinct value-sets in parsed_probabilities:        {(0.0, 1.0): 234}
```

`parsed_probabilities` on every usable MiMo row is a degenerate {0.0, 1.0} map
**manufactured by the harness** from the one-word answer (`"no"` →
`{"yes":0.0,"no":1.0}`). The API returned no probabilities, no logprobs, and no
per-token data on any of the 234 calls. The field name asserts that 234 calls
"exposed probabilities"; comparison.md §4/§7 asserts MiMo "exposes none". Both
cannot be right, and the summary is the one that is wrong. A reader of
`summary.json` alone — which is the artefact the report claims to be rendered
from — would conclude the interface advantage runs the *other* way.

The probe row itself is the sound evidence and it is recorded correctly:
`request_fields` includes `logprobs`, `http_status` 200, the response has keys
`[choices, created, id, model, object, usage]` and the message has
`[content, reasoning_content, role, tool_calls]` — no logprobs. §4's reasoning
("the frozen request shape does not request logprobs … the labelled interface
probe is what tests the latter") is exactly right.

Net effect on the classification audit: the ESTABLISHED interface claim is
**true but unsupported by any statistic in the deterministic summary** — F3
breaks the Jev-side statistic, F4 corrupts the MiMo-side one. It survives only
on manual reading of `raw_response`, which is not reproducible evidence in the
manner the document claims for everything else.

**F5 — MODERATE. The transport-vs-service separation double-counts DNS and TCP,
so the identity the report presents as exact is not exact.**

`curl`'s `-w` phase counters are **cumulative from the start of the transfer**,
not per-phase increments. Proved locally against a TLS server on
`127.0.0.1` (no external network, no credentials):

```
namelookup=0.000056 connect=0.000211 appconnect=0.005368
pretransfer=0.005419 starttransfer=0.006286 total=0.006385
SUM of the five earlier counters = 0.017340   (2.7x time_total)
appconnect already contains namelookup+connect: True
```

The study's own rows show the same signature: `appconnect` mean 201.64 ms versus
`namelookup+connect` mean 3.40 ms.

`analyze_ops.py` defines `transport = namelookup + connect + appconnect` and
labels it "DNS, TCP, TLS". It therefore double-counts DNS and TCP by 3.398 ms
on the mean. Consequences, all reproduced:

```
setup_before_first_byte mean      205.0413   (should be 201.6431 = appconnect alone)
post_first_byte_body_wait mean   5770.6702
setup + post                   = 5975.7115
time_total                    = 5972.517      -> the stated identity is off by +3.194 ms
shares 3.4331% + 96.6204%     = 100.0535%     -> the §1.1a table prints "100%" on the total row
```

The overshoot decomposes exactly: `mean(namelookup+connect) −
mean(starttransfer − appconnect) = 3.3982 − 0.2037 = 3.1945 ms`. The exact
identity is `total = appconnect + (starttransfer − appconnect) + (total −
starttransfer)`; the report's components omit the middle term and double-count
the first.

Correct figures if fixed: transport (DNS+TCP+TLS) mean **201.643 ms**, share
**3.3760%** of the mean total (not 3.4331%); the "brief's two components"
sum 404.77 ms becomes 401.37 ms. Magnitude: 0.057% of a call. **No conclusion
in the document changes** — the qualitative reading ("a large fraction of a MiMo
call is network setup, not model work" → actually the *opposite*: only 3.4% is
setup and 96.6% is post-first-byte body wait) is unaffected, and §1.1a already
makes that point correctly. The fault is that a table headed "share of total"
and a summary field headed `"identity"` both assert exactness they do not have.

Note the analyzer *also* computes the correct quantity, `setup_to_tls_complete_ms`
(mean 201.6431, median 198.29) — and uses it for the TLS-completion comparison in
§1.1, but not for the decomposition table. The connect-only probe supports the
transport separation in substance (see F16a).

**F6 — MODERATE. `derived_cost_usd_per_correct_control_decision` is wrong under
any consistent basis. Not used in `comparison.md`.**

```
committed                                    5.46296e-05
= 0.0059 (total cost PRE-ROUNDED to 4 dp) / 108 (warm-block-only correct count)
consistent, warm-only:  0.00491176 / 108  =  4.54793e-05   <- this is what the report prints
consistent, warm+idle+concurrency: 0.00586670 / 134  =  4.37813e-05
```

Two independent errors in one figure: the numerator was rounded to 4 dp before
dividing (the same `r4` class of defect the commit `e598a942` claims to have
fixed for the per-call figure, left unfixed one line away), and the numerator
covers 222 calls while the denominator counts only the warm block's 108 correct
decisions — the idle and concurrency rows contributed 26 further correct
control decisions (2 idle + 24 concurrency; `b-a03` and `a-dist1`/`a-miss1` are
excluded as non-control or unanswerable), and they are omitted from the
denominator. The report's own $0.000045 figure is correct and unaffected; the
error is latent in `summary.json`.

**F7 — MODERATE. The warm-up-inclusion note is vacuous and its stated
consequence is false, in the report as well as the summary.**

`tokens_and_cost.selection` is
`block='resume1' AND phase IN ['warm','warmup','idle','concurrency'] AND no
typed_error`, and `warmup_included_in_cost_total: true`. But the warm grid was
run with `--skip-warmup` (README step 3), so all 5 MiMo warm-up rows live in the
aborted `block=null` block:

```
warmup rows by block: {None: 5}     -> the 222-row cost selection contains
                                         ZERO warm-up rows
```

So "which **INCLUDES** warm-up calls when `warmup_included_in_cost_total` is
true" (printed verbatim in comparison.md §1.4) describes nothing, and
`per_correct_denominator`'s "the total includes warm-up calls, so this is a
slight UNDER-estimate" is the wrong reason for the two per-correct figures
differing — the real difference is the idle + concurrency rows. The README
repeats it: "the 222 usable grid calls the cost section aggregates
(warm + warm-up + idle + concurrency)".

**F8 — MODERATE. §1.2a misstates the measured gap, and its caveat is inverted
as a result.**

§1.2a: "The client made NO call for **120s**, then issued 3 calls", and
WHAT-NOT-TESTED: "a single **120s** gap rather than **minutes or hours**".

The realised gap, from the rows:

```
last warm call    2026-09-26T13:32:54Z
first idle call   2026-09-26T13:51:31Z
=> 1117 s = 18.6 minutes
```

120 s is the harness's sleep parameter, recorded as
`idle_seconds_before_first_call: [120]`; the observed idle interval was ~9×
longer. So the gap was minutes, and the caveat's own wording ("rather than
minutes or hours") is contradicted by the data it is attached to. The
substantive conclusion ("no cold-start penalty observed", "not observed" not
"small") is unaffected and remains correct, and is if anything *better* founded
than the report claims.

**F9 — MINOR. §1.1 asserts a mechanism that §2 says is unobservable.**

§1.1: "the endpoint's serving time for a fixed small request is dominated by
variable **queueing** that the client cannot see or control"; §1.2: "it is added
**queueing** cost at the service". §2: "`server_side_queueing_or_batch_effects`
— **NOT OBSERVABLE** from the client". The evidence supports "dominated by
variable, uncontrolled **serving-side** delay"; it does not identify queueing as
the mechanism, and the document says so itself nine lines later. The ESTABLISHED
section should not name a mechanism the UNRESOLVED section rules out.

**F10 — MINOR. §1.6's probe table misstates three recorded gap values.**

Recorded `seconds_since_previous_attempt`:
`60.0, 85.0, 60.0, 60.0, 61.0, 60.0, 61.0, 61.0, 60.0`.
Printed in §1.6: `60.0, 85.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0, 60.0`.
Three recorded `61.0` values are displayed as `60.0` — rounded *down onto the
floor* in the one table whose subject is pacing discipline. The floor claim
itself survives (61 ≥ 60).

**F11 — MINOR. Wrong stated resolution in a cross-window denominator.**

`summary.json.ratios.structural.denominators.jev`: "n=64 frozen calls, median
over **1-second-rounded** `latency_ms`". The frozen values are all multiples of
**0.1 s** (586.8, 525.3, 763.5, …) — 0.1-second resolution, not 1-second. The
median itself (586.8) is unaffected; the stated basis is wrong.

**F12 — MINOR. "Reproduces `subset.json` byte for byte" is false.**

README §1. Re-running `run_ops.py subset` in an isolated copy:

```
only difference:  "frozen_at_utc": "2026-09-26T06:34:18Z"  ->  "2026-09-26T14:25:43Z"
every other field identical (id list, selection order, 16-step trace, coverage,
F1 derivation, gate digests, design constants, planned calls, rationale)
```

The file embeds a wall-clock stamp, so a re-run always differs in that field.
The substantive guarantee — the harness hard-stops on selection drift — is
real and I exercised it; the "byte for byte" phrasing is what is wrong, and it
is wrong in a way that would make a careful auditor's `cmp` look like drift.

**F13 — MINOR. The probe file is not byte-reproducible with the committed
harness.**

`results/jev_ratelimit_probes.ndjson` was written by commit `0f2a97ad`;
`jev_ratelimit_probe.py` was changed afterwards by `e598a942`, which added an
`error_type` field. The committed rows therefore have no `error_type` key, and a
re-run with the current harness would add one. The analyzer notices and
compensates (it derives the type from `raw_response_excerpt` and stamps
`error_type_derived: true`), so the reported
`{'FreeUsageLimitError': 10}` is correct — I confirmed the type is on all 10
bodies. The gap is between the committed evidence and the committed code.

**F14 — MINOR. Three traceability gaps in the raw rows.**

* Probe rows carry **no `request_hash`**, so the probe request bodies cannot be
  verified against the frozen Jev request from the artefact. They *are* the
  frozen body by construction (the probe reuses `run_one` → `build_call_body`),
  but the grid rows carry the hash and the probe rows do not, so the frozen
  condition is asserted for probes and evidenced for grid calls.
* Probe rows carry `question_type: null` — the same broken join as F3.
* The 9 `empty_content` warm rows carry **no `excluded_from_statistics` flag**
  and no note (the 5 warm-up rows carry `excluded_from_statistics: true`). A
  reader scanning `mimo_ops_raw.ndjson` cannot see that they were dropped, and
  they consumed 3,186 tokens / $0.000769 of real spend excluded from the
  reported per-call cost. The README explains it; `comparison.md` does not.

**F15 — MINOR (omission). Free-tier serving priority is an undeclared confound
on the one ratio that favours Jev.**

`summary.json` records `tier_state: "free tier, inside quota at that time"` for
the frozen Jev window, and the cross-window caveat covers window, transport and
tier state. Nowhere does the document note that a free tier's serving priority
is an unmeasured property that could account for a large part of Jev's
advantage. That matters most for `warm_median_latency_ratio_jev_over_mimo =
0.1454` — Jev appearing ~6.9× faster than MiMo — which is the only headline
number in the document that favours Jev, and which is already cross-window and
cross-transport. The frozen Jev latency (median 586.8 ms, max 763.5 ms) has a
stdev of 48.29 ms, i.e. it is *too tight to be a contended route*, which is at
least consistent with a low-priority-but-uncontended free tier; that is an
observation, not a measurement, and the document does not make it.

**F16 — MINOR. Two available cross-checks not performed, one presentational
gap.**

* (a) The connect-only probe and the in-grid rows measure the same quantity
  twice and the report never compares them: probe `time_appconnect` median for
  MiMo is **220.0 ms** (n=3) against the in-grid `setup_to_tls_complete` median
  of **198.29 ms** (n=183) — a 10.9% difference, plausibly within 3-sample noise
  but unremarked. This is the cheapest available check on the transport
  separation and it was available for free.
* (b) §1.2 reports "sequential: 0.167 calls/sec" and the concurrency table
  reports "C=1 → 0.252 calls/sec", a 1.5× gap between two nominally
  one-call-at-a-time conditions, with no explanation. It is case mix, not
  concurrency: the C=1 block covers 6 cases whose warm medians average
  4,482 ms, against 5,009 ms across all 16. The scaling ratios are computed
  within the block and are unaffected, but a reader comparing the two figures
  has no way to know that.

**F17 — MINOR. The transport probe's own description of what it did is wrong.**

`results/transport_probe.json`: "the request is abandoned **without an HTTP
request line**". The code path is `curl --head` (`run_ops.py:747`), i.e. a HEAD
request line **is** sent, and the server answers `404` on all 6 rows (bytes 0).
The substantive claim holds — a HEAD carries no body, so no model input and no
inference, and the 404 confirms nothing was served — and the report uses only
`time_appconnect`, which is the correct counter for a handshake measurement. But
the probe's `time_total_s` (0.35–0.39 s) therefore includes a server round trip
and is not a pure handshake total, which matters if anyone reads that field.

## 8. Measurement limitations

Correctly disclosed by the report: per-call cold start not directly observable
(shared endpoint, unobserved server state); server-side queueing/batching not
observable; sustained multi-hour throughput not measured for either mechanism;
price elasticity / paid Jev tier out of scope; p99 thin on every small sample
(the analyzer stamps `p99_is_thin`); the Jev side unrepeatable because the paced
block's precondition never held.

Additional limitations the report does **not** state, which a consumer of these
numbers needs:

1. **No connection reuse on any call, by design** — verified, `num_connects == 1`
   on all 486 rows + 6 probes. Every call therefore pays a full
   DNS+TCP+TLS handshake (~202 ms = 3.4% of a MiMo call). This is a
   *client-design* cost, not a property of the route, and it inflates both
   mechanisms; it also means the cross-window Jev/MiMo latency ratio (0.145) is
   a ratio of two differently-transported, differently-reusing clients. A
   keep-alive client would see materially lower latency for both.
2. **Single client host, single path, single CDN edge, one vantage point.** The
   43× within-case spread on `b-a02` (1,398–60,608 ms for the same request) is
   attributed to serving-side variation, which is the right reading, but no
   second vantage point exists to separate path effects from service effects.
3. **`p99` is thin everywhere and equals the max by construction** at n=12
   (concurrency), n=3 (idle, transport probe), and n=64 (frozen Jev, where
   p99 = max = 763.5). Only the n=183 warm block has a meaningful p99, and even
   there the 99th percentile rests on 2 observations.
4. **Block makespan is a single unreplicated measurement** per concurrency level
   (one `time.monotonic()` interval), and the C=1/4/8 comparison across three
   levels run minutes apart carries unquantified between-block drift. The
   ratio-based reading ("throughput falls at C=4") rests on one block per level.
5. **Cost figures are token-rate arithmetic over self-reported `usage`.** No
   billing record was checked. `cache_read_tokens` is 0 on every row, so the
   $0.0028/Mtok cache-read rate is present in the model but never exercised —
   and the probe row's response shows `cached_tokens: 64` while the row records
   `cache_read_tokens: 0`, so cache accounting is at least partly unverified.
6. **`b-a03` has n=3 usable reps**, so the only non-zero flip rate in the study
   (0.3333) rests on 3 observations, and that case is also the one that produced
   all 9 `empty_content` failures. The "15 of 16 cases stable on every rep"
   figure is sound; the 0.0208 mean flip rate is dominated by this one thin case.
7. **The Jev 403/429 window is a one-shot artefact** that cannot be reproduced
   by design — the measurement cannot be re-run at all without quota, so no
   independent party can regenerate it. My live re-sample confirms the refusal
   persists (12/12 → 429) but cannot reproduce the 403 phase, and per F1 the
   403 phase is not evidence of exhaustion in the first place.
8. **Timing resolution is heterogeneous**: frozen Jev latency at 0.1 s, all
   `timestamp_utc` at 1 s (the sequential-throughput figure is therefore reported
   as an upper bound with a stated ±1 s coarseness — correctly done), curl phase
   counters at µs.

## 9. Unverifiable claims — explicit list

These cannot be verified from the artefacts, by me or by anyone else, with the
data this study retained. Each is stated so a consumer knows where the evidence
stops.

1. **That the 403 phase was caused by the free-tier cap** (F1, F2). No test
   discriminates cap-masking from an unrelated upstream or gateway failure. The
   claim is inference-favoured and labelled ESTABLISHED.
2. **That the study's 197 calls consumed an allowance** (F1). The window's first
   call was already refused, so no exhaustion event is observable in it.
3. **Whether the cap is a daily quota, a per-minute leaky bucket, or an
   entitlement that was never granted in this account** (F2). §2 concedes this;
   F1 deepens it, because the window never observed an available state.
4. **Jev's current-window latency, throughput, concurrency scaling, stability,
   and curl phase decomposition.** 0 usable calls. Unverifiable without quota.
5. **Whether the frozen Jev window's latency is a property of the model or of
   free-tier serving priority** (F15). No paid-tier Jev call exists.
6. **Whether MiMo's serving delay is queueing, batching or contention** (F9).
   The report asserts queueing in §1.1 and disclaims it in §2.
7. **Per-call cold start, for either mechanism.** Shared endpoint, unobserved
   server-side cache and connection state, fresh client connection per call.
8. **Sustained multi-hour behaviour, for either mechanism.** Every figure is a
   burst-window measurement (the MiMo warm block spans 23 min).
9. **That any raw row corresponds to an actual HTTP exchange.** I verified
   internal consistency exhaustively (§3) but there is no server-side log,
   signed receipt or independent witness. Absence of detectable fabrication is
   not proof of absence.
10. **The promotional rates themselves, and hence the absolute dollar figures.**
    `21988.0` correct decisions per dollar is derived from catalog rates current
    at 2026-09-26 (input $0.14/Mtok, output $0.28/Mtok, cache read
    $0.0028/Mtok). No invoice or billing record was checked, and the rates are
    promotional and tier-dependent by the report's own statement. The *ratios*
    and token counts are unaffected; the dollar values are not reproducible
    outside that rate card.
11. **Whether the 10 availability probes were the only Jev-directed traffic.**
    Any other account or client using the same credential in the same window
    would be invisible here.
12. **Cross-transport equivalence for Jev.** `run_ops.py verify` — the mode
    designed to validate curl-vs-urllib equivalence for Jev — was not run, and
    the README says so explicitly. Correct disclosure; recorded here as a known
    gap in the evidence chain behind §1.7.

## 10. What I would change, in priority order

Not applied — this verification does not fix anything. Offered so the builder
can decide.

1. Re-label the exhaustion claim. "Exhausting inside 197 calls" → "refused on
   all 197 calls, the first of which was already refused; the entitlement state
   at the start of the window is unknown." Fix the headline table, §3.1, §7 and
   the README. (F1)
2. Re-label the masking claim as inference, or run the test that would settle
   it. (F2)
3. Fix `probability_availability` to read `parsed.type`, and rename
   `probabilities_exposed_under_frozen_conditions` to something that does not
   claim an interface capability — or count `logprobs`/`probabilities` in the
   raw response instead of the harness's derived field. Then re-render. (F3, F4)
   Note that fixing F3 will change a printed line in §1.7 from `0/0` to
   `50/50`, `14/14`, `2/2` — which *supports* §4/§7 and should be welcome.
4. Define transport as `time_appconnect`, restore the exact identity, and
   recompute the §1.1/§1.1a tables. (F5)
5. Fix `derived_cost_usd_per_correct_control_decision` to a consistent
   numerator/denominator basis and stop rounding the numerator before dividing.
   (F6)
6. Correct the warm-up-inclusion note, the realised idle gap, the probe gap
   values, the frozen-latency resolution, the "byte for byte" claim, and the
   transport-probe description. (F7, F8, F10, F11, F12, F17)
7. Add the free-tier-priority confound to the cross-window caveat. (F15)
8. Consider one cheap cross-check that was available and not taken: the
   connect-only probe against the in-grid handshake time. (F16a)

---

## Verification method

Everything below is reproducible from this repository plus the scripts in
`/tmp/opencode/jev-phase1-followup3-verify/`:

| script | what it does |
|---|---|
| `repro_subset.py` | independent re-implementation of `STRAT-OPS-v1` and of the F1 derivation, from the rule text only |
| `gate_check.py` | rebuilds all 197 Jev + 232 MiMo request bodies with the frozen builders and compares hashes |
| `recompute.py` | all of §4 — every statistic recomputed from raw NDJSON, `analyze_ops.py` never imported |
| `integrity.py` | anti-fabrication and internal-consistency checks across all four raw files |
| `extra.py`, `extra2.py` | per-case spread table, idle ratios, `empty_content` bodies, correctness denominators, interface denominators |
| `curl_semantics.py` | local TLS server test proving curl's `-w` counters are cumulative (F5) |
| `live_resample.py` | check 5 and check 6, run against the `/tmp` copy of `phase1/` |
| `secret_scan.py` | live credential values vs every artefact byte, the git history, and the `.pyc` files |

Independent of the builder: no `analyze_ops.py` import, no reuse of the
harness's own arithmetic, no builder context. Where I used harness code at all
it was to *issue* calls through the documented path (`run_one`,
`curl_argv_for`) and to *rebuild frozen request bodies* from the frozen
`harness/` — never to compute a statistic. Percentile convention was taken from
the report's own documented statement and re-derived independently.

**Verdict: FAIL on check 7 (classification audit); PASS on checks 1–6 and 8,
with 14 minor faults recorded against the passing checks.** The measured
content of followup-03 is trustworthy and exactly reproducible; the layer that
decides what those measurements *mean* carries three material defects, one of
which (F1) asserts an exhaustion event the evidence does not contain.
