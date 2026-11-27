---
title: A local owner witness for activation, replacement and replay
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# A local owner witness for activation, replacement and replay

Once X has sent an append and exited, its process state cannot tell Y what to recover. In a local experiment, killing the owner immediately before its SQLite commit and immediately after that commit produced opposite correct replies to the identical old request. In each case Y could append to the same W/P after replacement. This supplies executable W5/W6-shaped evidence for a new, single-store experimental owner. The November review's separate conclusions about the native content and Rust custody stacks still apply to those stacks. [Review and acceptance criteria](../astra-followup-20261125/round25/WORK-UNIT-AUTHORITY-RUST-CUSTODY.md)

## Owner crosswalk

| Obligation | Where the experiment represents it |
| --- | --- |
| Continuing boundary | The protected selector row is keyed by W and P. A second position Q in the same W is exercised with the same request nonce. Resources A and B are fixed scoped names within a position. |
| Provenance and control | The owner mints a random 256-bit bearer on a separate management channel and records its W/P and generation. The worker submits that bearer, a request nonce, a resource and payload. Lookup at the owner supplies W/P and tenure. The worker has no management operation on the worker channel. Possession is the execution credential in this contract. |
| Whole replacement | Management supplies W/P and the expected current generation. In one transaction the owner installs a fresh grant and changes the current selector. Repeating the old expected generation is refused. The selector serializes all positions in one process/store in this experiment. |
| Whole admission | For a request with no prior outcome, the owner compares the authenticated grant to the selector and inserts the entire append inside the same transaction. The effect is the committed row. No post-commit delivery is needed for local visibility. |
| Exact retry | The same grant and nonce with identical resource and payload retrieves the original receipt. A conflicting reuse of an accepted nonce is refused. Only accepted appends are memoized. Retired grants can retrieve that receipt, and cannot read current contents or append fresh data. A current grant reads scope-bound durable bytes. |

The reference relation maps each store to its selectors, issued grant bindings and scope-filtered sequences of committed rows. An accepted insert extends exactly one such sequence. Replacement changes admission and preserves every sequence. A replay reads an existing row and leaves the projection fixed. Rollback before commit removes an uncommitted row. The induction uses SQLite's transactional semantics and one exclusive owner of the database. The test exercises these statements at selected process-loss cuts.

## Three distinguishable histories

Run `python3 docs/research/kernel-0/local_handover_owner.py` on a system with Python multiprocessing, POSIX process termination and SQLite. The test makes a disposable database per history and starts the owner using the spawn start method. A separate X process gets only the worker pipe and its prepared request, sends once, and exits. A trusted harness retains X's credential to probe delayed uses after replacement. A management-only test hook parks the owner at each specified point. The harness uses explicit acknowledgments of those points. It does not infer them from elapsed time. [Executable witness](local_handover_owner.py)

| Last event for X before management acts | Owner and replacement sequence | Reply to exact retry by X | Durable contents read using Y |
| --- | --- | --- | --- |
| Request delivered and queued before admission | Commit X→Y while X is queued, then process the old request | Stale, including the queued original | B contains Y's append |
| Row inserted inside open transaction | Kill the owner, reopen the store in a new process, commit X→Y | Stale | B contains Y's append |
| Commit returned, reply withheld | Kill the owner, reopen the store in a new process, commit X→Y | Original receipt 2 | A contains X's append once, B contains Y's append |

All three histories passed using SQLite 3.53.1. Q retained its own content and issued receipt 1. A fresh X request to B was denied after the A probe, old X could no longer read contents, a made-up bearer was refused, worker-side installation was refused, and stale management expectation could not replace Y. The before-admission hook exposes both the arrival order and the distinct decision order. The before/after-commit pair discriminates between fresh work and recovery of a previously accepted local outcome. The accepted bytes and retry identity are in the same row, eliminating a second store whose recovery cut would need alignment. [Residual fence argument](Which-gates-must-fence.md)

## Trust and remaining correspondence

ISOLATE here assumes exclusive trusted access to the database, grant material and management channel. CONNECT is an owner-minted bearer binding. ORDER uses the owner's transaction boundary. Process spawning separates the tested interfaces, but the harness runs under one OS principal. OS-level confinement against a malicious same-user worker, exclusive delivery to a particular executor, confidentiality of bearer material, management credential recovery and denial-of-service handling require separate evidence. A bearer can be copied. Grant uniqueness is constrained in the store and security against guessing depends on randomness. The protocol retains accepted receipts and old grants indefinitely.

The execution covers process termination and reopening one local store on the same host. Physical power failure, rollback of an authentic older database, lost management replies, hostile inputs, an independent external sink, distributed resource owners and engine integration remain open. This witness addresses local membership fixed at two resource names. It cannot validate the distributed membership construction. The working Work Unit and kernel designs receive evidence for this particular behavioral slice only.
