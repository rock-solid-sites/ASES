# RUNBOOK — Jev Phase 1 Diagnostic (issue #565)

Exact commands to reproduce every artefact in this directory, and the hashes to
compare them against. Everything here has been executed from a clean checkout;
the transcript of that test is in §6.

**Two tiers, and the difference matters.** Scoring (tier 1) is offline and
byte-reproducible. The raw run (tier 2) calls live models and is therefore
**not** byte-reproducible — Jev and the general model are both stochastic near
the decision boundary, which preflight P2c/P3 measured directly (0.59 on one
send, 0.61 on the next, same request). Tier 2 reproduces the *method*; it does
not reproduce the *bytes*. Nothing in tier 1 depends on tier 2 being re-run.

---

## 1. Prerequisites

| Requirement | Value | Checked by |
|---|---|---|
| Python | 3.10 or newer, **standard library only** | `python3 -V` |
| Third-party packages | **none** — no `pip install` step exists | `harness/*.py` import only stdlib |
| Network | not needed for tier 1 | §3 |
| API key | not needed for tier 1 | §4 only |

The whole harness is stdlib-only by design. If any `harness/*.py` or
`score.py` import ever needs a wheel, that is a defect, not a prerequisite.

---

## 2. Get the code

The work is on branch `research/jev-phase1-565`. Either read it in place:

```bash
cd /home/claude-code/projects/ASES/.worktrees/jev-phase1
cd research/jev-bounded-judgment/phase1
```

or make a genuinely clean copy, which is what §6 tests:

```bash
git clone --branch research/jev-phase1-565 \
  /home/claude-code/projects/ASES/.worktrees/jev-phase1 \
  /tmp/opencode/jev-phase1-runbook-test
cd /tmp/opencode/jev-phase1-runbook-test/research/jev-bounded-judgment/phase1
```

From here on `P1` means the `phase1` directory. All commands are run from it.

---

## 3. Tier 1 — reproduce the scored outputs (offline, deterministic)

### 3.1 Verify the inputs before trusting anything

```bash
sha256sum cases.ndjson results/jev_raw.ndjson results/baselines_raw.ndjson
```

Expected:

```
7dd4698f4614eee928a1a93cb0e9d33fd77a5c64963593d97b2678cdf5af558c  cases.ndjson
e17ae014f0fc6cc311646dbfd98d5115d41854ddfcb98cfb41268f2da482d3bc  results/jev_raw.ndjson
42f37690ec7ebbca75293ab0a690dc8efd8d5ef8a6a663db632bb05d682bf7ba  results/baselines_raw.ndjson
```

If any hash differs, **stop**. The scoring below will still run, but it will be
scoring data you have not read.

### 3.2 Validate the corpus structurally

```bash
python3 harness/validate_cases.py
```

Expected: a header line reporting `cases=64  sha256=7dd4698f...`, then `PASS`
on all **29** checks, `C1_count_within_60_plus_minus_5` through
`C14_abstain_expected_subset_of_unanswerable`, ending in `29/29 checks passed`
and `VALIDATOR RESULT: PASS`. Any `FAIL` means the corpus no longer satisfies
`schema.md` §2 and nothing downstream is meaningful.

### 3.3 Score

```bash
python3 harness/score.py --self-check --generated-utc 2026-09-26T03:44:59Z
```

`--self-check` scores twice and aborts if the two passes differ, so a
successful exit is itself the determinism proof. `--generated-utc` pins the one
wall-clock value in any output; without it only
`results/manifest.json -> scoring.generated_utc` differs between runs.

Expected on stdout:

```
self-check: scoring is deterministic (byte-identical)
score.py 1.0.0
  grid                       : 64 cases x 5 mechanisms = 320 cells, complete
  routing recompute mismatches: 0
  confidence recheck mismatch : 0
  scored.ndjson sha256        : 662d6ec615b5d9193f905145dc731e095db6c8203418a6fcf3ccdb6dacb179b3
  metrics.json sha256         : 3d2e3ac5bf00acc9c90c2917f59cd59347201547fb13731317658a7db6a3a9ee
  secret scan                 : 0 hits over 14 emitted files (boolean only)
  outputs                     : 15 files
```

### 3.4 Verify the outputs

```bash
sha256sum results/scored.ndjson results/metrics.json results/manifest.json
```

| Artefact | sha256 | Byte-reproducible? |
|---|---|---|
| `results/scored.ndjson` | `662d6ec615b5d9193f905145dc731e095db6c8203418a6fcf3ccdb6dacb179b3` | **yes, unconditionally** |
| `results/metrics.json` | `3d2e3ac5bf00acc9c90c2917f59cd59347201547fb13731317658a7db6a3a9ee` | **yes, unconditionally** |
| `tables/*.md` (11 files + index) | see `results/manifest.json -> outputs_sha256` | **yes, unconditionally** |
| `results/manifest.json` | `d07dad4a00df34c4d5c8598b5cce7057626a0e6694e87f2a136ad9b94a7508ba` | **no — see below** |

