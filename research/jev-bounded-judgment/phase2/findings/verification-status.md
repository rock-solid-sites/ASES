# Phase 2 verification status

- **Issue:** #570 · **Date:** 2026-09-27
- **Independent verifier:** `opencode/muse-spark-1.3-contributor-free` (family
  `muse-free`), which is a different model family from the artefact producer
  (the orchestrator)
- **Overall status:** **PARTIALLY VERIFIED — one required element is OUTSTANDING**

## Summary against the required gates

| required element | status | by whom |
|---|---|---|
| reproduce representative source→structure transformations | **DONE, independently** | Muse Spark |
| reproduce the final reported statistics | **OUTSTANDING** — orchestrator cross-check only | orchestrator |
| adversarial judgement of the claims | **OUTSTANDING** | — |
| clean-clone reproduction, verified | **DONE** | orchestrator |
| harness/corpus/frozen unmodified | **DONE** | orchestrator |
| no credential values in artefacts | **DONE** | orchestrator |

The stop condition requires independent verification. **It is not met for the
statistics.** Nothing below should be read as closing Phase 2.

## 1. What the independent verifier DID establish

`verification.md` Step 1 is complete and independent. Six (module, function)
pairs were checked by reading `corpus/*.py` directly, forming an independent
reading, and only then comparing to the extractor:

| pair | verdict |
|---|---|
| `shlex.__init__` | extractor correct |
| `split` | extractor correct |
| `JSONEncoder.iterencode` | extractor correct |
| `TextWrapper._wrap_chunks` | extractor correct |
| `dataclass` | extractor correct |
| `RawConfigParser._read` | extractor correct |

**6/6 confirmed.** The verifier recorded that **every first-pass disagreement
resolved in the extractor's favour** on re-inspection with cited line numbers,
and stated plainly: "the extractor survived adversarial re-checking; my initial
readings were the faulty ones." It declined to manufacture faults.

It also produced three documentation-grade observations that are worth keeping:

1. `params` are emitted alphabetically, not in `def` order. Benign, but the
   order is not recoverable from the structure.
2. `assigned_locals`, `has_try`, `has_raise` and `max_nesting` **include
   nested-def bodies**, while call edges **exclude** them. This asymmetry is
   intentional and visible in the code, but it is surprising and is now a
   candidate for an explicit note in the README.
3. `elif` opens a nesting level while `else` does not, so `max_nesting`
   penalises elif-chains. This is what produces `iterencode` = 4 and
   `_read` = 6.

**HOW CERTAIN:** evidence-based (hand re-derivation per function, then
mechanical comparison). **WHAT-NOT-TESTED:** only these six pairs; the other
~180 functions, the byte output of `render_struct`, and the frozen digests.

## 2. The outstanding element, and why

The verifier was stopped by an external rate limit after completing Step 1. It
announced it would re-derive the statistics and the turn ended.

Exact signature from `~/.local/share/opencode/opencode.log`:

```
level=ERROR message="stream error" providerID=opencode
  modelID=muse-spark-1.3-contributor-free agent=build
  error.error="AI_APICallError: Rate limit exceeded. Please try again later."
level=WARN  message=retry provider=opencode attempt=1
  code="Rate limit exceeded. Please try again later." nextDelay=15780000
level=ERROR ... "AI_RetryError: Failed after 3 attempts. Last error:
  Rate limit exceeded. Please try again later."
```

`nextDelay=15780000` ms is **≈ 4.4 hours**. A subsequent liveness probe returned
no text and no error event, consistent with the limit still being in force.

**Update 21:42Z — the blocker widened.** A second attempt to place the
verification on the *other* designated model, `opencode/mimo-v2.6-flash-free`,
also failed:

```
21:39:03Z ERROR providerID=opencode modelID=mimo-v2.6-flash-free agent=build
  error.error="AI_APICallError: Rate limit exceeded. Please try again later."
21:39:03Z WARN  message=retry attempt=1 nextDelay=8457000
```

Both designated verifiers are therefore blocked, clearing at approximately the
same moment (muse ~23:59Z, mimo ~23:58Z), which points to an account-level
free-tier quota rather than a per-model fault. This is the third distinct
free-model failure mode in this programme, after `longcat` (no Go entitlement)
and MiMo's earlier task-completion failures.

Two live, undesignated, cross-family free models were confirmed available by
liveness probe: `opencode/nemotron-3-ultra-free` and
`opencode/nemotron-3.5-lightning-free`. The orchestrator did **not** use either.
Using an undesignated model as the formal verifier is an operator decision; per
`model-discipline.md` the correct response to an unreachable approved model is to
stop and report, not to shortlist a replacement.

The full blocker record, with log signatures and both retry delays, is appended
to `verification.md` under a heading that marks it as orchestrator-authored, so
it cannot be mistaken for verifier evidence.

**Paid escalation is not available.** `model-discipline.md` permits escalation
after a concrete capability failure, but the `opencode-go/` route returns
`403 "An active OpenCode Go subscription is required"` on this account, so
there is nowhere to escalate to. Per the recorded rule, the failure is reported
rather than routed around.

