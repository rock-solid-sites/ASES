# Followup-03 — operational comparison: Jev 1.13 (free) vs MiMo V2.6 Flash

*given roughly matched bounded-decision accuracy on the frozen corpus, does Jev provide a material LATENCY, THROUGHPUT, COST or OPERATIONAL advantage over MiMo V2.6 Flash?*

Issue #565. Analysis is deterministic: `python3 harness/analyze_ops.py --check` rebuilds this document from the raw NDJSON and asserts the two serialisations are byte-identical.

## Headline

**The comparison the brief asked for cannot be completed as a matched pair, and the reason is itself the finding.** Jev's free tier refused every call in this window, so the only Jev latency, token and stability evidence that exists comes from a different window measured with a different transport. MiMo was measured cleanly. What follows separates the two, and marks the Jev/MiMo ratios as cross-window rather than pretending they are matched.

| | MiMo V2.6 Flash | Jev 1.13 (free) |
|---|---|---|
| Calls attempted this window | 232 attempted / 223 usable | 0 usable (of 197 attempted) |
| Warm latency | measured | UNRESOLVED this window |
| Throughput | measured | UNRESOLVED this window |
| Concurrency scaling | measured | UNRESOLVED this window |
| Cost per call | $0.000026 | $0.00 |
| Cost per correct decision | $0.000045 | $0.00 |
| Correct decisions per dollar | 21,988.0 | **UNDEFINED at $0** |
| Availability under load | sustained | **exhausted inside 197 calls** |

## 1. ESTABLISHED — structural measurements

Tier-independent. Nothing in this section uses a price.

### 1.1 MiMo warm latency (this window, curl)

Rows: `mechanism=mimo_v26_flash AND phase=warm AND block='resume1' AND no typed_error AND a parseable label/score`. 183 of 192 available rows used (9 dropped as unusable).

| statistic | total time (ms) | time to first byte (ms) |
|---|---|---|
| n | 183 | 183 |
| mean | 5,972.52 | 201.85 |
| median | 4,035.47 | 198.49 |
| p90 | 12,473.07 | 215.28 |
| p95 | 15,955.57 | 220.85 |
| p99 | 27,609.55 | 254.32 |
| min | 1,217.15 | 189.36 |
| max | 60,607.85 | 299.89 |
| stdev | 6,402.99 | 12.49 |

Decomposition (mean share of total that is pure transport: **3.43%**):

| component | mean ms | median ms | p95 ms |
|---|---|---|---|
| transport (DNS+TCP+TLS) | 205.04 | 201.78 | 224.78 |
| service+transfer (starttransfer − connect) | 199.73 | 195.99 | 219.15 |

The transport share matters for interpretation: a large fraction of a MiMo call is network setup, not model work, so wall-clock latency overstates the model's own cost and a like-for-like comparison must either hold transport constant or subtract it.

#### 1.1a The brief's two components do not sum to the total — and the missing term is the largest one

Rows: `mechanism=mimo_v26_flash AND phase=warm AND block='resume1' AND no typed_error`, n=183.

| component | mean ms | share of total |
|---|---|---|
| setup before first byte (DNS+TCP+TLS) | 205.04 | 3.43% |
| **post-first-byte body wait (the residual)** | **5,770.67** | **96.62%** |
| total | 5,972.52 | 100% |

The brief's two components sum to 404.77 ms of a 5,972.52 ms call. This is the brief's transport + (starttransfer - connect). It is reported for fidelity to the design and it does NOT account for the total; the post-first-byte wait is the missing term and is the larger one. Reporting the brief's decomposition without this residual would attribute a call's cost to the wrong place.

**`time_starttransfer` is not a model signal here.** Time_starttransfer is within a few ms of TLS handshake completion and varies far less than the total, so the endpoint emits response headers before the model has produced anything. time_starttransfer is therefore NOT a time-to-first-token measurement and must not be read as model responsiveness. Measured: median first byte 198.49 ms against median TLS completion 198.29 ms, with a first-byte SD of 12.49 ms against a total SD of 6,402.99 ms. The only defensible client-observed latency figure is time_total.

Token count explains only part of the latency: Pearson r between total time and output tokens is **0.394**. A moderate correlation means token count explains part of the latency and leaves a large serving-side residual. A value near 1.0 would mean the endpoint simply streams at a fixed token rate; a value near 0 would mean latency is independent of the work done.

