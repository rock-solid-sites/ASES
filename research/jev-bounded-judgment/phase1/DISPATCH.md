# Dispatch Record — Jev Phase 1 (issue #565)

Per-launch approval basis: operator instruction 2026-09-26 — "Use the free
Spacebunny models to do all non-Jev work." Model verified in refreshed catalog
before each launch. All delegations are bounded, sequential, and checkpointed
by git commits in this worktree (`research/jev-phase1-565`). No pushes.

## D1 — Builder: schema, cases, harness, baselines, raw run

- Agent: `space-bunny` subagent (OpenCode)
- Model: `opencode-go/space-bunny-free` (Space Bunny Free)
- Cost fields at dispatch: input 0 / output 0 / cache read 0 / write 0
- Reasoning: on; tool calling: on; context 1,048,576
- Catalog refreshed: 2026-09-26 ~02:31Z
- Assigned paths: `research/jev-bounded-judgment/phase1/**` only
- Status: dispatched 2026-09-26
- Deliverable: deliverables 1–5 and 8 of README, raw run complete, committed
- Result: (pending)

### D1 preflight — 2026-09-26, OBSERVED

Evidence file (verbatim bodies): `results/preflight_evidence.json`.
Branch `research/jev-phase1-565`, HEAD at preflight
`70d50ce4846ebb2164614dc0c38637acd2dfc3b0`. Python 3.10.12, stdlib only.

**P1 — key.** `OPENCODE_GO_API_KEY` = **SET** (length 67). Value never printed
or written to any artefact.

**P2 — Jev smoke, `POST https://opencode.ai/zen/v1/systemone`.** All 200.

| Probe | State | `noul` | latency_ms | tokens in/out |
|---|---|---|---|---|
| P2a | all 42 tests passed | 0.99 | 701.7 | 289/20 |
| P2b | 7 of 42 tests failed | 0.01 | 747.5 | 291/20 |
| P2c | FAIL at 03:12 and PASS at 03:13, cause unrecorded | 0.61 | 608.7 | 320/20 |
| P2d | migration deployed, no logs/metrics available | 0.47 | 520.2 | 304/20 |
| P2e | repeat of P2a | 0.99 | 577.3 | 289/20 |

Exact body (P2a):
`{"model":"jev-1.13-free","answers":{"q":{"type":"noul","noul":0.99}},"usage":{"input_tokens":289,"output_tokens":20}}`

**Reverse-anchor verdict: `noul` = P(yes) is empirically CONFIRMED, no
contradiction.** P(yes|passed)=0.99 and P(yes|failed)=0.01 are the expected
pattern for P(yes). The anchors do not contradict the documented reading.

Additional observation, not required by the brief: the *decisive* anchors are
stable (0.99/0.01 reproduced across 3 and 2 repeats respectively, byte-identical
bodies), but the *ambiguous* anchor is **not** stable: 0.59 on the first
observation and 0.61 on the second. Jev is therefore near-deterministic on
saturated answers and stochastic at the ~0.02 level near the decision boundary.
Harness records every response verbatim so this is measurable per case.

**P3 — question-type schema (discriminating probe).** The README's flat
`{type, instructions, criteria}` shape is **only** correct for `noul` and
`score`. Measured:

| Probe | Shape | Status | Result |
|---|---|---|---|
| P3a | `choice` + `criteria` as **dict** | 200 | `{"type":"choice","choice":"escalate","confidence":0.13,"probabilities":{...}}` |
| P3b | `choice` + `criteria` as list | 422 | `dict_type` at `body.questions.q.choice.criteria` |
| P3c | `score` + `criteria` as **list** | 200 | `{"type":"score","score":1.62,"confidence":0.44,"legend":{"0":"weak","1":"moderate","2":"strong"},"probabilities":{"0":0,"1":0.37,"2":0.63}}` |
| P3d | `score` + `criteria` as dict | 422 | `list_type` at `body.questions.q.score.criteria` |
| P3e | `choice`, 3 labelled options | 200 | `{"choice":"build","confidence":0.56,"probabilities":{"escalate":0.28,"repair":0.01,"build":0.71}}` |

