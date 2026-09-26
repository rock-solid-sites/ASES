# ERRATA — Phase 1 record reconciliation

**Crosslink issue:** #565 · **Authority:** independent verification governs
builder/analyst prose. This file lists every claim that a later verification
superseded, with the authoritative statement. Frozen artifacts are not
rewritten; this file plus `PHASE1-VERDICT.md` reconcile the record.

Precedence for any future reader: `PHASE1-VERDICT.md` > per-stage
`verification.md` > per-stage reports (`comparison.md`, `findings.md`, tables).

---

## A. D1 / D2 / D3 (core diagnostic)

| # | Superseded claim | Authority | Authoritative statement |
|---|---|---|---|
| A1 | "0 of 320 cells set the `abstained` flag" presented as a mechanism finding (`README.md`, `DISPATCH.md`, `tables/T1`, `T7c`) | D2 `verification.md` F2 (`4e50a936`); D3 S8/N7 (`355ab6ad`) | The flag is a harness tautology — hard-coded `false` at `harness/common.py:298`. The measurable evidence is **69 of 70 unanswerable mechanism-cells emitted a label**; no mechanism in the grid could express abstention. |
| A2 | Jev "98.0% answerable accuracy" as the general statement | D2 `verification.md` F1 (`4e50a936`); D3 S1/S5 | On the justified subset (both `cp4` members unanswerable per F1) Jev is **48/48 = 100%**; answerable n becomes 48, unanswerable 16. Quote 98.0% only for the raw committed labels and state the defect. |
| A3 | `general_model` `empty_content = 1/64` as a reliability rate (`tables/T11`, `README`) | D2 `verification.md` F3 (`4e50a936`); D3 N6 | Re-measured rate at `max_tokens=256` is **≈11% (4/35)**; the committed 1/64 was a lucky draw, not a rate. |
| A4 | Confounder unnamed in D1 artifacts | D2 `verification.md` §7 F8 (`4e50a936`); D3 L1 | Corpus author, harness author, `general_model` baseline and verifier are all `space-bunny-free`; the confound can only inflate that baseline (bias against Jev). |
| A5 | D2 `verification.md` §6 Attempt 4: "always-`escalate` would score 10/12" | D3 N12 (`355ab6ad`) | Does not reproduce: always-`escalate` scores **2/12**; best constant strategy **3/12**. Do not quote 10/12. |
| A6 | `c-p4b` counted as a normal answerable case | D2 `verification.md` F1 (`4e50a936`) | `c-p4b`'s ground truth is not derivable from model-visible text; both `cp4` members are unanswerable on the justified reading. The defect class may contain others (L11). |
| A7 | `RUNBOOK.md` hashes/flag for clean-clone reproduction | D2 `verification.md` F4 (`4e50a936`); D3 L14 | Two of twelve checklist items fail (stale `metrics.json`/`manifest.json` hashes; `gen_cases.py --out` does not exist and would overwrite the corpus). Data unaffected; runbook not fully reproducible as written. |
| A8 | D3 analyst-derived statistics (AUC, margin, acted composition, `run_rule` accesses, `acc_mixed` decomposition) | D3 L13 (`355ab6ad`) | Reproducible from committed files but outside D2's 2,315-comparison envelope; treat as analyst-derived, not independently verified. |

## B. Followup-01 (`space-bunny-free`)

| # | Superseded claim | Authority | Authoritative statement |
|---|---|---|---|
| B1 | Implied as the cross-family decision run | D3 L1; followup-02 design | `space-bunny-free` is the corpus-author family. Retain followup-01 only as a same-family **reference**; its band verdict (REFUTES, raw 49/50, corrected 48/48, b=0/c=0) is a weaker test. The decision run is followup-02 (MiMo). |

## C. Followup-02 (`mimo-v2.6-flash`)

| # | Superseded claim | Authority | Authoritative statement |
|---|---|---|---|
| C1 | `comparison.md` §7 `band_flip_margin` series ("k extra errors → acc (48−k)/48") | `verification.md` §5 fault 1 (`a1a1c93a`) | Off-by-one: `k` is additional errors, so `acc = (47−k)/48`, `c = 1+k`. The margin table as printed is wrong; the headline refute verdict is unaffected. |
| C2 | Band evaluator used OR for the refute arm | `verification.md` §5 fault 2 (`a1a1c93a`) | The declared rule is `acc ≥ 96% AND c ≤ 1`; both arms hold here, so the verdict (REFUTES) is unchanged. Use the AND rule going forward. |
| C3 | Derived cost understated | `verification.md` §7 fault 3 (`a1a1c93a`) | Understated by $3.6e-7; `cached_tokens: 0 throughout` is false. |
| C4 | §4 "that did not happen" robustness claim | `verification.md` §8 F3 (`a1a1c93a`) | Falsified by the verifier's re-run: reasoning-token counts vary at `temperature=0`; `b-a03` had only 11/256 tokens of headroom. |

## D. Followup-03 (operational; free-tier Jev route)

