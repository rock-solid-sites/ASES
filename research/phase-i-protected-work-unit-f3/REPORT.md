# F3 protected-work-unit mechanism report (incomplete)

## Scope and disposition

This is a minimal report of the executed retained-descriptor experiment and the current trust-boundary inventory. It does not establish a production mechanism, complete lifecycle semantics, or F3 acceptance. F1 is incomplete, so no broader lifecycle implementation is authorized by this checkpoint.

## Executed evidence

`exp1/retained_handle.py` ran the disposable plain-POSIX mode variant; exact output is in `exp1/observations-plain.json`. Before the mode change, holder H obtained an ordinary read descriptor, and both H, fresh activity F, and grantor G could access the fixture. After the fixture owner ran `chmod 000`, H's already-open descriptor still read `F3-sentinel-content\n`; H's subsequent fresh path open and G's fresh opens failed with EACCES. After the mode was restored to 0666, H, F, and G could open/access it again. Killing H did not stop F or G from accessing the path.

The narrow result: changing discretionary mode metadata prevented new opens by these tested processes while the restrictive mode applied, but did not revoke an already-issued open file description. Therefore this result refutes the claim that chmod-based permission change, by itself, revokes access represented by a retained descriptor. It also demonstrates that stopping the holder process is not equivalent to revoking a pathname grant still available to other principals.

This does not establish universal Linux behavior, confidentiality against copied bytes, write behavior through an already-open writable descriptor, revocation through ACLs/mount namespaces/leases, protection against other identities or privileged actors, or any complete protected-work-unit design. The experiment used one file and a limited set of read/fresh-open checks. A metadata permission change changes checks on later path opens; it is not proof that existing handles or data copies have been invalidated.

## Inconclusive / unexecuted evidence

`observations-acl.txt` and `observations-acl-attempt.txt` record attempts, not successful ACL/no_new_privs tests. Parent path access failed with EACCES; the no_new_privs pre-exec hook was not applied (the script explicitly reports plain spawn). ACL grants did not produce successful fresh access in the recorded attempts. Do not infer ACL revocation or no_new_privs enforcement from these runs.

`probe/` and `probe/support/` are unexecuted drafts. In particular, their socket proxy, bodyguard parent-death handling, runner path pinning, and proposed ACL are hypotheses/design material, not experimental evidence. They do not provide a tested bypass inventory or a security boundary.

## Trusted-boundary inventory (current evidence vs. proposed design)

| Element | Trust/authority role | Current evidence / boundary |
|---|---|---|
| Fixture file and parent directory | Protected object and path-resolution context | One disposable file under this worktree only. Mode 000 blocked tested fresh opens; it did not revoke H's existing descriptor. No symlink/race/rename coverage. |
| Fixture owner/parent process | Changes mode and observes results | Retained authority to restore mode in plain run. ACL attempt lost path access and could not demonstrate a grant. No independent revoker tested. |
| Grantor G | Superior-authority path opener in experiment | Its fresh opens obeyed current mode in plain run. G remained live after H was killed, so holder termination did not remove G's authority. Not an isolation mechanism. |
| Holder H | Activity with retained descriptor | Existing descriptor remained readable after chmod 000. Killing H ends that process but says nothing about other descriptors, copies, or other actors. |
| Fresh activity F | Activity that never previously opened file | Fresh opens followed current mode; succeeded again after regrant and after H termination. |
| OS/filesystem permission enforcement | Enforces tested path-open permission checks | Only the observed fixture and operations are evidenced. No claim about all kernel/filesystem configurations. |
| Proposed ACL proxy | Would mediate requests routed through its socket | Draft only. Cannot mediate direct filesystem access or sibling processes resolving paths themselves; path canonicalization, races, protocol and descriptor escape remain untested. |
| Proposed bodyguard / runner | Would supervise process lifetime and alter launch environment | Draft only. `PR_SET_PDEATHSIG`, child tree coverage, races, and the purported engine/activity anchoring are unverified; no enforcement claim. |
| Caller / sibling processes / inherited handles | Potential direct or delegated access paths | Not comprehensively enumerated or tested. No evidence that all access routes are forced through a mediator. |
| Bytes already read/copied; other storage, caches, logs, IPC | Data-exfiltration/retention surfaces | Outside experiment scope and not inventoried exhaustively. Path permission changes cannot be treated as erasing copies. |

## Next bounded step

After reconciling with the F1 model, define one disposable mediated-attachment test and its explicit bypass cases. Test only there with a short timeout; record failures literally. Do not broaden into lifecycle implementation until an exclusion mechanism passes that initial discriminating test. Preserve `exp1/run/` and the recovery snapshot; its mode-000 target bytes are separately retained as documented in the snapshot README.