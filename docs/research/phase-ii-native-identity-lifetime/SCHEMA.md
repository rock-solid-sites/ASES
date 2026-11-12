# Evidence record schema

The `evidence/` records accompany the bounded identity-observation fault
histories in `REPORT.md`. They capture source provenance, exact commands and
raw command output. A synthetic identity supplied by the private test reader
must always be labeled as injected; it is not an operating-system observation.

## `meta.json`

Each run metadata record contains:

| Field | Meaning |
| --- | --- |
| `phase` | `pre-fix` or `post-fix` |
| `source_commit` | Git commit whose production source was executed |
| `source_path` | Repository relative path to the adapter source |
| `source_sha256` | SHA-256 of that source file at the run's source commit |
| `test_path` | Repository relative path to the test module |
| `test_sha256` | SHA-256 of the test module used for the run |
| `command` | Exact Cargo command and environment settings |
| `exit_code` | Process exit status from Cargo |
| `stdout_path` | Relative path to unmodified combined stdout and stderr |
| `stdout_sha256` | SHA-256 of captured command output |
| `injected_observation` | Label and description of the synthetic stale reader value |
| `what_not_tested` | Explicit untested surfaces, including real PID reuse |

For the pre-fix source, `seam-only.patch` records the private reader seam
relative to its parent commit. This permits checking that the fault-injection
run changed only how identity observations are supplied, while retaining the
old lifetime algorithm.

The test histories use a real `LocalSupervisor`, the actual SQLite-backed
`Store`, and a fixed `/bin/true` child. They do not create or adopt a second
process and do not claim that the stale token came from `/proc`.
