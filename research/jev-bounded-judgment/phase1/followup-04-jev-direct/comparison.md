# followup-04 — Jev over the direct TypeSafe API, compared with the frozen MiMo measurements

**Question this document answers.** At approximately matched semantic capability,
does direct Jev (`jev-1.13.0`) materially improve latency, tail latency,
throughput, reliability, probability availability, or cost relative to MiMo
V2.6 Flash (frozen followup-03 measurements)?

**What this document does NOT do.** It does not produce the consolidated
Phase-1 verdict. It resolves the Jev side of followup-03's open item and
compares. The verdict is the orchestrator's to draw from the whole evidence
set, not this follow-up's to assert.

**Why this is not a rerun of followup-03's Jev route.** followup-03 measured
`jev-1.13-free` over `https://opencode.ai/zen/v1/systemone` and obtained **zero
usable answers**, so its Jev latency, throughput, concurrency and stability
cells are recorded UNRESOLVED. This run changes the route and the model tag:

| | followup-03 (frozen, UNRESOLVED) | this run |
|---|---|---|
| endpoint | `https://opencode.ai/zen/v1/systemone` | `https://api.typesafe.ai/v1/systemone` |
| model | `jev-1.13-free` | `jev-1.13.0` (pinned) |
| price | free tier, $0 | $0.042 per Mtok input, output free |
| usable answers | 0 of 197 | **238 of 238** |

So these are **new observations of a new path**. They do **not** retroactively
fill followup-03's UNRESOLVED cells: those were properties of the free-tier
route, and a different route cannot be used to complete them.

---

## 0. Conditions, and the cross-window caveat

**CROSS-WINDOW COMPARISON.** MiMo was measured in followup-03 block `resume1`
at roughly 2026-09-26T13:09Z–13:33Z. Jev-direct was measured in this run's
window. Same host, same `curl` transport, same 16-case subset, same scoring
function — **different time window, and for Jev a different route**. Any
difference below therefore mixes three separable causes, and the tables keep
them apart:

1. **STRUCTURAL** — a property of the model/endpoint behaviour (latency,
   tokens, throughput, stability, distribution availability).
2. **NETWORK TRANSPORT** — a property of the path (DNS/TCP/TLS, first byte).
   Not attributable to either model.
3. **PRICING / SERVING ARTEFACT** — a property of the tariff or of the
   measurement plumbing, not of capability.

**Semantic capability is matched, and this was verified before any comparison
was used** (`results/equivalence.json`). Against the frozen `jev-1.13-free`
rows on the same 16 cases, direct `jev-1.13.0` gives:

| equivalence check | result |
|---|---|
| cases whose label matches the frozen row | **16 / 16** (rate 1.0) |
| cases with any answer change | **0** |
| cases label-unstable across the 12 warm reps | **0** |
| `noul` worst-case max abs drift | **0.04** (median of case medians 0.01) |
| `choice`/`score` overall max abs probability delta | **0.01** (median of case medians 0.00) |

**No equivalence is claimed.** What is reported is measured agreement plus
measured drift between two different model tags on two different routes, and
the direct side's own repeat stability. The licence it gives is narrow and
sufficient: the direct route answers the frozen corpus the same way the frozen
Jev run did, so "approximately matched semantic capability" holds and an
operational comparison is meaningful. It does not license any claim that the
two routes are interchangeable in production.

**Both mechanisms scored identically.** Control-only scoring, frozen ground
truth, F1 correction applied by followup-03's own function:

| scoring | Jev direct | MiMo frozen |
|---|---|---|
| control correct / opportunities | **108 / 108** | 108 / 108 |
| control error rate | **0.0** | 0.0 |
| all-subset correct / opportunities | **132 / 132** | 132 / 132 |

Both are at ceiling on this subset, so **every throughput and cost-per-decision
ratio below is a ratio at matched accuracy, not an accuracy-disguised
speedup.**

---

## 1. ESTABLISHED

Each item states WHAT, WHY, HOW CERTAIN, and WHAT-NOT-TESTED.

