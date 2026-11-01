# SQLite transactional policy gate — adversarial integration audit

Date: 2026-11-01. Status: **research prototype, local tests only**.

## Evidence

The standalone SQLite policy gate (policy_gate.py with sqlite_ledger.py) was tested against the prior 20 regression methods: **20/20 passed**.

Seven additional adversarial tests produced **five genuine assertion failures before the fix**: undeclared project references, empty provider identity, duplicate policy account entries, unexpected top-level policy keys and unexpected task keys were accepted. Strict closed-schema validation, nonempty identities, declared-project checks and unique authorized account entries corrected all five. The suite then passed **27/27**.

Two more test methods were added: malformed task selection rejection and 30 independent repeated races between a policy update and admission. Final local suite **29/29 passed** (0.834 seconds in the final run). Each race uses SQLite transactions and checks the policy revision and ledger version. It does not establish network-filesystem or multi-host safety.

## Transaction model

Policy update and admission use the same SQLite database and BEGIN IMMEDIATE transaction. Admission checks policy revision, content digest, ledger version, task identity, authorization, discrete bucket identity and available budget before reserving. Policy updates increment both policy revision and ledger version. Existing reservations are not automatically canceled by revocation.

## Caveats and unresolved risks

- The implementation and tests remain a **local artifact**, not committed repository code. This audit report is committed; do not imply CI or repository test reproducibility.
- Policy+ledger initialization consists of two transactions; an interruption between them needs recovery design.
- Task schema is intentionally narrow, with Boolean selection rather than actual scheduler placement and runtime mode mapping.
- The period is caller-supplied, not calculated from provider billing windows or execution timestamps.
- Provider usage reconciliation and idempotent external settlement are not implemented.
- SQLite WAL requires an appropriate local filesystem; no multi-host/NFS guarantee.
- Python 3.13 reported a fork-from-multithreaded-process deprecation warning in one multiprocessing test; use spawn/forkserver for portable process tests.
- Fault injection, disk-full, corrupt DB, migrations and integration with the actual portfolio oracle remain unverified.

## Verification standard

Five defects have real RED-before-fix evidence, GREEN after fix. The two new passing tests are additional regression evidence, not retrospective claims of RED. Earlier suite tests retain their prior evidence status. Do not equate passing tests with complete coverage.

Next: commit reviewed implementation and tests, build a clean-checkout CI run, then test interrupted initialization, policy revocation vs running work, cross-period billing, crash recovery and provider settlement.
