# followup-04-jev-direct — Jev over the direct TypeSafe API

**One bounded experiment, answering the Jev side of followup-03's open item.**

## The question

At approximately matched semantic capability, does direct Jev (`jev-1.13.0`)
materially improve **latency, tail latency, throughput, reliability, probability
availability, or cost** relative to MiMo V2.6 Flash (frozen followup-03
measurements)?

**This follow-up does not produce the consolidated Phase-1 verdict.** It
measures the Jev side and compares. The verdict is the orchestrator's to draw
from the whole evidence set.

## What changed, and why this is not a rerun

followup-03 measured `jev-1.13-free` over
`https://opencode.ai/zen/v1/systemone` and obtained **0 usable answers in 197
calls**, so its Jev latency / throughput / concurrency / stability cells are
recorded UNRESOLVED. This run changes the route and the model tag:

| | followup-03 (frozen) | this run |
|---|---|---|
| endpoint | `https://opencode.ai/zen/v1/systemone` | **`https://api.typesafe.ai/v1/systemone`** |
| method | POST | POST |
| model | `jev-1.13-free` | **`jev-1.13.0`** (pinned) |
| price | free tier, $0 | **$0.042 / Mtok input, output free** |
| rate limits | free-tier cap | 250,000 tok/s, 1,200 req/min (429 over; 529 overloaded) |
| context | — | 64k |
| usable answers | 0 of 197 | **238 of 238** |

`jev-latest` resolves to `jev-1.13.0`; `jev-1.13` is rejected with 400. The pin
is sent verbatim and **the response `model` field is asserted equal to
`jev-1.13.0` on all 238 rows** (0 mismatches).

**These are new observations of a new path.** They do **not** retroactively fill
followup-03's UNRESOLVED free-tier cells — a different route cannot complete
them.

## Headline result

At **matched control accuracy (108/108 for both)** and **matched semantic
capability (16/16 label agreement with the frozen Jev row, verified before any
comparison was used)**:

| axis | Jev direct | MiMo frozen | ratio |
|---|---|---|---|
| median latency | **304.9 ms** | 4,035.5 ms | 13.2x faster |
| p95 latency | **345.7 ms** | 15,955.6 ms | 46.2x faster |
| p99 latency | **390.0 ms** | 27,609.6 ms | 70.8x faster |
| p99 / median (tail shape) | **1.28x** | 6.84x | — |
| sequential calls/sec | **3.286** | 0.167 | 19.6x |
| correct control decisions/sec | **1.848** | 0.099 | 18.7x |
| warm usable calls | **192 / 192 (100%)** | 183 / 192 (95.3%) | — |
| label-stable cases | **16 / 16** | 15 / 16 | — |
| model-provided probabilities | **192 / 192 (100%)** | **0 / 183 (0%)** | — |
| USD per call | **$1.5057e-05** | $2.6840e-05 | 1.78x cheaper |
| correct decisions per dollar | **37,358** | 21,988 | 1.70x |
| concurrency C=1→4→8 | **1.00x / 1.04x / 1.01x** (flat) | 1.00x / 0.68x / 0.81x (degrades) | — |

Full analysis, classification, and caveats: **`comparison.md`**.

Two things to read before quoting any of it:

- The comparison is **CROSS-WINDOW** (MiMo ~13:09Z–13:33Z, Jev-direct this
  window; same host) and separates structural / network-transport /
  pricing-serve causes.
- Jev's cost advantage is a **tariff** result, not token efficiency: Jev uses
  **2.85x more input tokens** per call and is still cheaper because
  $0.042/$0.00 beats $0.14/$0.28. Both tariffs are promotional and
  tier-dependent.

## Headline caveats

- **`time_starttransfer` is NOT a model signal on this endpoint.** The first
  byte lands 0.20 ms after TLS completion; 82% of the call is the post-first-byte
  body wait. Only `time_total` is a defensible latency figure. (Same finding
  independently reproduces for MiMo on a different host.)
- **Jev's transport *share* rising to 17.5% is not a transport regression** —
  the absolute handshake is 3.8x faster; the share rises only because the total
  shrank.
