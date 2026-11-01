# SQLite transactional policy gate — experimental test record (2026-11-01)

Status: **local prototype only**. Code and tests are packaged in the conversation artifact sqlite_policy_gate_v1.zip; they have **not** been committed to ASES.

## Red–green evidence

- Wrote 10 tests before implementation. Against an importable stub, 4 assertion failures and 1 error were observed; remaining tests passed trivially or exercised failure behavior.
- Implemented a SQLite WAL gate using the existing SQLiteLedger, BEGIN IMMEDIATE, a persistent policy_state row containing revision, canonical JSON, and SHA-256 digest. Admission checks authoritative policy and reserves quota within **the same write transaction**.
- Initial 10 tests green; added 10 boundary/concurrency tests, total **20/20 green** with ResourceWarning treated as error.
- Mutation verification: bypassing the snapshot-digest comparison made test_snapshot_tampering fail (accepted tampered credits). Restored guard and verified **20/20 green**.
- Multi-process tests: 12 competing attempts after revocation admitted **zero**; 16 simultaneous reservations against five available units and three-unit claims admitted **exactly one**.

## Explicit boundaries

The gate currently uses a deliberately simplified selected-task plan, not the full scheduling schema. It validates task authorization, charge identity and amount against a stored policy snapshot; the caller cannot submit arbitrary claim amounts. It rejects stale policy revision, stale ledger version, mutated snapshot, duplicate plan IDs, invalid IDs, and wrong billing periods. It persists policy revisions and reservations in one SQLite database.

## High-priority limitations

1. **Not yet integrated with portfolio_oracle_v1 or full scheduling placements.** CPU/RAM contention, dependencies, task start/end times, reset crossings and nonchargeable execution are not validated by this gate. Do not authorize actual execution through it.
2. **Existing SQLiteLedger.initialize is called before policy_state initialization**, so first-time initialization is not a single atomic schema/policy/budget operation. A crash between stages can leave a partial database; migration/recovery tests are required.
3. **Policy updates increment the global ledger version** through the inherited mutation helper; callers must refresh both revision and ledger version. Test that behavior at the API boundary.
4. Existing reservations are not automatically revoked on policy updates. Define running-task revocation semantics.
5. Local WAL behavior is not proof of multi-host, network filesystem or durable storage safety. Disk-full, corrupt database, migration and checkpoint tests remain.
6. The 20 tests and one targeted mutation are not a comprehensive fuzz or mutation score. Next steps should include model-based interleavings of policy updates/admissions/settlements, crash injection at transaction boundaries, and full scheduler oracle integration.

Do not mark this prototype production-ready. The next phase should first close the simplified-plan authorization gap, then conduct additional red–green and fault-injection rounds before committing implementation.
