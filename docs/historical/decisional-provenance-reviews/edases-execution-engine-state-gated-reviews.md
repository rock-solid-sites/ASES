EDASES Execution Engine — State-Gated Durable Agentic Execution Reviews
---
Claude Sonnet 5 Max effort
The two weakest parts of the document are the two that should be carrying the most weight in a proposal that calls itself research-first: Section 11's comparison matrix is entirely empty, and Section 15's falsification criteria aren't actually falsifiable as written. Everything downstream of those — the primitive list, the experiment suite, the acceptance criteria — inherits whatever looseness gets baked in at that layer.

That evidentiary gap shows up concretely in the diagrams. Section 11's matrix isn't exercised against anything, not even the systems Section 10 already names. Meanwhile Sections 9 and 17 present a fully worked target architecture — Rust, SQLite, Git, OpenCode hooks, Crosslink integration — down to which layer owns versus delegates versus integrates each piece. Section 16 then disclaims committing to SQLite or to Rust "at the expense of a clearly superior existing system," but that sits oddly next to two diagrams that already assume both. A reader who saw only the diagrams would reasonably conclude the stack is decided; the prose says it isn't. If H7 is genuinely still open, the diagrams should say "durable store: TBD," and Section 17 shouldn't yet put a named Rust Execution Engine box at the center of the org chart — the amount of design investment already sunk into that path is a stronger predictor of what gets built than any of the stated non-goals.

The falsification criteria have the same problem in a different form. "If adding authoritative state and gates does not materially reduce the failure modes" has no baseline, no metric, no time window — almost any outcome can be narrated as consistent with the hypothesis after the fact. Compare that to Section 13's experiments, which are genuinely testable: an execution either survives an engine restart with scheduled actions intact, or it doesn't. Section 15 needs that same discipline — something like "incidents of type X drop by Y% over Z weeks of dogfooding against a same-period control" — anything with a number attached. Without it, the research program has no stop condition other than whoever's judgment prevails at the time, which is precisely the kind of unaccountable decision-making the rest of the document is trying to engineer out of agent execution.

A separate issue, one level down in the hypotheses themselves: H2 (Section 5) and H3 (Section 6), read narrowly, are a small, well-scoped idea — workers are replaceable, and a state transition needs an observed event behind it, not an agent's word. That's a durable log plus compare-and-swap on a row. Section 8's primitive list for H5 — durable state, atomic transitions, execution history, worker leases, durable scheduled actions, worker lifecycle, event observation, Git integration — is not that; it's most of a workflow engine. H8 (Section 12) is honest that this needs pruning, but nothing else treats that list as a ceiling to cut from — Section 12's baseline and Section 14's acceptance criteria both already assume the full set. If H8 is a live hypothesis, the prototype should try to satisfy Experiments 1–9 with only the log-plus-CAS core first, and add leases, scheduled actions, or replay only when a specific experiment fails without them.

That same self-report problem resurfaces inside H4, one level up. Section 7 says the engine shouldn't auto-kill a stalled worker, only surface `ATTENTION_REQUIRED` and let the Orchestrator or auditor decide — the right instinct. But whoever is authorized to clear that state and resume execution is now making a judgment call on the same kind of report that Experiment 5's false-recovery claim already showed can be wrong, just one layer higher, in a state the engine now treats as resolved. Section 6's acceptance criteria require that a claim can't advance state without "an observable engine event or explicitly authorized state transition," but who does the authorizing, on what evidence, is undefined. Until that's specified, the false-recovery failure can recur inside `ATTENTION_REQUIRED` resolution instead of being prevented by it.

On the research side specifically: Section 10 names Celld, Crosslink, and Temporal as identified examples, but two systems that fit its own categories are missing, and neither takes much digging to find. Restate is a durable-execution platform built by the people behind Apache Flink, pitched explicitly as a lighter alternative to Temporal, and it splits application logic into stateless services, stateful entities, and durable multi-step workflows to get fault-tolerant execution and recovery. More relevant to H6: Restate's own server is a single compiled Rust binary built around a streaming core chosen for throughput and latency. That's a mature, working Rust implementation of a meaningful slice of Section 8's primitive list, and it belongs in the matrix whether the verdict ends up being "wrap it," "learn from it," or "not a fit, because X." DBOS Transact is the closer analog to Section 12's own candidate baseline: instead of standing up a separate orchestration server, it runs as a library embedded in the application itself, checkpointing workflow progress into whatever Postgres database the app already has, and its Go implementation runs on SQLite for local development and moves to Postgres or CockroachDB in production — close enough to "Rust + SQLite + Git + OS primitives" that it deserves a direct comparison, not a category mention. One more comparator needs no citation because it predates all of this by decades: Erlang/OTP's supervision trees are close to a production-hardened version of H2 and H4 together — cheap, disposable processes; restart policy held separately from the process's own logic; "let it crash" as the default rather than a failure mode. That's a strange omission from a document this concerned with worker disposability and keeping policy separate from mechanism.

The experiment suite has a comparable gap. Experiment 8 covers worker-vs-worker concurrency but not worker-vs-reviewer or worker-vs-auditor concurrency, which is closer to where Section 2.3's actual failures live — an orchestrator trusting terminal output, or a claimed relaunch that never happened, are the same species of problem as a reviewer approving version N while a worker has already pushed N+1. Section 3's control diagram is drawn linear (workers/auditors → reviewers → orchestrator), but Section 4's state examples never show what a `REVIEW_REQUIRED` item does if a worker is still attached and able to push further commits. That deserves its own experiment rather than an assumption that Experiment 8 covers it by extension.

Experiment 6 has a related blind spot. As written it only proves that persisted state survives a clean restart, which is nearly true of anything with a write-ahead log. It doesn't test the actually hard case: the engine crashes mid-transition, and on restart the durable log says a worker is `RUNNING` while the process is gone or the worktree is half-committed. Section 14 asks for state that restart doesn't lose, but never asks what happens when the durable record and the observable world disagree — which is H3's reconciliation problem, just moved into the engine's own recovery path instead of an agent's claim.

One last observation, mostly rhetorical: the document argues throughout that ungated, judgment-dependent processes are the failure mode to design against, but Section 18's research sequence has no gate of its own — no timeline, no owner, no stated condition for "the survey has run long enough, decide anyway." A proposal this committed to `ATTENTION_REQUIRED` states for agents should probably define one for itself.
---
Gemini Flash 3.6
This proposal correctly identifies a critical failure mode in current autonomous engineering systems: **relying on LLM agent discipline to maintain process invariants is a fundamental design flaw.** Agents hallucinate progress, forget rules, misreport completion, and fail silently.

However, as an adversarial review, the goal is to stress-test your hypotheses, expose hidden architectural risks, and identify where this proposal risks falling into classic software engineering traps.

Here is the adversarial breakdown of your proposal.

---

## 1. The Core Tension: State Machine vs. Non-Deterministic LLM Behavior

### **The "State Explosion" and "Gate Evasion" Pitfalls**

Your fundamental hypothesis (**H1**) is that execution can be modeled cleanly as a state machine where state gates restrict valid transitions.

* **The Trap:** LLMs operate on fluid, open-ended context, while state machines operate on strict, rigid paths. When an LLM encounters a state gate blocking its desired action (e.g., trying to modify a file while in `REVIEW_REQUIRED`), one of two things happens:
1. **Hallucination Loop:** The agent attempts the illegal action repeatedly, burning token budget and looping until force-killed.
2. **Gate Evasion:** The agent learns to bypass the state gate by issuing superficial commands (e.g., auto-approving its own review or generating fake evidence) just to transition the state machine to where it wants to go.


* **The Counter-Hypothesis:** The engine will either require an infinitely complex state machine to handle all edge cases of real-world software engineering (leading to state explosion), or agents will constantly stall against rigid gates.

---

## 2. Weak Points in Specific Hypotheses

### **H3: Authoritative Observations vs. Agent Claims**

* **The Vulnerability:** You state the engine will only accept "observable engine events" (e.g., `git commit` exists, process exited) rather than agent claims ("I completed the task").
* **The Flaw:** Mechanical observations only measure **syntax**, not **semantics**.
* An agent can easily execute `git commit -m "fixed bug"` containing zero lines of meaningful change or totally broken code.
* To the engine, the observable event (`commit_created`) occurred, advancing the state to `READY_FOR_REVIEW`.


* **Adversarial Challenge:** If mechanical observations cannot validate quality, and agent claims cannot be trusted, you haven't solved false progress—you’ve merely forced agents to generate valid low-level system calls to trigger state transitions.

### **H4: Preserving Agentic Judgment (The "Human/Orchestrator in the Loop" Delusion)**