- **followup-03's `probabilities_exposed_under_frozen_conditions: 234` is a
  parser artefact** (one-hot vectors built by the frozen regex parser from a
  scraped label), not a model capability. The defensible MiMo figure is **0**,
  corroborated by `logprobs` being null in all 183 responses and by
  followup-03's own `logprobs: true` probe failing.
- **Untested:** sustained multi-hour throughput, the rate-limit envelope,
  HTTP 529 behaviour, concurrency above C=8, probability *calibration*,
  behaviour across route/model version changes.

## Conditions

**Request semantics.** For each of the 16 frozen subset cases the request body is
the **frozen phase-1 `results/jev_raw.ndjson` `request_body` verbatim**, with
exactly one field changed: `model` → `jev-1.13.0`. `state` and `questions` are
byte-identical. Asserted per case, not assumed: the body with `model` normalised
away compares **equal** to the frozen body with `model` normalised away for all
16/16 cases, or the process exits non-zero before any call. Per-case request
hashes (frozen and as-sent) are in `results/summary.json`.

**Transport.** `curl` per call, **one process per call**, **no connection reuse**
(`num_connects == 1` on every row, so the claim is checkable), same `-w %{json}`
phase template as followup-03, **N = 1 attempt, no retries** at any concurrency
level. A retry on exactly the failing cells would convert an N=1 observation into
a survivorship-biased one.

**Schedule** (mirrors followup-03 exactly; nothing tuned):

| phase | calls | label |
|---|---|---|
| route pre-flight | 1 | `route_probe` — excluded from statistics |
| warm-up (discarded) | 5 | `warmup` — excluded from statistics |
| warm grid, sequential, case-major | 16 × 12 = 192 | `warm`, block `direct1` |
| idle proxy, after ≥ 120 s idle | 3 | `idle` |
| concurrency, fixed 6-case × 2-rep block | 3 × 12 = 36 | `concurrency`, C ∈ {1,4,8} |
| interface probe (mixed noul+choice+score) | 1 | `interface_probe` — excluded |
| **total** | **238** | |

**Frozen-condition gate** — every phase exits non-zero without touching the
network unless all of:

- all four digests match (below);
- the 16 subset ids re-derive from the frozen `cases.ndjson` by followup-03's
  **own** `select_subset` rule and match the stored `subset.json`;
- all 16 request bodies equal their frozen body after `model` normalisation,
  with `state` and `questions` byte-identical;
