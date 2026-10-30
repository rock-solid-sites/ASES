# F2 T05 — Independent Host Evidence Adapter (bounded)
**Status:** compiled task, not an executed host verification. 2026-10-30.
**Target:** existing F2 branch \`research/phase-i-hostile-fixtures-f2-20261029\` @ \`5fb690d4ba7544a4a7eb5fce9ca1e54485543d64\`, with F3 host result pinned @ \`04600b1b45e6510665bdc3108db9d51f6b2f8c56\`.
**Governed by:** \`codex/execution-engine-roadmap:docs/architecture/core-substrate/Phase-I-Verification.md\` §3 T05 and §4 F3.

## One objective
Convert the **T05 authority-holder loss, surviving worker, retained socket, current protected read** *subprofile* from prepared-only to an independently evaluated host observation, without changing T05's expected outcome or pretending all T05 routes are covered. Keep the F2 oracle and fixture catalogue independent from F3 code.

## Reuse without cross-worktree mutation
Source F3 evidence: \`research/phase-i-protected-work-unit-f3/authority-loss/authority_loss.py\`, \`run.json\`, \`REPORT.md\` at the pinned commit. F3 selected safe case: H=M, pre-loss sentinel reply, H killed/reaped, W CPU work, post-loss EPIPE, denied direct/symlink/write-open. Mutated separate H and M survives with cached grant and delivers forbidden sentinel. F2 preexisting T05 prepared-only expectation remains unchanged. F3's \`safe_candidate_pass\` and \`violation_detected\` are **untrusted result labels**: never use them as sole assertions.

Implement a separate small **F2-side** evaluator over the raw JSON event/trace fields, with (where practical) an optional command to invoke the **unchanged pinned F3 fixture in a new disposable directory/clone**. No edits to F3 source, branch, runtime JSON, or other agents' worktrees. The existing F2 catalogue, runner and expectations remain intact. Base all selected-profile distinctions on physical trace observations, not an F3-internal PASS boolean.

## Explicit assertions
1. Positive nonvacuity: safe and fault-control baseline sentinel reply equals expected bytes; worker PID and holder PID distinct.
2. Real observed loss: H pid killed with returncode -9, independent reap time after kill request and **before** post-loss worker trigger; H=M for safe, H≠M for unsafe control. A logical revoke message is not substituted.
3. Surviving W: observed positive integer \`cpu_iterations\` and start/end after reap; worker exits successfully after trying the second request. Report \`392488\` as the recorded baseline measurement only, not a fixed future threshold.
4. Protected route denial: safe second reply does not contain sentinel; no protected bytes; direct target, chosen symlink, no-op O_WRONLY return denial (errno 13) **as independent fields**. Recognize EPIPE as loss of same socket's peer, not as proof of universal confinement.
5. Counterexample discrimination: unsafe separate H/M control returns protected bytes after H reap, and the independent evaluator **fails the expected D1 selected-profile claim** on those raw fields. Require testing the evaluator against at least one deliberately altered safe trace which admits protected bytes; a detector that accepts every trace fails.
6. Record raw event order, script and JSON hashes, PIDs, OS/Python/Landlock versions, exact command, denied route set and excluded routes; if any required field absent mark **INCOMPLETE**, not PASS.
7. Classify T05 as **host-observed selected subprofile only**. T05 physical inherited FDs, hostile peers, descriptor passing, child processes, arbitrary filesystem aliases, other protected external effects, and general D2 are **not tested**. Other T01–T24 abstract statuses unchanged.

## Evidence and stopping
Run the existing F2 abstract tests as regression plus the adapter's pure JSON mutation tests; if feasible independently reproduce F3 fixture once in disposable confines. Provide exact commands and outputs, new F2 coverage entry, and a limited technical report; preserve separate test-oracle ownership. Commit/push via approved host-side Git in the **F2** branch with five-minute checkpoints; never modify dirty main, F3 worktree, or retained snapshots. Stop with a reproducible selected-profile pass plus an unsafe control detected, or a precise missing evidence field/contradiction. Do not call this clean-room F5.