---
title: Resource Solver Admission Gate and Exact Reference Audit 2026-11-01
program: EDASES
layer: Research
status: Experimental
last_updated: 2026-11-01
---

# Admission and solver audit — 2026-11-01

## Test-first evidence

**Snapshot gate**: 12 focused tests were written before implementation. The initial missing-module failure was not counted as RED. Against an importable deliberately incomplete stub, **four behavioral tests failed**. After implementing the single-process gate, **12/12 passed**. Eight further gate tests passed, bringing the gate suite to 20.

**Allowance-period identity**: Two additional tests were added. The wrong-period rejection test initially **failed because a plan charged a November allowance while the snapshot said December**. After adding a fail-closed period check, both tests passed, bringing the gate suite to **22/22**.

**Fixture isolation defect**: During this run, a later test unexpectedly failed because `vars(B)` returned a mutable dictionary attached to a frozen dataclass instance; an earlier test mutated that dictionary and polluted subsequent cases. The fixture now uses `dict(vars(B))` to isolate its allowance identity. This illustrates why test order and state leakage deserve explicit attention.

The gate uses a canonical SHA-256 fingerprint of the JSON snapshot, a revision check, and a process-local lock around snapshot updates, schedule validation, claim generation, and ledger reservation. It is a prototype, **not** a distributed transaction. A stale plan cannot be admitted after a policy update within the same process, even when its old allowance version would otherwise fit.

**Mutation checks**: targeted changes to fingerprint comparison and schedule/policy validation caused their corresponding tests to fail. An initial version-check mutation was applied to the wrong method and survived the chosen test; after selecting the update-revision test, the change was detected. These are targeted mutation checks, not comprehensive mutation coverage.

## Independent exact-reference comparison

A new test enumerates all possible placements and omissions for **50 seeded three-task instances**, using the independent feasibility oracle to determine the maximum on-time value. It compares both greedy and beam(width=30) against that reference: **100 heuristic evaluations, all feasible, five suboptimal, maximum value gap five synthetic units**. This is evidence that the heuristics are not always optimal, not a correctness failure of the admission validator. Exact reference uses the same feasibility oracle, so it is not an independently implemented second validator.

## Code and test locations

- `research/resource-solver/allowance_admission_v2.py` — committed discrete claims and reserved/spent ledger.
- `research/resource-solver/snapshot_gate_v1.py` — committed policy/snapshot admission gate.
- `research/resource-solver/test_snapshot_gate_v1.py` — 22 local passing tests.
- `research/resource-solver/test_exhaustive_v1.py` — 50 exact-reference instances.

Run from repository checkout:

```sh
python3 -m unittest discover -s research/resource-solver -p 'test_snapshot_gate_v1.py' -v
python3 -m unittest discover -s research/resource-solver -p 'test_exhaustive_v1.py' -v
```

The source and tests were reproduced and executed in a local container. **A clean-checkout CI run has not been verified.**

## Known limitations and safety blockers

1. **No durable CAS or crash recovery**. The lock serializes only threads sharing one process. Multiple agents or restarts can double-allocate if they create independent gates.
2. **No provider reconciliation**. Ledger spent values are local estimates, not verified actual usage.
3. **Single explicit period only**. `allowance_period` is a snapshot string; the gate checks identity but does not map wall-clock execution timestamps to billing periods. A job crossing a reset must be modeled explicitly before production use.
4. **Snapshot policy update semantics**. Existing reservations remain after policy changes; revocation does not automatically cancel running work. Need a rule for running/frozen tasks and owner reclaim.
5. **Untrusted provider inputs**. Snapshot digest binds JSON content but does not prove the provider observations are authentic, recent, or complete.
6. **No free-only plan admission**. The gate rejects plans without chargeable claims; a separate local CPU/RAM reservation mechanism is required.
7. **No persistent audit trail or idempotent settlement request keys**. Replayed settlement with a newer revision could consume additional reserved credits; define settlement events and provider usage IDs.
8. **Mutable nested schema and incomplete preflight**. Validate mode overrides, policy structure, allowance identities, cyclic graphs, resource arithmetic and zero-cost tasks before planning.
9. **Optimization evidence limited**. The exact-reference instances are tiny and synthetic. Compare additional generated DAG families and measure runtime, memory, regret and cost.

## Next verification gates

Prioritize durable transactional state and a reservation/settlement state machine; test restart and multiple-process races using a disposable SQLite WAL store. Add mode-to-period timestamp validation, fail-closed nested schema preflight, and frozen-work policies. Preserve test-first failure evidence and require mutation kills for critical guards. Continue exact-reference comparisons on progressively larger small instances before relying on heuristic quality.
