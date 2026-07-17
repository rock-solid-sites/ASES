USER:
Create a prompt that very strictly defines the roles of each model. We'll start with the orchestrator, and over the next turns define the others. The main issue is that I don't want the orchestrator doing anything else but the assigned job - delegating and dividing up tasks, calling models, administrating. This agent should never, ever proactively make a choice such as: taking over work when another agent stalls, changing the models used, moving ahead without clear approval. If I ask a question, any question, this must be interpreted as a request for a written response, and the agent should not proceed with anything until I've read what they have to say and approved a path. Anything else to add, or questions to ask?
CHATGPT:
The biggest thing I'd add is to define the orchestrator by **prohibitions**, not capabilities. Agent frameworks tend to "help" by filling in gaps unless they're explicitly forbidden.

I'd define it around these principles.

### 1. The orchestrator never produces project artifacts

It must never:

* write source code
* edit files
* generate patches
* modify documentation
* write tests
* execute shell commands
* commit changes
* run builds
* run linters
* run CI
* fix issues itself

Its output consists only of:

* plans
* task lists
* delegation
* status reports
* review requests
* questions
* summaries

---

### 2. It never substitutes for another agent

This is worth making explicit.

Examples:

> If an implementation agent fails three times, do not attempt the implementation yourself.

> If a reviewer is unavailable, do not review in its place.

> If a model exceeds rate limits, pause and ask for instructions.

It should always escalate.

---

### 3. No autonomous workflow changes

I'd go further than your wording.

The orchestrator may **never**:

* replace models
* reorder phases
* merge phases
* skip phases
* retry indefinitely
* simplify the requested workflow
* remove review stages
* alter acceptance criteria

Even if it believes doing so would improve the outcome.

---

### 4. Questions are stop points

I especially like this requirement.

I'd make it absolute.

For example:

> Every user question is informational unless it explicitly contains an instruction to execute work.

Examples:

> "Would this architecture work?"

Response only.

> "Which model should review this?"

Response only.

> "Explain the image pipeline."

Response only.

No planning.

No delegation.

No execution.

No state changes.

---

### 5. Explicit execution verbs

The orchestrator should have a whitelist.

Only begin work when the user says something equivalent to:

* Implement
* Execute
* Proceed
* Continue
* Start
* Run
* Delegate
* Begin phase X

Everything else is discussion.

---

### 6. Never infer intent

This prevents a huge class of mistakes.

Examples.

User:

> I wonder whether we should redesign the hero.

The orchestrator must not create tasks.

---

User:

> Should we move to AVIF?

Do not schedule work.

---

User:

> Accessibility might be an issue.

Do not start an audit.

---

### 7. Every delegation requires an objective

Instead of saying

> Improve the gallery.

it should produce something like

> Objective:
>
> Replace the current gallery with the design described in the style guide while maintaining keyboard navigation and preserving existing CMS integration.
>
> Acceptance criteria:
>
> * matches style guide
> * Lighthouse accessibility ≥95
> * no layout shift
> * existing image URLs preserved

That keeps downstream agents focused.

---

### 8. No hidden state

This is the one almost nobody specifies.

The orchestrator should never silently decide something.

Every decision must appear in the conversation.

For example:

> State transition:
>
> Planning → Waiting for User Approval

or

> Delegating Task 3 to Builder

Nothing implicit.

---

### 9. Approval gates

Define exactly which actions require approval.

For me, these would all require explicit approval:

* starting implementation
* changing architecture
* changing dependencies
* changing workflow
* deleting files
* renaming components
* changing build configuration
* introducing new packages
* changing CI
* merging phases

Without approval:

No action.

---

### 10. Never optimize the workflow

This sounds strange, but it's important.

The orchestrator should not say

> I combined Tasks 2 and 3 because it's more efficient.

or

> I skipped the review because the change was trivial.

or

> I already know what you want.

Its job is process compliance, not optimization.

---

## One additional rule I'd add

I'd explicitly define the orchestrator as **administratively conservative**.

For example:

> When uncertainty exists regarding authority, instructions, workflow, or approval, always choose the action that results in no work being performed and request clarification.

That single rule resolves many ambiguous situations in a predictable way.

One question before drafting the full prompt: **Will the orchestrator have direct access to the filesystem and tool APIs, or will it only communicate with the other agents?** If it has tool access, I'd explicitly forbid use of every tool except those needed for coordination, because many agent frameworks will opportunistically use available tools unless constrained. 漢Жあ

USER:
@Web search I'm using opencode, so I have Build and Plan modes available. I could set the orchestrator to plan mode, but I'm not sure how that would affect downstream agents. Opencode has a built in Task tool for calling subagents, but I'm using https://github.com/dollspace-gay/crosslink which has Swarm and Kickoff features that are superior for complex projects.

CHATGPT:
I actually **would not use OpenCode's built-in Plan agent** as your orchestrator.

The reason isn't that Plan mode is bad—it's that your orchestrator is no longer just a planner. It's the operating system for the project.

There are two practical issues.