### 1.1 Latency — direct Jev is an order of magnitude faster, and its tail is flat

Rows: Jev `phase=warm AND block=direct1 AND usable` (n=192); MiMo frozen
`block=resume1` (n=183). `time_total`, the only defensible client-observed
latency figure on either route (§1.3).

| statistic | Jev direct (ms) | MiMo frozen (ms) | Jev / MiMo | speed-up |
|---|---|---|---|---|
| n | 192 | 183 | | |
| mean | 304.33 | 5,972.52 | 0.051 | 19.6x |
| **median** | **304.91** | **4,035.47** | **0.076** | **13.2x** |
| p90 | 333.83 | 12,473.07 | 0.027 | 37.4x |
| **p95** | **345.67** | **15,955.57** | **0.022** | **46.2x** |
| **p99** | **389.98** | **27,609.55** | **0.014** | **70.8x** |
| min | 254.26 | 1,217.15 | 0.209 | 4.8x |
| max | 400.75 | 60,607.85 | 0.007 | 151.2x |
| stdev | 23.56 | 6,402.99 | 0.004 | 271.8x |

**The tail result matters more than the median.** Expressing tail as a multiple
of each route's own median:

| tail shape | Jev direct | MiMo frozen |
|---|---|---|
| p99 / median | **1.28x** | 6.84x |
| max / median | **1.31x** | 15.02x |

Jev's worst call in 192 is 1.31x its typical call. MiMo's worst was 15x its
typical. followup-03's strongest operational finding on MiMo — that a fixed
small request is dominated by variable queueing the client cannot see or
control, so a single-call latency figure is a sample from a wide distribution
— **does not reproduce on the direct Jev route**. The Jev distribution is tight
enough that the median is a usable summary statistic, which it demonstrably was
not for MiMo.

**WHY:** the Jev latency distribution is bounded (254–401 ms over 192 calls)
while MiMo's spans two orders of magnitude (1.2–60.6 s).
**HOW CERTAIN:** evidence-based (n=192, 12 reps × 16 cases, cross-window,
single host, single burst window).
**WHAT-NOT-TESTED:** sustained multi-hour load; load from a different network
or region; behaviour under contention the client did not generate; whether the
bound is a property of the endpoint or of the empty queue it was measured in.

### 1.2 Latency is nearly independent of the work done — a different serving shape

| correlation | Jev direct | MiMo frozen |
|---|---|---|
| Pearson r(`time_total`, output tokens) | **−0.0125** | 0.394 |

On MiMo, token count explains a moderate part of the latency and leaves a large
serving-side residual. On the direct Jev route the correlation is
indistinguishable from zero: **latency is a near-fixed cost that does not scale
with how much the model emits.** This is consistent with a non-streaming
bounded-decision endpoint that returns a small fixed-shape answer (output
median 20 tokens, max 69) after a roughly constant serving cost, and it is the
mechanism behind the flat tail in §1.1.

**WHY:** an r of ~0 means latency is independent of work done; r near 1 would
mean fixed-rate streaming.
**HOW CERTAIN:** evidence-based (n=192).
**WHAT-NOT-TESTED:** whether the independence holds for longer generations.
The whole measured output range is 17–69 tokens, so the correlation is
established only over that narrow range and **must not be extrapolated** to
long-form output. This is a real limit on the finding.

### 1.3 `time_starttransfer` is NOT a model signal on this endpoint

Required by the brief, stated explicitly:

| | Jev direct | MiMo frozen |
|---|---|---|
| mean first byte (`time_starttransfer`) | 53.41 ms | 201.85 ms |
| mean transport setup (`time_appconnect`) | 53.21 ms | 201.64 ms |
| first byte − transport setup | **+0.20 ms** | **+0.20 ms** |
| mean total | 304.33 ms | 5,972.52 ms |
| mean post-first-byte residual | 250.92 ms | 5,770.87 ms |
| post-first-byte share of total | **82.45%** | 96.62% |
| first-byte stdev | 3.82 ms | 12.49 ms |
| total stdev | 23.56 ms | 6,402.99 ms |