| # | Superseded claim | Authority | Authoritative statement |
|---|---|---|---|
| D1 | "exhausted inside 197 calls" / "watched it exhaust" (`comparison.md` §3, `summary.json`, issue comments) | followup-03 `verification.md` material faults 1–2 (`70ef037e`); followup-04 `verification.md` §3 item 4 (`63aa33c5`) | **Not established.** The window's first call was already refused; no available→exhausted transition was observed. The established fact is: every call in that window was refused (403s then 429s; 10/10 spaced probes 429) — a fact about the free-tier route, not proof the 197 calls caused it. |
| D2 | "the 403 phase masks the cap" | same material fault 2 | Inference, not established: the 403 body names no cap and no discriminating test was run. |
| D3 | `summary.json` interface statistics (Jev-side `0/0`; MiMo-side "234 probabilities exposed") | followup-03 `verification.md` material fault 3 | The Jev-side value was a never-computed `0/0`; the MiMo-side value counted harness-synthesised one-hot vectors. The defensible MiMo figure under frozen conditions is **0**; Jev-direct provides real distributions except the one-hot Choice limitation (E1). |
| D4 | Transport-vs-service decomposition and shares | followup-03 `verification.md` moderate fault; followup-04 `comparison.md` §3.1 | curl `-w` phases are cumulative; summing DNS+TCP+TLS double-counts. Correct transport term is `time_appconnect` alone. followup-03's share percentages are superseded (both qualitative claims survive). followup-04 `comparison.md` §3.1's "−3.19 ms" is itself wrong (see E4). |
| D5 | MiMo probability-availability across the run | followup-04 `verification.md` §3 item 4 (`63aa33c5`) | The 234 figure is a parser artefact; MiMo returned no model-provided probabilities under the frozen shape. |

## E. Followup-04 (direct `jev-1.13.0`)

| # | Superseded claim | Authority | Authoritative statement |
|---|---|---|---|
| E1 | Probability-availability presented as "100% model-provided" | `verification.md` G1 (`63aa33c5`) | 36/192 warm calls (18.75%) — all three `choice` cases — are degenerate one-hot with `confidence` exactly 1.0. Record this as a limitation. |
| E2 | "A calibrated probability per option is available / can be built on this route" (§1.9, §4.2) | `verification.md` G2 (`63aa33c5`) | Unsupported; contradicts the document's own "calibration NOT MEASURED". No calibration claim may be made from this run. |
| E3 | "Jev uses 2.85× more input tokens" | `verification.md` D4 (`63aa33c5`) | Like-for-like warm-only penalty is **2.79×**; the 2.85× mixed two denominators. Cost conclusion unchanged. |
| E4 | §3.1 "−3.19 ms on MiMo" for first-byte minus TLS | `verification.md` D3 (`63aa33c5`) | Recomputed value is **+0.2037 ms** (consistent with §1.3's +0.20 ms). |
| E5 | "`logprobs` present and null in all 183" | `verification.md` G3 (`63aa33c5`) | The key is **absent** from all MiMo raw responses, not present-and-null. Substantive conclusion unchanged. |
| E6 | "a full 6-way distribution" for Choice | `verification.md` G4 (`63aa33c5`) | Six keys, but degenerate on 36/36 calls (see E1). |
| E7 | MiMo measurement window stated as 13:09Z–13:33Z | `verification.md` G7 (`63aa33c5`) | 13:09Z–13:33Z is the warm window; the full `resume1` block extends to ~13:56Z. |
| E8 | Field named `median` | `verification.md` D1 (`63aa33c5`) | It is nearest-rank p50 (Jev warm 304.908 vs true 305.1335); all rounded quoted figures survive. |
| E9 | Transport/post-first-byte "share" percentages | `verification.md` D2 (`63aa33c5`) | Undocumented ratio-of-means estimator; an alternative estimator moves the shares (transport 3.377%→5.943%; post-first-byte 96.620%→94.051%). No cross-mechanism comparison is biased; qualitative claims survive. |
| E10 | MiMo column traceability | `verification.md` D5 (`63aa33c5`) | Produced by an uncommitted scratch script; all figures were independently recomputed and are correct, but the column is not reproducible from committed code. |

## F. Standing interpretation rules (from the corrections)

1. **Route scope.** Followup-03's failures are evidence about the OpenCode
   free-tier route, not about Jev generally; followup-04's direct-route results
   are evidence about `jev-1.13.0` as served in its window.
2. **No retroactive completion.** followup-04 cannot fill followup-03's
   UNRESOLVED cells; those remain properties of the free-tier route.
3. **Tariffs are not capability.** Jev's cost edge is $0.042/Mtok input with
   free output vs $0.14/$0.28; both are tier-dependent, promotional facts.
4. **Cross-window.** MiMo (13:09Z–13:56Z) and Jev-direct (later same day) were
   not measured simultaneously; structural comparisons carry that caveat.
5. **Verifier authority.** Where any report prose conflicts with a
   `verification.md`, the verification governs.
