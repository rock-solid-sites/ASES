---
title: Execution Engine Classification - Mechanical Invariants, Gates Around Judgment, and Model Judgment
program: EDASES
layer: Implementation
document_type: Analysis
status: External-Unverified
authority: External
canonical_repository: edases
parent_epic: "#423"
provenance: "ChatGPT independent review of hookability classifications, 2026-08-24, operator-conducted"
verification_status: "claims citing upstream issues/sources unverified - cross-check against issue #455 fact-check pass and direct source inspection"
---
---
The classification is directionally right, but I would change the boundary substantially: **many of the rules in (C) are not truly “not hookable”; they are “not fully decidable mechanically.”** That distinction matters for EDASES because the execution engine can mechanically enforce a rule *after* an agent/model supplies a judgment, or enforce the structural prerequisites around that judgment.

The most valuable shift is to classify rules into **mechanical invariant, mechanical gate around a judgment, and genuinely judgmental** rather than hookable/not-hookable.

## 1. The biggest classification change

I would split (C) roughly like this:

| Rule                          | My classification                        | Why                                                                                        |
| ----------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------ |
| danger rationale              | **Judgment + mechanical gate**           | Model supplies rationale; engine can require its existence, schema, evidence, and approval |
| correct-alternative selection | **Judgment**                             | Usually semantic                                                                           |
| tier selection                | **Judgment + mechanical gate**           | Model selects; engine can enforce permitted transitions and required evidence              |
| timeout estimation            | **Judgment + mechanical enforcement**    | Model estimates; engine enforces the resulting deadline                                    |
| acceptance criteria prompts   | **Mechanical gate**                      | Engine can require criteria before launch; model writes them                               |
| skeleton-vs-fidelity          | **Judgment**                             | Unless represented by explicit project metadata                                            |
| proven-pattern judgment       | **Judgment + evidence gate**             | Model judges; engine can require cited repository evidence                                 |
| decision-gating judgment      | **Judgment + state gate**                | Engine can prevent progress until decision exists                                          |
| failure-response behavior     | **Judgment + constrained state machine** | Model chooses halt/report/wait; engine restricts legal transitions                         |

That last category is especially important. **The model should decide what to do; the engine should decide whether what it chose is a legal state transition.**

That is much closer to the EDASES state-machine hypothesis.

---

# 2. I would add a fourth category: mechanically enforceable invariants

Your (B) list is good, but I think it misses a larger class of rules that fall out of the execution substrate.

### Highest-value additions

**A. Session/worker identity binding**

Every worker should have a binding:

```text
work_item
    ↕
execution_id
    ↕
session_id
    ↕
process_id / incarnation_id
    ↕
worktree
```

The engine can then reject events that don't correspond to the expected execution.

This is much stronger than merely logging session IDs. OpenCode's plugin API exposes `sessionID` on tool hooks, while its event hook receives the event bus globally. ([GitHub][1])

This enables mechanical enforcement of:

* worker cannot operate outside its assigned worktree;
* worker cannot modify another work item's state;
* telemetry must belong to the claimed execution;
* stale worker cannot mutate current work-item state;
* restarted worker is a new **incarnation**, even if it resumes the same session.

I would rank this **very high**.

---

### B. Tool-call provenance

Every tool invocation can be given an execution record:

```text
execution
session
message
tool
call
arguments
permission decision
start
finish
result
```

The plugin API explicitly exposes `tool`, `sessionID`, and `callID` before execution, and those same identifiers after execution. ([GitHub][2])

That means the engine can mechanically establish:

> "This command was actually executed by this worker, as part of this session, under this policy."

That opens up enforcement of **evidence provenance**, not merely logging.

For EDASES I think this is more important than conventional logs.

---

### C. No-progress / repeated-progress detection

Your existing doom-loop detection should not be treated as the whole liveness mechanism.

OpenCode's built-in detector is only:

> three identical consecutive tool calls.

That's a very narrow pattern.

Your engine can detect richer conditions:

```text
N tool calls with no state change
N minutes with no artifact change
N minutes with no Crosslink transition
N iterations with identical failure
N retries against same external resource
N commands repeatedly returning same result
```

