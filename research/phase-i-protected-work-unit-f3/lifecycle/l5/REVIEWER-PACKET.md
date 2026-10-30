# F3 L5 — independent clean-room source review

**Task:** Independently verify or falsify the bounded F3 L5 host-experiment claim below. This is a source/evidence audit, not implementation or repair.

## Pinned inputs

Repository: `rock-solid-sites/ASES`

**Implementation and recorded observations — exact commit:**
`fb34deca9ea8c1bf04ec808052b39d7521040290`

Read:
- `research/phase-i-protected-work-unit-f3/lifecycle/l5/l5_write.py`
- `research/phase-i-protected-work-unit-f3/lifecycle/l5/verify_l5_write.py`
- `research/phase-i-protected-work-unit-f3/lifecycle/l5/l5-write-raw.json`
- Only direct implementation dependencies needed to understand or execute these artifacts.

**Governing specifications — exact commit:**
`5c03a425fd5627c3764806292b8c5cb653498f4f`

Read:
- `docs/architecture/core-substrate/Phase-I-Verification.md` — T11 and F3 requirements.
- `docs/architecture/core-substrate/Phase-I-Closure.md` — §7 and related definitions necessary to interpret the claim.

Use the pinned versions, not moving branch heads.

## Claim to assess

For one selected host profile, a trusted authority mediates worker requests to read accepted content and perform a write. A child C has local read/write permission. Before a sealed move, its parent P permits reads but not writes; the destination parent Q permits both. After the P→Q move and a separately authorized activation, the previous effective read-only restriction must continue to prevent writes. Reading accepted content x should remain possible. A positive control should demonstrate that mediated writing can succeed; a weakened restriction should allow a previously forbidden write and expose the distinction. The accepted content must remain unchanged.

Determine precisely which parts of this claim the implementation, execution and recorded evidence establish, and which they do not. Distinguish observed host behavior from general or untested guarantees. Do not infer full F3 or F5 closure.

## Independent examination

Start in a fresh context with no prior review findings. Base conclusions on the pinned source, raw observations, governing requirements, your own reasoning, and reproducible checks.

Do not read builder explanations, result summaries, incident records, earlier review reports, or agent conversations before recording an independent verdict. Do not communicate with other reviewers or inspect their outputs until all reviews have been submitted.

Inspect control/data flows and evaluate the claim yourself. Re-run checks when practical. If testing alternative inputs or evidence mutations, use isolated disposable copies only; preserve the original recorded observations and implementation unchanged.

## Delivery

Run entirely on the existing Ubuntu VPS. Use an isolated fresh checkout/worktree and a unique review branch based on the **implementation commit** above. Do not alter `main`, existing worktrees, builder branches, or the source under review. Do not use paid services or alternate execution hosts.

Write one report at `F3-L5-INDEPENDENT-REVIEW.md` on your own review branch. For each material conclusion, give: verdict (`supported`, `partial`, `unsupported`, or `contradicted`), exact source or evidence reference, reproduction/check performed, and limits. Include any substantive findings and the smallest follow-up needed. Clearly distinguish tests actually executed from reasoning-only checks.

Commit and push only your review report and any self-contained, disposable-derived test code needed to reproduce a finding. Provide the review branch name and verified remote commit SHA. If required access, evidence, or a safe execution route fails, stop and report the specific blocker without substituting a different route or model.