**Answer: `time_starttransfer` tracks only header/TLS completion. It is not a
time-to-first-token measurement on this endpoint and must not be read as model
responsiveness.** The first byte lands 0.20 ms after the TLS handshake
completes — the endpoint emits response headers before the model has produced
anything — while 82.45% of the call is spent in the post-first-byte body wait.
The variance ratio makes the same point: first-byte stdev is 3.82 ms against a
total stdev of 23.56 ms, so the first byte is nearly constant while the total
is not.

This **independently reproduces** followup-03's finding for MiMo, on a different
host and a different provider. Two unrelated endpoints behaving the same way
here is a property of non-streaming JSON endpoints, not of either model.

**Consequence for the tables above:** only `time_total` appears in any latency
comparison. Reporting a "time to first byte" column for these two mechanisms
side by side would compare TLS handshakes and call it model latency.

### 1.4 Network transport — a real but arithmetically inverted difference

curl's `-w` phase timings are **cumulative from transfer start**, verified
strictly monotonic on all 192 Jev and all 183 MiMo rows
(`namelookup ≤ connect ≤ appconnect ≤ pretransfer ≤ starttransfer ≤ total`).
Transport setup is therefore `time_appconnect` **alone**; the sum
`namelookup + connect + appconnect` that followup-03 used double-counts. The
`time_appconnect`-alone figures are used throughout this document (see §3.9
for the correction and its size).

| component | Jev direct | MiMo frozen |
|---|---|---|
| mean DNS (`time_namelookup`) | 1.05 ms | 1.28 ms |
| mean TCP connect complete (`time_connect`) | 1.91 ms | 2.12 ms |
| **transport setup = `time_appconnect`** (mean) | **53.21 ms** | **201.64 ms** |
| transport setup (median) | 52.28 ms | 198.29 ms |
| transport share of total (mean) | **17.48%** | **3.38%** |
| post-first-byte residual (mean) | 250.92 ms | 5,770.87 ms |
| model-attributable residual = total − transport (mean) | **251.12 ms** | **5,770.87 ms** |

**Read these two facts together, or you will read the wrong story.** Jev's
transport is *faster in absolute terms* — a 52.28 ms median setup versus
198.29 ms, a 3.8x improvement, consistent with a closer or warmer edge. But its
transport is a **larger share** of the call (17.48% versus 3.38%) purely
because the denominator shrank: the same handshake is a bigger fraction of a
304 ms call than of a 5,972 ms call. **The rising share is an arithmetic
consequence of the model-side speed-up, not a transport regression.**

**WHY it is kept separate: a difference here is a property of the network path
and the CDN edge, NOT of either model.** For a like-for-like model comparison,
transport must be held constant or subtracted. Subtracting mean transport from
the mean total leaves a model-attributable residual of **251.12 ms for Jev vs
5,770.87 ms for MiMo** — a **23.0x** ratio, slightly larger than the 19.6x raw
ratio, i.e. the transport advantage slightly *understates* the model-side gap.
**HOW CERTAIN:** evidence-based. **WHAT-NOT-TESTED:** no followup-03 transport
probe was re-run; MiMo's transport figures are its own window's; a different
time of day could reorder the two edges.

### 1.5 Sequential throughput — 19.6x at matched accuracy

| | Jev direct | MiMo frozen | ratio |
|---|---|---|---|
| sequential calls/sec | **3.2859** | 0.1674 | **19.63x** |
| incl. curl process spawn | 3.1592 | 0.1670 | 18.92x |
| **correct control decisions/sec** | **1.8483** | 0.0988 | **18.71x** |
| control correct / opportunities | 108 / 108 | 108 / 108 | — |
| control error rate | 0.0 | 0.0 | — |

A strictly sequential client issues one call at a time, so elapsed time is the
sum of per-call `time_total`; this **excludes client think-time and is an upper
bound** on the attainable rate. Because both mechanisms score 108/108 on
control, the correct-decisions/sec ratio is a pure throughput ratio at matched
accuracy.

### 1.6 Concurrency — flat on Jev, degrading on MiMo