The important part is that these are **observable properties**, not model judgments.

This should probably become a major enforcement family of its own.

---

### D. Permission-wait detection

This is distinct from your 120-second heartbeat.

An agent can be:

```text
alive
not executing
not dead
waiting for permission
```

and therefore look healthy to a heartbeat monitor.

The existing OpenCode permission architecture has precisely the ingredients that make this detectable. More importantly, there is a documented problem where unanswered permission requests can leave headless sessions stalled indefinitely. ([GitHub][3])

So I would add:

> **permission-pending timeout/escalation**

For example:

```text
permission pending > 60s
    → coordinator notification

> 5m
    → execution state = BLOCKED

> 15m
    → escalate
```

This is potentially as valuable as the 429 detector.

---

### E. Queue/backpressure detection

A worker can also be alive but not actually making progress because work is queued behind another operation.

Since the platform exposes session status and asynchronous prompting, the execution engine can distinguish:

```text
RUNNING
WAITING_FOR_PERMISSION
WAITING_FOR_PROVIDER
WAITING_FOR_INPUT
QUEUED
STALLED
FAILED
COMPLETED
```

rather than collapsing all of these into "agent alive/dead."

That is precisely the sort of explicit state gating you have been moving toward.

---

# 3. Your #1 rate-limit detector should probably become broader

I agree with putting the 429 detector first, but I would change its definition.

Don't build:

> "429 detector"

Build:

> **provider-backoff state detector**

Because the structured provider error path already exposes status, retryability, and response headers, and OpenCode's retry subsystem consumes retry headers. The execution engine can therefore distinguish at least:

```text
RATE_LIMITED
TRANSIENT_PROVIDER_FAILURE
AUTH_FAILURE
PROVIDER_UNAVAILABLE
PERMANENT_PROVIDER_ERROR
UNKNOWN_PROVIDER_FAILURE
```

Then the policy becomes:

```text
RATE_LIMITED
    → PARKED / WAITING_FOR_PROVIDER
    → don't classify as worker stall

AUTH_FAILURE
    → BLOCKED

PERMANENT_PROVIDER_ERROR
    → FAILED

TRANSIENT
    → RETRYING

UNKNOWN
    → ESCALATE
```

That's substantially more valuable than merely preventing false-positive stall detection.

---

# 4. Your webfetch guard is probably too high-level

The three-state model is sensible, but I'd move the mechanical boundary down.

Instead of:

> allow queries / ask bulk-ingestion / deny excess

make the engine mechanically track **network acquisition budget**:

```text
request count
bytes acquired
domains
URLs
response size
repeated URL
time spent
artifact destination
```

Then a policy/model can decide whether a particular research operation is legitimate, while the engine enforces hard limits.

For example:

```text
ordinary search
    ≤ 20 requests

bulk acquisition
    requires declared research task

> 100 MB
    hard block

same URL repeatedly
    warn/block

unbounded pagination
    block
```

That turns "don't let agents scrape the internet indiscriminately" into an actual resource-control primitive.

---

# 5. The wrapper catalog rule is more important than it looks

I agree with your #3, but I'd expand it into **launch contract validation**.

At worker launch, mechanically verify:

```text
model exists
provider exists
agent exists
configuration exists
required tools exist
required MCPs exist
worktree exists
issue exists
issue is claimed
execution budget exists
timeout exists
policy version exists
```

Then don't launch the worker if the contract isn't satisfied.

This is one of the cleanest examples of EDASES doing something the model fundamentally shouldn't be trusted to do.

---

# 6. Pre-flight should become a formal admission gate

Your #4 is correct, but I'd broaden it substantially.

The execution engine should have something conceptually like:

```text
ADMISSION
  ↓
identity valid
issue valid
issue claimed
worktree valid
HEAD state valid
branch valid
policy valid
model valid
budget valid
required evidence available
  ↓
RUNNING
```

The agent shouldn't get to discover halfway through execution that its preconditions weren't met.

This is a very strong fit for the state-machine architecture.

---

# 7. `>45m atomization warnings` are only partially mechanical

I would challenge the current wording.

The engine can absolutely enforce:

```text
elapsed > 45m
```

It cannot establish mechanically:

> "this task should have been atomized."

So I'd implement:

```text
45m elapsed
    → ATOMIZATION_REVIEW_REQUIRED
```

rather than:

```text
45m elapsed
    → task was incorrectly designed
```

Then the coordinator/model makes the judgment.

That same pattern applies to several items in (C).

---

# 8. Acceptance criteria are much more hookable than classified

I would move **acceptance-criteria prompts** from C into B.

You don't need the engine to determine whether criteria are *good*.

It can require:

```text
acceptance_criteria != empty
```

before admission.

It can require each criterion to have:

```text
id
description
verification method
status
evidence
```

before completion.

A model can still be responsible for determining whether the criteria themselves are sensible.

That's a textbook **mechanical gate around model judgment**.

---

# 9. "Proven pattern" is another hybrid

The engine can't determine:

> "This is genuinely the right proven pattern."

But it can require:

```text
pattern_claim
    ↓
repository reference
    ↓
specific file/symbol/commit
    ↓
evidence retrieved
```

before allowing the decision to be marked "pattern-based."

That is particularly interesting given the Crosslink Index / semantic repository work.

The model supplies the semantic claim.

EDASES verifies the evidence chain.

That is much stronger than trusting the model's statement that something is "a proven pattern."

---

# 10. Failure-response behavior should absolutely have mechanical enforcement

I would strongly challenge its placement in C.

The engine should not decide:

> halt vs report vs wait

but it **should** define which transitions are legal.

For example:

```text
RUNNING
  ├── failure → FAILED
  ├── recoverable → RETRYING
  ├── external dependency → BLOCKED
  ├── human decision → WAITING
  └── escalation → ESCALATED
```

A model can propose:

```text
"I think this is recoverable."
```

But the engine decides whether the requested transition is permitted.

And certain conditions can force transitions:

```text
invalid signature → BLOCKED
provider auth failure → BLOCKED
budget exhausted → PAUSED
worktree corruption → FAILED
permission timeout → ESCALATED
heartbeat timeout → STALLED
```

This is exactly the distinction between **reasoning about state** and **owning state**.

---

# 11. One important new capability: external orchestration is stronger than your list implies

The `prompt_async` endpoint gives the coordinator an actual control channel into a live session. Current source documents it as:

> send an async message, starting the session if needed, and return immediately. ([GitHub][4])

That enables mechanically implemented:

```text
worker event
    ↓
execution engine
    ↓
state transition
    ↓
coordinator wake
    ↓
prompt_async(coordinator, structured event)
```

So the coordinator does **not** need to continuously poll every worker.

That could significantly reduce token consumption.

However, I would not yet make this a hard architectural dependency without testing the exact version you're targeting. There have been historical `prompt_async` regressions, including cases where asynchronous prompts were accepted but not properly propagated through SSE. ([GitHub][5])

Also, there has been a nasty semantic issue where `prompt_async` could accidentally change the active agent/model when those fields were omitted. ([GitHub][6])

So the EDASES wrapper should explicitly specify the agent/model when using this as an orchestration channel, rather than relying on OpenCode defaults.

---

# 12. One caveat I would add to your "verified facts"

Your statement:

> "plugin event hook receives ALL internal events"

is correct as an API contract: the documented hook is explicitly `event(input): every bus event`. ([GitHub][1])

But I would phrase the research finding as:

> **The plugin API exposes the event bus to plugins; event payloads must be independently audited for the specific event types and identifiers required by EDASES.**

That's a more defensible architectural statement.

Likewise, don't treat "plugin hooks work" as equivalent to "plugin hooks work identically everywhere." There is a current report of Desktop v1.18.4 registering plugins but failing to invoke `event` and `tool.execute.before`, while the CLI worked. ([GitHub][7])

For an execution engine, that means **CLI/server execution should probably be the supported enforcement substrate**, unless Desktop hook parity is explicitly tested.

---

# Revised priority

I'd reorder your research/enforcement backlog like this:

### Tier 1 — execution correctness

1. **Execution/session/work-item identity binding**
2. **Provider-backoff/error state detection**
3. **Admission/pre-flight gate**
4. **Permission-wait detection**
5. **General no-progress/liveness detection**
6. **Legal state-transition enforcement**
7. **Tool-call provenance/evidence**
8. **Model/wrapper/agent launch-contract validation**

