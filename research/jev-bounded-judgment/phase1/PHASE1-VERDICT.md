# Jev Phase 1 — Consolidated Verdict

**Crosslink issue:** #565 · **Branch:** `research/jev-phase1-565`
**Status:** Phase 1 complete. Consolidated verdict of record for the evidence set
below. No new experiments were run to produce this document.
**Authority rule:** where builder/analyst prose conflicts with an independent
verification, the verification governs. `ERRATA.md` (this directory) enumerates
every such correction; this document states the reconciled result.

## 0. Evidence set and how it fits together

| Stage | What it produced | Commits |
|---|---|---|
| D1 builder | frozen 64-case corpus, 5-mechanism grid (320 cells), deterministic scorer, tables, RUNBOOK | `8ebba5b5`…`19eccb0f` |
| D2 verifier | independent re-scoring (2,315 comparisons), live re-runs, controls audit | `4e50a936` |
| D3 analyst | findings S1–S10 / P1–P6 / L1–L14 / N1–N12, next-phase question | `355ab6ad` |
| Followup-01 | `space-bunny-free` replication (same-family reference) | `42d2fdbc`…`b78bfca7` |
| Followup-02 | `mimo-v2.6-flash` confound-free baseline; pre-registered bands | `8478edca`…`a1a1c93a` |
| Followup-03 | operational comparison; free-tier Jev route failed 0/197; MiMo measured | `d81cf418`…`70ef037e` |
| Followup-04 | direct `jev-1.13.0` operational run + semantic equivalence + cross-window comparison | `5da5872e`…`63aa33c5` |

Frozen inputs throughout: `cases.ndjson` sha256 `7dd4698f…f558c`,
`results/jev_raw.ndjson` sha256 `e17ae014…d3bc`. No experiment was re-run for
this closeout.

The verdict is stated on four separate tracks. They must not be merged:
**capability**, **uncertainty/abstention**, **operational performance**, and
**serving/pricing artifacts**.

---

## 1. Capability — supported result

**1.1 Jev exceeds the deterministic/lexical floor on this corpus.**
On the 50 answerable cases Jev answered 49/50 (98.0%), against `lexical` 58.0%
and `rule` 78.0%. All seven paired comparisons vs `lexical` had `c = 0`
(none where lexical was right and Jev wrong), including +40.0pp overall
(b=20/c=0) and per-area +40.9 / +18.8 / +66.7 (A/C/D).
*Provenance:* `findings.md` S2 (commit `355ab6ad`); `results/metrics.json:m3b_jev_vs_all`;
`tables/T3-incremental-gain.md` (commit `040a58af`).

**1.2 No semantic-capability niche over MiMo V2.6 Flash was demonstrated.**
Against the confound-free cross-family baseline (`mimo-v2.6-flash`, followup-02):
raw 48/50 = 96.0%, F1-corrected 47/48 = 97.9%; paired vs Jev b=0/c=1/ties=47
(the single discordant cell, `c-p6a`, favours Jev); the pre-registered band
returned **REFUTES a Jev niche** (acc ≥ 96% and c ≤ 1). The same-family
Space Bunny replication (followup-01) returned raw 49/50, corrected 48/48,
b=0/c=0, and also REFUTES; because it is the corpus-author family that result is
a weaker test and is retained only as a reference.
*Provenance:* `followup-02-mimo-v2.6-flash/comparison.md` §1 (verification
`a1a1c93a`); `followup-01-spacebunny/comparison.md` (verification `b78bfca7`).
MiMo is cross-family to both Jev and the corpus author, so the refutation is not
an authorship artefact.

**1.3 Known ground-truth defect.** `c-p4b`'s ground truth is not derivable from
model-visible text (D2 F1). Treating both `cp4` members as unanswerable gives the
justified subset 48 answerable / 16 unanswerable and Jev 48/48; it also removes
the run's only informative confidence-ordering verdict (D3 S6). The defect class
is invisible to the validator and may contain other instances (D3 L11).

**Capability caveats:** n=64 synthetic template cases authored by one model
family; no significance test; `lexical`/`rule` lexicons were authored with the
corpus in view (upper bounds, not point estimates); `rule` on area D is a
tautology. These bound the size of 1.1; they do not overturn 1.2.

---

## 2. Uncertainty and abstention — supported result

**2.1 Intrinsic abstention was not established.**
No mechanism in the grid could record an abstention: `abstained` is hard-coded
`false` in `harness/common.py` (D2 F2 / D3 S8/N7). The measurable fact is that
**69 of 70 unanswerable mechanism-cells emitted a label**; Jev answered 14/14
unanswerable cases, four with derived confidence ≥ 0.76. Jev publishes **no**
confidence and no probabilities for `noul` questions (50/64 cases), so the
escalation analysis rests on a locally derived value, `2·max(p) − 1`, which is
thresholding on `p ≥ 0.95` — a deployable rule but not a model confidence claim.