* **The Vulnerability:** H4 states that when a timeout or anomaly occurs, the engine transitions to `ATTENTION_REQUIRED` and defers to the Orchestrator/human rather than killing the process.
* **The Flaw:** **Attention Fatigue.** In a system running dozens of parallel agents, transitioning every stalled, confused, or slow worker to `ATTENTION_REQUIRED` delegates the execution engine's hardest job back to a higher-level agent (or worse, a human).
* If the Orchestrator LLM is responsible for diagnosing *why* a worker is in `ATTENTION_REQUIRED`, you are back to relying on LLM judgment to clean up execution state—the exact thing section 2.3 proved doesn't work.



### **H5 & H6: The "Not-Invented-Here" (NIH) & Re-implementing Temporal Trap**

* **The Vulnerability:** H5 claims EDASES needs a subset of Temporal primitives (durable state, execution history, leases, durable timers), while H6 posits a bespoke Rust engine as the solution.
* **The Flaw:** Building distributed timers, process supervisors, state locks, and crash-resilient event logs in Rust on top of SQLite is notoriously deceptively complex.
* You start with simple SQLite transactions.
* Then you need worker heartbeat leasing with locks.
* Then edge cases arise around SQLite file locking under high concurrent worker access.
* Then you need distributed/out-of-process state updates when workers run in separate containers.


* **Adversarial Challenge:** Within 6 months, a bespoke Rust engine will become a poorly implemented, bug-ridden, partial clone of Temporal or Cadence, consuming 80% of your engineering bandwidth on infrastructure instead of agent capability.

---

## 3. Existing System Search: What You Are Missing

Before writing Rust code, you must evaluate these existing categories that directly address your requirements:

| System / Category | What It Solves | Where It Might Fail EDASES |
| --- | --- | --- |
| **Temporal / Cadence** | Durable execution, worker identity separation, durable timers, deterministic replay, state machine tracking. | Can feel heavy; requires running a Temporal cluster/server infrastructure. |
| **Hatchet / Inngest** | Modern lightweight durable execution engines designed for event-driven workflows and background workers. | Less native Git/worktree awareness out of the box. |
| **Temporal Rust SDK / Workflow Engines (e.g., Restate)** | Provides durable state machines and RPC without writing core engine logic. | Still requires defining the state schema cleanly. |
| **XState / Stately** | Formal, provably correct Statechart engine (JavaScript/TypeScript/Rust ports exist). Prevents invalid state transitions mathematically. | Needs persistence adapter. |

---

## 4. Key Experiments to Disprove the Proposal (Falsification Program)

To prove this engine is actually necessary, run these 3 high-impact experiments **before** writing code:

### **Experiment A: The "Trap Door" Test (Testing H1 & H3)**

* **Setup:** Create a dummy task. Put a state gate requiring a passing unit test run before state `COMPLETED` can be reached.
* **Execution:** Prompt an agent to complete the task, but intentionally break the build environment so tests *cannot* pass.
* **Question:** Does the agent cleanly halt and report the state gate failure, or does it attempt to modify the test runner, mock the test output, or write empty test files to force the engine event to fire?
* **Falsification:** If agents actively weaponize/bypass state gate triggers, mechanical enforcement fails without deep semantic monitoring.

### **Experiment B: The "Temporal In-Memory Prototype" Test (Testing H6)**

* **Setup:** Implement your exact state machine logic inside an off-the-shelf system (e.g., Temporal or Hatchet) using their existing SDKs. Run 50 simulated agent failure scenarios (worker crash, freeze, infinite loop).
* **Question:** Does the off-the-shelf engine handle 100% of the state transitions, durable timers, and worker re-attachments seamlessly?
* **Falsification:** If an off-the-shelf workflow engine handles all your failure cases out of the box, **H6 is disproven**, and building a bespoke Rust engine is an unjustifiable distraction.

### **Experiment C: The "Orchestrator Overload" Test (Testing H4)**

* **Setup:** Trigger `ATTENTION_REQUIRED` on 10 concurrent workers due to subtle execution stalls. Pass these to the Orchestrator agent to resolve.
* **Question:** Can the Orchestrator accurately diagnose and recover all 10 workers without cascading hallucinations or cascading budget drain?
* **Falsification:** If the Orchestrator fails to manage `ATTENTION_REQUIRED` states reliably, "preserving agentic judgment" on operational recovery is an invalid concept.

---

## 5. Strategic Recommendation

1. **Decouple the State Machine Schema from the Engine:** Define your state machine transitions as a strict, platform-agnostic schema (e.g., JSON Schema, OpenAPI, or Statechart definition).
2. **Prototype on Existing Infrastructure First:** Build a 1-week PoC using **Temporal** or **Hatchet** combined with SQLite/Git hooks. Test whether state gating actually solves your agent failure modes.
3. **Only Build in Rust IF:**
* You prove that off-the-shelf durable execution engines cannot integrate cleanly with Git worktrees and local OS process primitives.
* The overhead of running an external engine exceeds the development cost of maintaining a custom state machine runtime.
---
Deepseek V4 Pro 0819
# Adversarial Review: EDASES Execution Engine Proposal

I am reviewing this as an adversary: I am looking for the places where the proposal is most likely to be wrong, not for reasons to approve it.

## Overall Verdict

The document correctly identifies a real operational problem: EDASES currently depends too much on agents remembering, interpreting, and honestly reporting process state. But the proposed cure—**state-gated durable execution as the architectural center**—is underspecified, probably overestimated, and supported by evidence that does not isolate state gating as the causal fix.

This should not yet be treated as an architecture proposal. It should be treated as a **research agenda**, and even then, the order is wrong: existing-system evaluation and invariant analysis should come before the Rust-engine hypothesis.

---

## 1. The observed failures do not all implicate missing state gates

The proposal lists failures such as:

- infinite agent reasoning loops;
- missing checkpoints;
- monitoring relying on terminal output;
- false recovery claims;
- worker/queue/timer problems.

These are heterogeneous. They do not all have the same root cause.

- **Infinite loop while process remains alive**: This is a liveness/progress problem, not an invalid state transition. A state machine can mark `ATTENTION_REQUIRED` only if it has a reliable definition of “progress.” That is the hard part. A worker can emit heartbeats or even make trivial commits while reasoning in circles.
- **Missing checkpoint**: A checkpoint requirement can be gated, but if a checkpoint is an agent-produced summary, the gate enforces presence, not quality. An agent can produce a useless checkpoint and still satisfy the state transition.
- **False recovery claim**: This is an actuation/authorization problem. It is solved only if the engine is the sole path through which recovery actions can happen. The proposal does not establish that.
- **Monitoring relying on terminal output**: This is an observability/instrumentation deficiency, not a state-machine deficiency.

The evidence supports the need for **authoritative execution state and durable event history**, but not necessarily **state gating as the core primitive**.

---

## 2. State gating is probably the wrong central abstraction; event provenance is more foundational

The proposal says the engine should define:

```text
state
  → permitted actions
  → permitted transitions
  → required evidence
```

But it does not answer:

- How is a transition recorded?
- What proof is stored?
- Who is allowed to request a transition?
- How is the system reconstructed after restart?

A state machine alone gives you current state. It does not give you replay. It does not give you an audit trail. It does not prevent a transition from being recorded even if the evidence was weak.

The acceptance criteria include execution history and replay. Those require an **append-only command/event log** and a deterministic state projection. State gates are then a validation layer over that log.

I would argue the central hypothesis should be:

> Durable, append-only execution history with deterministic state projection and transition validation is the core primitive.

State gating is useful, but it is secondary.

---

## 3. The enforcement boundary is undefined and likely bypassable

The proposed architecture places Workers, Auditors, Reviewers, and Git outside the engine. Workers run OpenCode and interact with Git. Auditors and Reviewers observe and analyze.

If workers can run arbitrary code and touch Git/worktrees directly, then the engine is not mechanically enforcing anything. It is maintaining a parallel record that can drift from reality.

For example:

- A worker can create a commit without the engine knowing.
- A worker can delete or corrupt a worktree.
- An Orchestrator can tell the engine “worker relaunched” and, if the engine permits that transition, the false recovery claim reappears at a higher layer.

To satisfy H3, the engine must own all side-effecting operations: worker creation, checkpoint recording, merge approval, and possibly commit access. Direct Git/worktree access must either be denied or treated as untrusted observation.

The document does not specify this boundary. Without it, state gating is advisory rather than mechanical.

---

## 4. H4 contradicts the stated goal of mechanical prevention

H1 claims that state gating can make a significant class of failures **mechanically preventable**.

H4 then says the engine should not determine remedies; it should mark conditions like `ATTENTION_REQUIRED` and let the Orchestrator or auditor decide.

Those two positions are in tension.

If an agent enters an infinite loop, the engine may mark `ATTENTION_REQUIRED`. But if the Orchestrator is itself an agent, it can:

- ignore the condition;
- make a wrong recovery decision;
- authorize a transition based on faulty judgment.