These establish the actual execution substrate.

### Tier 2 — work quality and coordination

9. **Acceptance-criteria admission/completion gates**
10. **Commit/work-item reference validation**
11. **Session-end evidence/notes**
12. **Multi-reviewer isolation**
13. **Two-repository synchronization invariants**
14. **Blind-sync prevention**
15. **Artifact hygiene**
16. **Task-duration/atomization escalation**

### Tier 3 — policy/resource controls

17. **Network acquisition budgets**
18. **Webfetch escalation**
19. **Push approval + ahead-count**
20. **Signing-key/environment revalidation**

### Tier 4 — model judgment

21. Danger rationale
22. Correct alternative
23. Tier selection
24. Timeout estimate
25. Skeleton/fidelity
26. Proven-pattern judgment
27. Decision quality
28. Failure-response choice

But several Tier-4 items should have **Tier-1/2 mechanical envelopes** around them.

---

## The architectural rule emerging from this

I think the useful formulation is no longer:

> **What can hooks enforce?**

It is:

> **What properties of an agent execution can the engine observe, what state transitions can it mechanically constrain, and where must a model supply a judgment?**

That produces three layers:

```text
                    MODEL
             semantic judgment
                    │
                    ▼
             POLICY / DECISION
        "I think this is acceptable"
                    │
                    ▼
        ┌─────────────────────────┐
        │     EXECUTION ENGINE    │
        │                         │
        │ admission               │
        │ identity                │
        │ state transitions       │
        │ budgets                 │
        │ timeouts                │
        │ permissions             │
        │ provenance              │
        │ liveness                │
        │ evidence requirements   │
        └────────────┬────────────┘
                     │
                     ▼
                  OPENCode
```

The model is allowed to **reason about what should happen**.

The execution engine is responsible for **making sure only legal things actually happen**.

That is a materially stronger framing for EDASES than the original hookability classification, and it also gives you a much cleaner way to evaluate prior art: ask whether a candidate system owns **execution state and invariants**, rather than merely whether it exposes enough hooks.

One final point: OpenCode's current plugin surface itself has some instability around `permission.ask`; the hook exists in the SDK, but current issues indicate it has had gaps between declaration and actual triggering, particularly around the newer PermissionV2 path. ([GitHub][2]) That reinforces the case for treating OpenCode hooks as an **observation/control interface**, not as the ultimate source of truth for EDASES state. The EDASES engine should own that state independently.

Жλא

[1]: https://github.com/anomalyco/opencode/blob/dev/packages/core/src/plugin/skill/customize-opencode.md?utm_source=chatgpt.com "opencode/packages/core/src/plugin/skill/customize-opencode.md at dev · anomalyco/opencode · GitHub"
[2]: https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/index.ts?utm_source=chatgpt.com "opencode/packages/plugin/src/index.ts at dev · anomalyco/opencode · GitHub"
[3]: https://github.com/anomalyco/opencode/issues/34327?utm_source=chatgpt.com "[FEATURE]: let plugins gate the auto-approve path via a permission hook in PermissionV2 · Issue #34327 · anomalyco/opencode · GitHub"
[4]: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/server/routes/instance/httpapi/groups/session.ts?utm_source=chatgpt.com "opencode/packages/opencode/src/server/routes/instance/httpapi/groups/session.ts at dev · anomalyco/opencode · GitHub"
[5]: https://github.com/anomalyco/opencode/issues/26635?utm_source=chatgpt.com "prompt_async silently discards requests in v1.14.44 (SSE path broken) · Issue #26635 · anomalyco/opencode · GitHub"
[6]: https://github.com/anomalyco/opencode/issues/21728?utm_source=chatgpt.com "Bug: prompt_async notifications override session's active agent and model · Issue #21728 · anomalyco/opencode · GitHub"
[7]: https://github.com/anomalyco/opencode/issues/38604?utm_source=chatgpt.com "Desktop app: local plugins load and register but their hooks (tool.execute.before, event) are never invoked · Issue #38604 · anomalyco/opencode · GitHub"
