---
title: "EDASES Topic: Git-Based Engineering Systems"
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Experimental
canonical_repository: edases

depends_on:
  - Documentation Standard
  - EDASES Phase 4 Retrospective

related_documents:
  - EDASES-topic-Methodology-Research.md
  - crosslink-gates/updated-evidence-based-gates.md

consumed_by:
  - Execution engine research programme
  - ASES methodology development

supersedes: []

superseded_by: []

last_updated: 2026-08-10
---

# EDASES Topic: Git-Based Engineering Systems

## 1. Purpose

This research investigates whether Git and GitHub can serve as a substantial part of the engineering substrate for EDASES: not merely as source control, but as infrastructure for persistent engineering state, provenance, agent coordination, progress observation, recovery, review, and controlled integration.

The immediate motivation is that several practices have independently emerged within EDASES that now appear to overlap with broader developments in AI-assisted and agentic software engineering:

* GitHub is already part of the EDASES development environment.
* Agents are already familiar with Git-based workflows.
* Git commits are being used as persistent records of work.
* Agents use five-minute check-in commits as liveness/progress signals.
* Crosslink already launches agents in isolated Git worktrees through its kickoff and swarm workflows.
* Experience with those workflows has produced substantial custom tooling in response to real operational problems.
* Stacked diffs and stacked PRs have subsequently emerged as a promising way to structure incremental agent work.
* GitHub and other tooling vendors are actively developing more agent-oriented Git workflows.

The research should therefore determine whether these are isolated conveniences or parts of a coherent **Git-based engineering methodology for agentic software development**.

The central research question is:

> **To what extent can existing Git and GitHub primitives provide the persistent, observable, recoverable, reviewable, and coordinatable engineering substrate required by EDASES, and where does EDASES genuinely require additional infrastructure?**

The outcome should not be predetermined. Git may prove capable of representing substantially more EDASES state than currently expected, or the research may identify clear boundaries where external state and coordination mechanisms are necessary.

---

## 2. EDASES Context

Git should be investigated in the context of the methodology EDASES is already developing rather than as a generic version-control technology.

EDASES is concerned with software engineering performed through AI agents under human direction, with particular emphasis on preventing loss of context, knowledge, reasoning, assumptions, and engineering state.

This makes several properties of Git unusually relevant:

* commits provide durable snapshots of state;
* diffs expose concrete changes;
* parent relationships provide causal history;
* branches represent divergent lines of work;
* merges represent convergence;
* worktrees provide isolated working environments;
* GitHub provides pull requests, reviews, CI results, issues, and discussion;
* repository history provides an inspectable record after an agent session has ended.

The important question is therefore not simply whether EDASES should "use Git." It already does.

The question is:

> **How much of the EDASES engineering process can naturally be expressed through Git-based primitives before bespoke coordination or state infrastructure becomes necessary?**

---

## 3. Existing EDASES Evidence: Crosslink

EDASES already has a substantial operational basis for researching Git-based agent workflows through Crosslink and its associated kickoff and swarm mechanisms.

Crosslink launches agents into isolated Git worktrees rather than relying on the standard single-workspace subagent mechanism. Swarm workflows extend this model to multiple agents operating concurrently and through staged coordination.

This is important because worktree isolation should therefore **not** be treated as a greenfield EDASES experiment.

There are already numerous real agent sessions from which evidence can be gathered, including both successful workflows and the problems encountered in practice. A significant amount of custom tooling has emerged in response to those problems.

The first research activity should therefore be a retrospective analysis of this existing operational history.

### Questions for the retrospective

For existing Crosslink sessions, investigate:

* How were agents assigned work?
* What Git branches and worktrees were created?
* What commits did agents produce?
* How frequently did agents commit?
* What information was recoverable from Git alone?
* What information existed only in Crosslink's state?
* What failures occurred?
* Which failures required intervention?
* How was stalled work detected?
* How was incomplete work handed to another agent?
* What integration conflicts occurred?
* Which problems resulted in additional Crosslink tooling?
* Did the tooling duplicate information already represented by Git?
* Which information genuinely could not be represented conveniently through Git?
* How well could a new agent reconstruct an interrupted session from the repository?
* How much of the agent's reasoning or intent survived in repository artifacts?