**2.2 The escalation gate is real but fragile on this sample.**
At threshold 0.90, 38 cells act, 38/38 correct (59.4% coverage), and, after the
F1 correction, 10 correct answers are withheld to eliminate 16
false-confidence errors. The margin is **0.04**: maximum unanswerable derived
confidence 0.86 over n=14. At 0.95 coverage falls to 39.1%.
*Provenance:* `findings.md` S5; `results/metrics.json:m4_coverage_error` and
`m6_contrastive_and_controls`; `tables/T5`,`T6`.

**2.3 Choice probability and calibration usefulness is unsupported on the
observed cases.** In the direct-API run, all three `choice` cases returned
degenerate one-hot distributions with `confidence` exactly 1.0 on 36/36 calls
(18.75% of all 192 warm calls); calibration was never measured, and the
`confidence` semantics are inconclusive (0.5 on probe answers).
*Provenance:* `followup-04-jev-direct/verification.md` G1/G2 (commit `63aa33c5`);
`followup-04-jev-direct/comparison.md` §2 "calibration NOT MEASURED".

---

## 3. Operational performance — supported result

Direct `jev-1.13.0` at matched control accuracy (108/108 control opportunities
for both mechanisms) against the frozen MiMo operation measurements. The
comparison is cross-window, single host, short burst — see §5.

| Axis | Direct Jev `jev-1.13.0` | MiMo V2.6 Flash |
|---|---|---|
| Warm median (n) | **304.91 ms** (192) | 4,035.47 ms (183) |
| p95 / p99 / max | **345.67 / 389.98 / 400.75 ms** | 15,955.57 / 27,609.55 / 60,607.85 ms |
| Tail shape (p99 ÷ median) | **1.28×** | 6.84× |
| Latency↔output-token correlation | **−0.0125** | 0.394 |
| Sequential throughput | **3.2859 calls/s** | 0.1674 calls/s |
| Correct-control decisions/s | **1.8483** | 0.0988 |
| Concurrency C=1/4/8 (scaling) | 3.09 / 3.23 / 3.14 c/s (**1.00/1.04/1.01×**) | 0.25 / 0.17 / 0.20 c/s (**1.00/0.68/0.81×**) |
| Usable calls | **238/238, 0 failures** | 183/192 (9 `empty_content`) |
| Repeat stability | **16/16 labels stable over 12 reps**; noul drift ≤ 0.04; prob drift ≤ 0.01 | 15/16 |
| Cost per call · per correct decision | **$1.5057e-05 · $2.6768e-05** | $2.6840e-05 · $4.5479e-05 |
| Usage per call (input) | 358.50 tokens | 128.43 tokens (like-for-like warm) |

Semantic equivalence cross-check: 16/16 cases agree with the frozen
`jev-1.13-free` majority labels, 0 answer changes, max `noul` drift 0.04, max
choice/score probability drift 0.01. Equivalence is **not** claimed — the route
and model tag changed (`opencode.ai/zen/v1/systemone` `jev-1.13-free` →
`api.typesafe.ai/v1/systemone` `jev-1.13.0`).
*Provenance:* `followup-04-jev-direct/comparison.md` §1 (raw:
`results/jev_direct_raw.ndjson`, 238 rows); `results/equivalence.json`;
`followup-03-operational/comparison.md` §1–§2 for MiMo (raw:
`results/mimo_ops_raw.ndjson`, block `resume1`). Verifications: `63aa33c5`
(followup-04: every figure reproduced to the last printed digit), `70ef037e`
(followup-03).

**Established operational advantages of direct Jev on these axes:** latency
(13.2× median), tail (70.8× p99; flat distribution), sequential throughput
(19.6×), reliability (0 failures in 238 calls vs 9 transport failures),
stability (16/16), and current-tariff cost (1.70× cheaper per correct decision).
Concurrency is a free option for Jev and a regression for MiMo on this route.

---

## 4. Serving and pricing artifacts — not capability findings

1. **Time-to-first-byte is not model latency on either route.** First byte lands
   0.20 ms after TLS completion; 82.45% (Jev) and 96.62% (MiMo) of the call is
   post-first-byte body wait. A "TTFB" comparison would compare handshakes.
2. **Jev's transport *share* rising is not a transport regression** — its
   handshake is 3.8× faster; the share rises because the total shrank.
3. **The cost advantage is tariff arithmetic, not token efficiency.** Jev uses
   ~2.79× more input tokens and is still cheaper because $0.042/Mtok input with
   free output beats $0.14/$0.28 (followup-04 verification D4; the 2.85×
   headline was a mixed-denominator figure and is superseded).
4. **The free-tier route failure is evidence about that route, not about Jev.**
   Followup-03 recorded 0 of 197 usable answers on
   `opencode.ai/zen/v1/systemone` `jev-1.13-free` (403s then 429s; 10/10 spaced
   probes 429). The verifier established that the window began already refused —
   "exhausted inside 197 calls" is **not** established (followup-03 verification,
   material faults 1–2). The direct key succeeded 238/238.
5. **`probabilities_exposed = 234` (followup-03 summary) is a parser artefact**
   (harness-synthesised vectors). The defensible MiMo figure under frozen
   conditions is **0** (followup-04 verification).
