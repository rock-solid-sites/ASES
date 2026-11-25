# **Independent architectural derivation — ASES Kernel-0 and Work Unit substrate**

**Basis:** The supplied reasoning packet, version 0.2.0, pinned to commit `5385e4157c8506baf8e40d4bf288fec364656360`. I treat its established requirements as premises and its discriminating histories as model-adequacy obligations, not as a prescribed architecture. No previous implementations or other participants' conclusions are used.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://raw.githubusercontent.com\&sz=32)

GitHub



## **1. Central conclusion**

Kernel-0 should be understood as a **minimal substrate governing authoritative state transitions and the validity of authority across changing execution circumstances.**

It should not fundamentally be an execution engine, process manager, workflow engine, or Work Unit manager.

The essential architectural distinction is between:

- What continues to exist.
- What is presently permitted to change it.
- What temporarily performs that change.
- What has already been authoritatively decided.
- What has actually happened outside the authoritative boundary.

These distinctions cannot safely be collapsed, even if a particular realization represents several of them using the same mechanism.

The Work Unit architecture requires durable continuity under changing execution authority. The kernel must make that architecture enforceable, but it need not understand the domain meaning of work.

**Replacement is fundamentally a change in authority, not a change in the identity of work or necessarily the termination of a process.**

## **2. Necessary semantic distinctions**

The following are semantic necessities, not proposed kernel object types.

| Distinction                                     | Why it is necessary                                                                                    |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Authoritative state vs. proposed state          | A request must not become truth merely by being submitted.                                             |
| Persistent identity vs. temporary execution     | Work must survive executor disappearance and replacement.                                              |
| Possession vs. current authority                | Retaining an old reference or credential must not preserve revoked permission.                         |
| Authority validity vs. transition admissibility | Even an authorized executor can request an invalid state change.                                       |
| Authority scope vs. executor identity           | One executor may have different permissions over different state or resources.                         |
| Historical authority vs. present authority      | A previously legitimate outcome must remain distinguishable from a new action under expired authority. |
| Request acceptance vs. authoritative commitment | An admitted request may still fail its final conditions.                                               |
| Authoritative commitment vs. external effect    | An internal decision does not establish that something happened externally.                            |
| Unknown outcome vs. known failure               | Missing evidence cannot establish non-occurrence.                                                      |

The strongest minimality argument is observational: if two histories require different permissible subsequent behavior, the substrate must preserve enough information to distinguish them.

Conversely, if a distinction does not change permitted authoritative behavior, recovery behavior, or a required observable outcome, there is no demonstrated reason to make it intrinsic to Kernel-0.

## **3. The smallest plausible authoritative model**

A sufficient starting hypothesis is that the kernel governs three logical categories of information:

\\[ K=(S,A,H) \\]

| Element | Meaning                                                                              |
| ------- | ------------------------------------------------------------------------------------ |
| \\(S\\) | Current authoritative state                                                          |
| \\(A\\) | Facts determining currently valid authority                                          |
| \\(H\\) | Retained historical facts and commitments required for continuity and accountability |

This is a conceptual decomposition. Authority and history could themselves be represented within authoritative state. There is no requirement for three independent stores.

External reality, \\(E\\), is deliberately excluded from this tuple. The kernel may possess evidence about external reality, but its possession of evidence and the external reality itself are different facts.

### **3.1 Authoritative transitions**

For a requested transition \\(r\\), commitment requires:

\\[ \begin{aligned} &\operatorname{ValidAuthority}(A,r)\\\ {}\land{}&\operatorname{InScope}(A,r)\\\ {}\land{}&\operatorname{Admissible}(S,r)\\\ {}\land{}&\operatorname{Invariant}(K') \end{aligned} \\]

Here, \\(K'\\) is the permitted successor state.

Crucially, these conditions must hold in relation to the **same authoritative transition**, not merely at independent moments preceding it.

An authority check performed when a request arrives is insufficient if the resulting mutation can commit after that authority becomes invalid.

A rejected transition must not silently apply a subset of the requested changes, substitute a different mutation, or leave authoritative state partially modified. Explicitly specified rejection records are compatible with this requirement.

This implies atomicity at the semantic boundary of the requested authoritative change, but it does not prescribe a database, transaction mechanism, global lock, or instruction set.

### **3.2 Authority must itself be governed**

Authority creation, modification, delegation where supported, and withdrawal are authoritative changes.

A caller must not be able to manufacture permission by modifying its own authority representation.

This requires a trusted authorization foundation: initial authority and the rules governing subsequent changes to authority.

The model cannot derive legitimate initial authority from nothing. Bootstrap authority is an explicit trust assumption, not something that recursion through an authorization mechanism resolves.

### **3.3 Minimal invariants**

I derive seven invariants:

| Invariant                     | Required property                                                                                            |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **I1 — Integrity**            | Authoritative state changes only through permitted transitions.                                              |
| **I2 — Current validity**     | New executor-originated mutations require authority valid at their authoritative decision point.             |
| **I3 — Non-resurrection**     | Superseded authority cannot become usable accidentally through identifier reuse or retained representations. |
| **I4 — Compatibility**        | Authoritative combinations prohibited by applicable constraints cannot coexist.                              |
| **I5 — Continuity**           | Executor loss does not inherently destroy required durable work state.                                       |
| **I6 — Failure atomicity**    | Rejected or interrupted authoritative changes do not expose unintended partial states.                       |
| **I7 — Historical integrity** | Supersession does not retrospectively invalidate legitimate past outcomes.                                   |

None requires Work Units, attachment positions, or executions to be hard-coded kernel entities.

## **4. Deriving the Work Unit architecture over Kernel-0**

The three-level architecture can be expressed using stable identities, governed relationships, and scoped authority.

### **Work Unit**

A Work Unit is a stable domain identity associated with durable work state.

Its existence must not depend on the existence of an active executor. It may be inactive, suspended, awaiting input, or undergoing replacement without ceasing to be the same work.

The kernel does not need to understand what successful completion of that work means.

### **Attachment Point**

An Attachment Point is a stable logical position through which execution participates in work.

Its independent significance is that continuity can belong to a particular position within work rather than to the whole Work Unit or to a particular executor.

It need not be a resident process, live connection, reserved thread, or permanently allocated execution resource.

Whether it has a dedicated representation or is derived from other authoritative relationships is not determined by the requirements.

### **Execution**

Execution is a temporary participant that may exercise externally governed authority.

Its identity, existence, current activity, and eligibility to perform authoritative mutations are separate facts.

In particular:

\\[ \operatorname{Alive}(X) \not\Rightarrow \operatorname{Authorized}(X) \\]

Nor does executor disappearance necessarily establish that its authority has been withdrawn. That depends on the governing validity rules and trusted evidence of disappearance.

### **Replacement**

Replacement changes the applicable authority relationship while preserving the relevant continuity identity.

For an exclusive attachment position:

Before replacement

**W / P**

Authority X

After replacement

**W / P**

Authority Y

Old authority X invalid

Persistent identity is unchanged. Previously committed X outcomes remain part of history.

Invalidation of X's relevant authority must precede or coincide with activation of incompatible authority for Y. An interval in which neither is eligible may be permissible.

A gap-free, instantaneous handover is a stronger availability requirement and is not established by the packet.

## **5. Concurrency and exclusivity are constraints, not modes**

There is no demonstrated need for separate kernel modes for single, sequential, parallel, or collaborative execution.

Instead, the substrate must enforce the compatibility conditions applicable to the relevant authority and state.

For example:

| Configuration        | Permitted arrangement                                             |
| -------------------- | ----------------------------------------------------------------- |
| Single execution     | One eligible authority within a defined scope                     |
| Sequential execution | Different authorities become eligible over time                   |
| Concurrent execution | Multiple compatible authorities coexist                           |
| Isolated resources   | Authority scopes do not overlap for designated resources          |
| Shared resources     | Multiple participants operate under applicable shared constraints |
| Hybrid resources     | Compatibility varies by resource and operation                    |

Exclusivity may apply to authority holdings, authoritative state, or operations on a resource. These are different forms of exclusivity.

Two executors may legitimately coexist while particular mutations remain mutually incompatible. Conversely, executors attached to different positions may still conflict over a shared resource.

**Therefore, attachment identity alone cannot define the complete conflict boundary.**

The kernel requires an enforceable notion of compatibility, not an understanding of organizational roles such as reviewer, planner, worker, or supervisor.

## **6. The decisive race: mutation versus supersession**

Let:

- \\(M_X\\) denote a new mutation requested by X under its existing authority.
- \\(R\_{X\to Y}\\) denote supersession of that authority and replacement by Y.

There are two decisive authoritative orderings.

History A — Mutation commits first

History B — Supersession commits first

These diagrams represent authoritative ordering, not wall-clock time.

Assuming the mutation is otherwise admissible, History A may succeed. History B must reject the mutation under the superseded grant.

### **The forbidden interleaving**

Consider:

1. X's authority is checked and found valid.
2. Supersession commits.
3. Y becomes eligible.
4. X's mutation commits using the earlier authorization result.

This is invalid if step 4 is the first authoritative commitment of that mutation. Earlier validation cannot justify a later unauthorized commitment.

If an earlier step already committed an irrevocable operation, however, later materialization of that operation is a different history. That distinction is essential.

The kernel must give conflicting decisions a coherent authoritative ordering. It need not impose a global total order over unrelated, independent operations.

### **The identifier reuse counterexample**

Suppose authority is represented solely by an attachment identifier and executor name.

X is replaced by Y. Later, another execution bearing the name X becomes eligible. An old request from the original X now appears valid again.

This violates non-resurrection.

The model needs a distinction between separate issuances or incarnations of authority wherever reuse would otherwise cause ambiguity. Monotonic generations, unique grants, or equivalent validity relations are possible representations—not mandatory primitives.

## **7. The hardest boundary: unresolved external effects**

This is the most consequential part of the derivation.

Revoking authority to initiate new authoritative changes does not necessarily undo previously authorized actions or prevent externally initiated effects from completing.

An adequate model must distinguish at least:

**Request**

Executor proposes an operation.

**Authoritative decision**

Reject, commit an intent, or establish an obligation.

External-effect boundary

**External acceptance or dispatch**

The operation crosses into another system.

**External occurrence**

The effect happens, fails, or remains pending.

**Authoritative outcome recording**

Evidence is incorporated through a permitted transition.

Conceptual distinctions, not a required five-stage protocol. Some stages may coincide, be absent, or be unobservable.

### **7.1 Distinct histories**

| Circumstances at replacement                       | Required treatment                                                                        |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Request exists but has not committed               | Old authority cannot justify a new commitment after supersession.                         |
| Intent is committed but still cancellable          | Continuation or cancellation follows explicit governing rules.                            |
| An enduring obligation was validly committed       | It may survive replacement independently of X's authority.                                |
| External operation was dispatched; outcome unknown | Preserve uncertainty. Do not assume failure.                                              |
| External effect occurred; response was lost        | Preserve the possibility of success. Do not blindly repeat it.                            |
| Outcome arrives after supersession                 | Evaluate it as evidence concerning the earlier operation, not as renewed authority for X. |

A committed intent must not automatically be interpreted as an unrestricted permission to perform every subsequent action. Its semantics determine which later steps are already authorized and which require new authorization.

### **7.2 Historical outcomes are not stale mutations**

Suppose X initiates an authorized external operation, is superseded, and subsequently receives confirmation that the operation succeeded.

Two inadequate extremes are possible:

- Reject all information associated with X after supersession, losing legitimate historical outcomes.
- Allow X to continue mutating current state because it possesses information about a legitimate earlier operation.

Neither is necessary.

A separately authorized reconciliation transition may incorporate evidence about the earlier operation. X can be a source of information without being a source of current authority.

The provenance and validity of that evidence must be evaluated at an appropriate trusted boundary.

### **7.3 The impossibility result**

Consider two external histories:

| World A                           | World B                                |
| --------------------------------- | -------------------------------------- |
| The external operation succeeded. | The external operation never occurred. |
| Its response was lost.            | No response was produced.              |
| Kernel observes no confirmation.  | Kernel observes no confirmation.       |

The kernel's available evidence may be identical.

If Y repeats the operation, World A may experience a duplicate effect. If Y does not repeat it, World B may leave the intended work undone.

Without additional external guarantees or reliable evidence, no kernel decision can ensure both non-duplication and eventual completion in both worlds.

Possible additional conditions include externally enforced operation identity, reliable outcome queries, transactional participation, cancellation guarantees, and effective fencing at the external resource.

These are assumptions about the environment, not guarantees Kernel-0 can manufacture internally.

### **7.4 Consequence for replacement**

Execution replacement and resolution of outstanding external obligations must be independently expressible.

Y may become eligible to continue work while some conflicting operations remain prohibited pending reconciliation.

If the requirement instead demands that Y immediately obtain unrestricted access to an external resource while X has unresolved effects against that resource, safety cannot generally be guaranteed.

The architecture must allow unresolved obligations to constrain subsequent operations where necessary, without automatically blocking all unrelated work.

## **8. Kernel boundary: what belongs inside and outside**

The correct placement criterion is not whether a function is important, but whether its exclusion would make a required authoritative invariant unenforceable.

| Responsibility                               | Kernel-0 requirement                                |
| -------------------------------------------- | --------------------------------------------------- |
| Authoritative identity and state integrity   | Inside the authoritative boundary                   |
| Authority validity and scope enforcement     | Inside                                              |
| Governed changes to authority                | Inside                                              |
| Conflict resolution at commitment            | Inside                                              |
| Durability and recovery guarantees           | Inside the trusted substrate; mechanism unspecified |
| Enforcement of necessary invariants          | Inside the authoritative boundary                   |
| Work Unit domain semantics                   | Outside                                             |
| Attachment organization and role definitions | Outside                                             |
| Executor selection and scheduling            | Outside                                             |
| Planning and decomposition                   | Outside                                             |
| Review and semantic evaluation               | Outside                                             |
| Issue tracking and progress reporting        | Outside                                             |
| Resource allocation strategy                 | Outside                                             |
| External-effect reconciliation strategy      | Outside, subject to authoritative constraints       |

There is an important subtlety concerning policy.

The kernel does not necessarily need to formulate policy, but it must enforce the authoritative consequences of policy.

For example, an external reviewer can determine whether work should be accepted. The kernel must nevertheless prevent an unauthorized caller from manufacturing the authoritative acceptance decision.

Moving judgment outside the kernel does not mean making integrity voluntary.

## **9. Trust boundary and necessary assumptions**

The architecture is only adequate under an explicit trust and failure model.

| Assumption                                             | Consequence if absent                                           |
| ------------------------------------------------------ | --------------------------------------------------------------- |
| Complete mediation of authoritative mutations          | Executors can bypass kernel enforcement.                        |
| Protected authority determination                      | Executors can fabricate their own permissions.                  |
| Sufficient distinction between authority issuances     | Old authority can accidentally become valid again.              |
| Coherent ordering of conflicting transitions           | Mutation and supersession races become unsafe.                  |
| Reliable recovery within the declared failure model    | Durable continuity cannot be guaranteed.                        |
| Trustworthy external evidence where relied upon        | False observations can become authoritative outcomes.           |
| External enforcement where external safety is promised | Superseded executors may still cause effects beyond the kernel. |

Executor isolation is necessary to the extent that it prevents bypassing required enforcement. A particular isolation technology is not necessary.

Similarly, durability must be defined relative to a failure model. Surviving executor disappearance is not equivalent to surviving complete destruction of all persistent storage.

If expiration is time-dependent, the relevant time source becomes a trusted assumption. If authority depends on a claim that an executor has ceased to exist, the reliability of that claim becomes a trusted assumption.

Neither clocks nor reliable failure detection are demonstrated universal prerequisites.

## **10. Minimal falsifying histories**

The following are abstract model-adequacy checks. They are not implementation tests and have not been executed.

| History                                                               | Required result                                              | Insufficient model falsified         |
| --------------------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------ |
| Create W/P; attach X; lose X; attach Y                                | Same W/P and required continuity state survive               | Execution-owned work                 |
| Replace X; reuse X's retained reference                               | New mutation rejected                                        | Possession-based authority           |
| Commit X mutation; replace X                                          | Mutation remains legitimate history                          | Retroactive invalidation             |
| Validate X; replace X; attempt X commitment                           | Mutation rejected unless already authoritatively committed   | Check-on-entry authorization         |
| Request an indivisible change containing an invalid component         | No unintended partial mutation                               | Non-atomic validation                |
| Replace X; reuse its execution identifier                             | Old issuance remains invalid                                 | Identity-only authorization          |
| Replace X at P₁ while Z operates at P₂                                | Z remains eligible absent a relevant conflict                | Global revocation                    |
| Two attachment positions request incompatible shared-resource changes | Prohibited combination cannot commit                         | Attachment-local conflict checking   |
| External success with lost response vs. non-occurrence                | Both possibilities remain distinguishable from known failure | Missing-response-as-failure model    |
| Receive legitimate historical outcome after replacing X               | Reconciliation possible without restoring X's authority      | Conflation of evidence and authority |

A further negative control is important: the model must not reject every mutation, prohibit all concurrency, or prevent all replacement merely to preserve safety.

Such a model would satisfy many negative safety properties while failing the positive adequacy requirements for usable, continuing work.

## **11. What the requirements do not establish**

A first-principles derivation must resist promoting familiar mechanisms into necessities.

| Not established as mandatory             | Actual requirement                                  |
| ---------------------------------------- | --------------------------------------------------- |
| Capability tokens                        | Enforceable authority validity                      |
| Generation counters                      | Non-resurrection of superseded authority            |
| Append-only event sourcing               | Sufficient historical integrity and recovery        |
| Global consensus or global serialization | Coherent ordering wherever decisions conflict       |
| Leases and heartbeats                    | Governed authority lifetime                         |
| One executor per attachment              | Applicable compatibility constraints                |
| Permanent Work Unit processes            | Durable work continuity                             |
| Dedicated kernel Work Unit objects       | Ability to represent and enforce work relationships |
| Exactly-once external execution          | Explicit handling of external uncertainty           |
| Universal rollback                       | Prevention of unintended authoritative mutations    |
| A particular primitive vocabulary        | Sufficient expressive and enforcement power         |

Even the proposed \\(K=(S,A,H)\\) decomposition is not uniquely necessary. A smaller representation is adequate if it preserves all the required distinctions.

**Semantic minimality is not the same as minimizing the number of data types, state variables, or kernel primitives.**

A small but ambiguous ontology can be less adequate than a larger, precise one. Conversely, several necessary semantic distinctions may be supported by a single general primitive.

## **12. Model adequacy versus realization conformance**

These are separate proof obligations.

**Model adequacy** asks whether the abstract transition system can express the required histories, admit legitimate changes, reject forbidden changes, preserve continuity, and accurately represent uncertainty.

**Realization conformance** asks whether a concrete system actually implements those guarantees under concurrency, interruption, recovery, retained references, unauthorized access, and its declared failure conditions.

A model that defines commitment atomically does not prove that its realization commits atomically.

Likewise, a successful demonstration of executor replacement does not prove that every race involving supersession is safe.

The realization must justify the correspondence between concrete events and abstract authoritative decisions. Neither correctness of the model nor correctness of a few observed histories establishes that correspondence automatically.

## **13. Most consequential remaining uncertainty**

The central unresolved architectural question is:

**Does execution authority govern only new Kernel-0 authoritative commitments, or must it also govern the initiation and completion of effects outside Kernel-0?**

**Internal authority boundary**

Superseded execution cannot commit new authoritative changes.

Kernel can enforce this within its trusted substrate.

**Extended effect boundary**

Superseded execution cannot cause prohibited external effects.

Requires mediation and guarantees beyond internal state.

Neither guarantee automatically implies the other.

This uncertainty is more fundamental than selecting the persistence mechanism, authority representation, primitive vocabulary, or execution topology.

It determines whether unresolved external operations can remain a higher-level reconciliation concern or must participate directly in the authoritative constraints governing replacement and resource reuse.

My derivation assumes complete mediation of internal authoritative changes but makes no assumption of universal external mediation, instantaneous cancellation, or reliable exactly-once behavior.

The supplied packet does not settle the external guarantees or the complete durability failure model. Stronger conclusions would therefore require additional premises.

## **14. Final architectural conclusion**

The smallest defensible Kernel-0 is a substrate capable of enforcing:

1. **Persistent authoritative continuity** independent of temporary execution.
2. **Externally governed, scoped, currently valid authority.**
3. **Atomic, invariant-preserving authoritative transitions.**
4. **Coherent ordering between conflicting mutations and authority changes.**
5. **Non-resurrection of superseded authority.**
6. **Preservation of relevant historical facts and unresolved commitments.**
7. **An explicit boundary between authoritative decisions, external reality, and evidence about that reality.**

Everything else requires an independent justification for inclusion.

The Work Unit architecture can then be constructed as a domain-level organization of persistent work identities, stable participation positions, temporary executions, and governed authority relationships.

The kernel does not need to know what work means. It needs to guarantee that whatever the work means, its authoritative continuity and integrity cannot be compromised merely by the disappearance, persistence, replacement, or concurrency of its executors.

**Execution is replaceable. Authority is conditional. Work is durable. History is preserved. External reality is not assumed.**

Those are the fundamental semantic separations from which the architecture follows.