Repeating the **identical** request moves latency by between 3,630 ms and 59,209 ms across the 16 cases. Repeating the SAME request moves latency by this much, so a single-call latency figure is a sample from a wide distribution rather than a property of the request.

| case | n | min ms | median ms | max ms | range ms | max/min |
|---|---|---|---|---|---|---|
| a-dist1 | 12 | 1,680 | 4,229 | 8,465 | 6,785 | 5.04x |
| a-e01 | 12 | 1,365 | 2,436 | 4,995 | 3,630 | 3.66x |
| a-e02 | 12 | 1,290 | 2,212 | 6,392 | 5,102 | 4.96x |
| a-h04 | 12 | 1,751 | 2,699 | 8,264 | 6,513 | 4.72x |
| a-m07 | 12 | 1,638 | 4,084 | 13,699 | 12,062 | 8.37x |
| a-miss1 | 12 | 3,441 | 8,251 | 18,394 | 14,953 | 5.35x |
| a-noise1 | 12 | 2,307 | 3,235 | 8,690 | 6,382 | 3.77x |
| b-a01 | 12 | 1,362 | 3,326 | 27,610 | 26,248 | 20.28x |
| b-a02 | 12 | 1,398 | 3,022 | 60,608 | 59,209 | 43.34x |
| b-a03 | 3 | 8,544 | 15,767 | 26,539 | 17,995 | 3.11x |
| b-dist1 | 12 | 1,381 | 4,664 | 12,960 | 11,579 | 9.38x |
| c-p1a | 12 | 1,324 | 3,431 | 17,258 | 15,934 | 13.03x |
| c-p1b | 12 | 1,217 | 2,519 | 6,451 | 5,234 | 5.30x |
| d-01 | 12 | 2,983 | 5,173 | 12,263 | 9,280 | 4.11x |
| d-02 | 12 | 1,656 | 2,572 | 8,699 | 7,043 | 5.25x |
| d-03 | 12 | 2,647 | 5,531 | 17,407 | 14,760 | 6.58x |

This is the strongest operational finding on the MiMo side, and it cuts against using any single latency number: the endpoint's serving time for a fixed small request is dominated by variable queueing that the client cannot see or control. Report the distribution, not the mean.

### 1.2 MiMo sequential and concurrent throughput

Rows: `mechanism=mimo_v26_flash AND phase=warm AND block='resume1' AND no typed_error`. A strictly sequential client issues one call at a time, so elapsed time is the sum of per-call time_total; calls/sec is n_calls_usable / that sum. This EXCLUDES any client think-time and is an upper bound on the attainable rate.

- sequential: **0.167 calls/sec** (183 calls / 1,092.97 s of summed per-call time)
- including curl process spawn: 0.167 calls/sec
- correct control decisions/sec: **0.0988** (108 correct of 108 control opportunities)
- correct decisions/sec over the full answerable subset: 0.1208 (132 of 132)

| C | usable | failed | 429 | makespan (ms) | calls/sec | scaling vs C=1 | p50 latency ratio vs C=1 |
|---|---|---|---|---|---|---|---|
| 1 | 12 | 0 | 0 | 47,719 | 0.252 | 1.00x | 1.00x |
| 4 | 12 | 0 | 0 | 70,279 | 0.171 | 0.68x | 2.06x |
| 8 | 12 | 0 | 0 | 58,915 | 0.204 | 0.81x | 1.79x |

Scoring definition: throughput(C)/throughput(1). Ideal linear scaling at concurrency C would be C.

**Reading the curve: there is no client-side concurrency benefit.** Throughput does not rise with in-flight count; it FALLS from C=1 to C=4 and only partly recovers at C=8, while per-call median latency roughly doubles. No level returned a single 429 or any other error, so this is not a cap being hit -- it is added queueing cost at the service. The operational consequence is concrete: on this route, issuing calls concurrently makes the batch finish LONGER, so the sequential C=1 condition is both the simplest and the fastest measured option. Not tested: whether a different request mix (longer generations, different case sizes) or a sustained multi-hour load would cross over, and whether the service is queueing, batching or simply contended -- none of that is observable from the client.

### 1.2a MiMo idle-gap probe (cold-proxy)

Rows: `mechanism=mimo_v26_flash AND phase=idle AND block='resume1' AND no typed_error`. The client made NO call for 120s, then issued 3 calls.