So `choice.criteria` is a **dict** (option key -> option label) and
`score.criteria` is a **list** (ordered labels). This corrects the README's
undifferentiated "`criteria`" wording and is carried into `schema.md`.

**Confidence formula spot-check (3 samples).** Predicted
`(n*max(p)-1)/(n-1)` vs reported: P3a n=6 max=0.27 -> 0.124 vs 0.13; P3e n=3
max=0.71 -> 0.565 vs 0.56; P3c n=3 max=0.63 -> 0.445 vs 0.44. Consistent within
rounding of the published probabilities. Note the reported `confidence` is *not*
`max(p)` — it is materially lower, so threshold sweeps must use the reported
`confidence` field. `score.py` re-derives this across the whole run.

**P4 — cheap general model baseline.**

- **P4a `POST https://opencode.ai/zen/go/v1/chat/completions`, model
  `space-bunny-free` -> HTTP 403 TYPED FAILURE.**
  Body: `{"error":{"type":"server_error","message":"Upstream request failed: An
  active OpenCode Go subscription is required to use Go models."}}`
  (891.1 ms.) The Go endpoint is not usable with this credential. The same probe
  without `x-opencode-session` first returned HTTP 400
  `MissingSessionID`, so the session header was not the cause.
- **P4b the SAME model ID `space-bunny-free` on
  `POST https://opencode.ai/zen/v1/chat/completions` with the same key -> HTTP
  200.** Body: `{"id":"070662634abe733676c514ad5d307b6d","object":"chat.completion","created":1790390115,"model":"space-bunny-free","choices":[{"index":0,"finish_reason":"stop","message":{"role":"assistant","content":"YES","name":"Space Bunny"}}],"usage":{"prompt_tokens":192,"completion_tokens":2,"total_tokens":194,"prompt_tokens_details":{"cached_tokens":149}}}` (1036.9 ms.)
  This is **not a model substitution** — the model ID is identical
  (`opencode-go/space-bunny-free`, confirmed in the refreshed catalog). Only the
  endpoint differs, because the Go-specific endpoint is unavailable. Both
  endpoints, both outcomes are recorded in `results/manifest.json`, and the
  general-model rows carry `endpoint` so the substitution of route (not model)
  stays auditable. Flagged as a **disclosed deviation from the README endpoint
  recommendation**, not a silent change.
- P4c control: `jev-1.13-free` on `zen/v1/chat/completions` -> HTTP 403
  `FreeTierError`, reproducing the README's established interface fact.

**P5 — transport gotcha (not in README).** urllib's default `User-Agent`
(`Python-urllib/3.10`) is rejected by Cloudflare on both endpoints with HTTP 403
`error code: 1010`. An explicit `User-Agent` header is mandatory. Recorded so
the RUNBOOK is reproducible.

**Preflight conclusion: PROCEED.** Jev reachable, `noul` semantics confirmed,
all three question types schema-resolved. The general-model baseline runs on the
Zen chat endpoint with the same model ID; the Go endpoint is a typed failure.

## D2 — Verifier: independent re-run and audit

- Agent: `space-bunny` subagent (fresh session)
- Model: `opencode-go/space-bunny-free`
- Status: pending D1 commit
- Deliverable: `verification.md` + raw evidence; PASS/FAIL per check
- Independence note: same model family as D1 (operator-scoped constraint);
  verification is session-isolated but not cross-family. Disclose in findings.

## D3 — Analyst: findings from verified data

- Agent: `space-bunny` subagent (fresh session)
- Model: `opencode-go/space-bunny-free`
- Status: pending D2
- Deliverable: `findings.md` (supported / provisional / limitations /
  counterexamples / next-phase questions)
