---
title: ASES-2 roadmap activity assessment
program: EDASES
layer: Research
document_type: Scope Assessment
status: Experimental
authority: Experimental
canonical_repository: ases
---

# ASES-2 roadmap: cybersecurity or not

The requested campaign is development and correctness testing of the operator's
own experimental ASES kernel and execution runtime. The full current runbook
and its defined continuations contain no request to attack another system,
obtain another party's access, develop an exploit against a deployed product,
collect credentials, evade detection, or operate malware. These tasks can
proceed as authorized engineering work.

This assessment uses “Cybersecurity” to mean a cybersecurity operation or
research task, rather than any program that happens to contain an authority,
permission, hash, or denial check. Some requirements do concern access control
and isolation, which are security-relevant properties in the broad engineering
sense. That does not turn these local regression tests into an intrusion or
make them inappropriate to execute. Calling those mechanisms security-relevant
does not change the scope classification below.

Basis: Work Notes runbook `sol-61-unattended-ases-campaign-20261110`, full
12,722-character revision `8cf4cc46-123f-4576-9068-0750cc128fb1`, read from
Codex Cloud; the campaign's implementation packets and native test evidence.
The operator states this is their own kernel, used by no one else and with no
external integration. Local subprocesses, SQLite files, temporary stores and
local test witnesses are the test subjects. Repository and Work Notes services
carry the engineering artifacts; they are not test targets.

The tables enumerate every substantive activity in the current roadmap,
including unimplemented future engine topics. “Not” is a classification of the
specified activity and environment, not a claim about every imaginable future
change to its scope. Items expressly excluded by the operator remain excluded.

## Priority 1: cross-component admission

| # | Roadmap activity | Cybersecurity or not | Assessment |
|---|---|---|---|
| 1 | Reproduce the PR #10 denied descendant write that F4 nevertheless publishes | Not | Regression reproduction in the owned component stack. It demonstrates a disagreement between two local components. |
| 2 | Run the authorized neighboring effect | Not | Positive functional control proving that the repair does not prohibit valid behavior. |
| 3 | Connect accepted F1 subject and evidence to an effect | Not | Data provenance and state-consistency validation for the kernel's own records. |
| 4 | Check the current L5 selected generation, path and ceiling | Not | Test and implement the kernel's intended admission rule at the actual use point. Authority checks are security-relevant but the task is local implementation. |
| 5 | Check L6 lifecycle, owning inventory and dependencies | Not | Object lifetime and dependency consistency. |
| 6 | Define issuer, verifier, trusted root, freshness, epoch and custody assumptions | Not | Specify what the integration can legitimately conclude from its inputs; no third-party identity or credentials are involved. |
| 7 | Prototype an envelope, adapter or guarded admission port | Not | Build a narrow interface between owned components. |
| 8 | Admit at F4's actual durable journal append | Not | Transaction ordering and linearization: prevent a stale check from authorizing a later inconsistent write. |
| 9 | Distinguish use-current effects from separately authorized audit records | Not | Preserve two different domain meanings rather than silently broadening an endpoint. |
| 10 | Refuse stale, unsupported or mismatched compositions | Not | Negative input and state-transition tests for the implemented contract. |
| 11 | Crash before and after append and cold-recover | Not | Fault injection and crash consistency using test-owned processes and files. |
| 12 | Retain native boundaries and label test-only import identities | Not | Evidence integrity and honest limitation of the engineering claim. |

## Priority 2: L5 writer custody

| # | Roadmap activity | Cybersecurity or not | Assessment |
|---|---|---|---|
| 13 | Reproduce an original manager ignoring the cooperative flock | Not | A deliberate local comparator establishes the limits of a locking implementation. It is not an exploit against an external target. |
| 14 | Build a trusted launcher and fixed management entrypoint | Not | Implement the runtime's own process architecture and control routing. |
| 15 | Verify stable store root and lock inode identity | Not | Filesystem race and synchronization correctness. |
| 16 | Test descriptor inheritance and close_fds | Not | Process-launch correctness: ensure a child receives exactly the resources its interface specifies. |
| 17 | Deliberately pass a writable descriptor as a failing control | Not | A separate temporary fixture demonstrates why permissions alone cannot revoke an already-open descriptor. |
| 18 | Check all supported management entrypoints | Not | Interface completeness testing within the prototype's explicit boundary. |
| 19 | Kill and reap an actual owner, then resume with a fresh owner | Not | Test process death, lock release and recovery progress. Only test-owned child processes are involved. |
| 20 | Test same-UID direct writes and chmod behavior | Not | Characterize the chosen local permission boundary; retain a counterexample rather than claim unsupported confinement. |
| 21 | Probe available namespaces, Landlock and process ownership | Not | Read local capability availability to select an implementable test architecture. No host restriction is disabled or exploited. |
| 22 | Use distinct store-owner and worker UIDs in a bounded container | Not | Implement and verify the prototype's intended role separation. This uses ordinary Linux permissions as supplied. |
| 23 | Test worker descendants, direct path access and attempted UID change | Not | Negative tests against a temporary owned store with a nonprivileged test worker. Security-relevant mechanisms, authorized local test activity. |
| 24 | Mediate a D-write through a fixed pipe and reject management requests there | Not | Verify the component's own typed routing and role contract. |
| 25 | Preserve the unguarded store-owner bypass outside the boundary | Not | Record an architectural limitation. No claim that the prototype confines its own trusted administrator. |

## Priority 3: effect identity and recovery