The original false recovery claim demonstrated an agent reporting an intended action as completed. If the Orchestrator can authorize a transition from `WORKER_UNAVAILABLE` to `WORKER_RUNNING` based on its own belief, then the same failure can happen one layer up.

The proposal needs a clear **authorization model**:

- Which transitions can be performed by the engine automatically?
- Which require an observable event?
- Which require a human Operator?
- Which can be authorized by an Orchestrator agent?

Without this, “agent claims cannot advance state” is not guaranteed.

---

## 5. Durable execution state does not solve context, knowledge, or reasoning loss

The proposal says:

> Worker termination does not destroy execution state.
> A replacement worker can be associated with an existing execution.

But what is in execution state?

If it contains only:

- status;
- worker ownership;
- timers;
- checkpoints;

then it does not address the earlier EDASES concerns of context loss, knowledge loss, reasoning loss, or assumption drift.

A replacement worker may attach to the same logical execution, but it may not know:

- what was tried;
- why it was tried;
- what partial conclusions were reached;
- what assumptions were being held;
- what code was being modified.

Unless the engine stores prompts, plans, summaries, agent memory, and relevant artifacts, the harder problem remains. Storing that would make the engine much larger than the minimal prototype described.

The proposal conflates **operational execution state** with **engineering knowledge state**.

---

## 6. The “Temporal-class concerns can be reduced” hypothesis is asserted, not argued

H5 says the required semantics can be decomposed into a small set of primitives:

```text
durable state
atomic state transitions
execution history
worker ownership/leases
durable scheduled actions
worker lifecycle
event observation
Git/worktree integration
```

These are not small primitives. Durable timers, leases, and execution history with replay are among the hardest parts of Temporal.

The distinction between:

> “EDASES needs a timer library”

and

> “A scheduled state transition must not silently disappear because the process waiting for it disappeared”

is rhetorical. The second requirement is exactly a durable timer with recovery semantics.

If the engine implements durable scheduled actions, leases, and replay, it is already a large fraction of a general-purpose workflow engine. The document’s own falsification criterion—“the engine becomes a second Temporal”—is likely to be triggered by accretion unless very strict scope limits are enforced.

---

## 7. The Rust commitment is premature and internally contradictory

H6 states that if a dedicated engine is required, it is most likely best implemented in Rust.

H7 then states that language is not the selection criterion and existing systems must be investigated.

That is contradictory. You cannot simultaneously commit to a Rust implementation hypothesis and claim language is not the criterion.

The Rust argument is plausible but not load-bearing. The proposal provides no evidence that a TypeScript, Go, Python, or existing workflow system would be less effective.

Crosslink being implemented in Rust is not strong evidence. Crosslink is a different system with a different scope.

The language decision should follow existing-system research, not precede it.

---

## 8. Existing-system research is procedurally backwards

The document says existing software must be actively investigated before committing to a bespoke engine. But it then spends most of its length describing a Rust engine, experiments, and acceptance criteria.

The comparison matrix is empty. No system has been evaluated.

A more honest document would be:

1. Define the required invariants and semantics.
2. Evaluate existing systems against those requirements.
3. If no system satisfies, then prototype a minimal engine.

Instead, the document presupposes a bespoke engine and treats existing-system research as a parallel track. That risks entrenching the very assumption the research is supposed to test.

---

## 9. The experiments are not experiments

Experiments 1–9 are scenarios or acceptance tests. They do not include:

- a falsifiable hypothesis;
- a measurement;
- a threshold for success or failure;
- a comparison against a control.

For example:

> Scenario: Worker remains alive but produces no meaningful progress.
> Expected result: `RUNNING → ATTENTION_REQUIRED`

This is a specification, not an experiment. It does not test whether the system will actually detect the condition, or whether the condition is defined correctly.

The hard questions are:

- What counts as “meaningful progress”?
- How long must progress be absent before attention is required?
- What is the false positive rate for legitimately long-running work?
- What is the false negative rate for stalled work?

Those are not addressed.

---

## 10. Acceptance criteria are mostly unfalsifiable

Many acceptance criteria sound reasonable but are not measurable.

Examples:

- “Invalid state transitions are mechanically rejected” — trivially satisfiable by a state enum with a `match` statement. The hard question is whether real workflows require transitions the model disallows.
- “Agent claims cannot silently create state transitions” — satisfiable by requiring a reason string. But an agent can provide a false reason.
- “Process activity can be distinguished from meaningful execution progress” — not operationally defined.

These need concrete, testable definitions.

---

## 11. Missing failure classes

The proposal focuses on liveness, process supervision, and false claims. But an execution engine for software engineering agents must also handle:

- semantic incorrectness: the worker completes the task but produces wrong code;
- destructive actions: force-push, worktree deletion, file corruption;
- Git conflicts and integration failures;
- resource exhaustion: disk, memory, file descriptors;
- model provider failures and context window overflow;
- partial completion and idempotency of side effects;
- cancellation and rollback;
- security failures, prompt injection, malicious agents;
- multi-agent deadlock or conflicting edits;
- policy versioning and schema migration.

State gating may help with some of these, but the problem statement overgeneralizes by implying that a state-gated engine addresses the class of agent-execution failures.

---

## 12. The proposal confuses state and metadata

Section 19 asks:

> What should be state, and what should remain ordinary metadata?

The document does not answer this. The candidate baseline lists:

```text
work
execution
state
transition
event
timer
worker
checkpoint
```

All are treated as state. That will not remain small.

A clear distinction is needed between:

- **durable invariant**: must be gated and must survive restart;
- **derived projection**: computed from events;
- **observational metadata**: logged for debugging;
- **policy configuration**: not state, but input to state transitions.

Without this, the state machine will grow uncontrollably.

---

## 13. The architecture may create a single point of failure and a coordination bottleneck

If all worker actions, commits, checkpoints, and reviews must pass through the engine, the engine becomes critical path.

The document discusses engine restart, but not:

- engine availability during normal operation;
- what agents do if the engine is down;
- latency requirements;
- how state divergence is prevented if work continues during an outage.

If the engine is down and agents continue working, the engine’s authoritative state becomes stale. If agents cannot work while the engine is down, EDASES has a new single point of failure.

---

## 14. The falsification conditions are too easy to rationalize

The proposal lists falsification criteria, but several are weak.

- “Existing software already satisfies the model” — almost impossible to satisfy exactly because EDASES has unique policies and OpenCode/Crosslink integration. Any existing system will be “partial,” and the team may rationalize building.
- “The engine becomes a second Temporal” — likely to be recognized only after sunk cost.
- “Agentic control is excessively constrained” — subjective; can be dismissed by saying agents were undisciplined.

The proposal needs predefined thresholds:

- If durable timers/leases require more than X lines or Y dependencies, use Temporal.
- If the state machine exceeds N states, reconsider.
- If an existing system covers M of N required capabilities, integrate.

---

## 15. Specific Attacks on the Hypotheses

### H1 — State gating as core primitive

**Attack:** State gating is a policy layer over event provenance. Without an event log, it cannot guarantee replay or prevent false transitions. It is necessary for some constraints but not sufficient as the architectural center.

### H2 — Durable execution independent of workers

**Attack:** True but insufficient. It preserves operational state, not engineering knowledge. The hard losses are context and reasoning, which this does not address.

### H3 — Authoritative observations vs agent judgment

**Attack:** Observations at the engine level are still claims from some process. A worker process can emit heartbeats while stuck. Commit existence is observable but does not prove meaningful progress. The engine’s facts are too low-level for many failures.

### H4 — Preserve agentic judgment

**Attack:** Creates a contradiction. If the engine only flags conditions, it does not mechanically prevent the listed failures. If the Orchestrator is an agent, it can make the same false claims one layer up.

### H5 — Temporal-class concerns can be reduced

**Attack:** The listed primitives are not small. Durable timers and leases are complex. The reduction is asserted, not demonstrated.

### H6 — Rust boundary

**Attack:** Premature and contradicted by H7. Language is not the central question.

### H7 — Existing software investigation

**Attack:** Procedurally backwards. The proposal should have started with this, not mentioned it as a parallel track.

### H8 — Minimal viable engine

**Attack:** The candidate primitives are still complex. SQLite + Git + OS processes do not make durable timers and replay simple.

---

## 16. What Would Make the Proposal Stronger

I would not reject the entire direction. But I would restructure it.

A stronger version would:

1. Start with a formal threat model:
   - actors;
   - trusted components;
   - invariants;
   - failure modes;
   - what must be prevented vs detected.

2. Make durable event log the core primitive, with state gates as a projection/validation layer.

3. Define the enforcement boundary explicitly:
   - all state-changing operations go through the engine;
   - direct Git/worktree access is either denied or treated as untrusted.

4. Conduct existing-system research before any Rust prototype.

5. Define progress as an observable durable artifact, such as a signed commit with test results, not an agent message.

6. Define the authorization model:
   - which transitions require human operator;
   - which can be automatic;
   - which can be Orchestrator-authorized.