Fixed block of 6 cases × 2 reps = 12 calls per level, real in-flight limit, no
retries.

| C | Jev makespan (ms) | Jev calls/sec | Jev p50 (ms) | Jev p95 (ms) | Jev scaling | MiMo calls/sec | MiMo scaling | MiMo p50 (ms) |
|---|---|---|---|---|---|---|---|---|
| 1 | 3,878.3 | 3.0941 | 302.43 | 363.78 | 1.00x | 0.2515 | 1.00x | 2,758.93 |
| 4 | 3,720.2 | 3.2256 | 297.83 | 340.57 | **1.04x** | 0.1707 | **0.68x** | 5,681.48 |
| 8 | 3,824.5 | 3.1377 | 304.01 | 356.21 | **1.01x** | 0.2037 | **0.81x** | 4,951.27 |

All levels: **12/12 usable, 0 HTTP 429, 0 HTTP 529 on both mechanisms.**

Ideal linear scaling at concurrency C would be C. Neither route approaches it.
The difference is in the *sign* of the deviation:

- **Jev: 1.00x → 1.04x → 1.01x.** Throughput is flat and per-call latency does
  not move (p50 302.4 → 297.8 → 304.0 ms). Raising concurrency neither helps
  nor hurts. No queueing cost is observable.
- **MiMo: 1.00x → 0.68x → 0.81x.** Throughput *falls* 32% at C=4 while p50
  latency roughly doubles. followup-03's conclusion — on that route, issuing
  calls concurrently makes the batch finish **longer** — reproduces exactly,
  and its operational consequence (use C=1) stands for MiMo.

**The operational consequence for Jev is different in kind:** concurrency is a
free option, not a trap. It is also an option that buys nothing here, because
C=1 is already at the endpoint's apparent service rate.

**HOW CERTAIN:** evidence-based, but **n=12 calls per level** — a small block.
**WHAT-NOT-TESTED:** whether the flat curve holds at C=16/32/64; whether the
published ceilings (250k tok/s, 1,200 req/min) bind at any reachable
concurrency; 529 overload behaviour (never observed on either route); sustained
load. **A flat curve over C=1..8 is consistent with a hard per-request service
rate and does not prove the endpoint can absorb 8× sustained load.**

### 1.7 Reliability — 238/238 on Jev, 183/192 on MiMo

| | Jev direct | MiMo frozen |
|---|---|---|
| rows total | **238** | 243 (grid) |
| typed errors, all rows | **0** | — |
| warm usable / emitted | **192 / 192 (100%)** | 183 / 192 (**95.31%**) |
| HTTP 429, all rows | **0** | 0 |
| HTTP 529, all rows | **0** | 0 |
| attempts per call | 1 | 1 |
| retries | 0 | 0 |

MiMo's 9 unusable warm calls are **all case `b-a03`**, all
`typed_error=empty_content`, all **HTTP 200** with
`finish_reason: "length"` and `content: null` — the model consumed its
`max_tokens` on reasoning content and returned no answer. That is 9 of 12
reps of `b-a03` failing (75% of that case) and 0 failures on the other 15
cases. It is a **silent** failure: the status code says success.

**Jev produced no empty answers, no parse errors, and no rate-limit responses
in 238 calls.** Note the narrowness of that claim: it is one burst window on
one host against a service that was nowhere near its published ceilings, so it
bounds the *observed* failure rate at 0/238 and does not bound the tail
failure rate of a production deployment.

**N = 1 attempt, no retries at any level.** A retry on exactly the failing
cells would convert an N=1 observation into a survivorship-biased one, so the
9 MiMo failures are reported as failures and never re-sent.

### 1.8 Repeat stability — no label flips on Jev, 15/16 on MiMo

| | Jev direct | MiMo frozen |
|---|---|---|
| cases fully label-stable | **16 / 16** | 15 / 16 |
| mean flip rate | **0.0** | 0.0208 |
| max flip rate | **0.0** | 0.3333 |
| median over cases of max-prob spread | **0.01** | — |
| max over cases of max-prob spread | **0.03** | — |