`scored.ndjson`, `metrics.json` and every table are pure functions of the raw
input files. They must match, always, with no caveats.

`manifest.json` embeds provenance about *where it was run*, so it cannot be
byte-reproducible across checkouts. Exactly three keys can move:

| Key | Why it moves |
|---|---|
| `git.commit` | The manifest is committed, so the commit it records is always the commit *before* the one that contains it. A self-reference has no fixed point. |
| `git.remote` | A clone from a local path has a local path as its remote; the worktree has the GitHub URL. |
| `scoring.self_check_passed` | `false` if you omit `--self-check`. |

Everything else in the manifest — every input hash, every output hash, the
error and retry counts, the environment notes — is a function of the inputs and
must match. Verify it by diffing the parsed objects rather than the file bytes:

```bash
python3 - <<'PY'
import json
m = json.load(open("results/manifest.json"))
assert m["grid"] == {"cells_complete": True, "n_cases": 64, "n_cells": 320,
                     "n_mechanisms": 5}, m["grid"]
assert m["inputs"]["cases.ndjson"]["sha256"].startswith("7dd4698f")
assert m["outputs_sha256"]["results/scored.ndjson"] == \
    "662d6ec615b5d9193f905145dc731e095db6c8203418a6fcf3ccdb6dacb179b3"
assert m["outputs_sha256"]["results/metrics.json"] == \
    "3d2e3ac5bf00acc9c90c2917f59cd59347201547fb13731317658a7db6a3a9ee"
assert m["secrets"]["scan"]["hits"] == 0
print("manifest OK; commit =", m["git"]["commit"])
PY
```

### 3.5 Prove it twice

Re-score, then check that **nothing but possibly the manifest** moved:

```bash
python3 harness/score.py --self-check --generated-utc 2026-09-26T03:44:59Z >/dev/null
git status --porcelain
```

Expected: either no output at all, or exactly one line naming
`results/manifest.json`. Any other path in that output means a generated file
is not byte-reproducible, which is a real defect — investigate it rather than
re-running.

---

## 4. Tier 2 — re-run the raw mechanisms (live, NOT byte-reproducible)

Only needed to regenerate `results/jev_raw.ndjson` and
`results/baselines_raw.ndjson`. **Do this in a scratch copy, never over the
committed files** — the committed raw data is the evidence of record.

```bash
# 4.0 the key must exist. Never print it, never echo it, never pass it on a
#     command line that lands in a shell history or a process listing.
test -n "$OPENCODE_GO_API_KEY" && echo "key present" || echo "KEY MISSING"

# 4.1 regenerate the corpus into a scratch path and confirm it is identical
python3 harness/gen_cases.py --out /tmp/opencode/jev-cases-repro.ndjson
sha256sum /tmp/opencode/jev-cases-repro.ndjson     # must equal the cases hash

# 4.2 Jev, 64 calls, ~0.6 s each
python3 harness/run_jev.py \
  --cases cases.ndjson --out /tmp/opencode/jev-raw-repro.ndjson

# 4.3 prior + rule + lexical + general model, 64 chat calls
python3 harness/run_baselines.py \
  --cases cases.ndjson --out /tmp/opencode/baselines-raw-repro.ndjson

# 4.4 score the re-run and diff the metrics
python3 harness/score.py --phase1-dir . --no-tables   # uses the committed raw
```

Point `score.py` at the re-run instead of the committed raw by copying them
into a scratch tree, or by running the runners with `--out` inside a scratch
copy of this directory. `score.py` always reads
`results/jev_raw.ndjson` + `results/baselines_raw.ndjson` from `--phase1-dir`.

### Gotchas that will otherwise cost you an hour

1. **`harness/gen_cases.py` and `harness/preflight.py` have no `--help`.** They
   take no arguments and act immediately: `gen_cases.py` **overwrites
   `cases.ndjson`**, and `preflight.py` makes ~13 **live API calls** and writes
   to `/tmp/opencode/preflight_evidence.json`. Do not probe them with `--help`.
   Both are deterministic/harmless in effect — `cases.ndjson` regenerates
   byte-identically — but the live calls are not free and the overwrite is not
   obviously safe.
2. **A `User-Agent` header is mandatory.** urllib's default
   `Python-urllib/3.10` is refused by Cloudflare with `HTTP 403 / "error code:
   1010"`. `harness/common.py` sets one; any reimplementation must too.
3. **The Go chat endpoint is dead with this credential.** `POST
   https://opencode.ai/zen/go/v1/chat/completions` returns `HTTP 403` with "An
   active OpenCode Go subscription is required to use Go models." The same
   model ID works on `https://opencode.ai/zen/v1/chat/completions`. That is a
   route change, not a model substitution, and `run_baselines.py` defaults to
   the working route.
4. **`max_tokens` for the general model must be 256, not 16.** At 16 the
   reasoning model spends the whole budget on `reasoning_content` and returns
   `HTTP 200` with empty content — 14/64 cells failed that way. The failure is
   also non-deterministic at 16 (the same request returned content at 16,
   empty at 64, content at 256 on different sends at temperature 0). The
   pre-fix run is preserved at
   `results/baselines_raw_prefix_max_tokens16.ndjson` with a `_meta` row; do
   not delete it, it is the evidence that this was a harness defect.
