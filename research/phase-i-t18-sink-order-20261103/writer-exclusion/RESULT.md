# Same-journal startup needs an actual writer-exclusion premise

Execution sourcec806ef4 (exact SHA raw.json), includes fetchedbacf8f7 before behavior.
Reproduce `python3 research/phase-i-t18-sink-order-20261103/writer-exclusion/probe.py > /tmp/sink-writers.json`, then
`python3 research/phase-i-t18-sink-order-20261103/writer-exclusion/check.py /tmp/sink-writers.json`.

WHY: journal-existence check avoids silent reset but did not realize the assumed one
writer. WHAT: two actual serving processes ready on same missing journal before first
request, real HTTP/ACK/status/raw journal, strict cold reader, native flock identity and
actual process death/current-file recovery. Certainty: executed finite controls and
coordinator checker, no independent review yet.15 actual children/max2, all reaped.

Original overlap: A and B ready before append, each valid token1 request gets201 with
seq1. Both complete accepted records remain in shared journal; A/B in-memory effects
are separately scoped. Strict fresh-process recovery refuses duplicate durable seq,
unchanged bytes. This is a missing singleton realization counterexample, not proof
accepted bytes disappeared or that earlier single-holder evidence violated its scope.

Reference wrapper: guard inode acquired before original fresh/recovery validation and
held through serving. While journal still absent, second cooperating startup refuses
before ready/exit75, no journal effect. A actual201/seq1, SIGKILL/reap; fresh mode on
existing journal refuses unchanged; explicit guarded recovery reconstructs A, then new
actual201/seq2. Second same-file cold recovery retains both exact ACKed effects, with
no observer fixture/oracle input. Same guard dev/inode/path in selected history.

Weak participation control: guarded A plus original nonparticipating B both ready
before append again produce two201/seq1 and strict refusal. Thus flock is advisory
and participation/trusted root are indispensable premises; no host confinement. Two
different guarded roots simultaneously acquire/ACK and recover their own effects,
so guard is not a global deny-all. Missing startup/recovery-byte controls INCOMPLETE.
Journal itself has no writer PID/root identity; actual attribution is supported by
owned startup/process/port/caller metadata. Do not infer universal writer provenance
from journal fields alone.

Source-selection mistake preserved in prereg: initial unqualified fetch updated
FETCH_HEAD but stale tracking ref created continuation from4f8f3ff. Before any behavior,
explicit ref update/research-only merge integrated currentbacf8f7 and preserved both
published histories. No reset/rebase/force/main/canonical merge. Exact executable/base/
wrapper/runner hashes retained at actual execution pin.

WHAT NOT TESTED: uncooperative-writer enforcement, guard inode replacement (prior F1
already exposes it), hostile root/credential confinement, independent root/currentness
or nonrollback, physical power loss/storage failure, generic F2/F4/F1 completion. This
wrapper covers selected ordered/recovery sink paths only; other management/witness
profiles not automatically guarded. Process death closes this owner's lock reference,
not proof every conceivable duplicate reference dies. Advisory stable-inode/all-writer
TCB is explicit, not canonical methodology or native F3 acceptance. Next independent
bounded audit, then another highest-value missing obligation rather than guard variants.
