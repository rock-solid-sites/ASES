# Followup-03 — operational comparison: Jev 1.13 (free) vs MiMo V2.6 Flash

Issue **#565**. One bounded operational follow-up inside Phase 1.

## Question

> Given roughly matched bounded-decision accuracy on the frozen corpus, does
> Jev provide a material **latency, throughput, cost, or operational**
> advantage over the cheap general model (MiMo V2.6 Flash)?

This study does **not** re-derive the semantic benchmark and does **not**
write a consolidated Phase-1 verdict. Its outcome is operational, and one of
its two main results is negative: see `comparison.md`.

## Read this first — the headline caveat

**The Jev/MiMo comparison could not be completed as a matched pair.** Jev's
free tier refused every call in this measurement window (197 of 197), and a
bounded 10-probe availability series found no usable answer either. So:

- MiMo's latency, throughput, concurrency scaling, stability, token use and
  derived cost are **measured in this window**.
- Jev's latency, throughput and concurrency in this window are
  **UNRESOLVED** — not estimated, not extrapolated, not filled in.
- The only Jev latency/usage evidence that exists comes from the **frozen
  Phase-1 window** (`../results/jev_raw.ndjson`, 64 usable calls, 02:46–02:50Z,
  Python `urllib` transport). It is a different window and a different
  transport, and every Jev/MiMo ratio in `comparison.md` is labelled
  cross-window for that reason.

## Scope and frozen conditions

| | |
|---|---|
| Corpus | `../cases.ndjson` (frozen, sha256 `7dd4698f…f558c`) |
| Subset | `subset.json` — 16 cases, frozen before any measurement |
| Selection rule | deterministic, stratified by area A/B/C/D; 12 noul / 3 choice / 1 score; 5 unanswerable; 4 control variants; 3 complete contrastive pairs |
| F1 correction | `cp4`, derived not hardcoded; a **verified no-op** on this subset (the rule selected no `cp4` member) |
| Attempts per call | **1** |
| Retries | **0** |
| Sequential order | case-major, ascending case id |
| Concurrency | 6 cases x 2 reps = 12 calls at C=1, 4, 8 |
| Model parameters | frozen; **nothing tuned** |
| Transport | `curl` for both mechanisms, one process per call, no connection reuse |
| Credentials | resolved at runtime, passed to curl on stdin, **never printed or written to any artefact** — only the source label (`env:OPENCODE_GO_API_KEY`, `auth.json#opencode-go`) |

Frozen inputs are re-verified at the start of every harness command and again
at analysis time; a mismatch is a hard stop.

### Cost

Derived from actual per-row `usage` at the current catalog rates
(MiMo: input $0.14/Mtok, output $0.28/Mtok, cache read $0.0028/Mtok; Jev free
tier 0/0/0). These rates are **pricing and entitlement facts** — promotional
and tier-dependent — and are never used to support a structural latency or
throughput claim. Actual spend for the whole study is under $0.01.

## Files

```
subset.json                       frozen 16-case id list, rule, rationale
harness/run_ops.py                subset | transport | verify | warm | idle | concurrency | probe
harness/jev_ratelimit_probe.py    bounded Jev availability probe series
harness/analyze_ops.py            deterministic analysis -> summary.json + comparison.md
results/jev_ops_raw.ndjson        197 rows, block=null, 0 usable — the 403->429 evidence
results/mimo_ops_raw.ndjson       243 rows: 11 block=null (aborted) + 232 block=resume1
results/concurrency_defect_401.ndjson  36 rows, HTTP 401 — a harness defect, see below
results/jev_ratelimit_probes.ndjson  10 bounded probes, >=60s apart
results/transport_probe.json      connect-only reachability, no inference
results/summary.json              every statistic with its own denominator
comparison.md                     findings, rendered from summary.json
```

`results/mimo_ops_raw.ndjson` in block `resume1` breaks down as
**192 warm + 3 idle + 36 concurrency + 1 interface_probe = 232 rows, 223 usable**
(9 warm rows are `empty_content`: reasoning consumed the whole 256-token
budget before any answer text was emitted).

### Raw-file block labelling

The raw NDJSON files hold **two blocks**, and this matters when reading any
number:

- `block: null` — the first, aborted attempt. For Jev it is the 197-call
  rate-limit collapse. For MiMo it is 11 rows (5 discarded warm-up + 6 of a
  warm grid that never finished). **Excluded from every warm statistic.**
- `block: "resume1"` — this run's complete MiMo grid. **This is the
  measurement block.**

The appender keys on `(mechanism, phase, case, repeat, concurrency, block,
probe)`, so a resumed block can neither duplicate nor rewrite an earlier one.
The failed null-block Jev rows are retained verbatim and must never be
deleted: they are the evidence for the study's main negative result.

