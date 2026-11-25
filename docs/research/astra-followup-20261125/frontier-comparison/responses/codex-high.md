# Operator-supplied Codex responses (2026-11-25)

Transcribed from the operator's pasted message; table padding normalized. Model/effort labels are operator-reported, not independently attested. Common input: [v0.2.0 question](https://github.com/rock-solid-sites/ASES/blob/5385e4157c8506baf8e40d4bf288fec364656360/docs/research/astra-followup-20261125/frontier-comparison/WORK-UNIT-AUTHORITY-QUESTION.md). No elapsed-time, before/after allowance or token counts supplied for these specific responses.

## Astra 6.2 High

**Kernel-0 must make it possible to change who may act while preserving what they were acting on.** Its smallest defensible contract is that each authoritative change has a defined scope, an authorized basis, and a determinate outcome at the point the change takes effect. Work identity and prior outcomes must survive the loss of an execution. The packet leaves the representation of all three open.

### Authority and continuity

A sufficient abstract rule is to accept a requested transition only if the authority applicable to that operation and scope is current, its preconditions hold, and its whole declared result preserves the required invariants. Rejection leaves the requested state change unapplied. A rejection may itself be recorded. Conflicting changes need a consistent authoritative order wherever their order affects validity. Independent changes need no global order.

Changing eligibility is itself an authoritative transition. At an exclusive handoff, making Y eligible requires that X’s superseded authority can no longer justify a fresh change, even if X still runs, retains its credential, or later reconnects. A vacancy between X and Y is permissible unless continuous availability is separately required. Caller identity can help authenticate a request. A caller’s instructions, role label, or possession of an old representation cannot establish current entitlement.

A Work Unit identifies the continuing work and its authoritative continuation state. An Attachment Point identifies a durable position within that work across successive executions. An Execution is a temporary participant whose eligibility can change. These distinctions must be *expressible*. A kernel governing generic state, scoped authority, and conditional transitions could express them without three built-in object types. Work and vacant positions need no resident process. Orchestration can choose Y, review can judge its output, and resource planning can choose sharing or isolation. Kernel enforcement becomes necessary wherever those choices constrain an authoritative change.

### Five falsifying histories

| History | Required observation |
|---|---|
| **1. Loss and continuation.** X records progress on W/P and disappears. Later Y occupies P. | Y can recover the committed continuation under the same W/P. Recovering only X’s private memory, or creating equivalent-looking work under a new identity, fails this test. |
| **2. Stale authority.** X commits A, Y supersedes X, and X presents its old authority to commit B. | A remains accessible as history. B cannot take effect on that authority. Reusing P for Y must never make X’s old authority current again. |
| **3. Race.** X’s mutation overlaps the handoff. | If the mutation takes effect first, its valid result survives handoff. If handoff takes effect first, the old authority fails. A check before handoff followed by an unconditional write afterward admits a forbidden third outcome. Response times and transcript order cannot decide the case. |
| **4. Unresolved effect.** X obtains authorization for operation E. At handoff there is no reply. | E may still await dispatch, may be in flight, or may already have happened with its reply lost. Acceptance, external occurrence, and knowledge of the outcome are distinguishable facts. A late receipt can settle E under a current rule for recording evidence without restoring X’s authority. |
| **5. Scoped concurrency.** X at P and Z at Q are eligible on W. Y replaces X at P. | Z retains its independent eligibility. If Y and Z touch a shared resource, that resource’s conflict rule still applies. A work-wide revocation would wrongly disable Z. Position-local checks alone would miss a shared-resource invariant. |

### External effects and the trust boundary

The decisive question for an accepted but unfinished request is **what its acceptance authorized**. If acceptance durably committed an independent obligation, that obligation may survive X. If dispatch requires current execution authority, dispatch after handoff requires a fresh check at an enforceable boundary. Both policies fit the packet. Neither policy can recall a message already beyond that boundary.

Suppose the external recipient performed E and lost the reply. From Y’s perspective this can be indistinguishable from a history in which the recipient never received E. Retrying can duplicate the first effect. Suppressing retry can omit the second. Where continuation depends on E, it must preserve enough information to identify the outstanding operation and its uncertainty. Stronger guarantees require a stated recipient property, such as durable deduplication for the same operation or recipient-enforced fencing. A local record alone establishes neither.

The **most consequential uncertainty** is where each irreversible effect becomes authoritative and which participant can enforce the handoff there. An adequate model exposes external occurrence separately from local evidence and admits both race orderings. A realization has a separate obligation to show that every authoritative mutation path enforces the rule, that committed work and authority changes survive the claimed failures, and that any recipient guarantees it relies on actually hold.

## Sol 6.2 High

