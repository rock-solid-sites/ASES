# Historical decision register — retrospective, as of M5-8

Parent: ASES-21. This is a reconstructed pilot artifact, not a historical preregistration or change to the original task.

| Decision ID | Question | Evidence available at cutoff | Status | Next action |
| --- | --- | --- | --- | --- |
| STREAM-D1 | Can client receive, frame, decode, classify and persist stream events? | M4R, M5-1, M5-2 mock/native qualification | RESOLVED for qualified routes | Reuse observer, preserve evidence |
| STREAM-D2 | Does active reasoning explain the observed non-completion? | M5-4 live valid reasoning, no visible text, interrupt and no orphan | RESOLVED for reproduction | Classify active reasoning separately from idle |
| STREAM-D3 | Is reasoning control a useful mitigation for this route? | M5-5 matched prompt/model/route with historical baseline cap uncertainty; live completion under none | RESOLVED for tested configuration, causality limited | Record as route-specific mitigation candidate; not universal policy |
| STREAM-D4 | Does a per-request cap bound an entire task? | Cap F and source continuation trace | RESOLVED: no | Integrate task-wide admission |
| STREAM-D5 | Can aggregate controls classify and settle known failure outcomes? | M5-8 reference 32 checks, 14 replays | IMPLEMENTATION_READY, not deployed | Integrate observer/controller, cancellation verification and durable settlement with Resource Solver/ASES-13 |
| STREAM-D6 | Which models/prompts produce reliable reviews? | Limited comparison, no general quality conclusion | DEFERRED from STREAM critical path | Separate research if a real quality decision arises |
| STREAM-D7 | Did every historical provider stall have the same cause? | Incomplete authentic telemetry | OPEN, nonblocking implementation | Preserve uncertainty; discriminate when a concrete recurrence requires it |

## Admission decisions at the two historical cutoffs (retrospective)

A: after M5-4, proposed one native effort-none live test. DeepSeek REDUCE (recover cap, conditional matched pair); HungerG REUSE. Coordinator adjudication: classification evidence sufficient; mitigation validation may justify separate bounded question if implementation needs it. Preserve observed M5-5 result, do not erase or retroactively mark it worthless.

B: after M5-8, proposed comparative model review fixture. MiMo IMPLEMENT, Beam REJECT. Coordinator disposition: do not admit comparative review on this critical path; implement D5, keep D6 in separate research. Model quality is not resolved, but it is not a prerequisite to wiring the controller.

Evidence: [pilot report](PILOT-RESULTS.md), [frozen reviewer responses](evidence/frozen-reviews-part1.json), [MiMo](evidence/frozen-reviews-part2.json). No additional investigation launched.
