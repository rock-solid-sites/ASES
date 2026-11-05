# Same-journal startup overlap and actual sink writer exclusion

Frozen from current fetched prefix-recovery headbacf8f7 before implementation/execution.
Original sink assumes one holder; fresh-journal existence check prevents silent restart
reset but has not itself demonstrated singleton exclusion. Cross-layer question: two
fresh serving processes can both observe missing journal before first request, then
independently issue seq1. Predict actual two201 acknowledgments/duplicate durable seq1
and strict recovery refusal. This exposes missing realization premise, not a violation
of earlier explicitly single-holder test scope or aggregate F4 failure.

Selected reference wrapper holds an actual nonblocking exclusive flock on a stable
trusted-root guard inode BEFORE fresh/recovery state validation and throughout serving.
No canonical policy change; trusted all-writer participation/stable inode/root custody
and same-host lock semantics remain explicit premises. This is cooperative sink writer
exclusion, not hostile host confinement or real credential revocation. Prior F1 inode-
replacement/retained-lock controls already establish those limits; do not rerun them.

Cheapest controls:
1. Original A/B both ready on same missing journal, actual sends only afterward; expect
both201/two seq1 records, complete bytes retained, cold strict refusal.
2. Guarded A ready while journal absent; guarded B refuses before ready without effect.
A201, actual kill/reap, fresh mode refuses existing journal, explicit guarded recovery
reconstructs A and next seq2; B201 and second cold restart retains both actual ACKs.
No observer/oracle data/fixture copying passed to recovery, only actual path/mode.
3. Guarded A + original unguarded B both ready before first append reproduces failure:
advisory lock is not enforcement against a nonparticipating writer.
4. Different owned roots guarded A/B both ready/accept/recover independently, preventing
false success from a global deny-all lock.

Bound <=2 owned serving children,256MiB inherited, finite loopback/startup waits. Preserve
actual startup frames/no-ready reason/exit, journal-existence observations, request/
reply/sequence/effects/raw bytes, guard inode/dev/path, process ordering, source/executable
hashes and reproduction. Missing startup/sequence metadata INCOMPLETE, invalid journal
refusal not content-loss proof. Distinguish process termination, reconstructible current
journal and actual power loss/storage/authority rollback. No whole F2/F4/F1 completion,
root authentication, uncooperative-writer exclusion or physical power-loss claim. Next
consequential discriminator depends on observed failure; do not promote flock into F3
native confinement or repeat forbidden/unavailable Kernel/Landlock routes.