This retrospective should explicitly examine whether existing Crosslink mechanisms represent **necessary extensions to Git** or whether some have arisen because Git-native mechanisms were not yet being exploited.

Crosslink should be treated as an empirical case study in the design of multi-agent Git workflows, not merely as an implementation dependency.

---

## 4. Existing EDASES Check-In Mechanism

EDASES already uses a five-minute check-in commit mechanism for agents.

The immediate purpose is operational: a supervisor can quickly identify an agent that has stopped making expected progress and intervene.

This introduces an important distinction between three possible kinds of Git activity:

**Heartbeat**

> The agent is still operating.

**Progress**

> The agent has reached a particular state or produced a meaningful intermediate result.

**Deliverable**

> A coherent change is ready for review or integration.

These do not necessarily need to be separate Git mechanisms, but the methodology should investigate whether they should remain semantically distinct.

The check-in system is particularly relevant because it extends Git's role beyond source history:

> **Repository activity can become an observable operational signal.**

This raises a testable hypothesis:

> Can Git activity provide useful agent liveness and progress detection without requiring a separate monitoring database?

The research should examine false positives, false negatives, stalled sessions, recovery scenarios, and the information available to a supervisor from the repository history alone.

---

## 5. State-of-the-Art Survey

The research should survey current and in-development Git-based engineering workflows, with particular attention to systems designed for or increasingly adapted to AI agents.

The survey should distinguish:

* established production practices;
* mature open-source tooling;
* emerging practices;
* private previews and in-development features;
* announced roadmaps;
* experimental systems;
* empirical research.

Marketing claims and roadmap statements should not be treated as evidence that a capability works reliably.

### 5.1 Git as Persistent Engineering Memory

Investigate the use of:

* commits;
* branches;
* tags;
* repository history;
* commit metadata;
* Git notes or equivalent metadata mechanisms;
* signed commits;
* reflogs and recovery mechanisms;
* GitHub issues and PR history.

The objective is to determine what engineering state can be durably reconstructed from Git and GitHub artifacts.

### 5.2 Agent Isolation

Survey:

* Git worktrees;
* per-agent branches;
* ephemeral clones;
* repository-per-agent approaches;
* shared workspaces;
* filesystem and execution isolation combined with Git isolation.

The emphasis should be on how different systems assign ownership of repository state to concurrent agents and how they handle integration.

### 5.3 Incremental and Stacked Work

Survey:

* incremental commits;
* stacked diffs;
* stacked branches;
* stacked pull requests;
* dependent PRs;
* branch-stack management;
* agent support for stacked workflows.

Relevant systems include GitHub's emerging stacked-PR capabilities, Graphite, GitButler, Git Town, Sapling, Jujutsu, Gerrit-style change workflows, and other systems discovered during research.

The research should specifically investigate whether stacked diffs are primarily a review optimization or whether they provide deeper benefits for agent reasoning, recovery, provenance, and coordination.

### 5.4 Agent Coordination and Lifecycle

Investigate Git-based mechanisms for:

* agent assignment;
* progress reporting;
* check-ins;
* handoffs;
* interruption;
* recovery;
* ownership;
* dependency representation;
* stalled-agent detection.

The survey should include both Git-native mechanisms and systems that place an additional coordination layer around Git.

### 5.5 Review and Verification

Investigate workflows in which:

```text
agent
  ↓
commit(s)
  ↓
PR
  ↓
CI / review
  ↓
agent feedback loop
  ↓
additional commit(s)
  ↓
verification
  ↓
merge
```

The research should examine PRs as more than delivery mechanisms: they may function as structured boundaries for proposed engineering state transitions, review, evidence, and intervention.

### 5.6 GitOps and Declarative/Reconciliation Models

GitOps should be included as a related methodology rather than treated as the overall answer.

Investigate:

* Git as authoritative desired state;
* declarative configuration;
* reconciliation;
* Git-triggered deployment;
* infrastructure-as-code;
* Git-based control planes;
* separation between desired state and observed state.

The objective is to identify principles transferable to EDASES rather than to adopt GitOps terminology or architecture wholesale.

---

## 6. Research Hypotheses

The research should treat the following as hypotheses rather than assumptions.

### H1 — Git can provide durable engineering memory for a substantial portion of EDASES state.

A meaningful amount of engineering context, progress, provenance, and state should be reconstructable from commits, branches, PRs, reviews, and related repository artifacts.

