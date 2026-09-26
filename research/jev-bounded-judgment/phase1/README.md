# Jev Phase 1 Diagnostic — Bounded Judgment vs Cheaper Mechanisms

**Crosslink issue:** #565
**Status:** in progress — dispatched to builder (see `DISPATCH.md`)
**Started:** 2026-09-26
**Scope:** Phase 1 only. Stop after one reproducible ~60-case diagnostic run.

## Question

Where, if anywhere, does Jev (`jev-1.13-free`, TypeSafe AI System One via
`POST https://opencode.ai/zen/v1/systemone`) add value beyond cheaper
deterministic/lexical mechanisms, and does its uncertainty support escalation?
Neither a positive nor a negative conclusion is assumed.

## Scope (from issue #565)

- **A. Cheap-baseline comparison** (measured prior/majority -> deterministic rule
  -> lexical baseline -> Jev -> cheap general model). Metric = incremental gain
  over the cheapest preceding mechanism.
- **B. Abstention/escalation**: coverage vs error at thresholds 0.70/0.80/0.90/0.95;
  coverage at 1/5/10% error budgets.
- **C. Contrastive/causal perturbations**: paired cases differing only in the
  deciding fact, plus irrelevant-change controls.
- **D. Workflow routing**: Foreman-like states (build/review/investigate/repair/
  redesign/escalate) with deterministic legality computed BEFORE Jev sees a case.
- **Adversarial controls**: option reorder, opaque label rename, distractor text,
  evidence removal, noise injection.
- Total: ~60 synthetic cases, no personal content, no secrets.

## Deliverables

1. `schema.md` — reusable case/result schema for Phases 2–4 (derived by builder).
2. `cases.ndjson` — the ~60 cases with ground truth and control metadata.
3. `harness/` — deterministic validation, Jev client, baseline engines, scoring.
4. `results/` — raw Jev responses (full distributions), latency + usage, baseline
   outputs, scored records, run manifest with hashes. Never reduced to pass/fail.
5. `tables/` — summary tables (incremental gain, coverage/error, perturbations,
   routing legality).
6. `findings.md` — supported / provisional / limitations / counterexamples /
   next-phase questions.
7. `verification.md` — independent re-run verdict (separate agent).
8. `RUNBOOK.md` — exact reproduction commands.

## Established interface facts (recon 2026-09-26)

- Jev is NOT a chat model. Chat/completions returns 403 FreeTierError for it.
- Endpoint: `POST https://opencode.ai/zen/v1/systemone` with
  `Authorization: Bearer $OPENCODE_GO_API_KEY` (env var; never print its value).
- Request: `{model, state, questions: {qid: {type: noul|choice|score,
  instructions, criteria}}}`. `state` may be str or object; `instructions` may be
  str/object/array.
- Response: `noul -> {noul: P(yes) in [0,1]}`; `choice -> {choice,
  probabilities, confidence}`; `score -> {score, confidence, legend,
  probabilities}`; plus `usage.input_tokens/output_tokens`.
- `confidence` is reportedly DERIVED from the probability vector
  (~(n*max(p)-1)/(n-1)). Must be verified empirically and reported.
- Observed latency ~0.6 s, flat in question count.
- Free/Unlimited tier. No OpenCode client needed; direct HTTP is deterministic.
- Cheap general model baseline: `space-bunny-free` via
  `POST https://opencode.ai/zen/go/v1/chat/completions` (OpenCode Go key); smoke-
  test before use and record exact model ID in the manifest.

## Model discipline / cost record

- Catalog refreshed 2026-09-26 ~02:31Z via `opencode models --verbose --refresh`.
- Non-Jev work approved by operator for this task: **Space Bunny Free**
  (`opencode-go/space-bunny-free`), provider OpenCode Go, cost fields
  input 0 / output 0 / cache read 0 / write 0, context 1,048,576, reasoning on,
  tool calling on.
- Jev `jev-1.13-free` is Free/Unlimited-tier; usage tokens are still recorded.
- Delegations are sequential, bounded, and committed to git; no pushes.

## Constraints

- Deterministic tooling for construction/execution/scoring/logging.
- Do not optimize toward Jev looking good; preserve negative and failed results.
- No extrapolation beyond sample support; separate train/dev/test and keep
  contrastive families in one split.
- No secrets and no personal data in artifacts or logs.