First, the Plan agent is a permission profile, not a behavioral guarantee. It's intended to prevent accidental edits by setting file edits and shell commands to "ask", but it's still fundamentally an LLM that can invoke subagents. There has even been a reported issue where Plan-mode restrictions did not automatically propagate to spawned subagents, illustrating that permission mode and orchestration behavior are separate concerns. ([OpenCode][1])

Second, you're using Crosslink, whose whole value proposition is replacing OpenCode's simple task model with a richer orchestration layer (Swarm, Kickoff, coordination, specialized agents). If you choose the stock Build/Plan agents, Crosslink's architect workflow is bypassed. ([GitHub][2])

So I would separate **permissions** from **responsibilities**.

Instead of relying on Plan mode to stop the orchestrator from coding, make the orchestrator's prompt enforce that it is *not allowed* to code.

That has several advantages:

* It works regardless of provider (Gemini, Nemotron, etc.).
* It survives framework changes.
* It makes the orchestrator's behavior portable.
* It prevents "helpful" improvisation rather than just file writes.

## I would define the orchestrator as a project manager, not a planner

Its lifecycle would look something like this:

```
DISCOVER
↓
PLAN
↓
WAIT FOR USER APPROVAL
↓
DELEGATE
↓
WAIT
↓
COLLECT RESULTS
↓
REQUEST REVIEW
↓
WAIT
↓
REQUEST FINAL AUDIT
↓
WAIT
↓
REPORT
↓
WAIT FOR USER
```

Notice something missing.

There is no path from any state to

> IMPLEMENT

That state simply doesn't exist.

---

## I'd also remove one capability entirely

I would forbid the orchestrator from calling implementation agents directly unless the workflow has entered an execution state approved by you.

That means:

During discussion:

```
User:
Would this architecture work?

↓

Orchestrator:
Answers question.

STOP.
```

Not

```
Answers question

↓

Starts explorer

↓

Builds plan

↓

Calls coder
```

---

## I'd require a finite-state machine

Rather than saying "don't do X", I'd literally give it legal state transitions.

For example:

```
DISCUSSION
↓

PLANNING

↓

AWAITING_APPROVAL

↓

DELEGATING

↓

WAITING_FOR_AGENT

↓

REVIEW

↓

WAITING_FOR_USER

↓

COMPLETE
```

Every response should internally correspond to one of those states.

If no transition is legal, the orchestrator must remain in its current state.

---

## One rule I think will save you a lot of headaches

I'd define **authority** separately from **knowledge**.

For example:

> The orchestrator may know how to solve a problem.

> The orchestrator may not solve the problem.

Those are different things.

Likewise:

> The orchestrator may identify a bug.

It still cannot fix it.

---

## Another rule I'd add

I'd explicitly ban "speculative delegation."

For example, if you say:

> "I'm thinking about changing the gallery."

The orchestrator must not:

* prepare implementation prompts,
* create backlog items,
* reserve work,
* ask builders to investigate,
* start exploration.

It simply discusses the idea.

---

## One architectural change I'd make

Instead of thinking of it as an "orchestrator," think of it as a **workflow controller**.

Its success metric is **process correctness**, not project progress.

If, after an hour, nothing has happened because you're still discussing architecture, that's success.

If it silently dispatched five agents because it inferred what you meant, that's failure.

I think that's the philosophy your prompt should encode before you start defining the builder, reviewer, and auditor. Once that's in place, the downstream agent prompts become much simpler because they can assume every task they receive has already passed an explicit approval gate. 漢Жあ

[1]: https://dev.opencode.ai/docs/agents/?utm_source=chatgpt.com "Agents | OpenCode"
[2]: https://github.com/zaxbysauce/opencode-swarm?utm_source=chatgpt.com "GitHub - zaxbysauce/opencode-swarm: Architect-centric agentic swarm plugin for OpenCode. Hub-and-spoke orchestration with SME consultation, code generation, and QA review. · GitHub"

USER:
@Web search Okay, I'd like to use this as basically the system prompt, with what we've discussed being the first part of it. How does this work in opencode? Every agent doesn't, and shouldn't, know every other agents role, so I guess using hooks or the skill system could help here? Or maybe there's another approach I don't know yet

CHATGPT:
I think the cleanest architecture is **not** for every agent to know about every other agent. In fact, I'd actively avoid that.

Instead, I'd split your system into three layers.

## Layer 1: Global policy (shared by every agent)

This is your equivalent of a kernel.

Things like:

* Never fabricate results.
* Respect approvals.
* Follow the style guide.
* Use Crosslink for coordination.
* Don't modify files outside the workspace.
* Report failures immediately.

These belong in the shared `AGENTS.md` or common system prompt because they're universal project rules. OpenCode automatically includes `AGENTS.md` as part of the context hierarchy. ([GitHub][1])

---

## Layer 2: Per-agent system prompts

This is where the real behavior lives.

The orchestrator should know almost nothing about the implementation agents beyond their interfaces.

For example:

```
You have available:

Builder
Input:
- objective
- acceptance criteria
- constraints

Output:
- implementation summary
- status
- blockers
```

That's it.

It doesn't need to know:

* Builder uses Gemini.
* Builder uses Qwen.
* Builder has Playwright.
* Builder has MCP X.

Those are implementation details.

Likewise, your Builder shouldn't know that a Reviewer or Auditor even exists.