### H2 — Incremental commits improve recoverability compared with monolithic agent changes.

An interrupted agent should leave behind enough structured intermediate state for another agent to understand and continue the work more effectively.

### H3 — Repository activity can provide useful liveness and progress signals.

Regular Git activity may allow stalled agents to be detected and intervention initiated without requiring a separate monitoring mechanism for every session.

### H4 — Stacked diffs provide useful boundaries for agent work.

Breaking dependent work into reviewable increments may improve review, verification, recovery, handoff, and error localization.

### H5 — Git worktrees provide an effective isolation primitive for concurrent agents.

The existing Crosslink experience should reveal both where worktree isolation works well and where additional coordination mechanisms become necessary.

### H6 — Git-native workflows reduce the need for bespoke agent coordination protocols.

Agents already understand Git. A workflow based primarily on familiar Git operations may therefore provide lower cognitive and implementation overhead than an equivalent custom coordination protocol.

### H7 — Git cannot represent all EDASES state efficiently.

The research should actively seek counterexamples. Some state may require external storage because it is dynamic, operational, query-oriented, ephemeral, or poorly represented by Git's data model.

---

## 7. Experimental Program

The experimental program should proceed from existing evidence toward targeted experiments rather than immediately constructing artificial benchmarks.

### Experiment A — Crosslink Historical Analysis

Analyze existing kickoff and swarm sessions.

For representative sessions, reconstruct:

* agent topology;
* worktree topology;
* branch topology;
* commit sequence;
* check-in activity;
* failures;
* interventions;
* handoffs;
* integration events;
* external coordination state.

Determine what could have been recovered from Git/GitHub alone and what required Crosslink-specific state.

This should be the first experiment because it uses evidence already accumulated during EDASES development.

### Experiment B — Check-In and Recovery

Use the existing five-minute check-in mechanism.

Intentionally terminate or stall agents at different points in representative tasks.

Measure:

* detection latency;
* false detection rate;
* information available to the supervisor;
* time required for another agent to resume the work;
* amount of lost context;
* usefulness of intermediate commits.

Compare recovery from sessions with useful incremental commits against sessions with minimal or monolithic commits.

### Experiment C — Incremental vs. Monolithic Work

Have comparable agents perform equivalent tasks under two workflows:

**Monolithic**

One large change followed by a final PR.

**Incremental**

Multiple meaningful commits representing intermediate progress.

Evaluate recoverability, reviewability, error localization, and handoff quality.

### Experiment D — Stacked vs. Conventional PRs

Compare conventional feature branches against stacked changes.

The experiment should not merely measure review speed.

It should investigate whether stacking improves:

* decomposition;
* dependency visibility;
* review boundaries;
* verification;
* intervention;
* handoff;
* recovery;
* attribution of failures.

Where possible, use tasks and histories derived from real EDASES work rather than synthetic examples.

### Experiment E — Concurrent Agents and Worktrees

Use the existing Crosslink infrastructure to study concurrent agents.

Measure:

* isolation failures;
* integration conflicts;
* coordination overhead;
* repository-state ambiguity;
* recovery after individual agent failure;
* usefulness of branch/worktree topology;
* external state required to coordinate agents.

The purpose is not to prove that worktrees work; EDASES already uses them. The purpose is to establish their limits and determine what must surround them.

### Experiment F — Integrated Git-Native Workflow

Combine the mechanisms that survive the earlier experiments:

```text
isolated worktree
      ↓
check-in / heartbeat
      ↓
incremental commits
      ↓
stacked change
      ↓
CI / review
      ↓
agent remediation
      ↓
verification
      ↓
merge
```

Evaluate the integrated workflow as a candidate EDASES engineering pattern.

The integrated experiment should specifically test whether the individual mechanisms reinforce one another or merely add procedural complexity.

---

## 8. Evaluation Criteria

Experiments should be evaluated against properties that matter directly to EDASES.

### Recoverability

Can another agent resume meaningful work after an agent terminates unexpectedly?

### Observability

Can a supervisor determine what agents are doing without interrogating each agent directly?

### Provenance

Can the system reconstruct what changed, when, by whom, and through which sequence of intermediate states?

### Reviewability

Can humans or agents understand individual changes without reconstructing an enormous undifferentiated diff?

### Isolation

