# Gas Town Deep Dive: An Architectural Archaeology: Qwen3.7-Plus Summary

## Executive Summary
Gas Town is worth a deep dive precisely because its failure is unusually informative. It explored a massive portion of the design space around autonomous multi-agent software development, accumulated an enormous amount of machinery, and then progressively extracted simpler primitives from that machinery. 

While often dismissed as an overengineered "art project" by a manic creator (Steve Yegge) that mercilessly wasted tokens, Gas Town actually functioned as a large-scale empirical investigation into the failure modes of LLM software development. By building an unusually large experimental apparatus around a handful of correct observations, it magnified agent problems until they became architectural failures. Its successor, **Gas City**, explicitly presents itself as the lower-level, simplified orchestration substrate extracted from Gas Town's corpse.

This report documents the repository archaeology, topology, failure inventory, lineage, and the philosophical divergence between Gas Town, Gas City, and the **ASES/EDASES** methodology.

---

## 1. The Core Insights of Gas Town
Beneath the elaborate vocabulary (Mayor, Polecat, Witness, Convoy, Molecule), Gas Town discovered several fundamental architectural primitives:

1. **Work must outlive the agent:** The agent session is not the durable unit of execution. A session is disposable; work state must be durable and survive crashes, compaction, and restarts.
2. **GUPP (Gas Town Universal Propulsion Principle):** "If work is assigned to you, you execute it." An executable state should imply the next permitted action. The execution engine must enforce state transitions, rather than relying on agent instructions.
3. **The Witness Problem:** Don't ask an agent to enforce a property that the execution substrate can enforce mechanically. Using an LLM to watch another LLM creates a recursive, expensive, and fragile supervision chain.
4. **The Token Tax of Coordination:** Gas Town discovered that paying LLMs to operate orchestration machinery (patrols, idle detection, context repair) is absurdly expensive. If a decision can be made from explicit execution state, do not spend model tokens making it.
5. **Durable State vs. Ephemeral Execution:** Not all workflow steps deserve permanent database rows. Gas Town distinguished between expensive workflows requiring materialized checkpoints (Molecules) and cheap, high-frequency orchestration (Wisps).

---

## 2. Repository Archaeology & Chronology
Gas Town did not begin as a giant system; the giant system emerged by repeatedly adding machinery around a much smaller durable-work primitive. 

### The Conceptual Lineage
*   **Oct 2025 (Beads):** Started as a lightweight issue tracker with Git-backed persistence to solve LLM working memory and long-horizon task tracking.
*   **Dec 17, 2025 (Molecules):** Introduced to break agent work into predefined sequential tasks, preventing agents from managing their own chaotic TODO lists.
*   **Dec 18-20 (Protomolecules & Formulas):** Created to make workflow graphs reusable and composable. Formulas became the "source code" for generating workflow graphs.
*   **Dec 21, 2025 (Wisps):** Introduced as ephemeral, vapor-phase molecules for high-velocity orchestration (e.g., patrol workers) so recurring workflows wouldn't pollute the durable project history.
*   **Jan 2, 2026 (Gas Town v0.1):** The public release. Packaged Beads, Molecules, Hooks, GUPP, and the role hierarchy (Mayor, Deacon, Witness, Refinery, Polecats) into a concrete autonomous software factory.

### The Accumulation of Machinery
Following v0.1, the system metastasized to solve emergent problems:
*   *Problem:* Agents don't start work. -> *Solution:* Hooks, GUPP, `gt sling`, `gt prime`, nudges.
*   *Problem:* Agents stall or die. -> *Solution:* Witness (per-rig health), Deacon (cross-rig health), Boot.
*   *Problem:* Dispatch overloads the system. -> *Solution:* Queues, capacity schedulers, dispatch daemons.
*   *Problem:* State representations diverge. -> *Solution:* Reconciliation loops, Dolt database migration.

---

## 3. System Topology
Gas Town is not one graph, but several coupled graphs with increasingly elaborate machinery sitting at their boundaries.

```text
HUMAN / MAYOR (Strategic Coordination)
       │
       ▼
┌─────────────────────────────────────┐
│ TOWN / RIG (Beads, Convoys, Mail)   │
│ Durable Work & Dependency Graph     │
└──────────────────┬──────────────────┘
                   │ gt sling (Assignment)
                   ▼
┌─────────────────────────────────────┐
│ HOOK (Persistent Agent Ownership)   │
│ GUPP (Propulsion / Behavioral Rule) │
└──────────────────┬──────────────────┘
                   │ prime / nudge
                   ▼
┌─────────────────────────────────────┐
│ AGENT SESSION (tmux + LLM)          │
│ Ephemeral Cognition & Execution     │
└──────────────────┬──────────────────┘
                   │ git worktree
                   ▼
┌─────────────────────────────────────┐
│ REFINERY (Merge / Integration)      │
└─────────────────────────────────────┘

* Overlaid by the SUPERVISION PLANE:
  Deacon (Cross-rig) -> Witness (Per-rig) -> Polecat (Worker)
```