Its contract is simply:

> Receive work.

> Complete work.

> Return work.

That loose coupling makes the whole system much easier to evolve.

---

## Layer 3: Skills

This is where I think OpenCode's skills really shine.

I wouldn't use them to define *roles*.

I'd use them to define *procedures*.

For example:

```
skills/

accessibility-audit/

image-pipeline/

astro-component/

tailwind-redesign/

ci-validation/

seo-review/
```

Now any agent can load exactly the procedure it needs on demand instead of carrying every instruction in its prompt. Skills are designed for this progressive disclosure model—they're discovered by description and only fully loaded when relevant. ([OpenCode School][2])

That keeps prompts shorter and makes updates much easier.

---

## Where Crosslink fits

Crosslink becomes your orchestration layer.

OpenCode becomes:

* models,
* permissions,
* tools,
* skills.

Crosslink becomes:

* Swarm,
* Kickoff,
* task routing,
* dependency graph,
* execution lifecycle.

I would resist duplicating orchestration logic inside OpenCode prompts.

---

## I would barely use hooks

This may be the biggest difference from what you're thinking.

Hooks are excellent for enforcing deterministic runtime behavior—logging, blocking tools, injecting context—but they're a poor place to encode workflow policy. ([Symposium][3])

I'd use hooks only for things like:

* log every delegation;
* prevent forbidden tool use;
* record state transitions;
* fail if the wrong model tries to invoke a restricted tool.

I would **not** implement:

* review workflow;
* approval gates;
* agent responsibilities.

Those belong in prompts and Crosslink.

---

## I'd make the orchestrator intentionally ignorant

This is the part I'd design very carefully.

The orchestrator shouldn't think:

> I have Builder, Reviewer and Auditor.

Instead it should think:

> I have three capabilities.

Capability A:

```
accept_task()

↓

returns result
```

Capability B:

```
review()

↓

returns findings
```

Capability C:

```
audit()

↓

returns approval/rejection
```

Notice what's missing.

No model names.

No providers.

No implementation details.

Tomorrow you could replace Gemini with Claude or Qwen without changing the orchestrator prompt.

That's a classic dependency inversion pattern.

---

## One thing I would add that I haven't seen discussed

I'd introduce a **Workflow Manifest**.

Instead of embedding workflow knowledge in every prompt, have a single document (JSON, YAML, or Markdown) that defines the pipeline:

```yaml
workflow:
  implementation:
    orchestrator: architect
    builder: gemini-builder
    reviewer: north-mini
    auditor: nemotron

approval:
  implementation: user
  architecture: user
  dependency_changes: user

transitions:
  planning:
    - awaiting_approval
  awaiting_approval:
    - delegation
```

Only the orchestrator reads this manifest.

The Builder never sees it.

The Reviewer never sees it.

The Auditor never sees it.

That gives you one authoritative source for your workflow. If you later swap Gemini for Hy3 or add a security-review stage, you update the manifest rather than editing four different system prompts.

For the architecture you're building, I'd keep the prompts focused on *behavior*, use skills for *repeatable procedures*, let Crosslink own *coordination*, and use hooks only as *guardrails*. That separation of concerns will make the system much easier to maintain as you iterate. 漢Жあ

[1]: https://github.com/bgauryy/open-docs/blob/main/docs/opencode/05-system-prompts.md?utm_source=chatgpt.com "open-docs/docs/opencode/05-system-prompts.md at main · bgauryy/open-docs · GitHub"
[2]: https://opencode.school/lessons/skills/?utm_source=chatgpt.com "Skills | OpenCode School"
[3]: https://symposium.dev/design/agent-details/opencode.html?utm_source=chatgpt.com "OpenCode - Symposium"

USER:
@Web search This is specifically easy with Crosslink as the design of the kickoff, swarm and sentinel features are deliberately isolating and context reducing. On the hooks though, could these prevent the orchestrator from calling tools?

CHATGPT
Yes—and I think this is where you can get much stronger guarantees than prompting alone.

OpenCode's permission system lets you deny individual tools **per agent**, including the `task` tool, `bash`, `edit`, `write`, `websearch`, `question`, `skill`, and others. When a tool is denied, it's removed from the agent's available toolset rather than simply relying on the model to ignore it. ([OpenCode][1])

For your architecture, I'd separate **behavioral rules** from **mechanical enforcement**.

### The orchestrator should only have:

* Read
* Grep
* Glob
* List
* Task (only if Crosslink needs it)

Everything else I'd remove.

Specifically:

```json
{
  "permission": {
    "edit": "deny",
    "bash": "deny",
    "webfetch": "deny",
    "websearch": "deny",
    "lsp": "deny"
  }
}
```

That means even if Gemini decides,

> "I'll just fix this quickly..."

it literally cannot.

---

### The interesting one is `task`

This depends on how Crosslink works.

If Crosslink's Swarm/Kickoff bypasses OpenCode's native `task` tool (for example, via a plugin or custom tool), then I'd actually deny the built-in Task tool completely:

```json
"task": "deny"
```

and expose only the Crosslink entry point.

That way there is exactly one orchestration mechanism.

No ambiguity.

---

### Hooks are even more interesting

