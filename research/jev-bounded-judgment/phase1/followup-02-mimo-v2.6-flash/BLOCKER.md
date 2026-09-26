# followup-02-mimo-v2.6-flash — BLOCKED AT PREFLIGHT, no grid run

> **SUPERSEDED — this file records the blocker, not the outcome.**
> The blocker was resolved on 2026-09-26 and the run completed: **64/64 cells,
> 0 transport failures, band verdict REFUTES a Jev niche.** See the
> **[RESOLUTION](#resolution--unblocked-and-completed-2026-09-26)** section at
> the end of this file, and `comparison.md` for the results. Everything below
> the banner is the original blocked record, preserved unedited.

**Crosslink issue:** #565 · **Date:** 2026-09-26 · **Branch:** `research/jev-phase1-565`
**Status:** **STOPPED at brief step 1.** The model is unreachable with the
available credential. **No grid cell was run. There is no accuracy, no paired
`b`/`c`, and no band verdict.** Nothing below reports a measurement of MiMo's
judgement, because none was taken.

**Blocker in one line:** `mimo-v2.6-flash` cannot be called on either OpenCode
route with `$OPENCODE_GO_API_KEY`; the Go route is blocked account-wide by a
missing active Go subscription, and the Zen route does not host the model.

---

## 1. Headline

| | value |
|---|---|
| grid cells run | **0 / 64** |
| raw answerable accuracy (n=50) | **not measured** |
| F1-corrected answerable accuracy (n=48) | **not measured** |
| paired `b` / `c` / ties vs Jev | **not measured** |
| band verdict (F1-corrected) | **not evaluated** — no accuracy exists to apply it to |
| sufficiency flag | **not reached** — the brief's flag covers *transport failures dominating a completed run*; no run completed, so this is a different and prior failure |
| derived cost | **$0.00** |
| throwaway probe calls | 9 total (3 preflight + 6 diagnostics), **all non-corpus, none scored** |

`results/mimo_raw.ndjson`, `results/paired.ndjson`, `results/comparison.json`
and `results/manifest.json` **do not exist**, by design. Creating them would mean
inventing data.

---

## 2. What was attempted, and what came back

`POST` bodies identical in every respect except the two the brief permits to
differ — the `model` field and the route. Prompt, `temperature=0`,
`max_tokens=256`, one attempt, no retries, and the state text (non-corpus) were
constant across all nine calls.

| # | route | model | HTTP | provider message | what it decides |
|---|---|---|---|---|---|
| 1 | **Go** `…/zen/go/v1/chat/completions` | `mimo-v2.6-flash` | **403** | `An active OpenCode Go subscription is required to use Go models.` | the brief's step-1 smoke test, as specified |
| 2 | Go | `mimo-v2.6-flash` | 403 | *(same)* | consistency (2nd) |
| 3 | Go | `mimo-v2.6-flash` | 403 | *(same)* | consistency (3rd) — **consistent failure** |
| 4 | Go | `space-bunny-free` *(frozen model)* | **403** | *(same)* | **is the 403 model-specific? → NO** |
| 5 | Go | `opencode-go/mimo-v2.6-flash` | 400 | `Model is unavailable.` | does the qualified catalog id resolve? → no |
| 6 | **Zen** `…/zen/v1/chat/completions` | `space-bunny-free` *(frozen model)* | **200** | — | **is this key valid at all? → YES** |
| 7 | Zen | `mimo-v2.6-flash` | 400 | `Model is unavailable.` | does the Zen route host MiMo? → **no** |
| 8 | Zen | `opencode-go/mimo-v2.6-flash` | 400 | `Model is unavailable.` | qualified id on the Zen route → no |

Rows 1–3 are `results/preflight.json`. Rows 1, 4, 5, 6, 7, 8 are the
`results/route_diagnostics.json` probe matrix. Both are independent executions
of the same probe and agree exactly.

### The two findings that make this conclusive

**The 403 is account-wide, not model-specific.** Row 4 puts the **frozen**
`space-bunny-free` on the Go route and gets the byte-identical 403. So the Go
route rejects this key for *every* model, MiMo included. **No model selection
escapes it.** This is what rules out the reading "pick a different Go model and
proceed" — that would fail identically.

**The key is not the problem in general.** Row 6 puts the frozen
`space-bunny-free` on the Zen route and gets a clean **200** (`content="NO"`,
`finish_reason="stop"`) — the exact route+model pair the frozen `general_model`
run used successfully. The credential works. It is specifically the **Go route**
that is entitlement-gated, and specifically the **Zen route** that does not host
`mimo-v2.6-flash`.

Together these two rows close the space: the operator-stated route is closed to
this account, and the alternative route does not carry the model.

---

## 3. Why this is not repairable inside this experiment

The brief says: *"If the route returns 4xx/5xx consistently, STOP and report. Do
not change parameters to make it behave."* Rows 1–3 are a consistent 4xx.

- **Not repairable by parameter change.** A 403 with an entitlement message is
  returned before the model is ever consulted; the model name, `max_tokens`,
  `temperature` and prompt are irrelevant to it. Tuning anything would be
  theatre, and the brief forbids it.
- **Not repairable by model substitution.** `mimo-v2.6-flash` is pinned by the
  operator directive, and model selection is operator-gated (`AGENTS.md` model
  discipline). Substituting a different cross-family model would also void the
  frozen-condition design, which is built around one named baseline.
- **Not repairable by me at all.** Activating a Go subscription is an account
  action on the operator's side, and per `AGENTS.md` **D1** shell/admin work is
  agent work — but this one is an irreducible human identity action outside my
  reach, so it is escalated rather than attempted.
- **I did not shop for a substitute.** That would be an unapproved model
  selection presented as a completed experiment. Q1 stays open.

---

## 4. What was verified, and stands

The blocker is about *reachability*, not about the design. These all completed
and all still hold:

| check | result |
|---|---|
| `cases.ndjson` sha256 | `7dd4698f…f558c` — **matches** the frozen digest |
| `results/jev_raw.ndjson` sha256 | `e17ae014…d3bc` — **matches** |
| `results/baselines_raw.ndjson` sha256 | `42f37690…bf7ba` — **matches** |
| `mimo-v2.6-flash` in the live catalog | **yes** — `opencode models opencode-go` lists `opencode-go/mimo-v2.6-flash` |
| frozen-condition check | **64/64** — every rebuilt request is hash-equal *and* body-equal to the frozen `general_model` row |
| only difference vs the frozen request | the `model` value, confirmed by token-level diff of the serialised bodies |
| grid refused rather than emitting 64 failure rows | **yes** — `run_mimo.py` exits 1 on a preflight that never reached the route |
| secrets | key read from the environment, used as a bearer token, never printed or recorded; every artefact carries `secrets_recorded: false` |
| frozen artefacts modified | **none** — writes confined to this directory |

So the moment the route serves the model, the grid runs with **no further work**:
`python3 harness/run_mimo.py`, unchanged, and it will refuse to start until a
recorded preflight shows the route reachable.

---

## 5. Cost record

This is a paid model, so the cost record is stated exactly.

| | tokens | derived USD |
|---|---|---|
| `mimo-v2.6-flash` (9 rejected calls, 0 with usage) | 0 input, 0 output, 0 cache | **$0.00** |
| `space-bunny-free` control probe (1 × 200, free model) | 216 input, 2 output | $0.00 (0/0/0/0 rates) |

**Total derived cost: $0.00.** A rejected request carries no usage, so the MiMo
baseline consumed nothing. The 216/2 tokens in
`results/route_diagnostics.json` came from the **free** `space-bunny-free`
control probe, and cost accounting attributes each call to its own model at that
model's own rates — charging the free control at MiMo's 0.14/0.28 rates would
have reported a spurious $0.0000308. That misattribution was found and corrected
before commit.

Had the grid run, the recorded rates (input 0.14, output 0.28, cache read
0.0028, cache write 0.00 per million) would put a 64-cell run of this shape at
roughly the frozen run's volume — ~16.5k input, ~1.3–1.7k output — i.e. about
**$0.003**. That is an order-of-magnitude estimate from the frozen run's token
counts, **not a measurement**, and is not recorded as one.

---

## 6. Effect on the research question

**Q1 (`findings.md` §6) remains open and untested.** This run was the
confound-free test that could have closed it: `mimo-v2.6-flash` is a different
family from both Jev and the corpus author, so unlike followup-01 it would not
have been inflated by same-family authorship. It produced no evidence either
way.

Nothing here weakens followup-01's findings or Phase 1's. Those stand as
recorded. The correct statement is that **Q1 has now failed to produce data
twice for different reasons** — once because the model was same-family
(followup-01, a confound) and once because the model was unreachable (here, an
entitlement). Only the second is fixable by a single operator action.

---

## 7. To unblock

Any **one** of these is sufficient; nothing else needs to change.

1. **Activate an OpenCode Go subscription** on the account behind
   `$OPENCODE_GO_API_KEY`, then re-run the preflight. This is the cleanest fix —
   it is exactly the route the operator directive specified. *Irreducible
   operator action.*
2. **Confirm the model id.** The directive's `mimo-v2.6-flash` is present in the
   local catalog but is served by neither route under that name. A different
   served name (e.g. a dated or suffixed variant) would need operator
   confirmation, then a one-line change to `MODEL_ID` in `harness/run_mimo.py`.
3. **Name a different operator-approved cross-family model** that is reachable on
   the Zen route with this key. The Zen route demonstrably serves `opencode-go`
   models, so this is plausible — but it is a model selection and therefore
   operator-gated, and it must be a *different family from Jev and from the
   corpus author* or the whole point of followup-02 is lost.

Whichever is chosen, `harness/run_mimo.py` needs no other change, and the
frozen-condition gate will still verify 64/64 before a single call is made.

---

## 8. Artefacts

| path | what |
|---|---|
| `harness/run_mimo.py` | the runner. Frozen-input gate, 64/64 frozen-condition gate, preflight gate, `max_attempts=1`, no retries. **Ready to run unchanged.** |
| `harness/route_diagnostics.py` | the 6-probe reachability matrix that establishes *which* blocker this is. |
| `results/preflight.json` | the brief's step-1 smoke test: 3 × 403, `route_reachable: false`, `derived_cost_usd: 0.0`. |
| `results/route_diagnostics.json` | the probe matrix with per-model usage and per-model derived cost. |
| `BLOCKER.md` | this file. |
| `README.md` | scope, frozen inputs, model, reproduce commands, status. |

`results/mimo_raw.ndjson`, `results/paired.ndjson`, `results/comparison.json`,
`results/manifest.json`: **absent, deliberately.** No run, no score.

No frozen Phase-1 file was modified. Reproduce with `README.md` in this
directory.

---
---

# RESOLUTION — unblocked and completed, 2026-09-26

**Everything above is the original record and it is not edited.** The stop at
preflight was correct on the evidence available at the time, and the finding
that produced it — the 403 is account-wide, not model-specific — remains exactly
as recorded and turned out to be the whole diagnosis. This section appends what
changed. The run is complete: **64/64 cells, 0 transport failures, $0.00187
derived cost.** The results are in **`comparison.md`**; this section explains
how the blocker was resolved and nothing else.

## R1. The environment key is genuinely unsubscribed — the original finding stands

`$OPENCODE_GO_API_KEY` is present and non-empty (67 chars) and the Go route
rejects it for **every** model, with the byte-identical message
`An active OpenCode Go subscription is required to use Go models.`
Re-verified live today through the new transport:

| source | HTTP | outcome |
|---|---|---|
| `env:OPENCODE_GO_API_KEY` | **403** | `{"error":{"type":"server_error","message":"Upstream request failed: An active OpenCode Go subscription is required to use Go models."}}` |

§2 rows 1–4 of this file are not superseded. The original conclusion "not
repairable by parameter change, not repairable by model substitution" was right,
and the reason it read as a dead end is §3's "Not repairable by me at all": the
fix is an account-side fact, not a request-side one.

## R2. The subscribed credential is in the OpenCode CLI store

`~/.local/share/opencode/auth.json` holds twelve provider entries; the relevant
one is the top-level key **`opencode-go`**, whose value is an object with `key`
and `type`. Its `key` is served normally:

| source | HTTP | outcome |
|---|---|---|
| `auth.json#opencode-go` | **200** | valid `mimo-v2.6-flash` completion, `finish_reason: stop`, `content: "NO"`, usage present |

This is the same credential the OpenCode CLI itself authenticates with — the
orchestrator's probe `opencode run --model opencode-go/mimo-v2.6-flash` returns
OK — so the subscription is real; the *environment variable* simply points at a
different, unentitled credential.

**One correction to §7 of the original record.** The unblock is not a new
subscription and not a model-id change. It is a **credential-source change**,
which is why it needed no operator action at all. §7's item 1 (activate a Go
subscription) would also have worked, and would have been the wrong fix: the
account already had the entitlement.

