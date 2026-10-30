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

The bounded mediator authorization-revocation candidate is now tested and recorded in `exp3/RESULT.md`; stop mechanism broadening here. Future lifecycle work must first reconcile with B's partial F1 model. Preserve `exp1/run/` and the recovery snapshot; its mode-000 target bytes are separately retained as documented in the snapshot README. F5 independent review remains outstanding; F3 acceptance is not claimed.
## Landlock alternative mechanism probe

The bounded Landlock availability and path/alias/retained-FD discrimination results are recorded in `exp2/availability/RESULT.md` and `exp2/discrimination/RESULT.md`. The direct target and one symlink alias were denied under the child's empty read ruleset; a sibling per-operation mediator returned bytes; an FD inherited before restriction remained readable. This concrete retained-handle obstruction means Landlock did not provide handle revocation. Stop further mechanism broadening here. No F3 acceptance; F1 remains partial and F5 independent review outstanding.
## Mediator authorization-revocation candidate

`exp3/RESULT.md` records one successful bounded configuration: a Landlock-confined child, started with restrictions before exec and given only a retained local socket endpoint for attachment access, received an initial authorized mediator read. After authorization was revoked while child/socket stayed alive, the next operation was denied with zero bytes. Direct target and one symlink path returned EACCES. A separate negative-control process with a deliberately passed preopened FD read the fixture, confirming that such descriptors must not cross into the confined activity. This demonstrates per-operation authorization revocation in this tiny setup, not revocation of bytes already returned, arbitrary descriptors, or complete F3 acceptance. Stop broader runtime/lifecycle work; reconcile with partial F1 and keep F5 independent review outstanding.