| statistic | idle-gap probe (ms) | warm, same block (ms) |
|---|---|---|
| n | 3 | 183 |
| median | 3,357.02 | 4,035.47 |
| mean | 4,139.62 | 5,972.52 |
| min | 2,346.09 | 1,217.15 |
| max | 6,715.75 | 60,607.85 |

- idle-gap median / warm median = **0.8319x**
- idle-gap max / warm p95 = **0.42x**

**This probe found NO evidence of a cold-start penalty, and the reason it cannot claim one is the warm block's own spread.** The median after a 120s gap is not elevated -- it is slightly BELOW the warm median -- so there is no median-level penalty. The tempting reading is that the first call after the gap (6,715.75ms, 1.66x the warm median) is a cold start, and the next two calls returning to the warm range supports the shape of that story. But 6,715.75ms is only 0.42x the warm block's own p95 and well under its max (60,607.85ms): it sits INSIDE the ordinary warm latency range, so it cannot be distinguished from tail variance. The correct report is therefore 'not observed', not 'small'. This is an observable cold-ish PROXY only. Per-call cold start is NOT directly observable here: the endpoint is shared, any edge cache or connection-reuse state on the server side is unobserved, and the client opens a fresh connection per call by design. A difference here cannot be attributed to per-call model cold start. WHAT-NOT-TESTED: n=3 against a warm distribution whose p95 is ~4x its median and whose max is ~15x; a single 120s gap rather than minutes or hours; and the probe re-used cases already exercised by the warm block, so any per-case ordering effect is confounded with the gap. Detecting a real cold-start cost on this route would need either many more idle-gap samples or a warm block with a tight enough tail to resolve against -- the warm block here is too noisy to serve as that reference.

### 1.3 MiMo label stability

Rows: `mechanism=mimo_v26_flash AND phase=warm AND block='resume1' AND no typed_error`. Per case, (reps - modal_label_reps) / reps; 0 means the same label every rep, 1.0 would mean no label is modal.

- 16 cases x 183 warm observations
- mean flip rate: **0.0208**; max 0.3333
- cases stable on every rep: 15 of 16
- mean modal-label frequency: 0.9792

| case | type | reps | modal label | modal freq | distinct labels | flip rate | reasoning tokens mean (min–max) |
|---|---|---|---|---|---|---|---|
| a-dist1 | noul | 12 | no | 1.000 | 1 | 0.000 | 10.7 (2–16) |
| a-e01 | noul | 12 | yes | 1.000 | 1 | 0.000 | 16.5 (11–40) |
| a-e02 | noul | 12 | no | 1.000 | 1 | 0.000 | 9.4 (4–18) |
| a-h04 | score | 12 | low | 1.000 | 1 | 0.000 | 33.8 (25–63) |
| a-m07 | noul | 12 | no | 1.000 | 1 | 0.000 | 24.8 (20–35) |
| a-miss1 | noul | 12 | no | 1.000 | 1 | 0.000 | 68.9 (28–154) |
| a-noise1 | noul | 12 | no | 1.000 | 1 | 0.000 | 26.4 (19–40) |
| b-a01 | noul | 12 | yes | 1.000 | 1 | 0.000 | 58.6 (16–147) |
| b-a02 | noul | 12 | no | 1.000 | 1 | 0.000 | 27.4 (15–51) |
| b-a03 | noul | 3 | yes | 0.667 | 2 | 0.333 | 209.0 (187–224) |
| b-dist1 | noul | 12 | no | 1.000 | 1 | 0.000 | 24.8 (16–44) |
| c-p1a | noul | 12 | yes | 1.000 | 1 | 0.000 | 23.8 (17–53) |
| c-p1b | noul | 12 | no | 1.000 | 1 | 0.000 | 13.2 (5–18) |
| d-01 | choice | 12 | build | 1.000 | 1 | 0.000 | 16.3 (11–35) |
| d-02 | choice | 12 | redesign | 1.000 | 1 | 0.000 | 11.6 (8–19) |
| d-03 | choice | 12 | investigate | 1.000 | 1 | 0.000 | 16.4 (15–20) |

### 1.4 MiMo token use (including reasoning)

Rows: `mechanism=mimo_v26_flash AND block='resume1' AND phase IN ['warm', 'warmup', 'idle', 'concurrency'] AND no typed_error`. Tokens_per_call divides by n_calls, which INCLUDES warm-up calls when warmup_included_in_cost_total is true; set it false for a warm-only figure.

