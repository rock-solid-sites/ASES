# ChatGPT Research Level Classification 

My answer is that the three-level split survives this test extremely well. More importantly, I think the questions collapse into **a surprisingly small number of EDASES-level problems**, with ASES and Execution being progressively more concrete projections of them.

The strongest structure I see is **five fundamental research tracks**, not seventeen separate topics.

## 1. The fundamental EDASES layer

I would put five questions here.

### E1. Authority, Trust, and Evidence

This is the deepest one.

The fundamental question is:

> **In a software-engineering system containing probabilistic agents, what entities are authoritative about what facts, and what evidence is sufficient to change authoritative state?**

This subsumes much of:

* Authority Boundaries;
* Execution Trust;
* Completion Verification;
* Verification Architecture;
* Substrate Self-Repair;
* parts of Integration Authority;
* parts of Model Capability.

The critical distinction is between **claim, evidence, and authority**.

An agent can claim:

> “I fixed the bug.”

That is not the same fact as:

> “The requested change exists.”

which isn't the same as:

> “The change passes the specified verification.”

which isn't the same as:

> “The integrated system remains correct.”

And none of those necessarily means:

> “The authoritative system state may transition to Complete.”

I think this is very close to the actual theoretical center of EDASES.

---

### E2. The Nature of the Agent Participant

The second foundational question is:

> **What changes in software-engineering methodology when a participant is probabilistic, context-limited, non-deterministic, and capable of making plausible but false assertions?**

This is the distributed-systems question.

The important thing isn't simply that LLMs can fail. Traditional distributed systems already deal with crashed, delayed, Byzantine, and unavailable components.

The interesting question is the combination of:

* probabilistic reasoning;
* semantic competence;
* unreliable self-report;
* scope mutation;
* context dependence;
* tool-use failures;
* ability to generate new work;
* ability to reinterpret requirements.

This determines which distributed-systems assumptions survive and which don't.

So I would merge Qwen's “Distributed Systems + Adversarially Unreliable Participants” with the existing distributed-systems/Temporal/Kubernetes/MapReduce research.

The latter is **prior art investigation supporting the former**, rather than a separate fundamental research track.

---

### E3. Durable Work, Execution, and Identity

The fundamental question is:

> **What is the durable thing in agentic software engineering?**

This is the thread running through:

* Gas Town's Work/Molecule/Wisp distinction;
* Celld;
* Crosslink;
* Execution Engine state;
* session/work separation;
* restart survivability;
* RPC/process boundaries;
* durable versus ephemeral execution.

The hypothesis emerging from all of this is something like:

> **The agent session is not the durable unit. The work and its authoritative state are.**

But there are still unanswered questions about exactly what “work” means, what state belongs to it, and where execution identity begins and ends.

This is an EDASES question because choosing the wrong durable abstraction can make the entire methodology incoherent.

The actual database, RPC protocol, event format, Rust process architecture, etc. are Execution questions.

---

### E4. Composition and Collective Correctness

This is the one I think Qwen's response most usefully exposed.

The fundamental question is:

> **How does correctness compose when independently produced pieces of work interact?**

That gives us:

* merge/integration authority;
* stacked diffs;
* Refinery;
* convoy verification;
* scatter/gather;
* reviewer quorums;
* cross-work-item dependencies.

There is a major conceptual distinction:

**local correctness**

> This work item is correct.

versus

**compositional correctness**

> These individually correct work items are correct when combined.

This isn't merely a Git problem. Git happens to be where one manifestation becomes visible.

It is an EDASES research question because it asks something fundamental about how verified work can be composed.

---

### E5. Bounded Agency

I would add one that isn't quite explicit enough in the current inventory:

> **What is the maximum authority and freedom an agent should have while still permitting useful autonomous software engineering?**

This encompasses:

* pathological graph expansion;
* context boundaries;
* scope creep;
* work decomposition;
* agent capability;
* human authority;
* model diversity;
* architectural emergence.

The interesting question isn't “how do we stop agents doing stupid things?”

It's:

> **Where should autonomy terminate and authorization begin?**

That is a foundational EDASES question.

And it explains why your original “non-programmer + trustworthy software” goal matters. You cannot simply tell the user to supervise every action manually. The system has to convert bounded authority into useful autonomy.

---

# 2. ASES is the methodology derived from those questions

Once those five EDASES questions are accepted, most of the apparent complexity becomes ASES methodology.

For example:

### Authority / Trust → ASES

ASES needs:

* explicit authority boundaries;
* evidence contracts;
* completion protocols;
* independent verification;
* reviewer roles;
* integration verification;
* human approval boundaries;
* substrate-repair procedures.

### Agent Nature → ASES

ASES needs:

* work/session separation;
* externalized state;
* bounded retries;
* progress evidence;
* explicit scope;
* protection against self-generated graph expansion;
* independent review;
* appropriate model assignment.

### Durable Work → ASES

ASES needs definitions for:

* Work Item;
* execution identity;
* state;
* artifact;
* dependency;
* evidence;
* event;
* lifecycle.

This is where the Crosslink/Execution boundary becomes a methodological question.

### Composition → ASES

ASES needs:

* change dependencies;
* integration units;
* integration gates;
* collective verification;
* review semantics;
* promotion criteria.

### Bounded Agency → ASES

ASES needs:

* capability policies;
* authorized context;
* work decomposition rules;
* graph mutation rules;
* escalation rules;
* model-selection policy;
* human intervention points.

This is also where **architectural compression** belongs.

I would not make that a separate EDASES research track. I'd make it an ASES methodological principle:

> **Every methodological mechanism must justify its existence against simpler existing primitives and explicit failure modes.**

---

# 3. Execution is where the rules become mechanical

Then the Execution Engine has a remarkably clean job:

> **Make the ASES rules difficult or impossible to violate accidentally.**

So:

| ASES requirement                          | Execution concern                    |
| ----------------------------------------- | ------------------------------------ |
| Work has durable identity                 | Persistent state                     |
| Agent cannot arbitrarily transition state | State machine                        |
| Agent has bounded authority               | Capability enforcement               |
| Completion requires evidence              | Completion gate                      |
| Agent may stall                           | Liveness/progress monitor            |
| Work survives session death               | Durable execution state              |
| Execution survives restart                | Recovery/reconciliation              |
| Changes are isolated                      | Git worktrees                        |
| Integration is controlled                 | Integration queue/gate               |
| Scope is bounded                          | Filesystem/tool/context capabilities |
| Events are attributable                   | Event stream                         |
| Resources are bounded                     | Quotas/admission control             |
| Runtime failure is recoverable            | Restart/recovery protocol            |
| Process boundary is explicit              | RPC/API/process architecture         |

This is why I think the three-layer model is so useful: **Execution should not be deciding what “completion” means.**

ASES defines the completion protocol.

EDASES establishes why the protocol needs to exist.

Execution enforces it.

---

# 4. The questions that should be explicitly decomposed three ways

Several of the current research topics are misleading if treated as single questions.

### “Execution Trust”

This should become:

**EDASES:** What can an AI participant legitimately establish or claim?

**ASES:** What evidence and independent verification are required to accept a claim?

**Execution:** What state transitions mechanically require that evidence?

---

### “Authority Boundaries”

**EDASES:** What kinds of authority must exist, and why should authority be separated?

**ASES:** Which actor gets which authority under which conditions?

**Execution:** How are unauthorized operations mechanically prevented?

---

### “Liveness”

**EDASES:** What is meaningful progress in an agentic system?

**ASES:** What evidence constitutes progress and when should work be considered stalled?

**Execution:** How do we detect stalls, enforce budgets, recover, and escalate?

This distinction is important because “process is alive” is obviously an Execution observation, whereas “progress” is partly methodological and partly conceptual.

---

### “Integration”

**EDASES:** How does correctness compose?

**ASES:** What verification methodology establishes collective correctness?

**Execution:** How are changes queued, tested, merged, rolled back, and promoted?

---

### “Context”

**EDASES:** What information and authority does an autonomous agent fundamentally need to perform useful work?

**ASES:** How should context be scoped, hydrated, and authorized?

**Execution:** How do we enforce filesystem, repository, tool, API, and context capabilities?

---

### “Substrate failure”

**EDASES:** Who can legitimately repair the authority substrate?

**ASES:** What recovery protocol preserves authority when infrastructure fails?

**Execution:** How does the actual runtime detect, isolate, reconstruct, and recover from failure?

This is one of the clearest examples of why collapsing the levels would be dangerous.

---

# 5. What I would merge

I would substantially reduce the current inventory.

### Merge into **Authority / Trust / Evidence**

* Authority Boundary Comparison
* Execution Trust
* Verification and Review Architecture
* Substrate Self-Repair Limits

They aren't identical questions, but they are facets of one deeper problem.

### Merge into **Agent Nature / Distributed Systems**

* Agent Systems as Distributed Systems + Probabilistic Participants
* Temporal / Kubernetes / MapReduce prior art
* Liveness and Progress

