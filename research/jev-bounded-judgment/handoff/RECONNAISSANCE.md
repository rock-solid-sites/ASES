# Jev bounded-judgment evaluation — reconnaissance record

- **Issue:** #565
- **Date:** 2026-09-26
- **Author:** Orchestrator (pre-dispatch investigation)
- **Status:** complete
- **Purpose:** establish whether `jev-1.13-free` is reachable, and pin down its exact
  request/response contract, BEFORE any benchmark is built. Everything below is
  empirically observed or quoted from vendor docs with the source named.

---

## 1. Reachability: the headline finding

`jev-1.13-free` is real and free, but **it is not a chat model**, and it is
therefore invisible to every normal OpenCode model-selection path.

| Probe | Result |
|---|---|
| `opencode models --verbose --refresh` (869 KB, 14 providers, 663 ids) | **0 hits** for `jev` |
| `curl https://opencode.ai/zen/v1/models` (live, unauthenticated) | **81 ids, includes `jev-1.13` and `jev-1.13-free`** |
| `curl https://opencode.ai/zen/go/v1/models` (Go tier, authed) | 35 ids, **no** `jev` |
| `opencode run --model opencode/jev-1.13-free` | `UnknownError ref=err_…` |
| `opencode run --model opencode/big-pickle` | **works** |
| `POST /zen/v1/chat/completions` (jev, curl) | `403 FreeTierError: OpenCode's free tier can only be used from within OpenCode` |
| **`POST /zen/v1/systemone` (jev, curl)** | **`200 OK`, ~0.6 s** |

**Conclusion.** The local catalog is stale/filtered, not the live API. The live
Zen model list is authoritative. Jev is served on a **dedicated `systemone`
endpoint with no AI SDK adapter**, so the client has no chat path to it at all —
the `UnknownError` is the expected consequence of a missing adapter, **not** a
misconfiguration on our side.

### Why the local catalog omits it

`~/.config/opencode/plugins/dynamic-models.ts` line 108 sets
`cfg.provider["opencode"].whitelist = freeZenModels` — a hardcoded array of 62
ids that does **not** include `jev-1.13-free`. Separately, that plugin is
**currently broken and not loading at all**:

```
WARN failed to load plugin target=…/plugins/dynamic-models.js
     cause="Cannot find module './time.js'"
WARN failed to load plugin target=…/plugins/dynamic-models.ts
     cause="SchemaError(Expected object at [\"default\"])"
```

`dynamic-models.js` is a 7-line stale barrel re-exporting seven modules
(`./plugin.js`, `./time.js`, `./config.js`, `./providers.js`, `./credentials.js`,
`./resolver.js`, `./suppression.js`) **none of which exist** in `plugins/`.
So model whitelisting is silently not being applied right now. Flagged as a
separate latent defect; **not** in scope for #565 and not touched.

### Config change made and reverted

A temporary hand-registration of `jev-1.13-free` / `jev-1.13` was added to
`~/.config/opencode/.config/opencode/opencode.json`'s `provider.opencode.models`
and then **reverted** after the endpoint was found, because it could not work
(no chat adapter). Verified reverted: `opencode` provider models are back to
exactly `['mimo-v2.6-flash-free', 'ling-3.0-flash-fin-free']`.
Backup at `/tmp/opencode/opencode.json.bak-jev`.

---

## 2. The contract

- **Endpoint:** `POST https://opencode.ai/zen/v1/systemone`
- **Auth:** `Authorization: Bearer $OPENCODE_GO_API_KEY` — the *existing*
  `opencode-go` key works here even though the same key is refused on
  `/chat/completions`. No OpenCode client required. This is what makes a clean
  deterministic harness possible.
- **Docs:** <https://opencode.ai/docs/zen#jev>, <https://docs.typesafe.ai/>

### Request

```json
{ "model": "jev-1.13-free",
  "state": "<str or object>",
  "questions": { "<qid>": { "type": "noul|choice|score",
                            "instructions": "<str|object|array>",
                            "criteria": "…" } } }
```

`state` may be an **object** and `instructions` may be an **object/array**.
This matters for Phase 2: structural/AST state can be passed natively rather
than flattened into prose.

### Response

| type | fields |
|---|---|
| `noul` | `noul` — scalar, **P(yes) ∈ [0,1]**. *No* `confidence`. |
| `choice` | `choice` (selected), `probabilities` ({option: p}), `confidence` |
| `score` | `score` (continuous), `confidence`, `legend` (idx→level), `probabilities` (idx→p) |

Plus top-level `usage.input_tokens` / `usage.output_tokens`.

### Cost & latency (observed)

