---
title: EDASES Execution Authority - RPC Enforcement Prototype
program: EDASES
layer: Implementation
document_type: Experiment Design
status: Proposed
authority: Derived
canonical_repository: edases
parent_epic: "#441"
classification: v2-integration successor to the ases-tools thin CLI - build order CLI first, RPC core second
related_documents:
  - crosslink-auto-export-plan-v7.md
  - docs/research/deep-research-423-support-systems.md
  - agent-tooling-and-permission-enforcement.md
---

# EDASES Execution Authority — RPC Enforcement Prototype

## Objective

Test whether a thin OpenCode plugin communicating with a local Rust core over RPC can provide a reliable, low-overhead, machine-readable enforcement boundary for ASES.

### Hypothesis

A harness plugin can intercept agent tool use and delegate the decision to a durable EDASES state/policy authority, allowing methodology to be enforced mechanically rather than through prompts, while keeping policy logic and state outside the model context.

This is an experiment, not an architectural commitment.

## Minimal architecture

OpenCode
    │
    ▼
EDASES plugin
    │
    │ local RPC
    ▼
EDASES Rust core
    │
    ├── state
    ├── policy
    ├── lifecycle
    └── admission
    │
    ▼
ALLOW / DENY / REDIRECT / WAIT
    │
    ▼
OpenCode execution

The initial prototype should NOT implement the complete EDASES state machine, issue tracker, Crosslink replacement, semantic liveness system, or Orchestrator.

It should prove the enforcement boundary.

## Experiment 1 — Basic interception

Create the smallest possible plugin/core pair.

The plugin should intercept selected tool calls and send structured requests to the Rust core.

Test:

- ordinary tools;
- shell execution;
- subagent/task invocation;
- background execution;
- MCP tools;
- any other execution path exposed by the harness.

The core should receive enough information to identify:

- session;
- agent;
- tool;
- invocation;
- arguments;
- relevant execution context.

PASS:
Every tested execution path reaches the authority before execution.

FAIL:
Any execution path can bypass the authority without an explicitly documented exception.

## Experiment 2 — Hard policy enforcement

Implement only:

- ALLOW
- DENY
- REDIRECT

Example:

{
  "decision": "DENY",
  "code": "MODEL_NOT_APPROVED",
  "message": "The selected model has not been approved."
}

Verify that the agent receives a compact machine-readable rejection and can recover.

Test whether an agent can evade the rule by:

- changing tool arguments;
- changing tool names;
- invoking a shell wrapper;
- delegating to a subagent;
- invoking another available execution mechanism.

The important distinction is:

"the agent was instructed not to do X"

versus:

"X cannot execute in the current state."

## Experiment 3 — Stateful policy

Implement one deliberately simple cross-call rule:

- first three task invocations are permitted;
- the fourth invocation requires Swarm instead of Kickoff.

Example:

task
task
task
task

Expected:

ALLOW
ALLOW
ALLOW
REDIRECT → SWARM

The core must maintain the relevant state across calls.

This proves that the system is a stateful execution authority rather than a stateless permission checker.

## Experiment 4 — Lifecycle gate

Implement:

MODEL_SELECTION_PENDING

Attempt a tool operation while the state is pending.

Expected:

tool request
→ RPC
→ WAIT/DENY
→ operator or Orchestrator resolves model choice
→ state transition
→ operation becomes executable

Determine whether the harness can suspend and subsequently resume the same operation cleanly.

If it cannot, document the exact limitation rather than designing around it prematurely.

## Experiment 5 — Failure semantics

Terminate the Rust core while an agent is active.

Determine the behavior of:

- normal tool calls;
- read-only operations;
- recovery operations;
- already-running operations.

Compare:

- fail closed;
- fail open;
- restricted safe mode.

The support system must not create a worse failure mode than the failures it is intended to prevent.

## Experiment 6 — Performance

Measure:

- RPC round-trip latency;
- throughput;
- concurrent-agent behavior;
- CPU usage;
- memory usage;
- startup/restart time;
- additional model tokens;
- recovery time after DENY/REDIRECT.

The key metric is not simply RPC latency.

Determine whether moving policy out of model context produces a measurable reduction in total token consumption.

## Experiment 7 — Structured protocol recovery

Test whether compact structured decisions are sufficient for agents to recover.

Example:

{
  "decision": "REDIRECT",
  "required_operation": "swarm",
  "reason": "parallelism_limit",
  "details": {
    "requested": 4,
    "maximum": 3
  }
}

Compare this against natural-language policy instructions.

Measure:

- recovery success;
- additional tokens;
- number of turns;
- incorrect retries.

## Experiment 8 — Adversarial bypass

Attempt to bypass the authority through:

- subagents;
- background agents;
- MCP;
- shell wrappers;
- nested agent launches;
- direct Crosslink invocation;
- direct OpenCode invocation;
- alternate tool names;
- concurrent calls;
- malformed requests;
- process restarts.

Every discovered bypass should be classified as:

1. eliminate;
2. explicitly permit;
3. move the enforcement boundary;
4. harness limitation.

Do not silently assume that an interception hook covers every execution path.

## Experiment 9 — Crash and recovery

Kill the Rust core.

Restart it.

Determine whether it can reconstruct authoritative state from durable storage and continue safely.

Test:

- active sessions;
- pending gates;
- outstanding decisions;
- agent identity;
- work-item state;
- resource state.

The core must not depend on volatile process memory for information required to enforce methodology.

## Experiment 10 — Protocol as agent execution language

Test a more ambitious possibility.

Instead of exposing raw execution primitives and merely authorizing them, expose structured EDASES operations such as:

- dispatch;
- kickoff;
- swarm;
- inspect;
- request approval;
- report;
- complete;
- merge;
- retry.

Determine whether the model can operate primarily through these primitives.

The hypothesis is that the RPC can become not merely an authorization API but the machine-readable execution protocol through which the agent interacts with the methodology.

## Success criterion

The experiment succeeds if we can demonstrate:

1. reliable interception;
2. mechanical blocking;
3. stateful policy;
4. structured recovery;
5. acceptable latency;
6. safe core failure;
7. no unacceptable token overhead;
8. no unaccounted-for execution bypasses.

A successful result establishes a viable execution-authority substrate.

It does NOT establish the final EDASES architecture.

The next research questions should then determine what state, policy, coordination model, and harness adapters belong on top of it.