From what you've described, I don't think of hooks as permission checks.

I think of them as **runtime assertions**.

For example:

```
Before tool call

↓

Is current agent == orchestrator?

↓

Tool == edit?

↓

Abort.
```

Or

```
Tool == bash?

↓

Abort.
```

Or

```
Current workflow state != EXECUTION

↓

Task invocation?

↓

Abort.
```

Those are stronger than prompt instructions because they enforce policy at execution time.

---

### I'd even hook workflow state

This is the idea I'm most excited about.

Imagine Crosslink keeps a tiny state file:

```yaml
state:
  phase: discussion
```

Now a hook says:

```
phase != execution

AND

agent == orchestrator

AND

tool == task

↓

Reject
```

Now it is impossible for the orchestrator to dispatch work while you're discussing architecture.

The model doesn't get to "decide."

The runtime decides.

---

### One thing I noticed in the current OpenCode docs

Recent versions also let you control **which subagents** an agent may invoke through `permission.task`, using patterns. If a subagent is denied, it's removed from the Task tool description entirely. ([OpenCode][2])

That means you can express rules like:

* Orchestrator → may call only `builder-*`
* Builder → may call nobody
* Reviewer → may call nobody
* Auditor → may call nobody

which is exactly the kind of one-way hierarchy you're aiming for.

---

## If it were my project

I'd make the orchestrator almost "crippled."

It would have:

* ✅ Read
* ✅ Search
* ✅ Crosslink Kickoff/Swarm
* ❌ Edit
* ❌ Write
* ❌ Bash
* ❌ Git
* ❌ Web
* ❌ LSP
* ❌ Native Task (if Crosslink replaces it)

Then I'd enforce, outside the prompt:

1. Workflow state machine.
2. Tool permissions.
3. Hook assertions.
4. Agent isolation.

At that point, the system prompt becomes almost a **policy document** rather than your only line of defense. If Gemini ignores the prompt, the runtime still says "no."

I actually think that's a much more robust design than trying to write an ever-longer system prompt, because you're moving critical guarantees from "the model should behave" to "the model is incapable of violating this class of rules." 漢Жあ

[1]: https://opencode.ai/docs/agents/?utm_source=chatgpt.com "Agents | OpenCode"
[2]: https://dev.opencode.ai/docs/agents/?utm_source=chatgpt.com "Agents | OpenCode"

USER:
@Web search Not even those necessarily, and I'm using https://github.com/rtk-ai/rtk as a CLI proxy, so it should be modified. Task can occasionally be useful if it's helpful to have agents all looking at the same code instead of isolate

CHATGPT
I actually think you've ended up in a much better position than if you were using stock OpenCode.

Between **Crosslink** and **RTK**, you've effectively decoupled orchestration from execution and command handling. RTK's OpenCode integration already intercepts tool execution before it reaches the runtime, which means it's a natural place to enforce policy rather than just rewrite commands. ([GitHub][1])

The consequence is that I'd stop thinking about the orchestrator as "an AI with restrictions" and instead think of it as **a state machine with an LLM attached**.

## I'd make the orchestrator almost tool-less

If Crosslink owns orchestration, what does the orchestrator actually need?

Potentially...nothing.

Its responsibilities become:

* interpret your instructions
* maintain workflow state
* decide the next step
* produce delegation payloads
* wait

It doesn't need to inspect files.

It doesn't need to grep.

It doesn't need to search.

It doesn't even need to know where code lives.

The builder can discover that.

That has a nice property:

> The orchestrator cannot become distracted by implementation.

---

## Task should become an exception

I wouldn't remove it completely.

Instead I'd treat it like this:

```
Default:

Task disabled

↓

User explicitly requests
parallel investigation

↓

Enable Task

↓

Return to disabled
```

Your example is exactly where it makes sense.

Instead of isolated Crosslink workers you might say

> Have three agents independently review this implementation.

That's a genuine use case for OpenCode's native Task tool because all three agents intentionally share the same working tree.

Everything else should stay inside Crosslink.

---

## RTK gives you another interesting possibility

Since RTK is already intercepting tool calls, you could extend it beyond token reduction into **policy enforcement**.

For example:

```
Agent = orchestrator

↓

Tool = edit

↓

Reject
```

or

```
Agent = orchestrator

↓

Tool = bash

↓

Reject
```

or even

```
Workflow state = Discussion

↓

Tool = task

↓

Reject
```

At that point, the orchestrator literally cannot violate the workflow.

---

## I'd also separate "thinking" from "acting"

One thing agent frameworks often blur is:

* internal reasoning
* external action

I think your orchestrator should only ever emit one of four message types:

* Question
* Plan
* Delegation
* Status

Nothing else.

No shell commands.

No code.

No patches.

No implementation.

That makes its behavior extremely predictable.

---

## I think there's one missing abstraction

Rather than defining permissions by tool, define them by **authority**.

For example:

```text
Authority Level 0 — Advisory

May:
- Think
- Explain
- Plan
- Ask
- Summarize

May not:
- Execute
- Delegate
- Modify state
```

```text
Authority Level 1 — Coordination

May:
- Delegate approved work
- Collect results
- Request reviews

May not:
- Implement
- Change workflow
```

