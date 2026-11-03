# Independent bounded verdict: SQLite holder write failure

**Verdict (before reading historical result material):** The fixed proposition is supported for the selected `independent` profile under the tested Python 3.12.14 / SQLite 3.53.1 rollback-journal setup and induced `SQLITE_FULL` page ceiling. It is not a general claim about every storage error or power-loss durability.

## Exact boundary and observations

The experiment uses a disposable version-1 `kernel` table with one JSON `view` row, profile `independent`, and a small finite payload. Setup establishes/grants context and successfully acknowledges the exact state containing `accepted\u0000zero\n`. It then adds an expression index whose entry grows when the candidate view contains `one`. The deciding holder starts with 3 pages. In the failure case, `PRAGMA max_page_count=3` is applied after setup; the deciding `UPDATE` attempts to change the view and SQLite raises `OperationalError`, code 13 / `SQLITE_FULL`, message `database or disk is full`. The client observes EOF (`holder lost`), not a success reply. After killing the holder, a separately launched read-only SQLite process reports `integrity_check=ok`; the raw UTF-8 bytes and SHA-256 of the recovered view equal the pre-write acknowledged view (`d0ff51f2ff4921da90ed171c6a6c345348a2afba85f31943bb307ba812a43804`). A cold holder independently reads the same recovered state.

The positive neighbor uses a 64-page cap. Its `Store.write` returns, the holder replies `outcome=commit` with `accepted\u0000one\n`, and independent cold recovery returns the same state. The modified disposable probe records `write_returned` only after the actual `Store.write` call returns; this stage is present for the neighbor and absent for the failing write. The source control flow then issues SQL `COMMIT` before resolving/publishing the result and before sending the acknowledgement.

## Qualification and limits

The cap is a connection-local SQLite page limit configured after setup and verified at the deciding write. The trigger is actual index-page growth, not a mocked exception. Setup has its own successful acknowledgement and independent byte observation before the cap is installed. Recovery evidence comes from a separate read-only Python process plus a newly started holder. Each run is two fixed cases, 512 MiB address-space ceiling, temporary case files bounded by an asserted 1 MiB, and the observed case files were 12,288 / 20,480 bytes. No enumeration or truncation was used.

This supports only one row/schema, the finite accepted payloads, one profile, one SQLite build/runtime, and this storage-full failure path. It does not establish behavior for filesystem `ENOSPC`, I/O errors, commit failure, corruption, alternate journal/synchronous settings, larger payloads, other runtimes, or machine/power loss. This process-kill/reopen check is not F5 durability evidence. Native same-family qualification remains caller-owned.

**Cheapest counterexample attempted:** force the deciding index growth beyond the exact current 3-page ceiling, then independently compare the recovered raw row bytes against the previously acknowledged row. No counterexample was observed within this boundary. The meaningful positive control is the adjacent 64-page run; the meaningful failure control is SQLite's actual extended operation error `SQLITE_FULL`.

**Smallest missing discriminator:** a caller-owned native same-family qualification of the concrete SQLite/runtime/storage combination intended for use. For a broader storage-error claim, the next discriminating test should independently inject one actual write/commit I/O failure mode outside the page-limit mechanism and compare both acknowledgement and cold-recovered bytes.

## Reproduction evidence

Commands, exit codes, raw stdout/stderr, and input/result hashes are in this directory. The instrumented follow-up changed only a `/tmp` copy of the probe and added a log after `Store.write` returns. Repository sources were unchanged.