6. **Cross-window, single-host comparison.** MiMo was measured 13:09Z–13:33Z
   (warm window), Jev-direct later the same day. Network components cannot be
   separated from model components with one window each.
7. **Idle probe is a proxy only** (n=3; 279.60 ms vs 304.91 ms warm median);
   cold start was not directly observed for either mechanism.

---

## 5. Unresolved limitations (preserved, not smoothed)

- **Intrinsic abstention unestablished**, and the harness cannot express
  abstention (area B unmeasurable by construction in that design).
- **Choice probability/calibration unmeasured**; one-hot degeneracy on the only
  multi-way cases observed; `confidence` semantics inconclusive.
- **Corpus scope**: 64 fully synthetic cases, 30 templates, one author family;
  no significance tests; hand-authored baselines upper bounds; `rule` on area D
  tautological; `n=2` `score` and `n=12` `choice` cases.
- **`noul` uncertainty is derived**, not published; margin of the 0.90 gate is
  0.04 on n=14.
- **Ground-truth class**: `c-p4b` is the one found defect; `validate_cases.py`
  checks coherence, not derivability.
- **Operational envelope untested**: sustained multi-hour throughput; rate-limit
  envelope (published 250,000 tok/s / 1,200 req/min; 0 × 429 observed — never
  approached); HTTP 529 path; server-side queueing/batching; C > 8; batched
  multi-question economics; behaviour across route/model-version changes; cold
  start.
- **Free-tier Jev cells cannot be filled** by a different route; they remain a
  fact about that route.
- **Followup-01 confound**: Space Bunny is the corpus-author family; its
  comparison can only inflate that baseline and is a weaker test.
- **Cross-window operational comparison** (same host, same transport, same
  subset, different time window).

---

## 6. Consolidated verdict

1. **Capability:** Jev clearly exceeds the deterministic/lexical floor on this
   corpus (+40.0pp over `lexical`, c=0 in all paired scopes).
2. **Capability vs cheap general model:** no semantic-capability niche over
   MiMo V2.6 Flash was demonstrated (refute band, confound-free baseline).
3. **Operational:** direct `jev-1.13.0`, at matched control accuracy, showed
   material advantages on the measured latency, tail, throughput, reliability,
   stability, and current-tariff cost axes.
4. **Uncertainty:** intrinsic abstention was not established; the escalation
   rule works on this sample but is fragile (0.04 margin, derived confidence).
5. **Probability interface:** availability exists (noul scalar; score
   distributions) but Choice probability/calibration usefulness is unsupported
   on the observed cases.
6. **Route separation:** the OpenCode free-tier failures are evidence about that
   route, not about Jev generally; the direct API performed without failure.

**What this verdict does not claim:** it does not claim Jev is generally better
than MiMo (the semantic test was a tie with a one-cell margin and a
pre-registered refutation), does not claim calibrated probabilities, does not
claim sustained-load capacity, and does not extrapolate beyond the measured
corpus, windows, and tariffs. Phase 2 design is not decided here.

---

## 7. Provenance index (material numbers)

| Claim | Artifact / field | Commit |
|---|---|---|
| 64 cases; 320/320 cells | `results/manifest.json:grid` | `8ebba5b5`,`09df1e07` |
| Jev 49/50; lexical +40.0pp, c=0 | `findings.md` S1/S2; `results/metrics.json:m1_accuracy,m3b_jev_vs_all` | `355ab6ad` |
| `c-p4b` GT defect; corrected 48/48 | `verification.md` F1; `findings.md` S1 | `4e50a936`,`355ab6ad` |
| Abstention tautology; 69/70 | `verification.md` F2; `findings.md` S8/N7; `common.py:298` | `4e50a936`,`355ab6ad` |
| 0.90 gate 38/38; margin 0.04 | `results/metrics.json:m4,m6`; `findings.md` S5 | `355ab6ad` |
| MiMo raw 48/50, corrected 47/48, b=0/c=1, REFUTES | `followup-02-*/comparison.md`; `results/comparison.json` | `6c7b05b7`,`c79bd621`,`a1a1c93a` |
| Space Bunny 49/50, corrected 48/48, b=0/c=0 | `followup-01-*/comparison.md` | `f4ad24ac`,`a15b0b97`,`b78bfca7` |
| Free-tier 0/197; 10/10 429 | `followup-03-*/results/*`; `verification.md` faults 1–2 | `252a3009`,`70ef037e` |
| MiMo latency/throughput/concurrency/cost | `followup-03-*/results/mimo_ops_raw.ndjson` block `resume1`; `comparison.md` §1 | `0f2a97ad`,`e598a942`,`4e45187c` |
| Jev-direct latency/throughput/cost/equivalence | `followup-04-*/results/jev_direct_raw.ndjson`,`equivalence.json`,`summary.json`; `comparison.md` §1 | `0c2afc3a`,`364ccb3d`,`4896cb10`,`311ae5dc` |
| Jev-direct one-hot choice; calibration unsupported | `followup-04-*/verification.md` G1/G2 | `63aa33c5` |
| Cost rates and limits | TypeSafe docs `models.md` (fetched 2026-09-26); `followup-04-*/README.md` | `5da5872e` |