Repeating the **identical** request 12 times, Jev-direct returned the same
label on all 12 reps for all 16 cases, with a maximum probability spread of
0.03 across all cases. Combined with §0 (agreement with the frozen row on
16/16), the direct route is **deterministic on this corpus at this
temperature**, and its only non-determinism is in the third decimal of a
probability.

This is the operational property that most changes the picture: a bounded
decision whose label does not move across 12 identical retries can be cached,
retried, and reasoned about, which a 2% mean flip rate cannot support.

**HOW CERTAIN:** evidence-based (n=192 over 16 cases).
**WHAT-NOT-TESTED:** determinism was not tested across days, across route/model
version changes, or at any other temperature; the frozen `common.post_json`
path recorded `temperature: 0` in the inherited conditions for the *general*
builder, and the Jev `systemone` body carries no temperature field at all, so
determinism here is the endpoint's own behaviour and may not survive a backend
change.

### 1.9 Probability availability — a genuine structural difference, with a correction

This is the one dimension where a naive reading of followup-03 would be wrong,
so the correction is stated first.

| | Jev direct | MiMo frozen |
|---|---|---|
| usable calls | 192 | 183 |
| **model-provided** probability distribution | **192 / 192 (100%)** | **0 / 183 (0%)** |
| `logprobs` present in the response body | n/a (not the mechanism) | **null in all 183** |
| explicit `logprobs: true` interface probe | n/a | **`logprobs_present_in_response: false`** |
| reported `confidence` field | **48 / 192** (all choice + score calls) | 0 |
| confidence recomputable from the distribution | **192 / 192** | 0 (no distribution) |
| `score` cases returning a full labelled distribution | 12 / 12 | 0 |

**CORRECTION to followup-03's `probabilities_exposed_under_frozen_conditions: 234`.**
That figure counts rows where the harness's `parsed_probabilities` field was
non-null. For MiMo those values are **one-hot vectors synthesised by the frozen
regex parser from the scraped label** — e.g. `{"no": 1.0, "yes": 0.0}` for every
one of its 97 `no` answers. They are a **harness artefact, not a model
capability**, and the count of 234 overstates what MiMo returned. The honest
figure is **0 model-provided probabilities**, corroborated independently by the
`logprobs` field being null in all 183 responses and by followup-03's own
labelled probe failing to obtain them with `logprobs: true`.

Jev-direct's distributions, by contrast, are **returned by the endpoint**:

- `noul` — a scalar `noul` ∈ [0,1], expanded to {yes, no} by the parser
  (144 calls, 12 cases);
- `choice` — a full 6-way distribution over the option keys (36 calls,
  3 cases);
- `score` — a 3-label distribution plus a `legend` mapping indices to labels
  (12 calls, 1 case);
- a reported `confidence` field on every `choice` and `score` call (48/192).

**This is a capability difference, not a pricing or serving artefact.** It is
also the difference that changes what the EDASES use case can ask for: a
calibrated probability per option is available from Jev-direct and is not
available from MiMo on this route at all.

**HOW CERTAIN:** evidence-based for the Jev side (192 calls plus the
interface probe). **Evidence-based via a frozen artefact** for the MiMo side
(followup-03's raw responses and probe row, re-read here read-only).
**WHAT-NOT-TESTED:** whether MiMo would return probabilities under a different
`logprobs` shape, a different endpoint, or a different model in its family;
whether Jev's probabilities are calibrated (this study measures availability,
never calibration); whether the `confidence` field is meaningful or a constant
(it was `0.5` on both probe answers, which is **not** enough evidence that it
carries information — flagged, not interpreted).

### 1.10 Interface probe — a capability neither comparison route was tested for

One labelled call, outside the grid; its latency and cost are in no statistic
and no answer is scored.

The direct route **accepted a multi-key `questions` object and answered all
three types in a single response**:

