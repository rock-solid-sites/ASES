---
title: Resource Solver Red–Green and Mutation Verification
program: EDASES
layer: Research
status: Provisional
last_updated: 2026-11-01
---

# Resource-solver verification protocol

For each new requirement or correctness fix:

1. **RED**: Write a focused test first; run it on the prior implementation and record the expected behavioral failure, distinguishing it from syntax/import/setup errors.
2. **GREEN**: Implement the minimum fix; run the focused test and all affected regressions.
3. **REFACTOR**: Refactor only with behavior held constant and rerun the full suite.
4. **MUTATION**: Reintroduce the original defect (or a targeted equivalent) in an isolated copy; verify that the relevant test fails for the intended reason, then restore the correct code and verify green.
5. **BOUNDARIES**: Pair invalid-input rejection with neighboring valid-input acceptance, including exact limits, zero/negative/boolean values, stale/fresh versions, allowed/forbidden borrowers, and discrete account/provider/product/period/unit identities.
6. **EVIDENCE**: Record exact source revision, commands, environment, test counts, red reason, green outcome, mutation killed/survived, and remaining untested properties. Never label a test red–green verified without both executions.

## Retrospective audit, 2026-11-01

The previous allowance-admission v2 local prototype had 19 passing unit tests but lacked a documented red phase. A local mutation exercise on its existing tests deliberately changed six behaviors: replay prevention after release, settlement version check, account identity, oversettlement, allowance budget, and required explicit mapping. **All six targeted tests failed after the correctly scoped mutations.** An initial generic stale-version mutation changed the admission check instead of the settlement check and survived the settlement test; it was corrected to mutate the intended method. This is evidence for these six individual guards, not the entire module.

The v2 admission source and test suite were local files at the time of this audit and **have not been committed to this repository**. Do not claim that repository CI exercised them. The retrospective mutation exercise is not a historical red-before-green record; label it *retrospective mutation verification*.

## Backwards audit queue

- **Admission v2:** targeted mutation evidence for six guards; remaining guards and integration with planner unverified. Snapshot/policy revision binding and durable concurrency absent.
- **Allowance ledger v1:** 16 green tests reported; no contemporaneous red evidence. Re-run each invariant with targeted mutations and verify invalid/valid boundary pairs.
- **Portfolio planner v2:** 10 green tests reported; no contemporaneous red evidence. Validate mode-specific duration, resources, credits, ordering, dependency cycles and exact plan scoring using mutations and small independent reference cases.
- **Generated DAG scenarios v2:** committed but not yet executed in the prior report. Run and validate deterministic seeds and feasibility; independently enumerate small instances.
- **Independent oracle v1:** 36 aggregate suite tests reported, but only a subset tested by mutation. Audit fail-closed malformed input, borrowing, period reset, resource capacity, task graph cycles, and mode overrides.
- **Portfolio harness v0:** seven original green tests and baseline comparisons; no systematic red–green proof. Preserve baseline, audit tests in isolation, and distinguish model assumptions from bugs.

## Policy status

**Provisional project-level procedure**, pending wider ASES methodology review. This is a research quality gate, not proof of production readiness. Synthetic quotas and single-process locks cannot establish provider billing or distributed atomicity.


## Backwards audit execution — initial pass

Executed the previously available local suites without changes:

| Component | Existing green tests |
| --- | ---: |
| Allowance admission v2 (uncommitted local prototype) | 19 |
| Allowance ledger v1 | 16 |
| Portfolio planner v2 | 10 |
| Portfolio harness v0 + independent oracle and stress tests | 36 |

**Total: 81 passing test methods** across four separately executed local suites; this is not a single clean-checkout CI run.

The admission-v2 retrospective mutations killed **6/6** correctly targeted defects. The backwards mutation audit then killed **7/7** correctly targeted defects:

| Component | Mutation detected by |
| --- | --- |
| Allowance ledger v1 | `test_no_cross_bucket_substitution` (budget bypass) |
| Allowance ledger v1 | `test_stale_version` (version bypass) |
| Portfolio planner v2 | `test_dependency_cycle` (cycle detection disabled) |
| Portfolio planner v2 | `test_invalid_width` (invalid width accepted) |
| Independent oracle v1 | `test_capacity_collision` (all resource collision checks bypassed) |
| Independent oracle v1 | `test_duplicate_task_id` (duplicate task IDs accepted) |
| Portfolio harness v0 | `test_greedy_valid` (candidate validation bypassed, leading to a failing test) |

Two initial mutation attempts did not cause a failure because they targeted the wrong guard or only a subset of a compound guard; the audit corrected those mutations before recording the above 7/7. The original green tests were rerun successfully in their local directories. **These are retrospective mutation kills, not contemporaneous RED-before-fix proof.**

This is **13 targeted mutation kills across admission v2 and earlier layers**, not a comprehensive mutation score. There are still many untested branches and properties; do not infer full coverage or production safety. In particular, generated DAG execution, multi-process concurrency, policy-revision CAS, provider reconciliation, snapshot freshness and full end-to-end admission remain open.
