---
title: followup-04-jev-direct — Independent Verification
program: EDASES
layer: Research
document_type: Verification
status: Complete
authority: Independent check
canonical_repository: edases
study: followup-04 — Jev over the direct TypeSafe API vs frozen MiMo (issue #565)
verifies: research/jev-bounded-judgment/phase1/followup-04-jev-direct/
verifier_role: independent verifier (fresh session, no builder context)
date: 2026-09-26
---

# followup-04 — Independent Verification

**What this document is.** A fresh-session, read-only audit of the followup-04
deliverables against the frozen inputs and the raw NDJSON. The builder's
analysis code was **not imported**: every figure was recomputed from
`jev_direct_raw.ndjson` and `mimo_ops_raw.ndjson` with plain Python, and the
builder's `summary.json` / `equivalence.json` were read as *data to be
compared against*, never as the source of a number.

**Verdict: PASS WITH FINDINGS.** The measurement substance is sound. Every
latency, throughput, concurrency, stability, reliability, usage and cost figure
reproduces to the last printed digit, the frozen inputs are untouched, the
credential discipline holds under an adversarial scan, and the 16-case
semantic-equivalence check reproduces exactly. Fifteen findings are recorded
below: **two material** (both in the probability-availability classification,
one of which is an overreach against the document's own UNRESOLVED list), and
thirteen minor (labelling, an undocumented estimator, one internal
contradiction, one mixed-denominator table row, and a traceability gap in how
the MiMo column was produced). No finding overturns a conclusion; two narrow
what the evidence supports.

**Working state at verification time:** branch `research/jev-phase1-565`,
HEAD `311ae5dc`. The only repository mutation made by this verification is
this file.

---

## 0. Verdict table

| # | Check | Verdict | Headline evidence |
|---|---|---|---|
| 1 | Frozen-input integrity | **PASS** | `git diff 70ef037e..HEAD` touches only 6 followup-04 files; frozen phase1 root + followup-01/02/03 diff is empty; 4/4 digests recomputed and match |
| 2 | Route / model / credential handling | **PASS** | 0 hits for the key value in 9,696 working-tree files, 3,684,693 git-diff lines, 130,767 `/tmp/opencode` files; 276,241 live `/proc/*/cmdline` reads, 0 leaks; `jev-1.13.0` on 238/238 + 9/9 live |
| 3 | Request equivalence | **PASS** | 16/16 bodies equal after `model` normalisation; the only differing bytes are `"jev-1.13-free"` → `"jev-1.13.0"`; all 32 hashes recomputed and matched |
| 4 | Independent recomputation | **PASS with 5 findings** | 100+ statistics reproduced to 0 delta; findings D1–D5 below |
| 5 | Semantic-equivalence reproduction | **PASS** | 16/16 labels, 0 answer changes, 0 label-unstable, noul drift 0.04 / 0.01, choice-score delta 0.01 / 0.00 — all exact |
| 6 | Live sanity re-sample | **PASS** | 6 calls, 6/6 HTTP 200, 6/6 `jev-1.13.0`, 314–345 ms, **0 label flips**; 3 model-tag probes reproduce the documented alias/rejection behaviour |
| 7 | Concurrency spot-check at C=4 | **PASS** (flatness confirmed; per-level ratio is noise) | measured peak in-flight **4** at C=4; my scaling 0.9745x vs committed 1.0425x — both ≈1.0 |
| 8 | Classification audit | **MIXED** | 7 of 7 audit targets pass except the probability-availability claim (**2 material gaps**, G1/G2) and 4 minor wording/labelling gaps |
| 9 | Limitations + unverifiable claims | recorded | 10 limitations, 10 explicitly unverifiable claims |

**Counts.** 238 Jev-direct rows (1 route probe + 5 warm-up + 192 warm + 3 idle +
36 concurrency + 1 interface probe), 232 MiMo `resume1` rows, 16 cases, 9 live
calls by this verifier.

---

## 1. Frozen-input integrity — PASS

```
$ git log --oneline --name-status 70ef037e..HEAD -- research/jev-bounded-judgment/
311ae5dc  M  .../followup-04-jev-direct/results/equivalence.json
          M  .../followup-04-jev-direct/results/summary.json
4896cb10  A  .../followup-04-jev-direct/README.md
          A  .../followup-04-jev-direct/comparison.md
          M  .../followup-04-jev-direct/harness/run_ops_jev_direct.py
          M  .../followup-04-jev-direct/results/summary.json
364ccb3d  M  .../followup-04-jev-direct/harness/run_ops_jev_direct.py
          A  .../followup-04-jev-direct/results/equivalence.json
          M  .../followup-04-jev-direct/results/jev_direct_raw.ndjson
          A  .../followup-04-jev-direct/results/summary.json
0c2afc3a  A  .../followup-04-jev-direct/results/jev_direct_raw.ndjson
5da5872e  A  .../followup-04-jev-direct/harness/run_ops_jev_direct.py
```

Exactly 6 files, all under `followup-04-jev-direct/`. Nothing else in the
repository changed across the five followup-04 commits.

```
$ git diff 70ef037e HEAD -- <phase1 root files> <followup-01> <followup-02> <followup-03>
(empty)
$ git status --porcelain -- research/jev-bounded-judgment/
(empty)
$ git ls-files --others --exclude-standard -- research/jev-bounded-judgment/
(empty)
```

Digests recomputed with plain `sha256sum` (not via the harness):

| file | recomputed | matches declared |
|---|---|---|
| `phase1/cases.ndjson` | `7dd4698f4614eee9…f558c` | yes |
| `phase1/results/jev_raw.ndjson` | `e17ae014f0fc6cc3…82d3bc` | yes |
| `phase1/followup-03-operational/subset.json` | `58b855acefbd7cda2…1b8d3` | yes |
| `phase1/followup-03-operational/results/mimo_ops_raw.ndjson` | `40dbc56329dd2d51…5827cd8` | yes |

The harness's own gate also re-runs clean and touches nothing:

```
$ python3 harness/run_ops_jev_direct.py gate
FROZEN-CONDITION GATE: all conditions verified
  cases.ndjson 7dd4698f4614eee9... MATCH        (and 3 more, all MATCH)
  request gate: 16/16 bodies equal to frozen after model normalisation (jev-1.13-free -> jev-1.13.0)
  normaliser gate: reproduces frozen parse_jev on 64/64 frozen rows
  subset: 16 cases, rule STRAT-OPS-v1, re-derived == stored
  F1 correction: pair cp4 ['c-p4a', 'c-p4b'] (no subset member: True)
  credential: secrets/typesafe.env#TYPESAFE_API_KEY resolvable=True (value never printed)
  endpoint: POST https://api.typesafe.ai/v1/systemone   model pinned: jev-1.13.0
  planned calls: 238
```

The F1 pair `cp4` genuinely exists in `cases.ndjson` (`c-p4a`, `c-p4b` present,
`control.pair_id == "cp4"`), so the gate's claim is checkable, not asserted.

**Note (not a fault).** A `__pycache__/run_ops_jev_direct.cpython-310.pyc`
build artefact sits untracked in the harness directory. It is covered by
`.gitignore:38` (`__pycache__/`), so it cannot be committed, and it was
included in the credential scan below (clean).

---

## 2. Route, model and credential handling — PASS

### 2.1 Adversarial credential scan

The value was read from `~/.secrets/typesafe.env` into a variable, never
printed; only its length (108), a shape mask
(`XXXXXX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXX…`) and a
`sha256` prefix (`13a64715db52`) are reported here. Scans searched the **full
value**, the **first 20 characters** and the **last 20 characters**.

| surface | files / lines scanned | hits (full) | hits (first 20) | hits (last 20) |
|---|---|---|---|---|
| repository working tree (excl. `.git`) | 9,696 files | 0 | 0 | 0 |
| `git log --all -p` (every ref, every blob) | 3,684,693 diff lines | 0 | 0 | 0 |
| `/tmp/opencode` (incl. all builder logs) | 130,767 files | 0 | 0 | 0 |
| live `/proc/*/cmdline` during 6 real calls | 276,241 reads | **0** | **0** | **0** |

The argv probe ran concurrently with six live calls and read the command line of
**every** process on the host, not just the curl children:

```json
"argv_leak_probe": { "n_cmdline_reads": 276241, "leaks": [],
                     "needles_searched": ["full value","first 20 chars","last 20 chars"] }
```

The builder's own run logs are clean too. `fu4-warm.log`, `fu4-idle.log` and
`fu4-conc-probe.log` contain only progress lines and the interface-probe raw
response — no credential material, no argv echo.

### 2.2 Channel

* Read at runtime from `~/.secrets/typesafe.env` (`resolve_credential()`,
  harness line 255), parsed with `^\s*(?:export\s+)?TYPESAFE_API_KEY\s*=\s*(.*)$`.
* Not inherited: `env | grep -c TYPESAFE` → `0`; `"TYPESAFE_API_KEY" in
  os.environ` → `False` in the live run.
* Handed to curl on **stdin only**. `curl_argv()` builds
  `["curl", …, "--config", "-", …]` and `call_curl()` passes
  `input=curl_config(key)`. The key never appears in argv, never in a file,
  never in an `os.environ` assignment (the harness contains no `putenv` and no
  `os.environ` write — `grep` returns nothing).
* `call_curl()` refuses a key containing `"`, `\`, `\n` or `\r` rather than
  interpolating it, and no error path interpolates the value
  (`error_detail` is either a fixed string or `f"{type(e).__name__}: {e}"`).
* If the source does not resolve, `frozen_gate()` raises `SystemExit` naming the
  *label* and path only. Confirmed by reading the code; not triggered here
  because the source resolves.

### 2.3 Per-row labels, model pin, endpoint

Across all 238 rows:

| field | value | rows |
|---|---|---|
| `credential_source` | `secrets/typesafe.env#TYPESAFE_API_KEY` | 238 / 238 |
| `secrets_recorded` | `false` | 238 / 238 |
| `model_id` / `model_pinned` | `jev-1.13.0` | 238 / 238 |
| `endpoint` | `https://api.typesafe.ai/v1/systemone` | 238 / 238 |
| `response_model_field` | `jev-1.13.0` | 238 / 238 |
| `response_model_matches_pin` | `true` | 238 / 238 |
| `curl_phases.num_connects` | `1` | 238 / 238 |

Plus 9 live calls by this verifier: 6 re-sample + 3 model-tag probes. All
returned `model: "jev-1.13.0"` where a model was accepted.

The `credential_source` value is a **label**, not a value: it names the file
path and the variable name, and the name `TYPESAFE_API_KEY` appearing in
artefacts is expected and is what the README says a file-scan should look for.

---

## 3. Request equivalence — PASS

For each of the 16 subset cases the direct body was rebuilt from the **frozen**
`results/jev_raw.ndjson` `request_body` with only `model` replaced, serialised
with the same wire encoding, and hashed independently.

| property | result |
|---|---|
| cases checked | 16 / 16 |
| field-name set identical to frozen | 16 / 16 — `{model, questions, state}` on both sides |
| `state` byte-identical | 16 / 16 |
| `questions` byte-identical | 16 / 16 |
| equal after stripping `model` | 16 / 16 |
| keys only in frozen / only in direct | `[]` / `[]` on all 16 |
| frozen hash recomputed = hash on the frozen row | 16 / 16 |
| direct hash recomputed = hash on **every** direct row for that case | 16 / 16 |
| `summary.json` `per_case_request_hashes` = recomputed (frozen and direct) | 16 / 16 |
| direct hash ≠ frozen hash (only `model` differs) | 16 / 16 |
| subset ids present in the direct raw = `subset.json` ids | identical, 16 / 16 |

**No prompt or parameter drift.** For `a-h04` the serialised bodies share an
18-character common prefix and then differ only in the model token, with the
remainder byte-identical:

```
frozen: {"model":"jev-1.13-free","state":"The compliance audi
direct: {"model":"jev-1.13.0","state":"The compliance audit r
```

`sha256` of the direct serialised body for `a-h04`
(`ef1961be…f2779`) matches both the row-recorded `request_hash` and the
`summary.json` entry.

**Two non-defects, recorded so they are not mistaken for drift later.**

* `a-miss1` has 21 rows carrying a body hash, 20 of which are the grid hash
  `8839aaaa…f52`; the 21st is the `interface_probe` row with hash
  `a586702a…fa4` — a deliberately different multi-key body, which is the whole
  point of that probe. Excluding it, 20/20 agree.
* The 6 concurrency rows for that case carry `request_fields: null`. The field
  is written by `run_one()` but not by `row_from_finished_curl()`. The request
  *hash* is recorded on all 238 rows as the README claims; `request_fields` is
  simply absent on concurrency rows. Cosmetic schema inconsistency, no
  measurement impact.

---

## 4. Independent recomputation — PASS with 5 findings

The builder's harness and `analyze_ops` were **not** imported. Percentiles use
nearest-rank with no interpolation (the convention the artefact declares), and
medians are reported both as the true median and as the nearest-rank order
statistic so the difference is visible.

### 4.1 What reproduced exactly (delta = 0)

| statistic | recomputed | artefact | Δ |
|---|---|---|---|
| warm n / mean / p90 / p95 / p99 / min / max / sum / stdev | 192 / 304.3341 / 333.828 / 345.666 / 389.979 / 254.261 / 400.748 / 58432.154 / 23.5553 | identical | 0 |
| first-byte mean / p90 / p95 / p99 / min / max / sum / stdev | 53.4119 / 59.259 / 61.621 / 67.054 / 48.397 / 72.282 / 10255.081 / 3.8178 | identical | 0 |
| TLS-complete mean / all percentiles / stdev | 53.2123 / … / 3.7993 | identical | 0 |
| DNS mean / TCP-connect mean | 1.0491 / 1.9053 | 1.0491 / 1.9053 | 0 |
| post-first-byte residual mean | 250.9223 | 250.9223 | 0 |
| model-attributable residual mean | 251.1218 | 251.1218 | 0 |
| **monotonicity** `nl ≤ connect ≤ appconnect ≤ pretransfer ≤ starttransfer ≤ total` | 192/192 Jev, 183/183 MiMo | claimed | 0 violations |
| transport = `appconnect` alone (mean) | 53.2123 / 201.6431 | identical | 0 |
| the *wrong* sum `dns+tcp+appconnect` | 56.1667 / **205.0413** | followup-03 published 205.0413 | 0 |
| sequential calls/s (sum of `time_total`) | 3.2859 / 0.1674 → ratio 19.63 | 3.2859 / 0.1674 / 19.63 | 0 |
| sequential calls/s incl. process spawn | 3.1592 | 3.1592 | 0 |
| control correct / opportunities | 108/108 and 108/108 | 108/108 both | 0 |
| correct control decisions/s | 1.8483 / 0.0988 → ratio 18.71 | identical | 0 |
| all-subset correct / opportunities | 132/132 and 132/132 | 132/132 both | 0 |
| C=1 makespan / throughput / p50 / p95 | 3878.3 ms / 3.0941 / 302.428 / 363.777 | identical | 0 |
| C=4 makespan / throughput / p50 / p95 | 3720.2 ms / 3.2256 / 297.828 / 340.565 | identical | 0 |
| C=8 makespan / throughput / p50 / p95 | 3824.5 ms / 3.1377 / 304.006 / 356.214 | identical | 0 |
| concurrency scaling vs C=1 | 1.0 / 1.0425 / 1.0141 | identical | 0 |
| MiMo C=1/4/8 makespan, throughput, p50, scaling | 47718.8 / 70279.3 / 58915.4; 0.2515 / 0.1707 / 0.2037; 2758.927 / 5681.477 / 4951.268; 1.0 / 0.6787 / 0.8099 | identical | 0 |
| concurrency failure counts | 12/12 usable, 0×429, 0×529 at every level, both mechanisms | identical | 0 |
| idle proxy (Jev n=3) | 333.115 / 279.602 / 268.085 ms; median 279.602 | identical | 0 |
| measured warm→first-idle gap | **383 s** (satisfies "≥ 120 s") | nominal 120 s | a fortiori |
| Jev label-stable cases / mean flip / max flip | 16 / 0.0 / 0.0 | identical | 0 |
| Jev max-prob spread median / max over cases | 0.01 / 0.03 | identical | 0 |
| MiMo label-stable / mean flip / max flip | 15 / 0.0208 / 0.3333 (unstable case = `b-a03`, 3 usable, yes×2 no×1) | identical | 0 |
| Pearson r(`time_total`, output tokens) | −0.012477 / 0.393508 | −0.0125 / 0.394 | rounding |
| Jev input tokens mean / sum | 358.5 / 68832 | identical | 0 |
| Jev output tokens mean / sum / range | 28.75 / 5520 / 17–69 | identical | 0 |
| Jev USD/call (`input × 0.042/Mtok`, output free) | 1.5057e-05 | 1.5057e-05 | 0 |
| Jev USD per correct control decision | 2.6768e-05 | 2.6768e-05 | 0 |
| Jev correct decisions per dollar | 37358.04 | 37358.0395 | 0.02 |
| whole-run derived cost (238 calls, 84,763 input tokens) | $0.003560046 | $0.003560046 | 0 |
| MiMo warm-only USD/call, per correct, per dollar | 2.6840219e-05 / 4.5479259e-05 / 21988.05 | 2.6840e-05 / 4.5479e-05 / 21988.0 | 0 |
| cost ratios (per call / per decision / per dollar) | 1.7826 / 1.699 / 1.699 | 1.78x / 1.70x / 1.699 | 0 |
| input-rate ratio (0.14 / 0.042) | 3.3333 | 3.33x | 0 |
| Jev reliability | 238 rows, 238×HTTP 200, 0 typed errors, 0×429, 0×529, attempts 1, retries 0 | identical | 0 |
| MiMo 9 unusable warm calls | all `b-a03`, `empty_content`, HTTP 200, `finish_reason: "length"`, `content: null` | identical | 0 |
| MiMo `logprobs` | absent in **0 of 243** raw responses carry the key; all 183 warm usable return no logprobs | "null in all 183" | see G3 |
| MiMo `parsed_probabilities` | 183/183 warm usable are **exactly** one-hot; 234/234 across the whole file | "one-hot vectors … from a scraped label" | confirmed, see §8 |

`python3 harness/run_ops_jev_direct.py check` exits 0 and reports
`summary.json reproduces exactly from the same raw file with
['computed_at_utc'] excluded (PASS)`, writing only a `.check.tmp` that it
removes. `git status` was clean before and after.

### 4.2 Findings

**D1 — MINOR (labelling).** The field named `median` in every distribution
block is the **nearest-rank p50 order statistic**, not the statistical median.

```
Jev warm time_total, n=192 (even):
  statistics.median (true median)    = 305.1335
  nearest-rank p50 = sorted[95]      = 304.9080   <- what the artefact reports
  sorted[95]=304.9080  sorted[96]=305.3590
```

Δ = 0.2255 ms (0.074%). MiMo is unaffected (n=183 is odd, so the nearest-rank
p50 *is* the median). The same block declares
`percentile_method: "nearest-rank, no interpolation"`, so the block is
internally self-consistent — the field *name* is what is wrong. Every quoted
figure survives: 4035.47/305.1335 = 13.23x (reported 13.2x), p99/median =
1.2781 (reported 1.28x), max/median = 1.3134 (reported 1.31x), idle/warm =
0.9163 (reported 0.917). No conclusion moves.

**D2 — MINOR/MEDIUM (undocumented estimator).**
`transport_share_of_total_mean` and `post_first_byte_share_of_total` are
computed as a **ratio of means**, not a mean of per-row ratios, and the
estimator is nowhere documented.

| figure | artefact (ratio of means) | mean of per-row ratios | relative difference |
|---|---|---|---|
| Jev transport share of total | 17.483% | 17.569% | +0.5% |
| **MiMo transport share of total** | **3.377%** | **5.943%** | **+76%** |
| Jev post-first-byte share | 82.452% | 82.366% | −0.1% |
| **MiMo post-first-byte share** | **96.620%** | **94.051%** | **−2.7%** |

The divergence is large only on MiMo, because its mean is dominated by a
60.6 s outlier while its per-row ratio is dominated by the fast rows. Both
mechanisms use the same estimator, so **no cross-mechanism comparison is
biased** and both qualitative claims ("most of the call is post-first-byte",
"Jev's transport share is larger") hold under either estimator. But the
specific percentages in §1.3 (96.62%), §1.4 (3.38%) and §3.1 ("82% / 97%") are
estimator artefacts on a heavy-tailed sample and should be labelled as such.

**D3 — MINOR (internal contradiction, one side wrong).** §1.3's table gives
the MiMo "first byte − transport setup" as **+0.20 ms**. §3.1 gives the same
quantity for MiMo as **−3.19 ms**. My independent recomputation is
`mean(fb) − mean(tls) = 201.8468 − 201.6431 = +0.2037 ms`, which supports §1.3
and refutes §3.1. (The Jev figure, +0.1995 ms, is correct in both places.)

**D4 — MINOR/MATERIAL (mixed denominators inside one table).** §1.11's table
is headed *"Warm-only figures, like-for-like (both excluding warm-up calls)"*.
The USD rows honour that heading (Jev over 192 warm calls, MiMo over 183 warm
usable calls). The two **token** rows do not:

| row | artefact | denominator actually used | like-for-like warm-only |
|---|---|---|---|
| input tokens per call — MiMo | 125.91 | followup-03 `tokens_per_call` over **n_calls = 222** (warm 183 + idle 3 + concurrency 36) | 23502/183 = **128.426** |
| output tokens per call — MiMo | 31.42 | same 222 | 5791/183 = **31.644** |
| "input tokens per call — Jev | 358.50 | 192 warm | 358.50 ✓ |
| **"2.85x MORE input tokens"** | 358.50 / 125.9144 = 2.8474 | mixed | 358.50 / 128.426 = **2.7915** |

So on a genuinely like-for-like warm-only basis the input-token penalty is
**2.79x**, not 2.85x. The cost conclusion is untouched (the cost rows are
correctly warm-only, and the tariff argument — 2.8x more tokens offset by a
3.33x cheaper input rate and free output — holds at either figure). The defect
is that one table mixes two denominators under one "like-for-like" heading, and
the headline "2.85x" is not like-for-like as labelled. The same 2.85x figure is
repeated in `README.md` and in `comparison.md` §4.

**D5 — TRACEABILITY (no wrong number, but the MiMo column is not reproducible
from the repository).** The committed followup-04 `summary.json` contains **no
MiMo comparison column** — only the Jev-direct measurements plus the
`transport_measurement_correction_to_followup_03` block. The MiMo column of
`comparison.md` was produced by `/tmp/opencode/jev-phase1/cmp.py`, a scratch
script that is **not committed** and that, as it currently stands, **cannot
run**: it reads `M['warm_latency']`, `M['sequential_throughput']`,
`M['concurrency']['by_level']`, `M['stability']`, `M['idle_proxy']` and
`M['tokens_and_cost']` from the top level of followup-03's `summary.json`,
whereas followup-03's actual top-level keys are `blocks, determinism,
frozen_inputs_verified, inputs, interface_probe, mechanisms, not_measured,
question, ratios, schema_version, study, transport_probe` — those blocks live
under `mechanisms.mimo.current_window_measurement`. The script also **hard-codes**
seven MiMo values rather than reading them:
`2.684021858e-05`, `4.547925926e-05`, `21988.0253`, transport share `0.034331`,
post-first-byte residual `5770.6702`, Pearson r `0.394`, and the entire
183/192 + 9-empty_content + logprobs narrative.

I recomputed **all seven** from `mimo_ops_raw.ndjson` and every one is correct
(they are in §4.1 above). So the numbers stand. What does not stand is
`README.md`'s artefact table claim that `summary.json` holds "all measurements,
machine-readable, reproducible from the raw file" — true for the Jev side,
false for the MiMo column of `comparison.md`. A future reader cannot re-execute
the comparison from the repository alone.

---

## 5. Semantic-equivalence reproduction — PASS

Direct `jev-1.13.0` answers compared against the **frozen** `jev-1.13-free` row
for the same 16 cases, distributions read out of the raw endpoint JSON (not out
of the parser's output), 12 warm reps per case.

| quantity | recomputed | `equivalence.json` | `comparison.md` §0 |
|---|---|---|---|
| cases whose majority label matches the frozen row | **16 / 16** | 16 / 16 | 16 / 16 |
| agreement rate | 1.0 | 1.0 | 1.0 |
| cases with any answer change | 0 | 0 | 0 |
| cases label-unstable across the 12 warm reps | 0 | 0 | 0 |
| answer `type` stable and equal to frozen | 16 / 16 | — | — |
| `noul` worst-case max abs drift | **0.04** (case `c-p1a`) | 0.04 | 0.04 |
| `noul` median of case medians | 0.01 | 0.01 | 0.01 |
| `choice`/`score` overall max abs prob delta | **0.01** (case `a-h04`) | 0.01 | 0.01 |
| `choice`/`score` median of case medians | 0.00 | 0.00 | 0.00 |

All **16 per-case** drift figures match exactly (`a-dist1` 0.0, `a-e01` 0.01,
`a-e02` 0.01, `a-m07` 0.01, `a-miss1` 0.01, `a-noise1` 0.0, `b-a01` 0.01,
`a-h04` 0.01, `b-a02` 0.01, `b-dist1` 0.01, `c-p1a` 0.04, `b-a03` 0.02,
`c-p1b` 0.0, `d-01` 0.0, `d-02` 0.0, `d-03` 0.0).

The artefact's own conclusion is correctly bounded:
`"equivalence_claimed": false`, with a note that what is reported is measured
agreement plus measured drift between two different model tags on two different
routes. `comparison.md` §0 repeats that boundary and states the licence it
gives ("the direct route answers the frozen corpus the same way … so
'approximately matched semantic capability' holds") without claiming
interchangeability. That is the right scope.

---

## 6. Live sanity re-sample — PASS

Six calls under the documented conditions: the frozen request bodies with only
`model` → `jev-1.13.0`, one `curl` process per call, no connection reuse,
credential on stdin only, never printed. Cases chosen to span all three question
types.

| case | qtype | HTTP | response `model` | `time_total` | first byte | num_connects | in/out tok | answer |
|---|---|---|---|---|---|---|---|---|
| `a-h04` | score | 200 | `jev-1.13.0` | 345.5 ms | 82.0 ms | 1 | 362 / 17 | score 0.04, p = {0: 0.98, 1: 0.02} |
| `a-miss1` | noul | 200 | `jev-1.13.0` | 336.7 ms | 62.8 ms | 1 | 320 / 20 | noul 0.27 → no |
| `d-01` | choice | 200 | `jev-1.13.0` | 334.2 ms | 85.8 ms | 1 | 493 / 66 | build, p = {build: 1.0, ×5 at 0.0} |
| `c-p1a` | noul | 200 | `jev-1.13.0` | 331.8 ms | 70.3 ms | 1 | 308 / 20 | noul 0.72 → yes |
| `d-03` | choice | 200 | `jev-1.13.0` | 314.3 ms | 67.9 ms | 1 | 493 / 69 | investigate, p = {investigate: 1.0, ×5 at 0.0} |
| `a-e01` | noul | 200 | `jev-1.13.0` | 330.8 ms | 50.4 ms | 1 | 322 / 20 | noul 0.91 → yes |

* **Model pin:** `jev-1.13.0` on 6/6.
* **Answers parse:** 6/6, all three question types.
* **Latency order of magnitude:** 314.3–345.5 ms, mean 332.2 ms, against the
  committed warm block's 254.3–400.7 ms, mean 304.3 ms, p95 345.7 ms. Same
  order of magnitude, ~9% higher, consistent with a later window on the same
  host. Not a regression signal, and not claimed as one.
* **Label variance: 0 label flips on all 6 cases.** Every live label equals the
  committed modal label (`low`, `no`, `build`, `yes`, `investigate`, `yes`).
* **Probability variance:** `a-miss1` 0.27 (committed per-rep range
  0.27–0.29), `c-p1a` 0.72 (0.71–0.74), `a-e01` 0.91 (0.91–0.92) — all inside
  the recorded ranges. `a-h04` came back {0.98, 0.02} against the recorded
  {0.97/0.96, 0.03/0.04}: a 0.01 drift, inside the recorded 0.03 max spread.

**Three extra probes of the documented alias behaviour** (claims made in both
`README.md` and `comparison.md`):

| sent `model` | HTTP | response `model` | body |
|---|---|---|---|
| `jev-1.13.0` | 200 | `jev-1.13.0` | normal answer |
| `jev-latest` | 200 | **`jev-1.13.0`** | normal answer |
| `jev-1.13` | **400** | — | `{"detail":{"error_type":"api_usage_error","message":"Unknown model: jev-1.13"}}` |

Both documented claims — "`jev-latest` resolves to `jev-1.13.0`" and
"`jev-1.13` is rejected with 400" — reproduce exactly.

**The one-hot `choice` degeneracy of finding G1 reproduced live** on both choice
cases sampled (`d-01`, `d-03`: 1 of 6 non-zero probability keys, `confidence`
exactly 1.0). It is a stable property of the endpoint on these cases, not a
one-off.

---

## 7. Concurrency spot-check at C=4 — PASS (flatness confirmed)

Replicated the committed block exactly — 6 cases (`sorted(ordered)[:6]` =
`a-dist1, a-e01, a-e02, a-h04, a-m07, a-miss1`) × 2 reps = 12 calls, a real
in-flight limit of C, one curl process per call, credential on stdin, no
retries — and added an instrument the committed run did not have: a
dispatch/completion event log, so real in-flight overlap is **measured** rather
than inferred from the makespan. A C=1 control was run in the same window so
the scaling ratio is not itself cross-window.

| | my C=1 | my C=4 | committed C=1 | committed C=4 |
|---|---|---|---|---|
| calls / HTTP 200 / rc≠0 | 12 / 12 / 0 | 12 / 12 / 0 | 12 / 12 / 0 | 12 / 12 / 0 |
| HTTP 429 / 529 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| **measured peak in-flight** | **1** | **4** | not instrumented | not instrumented |
| makespan | 3764.2 ms | 3863.5 ms | 3878.3 ms | 3720.2 ms |
| throughput | 3.1879 /s | 3.1060 /s | 3.0941 /s | 3.2256 /s |
| Σ`time_total` | 3610.3 ms | 3752.5 ms | 3717.7 ms | 3622.7 ms |
| makespan / Σ`time_total` | 1.0426 | 1.0296 | 1.0432 | 1.0269 |
| p50 `time_total` | 292.2 ms | 309.0 ms | 302.4 ms | 297.8 ms |
| scaling vs C=1 | 1.000 | **0.9745** | 1.000 | **1.0425** |

**Real parallelism was achieved** — peak in-flight 4 at C=4 — and the makespan
still did not shrink. That is the substantive confirmation: the flat curve is a
property of the endpoint, not of a client that failed to issue calls in
parallel. Reading the harness confirms the committed run had the same property
by construction (it launches up to C processes before blocking on the first),
it simply did not instrument it.

**The qualitative finding reproduces; the individual per-level ratio does
not.** My C=4/C=1 is 0.9745x where the committed value is 1.0425x. Both are
≈1.0, so "flat" holds — but the *sign* of the deviation is not stable at n=12,
which means the specific figures "1.04x" and "1.01x" in `comparison.md` §1.6 and
`README.md` are noise-dominated and should be read as "flat within about ±5%".
`comparison.md`'s own caveat ("**n=12 calls per level** — a small block")
covers this; the numbers simply should not be quoted as a directional signal.

0 label flips in either block. `a-h04`'s `score` value drifted 0.03 → 0.04
across the two reps in **both** blocks — a numeric drift inside the recorded
0.01–0.03 spread, not a label flip. All 24 responses carried
`model: "jev-1.13.0"` and `num_connects: 1`. All 24 rows had a graded
distribution, because the 6 concurrency cases are all `noul`/`score` — the
degeneracy of G1 is a property of the `choice` cases specifically, not of
concurrency.

---

## 8. Classification audit — MIXED

### Targets that pass

| target | verdict | evidence |
|---|---|---|
| Every claim labelled ESTABLISHED / UNRESOLVED / SERVING-OR-PRICING-ARTEFACT | **PASS** | §1 (11 items), §2 (12 rows), §3 (9 items) partition the document with no orphan claim found; the four §1.8/§1.9/§2 "confidence" flags are cross-referenced rather than asserted |
| Transport vs service separation sound | **PASS** | `appconnect` alone; monotonicity verified on 192 Jev + 183 MiMo rows; the *incorrect* sum reproduces followup-03's published 205.0413 ms **exactly**, which validates the correction's premise rather than merely asserting it |
| Cross-window caveat present for the MiMo comparison | **PASS** | §0 (headed "CROSS-WINDOW COMPARISON", with the three-way cause split), §3.8, §5, plus `comparison_class` in `summary.json` |
| No claim rests on the old free-tier $0 | **PASS** | every `$0` mention is a contrast row ("free tier, $0" → "$0.042"), an explicit retraction ("The frozen Jev route cost $0 and this one does not… Any statement that 'Jev is free' is now false"), or the derived $0.00356. No ratio divides by the old $0 |
| Cost maths correct | **PASS** | every figure reproduces to 10 significant figures; the derivation (`input_tokens / 1e6 × 0.042`, output free) is exactly what the code does; tariff-ratio 3.3333x; whole-run $0.003560046 from 84,763 tokens |
| The probability-availability **correction** of followup-03's 234 | **PASS — decisively** | 0 of 243 MiMo raw responses contain a `"probabilities"` key; 0 contain `"logprobs"`; the raw `content` is the bare scraped label (`"low"`); **234 of 234** rows with non-null `parsed_probabilities` are *exactly* one-hot, i.e. synthesised by the parser. The correction is correct and the document is right to record it as a correction rather than silently applying it |
| "What this changes" note bounded, not a consolidated verdict | **PASS** | §4 states three changes and then a "What did not change" paragraph; the consolidated verdict is refused three times (README, `comparison.md` header, §4 close) and recorded as OUT OF SCOPE in both documents and in `summary.json.not_measured` |
| followup-03's free-tier Jev cells correctly left UNRESOLVED | **PASS** | followup-03's summary has `current_window_measurement` = all `null`, `status: "UNRESOLVED"`; its raw file has 197 rows = 125×HTTP 403 + 72×HTTP 429 with 0 parsed predictions |
| §2 UNRESOLVED completeness | **PASS** | §2 is a strict superset of `summary.json.not_measured` (6 keys) plus 6 further rows |

### Findings

**G1 — MATERIAL (classification gap).** §1.9/§4.2's probability-availability
claim is stronger than the evidence supports. **36 of the 192 warm calls
(18.75%) — every call on all three `choice` cases — return a *degenerate
one-hot* distribution**: exactly `1.0` on the selected option and `0.0` on the
other five, on all 12 reps of all 3 cases. Their reported `confidence` is
**exactly 1.0** on all 36.

```
case     qtype   n   keys  one-hot rows  graded rows  distinct non-zero counts
a-dist1  noul   12    2        0            12         {2: 12}
...  (11 more noul cases, identical shape)
a-h04    score  12    3        0            12         {2: 12}
d-01     choice 12    6       12             0         {1: 12}
d-02     choice 12    6       12             0         {1: 12}
d-03     choice 12    6       12             0         {1: 12}
TOTAL              192          36           156        one-hot 18.75% / graded 81.25%
Reported `confidence` field values observed: score 0.93 (×2), 0.94 (×9), 0.95 (×1);
choice 1.0 (×36).
```

Those 36 vectors are **informationally identical** to the one-hot vectors §3.4
correctly identifies as an artefact in followup-03's MiMo figures. The
*provenance* difference the document claims is real and correct (Jev's arrive in
the endpoint's JSON; MiMo's were built by the parser from a scraped label) — but
the document applies its own §3.4 standard to the parser's one-hot vectors and
not to the endpoint's, and nowhere records that 18.75% of its own "100%
model-provided distributions" carry no graded information. Graded multi-way
distributions *are* demonstrably available: the single interface-probe `choice`
answer had 5 of 6 keys non-zero (`review 0.59, investigate 0.37, repair 0.02,
escalate 0.01, redesign 0.01`). But that is n=1, outside the grid and explicitly
excluded from statistics. §1.9's "a full 6-way distribution over the option
keys" is technically true (6 keys) and materially misleading (degenerate on
36/36).

**G2 — MATERIAL (overreach against the document's own UNRESOLVED list).** §1.9
states "a calibrated probability per option is available from Jev-direct", and
§4.2 states "A bounded-judgement method whose whole value is a calibrated
probability per option can be built on this route". §2 of the *same document*
lists "Probability **calibration** | **NOT MEASURED**". The two cannot both
stand. Independently of the calibration question, the evidence does not support
the claim for the multi-way case at all: on the only 6-option cases measured, the
distribution was one-hot on 36 of 36 calls, and the `confidence` accompanying
them is the tautology 1.0.

**G3 — MINOR (wording, mechanism wrong).** §1.9: "`logprobs` present in the
response body … **null in all 183**". The `logprobs` key is **absent entirely**
— the string `"logprobs"` occurs in **0 of 243** MiMo raw responses. "Present
and null" and "absent" are different states. The substantive conclusion (MiMo
returned no logprobs, and an explicit `logprobs: true` probe failed) is correct
and independently verified.

**G4 — MINOR (wording).** §1.9's "`choice` — a full 6-way distribution over the
option keys (36 calls, 3 cases)" — see G1. Six keys, yes; "full" implies graded
content that was not present on any of the 36 calls.

**G5 — MINOR (labelling).** D1: `median` is nearest-rank p50.

**G6 — MINOR (estimator).** D2: the two "share" figures are ratio-of-means and
the estimator is undocumented.

**G7 — MINOR (window statement).** §0/§5 place MiMo at "roughly
2026-09-26T13:09Z–13:33Z". That is the **warm** window (followup-03's own
coarse check gives first `13:09:42Z`, last `13:32:54Z` over the 192 warm rows)
and is correct for the latency/throughput tables, but the full `resume1` block
runs to **13:56:27Z** because the concurrency block comes after. The stated
window therefore understates the MiMo measurement window by ~23 minutes for the
concurrency table. The word "roughly" and the cross-window caveat absorb it.

**Correctly classified and independently confirmed** (no finding): §1.3's
"`time_starttransfer` is NOT a model signal" (fb − tls = +0.1995 ms Jev /
+0.2037 ms MiMo; fb stdev 3.82/12.49 against total stdev 23.56/6402.99);
§3.9's followup-03 transport double-count correction and its error size
(205.0413 → 201.6431, +1.686%; 3.4331% → 3.3771%, +0.056 pp; 5767.4757 →
5770.8739, −0.059%, sign convention consistent with the row above it);
§1.7's characterisation of MiMo's 9 failures as *silent* (HTTP 200, content
null); §1.10's interface probe (raw response reproduced verbatim in
`fu4-conc-probe.log`, all 3 keys answered, nothing scored); §2's idle caveat
(n=3, proxy only — and the recorded `idle_seconds_before: 120` is the *nominal*
sleep while the measured warm→first-idle gap was 383 s, which satisfies the
"≥ 120 s" claim a fortiori).

---

## 9. Measurement limitations and unverifiable claims

### 9.1 Limitations of the evidence as it stands

1. **Cross-window, three windows, one host.** MiMo `resume1`
   2026-09-26T13:09:42Z–13:56:27Z; Jev-direct grid
   2026-09-26T16:15:53Z–16:24:00Z; this verifier's live re-sample ~16:5xZ. Same
   host, same `curl`, same 16-case subset, same scoring function. Structural,
   network-transport and pricing causes are separated by argument, not by
   design — one window each cannot separate a time-of-day effect from a
   mechanism effect.
2. **Single host, single network, single region.** No second vantage point, so
   every network-transport number is a property of this path.
3. **No connection reuse anywhere.** `num_connects == 1` on all 238 committed
   rows and on all 15 of my live calls. Every call pays a fresh DNS + TCP + TLS.
   This inflates absolute per-call latency for **both** mechanisms by the same
   ~53 ms (Jev) / ~202 ms (MiMo), so ratios are largely unaffected, but absolute
   calls/sec would rise on a reused connection and the transport share (D2)
   would change materially.
4. **Rate-limit ceilings never approached.** 0 × 429 in 238 calls. The published
   1,200 req/min ≈ 20/s against an observed ~3.3/s sequential and ~3.2/s at
   C=8. Nothing here constrains where the ceiling binds.
5. **n = 12 per concurrency level**, and my re-measurement shows the per-level
   ratio is noise-dominated (0.9745x vs the committed 1.0425x).
6. **n = 3 for the idle proxy**, per mechanism.
7. **The equivalence reference is one frozen row per case.** The frozen side has
   no repeat axis, so a single frozen row cannot itself be shown to be stable;
   all stability evidence is on the direct side.
8. **One interface probe (n = 1)**, outside the grid, unscored, and the only
   evidence that a graded multi-way `choice` distribution is obtainable.
9. **Output-token range 17–69 only.** §1.2's "latency is independent of work
   done" is established over that narrow range and the document correctly
   forbids extrapolating it.
10. **Not tested at all:** sustained or multi-hour load, HTTP 529, C > 8,
    probability calibration, the meaning of `confidence`, cross-day and
    cross-version behaviour, and the economics of batched multi-question calls.

### 9.2 Claims that could not be verified

| # | claim | why unverifiable |
|---|---|---|
| U1 | §1.4 "consistent with a closer or warmer edge" | A causal hypothesis about CDN edge proximity. No artefact can distinguish edge distance from route quality, TLS negotiation cost, or transient load. Hedged, but unevidenced. |
| U2 | Published limits 250,000 tok/s and 1,200 req/min; HTTP 529 = overloaded; 64k context | Provider documentation, not present in any artefact. The document is right to keep them in a block explicitly named `published_facts_not_used_to_support_any_measurement` and to refuse to use them for any measurement — I verified that separation holds. |
| U3 | §3.6 `x-opencode-session` header semantics on `api.typesafe.ai` | The document already flags this as unestablished. Nothing in the evidence can establish it. |
| U4 | §1.1 "whether the bound is a property of the endpoint or of the empty queue it was measured in" | Correctly listed in WHAT-NOT-TESTED. Separating them needs sustained load, which was not run. |
| U5 | Whether MiMo would return probabilities under a different `logprobs` shape, endpoint, or sibling model | Correctly UNRESOLVED. Only `mimo-v2.6-flash` on this route was probed. |
| U6 | Whether Jev's probabilities are calibrated | Correctly NOT MEASURED. Availability was measured; calibration is a different experiment. |
| U7 | Whether the `confidence` field carries information | The document cites `0.5` on both probe answers. I can add evidence rather than resolve it: across the 48 grid rows it takes only three values — `1.0` on all 36 one-hot `choice` calls, and `0.93 / 0.94 / 0.95` on the 12 `score` calls, where it tracks the (degenerate-adjacent) distribution. Consistent with a deterministic function of the returned distribution; **not** evidence of calibration. |
| U8 | The MiMo figures hard-coded in the uncommitted `/tmp` script | I recomputed all seven from `mimo_ops_raw.ndjson` and all are correct, but the derivation path itself cannot be re-executed from the repository (D5). The numbers are right; the pipeline is not reproducible. |
| U9 | That the local answer normaliser generalises beyond the frozen corpus | The gate proves `normalise_answer` ≡ frozen `common.parse_jev` on 64/64 frozen rows — by design, equivalence on the corpus, not on arbitrary responses. The one multi-question response it was trusted on is n=1. |
| U10 | That `results/jev_direct_raw.ndjson` is a faithful record of the network | `check` proves `summary.json` is a pure function of the committed raw file; it cannot prove the raw file faithfully recorded the wire. My 9 live calls all agreed with the committed record on model, label and probability band, which is corroboration, not proof. The endpoint is live, so the run cannot be re-executed bit-identically. |

---

## 10. Summary of findings

| id | severity | finding |
|---|---|---|
| G1 | **MATERIAL** | 36/192 (18.75%) of Jev-direct's "100% model-provided" distributions — all three `choice` cases — are degenerate one-hot with `confidence` exactly 1.0; the document does not record this and does not subject the endpoint's own one-hot vectors to the §3.4 test it applies to the parser's. |
| G2 | **MATERIAL** | §1.9/§4.2's "a calibrated probability per option is available / can be built on this route" contradicts §2's own "Probability calibration NOT MEASURED" and is unsupported for the 6-option case. |
| D5 | traceability | The MiMo column of `comparison.md` is absent from the committed `summary.json` and was produced by an uncommitted scratch script that can no longer run against followup-03's summary. All figures recomputed and correct. |
| D4 | minor/material | §1.11 mixes a warm-only Jev token denominator (192) with followup-03's whole-window MiMo token denominator (222) under one "like-for-like" heading; the "2.85x more input tokens" figure is **2.79x** on a like-for-like basis. |
| D2 | minor/medium | The two "share" percentages are undocumented ratio-of-means; on MiMo the alternative estimator moves transport share 3.377% → 5.943% and post-first-byte share 96.620% → 94.051%. No cross-mechanism comparison is biased; both qualitative claims survive. |
| D3 | minor | §3.1's "−3.19 ms on MiMo" contradicts §1.3's "+0.20 ms" for the same quantity; the recomputed value is +0.2037 ms, so §3.1 is wrong. |
| D1 | minor | The field named `median` is nearest-rank p50 (Jev warm: 304.908 reported vs 305.1335 true). Every quoted figure survives to the same rounding. |
| G3 | minor | §1.9's "`logprobs` … null in all 183" — the key is absent from all 243 MiMo raw responses, not present-and-null. |
| G4 | minor | §1.9's "a full 6-way distribution" is six keys but degenerate on 36/36 calls. |
| G7 | minor | §0/§5's MiMo window (13:09Z–13:33Z) is the warm window; the full `resume1` block runs to 13:56Z. |
| — | observation | 6 concurrency rows lack `request_fields` (hash present on all 238). |
| — | observation | `idle_seconds_before: 120` is the nominal sleep; the measured gap was 383 s (satisfies the claim a fortiori). |
| — | observation | My C=4 scaling is 0.9745x against the committed 1.0425x; "flat" reproduces, the per-level ratio is noise. |
| — | observation | `README.md`'s claim that `summary.json` holds "all measurements" holds for the Jev side only. |
| — | observation | The interface probe is the only evidence that a graded multi-way `choice` distribution is obtainable (n=1). |

**Bottom line.** The measurement work is trustworthy: the frozen inputs are
intact, the request bodies are provably identical apart from the model pin, the
credential discipline survives an adversarial scan of 143,000+ files and 276,241
live process command lines, and every operational figure reproduces exactly from
the raw evidence. The findings are concentrated in *presentation and
classification*, not in *measurement*. The two material findings narrow — but do
not overturn — §1.9's probability-availability claim: the endpoint genuinely
returns a distribution on 192/192 calls where the comparison route returned none,
yet on the only multi-way cases measured that distribution carried no graded
information, and its calibration is untested by the document's own admission.

**The consolidated Phase-1 verdict remains out of scope and is not asserted
here.**
