# Executed original move publication cuts

One primary execution at0371966 completed six histories/12 actual children, max1.
Reproduce with `timeout 45 python3 research/phase-i-protected-work-unit-f3/lifecycle/l5/move-cuts/probe.py > /tmp/move-cuts.json`
then `python3 research/phase-i-protected-work-unit-f3/lifecycle/l5/move-cuts/check.py /tmp/move-cuts.json`.
Source/executable hashes, original manager request/wire response, exact selector/record/
object bytes, retained os.replace gate, caller/process/kill/reap/EOF observations are
retained in raw.json. All stderr files are empty; missing post-reap state INCOMPLETE
and contradictory reported/selected record VIOLATION controls pass.

Original authorized sealed move, source helper unchanged:

| Interruption | Actual private/public files after termination | Fresh selected state |
| --- | --- | --- |
| Before prepared record replacement | complete record-000002.json.tmp remains | exact old record1, C below P |
| After record replacement, before CURRENT | unselected complete record2 remains | exact old record1, C below P |
| After actual CURRENT replacement, before reply | CURRENT selects record2 | whole new C below Q, C/D read ceilings |

At each gate the original call is still pending; worker is SIGKILLed/reaped and stdout
drained through EOF, with no response/remainder. Fresh process receives only root path,
reopens actual CURRENT, validates graph/content and observes the selected sealed state;
prepared/unselected complete records do not override CURRENT. A separately authorized
original activation then tests current full-path D-write: all three cuts deny without
creating the effect. Actual accepted fixture x remains exact throughout.

Uninterrupted move returns actual COMMITTED manager wire reply and cold selects the
same new whole state; later write also denies. Separate P-read/write fixture activates
and produces the exact owned D-write effect, preventing universal-denial success.

Controlled split publication selects C.parent=Q before retaining C/D ceilings, then is
killed before its second publication. The selected state is graph-valid and sealed,
but is neither the old nor permitted new whole move. Fresh activation permits an actual
owned D-write with exact bytes. This is a weakened-control counterexample, not a defect
in the original single-publication manager or a new latent-policy finding.

This is executed process-live store/policy evidence, without independent reproduction
at publication. Synthetic existing accepted-x fixture and shared test credential do
not establish new content acceptance, provenance truth, manager identity or native
worker confinement. Original commit has no fsync; host/file-system currentness and
single holder remain premises. No actual power loss, concurrent manager safety,
physical/secure erasure, general recovery/activation or full T12/F3/F4 closure.

Next independent source-first check of this selected boundary, then inspect an actual
unverified cold-parser contract rather than repeat publication cuts. No Landlock retry.