- the F1 correction derives from `control.pair_id` and names exactly the ids
  `verification.md` §2 F1 names (delegated to followup-03's function);
- the local answer normaliser reproduces frozen `common.parse_jev` on **64/64**
  frozen rows before it is trusted on any new (multi-question) response;
- the credential source resolves.

Frozen inputs, all verified and **unmodified**:

| file | sha256 |
|---|---|
| `phase1/cases.ndjson` | `7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c` |
| `phase1/results/jev_raw.ndjson` | `e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc` |
| `followup-03-operational/subset.json` | `58b855acefbd7cda2c35ad39988c930acf39d54ec658d88a62b04585bc71b8d3` |
| `followup-03-operational/results/mimo_ops_raw.ndjson` | `40dbc56329dd2d5112cd92a14e9dddf7c5384356feaadd170e2b8ac575827cd8` |

The two followup-03 artefacts are read **read-only**; the MiMo comparison is made
against its frozen block `resume1` and **MiMo was not re-run**.

**Scoring.** Semantic scoring is **control only**, against the frozen ground
truth with the F1 correction applied by followup-03's own function. An
opportunity is one usable prediction on an **answerable control**
(`variant_kind == "base"`) case. An unanswerable case is never scored
correct/incorrect — answering at all on one is a different failure mode. Both
mechanisms score 108/108, so every throughput and cost-per-decision ratio is at
matched accuracy.

## Key handling

The credential is **`~/.secrets/typesafe.env`**, format
`export TYPESAFE_API_KEY=...`. A non-login process does not inherit it, so it is
**read at runtime** by the harness and never exported.

- The value is held **in memory only** and handed to `curl` on **STDIN** via
  `curl --config -`, so it appears in **neither argv** (where `/proc/*/cmdline`
  and shell history expose it) **nor any file**.
- **Only the source label** `secrets/typesafe.env#TYPESAFE_API_KEY` is ever
  written to an artefact. Every row carries `credential_source` and
  `secrets_recorded: false`.
- The value is **never printed, logged, persisted, committed, or interpolated
  into an error message.** A `file-scan` check for this repository should look
  for the *label* and for the literal `TYPESAFE_API_KEY` **name**, and should
  expect no key-shaped value in any tracked file.
- If the source does not resolve, the harness **exits non-zero**. It never shops
  for a credential that happens to work.

## Reproduce

All commands run from the repository root. Every phase is a separate,
restartable invocation; the appender refuses to double-count a call key, so a
re-run resumes rather than duplicating.

```bash
H=research/jev-bounded-judgment/phase1/followup-04-jev-direct/harness/run_ops_jev_direct.py

# 0. frozen-condition gate — no network touched if anything has drifted
python3 $H gate

# 1. measurement phases (in order). Each is idempotent/resumable.
python3 $H route                                   #  1 call  (pre-flight)
python3 $H warm                                    #  197 calls (5 discarded + 192)
python3 $H idle                                    # 120 s idle, then 3 calls
python3 $H concurrency                             # 36 calls (C=1,4,8)
python3 $H probe                                   #  1 call  (interface probe)

# 2. analysis — equivalence FIRST, before any comparative use
python3 $H equivalence      # -> results/equivalence.json
python3 $H summary          # -> results/summary.json

# 3. determinism check
python3 $H check            # PASS: summary reproduces from the same raw file
```

**These are the commands actually tested in this run**, in this order:
`gate` → `route` → `warm` → `idle` → `concurrency` → `probe` → `equivalence` →
`summary` → `check`. `check` exits 0.

For a long run, detach with a heartbeat rather than blocking a terminal:

```bash
nohup python3 $H warm > /tmp/opencode/jev-phase1/fu4-warm.log 2>&1 &
while kill -0 $! 2>/dev/null; do sleep 20; echo "warm: $(grep -c '"phase": "warm"' \
  research/jev-bounded-judgment/phase1/followup-04-jev-direct/results/jev_direct_raw.ndjson) rows"; done
```

`--reps` (default 12) and `--interval` (default 0.0) exist for a reduced block;
either deviation prints a loud label and the rows are marked
`reduced_reps` / `paced_interval_seconds` so they can never be confused with the
unpaced sequential figure. `--reps` above 12 is refused.

## Artefacts

| path | what |
|---|---|
| `harness/run_ops_jev_direct.py` | the whole harness: gate, measure, analyse, check |
| `results/jev_direct_raw.ndjson` | 238 rows, one per call, raw response verbatim, 0 typed errors |
| `results/equivalence.json` | direct `jev-1.13.0` vs frozen `jev-1.13-free` on the same 16 cases |
| `results/summary.json` | all measurements, machine-readable, reproducible from the raw file |
| `comparison.md` | the analysis, with ESTABLISHED / UNRESOLVED / SERVING-OR-PRICING-ARTEFACT classification |

Every row records: raw response verbatim, the full curl phase decomposition,
`http_status`, `bytes`, usage, parsed answers and typed errors, `block`,
`repeat`, `phase`, `concurrency`, `timestamp_utc`, the response `model` field
with its pin assertion, the request hash, the `credential_source` label, and
`secrets_recorded: false`. Failures are recorded as typed errors and never
re-sent.

## What was NOT measured

Stated so nothing above is over-read. See `comparison.md` §2 for the full table.

- Sustained multi-hour throughput; every figure is a short burst window.
- The rate-limit envelope — 0 × 429 in 238 calls, the published ceilings were
  never approached. HTTP 529 was never observed.
- Per-call cold start — the idle probe is a proxy only (n=3), on both mechanisms.
- Server-side queueing / batching / contention — not observable from the client.
- Concurrency above C=8.
- Probability **calibration** (only availability was measured) and the meaning
  of the `confidence` field (`0.5` on both probe answers — indistinguishable
  from a constant).
- The economics of the batched multi-question capability (§1.10 of
  `comparison.md`): one call was made, per-question latency is not observable
  from it.
- Behaviour across route or model version changes.
- **followup-03's free-tier Jev cells**, which stay UNRESOLVED.
- **The consolidated Phase-1 verdict**, which is out of scope by brief.