**How to discharge it:** re-run `VERIFY-BRIEF-2.md` with
`opencode/muse-spark-1.3-contributor-free` once the limit clears. The brief is
written to append to the existing `verification.md` and to skip Step 1.

## 3. Orchestrator cross-check of the statistics — NOT independent verification

To make progress on the blocked element without misrepresenting it,
`harness/crosscheck_stats.py` re-derives **every reported statistic** from
`results/*.ndjson` **without importing `harness/score.py`**, so a bug in the
scorer's arithmetic or grouping surfaces as a mismatch rather than being
reproduced by shared code.

```
checks run : 64
mismatches  : 0
```

It covers per-condition n/accuracy/state bytes/input tokens/latency/cost, the
per-case-type accuracy table, all four exact McNemar p-values, the distraction
degradation counts, the intrinsic case-group assignment and accuracies, the
probability-behaviour counts, the unanswerable answering and abstention counts,
the decided-vs-undecided split by unanswerable class, and two integrity
invariants: that no `ground_truth is None` cell was scored correct, and that no
`not_admissible` cell carries a parsed answer.

**This is an orchestrator-side cross-check and is explicitly NOT independent
verification.** The orchestrator wrote both the harness and the cross-check, so
a shared misreading of the question semantics would survive both. What it does
establish is that the scorer's arithmetic, grouping and integrity guards are
internally sound and that the reported numbers follow from the committed raw
evidence.

## 4. Clean-clone reproduction — verified

`reproduce.sh` was run in a **fresh `git clone`** at `/tmp/opencode/p2-clone`
(clone of branch `research/jev-phase1-565`, clean checkout, no uncommitted
files):

```
OK  frozen/cases.json           0e8585f85f4d2452101a1899ec0208ce5a10d48f113ccd3623504fe389bdf584
OK  frozen/admissibility.json   507bf023f2efb13ed2d91da4ba729d61d5441fae5065a9a6c44b587881685fbd
OK  metrics.json reproduced     2ce8ac4ee19a9445a9d67aa49437ba77bf377f8c7594f9b90e5bc29ea743f730
REPRODUCTION OK (tier 1)
```

The case set and admissibility matrix regenerate to the committed digests
exactly, and the metrics reproduce byte-identically from the committed raw
results. Tier 2 (live re-run) additionally needs `TYPESAFE_API_KEY` resolvable
from `~/.secrets/typesafe.env`; only that path is named, never a value.

## 5. Operational failures worth recording

### 5.1 Both designated free models fail the same way: they announce and stop

Across four verification/cross-check dispatches, neither designated free model
ever delivered a file on the first attempt:

| model | dispatch | outcome |
|---|---|---|
| `mimo-v2.6-flash-free` | 6-function extractor cross-check, attempt 1 (clean clone) | Crosslink **HALT** — the clone has no `issues.db`, so `crosslink-guard` blocked bash; 12 tool calls, no write |
| `mimo-v2.6-flash-free` | same, attempt 2 (real worktree) | 12 tool calls, read 4 of 6 functions, stopped at "Now let me read the remaining three functions"; **no write** |
| `mimo-v2.6-flash-free` | 1-function minimal task | 8 tool calls, **no text output at all**, no write |
| `muse-spark-1.3-contributor-free` | full 4-step verification, attempt 1 | 16 tool calls, completed Step 1, stopped at "now re-deriving the reported statistics"; **no write** |
| `muse-spark-1.3-contributor-free` | same, attempt 2 (hardened brief) | **delivered** `verification.md` Step 1, 11,691 bytes |

**Concrete capability failure in `mimo-v2.6-flash-free`:** it could not complete
a bounded six-function reading task in two attempts, and produced no output at
all on a single-function task. This is a capability limit on a designated free
model, not a prompt or environment fault. Reported, not escalated around,
because the escalation route is unavailable.

### 5.2 The fix that worked: force incremental writes to disk

A brief change fixed it. Adding an explicit section requiring the model to
**append each step's results to disk immediately, and never to announce a next
step before the current step is written**, converted a 0-byte outcome into a
complete Step 1. The failure mode is that these models treat an announced
intention as a turn ending; a partial file is recoverable and a chat summary is
not.

This is worth carrying into every future dispatch to a free model.

### 5.3 A clean clone is not a valid Crosslink worktree

The clone lacks `.crosslink/issues.db`, so any bash use inside it HALTs under
`crosslink-guard`. Reproduction and verification must run in the real worktree,
or the clone must be initialised for Crosslink. This cost one full dispatch.

## 6. What is deliberately NOT claimed

- That Phase 2 is verified. It is partially verified.
- That the statistics have had an independent verdict. They have had an
  orchestrator cross-check only.
- That the claims have survived adversarial review. `findings/findings.md`
  section 8's verdict table has not been independently challenged.
- That the extractor is correct beyond the six checked functions.
