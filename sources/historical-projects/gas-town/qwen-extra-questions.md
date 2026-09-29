Prompt continuing the Gas Town deep dive summar: Well done. Good analysis of the conversation. You identified the research questions we deferred - but did it seem like there were some more that we got close to but didn't quite articulate?

[QWEN3.7-Plus]
Yes, you are absolutely right to call that out. While we explicitly flagged several major research topics (like the Authority Boundary comparison and the Execution Trust matrix), there were several rich, half-formed hypotheses and tangential deep-dives that we touched on, recognized as valuable, but deliberately parked or left slightly unarticulated to stay on track. 

Here are the **implicit or near-miss research questions** that emerged from the conversation, which deserve to be formalized into future test programs or research tracks for EDASES/ASES:

### 1. The Integration & Merge Authority Gap
* **Where it came up:** When discussing Gas Town’s *Refinery* and how ASES currently handles isolated worktrees + orchestrator review, but hasn't fully solved large-scale multi-agent integration.
* **The Implicit Question:** How should an agent system safely integrate independently produced, semantically correct changes that might conflict structurally when combined? 
* **Why it matters:** ASES currently solves *semantic* correctness (did the builder do the right thing?), but not *integration* correctness (do Builder A’s and Builder B’s changes break the system when merged?). 
* **Test Program Idea:** Map Gas Town’s Refinery (Bors-style batching, binary bisection) and modern stacked-PR systems (Graphite, Treq, GitHub merge queues) against ASES’s current merge workflow. Design a deterministic "Integration Gate" that operates *after* semantic review but *before* mainline merge, specifically testing for cross-cutting failures.

### 2. Agent Systems as "Distributed Systems + Adversarially Unreliable Participants"
* **Where it came up:** During the Gas City v3 / Orchestration v3 (O3) prior-art analysis, comparing Gas City’s discoveries to Temporal, Kubernetes, MapReduce, and LSP.
* **The Implicit Question:** Which coordination, recovery, and state problems are simply mature distributed-systems problems, and which are *qualitatively different* (or entirely new) because the "worker" is a probabilistic LLM that can lie, hallucinate, or confidently declare false completion?
* **Why it matters:** It prevents EDASES from reinventing Temporal or Kubernetes, while highlighting exactly where traditional tools fail (e.g., Kubernetes trusts a Pod’s `Running` state; ASES cannot trust an LLM’s `done` state).
* **Test Program Idea:** Take a standard distributed workflow pattern (e.g., Scatter/Gather, Durable Wait/HITL, Reconciliation) and explicitly map how the "LLM unreliability factor" changes the required state machine, evidence contracts, and failure boundaries.

### 3. The "Skeleton Factory" Thought Experiment (Minimum Viable Architecture)
* **Where it came up:** Early in the conversation as a conceptual capstone.
* **The Implicit Question:** If we knew everything Gas Town discovered, but had to implement it from scratch using strict ASES constraints (no Gas Town vocabulary, minimal tokens, deterministic authority), what is the absolute minimum system we would build?
* **Why it matters:** It acts as a razor against "feature creep" and accidental complexity. If the resulting design still requires 15 concepts, Gas Town’s complexity was fundamental. If it requires 4, Gas Town’s complexity was accidental.
* **Test Program Idea:** A clean-room architecture exercise. Start with only: *Work Item, State Transition, Agent Session, Execution Evidence, Dependency, Policy*. Attempt to design a system that prevents the top 5 Gas Town failure modes (e.g., pathological graph expansion, GUPP violations, split-brain state) using *only* mechanical enforcement and minimal LLM judgment.

### 4. Context Hydration vs. Context Injection (The "60-Minute Research Adventure" Problem)
* **Where it came up:** When discussing Gas Town’s `gt prime` / hook injection versus ASES’s Crosslink retrieval, and your observation about agents going on massive, off-task research tangents or rewriting entire site architectures for minor fixes.
* **The Implicit Question:** What is the minimum viable context required for an agent to execute a complex project without hallucinating or expanding scope, and how do we mechanically enforce that boundary?
* **Why it matters:** Gas Town’s answer was to inject a massive "operational worldview" into the agent. ASES’s answer is structured retrieval. But agents still find ways to over-research. 
* **Test Program Idea:** Analyze the "scope violation" failure mode. Design a mechanical constraint (e.g., file-path allowlists, strict Crosslink query limits, or pre-coding grounding hooks like Chainlink’s) that physically prevents an agent from accessing or modifying out-of-scope domains, regardless of its prompt instructions.

### 5. Model Capability Matrix as an Architectural Control (Adversarial Redundancy)
* **Where it came up:** When discussing Hy3 as a reviewer because it "rederives almost every claim," and how model diversity isn't just about picking the "best" model, but about breaking correlated reasoning failures.
* **The Implicit Question:** How can model capability matrices be used not just for cost-effective task routing, but as a *mechanical control* to ensure that no single model’s blind spots can compromise the entire verification pipeline?
* **Why it matters:** It elevates model selection from a "performance optimization" to a "security/reliability invariant." 
* **Test Program Idea:** Define a "Verification Quorum" policy. Test scenarios where a cheap builder’s output is reviewed by Model A (strong at logic, weak at syntax) and Model B (strong at syntax, weak at logic), with an Auditor (Model C) specifically tasked with finding discrepancies between A and B’s reviews. Measure the false-positive/false-negative rates compared to a single frontier model.

### 6. Substrate Failure & Self-Repair Limits
* **Where it came up:** When you mentioned the Crosslink hydration incident that took a whole day to fix, blocking other work.
* **The Implicit Question:** When the authoritative state substrate (e.g., Crosslink, the Execution Engine) fails or becomes inconsistent, what is the recovery protocol that *does not* rely on the agent to fix its own tooling?
* **Why it matters:** Gas Town repeatedly ran into orphaned databases, Dolt migration failures, and stuck reconcilers. If the tool that enforces authority is broken, giving the agent "temporary authority to fix the tool" is a massive security and stability risk.
* **Test Program Idea:** Design a "Substrate Degradation Protocol." Define explicit, human-in-the-loop (or highly constrained deterministic) recovery paths for when the Execution Engine, Crosslink, or Git state diverge, explicitly forbidding the agent from autonomously rewriting state to "make it work."

### 7. The Meta-Question: Human Design vs. Model-Driven Emergence
* **Where it came up:** When analyzing Yegge’s own accounts of building Gas Town with Opus 4.5–4.7, noting the model’s tendency to over-engineer and the "just two more things" tic that eventually burned the project down.
* **The Implicit Question:** In AI-assisted architecture, how do we distinguish between a human’s deliberate, sound architectural insight and a frontier model’s tendency to generate elaborate, locally coherent but globally fragile scaffolding?
* **Why it matters:** It informs *how* we should use LLMs to build EDASES itself. If we ask an LLM to "design a better state machine," it might give us Gas Town v2. 
* **Test Program Idea:** Develop an "Architectural Compression" heuristic for EDASES development. Whenever a new mechanism is proposed (by human or AI), require a proof that it cannot be reduced to a simpler state transition, a deterministic script, or a capability restriction before it is accepted into the core.

---

**Summary:** 
We successfully mapped the *explicit* gaps (Authority, Execution Trust, Reviewer Quorums). But these *implicit* gaps represent the next layer of depth: how ASES handles integration, how it leverages model diversity as a security feature, how it prevents scope creep mechanically, and how it survives its own substrate failing. 

Would you like me to format any of these into the same rigorous "Research Question / Test Program" structure as the appendix for your records?