The prior-art investigation is evidence for the fundamental question rather than a separate research topic.

### Merge into **Durable Work / Execution Identity**

* Execution/Substrate Restart Survivability
* Crosslink / Work Substrate
* State / Durable Execution Boundary
* RPC / Process Boundary
* Celld-related state research

Again, these are different investigations of the same underlying boundary.

### Merge into **Composition / Collective Correctness**

* Merge / Integration Authority
* stacked diffs / merge queues
* scatter/gather
* integration verification
* reviewer quorum

### Merge into **Bounded Agency**

* Context Hydration vs Injection
* pathological graph expansion
* scope control
* model capability as an authority/reliability control
* human/model architectural authority

The **Skeleton Factory** remains separate because it is a synthesis experiment, not a property of the system itself.

---

# 6. The resulting research map

I would currently draw it like this:

```text
                         EDASES
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     AUTHORITY &      AGENT NATURE     DURABLE WORK
       TRUST              │             & IDENTITY
          │               │                │
          │               │                │
          ├──────── COMPOSITION ───────────┤
          │                                │
          └──────── BOUNDED AGENCY ────────┘
                           │
                           ▼
                         ASES
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   Authority &        Work / State       Verification /
   Evidence           Methodology        Integration
        │                  │                  │
        ├────────── Context / Scope ─────────┤
        │                  │                  │
        └──────── Model / Human Roles ───────┘
                           │
                           ▼
                    EXECUTION ENGINE
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    State Machine      Persistence        Capabilities
        │                  │                  │
    Scheduling         Recovery          Liveness
        │                  │                  │
    Git/Worktrees       Events           RPC
        │                  │                  │
        └──────── Integration Gates ──────────┘
```

And crucially, **the arrows aren't merely organizational**. They represent derivation:

> EDASES establishes the property → ASES specifies the methodology → Execution mechanically enforces it.

---

# 7. What I think is missing

There is one significant question I'd add to the inventory:

> **What does it mean for the system's authoritative representation itself to be correct?**

We've spent a lot of time asking whether agents can be trusted.

But there's a second-order problem:

**Why should we trust the state machine?**

If:

```text
agent → evidence → ASES decision → execution state
```

then we need to know what establishes the correctness of the transition mechanism itself.

This is different from ordinary substrate reliability.

The deeper question is:

> **What is the trusted computing base of an agentic software-engineering system, and how small can it be?**

That immediately connects to the Skeleton Factory.

If the Execution Engine has 200,000 lines of complicated orchestration code, we've potentially just moved the trust problem from “unreliable agents” into “huge unreliable infrastructure.”

That suggests another architectural objective:

> **Minimize the amount of machinery that must itself be trusted.**

This may ultimately be one of the strongest arguments for Rust, deterministic state transitions, capability-based enforcement, and a deliberately small execution core.

---

# 8. Where I expect independent researchers to disagree

The most interesting disagreements won't be over obvious assignments like “Git worktree management is Execution.”

They'll be over **boundary questions**.

The biggest three:

### Is “agent trust” EDASES or ASES?

I think the fundamental question is EDASES, while the trust protocol is ASES.

### Is durable state EDASES or Execution?

I think **what deserves to be durable** is EDASES, **what the methodology requires to be durable** is ASES, and **how it is persisted** is Execution.

### Is model diversity an architectural principle or a methodology?

I currently put the fundamental claim in EDASES:

> correlated model failure is a potential systemic reliability problem.

But the reviewer/quorum design is ASES, and actually selecting/routing models is Execution/tooling.

Those are exactly the sorts of disagreements that will make the independent exercise useful.

---

## My strongest conclusion

I don't think the exercise merely confirms that “everything fits somewhere.”

I think it suggests that **the three-level separation is itself a candidate EDASES result**.

The original motivation may have been organizational:

> research → methodology → implementation.

But after applying it to Gas Town, RCP/RPC, Crosslink, Celld, liveness, execution state, authority, verification, and integration, it looks more like an **abstraction theorem about the problem space**:

> **Agentic software engineering problems repeatedly appear in three forms: a question about what must be true, a question about how humans and agents should operate under that truth, and a question about how machinery can enforce the resulting methodology.**

If independent researchers independently reconstruct something close to that structure, that would be considerably more interesting than agreement over the individual topic labels. It would suggest that EDASES → ASES → Execution isn't just a convenient project decomposition; **it may be the correct conceptual decomposition of the domain.**

And that is exactly the hypothesis I'd want the next round of agents to attack. ϞЖא
