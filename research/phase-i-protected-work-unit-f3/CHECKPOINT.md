# Incomplete checkpoint — Agent D (F3 protected Work Unit)

- Branch: `research/phase-i-protected-work-unit-f3-20261029`
- Parent/base commit: `5c03a425fd5627c3764806292b8c5cb653498f4f`
- Crosslink: issue #10
- Provider session: `a6f5fdb3-8076-464d-829d-c20df6ef2827` (ended with HTTP 402)

## Executed observation

In the disposable assigned worktree, a child retained an open descriptor to a test file. After the parent changed the file mode to `000`, the retained descriptor still read the existing bytes, while fresh opens and fresh opens through the test grantor failed. After mode was restored, new access succeeded; stopping the grantor did not itself revoke the fresh path. This is evidence about the tested POSIX discretionary mode and fixture only, not general Linux revocation.

The ACL variant is inconclusive: the parent encountered `EACCES` traversing the test path, and the `no_new_privs` pre-exec hook was not applied in the plain run. No complete bypass inventory or final report exists. `probe/support/` contains unexecuted exploratory proxy/bodyguard drafts; these are not the accepted initial experiment.

## Incomplete work / next operation

Preserve the exact traces, explain which claim the descriptor result refutes, finish the bounded trusted-boundary inventory, then test the smallest viable mediated attachment in a disposable environment. Proceed to broader F3 lifecycle only after an exclusion mechanism passes the initial test and reconcile against B's F1 model.

## Artifacts

- `exp1/retained_handle.py`
- `exp1/observations-plain.json`
- `exp1/observations-acl.txt`
- `exp1/observations-acl-attempt.txt`
- unexecuted `probe/` drafts as identified above
## Resume checkpoint (2026-10-30)

Inherited plain-POSIX evidence: a descriptor opened before chmod 000 still reads existing bytes, while fresh path opens fail. Restoring mode permits fresh opens even after the holder is killed. This demonstrates permission-check behavior, not a revocable capability. ACL/no_new_privs remains inconclusive; proxy/bodyguard drafts are unexecuted. Next: complete minimal F3 report and trusted-boundary inventory from existing evidence. Preserve untracked exp1/run and snapshot. F1 remains incomplete; defer broader lifecycle and acceptance.