Kernel-0 needs to make one authoritative decision about each proposed change. At the point where the change takes effect, the authority covering it must still be valid, its preconditions must hold, and its full result must preserve the applicable invariants. Work can then survive executor replacement because the facts needed to continue it have a lifetime independent of the authority to change them.

### The minimum authoritative substrate

- **Durable facts and current authority have independent lifetimes.** The model must distinguish the work and its continuation state, historical outcomes, and the authority currently valid for a proposed change. Identity, role, instructions, and retained references can identify a caller or its past authority. Permission comes from a current authorization that covers the operation and its scope. A superseded authorization must stay unusable even if the same caller, attachment, or identifier is reused.
- **Validation and mutation form one decision.** A successful change applies its declared authoritative effects together. A rejected change leaves the facts it proposed to change intact. Authority changes themselves follow this rule under an explicit root of trust. A mutation and any revocation that would invalidate it require an authoritative order, as do changes that can jointly violate an invariant. Independent changes can remain unordered. This requires ordering the actual decisions, including their dependencies, beyond ordering requests, initial checks, or transcript entries.
- **Exclusivity has a scope.** The model must express which combinations of grants or states are incompatible. Replacement withdraws the authority being replaced and establishes the new authority without admitting a forbidden overlap. A gap is admissible if the handoff contract permits one. Other grants remain valid wherever their scopes and the invariants permit. Two writes to different records can still conflict if both consume the same exclusive entitlement.

These are semantic requirements. A generation counter, a lease, and a particular transaction mechanism are realization choices. If expiry or executor disappearance is meant to change eligibility, the model must say what trusted fact establishes it and when it becomes authoritative. A timeout alone leaves room for an executor that is still running.

### Work Unit continuity

A Work Unit can be expressed as durable work identity and continuation facts. An Attachment Point is a durable, addressable position associated with that work. An Execution is a temporary participant whose ability to act depends on current authority scoped to that position and any relevant resources. X can disappear while W and P remain addressable. Y can receive authority over the same W and P, and X’s outcomes can remain available under their original provenance. An inactive W or P needs durable representation and no resident executor.

This mapping can sit above generic authoritative facts, scoped grants, and conditional changes. Multiple positions or grants express concurrency. Overlapping resource scopes express sharing, disjoint scopes express isolation, and a mixture expresses hybrid use. Higher-level policy chooses participants, role profiles, resource allocation, scheduling, review, and how to interpret observations. Kernel-0 enforces the authoritative consequences of those choices. It needs a trusted basis for any external fact that a change depends on.

### The external-effect boundary

An authorized request, a committed intent, dispatch, an effect at the target, and observation of its outcome can occur at different points. Suppose X commits an intent before supersession, and Y becomes eligible while the outcome is unresolved. The target might already have applied the effect and lost the reply. It might still apply the effect later. The request might never have reached it. Those histories can look identical to Kernel-0 at handoff. Missing evidence therefore supports an **unknown** outcome. A late report can be attributed to X’s intent and evaluated under current evidence-handling authority. It cannot revive X’s authority to make new changes.

The effect contract must decide whether a committed intent carries permission to finish after handoff. If supersession must prevent an effect from taking place after the handoff, the target or an authoritative intermediary must enforce that boundary at the point the effect becomes irrevocable, across every path capable of producing it. An executor-side check before dispatch leaves a race. When the target provides neither reliable outcome lookup nor durable deduplication, retrying an unresolved request can duplicate an effect, and declining to retry can leave it undone. Y can still become eligible while policy holds a conflicting operation pending reconciliation. Stronger guarantees depend on what the target can enforce.

### Histories that can falsify the model

| Minimal history | Required result |
|---|---|
| X disappears. Y takes over P. | Y finds the same W and P and their authoritative continuation state. X’s outcomes remain attributable to X. |
| X retains an old handle. P is reassigned, then the same caller or identifier is reused. | The old authorization still fails. A fresh authorization can succeed on its own terms. |
| X passes an initial check. Supersession commits. X then attempts to commit. | The change is rejected without partial effects. In the reverse authoritative order, X’s valid commit survives supersession. The initial check and wall-clock ordering decide neither history. |
| Two requests each observe a free exclusive resource and propose changes to different records. | At most one incompatible claim commits. Superseding X at P leaves an independently valid grant at Q usable. |
| X’s intent commits. In one history the target applies it and loses the reply. In another the target never receives it. Y becomes eligible. | Both outcomes remain unknown on the evidence available at handoff. Any later conclusion or safe retry follows from the target’s guarantees and new evidence. |

Model adequacy requires representing these histories and their relevant orderings. Realization conformance requires showing that actual commits, recovery, and effect paths preserve those decisions within the claimed failure boundary. The most consequential open question is **where each external effect becomes irrevocable and whether that boundary participates in supersession**. The answer determines whether handoff can guarantee external exclusion or must carry unresolved effects forward.
