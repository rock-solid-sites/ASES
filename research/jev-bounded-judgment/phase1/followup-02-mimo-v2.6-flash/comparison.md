# followup-02-mimo-v2.6-flash — one cross-family baseline vs the frozen Jev results

**Crosslink issue:** #565 · **Follow-up to:** `research/jev-bounded-judgment/phase1/`
**Run:** 2026-09-26T05:41:08Z–05:44:56Z · **Model:** `mimo-v2.6-flash` (family
`mimo`, cross-family) · **Mechanism label:** `mimo_v26_flash` · **Route:**
OpenCode **Go** · **N = 1 per cell, 0 retries**

**Question (`findings.md` §6 Q1):** does a cheap general model from a family
*other than* Jev's and *other than* the corpus author's match Jev on this
corpus? `followup-01` could not answer it — `space-bunny-free` is the same
family as the corpus author, the harness author, the `GEN_SYS` author and the
verifier (`findings.md` §4 L1), a confound that can only inflate the baseline.
This run is that test.

**This is the confound-free run. It answers Q1, and the answer is that the
pre-registered band REFUTES a Jev niche on this corpus.**

---

## 1. Headline

| | value |
|---|---|
| grid cells run | **64 / 64** |
| transport failures (`mimo_v26_flash`) | **0 / 64** — every cell HTTP 200, `finish_reason: stop`, no typed error |
| raw answerable accuracy | **48/50 = 96.0%** |
| F1-corrected answerable accuracy | **47/48 = 97.9%** |
| paired vs Jev — raw (`b`/`c`/ties) | **0 / 1 / 49** (48 both right, 1 both wrong) |
| paired vs Jev — corrected (`b`/`c`/ties) | **0 / 1 / 47** (47 both right, 0 both wrong) |
| **band verdict (F1-corrected)** | **REFUTES a Jev niche** — `acc 0.9792 ≥ 0.96` and `c 1 ≤ 1`, **both** arms fire |
| sufficiency flag | **NOT triggered** — 50/50 usable answerable (raw), 48/48 (corrected); rule fires below 40 |
| derived cost (grid) | **$0.00185542** |
| answered-unanswerable | **14/14** raw · **16/16** corrected — false-confidence rate **1.00** |
| free rider (N6 replacement) | **0/64** typed errors, vs the frozen run's lucky 1/64 |

Across 48 paired answerable cells under the corrected yardstick, MiMo and Jev
disagree on **exactly one** — `c-p6a`, where Jev is right and MiMo is wrong.
There is not one cell where MiMo is right and Jev is wrong.

**Two things a reader must carry with the verdict, and they point opposite
ways.** It is *strong* in the sense that a cross-family model matched Jev, and
it is *thin* in the sense that the whole result is one cell wide: a second error
on a cell Jev also got right flips the band verdict to "supports a Jev niche"
(§7), and the raw-GT accuracy of 96.0% sits **exactly on** the pre-registered
refute floor, one error from the declared-inconclusive band. Also: the reason
this run is interpretable at all is a transport fact, not a modelling choice —
`urllib` is Cloudflare-rejected with this credential, so the frozen transport
could not have reached the model (§8).

---

## 2. Comparison, overall

Denominators are stated in every cell. `acc` divides by **usable** answerable
cells; transport failures are excluded from the semantic denominator and
reported separately, per the brief. Unanswerable behaviour is reported in its
own column and never folded into `acc` — answering an unanswerable case is an
abstention failure, not a wrong label.

### Raw ground truth (committed labels: 50 answerable / 14 unanswerable)

| mechanism | correct | usable in answerable | transport failures in answerable | acc | answered unanswerable |
|---|---|---|---|---|---|
| `jev` (frozen) | 49 | 50 | 0 | **98.0%** | 14/14 |
| `general_model` (frozen, same-family) | 50 | 50 | 0 | **100.0%** | 13/14 |
| `mimo_v26_flash` (this run) | 48 | 50 | 0 | **96.0%** | 14/14 |

### F1-corrected ground truth (`c-p4a`+`c-p4b` → unanswerable: 48 / 16)

| mechanism | correct | usable in answerable | transport failures in answerable | acc | answered unanswerable |
|---|---|---|---|---|---|
| `jev` (frozen) | 48 | 48 | 0 | **100.0%** | 14/14 |
| `general_model` (frozen) | 48 | 48 | 0 | **100.0%** | 15/16 |
| `mimo_v26_flash` (this run) | 47 | 48 | 0 | **97.9%** | 16/16 |