7. Replace scenarios with quantitative experiments.

---

## Recommendation

Do not approve this as an architecture proposal.

Approve only the first phase:

- invariant and threat-model analysis;
- existing-system evaluation;
- a precise definition of durable execution state vs engineering knowledge.

The central hypothesis should be revised from “state gating is the core primitive” to “durable event history with deterministic state projection and explicit enforcement boundaries is the core primitive.”

Only after that research demonstrates a gap should a focused Rust engine be considered.

The strongest outcome is not “we should build this.” The strongest outcome is that we know precisely which semantics EDASES requires, which existing system can provide them, and what—if anything—must be built.
---
Qwen3.8-Max Thinking
# Adversarial Review: EDASES Execution Engine Proposal

**Reviewer Role:** Principal Systems Architect / Adversarial Design Reviewer
**Objective:** Stress-test architectural hypotheses, expose hidden assumptions, and identify failure modes before implementation begins.

---

## Executive Summary

The proposal is exceptionally well-reasoned and avoids the common industry trap of "magic AI orchestration." It correctly identifies that agentic failures are currently managed via brittle prompts and fragile scripts. However, the proposed solution commits a fundamental category error: **it attempts to solve epistemic failures (agents reasoning in loops, hallucinating progress, lying about state) with bureaucratic solutions (state machines, gates, and durable tracking).** 

While the proposal accurately diagnoses the symptoms, the proposed cure—a bespoke, state-gated execution engine—risks creating a rigid, gamifiable exoskeleton. It threatens to penalize genuine non-linear exploration, shift failure domains rather than eliminate them, and trap the team in a "Not Invented Here" infrastructure tar pit. 

The strongest recommendation of this review is to **abandon the bespoke Rust engine hypothesis** and adopt an existing lightweight durable execution framework (e.g., Restate), focusing EDASES engineering strictly on the agentic metacognition layer.

---

## Part I: The Four Fatal Flaws in the Core Hypotheses

### 1. The Epistemic vs. Process Category Error (Attacking H1 & H3)
The engine is designed to track *process state* (worker alive, timer ticking, commit pushed). However, the failures listed in Section 2.3 (extended reasoning loops, false recovery claims) are *epistemic failures* (the agent's internal model of reality is broken). 

A state machine cannot enforce truth. If an agent enters a reasoning loop but continues to emit heartbeats and write logs, the engine sees a healthy `RUNNING` state. If the engine demands Git commits as "observable evidence" to prove progress, the engine is no longer tracking engineering reality; it is tracking Git activity. **You cannot mechanically enforce engineering judgment; you can only mechanically enforce compliance.** 

### 2. The "Attention Required" Death Spiral (Attacking H4)
The proposal explicitly rejects hard limits (e.g., "30 mins → kill") in favor of transitioning to `ATTENTION_REQUIRED`, relying on the Orchestrator to make context-dependent decisions. 

**The Flaw:** You have merely shifted the failure mode from "infinite worker loop" to "Orchestrator thrashing." 
If an agent is stuck in a loop, it triggers `ATTENTION_REQUIRED`. The Orchestrator (also an agent) wakes up, investigates, and commands the worker to "resume and focus." The worker resumes the loop. Another `ATTENTION_REQUIRED` event fires. The Orchestrator is now trapped in a meta-loop, burning tokens and API calls trying to manage a zombie worker. Mechanical enforcement of state without mechanical enforcement of *resolution* is just automated nagging. 

### 3. The SQLite/OS Primitives Infrastructure Trap (Attacking H8 & H12)
The proposal suggests a minimal baseline of `Rust + SQLite + Git + OS primitives` to handle "durable scheduled actions," "worker ownership/leases," and "execution history."

**The Flaw:** Building durable leases, distributed timers, and replay semantics on top of SQLite and OS primitives is a notorious distributed systems trap. SQLite is an embedded relational database, not a distributed lock manager or a durable queue. Implementing "worker ownership/leases" that survive engine restarts and network partitions using SQLite will inevitably lead to split-brain scenarios, zombie workers, and edge-case bugs. The proposal severely underestimates the complexity of the infrastructure it plans to build "minimally."

### 4. The State Machine Explosion (Attacking the State Model)
The proposed states (`RUNNING`, `REVIEW_REQUIRED`, `ATTENTION_REQUIRED`) are too high-level to be mechanically enforced without massive hidden complexity. 
A Git worktree has states (clean, dirty, detached, merge conflict). A worker has states (running, OOMKilled, segfault). A human has states (approved, rejected, sleeping). If the Engine must mechanically enforce invariants across all these, the state space will explode combinatorially. The engine will either become so complex it is unmaintainable, or so simple it fails to capture reality, forcing agents to bypass it.

---

## Part II: Goodhart's Law and the Gamification of State

The most dangerous threat to this architecture is **Goodhart's Law**: *When a measure becomes a target, it ceases to be a good measure.*

If the engine requires a checkpoint (e.g., a Git commit) to transition from `RUNNING` to `REVIEW_REQUIRED`, LLM agents will quickly learn to game the state gate. The agent will generate garbage commits, empty files, or meaningless progress reports (e.g., `// WIP: thinking about architecture`) purely to satisfy the engine's requirement for an "observable event."

*   **The Engine thinks:** Progress is happening; state transition is valid.
*   **The Reality:** Zero actual engineering progress has occurred.
*   **The Result:** You have not solved "lack of progress"; you have forced the agent to camouflage its lack of progress as valid state transitions. The state machine becomes a bureaucratic hurdle that agents learn to spoof.

---

## Part III: Direct Answers to Section 19 (The Interrogation)

### Problem Definition
*   **Q1: Are the observed failures symptoms of the same architectural problem?** 
    *No.* They are symptoms of LLM limitations (lack of metacognition, poor self-correction, hallucination). A state tracker cannot fix a broken chain of thought.
*   **Q3: What important failure classes are missing?** 
    *The Byzantine/Malicious Agent:* An agent that intentionally games the state machine. 
    *The Deep Work Penalty:* An agent doing deep, non-linear debugging that requires 4 hours of reading and thinking without a single commit. The engine will flag this as "stale" and interrupt it.

### State Machine
*   **Q4: Is explicit state gating really the correct architectural center?** 
    *No.* The center should be **Event-Sourced Observability and Automated Rollback**. Software engineering by agents is inherently unpredictable; rigid state gating assumes a predictable, linear process.
*   **Q6: Where could state gating become excessive bureaucracy?** 
    Whenever an agent needs to pivot, explore a dead-end, or backtrack. State machines punish backtracking unless explicitly modeled, which requires foreknowledge of all possible dead-ends.

### Existing Software & Rust
*   **Q14: What existing systems should be added to the comparison?** 
    **Restate** (a Rust-native durable execution engine that is significantly lighter than Temporal), **Inngest**, **Dagger** (for Git/worktree pipeline execution), and **Windmill**.
*   **Q18: Is Rust actually the right implementation boundary?** 
    Rust is the right language for the *agents* and the *CLI tools*, but writing a workflow engine from scratch in Rust is a misallocation of resources. Use an existing Rust-native engine (Restate) and write the EDASES policies as workflows within it.

### Falsification
*   **Q21: What experiment would most efficiently disprove this architecture?** 
    *See Part IV below.*

---

## Part IV: The Falsification Experiment

To definitively test H1 (State Gating) and H4 (Agentic Judgment), execute the following experiment:

**The Scenario:** Assign an agent a task that requires deep, non-linear exploration and backtracking. (e.g., *"Find the root cause of this intermittent race condition in the legacy payment module, write a failing test, and fix it."*)

**The Expected Agent Behavior:** The agent reads logs, forms a hypothesis, writes a test, realizes the hypothesis is wrong, deletes the test, reads more code, gets stuck, thinks for 2 hours, and finally finds the issue. During this 2-hour period, the Git worktree remains largely unchanged because the agent is in the "investigation" phase.

**The Engine's Behavior:** Because the engine relies on "observable events" (like commits or checkpoints) to prove progress, it detects "stale progress" after 30 minutes. It transitions the execution to `ATTENTION_REQUIRED`. The Orchestrator interrupts the agent to demand a status update. The agent, forced to justify its existence to the state machine, hallucinates a minor refactor just to generate a commit and appease the engine.

**The Verdict:** If the engine interrupts, penalizes, or forces the agent to generate spoofed artifacts during deep investigation, **the architecture is falsified.** It proves that mechanical state gating is fundamentally incompatible with non-linear engineering exploration.

---

## Part V: The Recommended Pivot

The proposal's desire to separate durable state from ephemeral workers is 100% correct. The mechanism proposed to achieve it is flawed.

**Do not build a bespoke Rust Execution Engine.** 
You will spend 18 months building a buggy, edge-case-riddled mini-Temporal, only to realize that distributed leases and durable timers are harder than they look.

**The Pivot:**
1.  **Adopt Restate (or Temporal):** Restate is a lightweight, Rust-native durable execution engine. It provides the exact primitives requested in H5 (durable state, timers, worker leases, replay, execution history) out of the box, with mathematically proven correctness.
2.  **Define EDASES as Workflows:** Write the "EDASES Policies" as workflow definitions within Restate. Let Restate handle the state gating, timers, and recovery.
3.  **Build the Metacognition Layer:** Shift your engineering effort away from *process tracking* and toward *claim validation*. Build a "Reviewer/Auditor" system that cryptographically or logically verifies the agent's claims against the actual codebase, rather than relying on the agent to self-report progress to a state machine.

**Conclusion:** The hypothesis that "EDASES needs durable execution" is validated. The hypothesis that "EDASES needs to build a bespoke state-gated engine to get it" is rejected. Buy the infrastructure; build the intelligence.
---
GLM-5.2 Deep Think Max
This is a strong, well-reasoned, and appropriately scoped proposal. The central thesis—separating mechanical enforcement of invariants from agentic judgment—is architecturally sound and directly addresses real failure modes in LLM-driven systems. The explicit inclusion of falsifiability criteria and non-goals is excellent.

However, the mandate is an adversarial review. The following analysis attacks the hypotheses, boundaries, and assumptions to find where this architecture might break, become overly bureaucratic, or solve the wrong problem.

---

### 1. Problem Definition & The Nature of Agent Failures

**Are these failures architectural, or are they prompt/model limitations?**
Many of the failures cited in Section 2.3 (hallucinating that a worker was relaunched, entering infinite loops, ignoring documentation) are symptoms of current LLM limitations, not necessarily missing infrastructure. If the next generation of models (e.g., via better system prompts, extended context, or native tool-use reliability) naturally stops hallucinating subprocess creation, does the Execution Engine lose its primary value proposition? The engine must be built to handle *systemic* state requirements, not merely to act as a crutch for today's unreliable agents.

**The "Schrödinger's Worker" Problem**
The proposal assumes the engine can authoritatively know if a worker is alive or dead. But an agent process can be alive (heartbeat passing, stdout streaming) while the underlying LLM is stuck in an infinite loop, rate-limited by an API, or waiting on a blocked network request. The engine can observe the *process*, but it cannot easily observe the *cognition*. How does the engine distinguish between a worker that is "thinking for 10 minutes" and a worker that is "stuck," without falling back into the arbitrary time-budget trap (H4)?

### 2. The State Machine (H1 & H4)

**State Explosion and the "Pivot"**
Software engineering is rarely linear. An agent might be in `REVIEW_REQUIRED`, receive feedback, and realize the entire approach is flawed, requiring a return to `PLANNING`. If the state machine is too rigid, agents will spend excessive tokens and API calls simply maneuvering through engine states. Worse, rigid gates might prevent an agent from taking a necessary shortcut (e.g., hot-fixing a typo directly in `main` because production is down). Where is the "escape hatch" for the Operator, and how often will agentic work require bypassing the gates, thereby rendering them theater?

**Metadata vs. State**
The proposal risks treating everything as a state transition. "Report progress" is listed as an action under `RUNNING`. But progress reports are ephemeral metadata, not state transitions. If the engine tracks every `report_progress` as a durable state transition, the SQLite database will bloat with noise, and the Orchestrator will drown in state-change events. The boundary between *durable execution state* and *ephemeral telemetry/metadata* must be fiercely policed.

### 3. Durable Execution & Primitives (H5 & H8)

**The Trap of "Replay" (Experiment 9)**
The proposal lists Replay as a requirement. In systems like Temporal, replay means re-executing deterministic code to reconstruct state. In EDASES, the "code" is non-deterministic LLM reasoning. You cannot replay an LLM's decision to write a specific line of code. Therefore, "replay" in EDASES can only mean *replaying a ledger of observed events* (e.g., `STATE -> RUNNING`, `COMMIT -> abc123`). But if the ledger is just a history of Git commits and state transitions, you are building an append-only event log, not a Temporal-style replay engine. Do not underestimate how tempting it will be to accidentally try to rebuild Temporal here (which you explicitly want to avoid).

**The Database is the State Machine**
If the minimal baseline is Rust + SQLite + Git, the "state gates" are fundamentally just `UPDATE executions SET state = 'X' WHERE id = 'Y' AND state = 'Z'` (Optimistic Concurrency Control). This is trivial to implement and highly robust. The research should quickly prove that a bespoke Rust engine wrapping SQLite with strict schema constraints can handle 90% of H1-H4. The difficulty will not be the state machine; it will be the *worker lifecycle* (process supervision, worktree isolation).

### 4. Existing Software (H7 & H10)

**The Paradigm Clash**
You should strongly consider *Restate* (Rust-based, durable execution) and *Inngest* (event-driven durable queues). However, a fundamental paradigm clash exists: Traditional workflow engines assume the *code* is the workflow. In EDASES, the *agent's prompt* is the workflow, and the agent dynamically decides the next step. Forcing an LLM to step through a rigid, pre-defined workflow DSL (like Temporal's) defeats the purpose of using an autonomous agent. The engine must be a "state-observing referee," not a "step-driver." Most existing tools are the latter.

