---
title: Portfolio Harness v0 — First Executed Baseline 2026-11-01
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
related_documents:
  - docs/research/Portfolio Allocation Harness v0 2026-11-01.md
last_updated: 2026-11-01
---

# First executed portfolio harness baseline

## Execution

The committed `portfolio_harness_v0.py` and `test_portfolio_harness_v0.py` contents were fetched through the GitHub connector and reproduced in a separate Python execution environment. This report describes **execution of those source contents**, not a CI run in GitHub or execution on the VPS. Standard-library Python was used.

Commands:
```sh
python3 -m unittest discover -s /mnt/data/ases_portfolio_test -p test_portfolio_harness_v0.py -v
python3 /mnt/data/ases_portfolio_test/portfolio_harness_v0.py
```

Seven of seven tests passed in 0.208 seconds. Both planners returned validator-accepted plans, scheduling all five tasks on time.

| Metric | Greedy | Beam width 100 |
|---|---:|---:|
| Tasks | 5 | 5 |
| On-time value | 37 | 37 |
| Late tasks | 0 | 0 |
| Synthetic cloud-credit ticks | 7 | 4 |
| Synthetic startup units | 4 | 4 |
| Feasibility errors | 0 | 0 |

Beam saved 3 of 7 modeled credit ticks (42.86%) relative to greedy, with no loss of on-time value in this fixture.

### Actual placements

Greedy:
- `hms-build` vps [0,3)
- `hms-test` burst [3,5)
- `ases-bench` burst [0,2)
- `rss-test` burst [0,1)
- `mbd-work` mbd-cloud [0,2)

Beam:
- `hms-build` vps [0,3)
- `hms-test` burst [3,5)
- `ases-bench` vps [3,5)
- `rss-test` vps [5,6)
- `mbd-work` mbd-cloud [0,2)

## Limitations and discovered research gaps

- This is one five-task synthetic fixture with seven coarse ticks, not a statistical benchmark or a claim about actual provider billing.
- Beam is heuristic, not proven optimal. No CP-SAT/MILP comparison yet.
- Startup units are reported but not charged as constraints or modeled as lifecycle delays.
- The current fixture's `reset_day` is not enforced. It does not test rolling-horizon quota reset.
- Current validation does not reject duplicate task IDs in the fixture, does not check resource snapshot schema completeness, and may raise exceptions on malformed candidate records; independent production admission must fail closed.
- The existing seven tests cover basic cases but not double-spend across overlapping quota domains, owner reclaim, credit expiry, uncertainty, stale snapshots, or concurrent policy changes.
- Current beam search orders tasks before evaluating placements and does not guarantee retaining the best completed portfolio across arbitrary larger instances.
- A Python interpreter startup emitted an unrelated spreadsheet-runtime warmup error on stderr, but unittest returned exit code 0 and all seven tests passed. The benchmark script itself returned exit code 0.

## Next experiment

Before a CP-SAT comparison, add negative tests for malformed snapshots, reset/expiry, shared quotas and task mode changes; build a second independent validator; and expand to multiple seeded scenarios. Measure wall time and peak RSS separately from modeled execution credits. Optimizer location remains deliberately undecided.