```json
{"model":"jev-1.13.0","answers":{
  "noul":{"type":"noul","noul":0.28},
  "choice":{"type":"choice","choice":"review","confidence":0.5,
            "probabilities":{"review":0.59,"build":0.0,"investigate":0.37,
                             "redesign":0.01,"repair":0.02,"escalate":0.01}},
  "score":{"type":"score","score":0.97,"confidence":0.5,
           "legend":{"0":"low","1":"medium","2":"high"},
           "probabilities":{"0":0.18,"1":0.67,"2":0.15}}},
 "usage":{"input_tokens":523,"output_tokens":97}}
```

**Batching several bounded decisions into one call** is a capability the frozen
Jev free-tier route was never tested for (it sent a single `q` key) and that
MiMo was never tested for. It is therefore **not a comparison** — it is a new
capability observation, and its practical value (fewer round trips, one
distribution per question) is **unquantified**: one call was made, and the
per-question latency split is not observable from a single batched response.

**Not scored:** the three questions came from three different states, so no
answer here is correct or incorrect by construction. The local answer
normaliser used for this row was proved equal to the frozen `common.parse_jev`
on 64/64 frozen rows before it was trusted here.

### 1.11 Cost — 1.78x cheaper per call, and it is a PRICING result, not an efficiency result

Warm-only figures, like-for-like (both excluding warm-up calls):

| | Jev direct | MiMo frozen | ratio |
|---|---|---|---|
| derived USD per call | **$1.5057e-05** | $2.6840e-05 | **0.561 (1.78x cheaper)** |
| derived USD per correct control decision | **$2.6768e-05** | $4.5479e-05 | **0.589 (1.70x cheaper)** |
| correct control decisions per dollar | **37,358.0** | 21,988.0 | **1.699** |
| input tokens per call | 358.50 | 125.91 | **2.85x MORE** |
| output tokens per call | 28.75 | 31.42 | 0.91x |
| whole-run derived cost (238 calls) | **$0.00356** | — | — |

**Jev uses 2.85x MORE input tokens per call than MiMo and is still 1.78x
cheaper.** The entire cost advantage is tariff arithmetic:

| | input $/Mtok | output $/Mtok |
|---|---|---|
| `jev-1.13.0` (direct) | **0.042** | **0.00 (free)** |
| `mimo-v2.6-flash` | 0.14 | 0.28 |
| frozen `jev-1.13-free` route | 0.00 | 0.00 |

Jev's 2.85x input-token disadvantage is more than offset by a 3.33x cheaper
input rate and a free output rate. **This is a PRICING AND ENTITLEMENT FACT,
promotional and tier-dependent — not a structural property of either model, and
not a token-efficiency result.** It could invert entirely on a different tariff.

**Two consequences that must not be skipped:**

1. **The frozen Jev route cost $0 and this one does not.** followup-03's cost
   ratio for Jev was *undefined* (division by zero at $0, with quota exhausting
   inside 197 calls). This run supplies the first **measured, non-zero** Jev
   cost. Any statement that "Jev is free" is now false for the direct route.
2. **The per-dollar comparison is at n=192 with a thin absolute base.**
   $0.00356 total derived cost is far below any rounding threshold that would
   matter commercially, so the *ordering* is robust and the *ratio* (1.70x)
   should not be quoted to three significant figures as a planning number.

---

## 2. UNRESOLVED

Not measured, or not observable, and not to be inferred from anything above.

