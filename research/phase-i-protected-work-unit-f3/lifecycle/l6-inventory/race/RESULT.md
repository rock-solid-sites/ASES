# Executed new-dependent phantom schedules

Sourceb669e5b ran once: three schedules/eight actual children, maximum overlap2.
Raw source/executable hashes, exact SQL/native errors, actual bytes, process/caller/
gate/response and EOF metadata retained. Checker source-pin/missing/contradiction
controls pass; stderr files empty. Reproduce:

```sh
timeout 45 python3 research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/race/probe.py > /tmp/l6-race.json
python3 research/phase-i-protected-work-unit-f3/lifecycle/l6-inventory/race/check.py /tmp/l6-race.json
```

Guarded remover pauses after the unchanged complete directory scan, within its original
BEGIN IMMEDIATE transaction. A second already-ready process attempts real candidate
creation: SQLite returns code5/SQLITE_BUSY after its configured150ms wait, before a file
or catalog row exists, and with no transaction acquired. Releasing the remover produces
successful empty removal/rmdir. The same creator's later new transaction sees the
removed unit and denies. A fresh root-only process retains the empty sealed tombstone.

Detached-scan mutation pauses outside any write transaction. The creator actually
fsyncs z, registers it, COMMITs and receives a reply before removal continues. Without
a recheck, the mutant records logical removal while the live candidate/file remain.
It explicitly does not claim physical boundary removal. Fresh management startup
refuses `removed-unit-has-surviving-material`, unchanged; refusal is not successful
recovery. This is an experimental structural admission counterexample, not host
namespace exposure or a defect attributed to the original in-profile guarded path.

Creator-first positive: actual candidate COMMIT/reply precedes ordinary guarded removal;
removal denies and trusted management reads the exact retained z bytes. The byte object
remains an unaccepted candidate; this reply is not content acceptance or provenance truth.

Every serving child is waited/reaped, then stdout is drained through EOF and the
remainder/time retained (empty in these histories). This fills an observation gap for
these new cases without retroactively supplying EOF evidence to the preceding experiment.
The cold refusal captures its complete stdout/stderr with communicate. Missing creator
observation is INCOMPLETE; intentionally contradictory parsed/wire code is VIOLATION.

Conditional flat enclosing root and every creator using the same current write boundary
are premises. A complete scan alone is insufficient; its currentness must be ordered
with mutation/removal. No arbitrary external writer/alias/inode attack, native worker
confinement, general T12/T15/L6/F3/F4 acceptance, SQL/rmdir interruption atomicity, secure
erasure or machine power-loss guarantee. This is executed store/policy evidence, without
independent reproduction of this extension at publication. Parent inventory/disposition
review covers its earlier pin only. Next independent check/integration or another
obligation; more identical SQLite schedules would add little discrimination.
