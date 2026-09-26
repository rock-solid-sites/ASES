# followup-02-mimo-v2.6-flash — BLOCKED AT PREFLIGHT, no grid run

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