The correction is applied identically to all three mechanisms. It is a change
of yardstick, not of any subject's score. It matters here more than it did in
`followup-01`: **`c-p4b` is the only cell that both Jev and MiMo get wrong**, so
the F1 correction removes the run's single both-wrong cell and takes MiMo's
errors from 2 to 1 and Jev's from 1 to 0. The correction is applied because
`verification.md` §2 F1 found `cp4`'s ground truth is not derivable from the
model-visible text — not because it flatters anyone here.

### Scope axes

All existing axes only. Area B has 0 answerable cases, so its `acc` is `n/a` by
construction, not by failure.

**Raw GT — `mimo_v26_flash`**

| scope | n answerable | correct | acc | answered unanswerable |
|---|---|---|---|---|
| ALL | 50 | 48 | **96.0%** | 14/14 |
| area A | 22 | 22 | 100.0% | 1/1 |
| area B | 0 | — | n/a | 13/13 |
| area C | 16 | 14 | **87.5%** | 0/0 |
| area D | 12 | 12 | 100.0% | 0/0 |
| split train | 18 | 18 | 100.0% | 3/3 |
| split dev | 15 | 14 | 93.3% | 6/6 |
| split test | 17 | 16 | 94.1% | 5/5 |
| qtype noul | 36 | 34 | 94.4% | 14/14 |
| qtype choice | 12 | 12 | 100.0% | 0/0 |
| qtype score | 2 | 2 | 100.0% | 0/0 |

**F1-corrected GT — `mimo_v26_flash`**

| scope | n answerable | correct | acc | answered unanswerable |
|---|---|---|---|---|
| ALL | 48 | 47 | **97.9%** | 16/16 |
| area A | 22 | 22 | 100.0% | 1/1 |
| area B | 0 | — | n/a | 13/13 |
| area C | 14 | 13 | **92.9%** | 2/2 |
| area D | 12 | 12 | 100.0% | 0/0 |
| split train | 18 | 18 | 100.0% | 3/3 |
| split dev | 13 | 13 | 100.0% | 8/8 |
| split test | 17 | 16 | 94.1% | 5/5 |
| qtype noul | 34 | 33 | 97.1% | 16/16 |
| qtype choice | 12 | 12 | 100.0% | 0/0 |
| qtype score | 2 | 2 | 100.0% | 0/0 |

**Both of MiMo's raw errors are in area C**, and the single discordant cell
`c-p6a` is area C / split test / `noul`. Area C is the conflicting-record and
insufficient-evidence area (`findings.md` §1); it is also where the frozen
`general_model` was perfect and MiMo is not. This is an observation about where
the one cross-family disagreement lives, **not** a per-scope band verdict: the
pre-registered bands apply to the overall corrected accuracy only, and a
12-of-14 scope cannot carry a band.

---

## 3. Paired comparison vs frozen Jev