| token class | total | per call |
|---|---|---|
| cache_read_tokens | 0 | 0.00 |
| cache_write_tokens | 0 | 0.00 |
| input_tokens | 27,953 | 125.91 |
| output_tokens | 6,976 | 31.42 |
| reasoning_tokens | 6,286 | 28.32 |
| total_tokens | 34,929 | 157.34 |

### 1.5 The Jev free-tier cap — an operational property, not a price

Rows: `mechanism=jev AND block=null AND phase IN (warmup, warm)`. **197 calls, 0 usable, 0 tokens consumed.** Window 2026-09-26T06:34:53Z → 2026-09-26T06:36:35Z.

| segment | calls | HTTP status mix | window |
|---|---|---|---|
| before_first_429 | 125 | {'403': 125} | 2026-09-26T06:34:53Z → 2026-09-26T06:36:01Z |
| from_first_429_onward | 72 | {'429': 72} | 2026-09-26T06:36:02Z → 2026-09-26T06:36:35Z |

Reading: The 403 phase masks the cap behind an upstream parse error, so a client that only inspects http_status would read it as a server fault, not an entitlement wall. The 429 phase names it: FreeUsageLimitError.

This is the sharpest operational result in the study, and it is worth stating plainly: **a free tier that answers 403 for 125 consecutive calls and only then starts answering 429 is a serving policy, not a benchmark result.** A client that retries on 403 alone would have spent 125 calls learning nothing. The 429 body names the cause (`FreeUsageLimitError`); the 403 body does not.

### 1.6 Jev availability probes (bounded series)

Protocol: 10 probes maximum, >= 60s apart, 1 attempt each, 0 retries, stopping early on the first usable answer. probing a rate-limited endpoint more tightly, or retrying, would manufacture load and destroy the signal the series exists to measure.

Result: **10 probes, 0 usable answers**, 2026-09-26T13:09:42Z → 2026-09-26T13:19:11Z. HTTP status mix {'429': 10}; error types {'FreeUsageLimitError': 10}. Smallest observed gap 60.0s (floor respected: yes).

| # | UTC | gap (s) | case | HTTP | error type | usable |
|---|---|---|---|---|---|---|
| 1 | 2026-09-26T13:09:42Z | n/a | a-h04 | 429 | FreeUsageLimitError | no |
| 2 | 2026-09-26T13:10:42Z | 60.0 | d-01 | 429 | FreeUsageLimitError | no |
| 3 | 2026-09-26T13:12:07Z | 85.0 | a-miss1 | 429 | FreeUsageLimitError | no |
| 4 | 2026-09-26T13:13:08Z | 60.0 | b-dist1 | 429 | FreeUsageLimitError | no |
| 5 | 2026-09-26T13:14:08Z | 60.0 | b-a01 | 429 | FreeUsageLimitError | no |
| 6 | 2026-09-26T13:15:09Z | 60.0 | a-dist1 | 429 | FreeUsageLimitError | no |
| 7 | 2026-09-26T13:16:09Z | 60.0 | a-m07 | 429 | FreeUsageLimitError | no |
| 8 | 2026-09-26T13:17:10Z | 60.0 | a-noise1 | 429 | FreeUsageLimitError | no |
| 9 | 2026-09-26T13:18:11Z | 60.0 | a-e01 | 429 | FreeUsageLimitError | no |
| 10 | 2026-09-26T13:19:11Z | 60.0 | b-a02 | 429 | FreeUsageLimitError | no |

The series exhausted its budget without a single usable answer, so the paced reduced Jev block described in the brief was **not run**: its precondition never held. No Jev number in this document comes from a fabricated or estimated call.

### 1.7 All Jev evidence that exists (frozen window)

Source: `../results/jev_raw.ndjson` (64 usable of 64 rows), window 2026-09-26T02:46:53Z → 2026-09-26T02:47:30Z, transport python urllib (the frozen Phase-1 transport), NOT curl; the current window uses curl. Client-side process-spawn and curl-instrumented phase timings are therefore NOT available for these rows., tier state: free tier, inside quota at that time.

Used because: the current window produced zero usable Jev calls, so this is the only Jev latency/usage/stability evidence that exists. Using it is honest; treating it as current-window data would not be.

| statistic | latency (ms) |
|---|---|
| n | 64 |
| mean | 593.83 |
| median | 586.80 |
| p90 | 668.10 |
| p95 | 685.10 |
| p99 | 763.50 |
| min | 525.30 |
| max | 763.50 |
| stdev | 48.29 |