### State Boundaries
*   **Town Beads:** Cross-rig coordination, Mayor mail, strategic issues.
*   **Rig Beads:** Project issues, MRs, project molecules, rig-level agent state.
*   **Git:** Canonical repo, worker branches, worktrees.
*   **Runtime:** tmux sessions, LLM context, injected hooks.

---

## 4. Failure Inventory & Emergent Complexity
Gas Town repeatedly solved a real local failure by adding another layer of state or automation, which then created new failure surfaces. 

### Key Failure Classes
1.  **Split-Brain State:** Multiple representations of an operational fact diverged. (e.g., `issues.status = hooked` but `wisps.hook_bead = NULL`, causing the agent to exit).
2.  **Propulsion Failure:** Work reaches execution state, but the model doesn't execute it. Required endless nudges and hooks.
3.  **Liveness vs. Progress:** "Process exists" does not mean "work is progressing." An LLM can be alive but completely wedged on a tool-use error.
4.  **Recursive Supervision:** The "watchdog watching the watchdog" pathology. `Polecat -> Witness -> Deacon -> Boot`. If the Witness is down, who notices?
5.  **Pathological Graph Expansion:** Agents were allowed to author and mutate the work graph without constraints. Faced with uncertainty, an LLM will convert a simple task into 17 sub-issues and endless documentation, creating the illusion of progress without advancing the terminal objective.
6.  **Completion Verification:** Termination is not proof of completion. Agents would run `gt done` and close beads without actually finishing the work.

### The General Principles Discovered
*   **State must have one authoritative representation.**
*   **Assignment, execution, and completion are different facts.**
*   **LLMs should not be trusted with control-plane transitions.**
*   **Progress must be externally observable** (via evidence, not self-report).
*   **Recovery must be idempotent and bounded** (crash loops burn tokens).

---

## 5. The Evolution to Gas City & Orchestration v3 (O3)
Gas City is not merely "Gas Town 2.0"; it is the SDK extracted from Gas Town. It tore down the fixed role hierarchy and rebuilt the reusable mechanisms as a declarative toolkit.

### The Six Primitives
Gas City reduced the conceptual model to six irreducible primitives:
1.  **Agent** (Who)
2.  **Bead** (What - durable work)
3.  **Formula** (How - workflow templates)
4.  **Rig** (Where - project scope)
5.  **Pack** (Configuration / Topology)
6.  **Event** (Observation)

*Note: The original Gas Town topology (Mayor, Witness, etc.) can now be expressed purely as a Gas City `gastown` Pack configuration.*

### Orchestration v3 (O3) Corrections
Gas City's v3 proposal addresses critical boundary failures inherited from Gas Town:
*   **Execution Scope vs. Work Scope:** Gas Town/GC v1 created one Run per bead. O3 recognizes this is wrong: implementation can be parallel per bead, but *verification* needs the combined convoy. O3 introduces the `Run` as the first-class execution identity over a `Convoy`.
*   **Scatter/Gather Policy:** Moving from hardcoded "any-fail = fail" to author-declared gather policies (e.g., 4 of 5 reviewers must pass).
*   **Typed Dispositions:** Replacing stringly-typed metadata (`gc.outcome=pass|fail`) with compiler-checked ADTs.
*   **Agent ABI:** Moving away from implicit prompt-based contracts to a typed, versioned capability interface (inspired by LSP).

---

## 6. Lineage & Descendants
Which ideas survived contact with reality? We can classify descendants by how they extracted Gas Town's insights:

*   **Chainlink (Refinement):** Extracted the concept of "Hooks" but changed their purpose. Instead of injecting Git/operational commands, Chainlink hooks inject *engineering constraints* (No stubs, proper error handling, pre-coding verification to prevent hallucinations).
*   **Beads Lite (Reduction):** Retained the durable work/dependency graph but replaced the complex SQLite/JSONL sync daemon with one JSON file per issue, achieving a 10x speed improvement.
*   **H2 (Philosophical Counter-example):** Uses Beads for durable work, but deliberately rejects deterministic workflow machinery, allowing a scheduler agent to reason about what happens next.
*   **Multiclaude (Convergence):** Independent convergence on simple mechanisms: JSON state, git worktrees for isolation, a supervisor, and CI as the final merge gate. "Worse is better. Unix vibes."

---

## 7. Gas Town / Gas City vs. ASES
While occupying the same problem space, these systems optimize under radically different resource constraints.

