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