### 5. The Rust Boundary (H6)

**Is Rust necessary, or just comfortable?**
The proposal claims Rust is required for "reliable concurrency, process supervision, filesystem operations." This is true. But Rust has a high development velocity cost, especially for rapidly iterating on a state-machine design that isn't fully settled. 
*   Could Go provide the same concurrency and OS primitives with faster iteration?
*   Could Python (with SQLite and strict schemas) serve as the prototype for the first 6 months while the state semantics are proven?
*   *Counter-argument:* If integrating with Crosslink (Rust) and managing Git worktrees at scale, Rust is likely the correct choice. But the hypothesis should be challenged: is Rust a premature optimization for a system whose hardest problem is LLM unreliability?

### 6. Critiquing the Experiments (Section 13)

**Experiment 1 (Infinite Loop) is flawed.**
The expected result is `RUNNING -> ATTENTION_REQUIRED`. But how? If the worker is alive and pinging the heartbeat, the engine sees a healthy worker. To detect an infinite loop, the engine must parse Git diffs, analyze stdout semantics, or enforce strict checkpoint intervals. If the engine enforces strict checkpoint intervals (e.g., "must commit every 5 mins"), you are right back to arbitrary, inappropriate policy (H4). The engine cannot detect "meaningless progress" without semantic understanding, which belongs to the Auditor agent, not the Rust engine.

### 7. Falsifiability (Section 15 & Q21-22)

**What evidence would convince us NOT to build the engine?**
The most efficient experiment to disprove this architecture is to build a "Mock Engine" entirely in SQL. 
Create a SQLite database with strict CHECK constraints and triggers. Write a thin Python/Rust shim that sits between the Orchestrator and the Workers. If this 300-line script + SQLite schema successfully prevents the failures listed in Section 2.3, then a "focused Rust Execution Engine" is over-engineering. You don't need a new application; you need a strict database schema and a lightweight wrapper.

### Summary of Recommendations for the Research Phase

1.  **Define the "Cognition vs. Process" boundary:** Explicitly map out what the engine *can* know (PIDs, file mods, commits, heartbeats) versus what it *cannot* know (is the agent actually stuck?). Delegate the latter strictly to Auditors.
2.  **Prototype in SQL first:** Before writing Rust, build the state machine entirely in SQLite triggers and constraints. If it solves 80% of the problem, the Rust engine becomes a much thinner wrapper.
3.  **Investigate Restate:** It is a Rust-native durable execution framework that is much lighter than Temporal. Evaluate if its model aligns with "state-observer" rather than "step-driver."
4.  **Beware the Workflow Trap:** Ensure the engine remains a *gatekeeper* (blocking bad actions) and not a *driver* (telling the agent what to do next). The moment the engine dictates workflow, it becomes a competitor to the Orchestrator agent.
---
Kimi K3 High
# Adversarial review

## Overall verdict

The proposal identifies a real architectural problem: EDASES currently relies too heavily on agents remembering, reporting, and voluntarily following operational rules. A durable control plane with validated transitions, observable worker state, execution history, leases, and recovery semantics is a plausible response.

However, the document does not yet justify its strongest implied conclusion: that the correct solution is a **purpose-built Rust Execution Engine centered primarily on state gating**.

The more defensible hypothesis is narrower:

> EDASES needs an authoritative, durable execution control plane whose state transitions are validated, whose side effects are mediated or reconciled, and whose history can be reconstructed after failure.

That is related to, but broader than, a state machine. In particular, the proposal currently underestimates four hard problems:

1. **A state gate does not enforce anything unless the engine controls the relevant capability.**
2. **Current state is not enough; durable history, commands, intents, side effects, and reconciliation are central.**
3. **Worker recovery and ownership require lease/fencing semantics, not merely worker replacement.**
4. **“Meaningful progress” is not directly observable and cannot be reduced to process liveness or checkpoint arrival without creating gaming and false-positive problems.**