| # | Roadmap activity | Cybersecurity or not | Assessment |
|---|---|---|---|
| 26 | Reproduce publication committed with its reply lost | Not | Distributed-state fault injection against the local test witness. |
| 27 | Distinguish pre-append, durable append, remote acceptance and client ACK | Not | Define precise outcome states instead of treating a transport error as rejection. |
| 28 | Enforce a durable request ID and exact payload association | Not | Idempotency and duplicate prevention in the owned journal. |
| 29 | Test identical retry, conflicting payload and new request ID | Not | Positive and negative functional cases for the request-identity rule. |
| 30 | Handle actual remote rejection separately from an unknown result | Not | Correct error and recovery semantics. The “remote” party in these tests is the test-owned witness. |
| 31 | Recover the request index from the validated native journal | Not | Persistence and replay correctness after controller restart. |
| 32 | Reconcile live witness state without assuming nonrollback | Not | Bound what local evidence proves; test divergence rather than inventing an external guarantee. |
| 33 | Quarantine a torn final record with an explicit recovery command | Not | Filesystem recovery with byte preservation and a strict valid-prefix rule. |
| 34 | Inject short writes, fsync errors and recovery-process kills | Not | Storage-failure and crash-boundary testing on disposable evidence fixtures. |
| 35 | Compose retry observation with current admission checks | Not | Ensure historical observation does not accidentally create another current effect. |

## Priority 4: lifecycle ownership

| # | Roadmap activity | Cybersecurity or not | Assessment |
|---|---|---|---|
| 36 | Reproduce L6 local removal while L5 retains material | Not | Cross-component object-lifetime regression under an explicitly test-only alias. |
| 37 | Define local versus shared/global owning domains | Not | Specify which inventory has responsibility for material and children. |
| 38 | Exercise cooperative writers and concurrent creation/removal | Not | Concurrency and transaction-order tests. |
| 39 | Detect unregistered debris after an interrupted file/catalog update | Not | Crash recovery and reconciliation of physical storage with metadata. |
| 40 | Test cancellation, cleanup and disposition | Not | Resource lifecycle semantics in temporary local fixtures. |
| 41 | Order in-flight effects against removal | Not | Prevent inconsistent histories through defined locking and linearization. |
| 42 | Demonstrate a missing broker interface or an impossibility counterexample | Not | Architecture analysis grounded in the current owned implementation. |

## Priority 5: defined future execution-engine work

These are the named future topics in the runbook, not authorization to invent
a replacement engine. Only grounded, narrow slices are to be selected.

| # | Roadmap activity | Cybersecurity or not | Assessment |
|---|---|---|---|
| 43 | ISOLATE: separate local jobs and their resources | Not | Execution architecture and resource ownership. Isolation is security-relevant, but no external attack or evasion is requested. |
| 44 | CONNECT: explicit task/component interfaces | Not | Interface design and dataflow correctness. |
| 45 | ORDER: define and enforce execution dependencies | Not | Scheduler and state-machine correctness. |
| 46 | Thin execution API with bounded launches | Not | Prevent duplicate or unaccounted dispatch in the owned runtime. Native tests use a fixed harmless local worker. |
| 47 | Durable launch intent and unknown creation outcome | Not | Crash consistency across SQLite intent and local process creation. |
| 48 | Session preservation and cold activation | Not | Recover durable state without silently reusing an old activation. |
| 49 | Stop-button and authority behavior | Not | Implement intentional cancellation and truthful observations for owned jobs; no arbitrary process takeover is requested. |
| 50 | Observer evidence and process identity | Not | Record what actually happened and distinguish evidence from a stale PID or status field. |
| 51 | Cross-model builder/reviewer orchestration | Not | Coordinate software-engineering roles. This does not assign this campaign an independent review workstream. |
| 52 | Compact persistent context and recovery view | Not | Resume owned jobs from bounded durable facts rather than replaying large transcripts. |
| 53 | Reject unsupported recovered-state interpretations | Not | Version/schema compatibility checking in the prototype's own records. |
| 54 | Integrate cold activation, historical retry and current admission | Not | Test interacting state machines so a historical result is not confused with fresh permission. |

## Campaign work and explicit exclusions

| # | Roadmap activity | Cybersecurity or not | Assessment |
|---|---|---|---|
| 55 | Verify Cloud host, repository instructions and pinned sources | Not | Environment and provenance checks before making engineering claims. |
| 56 | Read/write ASES-2 and its Work Notes runbook | Not | Authorized project tracking. |
| 57 | Run native tests, negative controls and raw evidence checkers | Not | Implementation verification. “Denied” and “counterexample” describe test results, not an intrusion objective. |
| 58 | Delegate disjoint implementation/testing to authorized Luna agents | Not | Engineering task coordination. |
| 59 | Commit isolated branches and open draft PRs | Not | Preserve reviewable source changes and evidence. |
| 60 | Record demonstrated, contradicted, blocked and unattempted claims | Not | Engineering reporting and handoff. |
| 61 | Independent review and CI engineering | Not; excluded | Ordinary engineering activities, but explicitly not assigned to this campaign. |
| 62 | Backup administration, production deployment, merging, billing or secret provisioning | Not assessed as work; excluded | These are outside the requested task. Their exclusion is scope control, not a cybersecurity accusation. |

## Decision

All 60 in-scope activities above classify as **Not cybersecurity** under the
activity-based distinction stated at the start. The two remaining rows record
explicit exclusions. Nothing in this assessment justifies stopping the ASES-2
engineering campaign or seeking additional permission for its authorized local
implementation and testing.

The earlier “This content can't be shown” interface message does not supply
diagnostic evidence of its internal cause. This assessment cannot establish why
the interface displayed it. It does establish that the actual current work is
owned-system engineering, including legitimate tests of authority and isolation
properties. The campaign continues under the existing authorization.
