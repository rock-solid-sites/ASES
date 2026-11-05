# One bounded continuation of the original first-context timeout

Frozen from53952b7 before execution. Earlier unchanged first-context driver had5s,
was still expanding containment-and-grants at4.5s (16207 seen/2941 queued), and is
inconclusive. This next test changes only parent wall budget to30s, keeping original
model, original context/state bound, child256MiB virtual limit and original phase/progress
instrumentation. No model optimization, alternate semantics, sampled pass or new agent.

Hypotheses: first context finishes in the larger bounded window; or still exceeds
window/declared state/memory bound. Capture which phase actually completes/fails, actual
state/queue/commit counts, actual process exit/timeout, wall/child CPU/RSS and source/
executable identity. If complete, record finite context invariant/observation results
without promoting it to full driver acceptance (other contexts/semantic checks/attacks
not run). If incomplete, do not double again solely for counts or call it pass/fail.
This single30s cost may resolve a still-genuine scope uncertainty; no import/cap100
controls repeated because unchanged prior evidence already establishes them.

Use parent timeout/reap, explicit stderr exceptions and original state-bound exception.
Distinguish MemoryError, state bound, wall timeout and harness/product failure. Source
hashes before/after; output evidence categories exact. No canonical policies/main changes
or F1 closure. Actual remaining model usage unknown; wall budget is not a quota estimate.
