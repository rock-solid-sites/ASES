# Phoenix Grove adversarial review — knowledge-index prototype (2026-11-19)

**State:** all three independent model reports delivered (five invocations); source-grounded hypotheses require executable reproduction. Neither experimental merge nor cross-project service adoption is approved.

## Fixed review boundary

- Target: [ASES draft PR #61](https://github.com/rock-solid-sites/ASES/pull/61), source commit `bef2782144ca5553b1632c6f0747169d5933e1ff`.
- Private independent-runner evidence: [Actions run 44577774247](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44577774247). Each reviewer received a bounded, source-pinned packet without the other reviewers' verdicts. Source code was **not executed** by the reviewers.
- DeepSeek `deepseek-v4.1-flash-1017`, identity/correctness: original job 135749867039, succeeded, 27,835 report bytes; output contains some self-corrected and unsupported claims and requires triage.
- GLM `glm-5.3-flash`, architecture: original job 135749867049, succeeded, 4,831 report bytes; review explicitly did not inspect several implementation files.
- MiMo `mimo-v2.6-flash`, security: original job 135749866521 and operator-authorized same-job retry 135755890404 each **failed** with timeout exit 124 at 250 seconds and zero report bytes. A clean, narrower one-model [Actions run 44580649550](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580649550), job 135760047565, **succeeded**, exit 0, 2,231 report bytes (SHA-256 `03289753a6c7c46f4747c36b5f43feb51a46ef942c29246cd278f79995e969fb`) in about 191 seconds. The revised prompt was 22,008 bytes (SHA-256 `7fb029f7d35d3006ff3d10b2ae7b5d986fe99e85fdaf1d62dd5123d84a853d53`) with a bounded 405-second deadline. Original prompt: 29,835 bytes. The two zero-report timeouts are not review verdicts.
- Provider-side billed cost and authoritative token breakdown: **unknown**. Codex read-only sandbox is not proof of deny-all model tool permissions.

## Initial source-checked hypotheses for executable falsification

These mechanisms are visible in the pinned source, **not yet independently demonstrated by new red tests**. Scope, severity and intended contract remain subject to review.

1. **Out-of-root source inclusion:** `scripts/knowledge_index/indexer.py:68-76,96-105` constructs source paths from unsanitized `include_paths` entries. Markdown may be read before `relative_to(root)` rejects escape; JSONL has no corresponding confinement check. Proposed negative control: create `../outside.jsonl`, include it explicitly, and require deterministic rejection without indexing content.
2. **Malformed JSONL loses controlled errors:** `indexer.py:101-110,196-224` calls `data.get` on any syntactically valid JSON value, then hashes IDs/endpoints before validating their type. Proposed controls: lines `42`, `[]` and `{"id":[]}`, expecting domain-specific `IndexErrorData` rather than raw `AttributeError`/`TypeError`.
3. **Metadata identity punctuation:** `indexer.py:45-57` uses `strip('\"\\'')` on scalar metadata; unmatched trailing apostrophes can change a declared ID. Proposed control: an unquoted `knowledge_id` ending in an apostrophe and a registry matching that exact value must preserve identity.
4. **Raw FTS query syntax:** `indexer.py:258-263` passes the caller's term to `search MATCH ?` without escaping or handling FTS syntax errors. Test quotation marks, incomplete operators and user-literal punctuation; decide whether to support full FTS expressions or literal search, and report invalid syntax predictably.
5. **Registry absence and evidence status are not independently enforced:** `registry.py:12-15` returns an empty mapping when `identities.json` is missing; `indexer.py:222-227` checks `evidence_refs` is a list but not that it contains evidence. These may be intentional experimental boundaries. Record the decision explicitly rather than treating candidate edges/IDs as reviewed authority.

## Focused MiMo findings and confidence boundaries

- **Out-of-root JSONL import** (`indexer.py:96-108`): MiMo independently identified the same path-confinement gap raised by DeepSeek. Static inspection confirms an explicitly supplied `../outside.jsonl` path can be read without a root-confinement check. Next: a minimal negative-control test including valid, public-visibility JSONL and a symlink escape, asserting rejection before ingestion. This remains an unexecuted reproduction proposal.
- **Unescaped `authority` in generated graph Markdown** (`graph_view.py:74-77`): MiMo identified that a public node's `authority` string is appended into the Markdown source-reference line without HTML/Markdown escaping. Source inspection confirms the interpolation, while the separate HTML renderer uses inert JSON and DOM text methods. A raw-markup output defect is plausible; external network loading or XSS is **renderer-dependent and not demonstrated**. Next: an adversarial `authority: <img src=//tracker.invalid/p>` test of `render_mermaid`, plus representative Markdown renderer tests; do not generalize this to the CSP-protected HTML view.
- MiMo reported **two** material findings, not a claim of full-system audit. Its report was mechanically nonempty and model-routed, but its assertions must pass source-grounded falsifying tests before being promoted to confirmed bugs.

## Disposition gate

Before merging the **experimental** source, reproduce prioritized cases with minimal negative tests and distinguish genuine defects from intentional prototype limitations and reviewer false positives. Re-run the 28-test suite plus new tests after any repair. A merged experiment must **not** approve a hosted index, ACL enforcement, source revocation or cross-project authoritative relation service. Planning gate: Projektor **ASES-19**.

_All reviewer outcomes are recorded. The next gate is to run minimal falsifying tests and separate genuine source defects, intentionally limited experimental semantics, and reviewer false positives. No repairs, service authorization, or production integrations were made in this review session._

## Operator-requested additional MiMo invocation — repeated success

- [Focused MiMo workflow rerun, job 135765340769](https://github.com/rock-solid-sites/ases-plugins/actions/runs/44580649550/job/135765340769), same frozen ASES source `bef2782144ca5553b1632c6f0747169d5933e1ff` and same focused review prompt: **22,008 bytes**, SHA-256 `7fb029f7d35d3006ff3d10b2ae7b5d986fe99e85fdaf1d62dd5123d84a853d53`.
- Model `pgs2/mimo-v2.6-flash` completed **exit 0**, report **2,810 bytes**, SHA-256 `8bf2e823194dbfac029fa81d15ddf7c6097541127a5be7989c20d4e82d2b288e`; started 2026-11-19 17:54:36 UTC, ended 17:57:41 UTC (about 185 seconds). Provider-side billing and input/output token accounting remain unknown.
- The independent response reproduced the prior source-path/symlink confinement and unescaped `authority` in rendered Markdown concerns. The impact of injected HTML depends on the downstream Markdown renderer; the separate generated HTML renderer is not proven compromised.
- **New conditional hypothesis — JSONL meta-edge public classification spoof:** `indexer.py:105-108,147-153` may classify a user-supplied edge with a `meta:` ID and no explicit visibility as public if both endpoints are public; `graph_view.py` may then project that candidate edge with unsupported explanation and empty `evidence_refs`. This is a defect only if imported JSONL is not pre-authorized as a trusted source. Run a minimal valid-node/edge negative test and decide the trust/authority policy before classifying it as a vulnerability.
- The additional rerun is **not** a fourth independent model, and no extra consensus is inferred from duplicate MiMo responses. At this checkpoint: **six total invocations**, three delivered reviewer models, two earlier MiMo timeouts, and two successful MiMo reports. All reviewer findings still require reproducible tests before code fixes are accepted.