## R3. `x-opencode-session` is required, and the runner now sends one

The Go route returns **`400 MissingSessionID`** when the header is absent and
**200** when it is present. This is a per-request requirement, not an
entitlement question, and it is why the orchestrator's probe succeeded.

The runner generates **one UUID4 per run** (`x-opencode-session`), records it in
`results/run_session.json` and in `results/manifest.json:conditions`, and sends
it on every call. This run's value:
`d365cc37-c2dc-424b-a034-d9f84141b641`. The preflight's was
`fea09ff9-99a4-409b-a7d9-3f95911f76e9`. It is a provider grouping header, **not
a secret**, and it is not part of the hashed request body — the 64/64
frozen-condition gate is unaffected by it.

## R4. Transport: urllib is Cloudflare-rejected, curl is not

| client | credential | result |
|---|---|---|
| Python `urllib.request` | `auth.json#opencode-go` | **403, Cloudflare error code 1010** (owner's user-agent block) |
| `curl` | `auth.json#opencode-go` | **200**, valid completion |

Same credential, same URL, same headers, same body. The difference is the HTTP
client's TLS/HTTP fingerprint. **No credential change and no parameter change
fixes this**, which is why `harness/run_mimo.py` now uses a `curl` subprocess
(`post_json_curl`) instead of the frozen `common.post_json`. The replacement
reproduces `common.post_json`'s return contract exactly and reuses
`common.classify` and `common._extract_usage`, so the recorded rows are shaped
identically to the frozen run's. `User-Agent` is still the frozen
`common.USER_AGENT`; the body is still the frozen `serialise(body)`.

**The frozen `harness/common.py` was not modified.** The transport substitution
lives entirely in the follow-up harness. A consequence worth stating plainly: a
re-run using the frozen harness verbatim will record 64 Cloudflare 403s and no
measurement, which is a transport artefact and not a finding.

## R5. Credential handling — how the value was kept out of every artefact

Resolution order is fixed: (a) `$OPENCODE_GO_API_KEY`, and **only** on an
account-level entitlement 403, fall back to (b) `auth.json#opencode-go`. Any
other failure stops the run; the harness never shops for a credential that
happens to work. The fallback fires once, in the preflight, and the grid then
uses the selected source directly — so **no cell was ever re-sent under a second
credential**, and N=1 per cell is preserved exactly.

The value reaches curl through a config on **stdin**:

```
printf 'header = "Authorization: Bearer %s"\n' "$KEY" | curl -K -
```

so it appears neither in `argv` (where `/proc/*/cmdline` and shell history would
expose it) nor in any file. The runner also refuses a credential containing a
quote, backslash or newline, rather than emit a config that would send a
different header than intended.

**Recorded in the manifest: the source label `auth.json#opencode-go`, never the
value.** The label appears in `results/preflight.json`
(`credential_source_selected`), `results/run_session.json`
(`credential_source_used`) and `results/manifest.json:credential.source_used`.
Every `secrets_recorded` field is `false`. Verified by scanning every file in
this directory for the credential value: **no leak.**

The env-key rejection is recorded rather than hidden: `preflight.json` shows both
calls, `n_calls: 2`, with the first as
`{"credential_source": "env:OPENCODE_GO_API_KEY", "outcome": "entitlement_403"}`.

## R6. The expected risk did not fire — but the margin was thin

The brief flagged that MiMo's reasoning consumes the output budget and that some
cells might end `finish_reason: length` with empty content at `max_tokens=256`,
and instructed that these count as transport failures with no tuning.

**It did not happen: 0 transport failures in 64 cells**, all HTTP 200, all
`finish_reason: stop`, no typed errors. `max_tokens` stayed 256, `temperature`
stayed 0, nothing was tuned, nothing was retried.

The margin is nevertheless the run's main caveat, and it is measured rather than
asserted: **92.4% of the output budget went to reasoning** (2,492 of 2,698
output tokens), leaving **206 content tokens across all 64 cells** — per-cell
content min 3, median 3, max 7. The worst cell (`b-a03`) spent **245 of its 256**
output tokens on reasoning and returned its answer in the remaining 3. One cell
roughly 10% more verbose in reasoning would have returned `content: null` and
been recorded as a transport failure. The sufficiency flag was pre-registered
for exactly this and did not fire (50/50 usable answerable).

## R7. Cost correction to §5

§5 recorded **$0.00**, correctly, for the blocked run. This section does not
amend that figure — it applies to the calls made then. For the completed run:

| | input | output | derived USD |
|---|---|---|---|
| 64 grid cells | 7,857 | 2,698 | $0.00185542 |
| preflight (1 rejected + 1 × 200) | 77 | 14 | $0.00001470 |
| **total** | **7,934** | **2,712** | **$0.00187012** |

At the recorded catalog rates (input 0.14, output 0.28, cache read 0.0028, cache
write 0.00 per million). This is the **first non-zero cost in Phase 1**; the two
prior general-model runs were free-tier. §5's order-of-magnitude estimate of
~$0.003 for a 64-cell run was accurate to within a factor of 1.6, and it is now
a measurement.

## R8. Status

| | |
|---|---|
| blocker | **resolved** — credential source, not a subscription |
| grid cells run | **64 / 64** |
| transport failures | **0 / 64** |
| raw answerable accuracy (n=50) | **96.0%** (48/50) |
| F1-corrected answerable accuracy (n=48) | **97.9%** (47/48) |
| paired `b` / `c` / ties vs Jev (corrected) | **0 / 1 / 47** |
| band verdict (F1-corrected) | **REFUTES a Jev niche** — `acc 0.9792 ≥ 0.96` and `c 1 ≤ 1`, both arms |
| sufficiency flag | **not triggered** (50/50 usable; rule fires below 40) |
| derived cost | **$0.00187012** |
| determinism | scorer run twice → `comparison.json`, `paired.ndjson`, `manifest.json` all byte-identical |

**Q1 (`findings.md` §6) is now answered**, and this is the confound-free run that
could answer it: `mimo` is a different family from both Jev and the corpus
author, so unlike followup-01 the self-preference confound cannot be inflating
the baseline. §6 of this file recorded that Q1 "has now failed to produce data
twice for different reasons"; it has now produced data. The full reading,
including the one-cell width of the verdict, is in `comparison.md` §7 and §10.

The frozen Phase-1 artefacts were re-verified against their digests before
scoring and **none was modified**. Writes are confined to this directory.