- `jev-1.13-free` — Free, unlimited-time offer.
- `jev-1.13` — $0.042 / 1M input, output free (fallback if free tier throttles).
- Latency **~0.6 s**, and **flat in question count** (vendor: questions evaluate
  in parallel, "adding questions barely changes the response time"). This is a
  first-order result versus a general model and must be reported separately from
  model capability.

---

## 3. The finding that changes the analysis design

**`confidence` is not an independent signal.** Per
<https://docs.typesafe.ai/confidence> it is a statistic computed *from* the
probability distribution the answer already contains — documented as
`(n × max(p) − 1) / (n − 1)`, clamped to [0,1] (the vendor describes this as an
approximation for n=3 and defers exact treatment to a cookbook).

Consequences, to be **verified empirically in Phase 1 rather than assumed**:

1. For a fixed option count, a confidence threshold is a monotone rescaling of a
   max-probability threshold. It adds **no** information.
2. Its only real value is normalising across *differing* option counts.
3. Therefore "reported confidence" and "raw selected probability" must be logged
   as separate fields but must **not** be treated as two independent signals, and
   any coverage-at-error-budget curve computed on one must be cross-checked
   against the other.
4. `noul` has no confidence at all — its 2-outcome distribution is fully
   described by the scalar. So for binary decisions, probability and confidence
   are *the same number*, and a threshold on it is a calibrated-looking quantity
   whose calibration is entirely unverified.

The brief's insistence on separating probability / confidence / calibration /
correctness is therefore well-founded, and now precisely characterisable.

---

## 4. Harness rule learned the hard way

A first probe asked four `noul` questions against **one state built by
concatenating four contradictory scenarios** (`STATE_1: … STATE_2: …`).
All four answers came back ≈ **0.45–0.48**, i.e. degenerate.

Re-run with **one scenario per request**, same instruction, same model:

| state | `noul` |
|---|---|
| "The test suite ran and all 42 tests passed. Exit code 0." | **0.99** |
| "The test suite ran and 7 of 42 tests failed. Exit code 1." | **0.01** |
| `` (empty — evidence removed) | **0.50** |
| "It was updated at some point." (vague) | **0.51** |

So the flat readings were **an authoring defect on our side**, not a model
limitation. Two rules for the benchmark builder:

- **R1: one scenario per `state`.** Never concatenate contrasting situations.
- **R2: never batch questions that share a state unless the state is genuinely
  single-scenario.** (Vendor documents questions as isolated; that held here,
  but R1 removes the confound entirely.)

**Early signal worth recording, not yet a finding:** with no evidence, `noul`
returned **exactly 0.50**, and vague evidence **0.51**. If that holds across
the unknowable-case set, it is a genuinely usable abstention signal and answers
research question 3. Treat as provisional until measured on the real set — this
is 4 hand-made probes, not evidence.

---

## 5. Implications for the evaluation design

1. **Jev cannot be compared like a chat model.** There is no `opencode run` path.
   The harness must call `systemone` directly — which is *better*: exact prompt
   control, no agent framing, no tools, clean latency measurement.
2. **Latency (~0.6 s) and price (free) are structural advantages** of a
   purpose-built decision model. The program must test whether they are
   *outweighed* by accuracy/calibration deficits, not assume they dominate.
3. **The hierarchy is testable as specified.** Jev is the "generic bounded
   judgment" tier. Phase 4's downward-compilation question becomes concrete: if
   Jev wins, collect verified examples and try to beat it with a rule, then a
   lexical classifier, then a small scorer.
4. **No model may author the cases that judge it.** Case authors must be a
   different family from TypeSafe/Jev (planned: Nemotron + Laguna, reviewed by
   Space Bunny).
5. **Phase 1 is fully synthetic → no confidentiality exposure.** Later phases
   touching real repo/session content must be restricted to
   **Space Bunny Free** (0-day retention, not used for training). Note the
   contrasts: Big Pickle / MiMo / Ling / Nemotron free tiers **may** use data for
   improvement; Muse Spark Contributor explicitly trains on prompts; Jev is
   US-hosted under Zen's standard zero-retention terms.

---

## 6. Open questions for Phase 1

- Q1: Does the documented confidence formula actually reproduce the returned
  `confidence` on real Choice/Score answers? (Deterministic, cheap, decisive.)
- Q2: Is 0.50-on-no-evidence robust across the unknowable set, or was it luck?
- Q3: Is `noul` calibrated in the frequentist sense (P(yes) ≈ empirical
  frequency), or only ordinally useful?
- Q4: Does Jev respect option order, or is it order-invariant by construction?
- Q5: Latency at larger `state` sizes — is it flat, and where does it break?

---

**Next step (blocked on operator approval):** dispatch W1–W6. Nothing has been
delegated yet; no model has been invoked for this program beyond the ~10
hand-made probe calls recorded above.