One label was set after the fact: the single interface-probe row was written
with `block: null` because `cmd_probe` does not forward `--block`. In this file
`null` asserts "predates block labelling / aborted first attempt", which is
false for a row produced inside the `resume1` window, so the row was relabelled
to `resume1` with a `block_label_correction` field recording the change. No
measured value was touched, and the row is outside every grid statistic by
construction (`phase: interface_probe`). Without the correction the `resume1`
window would have been silently split.

## Reproduce

Prerequisites: `python3` (stdlib only), `curl`, and both credentials
resolvable — `OPENCODE_GO_API_KEY` in the environment and
`opencode-go.key` in `~/.local/share/opencode/auth.json`. Jev's credential is
`env:OPENCODE_GO_API_KEY`; the Go environment key is unsubscribed, so MiMo
must come from `auth.json`.

Run everything from this directory (`followup-03-operational/`).

### 1. Freeze the subset (must precede any measurement)

```bash
python3 harness/run_ops.py subset
```

Re-running this on unchanged frozen inputs reproduces `subset.json` byte for
byte; the harness hard-stops on drift.

### 2. Connect-only transport probe (no inference; never folded into latency)

```bash
python3 harness/run_ops.py transport
```

### 3. MiMo measurement grid

```bash
# warm grid: 16 cases x 12 reps, sequential, one attempt, no retries
python3 harness/run_ops.py warm      --mechanism mimo_v26_flash --block resume1 --skip-warmup

# idle/cold proxy: idles >=120s with no calls, then 3 calls
python3 harness/run_ops.py idle      --mechanism mimo_v26_flash --block resume1

# concurrency: 6 cases x 2 reps at C=1, 4, 8
python3 harness/run_ops.py concurrency --mechanism mimo_v26_flash --block resume1

# interface probe: ONE labelled call outside the grid, with logprobs: true
python3 harness/run_ops.py probe     --mechanism mimo_v26_flash --block resume1
```

Total: 192 + 3 + 36 + 1 = 232 MiMo calls, 223 usable, 0 retries, 1 attempt per
call throughout.

Derived spend: **$0.0059** over the 222 usable grid calls the cost section
aggregates (warm + warm-up + idle + concurrency). Adding the 11 aborted
null-block rows and the 1 probe row, every row in the file sums to **$0.0069** —
the difference is selection, not drift. The interface probe alone cost
$0.000023.

> **A defect was found and fixed while running the concurrency phase — read
> `Known harness defects` below before reproducing it.** The first concurrency
> block in this window returned 36/36 HTTP 401 and was re-run after a one-token
> fix; both the defective rows and the fix are preserved.

**Long phases must be run detached with a heartbeat.** A foreground
`run_ops.py warm …` can produce no stream output for minutes, and a tool that
kills a silent command will kill the run mid-grid and leave a partial block:

```bash
setsid nohup python3 harness/run_ops.py warm --mechanism mimo_v26_flash \
    --block resume1 --skip-warmup > /tmp/fu3-mimo-warm.log 2>&1 &
PID=$!
# then poll from the foreground, printing every ~20s, exiting when the run does:
while kill -0 $PID 2>/dev/null; do
  echo "[hb] $(date -u +%H:%M:%SZ) rows=$(wc -l < results/mimo_ops_raw.ndjson) log=$(stat -c%s /tmp/fu3-mimo-warm.log)B"
  sleep 20
done
wait $PID; echo "exit=$?"
```

Prefer the captured-`$PID` `kill -0` loop over `pgrep -f`: `pgrep -f` can match
its own pattern or a *different* concurrent run of the same phase, and a
heartbeat that watches the wrong process is worse than no heartbeat. Every
phase in this window (idle, concurrency, probe) was run this way, one phase at
a time — the phases must not overlap, or the idle phase's 120 s gap is not a
gap.

`setsid` is recommended over `nohup` alone: a tool-level timeout kills the
whole process group, and `setsid` puts the run in its own session so it
survives. Both background attempts in this study that omitted `setsid` were
killed mid-grid; the rows they had written were kept and the block re-run under
`resume1`.

### 4. Jev availability probes (bounded; not a measurement phase)

```bash
python3 harness/jev_ratelimit_probe.py --max-probes 10 --min-gap 60
```

One attempt per probe, never retried, >=60s apart, at most 10, stopping early
on the first usable answer. Refuses a `--min-gap` below 60s. Rows go to
`results/jev_ratelimit_probes.ndjson` so no probe can leak into a statistic.

### 5. Jev grid — **did not run, and why**

The design's Jev warm grid was **not executed in this window** because the
free tier rejected every call. The fallback used instead:

```bash
# FROZEN Phase-1 Jev window: the only Jev latency/usage evidence that exists.
# Read-only; sha256 e17ae014…82d3bc, 64 usable calls, 02:46-02:50Z, python urllib.
../results/jev_raw.ndjson
```

Had a probe succeeded, the reduced paced block would have been:

```bash
# Reduced and PACED — not comparable to the unpaced sequential figure.
python3 harness/run_ops.py warm --mechanism jev --block paced1 --skip-warmup --reps 5 --interval 2
python3 harness/run_ops.py idle --mechanism jev --block paced1
python3 harness/run_ops.py concurrency --mechanism jev --block paced1
```

