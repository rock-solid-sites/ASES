# F3 authority-holder-loss experiment

Date: 2026-10-30. Status: **narrow selected-profile success, with a detected unsafe-mutant counterexample**. This is not F3 lifecycle closure, general confinement, D2, or arbitrary sink evidence.

## Boundary and reconciliation

Starting branch/worktree: `research/phase-i-protected-work-unit-f3-20261029`, base/origin HEAD `ad44b3ff93477cc694a5b0771c3b867afdfde620`. Packet read from `origin/planning/ases-phase-i-f3-authority-loss-20261030` commit `906ec6bd1ada2225b430b5b2ad91ef5176952783`; F1 model read at `d227a22b9bbc0732881bf58f6933ce46fddc08fa`; F2 coverage read at `5fb690d4ba7544a4a7eb5fce9ca1e54485543d64`. Existing `exp3/mediator_revocation.py` and `exp3/RESULT.md` were also reread before editing.

Reconciliation: F1 stop/recovery remains abstract/prepared-only physical evidence; F2 T05 remains prepared-only. T03, T20, and T24 remain model-only. This run advances only selected T05 read/CPU/holder-loss observations. It supplies no physical source-binding/old-capability result for T03, no physical holder fencing/takeover proof for T20, and no real ACL partial-application/open-handle result for T24. F1 C6/C13 abstractions and F2 T03/T20/T24 are not counted as physical evidence.

Actors: supervisor S, holder H, worker W, protected sentinel R, and mediator M. In the candidate, **H=M**: one disposable process owns the sentinel pathname access and request-serving socket endpoint. W has no target FD; its only deliberate protected attachment is its retained endpoint of a local socketpair. In the fault control, H and M are separate: H is killed while M deliberately retains and uses its stale cached grant. No control-message REVOKE is sent in either profile.

## Reproduction and environment

VPS worktree only: `/home/claude-code/.paseo/worktrees/216s81dw/phase-i-d-protected-work-unit-f3`. Linux `5.15.0-184-generic` (x86_64); Python `3.10.12` (GCC 11.4.0). Disposable fixture is this directory's `fixture/`; sentinel is `sentinel.txt`, with in-tree symlink `alias.txt`. Sentinel bytes are `authority-loss-sentinel-v1`; SHA-256 `eabb8101e77acddab40225156f2db71b7cda7ef722acd0d9bc816533c6d3e9de`.

Exact verification/run commands:

```sh
python3 -m py_compile research/phase-i-protected-work-unit-f3/authority-loss/authority_loss.py
timeout 20s bash -c 'ulimit -v 196608; python3 research/phase-i-protected-work-unit-f3/authority-loss/authority_loss.py > research/phase-i-protected-work-unit-f3/authority-loss/run.json'
sha256sum research/phase-i-protected-work-unit-f3/authority-loss/authority_loss.py research/phase-i-protected-work-unit-f3/authority-loss/run.json
```

The run completed in ~0.233 seconds, below the 20-second outer bound; virtual address-space limit was 196608 KiB. One runner, two sequential profiles. The worker restriction reuses exp3's Landlock ABI-1 helper: PR_SET_NO_NEW_PRIVS and Landlock are applied in `preexec_fn` before exec; only read_file/read_dir rights are handled, with runtime read paths allowed. The target and alias are outside those allow rules. No packages, sudo, sysctl, production service/policy, `/tmp`, real credentials, or external network were used.

Source SHA-256: `a933c0bda83fa1387f7548d2a40af9fde08531ed255b8e81c9c4c3e3f0dd435b`.
Run JSON SHA-256: `d0ccc00cb5f7fe4528c84e9f1b30d095a70d1ca85c931ca3374a1da7efc03947`.
Raw PIDs, monotonic timestamps, return codes, replies, worker CPU counts, direct/alias errors, and mediator traces are in `run.json`.

## Observations

**Candidate (H=M):** baseline W PID 183186 received `OK authority-loss-sentinel-v1` at monotonic ns `202723672727629`. S requested SIGKILL for H/M PID 183185 at `202723672943196`; independent `wait()` reaped it with return code `-9` at `202723674246146`. W was triggered only after that reap (`signal_ns=202723674293221`), performed CPU-only arithmetic (`cpu_start_ns=202723674314413`, `cpu_end_ns=202723754316693`, 2,438,677,479 loop iterations), then attempted a new read over its same retained socket. The peer was gone (`IOERROR:32`, EPIPE); no sentinel bytes were delivered. W stayed alive through this sequence and exited 0 after reporting. Its post-loss direct target and symlink opens both returned EACCES/errno 13. No explicit revocation message preceded H loss.