| item | status | why it stays unresolved |
|---|---|---|
| Sustained multi-hour throughput | **NOT MEASURED** | every figure is a short burst window. §1.6's flat C=1..8 curve does not establish sustained capacity. |
| Rate-limit envelope | **NOT TESTED** | the published ceilings (250,000 tok/s, 1,200 req/min) were never approached — 0 × 429 in 238 calls. Nothing here speaks to where the ceiling binds or how 429/529 behave under load. |
| HTTP 529 (overloaded) behaviour | **NEVER OBSERVED** | the endpoint was never overloaded, so the documented 529 path is untested. |
| Per-call cold start | **NOT DIRECTLY OBSERVABLE** | a shared stateless HTTPS endpoint; the idle probe is a proxy only (§3). |
| Server-side queueing / batching / contention | **NOT OBSERVABLE from the client** | the client cannot see whether the service batches, queues, or contends. §1.6's flat curve is consistent with a fixed service rate but does not identify the mechanism. |
| followup-03's free-tier Jev cells | **NOT FILLED** | 0 of 197 answers on that route remains a fact about that route. A different route cannot complete those cells. |
| Concurrency above C=8 | **NOT TESTED** | §1.6 covers C ∈ {1,4,8} only. |
| Probability **calibration** | **NOT MEASURED** | §1.9 measures availability. Whether Jev's probabilities are calibrated is a different experiment and is untested. |
| Meaning of the `confidence` field | **INSUFFICIENT EVIDENCE** | `0.5` on both probe answers. Cannot be distinguished from a constant. |
| Batched multi-question economics | **UNQUANTIFIED** | §1.10 is one call. Per-question latency, throughput gain, and cost of batching are all unmeasured. |
| Behaviour across route / model version changes | **UNTESTED** | §1.8's determinism and §0's agreement are both properties of `jev-1.13.0` as served in this window. |
| Consolidated Phase-1 verdict | **OUT OF SCOPE** | by brief. Not produced here. |
| Idle-gap proxy, direct Jev | **MEASURED, 3 calls** | idle median 279.60 ms vs warm median 304.91 ms (ratio 0.917). n=3; a 3-sample percentile is thin, and this is a proxy for cold start, not an observation of it. |

---

## 3. SERVING-OR-PRICING ARTEFACTS

Things that look like findings and are not. Each is separated out so a later
reader does not re-derive a capability claim from it.

1. **`time_starttransfer` is not model latency, on either route.** First byte
   lands 0.20 ms after TLS completion on Jev, −3.19 ms on MiMo, while 82% /
   97% of each call is a post-first-byte body wait (§1.3). A "TTFB" column
   comparing these two mechanisms would be comparing handshakes.
2. **Jev's transport *share* rising to 17.48% is not a transport regression.**
   The absolute handshake is 3.8x faster than MiMo's; the share rises only
   because the total shrank (§1.4). The two facts must be read together.
3. **Jev's cost advantage is a tariff, not token efficiency.** Jev uses 2.85x
   more input tokens and is still cheaper purely because $0.042/$0.00 beats
   $0.14/$0.28 (§1.11). Both are promotional, tier-dependent facts.
4. **followup-03's `probabilities_exposed_under_frozen_conditions: 234` is a
   parser artefact.** Those are one-hot vectors built by the frozen regex
   parser from a scraped label, not model output. The defensible MiMo figure
   is 0 (§1.9). *This correction is to a frozen followup-03 summary figure; the
   frozen artefacts themselves are unmodified and were read read-only.*
5. **The interface probe's answers are not scored** and support no accuracy
   claim (§1.10). The three questions came from three different states.
6. **`x-opencode-session` header semantics on the new host are unestablished.**
   The frozen header set was retained for request fidelity; the header is a
   provider grouping header, not a credential, and whether it does anything on
   `api.typesafe.ai` is unknown. It is recorded on every row.
7. **The idle probe is a proxy, not a cold-start measurement** — on both
   mechanisms (§2).
8. **Cross-window, single-host.** MiMo at ~13:09Z–13:33Z, Jev-direct later the
   same day. A different time of day, network, or host load could move the
   network components (§1.4) and cannot be separated from the model components
   with one window each.
9. **followup-03's transport-share figure double-counts.** curl's `-w` phase
   timings are cumulative from transfer start — verified strictly monotonic on
   all 192 Jev and all 183 MiMo rows — so
   `transport = namelookup + connect + appconnect`, which followup-03 used,
   adds three overlapping intervals. The correct transport is `time_appconnect`
   alone. The size of the error is small and it does not change any conclusion:

   | | followup-03 reported | corrected (`appconnect` alone) | error |
   |---|---|---|---|
   | MiMo mean transport | 205.04 ms | **201.64 ms** | +1.7% |
   | MiMo transport share of total | 3.4331% | **3.3771%** | +0.06 pp |
   | MiMo mean model-attributable residual | 5,767.48 ms | **5,770.87 ms** | −0.06% |

   *The frozen followup-03 artefacts are unmodified and were read read-only;
   this is a correction to how its figure is read here, recorded rather than
   silently applied. It does not affect followup-03's conclusions, which rest
   on `time_total`.*