Can multiple agents work concurrently without destructive interference?

### Intervention

Can stalled, incorrect, or misbehaving agents be stopped and replaced without losing useful work?

### Context Preservation

How much useful engineering knowledge survives agent termination?

### Complexity

How much bespoke infrastructure is required beyond Git and GitHub?

### Agent Usability

Can existing agents reliably operate the workflow using familiar Git primitives?

### Failure Behavior

What happens when an agent, Git operation, worktree, CI system, GitHub, or coordination mechanism fails?

---

## 9. Git-Native State vs. External State

A central output of the research should be a classification of EDASES state into three categories.

### Git-native

State that Git represents naturally and durably.

Examples may include:

* source state;
* declarative artifacts;
* incremental changes;
* branch relationships;
* engineering decisions represented as artifacts;
* historical provenance.

### Derived

State that can be reconstructed or calculated from Git/GitHub rather than stored independently.

Examples may include:

* progress;
* change lineage;
* branch topology;
* certain agent activity metrics;
* some aspects of workflow state.

### External

State that requires a separate mechanism because Git is an unsuitable representation.

Potential examples include:

* live process state;
* ephemeral locks;
* active resource allocation;
* high-frequency operational telemetry;
* coordination state requiring transactional queries;
* state whose authoritative representation cannot reasonably be a repository artifact.

This classification is more important than the question of whether EDASES should "use a database."

The research should determine **where an external state system adds genuine capability rather than duplicating information already available through Git**.

---

## 10. Tool and Methodology Comparison

The research should produce a comparative survey of relevant systems, including both established and emerging approaches.

The comparison should cover at minimum:

* GitHub native workflows;
* GitHub stacked PRs;
* GitHub Copilot agent workflows;
* GitHub Copilot CLI/fleet workflows;
* Graphite;
* GitButler;
* Git Town;
* Sapling;
* Jujutsu;
* Gerrit/change-oriented workflows;
* GitOps systems;
* Crosslink;
* other relevant agent-oriented Git systems discovered during research.

The purpose is not to select a single product.

Instead, identify **reusable engineering patterns and primitives**.

A useful result would distinguish:

1. patterns already present in EDASES;
2. patterns independently emerging elsewhere;
3. patterns that appear promising but remain immature;
4. patterns EDASES should experiment with;
5. patterns that appear unnecessary for EDASES.

---

## 11. Expected Outputs

The research should produce:

1. **State-of-the-art survey** of Git-based agent engineering workflows.
2. **Crosslink retrospective** based on actual EDASES sessions.
3. **Git capability map** showing what Git/GitHub can provide directly.
4. **External-state boundary analysis** identifying what requires additional infrastructure.
5. **Experimental results** for check-ins, incremental commits, stacking, worktrees, and integrated workflows.
6. **Recommended Git-based EDASES workflow.**
7. **Methodological requirements** that should become part of ASES if supported by evidence.
8. **Architectural implications** for EDASES and its lower-level execution systems.
9. **Tooling recommendations** where existing systems provide useful capabilities that EDASES should adopt rather than reproduce.

The final recommendation should explicitly distinguish between:

* mechanisms EDASES should adopt;
* mechanisms EDASES should adapt;
* mechanisms EDASES should merely understand;
* mechanisms EDASES should avoid;
* capabilities that remain unresolved research questions.

---

## 12. Guiding Principle

The research should follow a simple architectural principle:

> **Reuse mature engineering primitives wherever their semantics already match the problem; introduce bespoke machinery only where the existing primitives demonstrably cannot provide the required capability.**

This means the research should not begin from either of two assumptions:

> "Git should be the database."

or:

> "Git is only source control, so EDASES needs a separate coordination system."

Both are conclusions that the research should test.

The more useful possibility is a layered model in which:

```text
Git/GitHub
    ↓
persistent artifacts, history, provenance, review
    ↓
EDASES methodology
    ↓
coordination / orchestration semantics where required
    ↓
execution infrastructure
```

The purpose of this research is to determine how much functionality can remain in the first layer and how little bespoke infrastructure the layers above it actually need.

The existing Crosslink experience, five-minute check-in system, and emerging stacked-diff workflows provide EDASES with an unusually strong starting point: the project can investigate this question using both **real operational history and controlled experiments**, rather than designing the answer from theory alone.