| Feature / Philosophy | Gas Town / Gas City | ASES / EDASES |
| :--- | :--- | :--- |
| **Resource Assumption** | Abundant inference, unlimited budget. | Severely constrained ($10/mo), cheap/free models. |
| **Agent Autonomy** | Embraces autonomy; agents discover and create work. | Constrained autonomy; agents execute authorized topology. |
| **State Substrate** | Universal bead substrate for everything. | Separated: Crosslink (work), Execution Engine (state), Git (code). |
| **Completion** | Eventual completion via persistence & retries. | Verified completion via independent review & audit. |
| **Supervision** | Agent watches agent (Witness/Deacon). | Deterministic infrastructure watches agents. |
| **Context** | Inject massive operational worldview into agent. | Agent queries minimum required context from structured state. |
| **Target User** | Expert engineer managing a dark factory. | Non-programmer needing verifiable, quality software. |

**The Core Divergence:** 
Gas Town asks: *"How much autonomous machinery can I throw at software development?"*
ASES asks: *"What is the minimum amount of intelligence, context, and authority required to produce trustworthy software using the worst available tools?"*

---

## Appendix: EDASES Research Questions & Test Programs

The following research topics and test programs were identified during the Gas Town archaeology as being of specific interest to the future development of the ASES/EDASES methodology.

### 1. Authority Boundaries Comparison
*   **Context:** Discovered during the analysis of Gas Town's pathological graph expansion and ASES's Crosslink restrictions.
*   **Research Question:** How do different systems constrain agent authority over the work graph, execution state, and completion state? Which failures are prevented mechanically versus merely discouraged through prompts?
*   **Test Program:** Map Gas Town, Gas City, and ASES across four boundaries: *Graph Authority* (create/decompose/modify work), *Execution Authority* (claim/dispatch/retry), *Verification Authority* (declare completion/audit), and *Enforcement Mechanism* (Prompt vs. Hook vs. Capability vs. State Gate vs. Human Approval).

### 2. Execution Trust & Substrate Restart Survivability
*   **Context:** Arises from the "Separate Rust process + thin plugin" discussion and Gas City's controller restart limitations.
*   **Research Question:** What state must survive an execution-engine restart, and what state is legitimately reconstructible? How do we prevent the orchestration substrate from becoming the single point of catastrophic failure?
*   **Test Program:** Evaluate the "Thin CLI vs. Separate Process" architecture. Test admission control (quota parking), doom-loop gap enforcement, and structural event attribution (JSONL streams) under harness restart conditions.

### 3. Merge/Integration Queues & Stacked Diffs
*   **Context:** Identified when comparing Gas Town's "Refinery" to ASES's current isolated worktree model.
*   **Research Question:** How should an agent system safely integrate independently produced changes? Can autonomous merge queues be safely recovered once ASES authority and verification boundaries are in place?
*   **Test Program:** Research Bors-style batching, GitHub merge queues, and stacked PR systems (Sapling, Graphite, Treq). Design an ASES integration layer that maps the Crosslink work graph to change dependencies and integration queues.

### 4. Agent-System Fundamentals vs. Distributed Systems
*   **Context:** Emerged during the Gas City v3 (O3) prior-art analysis (Temporal, Kubernetes, MapReduce).
*   **Research Question:** Which execution, coordination, and recovery problems are inherited from distributed systems generally, which become qualitatively different with LLM workers, and which are genuinely specific to AI-agent software engineering?
*   **Hypothesis to Test:** *LLM agent systems are conventional distributed systems plus an adversarially unreliable participant.* (Where "adversarial" means probabilistic, prone to scope mutation, and capable of false semantic completion claims).

### 5. The "Skeleton Factory" Thought Experiment
*   **Context:** Proposed as the final synthesis of the Gas Town dive.
*   **Research Question:** If we knew everything Gas Town discovered, but had to implement it from scratch using ASES principles and constraints, what is the minimum system we would build?
*   **Test Program:** Reconstruct the architecture using *only* foundational primitives (Work Item, State Transition, Agent Session, Execution Evidence, Dependency, Artifact, Event, Policy). Explicitly prohibit Gas Town vocabulary. Measure the resulting complexity against Gas Town's original footprint to validate ASES's compression of accidental complexity.

### 6. Gas Town → Gas City → ASES Divergence Map
*   **Context:** The concluding synthesis of the architectural comparison.
*   **Research Question:** Where exactly do the lineage branches occur, and why?
*   **Test Program:** Create a subsystem-by-subsystem map (Work Graph, Execution, Scheduling, State, Identity, Git, Review, Recovery, Monitoring, Permissions, Context, Persistence, Human Authority) tracing the exact point where Gas Town's abundance-driven choices diverge from ASES's constraint-driven choices.