---

## 4. What this changes about the earlier operational picture

followup-03's operational picture was: **MiMo has a usable, cheap-enough bounded
decision, and Jev could not be measured at all.** Its Jev cells were UNRESOLVED
because the free-tier route returned no usable body, and its cost ratio was
*undefined* because Jev was $0 with quota that exhausted inside 197 calls. The
honest summary at that point was that the comparison did not exist.

This run changes three things and leaves the rest alone.

**1. The Jev side of the comparison now exists, and it is not marginal.** On
every operational axis measured here, at matched semantic capability and
matched control accuracy, direct Jev is better: 13.2x median latency, 70.8x
p99, a flat tail (p99 = 1.28x median versus 6.84x), 19.6x sequential
throughput, 0 failures in 238 calls versus 183/192, 16/16 label-stable versus
15/16, and 1.70x more correct decisions per dollar. The margin is large enough
that the conclusion does not rest on any single cell.

**2. The most consequential single finding is determinism plus availability,
not speed.** 16/16 cases returned the identical label on all 12 repetitions,
with maximum probability spread 0.03, *and* every call carried a genuine
model-provided distribution with a `confidence` field on choice and score. MiMo
on this route returned **no model-provided probabilities at all** — not because
the request omitted them, but because an explicit `logprobs: true` probe failed
to obtain them. A bounded-judgement method whose whole value is a calibrated
probability per option can be built on this route and **cannot** be built on the
MiMo route as measured. That is a capability boundary, not a performance
gradient, and it is the finding that most changes the picture.

**3. Two of followup-03's MiMo findings survive unchanged, and one needed
correcting.** MiMo's degrading concurrency curve (1.00x → 0.68x → 0.81x, so
C=1 is the right choice on that route) reproduces exactly. Its wide,
queue-dominated latency distribution reproduces exactly. Its
probability-availability figure did **not** survive scrutiny and is corrected
in §3.4 — a reminder that a non-null parsed field is not evidence of a
capability.

**What did not change, and what this run cannot settle.** followup-03's
free-tier Jev cells stay UNRESOLVED — a different route does not fill them.
The published rate-limit ceilings, sustained throughput, 529 behaviour, cold
start, and server-side queueing are all still untested. And the consolidated
Phase-1 verdict is **not** produced here: the Jev-direct advantage is large and
measured, but the earlier phases' semantic and architectural questions, the
cross-window caveat in §0, and the serving artefacts in §3 all remain live, and
drawing the verdict is the orchestrator's call on the whole evidence set, not
this follow-up's.

---

## 5. Provenance

| | |
|---|---|
| Jev-direct raw | `results/jev_direct_raw.ndjson` — 238 rows, 0 typed errors |
| Jev-direct analysis | `results/summary.json` (reproduces from the raw file; `harness/run_ops_jev_direct.py check`) |
| Equivalence | `results/equivalence.json` (computed **before** any comparative use) |
| MiMo comparison source | `../followup-03-operational/results/mimo_ops_raw.ndjson` (sha256 `40dbc563…27cd8`) and `summary.json`, both **read-only** |
| MiMo comparison block | `resume1` (frozen) |
| Frozen inputs | `cases.ndjson` `7dd4698f…f558c`; `results/jev_raw.ndjson` `e17ae014…d3bc`; `subset.json` `58b855ac…1b8d3` — all verified, all unmodified |
| Calls made | 238 (1 route pre-flight + 5 warm-up discarded + 192 warm + 3 idle + 36 concurrency + 1 interface probe) |
| Derived cost of this run | **$0.00356** |
| Comparison class | **CROSS-WINDOW** — MiMo ~13:09Z–13:33Z, Jev-direct this window; same host |
