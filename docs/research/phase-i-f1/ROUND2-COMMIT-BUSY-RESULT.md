# UPDATE success / COMMIT SQLITE_BUSY through actual holder

Executed preregistration ebb9341. Two disposable databases and genuine competing read-transaction processes. Real holder Boundary.resolve and Store.write remain unchanged. Instrumentation delegates SQL unchanged, sets only connection-local busy_timeout=100 ms, and traces completed/error statements.

Held reader: BEGIN IMMEDIATE completed, UPDATE completed with transaction open, COMMIT raised SQLITE_BUSY (5) while transaction remained open, then holder ROLLBACK completed. Client observed EOF, no success ACK. Reader process was still alive before explicit release. Independent read-only process and fresh holder recovered exact prior acknowledged state, integrity ok.

Released-reader positive: same reader establishes the lock then releases before proposal; UPDATE and COMMIT complete, commit response acknowledged, independent/cold holder recover new state. Both read-lock processes exit 0; tested/bootstrap/cold holders explicitly SIGKILL/reaped -9. Raw includes statement monotonic intervals, error code/name, client result, old/new exact bytes/digests, child observations, source/executable identities and file sizes (<1 MiB/case).

Command: `timeout 30 python3 docs/research/phase-i-f1/round2_commit_busy.py > docs/research/phase-i-f1/round2-commit-busy.raw.json 2> docs/research/phase-i-f1/round2-commit-busy.stderr.txt`, exit 0, stderr empty. This establishes a distinct actual COMMIT failure path rather than UPDATE failure. No product defect observed; successful UPDATE alone does not lead to ACK here. This is lock-contention failure, not disk I/O or power-loss failure; no universal error taxonomy, concurrent-writer guarantee or F1 closure. Existing post-COMMIT process death remains Kernel evidence; no repeated campaign.

Next cheapest new discriminator: a separately surviving currentness endpoint outside the rollback domain, including replay/endpoint-loss controls. It must name its trusted freshness and nonrollback premise rather than claiming pairwise equality provides it.