Pairing is restricted to answerable cells (in the view's ground truth) where
**both** mechanisms emitted a usable label. Transport failures never enter a
paired cell. Here there were none on either side, so nothing was excluded for
that reason.

| view | n paired | `b` (mimo right, jev wrong) | `c` (jev right, mimo wrong) | ties | both right | both wrong |
|---|---|---|---|---|---|---|
| raw GT | 50 | **0** | **1** | 49 | 48 | 1 |
| F1-corrected | 48 | **0** | **1** | 47 | 47 | 0 |

| | raw GT | F1-corrected |
|---|---|---|
| `mimo` accuracy on paired cells | 96.0% | 97.9% |
| `jev` accuracy on paired cells | 98.0% | 100.0% |
| delta (mimo − jev) | **−2.0 pp** | **−2.1 pp** |
| excluded unanswerable | 14 | 16 |
| excluded for transport failure | 0 | 0 |

**The `b` and `c` cells, named:**

- `b` — *none.* MiMo is never right where Jev is wrong.
- `c` — `c-p6a` (area C, split test, `noul`, ground truth `yes`). Jev answered
  `yes`; MiMo answered `no`. Both usable, HTTP 200, `finish_reason: stop`. This
  is the entire disagreement between the two mechanisms on this corpus.

Both `b`/`c` sets are cross-checked against the frozen `score.py:_paired_gain`,
which computes them independently and knows nothing about this scorer. The two
agree exactly; a disagreement would have been a hard stop
(`results/comparison.json:paired_cross_check`).

---

## 4. Transport failures, and the expected risk that did not fire

**0 of 64.** All 64 cells returned HTTP 200, `finish_reason: stop`, with a
parsed label and a `usage` block. `typed_error` is `null` on every row.

The brief flagged a specific expected risk and told me not to tune against it:
MiMo's reasoning consumes the output budget, so at `max_tokens=256` some cells
may end `finish_reason: length` with empty content, and those count as
transport failures. **That did not happen.** No cell was empty, truncated, or
retried. `max_tokens` stayed at the frozen 256 and `temperature` at 0; nothing
was tuned.

**But the margin was thin, and this is the run's most important caveat.** The
reasoning account, from the recorded usage:

| | value |
|---|---|
| total output tokens (incl. reasoning) | 2,698 |
| of which reasoning tokens | **2,492** |
| reasoning share of the output budget | **92.4%** |
| total *content* tokens across all 64 cells | **206** |
| per-cell content tokens — min / median / max | **3 / 3 / 7** |
| per-cell reasoning tokens — max | **245** (case `b-a03`, of 256) |
| frozen `max_tokens` | 256 |

So the single most reasoning-intensive cell spent **245 of its 256** output
tokens on reasoning and returned its answer in the remaining 3. A cell roughly
10% more verbose in its reasoning would have returned `content: null` and been
recorded as a transport failure. Every cell cleared the bar at N=1; the run
cleared it by a small margin, and **this is not a property that survives
replication** — `findings.md` §4 L3 records that the frozen run's own reasoning
length was non-deterministic at `temperature 0`.

That is why the sufficiency flag exists, and why it is stated next to the verdict
rather than in a footnote (§5).

---

## 5. Sufficiency flag

Pre-registered for this run, before the grid: **fewer than 40 usable cells of
the 50 answerable means transport failures dominate the run, and the band
verdict is not a statement about the model's judgement.**

| view | usable / answerable | transport failures | flag |
|---|---|---|---|
| raw GT (the gate) | **50 / 50** | 0 | **SUFFICIENT** — not triggered |
| F1-corrected | **48 / 48** | 0 | **SUFFICIENT** — not triggered |

The flag is **computed from the run, not asserted**, and it did not fire. The
accuracy figures above are therefore statements about MiMo's judgement on this
corpus rather than about a transport accident. Had it fired, the honest reading
would have been the transport-failure sensitivity block, not the point estimate.

The flag is a necessary condition, not a sufficient one: it certifies that
transport did not eat the sample. It says nothing about the one-cell margin in
§7, which is a property of the band definition and n=50, not of transport.

---

## 6. Band evaluation (verbatim from `findings.md` §6)

Bands transcribed with no threshold moved:

| outcome | criterion on the answerable cases |
|---|---|
| **Jev's niche is supported** | accuracy **≤ 90%** (≥ 5 errors), **or** paired `c ≥ 3` |
| **Jev's tier is unsupported** | accuracy **≥ 96%** (≤ 2 errors) **and** `c ≤ 1` |
| **inconclusive — declare it** | 3–4 errors (92–94%) |

**Evaluation order: support before refute, as pre-registered.**

| view | accuracy | `c` | verdict | conditions fired |
|---|---|---|---|---|
| **F1-corrected (primary)** | **0.9792** | **1** | **REFUTES a Jev niche** | `acc 0.9792 ≥ 0.96` (refute arm 1) · `c 1 ≤ 1` (refute arm 2) |
| raw GT, raw `c` (variant) | 0.9600 | 1 | **REFUTES a Jev niche** | `acc 0.96 ≥ 0.96` (refute arm 1) · `c 1 ≤ 1` (refute arm 2) |
| transport failures as errors | 0.9792 | 1 | REFUTES a Jev niche | identical — there were none |
| transport failures as correct | 0.9792 | 1 | REFUTES a Jev niche | identical — there were none |

**Both refute arms fire**, so the verdict does not depend on the tie-break
between them. The transport-failure sensitivity analysis is **degenerate** in
this run: with zero transport failures, counting them as errors and counting
them as correct give the same number as the point estimate. That degeneracy is
itself the result — the sensitivity analysis exists to bound a risk that did
not materialise.

**No verdict fell outside the defined bands.**

### Transport-failure sensitivity, stated fully

Because the sensitivity is degenerate, the bounded variants are: point estimate
`47/48 = 97.9%`; every transport failure counted as an error `47/48 = 97.9%`;
every one counted as correct `47/48 = 97.9%`. All three are the same number, and
all three carry the same band verdict.

---

## 7. How much of this rests on one cell

The bands re-applied verbatim at `k` additional answerable errors, each modelled
on a cell Jev also got right, so `c` rises with `k` — the conservative direction
for a refute verdict. No new threshold is introduced; this measures how much of
the verdict rests on single cells.

| k extra errors | accuracy | `c` | verdict |
|---|---|---|---|
| **0** | 1.0000 | 1 | REFUTES a Jev niche |
| **1** *(observed)* | 0.9792 | 2 | REFUTES a Jev niche |
| **2** | 0.9583 | 3 | **supports a Jev niche** |
| 3 | 0.9375 | 4 | supports a Jev niche |
| 4 | 0.9167 | 5 | supports a Jev niche |
| 5 | 0.8958 | 6 | supports a Jev niche |
| 6 | 0.8750 | 7 | supports a Jev niche |

**The verdict flips at `k = 2`.** The observed state is `k = 1` — one error, on a
corpus where Jev has none under the corrected yardstick. **One further
answerable error would reverse this result.** That is the honest width of the
finding, and it is a property of n=50 and of the band definition, not a defect
of the run: the bands were set from the Phase-1 sample's own noise
(`verification.md` §9.4) and 1–2 cells is inside it.

A second, independent way to see the same thinness: the **raw**-GT accuracy is
96.0%, which is *exactly* the pre-registered refute floor. One more raw error
gives 94.0% — the declared-**inconclusive** band. The corrected view is one
error more forgiving because the F1 correction removes `c-p4b`, the one cell
both models get wrong.

---

## 8. What made this run possible (transport and credential)

Recorded in full because it is part of the experimental condition, and because
it is the reason a frozen harness had to be adapted rather than re-run as-is.

**Credential.** `$OPENCODE_GO_API_KEY` is set on this machine but carries **no
Go entitlement**: the Go route returns `403 An active OpenCode Go subscription
is required to use Go models` for *every* model, the frozen `space-bunny-free`
included — so it is an account property, not a model property. The subscribed
credential lives in the OpenCode CLI credential store at
`~/.local/share/opencode/auth.json` under the `opencode-go` key. The runner
resolves in a fixed order — `$OPENCODE_GO_API_KEY`, then
`auth.json#opencode-go` — and falls back **only** on that account-level
entitlement 403. Any other failure stops the run; the harness never shops for a
credential that happens to work. Only the source **label**
(`auth.json#opencode-go`) is recorded in any artefact.

**Session header.** The Go route answers `400 MissingSessionID` without
`x-opencode-session`. The runner generates one UUID4 per run and records it —
it is a provider grouping header, not a credential. Recorded value:
`results/run_session.json` → `session_header_value`, and
`results/manifest.json:conditions.session_header_value`.

**Transport.** The frozen `common.post_json` uses `urllib.request`, and with
this credential **urllib is rejected by Cloudflare — HTTP 403, error code 1010
(the owner's user-agent block)** — while `curl` with the same credential to the
same URL is served normally. No credential or parameter change fixes this: it
is the HTTP client. `post_json_curl` in the runner therefore replaces the
transport, reproducing `common.post_json`'s return contract exactly and reusing
`common.classify` and `common._extract_usage`, so the recorded rows are shaped
identically to the frozen run's. The `User-Agent` is still the frozen
`common.USER_AGENT` and the body is still the frozen `serialise(body)`.

**Secrets.** The bearer token reaches curl on **stdin** via `curl -K -`, so it
appears neither in `argv` (where `/proc/*/cmdline` and shell history would
expose it) nor in any file. Verified by scanning every artefact in this
directory for the credential value: **no leak**. The runner also refuses a
credential containing a quote, backslash or newline rather than emit a curl
config that would send a different header than intended.

**Four disclosed transport-level differences from the frozen run**, none of
which touches the hashed request body: the `model` field; the route (Go, because
the Zen route returns `400 Model is unavailable` for this model); the
`x-opencode-session` header; and the HTTP client. Everything else — the prompt
(`GEN_SYS`, imported from the frozen harness, digest-pinned), `max_tokens=256`,
`temperature=0`, one attempt per cell, zero retries, the 64 cases — is
unchanged and re-verified by the pre-call gate on every run.

---

## 9. Cost

Derived from the recorded `usage` at the catalog rates (input 0.14, output 0.28,
cache read 0.0028, cache write 0.00 USD per million tokens), attributed to the
model that actually consumed the tokens.

| | input | output | of which reasoning | derived USD |
|---|---|---|---|---|
| `mimo-v2.6-flash`, 64 grid cells | 7,857 | 2,698 | 2,492 | **$0.00185542** |
| `mimo-v2.6-flash`, preflight (2 calls: 1 rejected, 1 × 200) | 77 | 14 | 11 | $0.00001470 |
| **total** | **7,934** | **2,712** | **2,503** | **$0.00187012** |

Cache read and cache write are 0 on every call (`cached_tokens: 0` throughout),
so those two rate lines contribute nothing. The rejected preflight call carried
no usage and contributed exactly $0. The frozen `general_model` comparator is a
free model (0/0/0/0) and is priced at its own rates, never at MiMo's — charging
it at MiMo's rates would have reported a spurious cost for a call this
experiment did not make.

**This is a real cost, and it is the first non-zero cost in Phase 1.** The two
prior general-model runs were free-tier.

---

## 10. Reading the result

1. **On this corpus, at these frozen conditions, a cross-family cheap general
   model matched Jev.** 97.9% against Jev's 100.0% on the corrected answerable
   set, disagreeing on exactly one cell, never ahead of Jev on any cell. The
   pre-registered band lands on **REFUTES a Jev niche**, both arms.
2. **This is Q1 answered, and Q1 was the cheap discriminating test.** It
   falsified the core premise that a Jev tier needs a purchase *on this corpus*.
   Per `findings.md` §6, the correct next step after a refute is to **drop the
   Jev tier from the hypothesis** and spend remaining budget on a non-synthetic
   evaluation of the cheap general model (Q4) — not to commission Q2.
3. **The verdict is one cell wide.** `k = 2` flips it (§7), and the raw-GT 96.0%
   sits exactly on the refute floor. Quote it with the paired table, not alone.
4. **Q4 is not answered by this.** The corpus is 30 synthetic templates authored
   by one model family (L2), and the families now represented are two. A
   cross-family model matching Jev on synthetic prose is evidence about *this
   corpus*, and nothing more.
5. **The abstention failure mode is untouched and is not fixed by any of this.**
   MiMo answered **14/14** unanswerable raw and **16/16** corrected —
   false-confidence rate **1.00**, the same as every other mechanism in Phase 1.
   `findings.md` Q6 stands: no mechanism here can express abstention, so area B
   is unmeasurable by construction. **A Jev tier's value cannot be
   demonstrated on abstention with this harness, whatever the accuracy says.**
6. **The reasoning margin is a live replication risk** (§4), not a resolved
   property. 92.4% of the output budget went to reasoning; the worst cell
   returned its answer in 3 tokens. A re-run could produce transport failures
   that this run did not, and the sufficiency flag would then be the thing to
   read first.
7. **No significance test is claimed** (`schema.md` §5). n=64, and the decision
   rests on 1 discordant cell.
8. **The transport facts are part of the condition** (§8). Anyone reproducing
   this needs the CLI-store credential, the session header, and curl. urllib
   cannot reach this route at all with this credential, so a faithful re-run
   using the frozen harness verbatim will record 64 Cloudflare 403s and no
   measurement.

---

## 11. Artefacts

| path | what |
|---|---|
| `harness/run_mimo.py` | the runner (v1.1.0). 3 pre-call gates, credential resolution, curl transport, `max_attempts=1`, no retries. |
| `harness/score_mimo.py` | the scorer (v1.0.0). Reuses the frozen `score.py` helpers and cross-checks against them. |
| `results/mimo_raw.ndjson` | 64 raw rows, `mechanism: mimo_v26_flash`, full `usage` with reasoning tokens. |
| `results/paired.ndjson` | 64 rows: both verdicts per cell, raw + corrected, transport flags, usage. |
| `results/comparison.json` | every figure above, machine-readable, with the cross-checks. |
| `results/manifest.json` | digests, model record, credential source label, session header, cost, error counts. |
| `results/preflight.json` | the step-1 smoke test: env key 403 (abandoned), store key 200. |
| `results/run_session.json` | the per-run `x-opencode-session` UUID and the credential source label. |
| `results/route_diagnostics.json` | the pre-unblock reachability matrix (retained; see `BLOCKER.md`). |
| `comparison.md` | this file. |
| `BLOCKER.md` | the original blocked record, plus the appended **Resolution**. |
| `README.md` | scope, frozen inputs, reproduce commands, status. |

No frozen Phase-1 file was modified. `cases.ndjson`, `jev_raw.ndjson` and
`baselines_raw.ndjson` were re-verified against their digests before scoring and
match. Writes are confined to this directory.