- input tokens per call: mean 353.9; output tokens per call: mean 29.4
- probability availability: noul scalar exposed on 0/0 noul calls; choice distribution on 0/0; score distribution on 0/0
- cost: $0.00 (free tier), with the same entitlement caveat as §1.5

**What this window cannot support:** curl phase decomposition (different transport), concurrency, idle/cold proxy, and a repeat-to-repeat stability rate (it holds one call per case, so a flip rate is not computable from it at all).

## 2. UNRESOLVED

Each item is a question this study could not answer. None is filled in by estimate.

- **jev_current_window_latency** — UNRESOLVED — 0 usable calls
- **jev_current_window_throughput** — UNRESOLVED — 0 usable calls
- **jev_current_window_concurrency** — UNRESOLVED — not attempted; issuing a concurrency block against an endpoint that has already refused 197 of 197 calls would have produced 12 more refusals, not a scaling curve
- **jev_current_window_idle_cold_proxy** — UNRESOLVED — not attempted
- **jev_current_window_stability** — UNRESOLVED in this window; the frozen window gives 1 call per case, so a repeat-to-repeat flip rate is NOT computable from it either
- **jev_current_window_curl_phase_decomposition** — UNRESOLVED — no usable curl response to decompose; only the rejection timings exist
- **jev_paced_reduced_block** — NOT RUN — its precondition (a probe returning a usable answer) never held
- **per_call_cold_start** — NOT DIRECTLY OBSERVABLE for either mechanism — an idle-gap proxy is all the design can see
- **server_side_queueing_or_batch_effects** — NOT OBSERVABLE from the client; the client cannot see whether the service batched or queued a request
- **sustained_multi_hour_throughput** — NOT MEASURED for either mechanism; every figure here is a short burst-window measurement
- **price_elasticity_or_paid_jev_tier** — NOT MEASURED — out of scope and not priced

The Jev side of the comparison is UNRESOLVED on every structural axis in this window. The single most consequential unknown is whether the cap is a hard entitlement wall or a burst allowance: 197 calls inside ~100 seconds exhausted it, but nothing here distinguishes "N calls per day" from "N calls per minute with a leaky bucket". That distinction decides whether Jev is operationally usable at all, and this design cannot make it.

## 3. SERVING-OR-PRICING ARTIFACT

Facts that look like results but are properties of a commercial arrangement rather than of either model.

1. **Jev's $0 price.** UNDEFINED at $0. Not 'infinite' and not 'best': the ratio has no value because its denominator is zero. The honest statement is the conditional one — while quota exists Jev costs $0 per call, and this study measured quota exhausting inside 197 calls.
2. **MiMo's rates.** PRICING/ENTITLEMENT FACT: input $0.14/Mtok, output $0.28/Mtok, cache read $0.0028/Mtok from the current catalog. Promotional and tier-dependent. These may be used to state a dollar cost. They may NOT be used to claim a latency or throughput advantage, and no such claim appears above.
3. **Matched-error comparison.** A matched-error comparison requires a per-dollar or per-latency figure at the SAME observed error level. Jev's error level in this window is undefined in the operational sense: 0 of 197 calls returned an answer, so its decision error rate is not measurable at all. No matched-error ratio is therefore reported, and none should be inferred from Jev's $0 cost.
4. **The 403→429 transition itself.** The 403 phase is a serving policy (error masking); the 429 phase is an entitlement wall. Neither is a property of Jev's reasoning. Any 'Jev is slow/unreliable' reading taken from this window is reading the free tier, not the model.
5. **Network/transport overhead.** The connect-only probe is a property of the path and the CDN edge, not of either model (A difference here is a property of the network path and the CDN edge, NOT of either model, and cannot be attributed to Jev or to MiMo.).

### Cost, stated with its denominator

- MiMo per call: **$0.000026** over 222 calls
- MiMo per correct CONTROL decision: **$0.000045** over 108 correct control decisions in the warm block
- MiMo correct decisions per dollar: **21,988.0** (reciprocal of the line above; promotional rates)
- Jev per call: **$0.00**; per correct decision: **$0.00**; per dollar: **UNDEFINED**
- MiMo control error rate this window: 0.0000 over 108 usable predictions on ANSWERABLE control (variant_kind=base) subset cases in the warm block

### Cross-window ratios (flagged, not matched)