`--reps` above the frozen 12 is refused; a lower value prints a
REDUCED/PACED banner and stamps `reduced_reps` / `paced_interval_seconds` on
every row, so a paced block can never be silently pooled with an unpaced one.

### 6. Cross-transport validation of the frozen Jev window

```bash
python3 harness/run_ops.py verify
```

Re-runs >=4 frozen Jev cases through curl and compares label and
distribution against the frozen rows. **Not run in this window** — it needs
Jev calls, and Jev was refusing them. It is listed so its absence is
explicit rather than mistaken for a passing check.

### 7. Analysis

```bash
python3 harness/analyze_ops.py --check
```

Deterministic: no clock read, no randomness, no network. `--check` builds the
document twice in-process and asserts the two serialisations are
byte-identical, then prints the SHA-256 of `results/summary.json` and
`comparison.md`. Running it twice from a clean clone over the same raw files
must print the same two hashes.

## Known harness defects found and fixed in this window

Two defects were found while finishing this study. Both are recorded here
because both **misreported a measurement rather than failing loudly**, which is
the dangerous class.

### 1. `curl_argv_for` dropped `--config -` — concurrency measured nothing

`call_curl` (the sequential path used by `warm`, `idle` and `probe`) passes
`--config -` so curl reads the bearer token from stdin. `curl_argv_for` (the
parallel path used by `concurrency`) deliberately omitted that token, so the
config piped to stdin was silently discarded and **no `Authorization` header was
sent**. Every call answered
`401 {"error":{"type":"AuthError","message":"Missing API key."}}`.

This failure is worse than an error because it *reads as a speedup*: with no
inference happening, `time_total` collapsed to ~0.2–0.3 s and the C=1 block
finished in 4.3 s instead of 47.7 s. Taken at face value it would have shown
concurrency making the route 10x faster. The tell was `2xx=0 http429=0
errors=12` — zero successes *and* zero rate limits.

- Fixed by adding `--config -` to `curl_argv_for` (one token).
- The 36 defective rows are preserved **verbatim** in
  `results/concurrency_defect_401.ndjson`. They cost $0.00 and consumed no
  tokens, because no inference occurred. They are held OUT of
  `results/mimo_ops_raw.ndjson` deliberately: they measure the harness, not the
  route, and leaving them in the measurement store would have silently split
  the `resume1` concurrency block.
- Re-run after the fix: 36/36 HTTP 200, 0 errors, 0 × 429.

### 2. Analyzer rounded USD-per-unit to 4 dp — cost reported as $0

`r4` (round to 4 decimal places) was applied to per-call and per-decision cost.
A per-call cost here is ~2.7e-5 USD, so `r4` returned exactly `0.0`. The
headline then read **"Cost per call $0.000000"** and "correct decisions per
dollar: n/a" — which, set against Jev's "$0.00", reads as *the two mechanisms
cost the same, i.e. both free*. The headline is the cost comparison this study
exists to make, so this was not cosmetic. Fixed with `r_usd` (10 dp) for
USD-per-unit quantities. The values are now `$0.000026` per call and
`$0.000045` per correct control decision (21,988 per dollar).

A second, smaller reporting error fixed at the same time: the headline row
"Calls attempted this window" read the **warm-only** usable count (183) from
the sequential-throughput statistic, understating the window once idle,
concurrency and probe rows existed. It now reports the whole measurement block
(232 attempted / 223 usable) via `window_call_counts`, with the warm-only
figure still available at `sequential_throughput.n_calls_usable`.

## Status

| phase | mechanism | state |
|---|---|---|
| subset freeze | — | done, `subset.json` |
| transport probe | both | done |
| warm grid, 192 calls | MiMo | done, block `resume1` (183 usable, 9 `empty_content`) |
| idle/cold proxy, 3 calls | MiMo | done — 120 s gap; **no cold-start penalty observed** (post-gap max 0.42x the warm p95) |
| concurrency C=1/4/8 | MiMo | done — 36/36 usable; **first block 36× HTTP 401 from a harness defect, fixed and re-run** |
| interface probe (logprobs) | MiMo | done — 1 call, HTTP 200, `logprobs` **not returned** |
| availability probes, 10 | Jev | done — 0 usable answers |
| warm grid, 192 calls | Jev | **not run — free tier refused all calls** |
| idle/cold proxy | Jev | **not run** |
| concurrency C=1/4/8 | Jev | **not attempted — see `comparison.md` §2** |
| paced reduced block | Jev | **not run — its precondition never held** |
| cross-transport verify | Jev | **not run — needs Jev calls** |
| analysis + report | both | done |

`comparison.md` carries the findings, classified **ESTABLISHED**,
**UNRESOLVED**, and **SERVING-OR-PRICING ARTIFACT**, with every denominator
stated and an explicit list of what could not be measured.