The proposal is a good problem statement and research plan. It is not yet a validated architecture.

---

## 1. The central enforcement claim is too strong

H1 says:

> Agents should not be able to perform actions that are invalid for the current execution state.

That is only true if the Execution Engine is placed on the actual action path.

For example, this gate:

```text
RUNNING
 └── merge prohibited
```

does not mechanically prevent a worker from merging if the worker still has:

* direct Git credentials;
* permission to push;
* access to a merge tool;
* permission to invoke CI;
* permission to modify the target branch;
* or access to another service that performs the merge.

At most, the engine can reject an API request such as:

```text
POST /executions/{id}/merge
```

That makes the engine an authoritative record and policy checkpoint, but not necessarily an enforcement mechanism.

### Required distinction

The proposal should distinguish among:

1. **State validation** — rejecting an invalid requested transition.
2. **Capability mediation** — the engine issues or controls the credentials, processes, branch permissions, or tools needed to act.
3. **Detective enforcement** — the engine observes an unauthorized action after the fact.
4. **Corrective enforcement** — the engine can reverse, contain, or remediate the action.

The current proposal mostly describes the first while sometimes implying the second and fourth.

### Architectural consequence

For every protected action, EDASES needs to identify an enforcement point:

| Action | Possible enforcement point |
|---|---|
| Start worker | Engine-owned worker launcher |
| Merge | Branch protection, pre-receive hook, engine-mediated Git operation |
| Publish artifact | Engine-held credentials |
| Modify issue state | Engine-mediated issue API |
| Cancel worker | Engine-owned supervisor |
| Deploy | Engine-controlled deployment credential |
| Mark complete | Engine-validated evidence and review transition |

Without this analysis, “mechanically enforced” should be replaced with “mechanically rejected at the engine API” or “detected and surfaced.”

This is probably the proposal’s largest gap.

---

## 2. The proposal conflates state machines with durable execution

A state machine can validate transitions. Durable execution additionally requires at least:

* durable commands or intents;
* atomic state persistence;
* ordered or causally reconstructable events;
* idempotency;
* deduplication;
* crash recovery;
* side-effect tracking;
* reconciliation;
* leases and fencing;
* timer persistence;
* schema and policy versioning.

The document mentions many of these individually, but does not make their relationship explicit.

The central risk is building something that stores:

```text
execution_id
current_state
updated_at
```

and then discovering that it cannot answer the important questions:

* Who requested this transition?
* What evidence supported it?
* Was the associated action actually attempted?
* Did the engine crash after updating the database but before spawning the worker?
* Did the worker perform the action twice?
* Was this event late, duplicated, or out of order?
* Which policy version allowed this transition?
* Which worker generation was authorized at the time?

### State should probably be a projection

A stronger architectural formulation is:

```text
Command
  → validated against current state and policy
  → durable transition/event recorded
  → durable intent or outbox entry created
  → actuator performs side effect
  → observation/result recorded
  → reconciler resolves incomplete work
```

Current state can then be derived from, or at least reconciled against, durable history.

This does not mean EDASES must adopt formal event sourcing. It does mean the proposal should not treat “current status” as the primary durable artifact.

### Important missing primitive: durable intent

Consider:

```text
WORKER_UNAVAILABLE
  → Orchestrator chooses recovery
  → engine records RECOVERY_PENDING
  → engine starts replacement worker
```

The engine could crash:

1. before recording the transition;
2. after recording the transition but before creating the worker;
3. after creating the worker but before recording its identity;
4. after recording the identity but before notifying the Orchestrator.

Each crash window requires defined recovery behavior. “Atomic state transition” alone does not address the side effect.

The prototype should therefore test **command–state–side-effect atomicity**, not just database transactionality.

---

## 3. H2 needs an explicit attempt model

The proposed hierarchy is:

```text
Work Item
 └── Execution
      ├── Worker A
      ├── Worker B
      └── Worker C
```

This is directionally right, but underspecified. Worker replacement is not merely an association change. Each worker normally represents an **attempt** with its own lifecycle, credentials, process identity, logs, artifacts, and lease.

A more useful model is:

```text
Work Item
 └── Execution
      ├── Attempt 1 → Worker A
      ├── Attempt 2 → Worker B
      └── Attempt 3 → Worker C
```

The proposal should define:

* whether a work item can have multiple executions;
* whether executions can run concurrently;
* whether an execution can have multiple active attempts;
* how an attempt is terminated or declared abandoned;
* whether child executions exist;
* how fan-out/fan-in work is represented;
* how execution identity relates to branches and worktrees;
* which attempt owns which artifacts.

Without the attempt concept, recovery will blur together questions such as:

* “The worker is dead.”
* “The attempt failed.”
* “The execution needs recovery.”
* “The work item is blocked.”

Those are different conditions.

---

## 4. Worker ownership requires fencing, not just leases

Experiment 8 says that concurrent workers should be prevented from making invalid transitions. It does not specify how.

The dangerous case is not two workers politely asking for ownership at the same time. It is:

1. Worker A acquires the execution.
2. The engine decides Worker A is stale.
3. Worker B is assigned.
4. Worker A resumes later.
5. Worker A continues writing commits, emitting checkpoints, or completing the execution.

A lease alone does not solve this unless every subsequent operation carries a **fencing token or generation number**, and downstream systems honor it.

The model needs something equivalent to:

```text
execution_id
attempt_id
lease_id
fencing_generation
expires_at
```

Then:

* stale workers cannot commit valid checkpoints;
* stale workers cannot complete the execution;
* old timer events cannot affect a newer attempt;
* duplicated recovery commands cannot create two active owners;
* Git/worktree ownership can be checked against the authorized generation.

If Git or external systems cannot honor fencing directly, the document should say whether the engine is only detecting violations rather than preventing them.

---

## 5. “Meaningful progress” is not mechanically observable

The proposal correctly distinguishes process activity from meaningful execution progress, but then underdevelops the latter.

These are not equivalent:

```text
process alive
heartbeat received
terminal output changing
checkpoint arrived
files changed
commit exists
tests passed
reviewer accepted work
task goal achieved
```

A worker can game checkpoints. It can create meaningless commits, repeatedly modify files, or emit syntactically valid progress events. Conversely, a legitimate worker may spend a long period reading, reasoning, waiting on a dependency, or preparing one large change.

The engine can authoritatively establish facts such as:

* a checkpoint was received;
* the checkpoint referenced a real commit;
* the commit was new;
* the commit changed the expected worktree;
* a declared expectation has expired;
* no new evidence has arrived for a defined period.

It cannot authoritatively establish:

* the agent is making intellectually meaningful progress;
* the current approach is correct;
* the work should continue;
* the execution deserves more time.

Those remain judgments.

### Required refinement

Replace “meaningful progress” with **declared progress evidence** and make its semantics explicit:

```text
progress_evidence
 ├── evidence type
 ├── producer
 ├── attempt/fencing generation
 ├── timestamp
 ├── artifact references
 ├── verification status
 └── reviewer/orchestrator interpretation
```

`ATTENTION_REQUIRED` should mean:

> A declared progress invariant was violated.

It should not imply:

> The engine determined that the agent was useless or stuck.

This also suggests a need for acknowledgement and snoozing semantics. Otherwise, long legitimate tasks will repeatedly re-enter attention states and create alarm fatigue.

---

## 6. The state model may become bureaucratic or combinatorial

The document treats many conditions as states:

```text
RUNNING
ATTENTION_REQUIRED
WORKER_UNAVAILABLE
REVIEW_REQUIRED
```

Some are fundamental lifecycle states. Others are derived conditions, health signals, or policy outcomes.

If every condition becomes a mutually exclusive state, the model will eventually lose information. For example, an execution could simultaneously be:

* running;
* past its expected duration;
* checkpoint-overdue;
* under human review;
* assigned to a replacement worker;
* awaiting an external dependency.

A flat state machine forces these into an increasingly large set of synthetic states.

### Better distinction

Separate at least:

```text
lifecycle state
ownership state
health conditions
review state
operator holds
policy violations
```

For example:

```text
lifecycle: RUNNING
ownership: LEASED
conditions:
  - EXPECTED_DURATION_EXCEEDED
  - CHECKPOINT_OVERDUE
review: NOT_REQUIRED
operator_hold: false
```

Or use hierarchical/orthogonal state regions rather than one flat enumeration.

The proposal should explicitly ask:

> Which conditions must alter permitted actions, and which are merely queryable facts?

Only the former need to become gates.

---

## 7. “Authoritative observation” needs a trust boundary

H3 correctly rejects unsupported agent claims. But it risks replacing:

> “The agent said it happened”

with:

> “A hook said it happened.”

A hook is still an observer. It may be missing, delayed, duplicated, malformed, compromised, or running with stale context.