**Fault control (H separate from M):** baseline W PID 183189 received the sentinel. H PID 183187 was SIGKILLed and independently reaped at `202723793161733` (return `-9`). W was triggered afterward, continued CPU work, and requested the same operation over its retained socket. Surviving M PID 183188 used the intentionally stale cached grant and returned `OK authority-loss-sentinel-v1`; `second_has_protected_bytes=true` and `violation_detected=true`. This is an unsafe mutated control and a concrete counterexample to treating H loss alone as revocation when M survives with stale authority. It is not a passing safe configuration.

**Disposition:** the candidate meets the packet's narrow nonvacuous baseline and post-loss denial for this one selected attachment under the explicit H=M process-lifetime coupling. The detector is sensitive to the separate stale-grant failure. Confirmed only for this fixture and its tested routes.

## Selected-profile route inventory

| Route / resource | Disposition in this fixture | Evidence / boundary |
|---|---|---|
| R via target pathname (read) | Fully mediated or denied | H=M opens R only for each socket request while alive; after H death no mediator remains. W direct post-loss open denied EACCES. Arbitrary filesystem aliases are not covered. |
| In-tree symlink alias (read) | Fully mediated or denied | Explicit post-loss open denied EACCES. One symlink only. |
| Other path aliases / bind mounts / alternate roots | Untested / excluded | No alias enumeration or mount manipulation. |
| Open/inherited target FD | Disabled in candidate | No target FD passed; Popen uses `close_fds=True`, `pass_fds` contains only W's client socket. No preopened target FD in W. Existing exp3 separate preopened-FD negative control remains recorded in `exp3/RESULT.md` and showed the FD can bypass path controls; it is not this candidate's evidence. |
| Other inherited descriptors | Partially inventoried; untested beyond setup | W also has standard descriptors and its stdout/stderr reporting pipe; no target FD. Exact `/proc` FD snapshot was not captured. |
| SCM_RIGHTS / descriptor passing | Disabled by fixture code; adversarial use untested/excluded | No `sendmsg`/`recvmsg` descriptor transfer occurs; mediator sends bytes, not an FD. No hostile peer test. |
| Descendants | None created by tested W code; arbitrary descendants untested/excluded | W does not spawn children in the trace. Landlock does not itself prevent fork/exec; no claim about a hostile descendant tree. |
| Retained local socket | Fully mediated in candidate | It returns sentinel before loss; after H=M SIGKILL and independent reap, same socket gives EPIPE and no bytes. In mutant, retained socket reaches surviving stale M and returns protected bytes. |
| External/network routes | Untested / excluded | No external network used or endpoint provided. No network namespace/seccomp policy; Landlock ABI-1 setup here does not claim network confinement. |
| Credentials | No real credentials provided; route untested / excluded | W inherits the disposable runner's Unix identity/environment. No credential files/secrets were configured; no credential isolation claim. |
| Shared resources | Limited observation; otherwise untested / excluded | R is a local file read only by H/M and W reads returned bytes. Other shared filesystem, mappings, shared memory, and writes are outside this test. |
| Actual authorization state | Observed | In candidate, the only current request-serving state/access is in H=M; process death removes it and closes the socket. In mutant M retains `authorized_from_cached_grant=true` and demonstrably serves after H loss. |
| Landlock policy state | Applied before W exec; partial application not tested | S's pre-exec helper constructs/applies ABI-1 rules and NNP. W cannot relax an inherited Landlock domain under NNP, though further restriction is possible. No partial/failed syscall application mutant was exercised. Host administrator/root policy alteration is outside the experiment. |

The fixture enforces read-path restrictions only for the declared object/alias observations. Landlock's configured handled rights are read_file/read_dir; writes, arbitrary sinks, network, credential access, and full descriptor closure are not established. S creates the fixture/policy and controls the SIGKILL; H=M's process code owns mediation and pathname access. No separate policy-update/revalidation mechanism or partial-application behavior was tested. The result depends on the observed process-lifetime coupling; killing H does not revoke a grant cached by another still-running M, as the fault control proves.

## Limits and stop

One worker, one logical holder, one mediator/path, one sentinel, one local socket, one symlink, two sequential requests, and one stale-grant mutant. No in-flight-before-loss ordering, already-returned-byte erasure, hostile socket peer, all-FD inventory, process-tree containment, race stress, production realization, power-loss/recovery, source identity, arbitrary sink, general proxy/runtime/lifecycle, or F3 lifecycle closure is claimed. T18 use-current, broad T03/T20/T24, and all remaining F1/F2 gaps remain outside this implementation. Stop at this packet's narrow success plus its explicit counterexample control; independent review remains separate.
