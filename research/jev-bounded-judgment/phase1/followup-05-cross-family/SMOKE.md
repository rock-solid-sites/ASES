# followup-05 — monitored smoke test (4 cases, 4 arms)

- **Issue:** #565 · **Date:** 2026-09-27 · **Status:** complete
- **Corpus:** frozen, `sha256 7dd4698f…f558c`, unmodified
- **Subset:** 4 cases spanning every parse branch — `a-dist1` (noul),
  `d-01` (choice), `a-h04` (score), `a-e01` (noul)
- **Purpose:** verify each arm is reachable and well-behaved *before* spending
  the full 64-case run, per the operator's instruction to monitor the free
  models closely.

## 1. Result: 3 of 4 arms runnable; `longcat` is structurally unavailable

| arm | catalog ID | outcome | HTTP | note |
|---|---|---|---|---|
| Big Pickle | `opencode/big-pickle` | **PASS** 4/4 | 200 | agent step window 2.7 s |
| Ling 3.0 Flash | `opencode/ling-3.0-flash-fin-free` | **PASS** 4/4 | 200 | 5.5 s |
| MiMo V2.6 Flash | `opencode/mimo-v2.6-flash-free` | **PASS** 4/4 | 200 | 7.0 s (transport control) |
| Longcat 2.5 | `opencode-go/longcat-2.5-preview-free` | **FAIL 0/4** | **403** | *no Go entitlement* |

### `longcat-2.5-preview-free` — negative result, preserved

```
APIError: Upstream request failed: An active OpenCode Go subscription is
required to use Go models.   statusCode 403, isRetryable: false
metadata.url = https://opencode.ai/zen/go/v1/chat/completions
```

Reproduced twice: once in the batch run, once as an isolated single-turn
probe with `--print-logs --log-level ERROR`. Not a rate limit, not a prompt
problem, not a malformed request. The account has **no active OpenCode Go
subscription**, so the Go route is closed regardless of the model's listed cost.

The catalog lists this model as `status=active`, `cost 0/0/0`. **Catalog
presence is not entitlement.** This is the second independent instance of that
gap in this followup (the first being the free-Zen chat gate in `RECON.md` §1),
and it is the same failure class recorded for the Go route in followup-02
(`BLOCKER.md` R2). A `cost=0` field is a tariff statement, not an access
guarantee.

**Consequence:** the arm is dropped, not retried and not substituted without
operator approval. Followup-05 therefore proceeds with **two cross-family arms
(`big-pickle`, `ling`) plus `mimo` as the transport control.**

## 2. Validation gates — all passed on all three viable arms

Every answer was pushed through the **frozen** `parse_general()` from
`harness/run_baselines.py`. No scorer code was modified.

| check | big-pickle | ling | mimo |
|---|---|---|---|
| text block found in event stream | ✅ | ✅ | ✅ |
| row count == expected | ✅ 4 | ✅ 4 | ✅ 4 |
| no duplicate `case_id` | ✅ | ✅ | ✅ |
| all `case_id`s present | ✅ | ✅ | ✅ |
| unparsable lines | 0 | 0 | 0 |
| **frozen parser accepts** | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 |

Acceptance by the frozen parser is the load-bearing check: it is what allows
`harness/score.py` to consume these arms unchanged.

## 3. Ground-truth containment

`smoke/build_tasks.py` emits only `id`, `question_type`, `instructions`,
`criteria` and the exact user message. It strips `ground_truth`,
`control.deciding_fact`, `difficulty_note` and `routing` — all four leak the
answer, in whole or in part. A leak guard scans the serialised output for
`ground_truth`, `deciding_fact`, `difficulty_note`, `rationale` and
`answerable` and **exits non-zero** if any survives. It reported `leak_guard=OK`.

The user-message text is produced by calling the frozen
`build_general_request()`, not by re-implementing it, so it is identical by
construction to what the direct-HTTP arms sent.

## 4. Answers observed

| case | type | big-pickle | ling | mimo |
|---|---|---|---|---|
| `a-dist1` | noul | NO | NO | NO |
| `d-01` | choice | build | build | build |
| `a-h04` | score | low | low | low |
| `a-e01` | noul | YES | YES | YES |

All three arms agree on all four. **This is not evidence about the arms.** Four
cases, deliberately chosen to exercise the parse branches, are far too few to
separate models — and the 2-arms-agree observation is exactly the kind of
number this programme forbids quoting as a result. Recorded only as evidence
that the pipeline is wired correctly end to end.

## 5. Effect on the pre-registered decision rule

`RECON.md` §6 requires a majority of cross-family arms for a "supported" verdict
and **all** arms for an "unsupported" verdict. With two cross-family arms a
majority is undefined and a split is indistinguishable from inconclusive.

**Rule as applied, fixed before the full run:** a verdict requires **both**
cross-family arms to land in the same band. A split is reported as
**inconclusive** and is not resolved by privileging one arm. This is
strictly more conservative than the three-arm rule it replaces, so the reduced
arm count cannot manufacture a positive finding for Jev.

The transport control (`mimo`) is not a cross-family arm and does not vote on
the band. It is reported separately, as the measured route/framing delta
against followup-02.

## 6. Cost note

The smoke test consumed 4 cases × 4 arms. The `longcat` failure consumed 2
wasted invocations (one batch, one isolated probe) and produced a preserved
negative result rather than a silent gap.

## 7. Next step

Proceed to the full 64-case run for the three viable arms, with the
completeness gate (`exactly 64 rows, all ids present, no duplicates, frozen
parser accepts`) applied per arm before any cell enters scoring. No case text,
ground truth, band, or scorer code changes.
