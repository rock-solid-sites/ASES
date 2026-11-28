---
title: What evidence can restore current owner selection?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Restoring-history-without-restoring-authority.md
  - docs/research/kernel-0/Native-acceptance-and-recovery-boundaries.md
  - docs/research/kernel-0/Committing-to-a-surviving-cut.md
last_updated: 2026-11-28
---

# What evidence can restore current owner selection?

A native owner can retain the file for a selected reservation without retaining proof that the reservation was selected. If the contract requires recovering that decision exactly, either the selection evidence itself must survive or the operation needs an earlier surviving decision that determines what recovery must do. If the contract allows release of eventless reservations after a fence, the recovered visible outcome can be the same for a formerly selected reservation and an abandoned candidate. That weaker contract still has to preserve old authorities, effects and promises that escaped before the fence. [Native indistinguishability pair](Restoring-history-without-restoring-authority.md)

## Three recovery contracts

Suppose a selector's local pointer can roll back while all immutable candidate records survive. The old owner and effect owners may have separate failures. Meaningful identities and scope are protected. A trusted part of the state supports recovery after the declared failure.

| Contract | Minimum kind of evidence | What can remain provisional |
| --- | --- | --- |
| Exact recovery of every selected owner decision, including an eventless reservation | Evidence that distinguishes which candidate was selected, bound to the authority scope and current cut | Local cache reads, if every consequential reader resolves the authoritative selection |
| Exact recovery of every consequential observation or effect, plus a unique outcome for ambiguous unobserved attempts | Evidence for those observations and effects. A prior durable obligation can force completion before a later local change is made. A safe abandonment rule can handle the remaining indistinguishable attempts. | An internal step whose alternatives cannot affect any promised answer or retained effect |
| Safety with fail-closed recovery | Authenticated authority to permit whatever action survives all compatible histories. When that intersection contains no useful next action, recovery can defer. | Completeness, progress and exact diagnostic certainty |

These contracts differ even if the stored record types are identical. A successful acknowledgement, an issued enable, reliance by a downstream appender and completed disposition are all consequential. A useful work history can already be affected before the user receives any reply.

**Boundary argument.** Let two executions have the same recoverable state and future recovery inputs. If the contract requires different outcomes, no deterministic recovery can meet it for both. A protocol that may randomize with zero error has the same problem. Adding a protected receipt *after* the first step that the contract makes consequential leaves the interval in which the receipt is absent. Increasing the local record number or hashing the candidate only establishes which bytes are available. The earlier native argument places this interval between record installation and pointer selection. A fresh F4 publication can certify the prior effect it actually names but cannot certify an unrelated owner-only change. [Native source crosswalk](Native-acceptance-and-recovery-boundaries.md)

## A witness at the selection boundary

One sufficient reference design is a protected compare-and-select operation per mutually dependent scope. Its use is conditional on a trusted non-forking implementation. It is an authority operation, so a compare-and-swap with caller-supplied expected bytes alone is insufficient.

1. Prepare immutable candidate bytes, naming the scope, immediate selected predecessor and relevant policy version. Retain the bytes and required references through the loss contract. Preparations by themselves confer no authority.
2. Authenticate the management caller. At the protected decision, establish that its grant is current, that the named predecessor is still selected, and that the proposed change is valid against that predecessor and any necessary current external facts. Select the candidate and record the stable request result as one decision, or provide a recoverable equivalent. Fresh identities are required when the same candidate bytes could recur with different authority.
3. Serve current observations and admit effects from the protected decision. A pointer in the rollback domain can cache the result. Recovery reads the protected selection, checks its bound material, and rebuilds any cache before allowing new effects. Replaying the same request observes the recorded outcome. A different candidate using the same key is a conflict.
4. Serialize commitment against any operation that could use superseded authority. A simple local realization could share a transaction. A separate gate could instead use an already proved fencing protocol. A previously correct pointer read followed by an unguarded append does not implement this step.

**Invariant.** Each selected value names one retained, validated candidate with the previously selected value as predecessor. Only the protected decision extends the selected chain. A discarded stage changes no authoritative fact. Idempotent reobservation changes no selected value. Recovery validates the proof and resumes from the unique retained selection. It can ignore whether a local pointer reflected it before loss. Serialization or fencing preserves the authority guard against a concurrent successor or revocation. If the protected witness and candidate bytes can be lost together, this proof has no such recovery premise. [Related protected append decision](Committing-to-a-surviving-cut.md) · [Commit coordination and durable decisions, Gray and Lamport](https://www.microsoft.com/en-us/research/publication/consensus-on-transaction-commit/)

Writing “intent” in a surviving log before local publication can be equivalent only when the record fixes the admissible outcome strongly enough. If the log records an authorized decision that must be completed, the local pointer is materialization. If recovery is free to choose independently whether an acknowledged operation happened, the name “intent” has not solved detectability. If the protocol lets the local pointer confer authority before the surviving record is fixed, there is still a hidden cut.

## When exact reservation recovery can be eliminated

Consider the two indistinguishable native histories where an eventless reservation may or may not have become selected. Ask for a contract in which pending work can be retired, with no loss of accepted effects. They can share a canonical recovery outcome only if both permit it.

A useful sufficient case is a **protected cancellation cut** that proves all of the following.

- No independent old path can complete the request after the cut. An in-flight operation has either reached its authoritative effect or lost all ability to do so. Delayed work, old credentials and escaped enables are covered by the same closure criterion.
- The effect evidence is complete through the closure cut. If the request appears, preserve it as accepted and reconcile exactly. If it does not appear, no actual acceptance is discarded.
- The reservation did not create a separate irrevocable obligation. If it could authorize capacity release or allocate a resource outside the append journal, that authority and its outcome require independent evidence.
- The terminal retry contract explicitly permits the chosen cancellation or unknown result. The implementation can keep a stable request key or issue a new incarnation so a delayed retry cannot create the abandoned effect again.

With these premises the two eventless histories have a common future behavior. Both may cancel the attempt and resume under a fresh, fenced scope with actual accepted work retained. This is an elimination witness for *one exact-history distinction under a changed contract*. It leaves the need to prove final effects and scope closure intact. The native source currently refuses eventless reconciliation, so this argument cannot be used to justify clearing its pending record. [Final effect extent](Custody-at-an-admission-closed-cut.md) · [Native pending behavior](Native-acceptance-and-recovery-boundaries.md)

**Disposition.** Source and existing evidence settle that a stronger exact-selection claim needs either surviving selection evidence or a stronger outcome-determining protocol. The contract choice remains open. Before an implementation investigation, choose whether eventless reservations must be recovered exactly or may be cancelled at a proven closure cut. Under exact selection, the cheapest discriminating future comparison is a candidate that physically survived without selection versus one selected before pointer rollback, including any reader or appender able to observe selection before the protected witness. Under cancellation, the discriminating case is a last in-flight effect on each side of closure with identical pre-closure pending evidence. Neither runtime matrix has been admitted or executed here.