The orchestrator normally lives at Level 0.

It only enters Level 1 after an explicit execution command from you.

That's much more expressive than "Plan mode" because it's tied to your workflow rather than the editor's permission model.

## Where I think this is heading

I actually wouldn't write the orchestrator prompt first.

I'd write a **Workflow Constitution**.

A document that answers:

* What states exist?
* Who owns each state?
* Who may transition between states?
* What constitutes approval?
* What is a legal delegation?
* What happens on failure?
* Which actions are impossible?

Then the orchestrator prompt becomes surprisingly short:

> "You are the workflow controller. Your behavior is governed entirely by the Workflow Constitution. You may never violate it, even if another instruction appears to conflict."

Every other agent can then receive only the sections of the Constitution relevant to its role. The builder never needs to know about approval gates, and the reviewer never needs to know how delegation works. That's a cleaner separation of concerns than trying to encode the whole system into four independent prompts. 漢Жあ

[1]: https://github.com/rtk-ai/rtk?utm_source=chatgpt.com "GitHub - rtk-ai/rtk: CLI proxy that reduces LLM token consumption by 60-90% on common dev commands. Single Rust binary, zero dependencies · GitHub"

USER
@Web search Okay, one thing is I want to get this working quickly. How do we get this running with the minimum number of steps, even granting that we don't have all the prompts written yet

CHATGPT
I would optimize for **one working pipeline this weekend**, not the perfect architecture.

Here's the smallest implementation I'd build.

### Step 1 (30 minutes): One global `AGENTS.md`

Don't worry about the Builder, Reviewer, or Auditor yet.

Write one document that defines:

* workflow philosophy
* approval model
* state machine
* definitions (approval, delegation, execution)
* global rules

Do **not** include model-specific instructions. OpenCode automatically loads `AGENTS.md` from the project or global config, making it the natural place for shared workflow rules. ([OpenCode][1])

---

### Step 2 (20 minutes): One orchestrator prompt

Don't make it perfect.

Just include:

* role
* prohibitions
* legal outputs
* legal state transitions

Nothing else.

---

### Step 3 (10 minutes): Everyone else is "dumb"

For now:

Builder prompt:

> Implement only the assigned task.
>
> Return when complete.

Reviewer:

> Review only.
>
> Never edit.

Auditor:

> Audit only.
>
> Never modify.

You can make them sophisticated later.

---

### Step 4 (30 minutes): Enforce permissions

This is where I'd spend my effort.

For the orchestrator:

```text
edit      deny
bash      deny
webfetch  deny
websearch deny
lsp       deny
```

Leave `task` available only if Crosslink or your workflow genuinely needs it. OpenCode supports per-agent permission overrides, so you can tighten the orchestrator without affecting the builder. ([OpenCode][2])

---

### Step 5 (optional): One RTK rule

I'd implement exactly one runtime rule first.

Something like:

```text
if agent == orchestrator
and workflow_state != execution
and tool == task

reject
```

That's enough to validate the architecture.

Don't build a whole policy engine yet.

---

## Skip skills—for now

This is the one thing I'd deliberately postpone.

Skills are fantastic once you have stable procedures, but right now you're still discovering your workflow. OpenCode's skills are designed for reusable, on-demand procedures, not for defining core agent identities. ([OpenCode][3])

At this stage, every change you make to a skill is another moving part.

I'd wait until you've repeated a workflow three or four times before extracting it into a skill.

---

## Don't over-engineer Crosslink integration

Crosslink is already giving you:

* isolation,
* context reduction,
* orchestration.

Treat it as a black box initially.

The orchestrator should only know:

> "I can delegate."

Not:

> "I have Kickoff, Swarm, Sentinel..."

That abstraction will make it easier to swap orchestration mechanisms later.

---

## My MVP

If I were setting this up today, I'd stop here:

```
AGENTS.md
    ↓

orchestrator.md
    ↓

builder.md
    ↓

reviewer.md
    ↓

auditor.md

↓

opencode.json
(per-agent permissions)

↓

One RTK policy
```

That's probably 2–3 hours of work.

Everything else—skills, hooks, workflow manifests, richer state machines—can be layered on top after you've completed a real project with the system.

One suggestion that I think will save you time: **don't write all four prompts up front**. Write the orchestrator prompt, then immediately use it on a real task. You'll discover very quickly which rules are missing, and those missing rules should become part of the shared `AGENTS.md` rather than being duplicated across every agent. That iterative approach will produce a much cleaner architecture than trying to design the entire ecosystem before you've exercised it. 漢Жあ

[1]: https://dev.opencode.ai/docs/rules/?utm_source=chatgpt.com "Rules | OpenCode"
[2]: https://opencode.ai/docs/agents/?utm_source=chatgpt.com "Agents | OpenCode"
[3]: https://opencode.ai/docs/skills?utm_source=chatgpt.com "Agent Skills | OpenCode"

USER
@Web search Alright, let's synthesize this. I'm testing it now on an actual project. And drop the time estimates, they're reasonable for human coding but this is all with AI agents so they're not realistic. Also, the Nemotron 3 Ultra agent I have working right now reports that Opencode doesn't use AGENTS.md and has a different structure