5. **Jev is not a chat model.** `POST /zen/v1/chat/completions` with
   `jev-1.13-free` returns `HTTP 403 FreeTierError`. Its endpoint is
   `/zen/v1/systemone` and its request shape is
   `{model, state, questions}`.
6. **`choice.criteria` is a dict; `score.criteria` is a list.** Swapping them
   returns `HTTP 422` (`dict_type` / `list_type`). `noul` takes no `criteria`
   at all. See `schema.md` §1.

---

## 5. Verifier checklist

A clean-clone reproduction passes when all of these hold.

| # | Check | Expected |
|---|---|---|
| 1 | `python3 harness/validate_cases.py` | `29/29 checks passed`, `VALIDATOR RESULT: PASS`, `cases=64` |
| 2 | input hashes (§3.1) | all three match |
| 3 | `python3 harness/score.py --self-check` | exits 0, prints the determinism line |
| 4 | grid completeness | `320 cells, complete`; the scorer aborts on any missing, duplicated or unknown-case cell |
| 5 | routing recomputation | `routing recompute mismatches: 0` over 60 area-D cells |
| 6 | confidence recomputation | `confidence recheck mismatch : 0` over 319 cells |
| 7 | `scored.ndjson` hash | `662d6ec6...` |
| 8 | `metrics.json` hash | `3d2e3ac5...` |
| 9 | `git status` after re-scoring | empty, or only `results/manifest.json` |
| 10 | secret scan | `0 hits over 14 emitted files` |
| 11 | manifest structural assert (§3.4) | passes |
| 12 | tier-2 (optional) | Jev reachable, all three question types schema-resolved; the general model reachable on the Zen chat route |

Checks 4, 5, 6 and 11 are the ones worth writing a test around: they are the
assertions that would catch a corrupted or silently altered input, and the
scorer treats a failure in any of the first three as fatal rather than as a
warning.

---

## 6. Clean-checkout test — performed, with result

Performed 2026-09-26 on Python 3.10.12 / Linux x86_64, into a fresh clone
outside the worktree. Executed exactly as written below.

```bash
rm -rf /tmp/opencode/jev-phase1-runbook-test
git clone --branch research/jev-phase1-565 \
  /home/claude-code/projects/ASES/.worktrees/jev-phase1 \
  /tmp/opencode/jev-phase1-runbook-test
cd /tmp/opencode/jev-phase1-runbook-test/research/jev-bounded-judgment/phase1
sha256sum cases.ndjson results/jev_raw.ndjson results/baselines_raw.ndjson
python3 harness/validate_cases.py
python3 harness/score.py --self-check --generated-utc 2026-09-26T03:44:59Z
sha256sum results/scored.ndjson results/metrics.json results/manifest.json
git -C /tmp/opencode/jev-phase1-runbook-test status --porcelain
```

**Result: PASS on every check, with two corrections found by running it.**

Observed in the clean clone:

- All three input hashes matched §3.1 exactly.
- `validate_cases.py` reported `29/29 checks passed` and
  `VALIDATOR RESULT: PASS`. *The first draft of this runbook claimed 14
  checks; the real count is 29, and §3.2 and §5 now say so.*
- `scored.ndjson` came back at `662d6ec6...` and `metrics.json` at
  `3d2e3ac5...` — identical to the worktree, no caveats.
- All eleven tables plus `INDEX.md` came back identical: after re-scoring,
  `git status --porcelain` named **only** `results/manifest.json`.
- The manifest's `manifest.json` differed from the worktree copy in exactly
  **one** key, `git.remote`, because a clone from a local path has a local path
  as its remote. A key-by-key comparison of the two parsed objects confirmed
  every other field matched, including all input and output hashes.
- Secret scan: `0 hits over 14 emitted files`.
- No network access and no API key were used at any point.

Two defects in this runbook were found *by running it* and are fixed above: the
validator check count (14 → 29) and the claim that `manifest.json` is
byte-reproducible (it is not, and §3.4 now explains the three keys that move).

Tier 2 was **not** re-run in the clean clone: it costs 128 live model calls and
cannot reproduce bytes by construction, so a clean-clone pass would prove
nothing that §5 checks 1–11 do not already prove. The live-call path is covered
by the preflight evidence in `results/preflight_evidence.json` and by the
committed raw run.

---

## 7. What this runbook does not cover

- **Multi-question requests.** One question per case throughout. The schema
  supports a list; the "latency is flat in question count" claim in `README.md`
  is untested here.
- **`state` as an object**, and **`instructions` as object or array.** Only the
  string forms were exercised.
- **Statistical significance.** At n=64 (50 answerable) no significance test is
  claimed anywhere, and none should be added downstream without a power
  calculation first.
- **A per-area or per-difficulty prior.** `prior` is global; a stratified prior
  would be a stronger baseline and is a fair Phase 2 question.
- **Tier-2 byte reproduction.** Structurally impossible; see the header.
