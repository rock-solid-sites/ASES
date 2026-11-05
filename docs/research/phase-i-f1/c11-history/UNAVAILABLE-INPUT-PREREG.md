# Recovery can read retained evidence without new-acceptance input

Frozen after9aaf60a before execution. Startup type checks permit observations=None for
legitimate recovery, which is necessary because original tuples must not be supplied
by the oracle. New question: can that recovered holder accept different content without
a new required tuple? Hypotheses: a valid current archive/startup is sufficient for
later new acceptance; or required input availability must be guarded at commitment.

Cheapest actual cases: bootstrap valid zero/old tuple; recover/configure holder with
no observations, prove real read returns retained valid pair, then submit original
accept-one wire request. Predict baseline content COMMIT with no companion update,
caller no usable response, raw current/archive binding incompatible, next cold startup
refuses. Positive supplies valid NEW tuple and ACKs/recoveries normally. This is a
semantic unavailable-input mode, not another field-type example.

After documented failure, candidate proposal guard under the existing holder lock/
SQLite transaction: if candidate changes accepted content and observations unavailable,
return no candidate/deny before content write. Keep reads valid. Conservative refusal
may deny reselecting already archived content; no maximal availability promise or new
protocol/source authority is claimed. Actual missing-input denial must ROLLBACK/no
COMMIT and retain previous ACKed pair; explicit-input positive remains. No oracle tuple
given to recovery, no auto-publishing/rewriting prior metadata.

Two actual admission histories per phase,8 owned children/max1,256MiB/bounded sockets.
Capture valid pre-read, request/reply/no reply, actual SQL trace and raw diagnostic rows,
new recovery readiness, exact source/executable hashes and process intervals. Missing
observation/trace metadata INCOMPLETE. Source/meaning/authentication, power loss,
nonrollback, generic C9/C11/F1 completion, arbitrary acceptance profiles and liveness
remain untested. Retained evidence sufficiency for current read does not imply authority
or information for new commitments. Next select a different strong remaining obligation
or independent adversarial check, not routine field-case expansion.