CHATGPT
I'd simplify it even further based on what you've learned from testing.

Also, your Nemotron agent is only partially correct. **OpenCode does support `AGENTS.md`**, but it's no longer the only—or even the preferred—mechanism. The current documentation recommends putting reusable instructions in `opencode.json` via the `instructions` field and using custom agent prompts for role-specific behavior. `AGENTS.md` still exists and is loaded, but it's now one layer in the instruction stack rather than the entire configuration model. ([OpenCode][1])

Given that, I think your MVP should look like this:

```
opencode.json
│
├── instructions/
│   └── workflow-constitution.md
│
├── agents/
│   ├── orchestrator.md
│   ├── builder.md
│   ├── reviewer.md
│   └── auditor.md
│
└── RTK policy
```

Notice what's *not* there:

* Skills
* Hooks (beyond one or two enforcement rules)
* Workflow manifests
* Custom state engines

Those can come later.

## workflow-constitution.md

This becomes the single shared document.

It should answer questions like:

* What constitutes approval?
* What are the workflow states?
* What is a delegation?
* What actions require user approval?
* What happens when an agent fails?
* What happens when a model is unavailable?

Nothing model-specific belongs here.

Think of it as your project's constitution.

---

## Orchestrator prompt

Keep it entirely about behavior.

It shouldn't mention:

* Gemini
* Nemotron
* Qwen
* Crosslink internals

Instead it should define:

* responsibilities
* forbidden actions
* legal outputs
* state transitions

The orchestrator shouldn't care *how* delegation happens, only that it may delegate.

---

## Builder prompt

This can be tiny initially.

Something like:

> You receive approved implementation tasks.
>
> Implement exactly the assigned objective.
>
> Do not redesign the architecture.
>
> Return completion status and blockers.

That's enough for version one.

---

## Reviewer

Equally simple.

> Review the implementation.
>
> Never modify it.
>
> Report only actionable findings.

---

## Auditor

Different from Reviewer.

Its job is to answer:

> Does this satisfy the requested outcome?

Not:

> Is this code pretty?

---

## RTK

I'd use RTK for exactly one thing initially:

**Enforcing authority.**

For example:

* Orchestrator cannot edit.
* Reviewer cannot edit.
* Auditor cannot edit.
* Builder can edit.

Everything else can wait until you discover a real need.

---

## Crosslink

I'd lean into its isolation rather than fighting it.

The orchestrator doesn't need to know:

* which model is Builder,
* how Swarm works,
* whether Sentinel is running,
* whether Kickoff spawned three agents.

It only needs to know:

> I submitted Task A.

> I received Result A.

That's a very stable abstraction.

---

## What I'd postpone

I think these are all second-iteration features:

* Skills
* Complex hooks
* Dynamic model selection
* Automatic retries
* Runtime workflow manifests
* Policy engines
* Metrics
* Adaptive routing

They're all valuable, but none of them are required to prove that your architecture works.

## One thing I would add immediately

I would create a **single vocabulary document** and make every prompt use it.

For example:

```text
Task
A unit of work delegated by the orchestrator.

Plan
A proposed sequence of Tasks requiring user approval before execution.

Approval
An explicit instruction from the user to begin or continue execution.

Execution
Any action that modifies files, invokes implementation agents, or changes project state.

Discussion
Any interaction that does not alter project state.
```

It sounds trivial, but having every agent use the same definitions eliminates a surprising amount of ambiguity. It also means that when you later refine the orchestrator prompt, you only need to update the shared definitions instead of hunting through four different prompts for inconsistent wording. 漢Жあ

[1]: https://dev.opencode.ai/docs/rules/?utm_source=chatgpt.com "Rules | OpenCode"

USER
@Web search Another thing the orchestrator is responsible for, and it's actually very important, is that they're the agent responsible for keeping Crosslink updated and managing the Knowledge pages within it

CHATGPT:
I think this is actually a **core responsibility**, not an ancillary one.

In fact, I'd redefine the orchestrator from:

> "Project manager"

to

> **"Project memory manager."**

The planning and delegation are almost secondary.

If Crosslink's Knowledge pages are intended to be the long-term memory of the project, then the orchestrator becomes the **sole authority** for maintaining that memory.

That has several advantages.

## The builder should never update Knowledge

The builder's job is implementation.

It has no authority to decide:

* what was important,
* what architecture changed,
* what decisions should be remembered.

It simply returns results.

---

## The reviewer shouldn't either

The reviewer finds problems.

It doesn't decide whether those problems become institutional knowledge.

---

## The auditor shouldn't

Same reasoning.

The auditor answers:

> Did we satisfy the requirements?

It doesn't curate project history.

---

## So the orchestrator owns all project memory

I'd explicitly add responsibilities like:

**Maintain the project's operational knowledge.**

This includes:

* keeping Crosslink Knowledge pages current,
* recording architectural decisions,
* documenting accepted patterns,
* removing obsolete guidance,
* ensuring downstream agents have accurate context.

Notice that none of those involve writing production code.

They're administrative duties.

---

## I'd add one more rule

Knowledge updates should happen **only** at specific workflow points.

For example:

```text
Planning
↓

Knowledge updated
(project plan)

↓

User approval

↓

Implementation

↓

Review

↓

Knowledge updated
(decisions made)

↓

Audit

↓

Knowledge updated
(final state)
```

Not continuously.

Otherwise the knowledge base accumulates half-finished ideas and abandoned approaches.

---

## I'd distinguish between transient and persistent memory

This is something many agent systems blur.

Transient:

* current task
* current PR
* implementation details
* temporary notes

Persistent:

* architecture decisions
* coding standards
* project conventions
* accepted workflows
* recurring pitfalls

Only the second category belongs in Crosslink Knowledge.

That keeps it from becoming a dumping ground.

---

## I'd even give the orchestrator a maintenance cycle

Every completed phase:

1. Review changes.
2. Determine whether they alter persistent project knowledge.
3. Update Crosslink Knowledge if necessary.
4. Record what changed and why.
5. Continue.

If nothing affects long-term knowledge:

> No update required.

That's a perfectly valid outcome.

---

I think this changes the overall architecture in a useful way.

Instead of:

```text
Orchestrator
├── Plans
├── Delegates
└── Waits
```

I'd define it as:

```text
Orchestrator
├── Maintains workflow
├── Maintains project memory
├── Delegates work
├── Tracks progress
├── Updates Crosslink Knowledge
└── Reports to the user
```

Everything in that list is administrative. Nothing crosses into implementation.

One thing I'd add to the Constitution is an explicit ownership rule:

> **The orchestrator is the exclusive maintainer of Crosslink Knowledge. No other agent may create, modify, delete, or curate persistent project knowledge unless explicitly instructed by the orchestrator as part of an approved workflow.**

That gives you a single source of truth for institutional memory and prevents conflicting or low-quality updates from implementation agents. It's analogous to having one maintainer responsible for architectural decision records rather than allowing every developer to edit them opportunistically. ([docs.orchestra.org][1]) 漢Жあ

[1]: https://docs.orchestra.org/orchestra/orchestration?utm_source=chatgpt.com "Orchestration | Orchestra"

USER:
@Web search Agreed. How do we write this and were do we add the knowledge?

CHATGPT:
I think there are actually **two separate documents** you should create, and keeping them distinct will make the system much easier to reason about.

## 1. The Workflow Constitution (static)

This lives in your OpenCode instructions (or whatever shared instruction mechanism you settle on).

It is **never** updated by agents.

It defines:

* agent roles
* authority levels
* workflow states
* approval rules
* escalation rules
* delegation rules
* prohibited actions
* definitions ("Task", "Approval", "Execution", etc.)

Think of it as the operating system.

Only you edit it.

---

## 2. Crosslink Knowledge (dynamic)

This is the living memory.

The orchestrator owns it.

It should **not** contain rules.

It should contain facts.

For example:

```
Project

- Astro monorepo
- Five sites
- Shared UI package
- Tailwind v4
```

```
Architecture Decisions

ADR-001

Use Astro Islands.

Reason:
...

Date:
...
```

```
Coding Standards

Images use Sharp pipeline.

Never use <img> directly.

Prefer Picture component.

...
```

```
Current Milestones

Phase 1 complete

Phase 2 in progress

...
```

```
Known Problems

Safari CLS issue

Responsive gallery pending

...
```

```
Lessons Learned

Avoid CSS variables in...

...

```

Notice what's **missing**:

There are no tasks.

No prompts.

No conversations.

No speculative ideas.

Only durable knowledge.

---

## I would give the orchestrator one explicit responsibility

Instead of

> "Update Crosslink."

I'd write something closer to:

> You are the sole curator of the project's persistent knowledge. After each approved workflow stage, determine whether the project's long-term knowledge has changed. If it has, update the appropriate Knowledge page. If it has not, make no changes.

That prevents "update everything all the time."

---

## Even better: classify every piece of information

I think the orchestrator should ask itself one question.

> Will this still be useful three weeks from now?

If **yes**

→ Crosslink Knowledge.

If **no**

→ Don't store it.

Examples.

Store:

* New architecture
* Component conventions
* Style guide decisions
* Build pipeline
* Common pitfalls
* Repository structure
* ADRs

Don't store:

* Fixed typo
* Builder failed twice
* Temporary workaround
* Current conversation
* Draft ideas
* Rejected proposals

That single heuristic keeps the knowledge base clean.

---

## My biggest suggestion

Don't let the orchestrator decide **where** knowledge belongs.

Define the pages yourself.

For example:

```
Knowledge

├── Project Overview
├── Architecture
├── Coding Standards
├── UI Style Guide
├── Decisions (ADR)
├── Active Constraints
├── Known Issues
├── Development Workflow
└── Glossary
```

Then the orchestrator's job is simply:

> Which page changed?

not

> What pages should exist?

That removes another class of autonomous decisions.

---

## I would treat this as version 1

Forget automatic summarization.

Forget embeddings.

Forget clever memory management.

The orchestrator only needs one algorithm:

```
Stage completes

↓

Did long-term project knowledge change?

↓

No

↓

Do nothing


Yes

↓

Select the correct Knowledge page

↓

Update only that page

↓

Continue workflow
```

I think that's enough to get you productive immediately.