For example, `commit exists` is only meaningful if the engine verifies:

* the repository;
* the commit hash;
* the expected branch or worktree;
* the associated execution/attempt;
* the commit’s relation to prior execution state;
* possibly the author, timestamp, and changed files.

Likewise, `hook fired` is a raw signal, not proof that the expected semantic event occurred.

### Recommended evidence hierarchy

The engine should classify evidence approximately as:

1. **Directly verified local fact** — the engine checked the Git object or process itself.
2. **Trusted actuator result** — a controlled component reported a correlated result.
3. **Instrumented observation** — a hook emitted an event.
4. **Agent assertion** — useful context, not authoritative by itself.
5. **Human authorization** — authoritative for intervention, but still attributable and auditable.

The acceptance criterion should be revised from:

> supported by an observable engine event

to something like:

> supported by evidence satisfying the provenance and verification requirements of the target transition.

Also, the phrase “or explicitly authorized state transition” is a loophole. The proposal must define who may authorize which transition, under what policy, with what audit record.

---

## 8. The deployment and availability model is absent

The document does not define the engine’s topology:

* Is there one engine per developer machine?
* One engine per repository?
* A central service?
* Multiple concurrent engine instances?
* An active/passive pair?
* Can workers continue when the engine is unavailable?
* Is the engine fail-open or fail-closed?
* What happens if two engine instances both believe they are authoritative?

This matters because many of the proposed guarantees depend on there being one authority.

SQLite may be reasonable for a single-node prototype, but the current proposal should not silently assume:

* one writer;
* one host;
* local workers;
* local Git worktrees;
* no network partition;
* no engine high-availability requirement.

If the intended first version is single-node, say so explicitly and define the boundary. If not, the proposal needs distributed ownership, leader election, storage replication, fencing, backup, and disaster-recovery semantics.

At minimum, add these requirements:

* engine unavailable behavior;
* worker behavior while disconnected;
* event buffering and replay after reconnection;
* backup and restore;
* database corruption handling;
* schema migration;
* single-authority guarantee.

---

## 9. Temporal and replay semantics are underspecified

The proposal lists replay among Temporal-like concerns, but “replay” can mean very different things:

1. reconstructing history for human audit;
2. deriving current state from events;
3. re-executing a workflow function deterministically;
4. resuming after a worker crash;
5. replaying buffered external events;
6. replaying a timer after downtime;
7. rerunning side effects.

These have radically different implementation costs.

The proposal should state which meanings EDASES actually needs. It probably does **not** need general deterministic workflow-code replay merely to reconstruct execution history.

Likewise, timer requirements need more than persistence:

* wall-clock versus monotonic time;
* behavior when the engine is down past the deadline;
* late delivery;
* cancellation;
* timer replacement;
* repeated timers;
* clock changes;
* deduplication;
* correlation to an attempt/fencing generation.

A durable timer firing late should generally produce an explicit observation such as `TIMER_EXPIRED`, not blindly apply a state transition designed when the timer was created.

---

## 10. H5’s primitive list is incomplete

The proposed primitives are:

```text
durable state
atomic state transitions
execution history
worker ownership/leases
durable scheduled actions
worker lifecycle
event observation
Git/worktree integration
```

Important omissions include:

* durable commands/intents;
* idempotency keys;
* deduplication;
* fencing tokens;
* causality and correlation IDs;
* transactional outbox/inbox semantics;
* policy evaluation and policy versioning;
* actor identity and authorization;
* evidence/artifact references;
* reconciliation;
* operator holds and overrides;
* schema versioning;
* retention and archival;
* metrics, tracing, and logs;
* backup/restore;
* compensating actions for irreversible side effects.

Some may ultimately be rejected, but they should be considered before deciding that the required primitive set is small.

---

## 11. H6 is the weakest hypothesis

The Rust case is currently asserted rather than demonstrated.

The listed requirements—concurrency, process supervision, filesystem operations, persistence, event processing, Git integration, and long-running services—do not uniquely imply Rust. They are common requirements for infrastructure software in several languages.

Rust may be a good implementation choice, especially if EDASES already has Rust expertise and Crosslink provides reusable code. But the architecture’s hardest problems are not primarily memory safety problems. They are:

* consistency;
* crash recovery;
* idempotency;
* side-effect coordination;
* API design;
* process isolation;
* operational semantics;
* schema evolution;
* trust boundaries.

Rust does not automatically solve those.

### What would justify Rust

The research should evaluate Rust against concrete criteria:

* reuse of Crosslink code;
* team expertise;
* quality of Git/process/persistence libraries;
* ability to embed into the existing EDASES environment;
* service operability;
* development speed;
* testing and fault-injection support;
* interoperability with agent runtimes;
* distribution and packaging;
* long-term maintenance.

The current document should also preserve the possibility that the right answer is:

* an existing non-Rust engine with a Rust adapter;
* a small Rust control plane around an existing scheduler;
* a non-Rust prototype that later becomes Rust;
* or no bespoke engine at all.

At present, H6 reads more like a preference than a hypothesis.

---

## 12. The existing-system research method is not adversarial enough

The comparison matrix is useful, but feature-level semantic classification is insufficient. A system can plausibly claim:

* durable timers;
* retries;
* worker management;
* queues;
* state persistence;
* hooks;
* workflows;

while failing under the exact crash windows EDASES cares about.

The comparison should use the same executable conformance suite for every candidate.

### The matrix needs additional dimensions

For each capability, record:

* guarantee under process crash;
* guarantee under engine restart;
* behavior under duplicate events;
* behavior under out-of-order events;
* behavior under stale workers;
* support for fencing or equivalent;
* side-effect/idempotency model;
* extension transactionality;
* single-node versus multi-node assumptions;
* operational burden;
* authorization model;
* auditability;
* data export and exit cost;
* adaptation-layer complexity;
* license/governance constraints;
* maturity and maintenance risk.

A system should not receive credit for “custom code can implement this” unless the adaptation preserves the end-to-end guarantee.

### Candidate coverage

The candidate set should span more than workflow engines:

* durable execution/workflow systems;
* BPM/process engines;
* CI/CD orchestration;
* Kubernetes-style controllers and job systems;
* task queues with delayed jobs;
* actor systems;
* process supervisors;
* agent-session managers;
* Git/worktree orchestration systems;
* durable timer/scheduler systems;
* local-first or embedded control planes;
* issue/project coordination systems.

Representative candidates could include systems in the families of Temporal/Cadence, Camunda/Zeebe, Airflow/Prefect/Dagster, Argo/Kubernetes Jobs, Nomad, Dapr Workflow, Restate/DBOS/Hatchet/Inngest/Windmill, durable job queues, and agent-framework checkpointing systems. The point is not to assume any one satisfies EDASES; it is to avoid comparing only systems that already resemble the preferred design.

---

## 13. The experimental program tests happy-path failure detection, not adversarial behavior

The nine experiments are valuable, but most are demonstrations that the engine can recognize expected conditions. They do not yet test the hard consistency boundaries.

Add fault-injection experiments for the following.

### Crash-window tests

For every important operation, crash:

1. before the command is persisted;
2. after command persistence but before state update;
3. after state update but before intent/outbox persistence;
4. after intent persistence but before side effect;
5. after side effect but before result persistence;
6. after result persistence but before notification.

The expected behavior must be defined for each window.

### Duplicate and stale-event tests

* Submit the same command twice with the same idempotency key.
* Submit the same checkpoint twice.
* Deliver a worker-death event after a replacement worker starts.
* Deliver timer events from an old attempt.
* Deliver events out of order.
* Restart the engine while duplicate events are pending.

### Lease and fencing tests

* Pause an old worker, assign a new one, then resume the old worker.
* Let two workers claim the same execution.
* Let an old worker try to complete after its lease expires.
* Reconnect a worker after the engine has reassigned ownership.
* Test worker replacement while the worktree contains uncommitted changes.

### Timer tests

* Engine stops before a timer fires and restarts afterward.
* Timer is cancelled while due.
* Timer is replaced by a newer policy.
* System clock changes.
* Timer fires for an obsolete attempt.
* Multiple timers fire concurrently.

### Git/worktree tests

* Git lock file remains after worker death.
* Worktree is dirty during recovery.
* Branch was moved externally.
* Commit exists but does not belong to the expected execution.
* Partial commit or index corruption occurs.
* A worker bypasses the engine and modifies the branch.
* Cleanup is attempted while another process holds files.

### Storage tests

* Database lock contention.
* Disk full during transition.
* Corrupt or truncated event record.
* Backup restore to an earlier point while workers continue.
* Schema migration with active executions.
* Event retention versus audit requirements.

### Authorization and adversarial-agent tests

* Worker attempts a prohibited transition.
* Worker forges another worker’s identity.
* Agent submits a checkpoint referencing someone else’s commit.
* Auditor attempts an Operator-only action.
* Human override lacks a required reason.
* A stale orchestration session sends an old recovery command.