MIMO figures are from THIS window (curl, block=resume1). Jev figures are from the FROZEN window (python urllib, 02:46-02:50Z) because this window produced no usable Jev call. Every Jev/MiMo ratio below is therefore a CROSS-WINDOW ratio across two transports and two tier states. It is reported because it is the only Jev evidence that exists, and flagged because it is not a matched pair.

- `tokens_per_call_input_ratio_jev_over_mimo` = **2.811**
- `tokens_per_call_output_ratio_jev_over_mimo` = **0.936**
- `warm_median_latency_ratio_jev_over_mimo` = **0.145**

Denominators:
- jev: n=64 frozen calls, median over 1-second-rounded latency_ms
- mimo: n=183 warm calls in block=resume1

## 4. Probability distributions — interface probe

**MiMo.** the frozen request shape does not request logprobs, so a null probabilities field under frozen conditions is a property of the REQUEST, not proof the API cannot return probabilities. The labelled interface probe is what tests the latter. Probe rows: 1; reasoning content exposed on 234 usable calls.
  - `a-miss1`: HTTP 200, logprobs requested=['logprobs', 'max_tokens', 'messages', 'model', 'temperature'], logprobs present in response=no

**Jev.** Jev's distribution availability is read from the FROZEN responses (see frozen_jev_window.probability_availability) rather than from new calls: a noul question returns the scalar `noul` and choice/score return full distributions, so a new probe call would have added cost and rate-limit pressure for no new information. In the frozen window Jev returns the scalar `noul` for noul questions and full distributions for choice and score — see §1.7. That is a genuine interface difference and the one operational advantage this study can point at with evidence, because it is a property of the response schema rather than of price or quota.

## 5. Failures and retries

N = 1 attempt per call, 0 retries, everywhere, by design. A retry would make an availability failure invisible, so it is not permitted in a measurement phase.

| mechanism | phase | rows | typed errors | HTTP status mix | retries |
|---|---|---|---|---|---|
| Jev | warm | 192 | 192 | {'403': 120, '429': 72} | 0 |
| Jev | warmup | 5 | 5 | {'403': 5} | 0 |
| MiMo | concurrency | 36 | 0 | {'200': 36} | 0 |
| MiMo | idle | 3 | 0 | {'200': 3} | 0 |
| MiMo | interface_probe | 1 | 0 | {'200': 1} | 0 |
| MiMo | warm | 198 | 9 | {'200': 198} | 0 |
| MiMo | warmup | 5 | 0 | {'200': 5} | 0 |

## 6. Row selection — which rows every statistic used

| mechanism | file | rows | blocks | phases |
|---|---|---|---|---|
| jev | `results/jev_ops_raw.ndjson` | 197 | {'None': 197} | {'warm': 192, 'warmup': 5} |
| mimo_v26_flash | `results/mimo_ops_raw.ndjson` | 243 | {'None': 11, 'resume1': 232} | {'concurrency': 36, 'idle': 3, 'interface_probe': 1, 'warm': 198, 'warmup': 5} |

Measurement block: `resume1`. the aborted first attempt, retained verbatim; excluded from warm statistics and reported separately under jev.free_tier_cap and mimo.aborted_first_block

Frozen inputs re-verified at analysis time: `cases.ndjson` (match), `results/jev_raw.ndjson` (match).

## 7. Honest summary of the comparison

- **ESTABLISHED:** MiMo's latency distribution, throughput at C=1/4/8, label stability, token use including reasoning, and derived cost, all under frozen conditions with one attempt per call and zero retries.
- **ESTABLISHED:** the Jev free tier is not merely slower or costlier than a paid tier — it is unavailable under sustained sequential load, exhausting inside 197 calls in ~100 seconds, and it masks that exhaustion behind 125 consecutive 403s before it will name it.
- **ESTABLISHED:** Jev's response interface exposes probabilities (scalar for noul, full distributions for choice/score) where MiMo's frozen request shape exposes none. This is an interface fact, and its operational value is real and independent of price.
- **UNRESOLVED:** every Jev structural metric in this window, and therefore any matched Jev-vs-MiMo latency, throughput or concurrency claim.
- **ARTIFACT:** Jev's $0 per-call cost. It is not an advantage that can be divided by; it is a promotional entitlement that this study watched exhaust. Whether Jev is cheaper in any decision-relevant sense depends entirely on a quota whose size is unpublished and whose rate this study could not measure.