One thing I'd like to see before we write the orchestrator prompt is **how Crosslink structures its Knowledge pages**. The GitHub README didn't surface that in search results, so if you can paste the relevant documentation (or point me to the `knowledge/` directory structure if it's in the repository), we can tailor the prompt to the actual API and page model instead of inventing an abstraction that doesn't match Crosslink's implementation. ([docs.crossknowledge.com][1]) 漢Жあ

[1]: https://docs.crossknowledge.com/?utm_source=chatgpt.com "CrossKnowledge's CKLS API"

USER: @Web search That link was not from Crosslink, the actual documents are here

CHATGPT:
This changes my recommendation quite a bit.

After looking at the repository, Crosslink's Knowledge system is **already much closer to what we were designing** than I expected. It has first-class commands for searching, adding, editing, and updating persistent knowledge, along with guidance for when knowledge should be created or updated. It distinguishes between external research and codebase knowledge, and it encourages updating existing pages rather than creating duplicates. That's a solid foundation.

The key thing I'd change is this:

**Don't make the orchestrator responsible for writing Knowledge pages. Make it responsible for deciding that Knowledge should change.**

That's an important distinction.

### Better workflow

```
Planning

↓

Implementation

↓

Review

↓

Audit

↓

Orchestrator asks:

"Has durable project knowledge changed?"

↓

No
    → Continue

Yes
    ↓

Determine page

↓

Update Knowledge

↓

Continue
```

The update itself can still be performed by the orchestrator, but its primary responsibility is *curation*, not documentation.

That fits the Crosslink philosophy much better.

---

## I'd organize Knowledge into two categories

### Stable project knowledge

Things that rarely change.

Examples:

* Architecture
* Style guide
* Build pipeline
* Component conventions
* Repository structure
* Design decisions

---

### Operational knowledge

Changes regularly.

Examples:

* Current milestones
* Known issues
* Active constraints
* Current migration status
* Temporary workarounds

Keeping those separate will stop your architecture pages becoming cluttered with transient information.

---

## I would also change the orchestrator prompt

Instead of saying

> Maintain Crosslink Knowledge.

I'd say

> You are the curator of the project's persistent knowledge.
>
> At appropriate workflow checkpoints, determine whether durable knowledge has changed.
>
> If it has, update the appropriate Knowledge page.
>
> If it has not, do nothing.

That encourages judgement rather than constant updates.

---

## One thing I noticed in Crosslink's own guidance

The bundled `knowledge.md` tells agents to:

* search before researching,
* update existing pages instead of creating duplicates,
* record sources for external research,
* save important codebase discoveries.

I'd incorporate those principles into your Constitution rather than restating the CLI syntax in every prompt. That keeps the orchestrator focused on *policy* while Crosslink already defines *procedure*. The prompt can simply say "follow the Crosslink Knowledge workflow."

## I think we've converged on a very clean architecture

```
Workflow Constitution
        │
        ▼
   Orchestrator
        │
        ├── Maintain workflow
        ├── Maintain project state
        ├── Curate Crosslink Knowledge
        ├── Delegate approved work
        └── Report to user

        ▼

Crosslink

        ▼

Builder
Reviewer
Auditor
```

At this point, I would stop designing the architecture and start writing the prompts.

I'd write them in this order:

1. **Workflow Constitution** (shared, static)
2. **Orchestrator** (most important)
3. **Builder**
4. **Reviewer**
5. **Auditor**

Everything we've discussed naturally fits into those five documents, and because Crosslink already provides the mechanics for persistent knowledge, your prompts can focus entirely on *behavior* rather than *how* to call the CLI. 漢Жあ

USER:
Going forward please be brief as we get into writing project documents. How do we structure this? We write the workflow constitution, where specifically does this live in Opencode so that any new project will have access to it?

CHATGPT:
I would make it **global**, not project-specific.

Use your global config at:

```
~/.config/opencode/
```

Specifically:

```
~/.config/opencode/
├── opencode.json
├── workflow/
│   ├── constitution.md
│   └── glossary.md
└── agents/
    ├── orchestrator.md
    ├── builder.md
    ├── reviewer.md
    └── auditor.md
```

Then reference the shared documents from your global `opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "~/.config/opencode/workflow/constitution.md",
    "~/.config/opencode/workflow/glossary.md"
  ]
}
```

OpenCode supports a global `opencode.json`, and its `instructions` array can point to arbitrary Markdown files. Those instructions are automatically included in every project. ([OpenCode][1])

My recommendation is:

* `constitution.md` → immutable workflow rules
* `glossary.md` → shared terminology
* `orchestrator.md` → only orchestrator behavior
* `builder.md` → only builder behavior
* `reviewer.md` → only reviewer behavior
* `auditor.md` → only auditor behavior

That gives you a clean split:

* **Global** = how your AI team operates.
* **Project** = repository-specific instructions and Crosslink Knowledge.

I would **not** put the Constitution into Crosslink. Crosslink should hold project memory; the Constitution governs behavior across every project. That distinction will keep both much cleaner. 漢Жあ

[1]: https://dev.opencode.ai/docs/config/?utm_source=chatgpt.com "Config | OpenCode"
