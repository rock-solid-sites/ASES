# followup-05 — cross-family general-model arms: pre-dispatch reconnaissance

- **Issue:** #565 · **Date:** 2026-09-27 · **Status:** complete (pre-dispatch)
- **Branch:** `research/jev-phase1-565` · **Trigger:** the smallest justified next
  experiment in `phase1/findings.md` §6 ("add exactly one cross-family
  general-model baseline to the existing grid").
- **Catalog refreshed:** 2026-09-27, `opencode models --verbose --refresh`
  (51,001 lines; 29 models at cost 0/0/0).

No experiment has been run. No grid cell has been produced. This file records
only what was directly observed.

---

## 1. The change to the premise: the free-tier chat route is closed to direct egress

Phase 1's `general_model` arm and the followup-02 MiMo arm both ran over
`POST https://opencode.ai/zen/v1/chat/completions` (`harness/run_baselines.py:60`).
**That route no longer answers free Zen models from a harness process.**

| Credential tried | Result |
|---|---|
| `OPENCODE_GO_API_KEY` (env) | **403** `FreeTierError: OpenCode's free tier can only be used from within OpenCode` |
| `auth.json#opencode-go` (CLI store — the credential followup-02 actually used) | **403**, identical message |

The CLI-store credential is the *same* one that returned a valid
`mimo-v2.6-flash` completion during followup-02 (`BLOCKER.md` R2). This is
therefore **not** a credential problem. It is a route/entitlement change since
2026-09-26.

Four header variants were tried to test whether the gate is a cheap client
identity check. All four returned the same 403:

- `User-Agent: opencode/1.18.13 (linux; x64)`
- `x-opencode-client: opencode`
- `User-Agent: opencode/1.18.13` + `x-opencode-session: jev-eval-preflight`
- `User-Agent` + `x-opencode-version` + `x-opencode-client`

**Interpretation (evidence-based):** the gate is enforced server-side against
request origin, not against a spoofable header. Free Zen chat models are
reachable *from inside OpenCode* (i.e. via a dispatched agent) and not from a
harness process. This matches the operator's statement that the free Zen models
remain available.

**Consequence for this followup:** the arms cannot be produced by
`harness/run_baselines.py`, which speaks direct HTTP. They must be produced
through an in-OpenCode agent route. This is a real degradation of measurement
fidelity, addressed in §4 rather than glossed over.

### Also observed on 2026-09-27 (adjacent route facts)

| Probe | Result |
|---|---|
| `ollama-cloud/kimi-k2.5` via `https://ollama.com/v1` | **410** — "retired at 2026-07-31" |
| `deepseek-v4-flash-free` on the Zen chat route | **400** — "Model is unavailable" |
| `opencode run --attach` against the local server (`127.0.0.1:49374`, `opencode2.exe serve --service`) | server is live but every endpoint returns **401**; no `OPENCODE_SERVER_PASSWORD` in the serve process environment, so the precise-control HTTP route was not available |

---

## 2. Jev is still reachable — verified, not assumed

The operator flagged that Jev remains available via the TypeScript/direct API.
Confirmed by a single live call:

```
POST https://api.typesafe.ai/v1/systemone
model: jev-1.13.0
→ HTTP 200, {"answers":{"ok":{"type":"noul","noul":0.98}}},
  usage: input_tokens 289 / output_tokens 20, wall time 0.309 s
```

Credential source (label only; value never recorded in any artefact):
`secrets/typesafe.env#TYPESAFE_API_KEY`, matching followup-04's documented
source. The `~/.secrets/typesafe.env` file is present on this host.

**No new Jev cells are required by this followup.** The pre-registered
comparison reads Jev's arm from the frozen `results/jev_raw.ndjson`. Jev
reachability is recorded here because it was an open premise for any follow-on
work, and because followup-03's free-tier route failure must not be read as
"Jev is unavailable".

---

## 3. Operator-selected arms

The operator selected four models. Exact catalog IDs, verified against the
refreshed local catalog — **not** guessed, per `AGENTS.md` model discipline:

| Operator wrote | Verified catalog ID | Family | Route | Cost in/out/cache-read | ctx | Provider |
|---|---|---|---|---|---|---|
| `big-pickle` | **`opencode/big-pickle`** | `big-pickle` | `zen/v1` | 0 / 0 / 0 | 200,000 | OpenCode Zen |
| `ling-3.0-flash-fin-free` | **`opencode/ling-3.0-flash-fin-free`** | `ling` | `zen/v1` | 0 / 0 / 0 | 200,000 | OpenCode Zen |
| `mimo-v2.6-flash-free` | **`opencode/mimo-v2.6-flash-free`** | `mimo` | `zen/v1` | 0 / 0 / 0 | 200,000 | OpenCode Zen |
| `longcat-2.5-preview-free` | **`opencode-go/longcat-2.5-preview-free`** | `longcat` | `zen/go/v1` | 0 / 0 / 0 | 1,000,000 | OpenCode Go |

All four: `status=active`, `reasoning=true`, `toolcall=true`.

`longcat-2.5-preview-free` is the only arm served from the **Go** route
(`https://opencode.ai/zen/go/v1`) despite carrying a free cost. Recorded because
it is a route difference between arms, not a model property.

### Why including `mimo-v2.6-flash-free` is load-bearing, not redundant

MiMo is **not** cross-family here: it is the model already measured over direct
HTTP in followup-02 (`6c7b05b7`, verification `a1a1c93a`). Re-running it under
the agent route therefore does **not** add a capability data point.

It is included deliberately as the **transport control**: the same model, the
same 64 cases, the same frozen prompt, but produced through the agent route
instead of direct HTTP. The difference between the followup-02 MiMo cells and
the followup-05 MiMo cells is a direct measurement of the framing/route effect
described in §4. Without it, that effect could only be asserted; with it, it is
quantified on the same corpus, the same model and the same labels.

**Cross-family arms proper:** `big-pickle`, `ling`, `longcat` — each a different
family from Jev (TypeSafe), from the corpus author (`space-bunny-free`, per
`ERRATA.md` B1 / `findings.md` L1) and from MiMo.

**Not selected, and why it matters:** `space-bunny-free` cannot serve as a
cross-family arm. It authored the corpus, the harness, the ground truth and the
prior comparator, holding four of the five seats in L1. `ERRATA.md` B1 already
rules it "a same-family reference… a weaker test". Dispatching it here would
re-run followup-01 and re-import the A4 confound.

---

## 4. The measurement cost, stated before the run

Phase 1's comparator cells were produced with a **byte-identical** request:
frozen `GEN_SYS`, `build_general_request()` shape, `temperature: 0`,
`max_tokens: 256`, no tools, no agent framing, N=1 per cell, no retries. That
fidelity is a deliberate design virtue (`RECONNAISSANCE.md` §5.1: "exact prompt
control, no agent framing, no tools").

An agent-routed arm cannot reproduce all of it:

| Property | Phase 1 direct HTTP | followup-05 agent route |
|---|---|---|
| `temperature: 0` pinned | yes | **not pinnable** — `opencode run` exposes no temperature flag |
| `max_tokens: 256` pinned | yes | **not pinnable** |
| System prompt = `GEN_SYS` only | yes | **no** — the agent's own system prompt is present |
| Tools available | none | agent tools present |
| N=1 per cell, no retries | yes | **must be enforced by output validation** |
| Clean latency comparability | yes | **no** — session startup dominates |

**What survives:** the capability question. Whether a free general model from
another family matches Jev on these 64 cases is still answerable, because the
cases, the frozen user-message construction and the ground truth are unchanged
and the scoring code is unchanged.

**What does not survive, and must not be claimed:** byte-level request
equivalence with the followup-02 cells, and any latency/throughput comparison
between agent-routed arms and direct-HTTP arms.

**Mitigation actually adopted:** the MiMo transport control (§3). The framing
effect is measured, not asserted.

**Second confound, unmeasured:** all four arms are agent-routed, so they share
one framing regime and remain comparable *to each other*. They are not
comparable to the frozen followup-02 cells except through that control.

---

## 5. What this followup still cannot tell us

Unchanged from `findings.md` §6, and restated because the temptation to read
past them grows with each result:

- **Q2** (does the unanswerable-confidence tail extend past 0.90?) — untouched.
  The 0.04 margin stands.
- **Q3** (is the graded distribution usable as a probability?) — untouched.
  followup-04's one-hot `choice` degeneracy is unaddressed.
- **Q4** (does any of this survive outside a template-generated corpus?) —
  untouched. 64 synthetic cases, one author family.
- **Q6** (can the harness express abstention?) — untouched. `abstained` is still
  hard-coded `false` in `harness/common.py`, so area B remains unmeasurable by
  construction.
- **Statistical power.** n=50 answerable cases. Per `findings.md` §6, a 1–2
  cell difference is inside the documented noise. The pre-registered bands
  must be reported including the inconclusive band.

---

## 6. Pre-registered decision rule (carried forward unchanged from `findings.md` §6)

Bands are fixed **before** the run and are reported whichever way they land,
including the inconclusive band. The primary read is the three cross-family
arms; MiMo is the transport control and is not itself a cross-family arm.

| outcome | criterion on the 50 answerable cases | conclusion |
|---|---|---|
| **Jev's niche supported** | cross-family accuracy **≤ 90%** (≥ 5 errors), **or** paired McNemar `c ≥ 3` | a free general model is measurably unreliable in a family-dependent way; a Jev tier has a defensible niche; next experiment is Q2 |
| **Jev's tier unsupported** | cross-family accuracy **≥ 96%** (≤ 2 errors) **and** `c ≤ 1` | no cheap general model needs a special tier; move budget to Q4 |
| **inconclusive — declare it, do not pick a side** | 3–4 errors (92–94%) | n=50 cannot separate the two; a larger corpus is required before any claim |

**Multi-arm reporting rule added here.** With three cross-family arms, a single
arm landing in a band is not sufficient to characterise "cheap general models"
as a class. Therefore:

- Report **each arm separately** against the bands. No pooling into an
  aggregate accuracy, because pooling would hide which family produced the
  result and would let one strong arm mask a weak one.
- The cross-family verdict is supported only if **a majority of arms** land in
  the supported band; unsupported only if **all arms** land in the unsupported
  band; otherwise **inconclusive**, stated as such.
- Report the spread across arms. Family variance *is* the finding if it is
  large; a tight spread would be evidence that family does not matter much here.

**Free-rider, unchanged from §6:** report each arm's typed-error count over its
own 64 cells, replacing the lucky 1/64 (N6) with same-conditions measurements.

---

## 7. Next step

Not blocked on further model selection: the operator has named all four arms
and they are verified active in the refreshed catalog.

Proceed to a monitored smoke test (small case subset, per-arm reliability and
failure-mode observation) **before** the full 64-case run, per the operator's
instruction to monitor these free models closely. Smoke results determine
whether the full run proceeds per-arm or is held.

Then: frozen `cases.ndjson` (`sha256 7dd4698f…f558c`, unchanged), frozen
`GEN_SYS`, unchanged `harness/score.py`, unchanged bands. Deterministic
completeness validation on every arm's output (exactly 64 rows, all case ids
present, no duplicates, parseable labels) before any cell enters scoring.
