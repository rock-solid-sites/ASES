# Phoenix Grove adversarial review — knowledge-index prototype (2026-11-19)

**State:** review in progress; independent reviewer hypotheses are not verified defects, and neither experimental merge nor cross-project service adoption is approved.

## Fixed review boundary

- Target: [ASES draft PR #61](https://github.com/rock-solid-sites/ASES/pull/61), source commit `bef2782144ca5553b1632c6f0747169d5933e1ff`.
- Private independent-runner evidence: [Actions run 44577774247](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44577774247). Each reviewer received a bounded, source-pinned packet without the other reviewers' verdicts. Source code was **not executed** by the reviewers.
- DeepSeek `deepseek-v4.1-flash-1017`, identity/correctness: original job 135749867039, succeeded, 27,835 report bytes; output contains some self-corrected and unsupported claims and requires triage.
- GLM `glm-5.3-flash`, architecture: original job 135749867049, succeeded, 4,831 report bytes; review explicitly did not inspect several implementation files.
- MiMo `mimo-v2.6-flash`, security: original job 135749866521, **failed** with timeout exit 124 at 250 seconds and zero report bytes. Authorized single-job retry is job 135755890404; outcome pending at this checkpoint. The failed attempt is not a review verdict.
- Provider-side billed cost and authoritative token breakdown: **unknown**. Codex read-only sandbox is not proof of deny-all model tool permissions.

## Initial source-checked hypotheses for executable falsification

These mechanisms are visible in the pinned source, **not yet independently demonstrated by new red tests**. Scope, severity and intended contract remain subject to review.

1. **Out-of-root source inclusion:** `scripts/knowledge_index/indexer.py:68-76,96-105` constructs source paths from unsanitized `include_paths` entries. Markdown may be read before `relative_to(root)` rejects escape; JSONL has no corresponding confinement check. Proposed negative control: create `../outside.jsonl`, include it explicitly, and require deterministic rejection without indexing content.
2. **Malformed JSONL loses controlled errors:** `indexer.py:101-110,196-224` calls `data.get` on any syntactically valid JSON value, then hashes IDs/endpoints before validating their type. Proposed controls: lines `42`, `[]` and `{"id":[]}`, expecting domain-specific `IndexErrorData` rather than raw `AttributeError`/`TypeError`.
3. **Metadata identity punctuation:** `indexer.py:45-57` uses `strip('\"\\'')` on scalar metadata; unmatched trailing apostrophes can change a declared ID. Proposed control: an unquoted `knowledge_id` ending in an apostrophe and a registry matching that exact value must preserve identity.
4. **Raw FTS query syntax:** `indexer.py:258-263` passes the caller's term to `search MATCH ?` without escaping or handling FTS syntax errors. Test quotation marks, incomplete operators and user-literal punctuation; decide whether to support full FTS expressions or literal search, and report invalid syntax predictably.
5. **Registry absence and evidence status are not independently enforced:** `registry.py:12-15` returns an empty mapping when `identities.json` is missing; `indexer.py:222-227` checks `evidence_refs` is a list but not that it contains evidence. These may be intentional experimental boundaries. Record the decision explicitly rather than treating candidate edges/IDs as reviewed authority.

## Disposition gate

Before merging the **experimental** source, reproduce prioritized cases with minimal negative tests and distinguish genuine defects from intentional prototype limitations and reviewer false positives. Re-run the 28-test suite plus new tests after any repair. A merged experiment must **not** approve a hosted index, ACL enforcement, source revocation or cross-project authoritative relation service. Planning gate: Projektor **ASES-19**.

_This document will be updated with the MiMo retry outcome, reviewer quality assessment, reproduction and repair links. No production integrations are modified by this record._