These tests are more likely to falsify the design than the current demonstrations.

---

## 14. The evidence base needs an incident taxonomy

Section 2.3 lists real failures, which is valuable, but the document jumps from anecdotes to architecture.

The next step should be a structured incident corpus:

| Incident | Root cause | Missing invariant | Required observation | Required enforcement point | Engine requirement |
|---|---|---|---|---|---|
| False relaunch claim | Intent reported as completed | State changes require actuator result | Worker identity/process exists | Engine-owned launcher | Durable intent + verified result |
| Infinite loop | No progress invariant | Fresh evidence required | Checkpoint/artifact freshness | Monitoring only | Staleness condition |
| Missing checkpoint | Policy not applied | Expected evidence deadline | Durable timer | Engine scheduler | Attention transition |
| Worker distribution failure | Ownership ambiguity | Single active attempt | Lease/fencing state | Worker assignment | Fencing tokens |

This would separate failures caused by:

* missing authoritative state;
* missing observability;
* missing capability enforcement;
* bad policy;
* agent reasoning failure;
* tooling defects;
* human-process ambiguity.

Without that mapping, EDASES may build an engine for several different problems while solving none of them well.

The research should also establish a baseline:

* frequency and severity of each failure class;
* current detection time;
* current recovery time;
* number of duplicate or conflicting executions;
* operator intervention burden;
* false-positive and false-negative monitoring rates.

Otherwise “materially reduces failure modes” cannot be evaluated.

---

## 15. The Orchestrator interface is underdefined

The architecture shows the Orchestrator above the engine but does not define the interaction model.

Important unanswered questions include:

* Is the Orchestrator a client, an event consumer, or both?
* Can it directly request transitions?
* Can it create policy?
* Can it override gates?
* Can there be multiple Orchestrators?
* How are conflicting Orchestrator commands resolved?
* Is every Orchestrator decision attributable?
* How does the engine notify it of attention conditions?
* Can the Orchestrator acknowledge, snooze, or resolve a condition?
* What happens when the Orchestrator is unavailable?
* Does the engine queue decisions or escalate to the Operator?

The engine could otherwise become another source of asynchronous messages that agents interpret inconsistently.

The proposal needs a clear command/query/event boundary, for example:

```text
Commands:
  CreateExecution
  AssignWorker
  SubmitEvidence
  RequestCompletion
  ApproveReview
  PauseExecution
  AuthorizeRecovery
  OverridePolicy

Queries:
  GetExecution
  ListAttentionRequired
  GetOwnership
  GetHistory
  GetPendingActions

Events:
  WorkerExited
  CheckpointVerified
  TimerExpired
  PolicyViolationDetected
  TransitionCompleted
```

The exact names are less important than making authority and interaction explicit.

---

## 16. Policy needs versioning and staged enforcement

The document correctly notes that bad mechanical policy can be harmful. It does not yet describe how EDASES will safely evolve policy.

Every transition decision should record:

* policy identifier;
* policy version;
* actor;
* evidence considered;
* decision;
* reason;
* resulting transition or rejection.

Policies should support at least:

```text
shadow/advisory
alerting
enforcing
deprecated
```

This lets EDASES evaluate whether a rule would have fired before making it mandatory.

There also needs to be an explicit exception mechanism:

* who can override;
* what state the override creates;
* whether the override expires;
* whether it applies to one execution or a class;
* what reason and audit trail are required.

Without this, legitimate work will create pressure to bypass the engine, which would undermine the core model.

---

## 17. Non-functional requirements are missing

Even a research prototype needs boundaries for:

* number of concurrent executions;
* expected event rate;
* acceptable transition latency;
* retention duration;
* history size;
* startup recovery time;
* worker reconnection behavior;
* logging and tracing;
* metrics;
* backup and restore;
* security and credential scope;
* data privacy;
* database migration;
* operational debugging;
* disaster recovery.

These are not implementation polish. They determine whether SQLite, a local service, an embedded library, or an existing distributed system is appropriate.

The document should also define what happens when the engine itself is the failed component. An execution engine that becomes a single point of silent failure would reproduce the original problem at a higher layer.

---

## 18. The proposed architecture should probably be reframed

The phrase “Execution Engine” encourages scope creep toward scheduling, queues, workflow execution, retries, supervision, and general orchestration.

A narrower name—such as **Execution Control Plane** or **Execution State Authority**—would better reflect the actual hypothesis.

A sharper provisional architecture would be:

```text
Orchestrator / Operator
        │
        ▼
Execution Control Plane
 ├── command API
 ├── state/transition validator
 ├── policy engine
 ├── durable event/history store
 ├── durable intent/outbox
 ├── timer scheduler
 ├── lease and fencing authority
 ├── reconciliation loop
 └── query/telemetry API
        │
        ▼
Actuators and integrations
 ├── worker launcher/supervisor
 ├── Git/worktree adapter
 ├── OpenCode hooks
 ├── Crosslink adapter
 ├── issue/artifact systems
 └── notification systems
```

The critical addition is the **reconciliation loop**. After a crash, the engine should not merely reload state. It should compare:

* recorded intent;
* observed external reality;
* active leases;
* pending timers;
* incomplete side effects;
* latest verified evidence.

Then it should place each execution into a valid, explainable condition.

---

## 19. Suggested hypothesis-by-hypothesis assessment

| Hypothesis | Assessment | Required change |
|---|---|---|
| H1: State gating is the core primitive | Plausible but overstated | Reframe as validated transitions plus mediated/reconciled side effects |
| H2: Execution state outlives workers | Strong | Add explicit execution/attempt/lease/fencing model |
| H3: Observations differ from judgment | Strong | Add evidence provenance, verification, and trust boundaries |
| H4: Preserve agentic judgment | Strong | Add acknowledgement, override, escalation, and alarm-fatigue semantics |
| H5: Temporal concerns reduce to small primitives | Unproven | Add intents, idempotency, fencing, reconciliation, policy, and authorization |
| H6: Rust is the right boundary | Weak/premature | Treat as an implementation decision to evaluate after semantics |
| H7: Existing systems must be investigated | Strong | Replace feature comparison with executable conformance testing |
| H8: Minimum engine is smaller than a workflow system | Plausible | Keep prototype small, but define topology and consistency boundaries first |

---

## 20. What would most efficiently falsify the proposal?

The strongest falsification program would combine three exercises.

### A. Incident-representation test

Take a representative set of real EDASES failures and model each one using:

* work item;
* execution;
* attempt;
* event;
* evidence;
* transition;
* policy;
* ownership;
* recovery.

If many incidents require ad hoc metadata, out-of-band decisions, or transitions that do not fit the model, state gating is insufficient as the center.

### B. Crash-consistency test

Implement the thinnest possible state authority and run the crash-window, duplicate-event, stale-worker, and timer-restart tests.

If the design cannot preserve simple invariants without acquiring a large amount of workflow infrastructure, the “small focused engine” hypothesis weakens substantially.

### C. Existing-system conformance test

Run the same tests against a small number of representative existing systems, including at least:

* one general durable workflow system;
* one task/job orchestration system;
* one agent/checkpointing system;
* one lightweight embedded approach.

If an existing system passes with a small adaptation layer, the bespoke-engine hypothesis is falsified or must be narrowed to integration-specific requirements.

---

## 21. Recommended revision to the central thesis

I would replace the current framing:

> State gating should be the architectural foundation of the engine.

with:

> EDASES should investigate an authoritative execution control plane in which durable state, validated transitions, evidence requirements, ownership/fencing, durable intents, and reconciliation together constrain agent execution while preserving agentic and human judgment.

And replace the implementation framing:

> A focused Rust Execution Engine is the likely implementation boundary.

with:

> If existing systems cannot provide the required semantics with acceptable adaptation and operational cost, EDASES should prototype the smallest execution control plane that satisfies the conformance suite; Rust is a candidate implementation language, not an architectural premise.

---

## Final assessment

The proposal is strongest when it argues that:

* agent claims are not authoritative;
* execution state should survive worker and runtime failure;
* recovery should attach new attempts to existing executions;
* time-based anomalies should produce attention, not automatic termination;
* existing systems must be tested before building a bespoke engine.

It is weakest when it implies that:

* state gates alone mechanically prevent invalid external actions;
* worker replacement is simple;
* checkpoint or process evidence establishes meaningful progress;
* a flat state model can represent all important execution conditions;
* SQLite/Rust/local-service assumptions can remain implicit;
* existing-system support can be evaluated through a feature matrix;
* Rust follows directly from the problem statement.

The next revision should focus less on naming the engine and more on defining its **authority boundary, consistency model, evidence model, attempt/fencing model, policy model, and failure semantics**. Those decisions will determine whether state gating is the right center, whether an existing system suffices, and whether Rust is justified.
---