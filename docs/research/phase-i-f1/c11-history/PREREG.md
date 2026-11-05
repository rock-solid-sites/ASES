# C11 latest-pair atomicity versus retained required evidence history

Frozen after29ec396, before implementation/execution. Parent physical experiment
supports only latest accepted content/tuple coupling. Source review finds singleton
id=1/upsert overwrites earlier accepted observation bundle. Original per-acceptance
opaque genesis/creator/project inputs do not establish stable Work Unit identity.
Neither fact is hidden by a passing latest-pair check.

Selected stronger contract: stable identity/genesis, created-by and project across two
accepted contents; consumer requires both earlier and later accepted evidence afterward.
Competing hypotheses: atomic latest tuple suffices; or independent older accepted
consumer evidence must remain observable. Two histories have identical protected core
sequence/bytes and final latest tuple; only earlier consumer_evidence differs A/B.
Use fixed stable three fields in both histories and later evidence M identical. Actual
latest-only SQLite rows/query should collapse the histories after new acceptance and
process death, losing ability to answer required older-evidence query. Do not claim
all physical stale-page bytes are identical or universally unrecoverable.

Candidate: experimental accepted-content-indexed immutable observation archive, written
in same existing SQLite transaction as content/latest row, with repeated identical
bootstrap write idempotent and conflicting replacement refused. Consumer query returns
retained accepted records; no source/provenance authority follows from archive. Four
actual histories: latest-A/B, archive-A/B. Existing exact one-lane holder, original
prepared/durable boundaries; kill after new content COMMIT before ACK, fresh holder and
independent read-only process receive path/profile only. Same prior ACKed zero then
accepted one, stable three fields, independently varied old evidence A/B and common new
M. Both archived records/bytes must recover; latest-only queries cannot recover old A/B.

Small reuse hook in earlier Holder launcher may accept extra config/source with exact
unchanged defaults; historical parent source pins/manifests remain historical. No
canonical schema or minimality claim. Count processes, capture actual raw SQL/records,
caller no-ACK, exact source/executable/fixture hashes, no runtime observation oracle.
Two missing-record/ACK evidence controls INCOMPLETE. <=1 owned child/256MiB, finite Unix
socket/pipe waits. Provenance meaning/authentication, independent trusted creation,
nonrollback, power loss, arbitrary accepted histories, same-content revision contracts,
concurrent writer and generic C11/F1/PhaseI closure remain untested. Stable opaque fields
are fixture premises, not proof of intrinsic identity. This closes neither prior gap by
assertion: it must execute the selected history and distinguish the representations.
Next discriminator: required observation conflict/validation, or other governing open
obligation; avoid mechanically expanding the schema/number of examples.
