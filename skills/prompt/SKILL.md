---
name: compact-prompt
version: 0.1-draft
description: Construct compact agent prompts for ASES/T3 workflows. Use when preparing fresh-context prompts for orchestrators, builders, recon/verification agents, reviewers, ontology reviewers, or synthesis agents. Select only task-specific instructions, run-specific policy, relevant context, and an observable completion condition; omit project knowledge and restrictions already supplied or enforced elsewhere.
---

# Compact Prompt Skill

## Purpose

Compile small, high-signal prompts for agents working in the current T3/Crosslink workflow. The skill reduces both token cost and semantic footprint: it should avoid introducing concepts the receiving agent does not need to reason about.

This skill does not own project architecture, ontology, role authority, model inventory, or execution policy. It selects from those sources and expresses only the task delta needed by the receiving agent.

## Core rule

Put stable meaning in canonical project knowledge, stable procedure in skills/roles, run-specific policy in the fresh orchestrator prompt, and only task-specific differences in the task prompt.

A short prompt is useful only when omitted information is either:
- already mechanically enforced;
- discoverable through the agent's allowed tools/context; or
- supplied as selected project context.

## Inputs

Before writing, identify:

- **operation**: what kind of reasoning/action is requested;
- **target**: artifact, diff, issue, subsystem, claim, or objective;
- **receiver**: orchestrator, worker, reviewer, ontology reviewer, synthesizer, etc.;
- **run policy**: facts that vary for this invocation, especially model/delegation policy;
- **context sources**: only sources whose contents could materially change execution;
- **completion condition**: observable state that ends the task;
- **authority**: what the receiver can actually do, preferably supplied mechanically rather than explained in prose.

## Compilation procedure

### 1. Choose one operation

Start with the smallest operation that fits. Current useful operations:

- `orchestrate` — decompose, delegate, inspect results, and drive a bounded objective to completion;
- `recon` — inspect and return implementation-relevant facts without changing the target;
- `implement` — make one bounded change and verify it;
- `verify` — test an existing claim/change and correct concrete defects when authorized;
- `adversarial-review` — try to falsify implementation/design claims using broad reviewer discretion;
- `ontology-review` — compare conceptual structure against selected canonical context;
- `synthesize` — reconcile already-independent findings into decisions or a correction brief.

Add new named operations only after repeated use demonstrates a distinct reasoning mode.

### 2. Atomize the task

Describe one independently reviewable transition, even though formal EDASES Work Units are not yet implemented.

Good task boundaries have:
- one primary objective;
- one coherent target area;
- a clear stopping condition;
- state that can be resumed from Crosslink if the agent fails.

Split only when parts can be executed, restarted, or reviewed independently. Do not manufacture decomposition merely to create more agents.

### 3. Select context

Use the minimum context that can change the answer.

Expansion order:

1. target itself;
2. directly governing issue/spec/test/claim;
3. directly related canonical concepts or project knowledge;
4. broader context only when ambiguity remains material.

Prefer references or retrievable sources over pasted explanations when the receiver can access them cheaply.

For ontology-sensitive work, select the relevant conceptual neighborhood rather than the whole corpus. Canonical terminology/registry entries establish identity and relationships; canonical specifications/architecture establish substantive meaning, invariants, ownership, and boundaries.

If required meaning is missing or contradictory, expose the gap instead of silently expanding the prompt into an invented explanation.

### 4. Preserve run-specific policy

Include instructions that can legitimately change from invocation to invocation and are not yet mechanically enforced.

Do not tell an orchestrator its own model identity by default. Model identity belongs in the prompt only when it materially changes execution policy or provenance — for example, when same-family builders generate code and later reviewer eligibility depends on which model family produced that artifact.

Example:

`Delegate bounded work to Luna Light; escalate a failed bounded task to Luna Medium on concrete evidence of capability failure.`

Do not move variable routing policy into permanent project documentation merely to shorten prompts. Prefer the runtime/orchestration layer to know model identity and enforce model-family constraints without making that identity part of the model-visible task unless the model must reason about it.

### 5. Remove redundant authority prose

If a capability is structurally unavailable, do not spend prompt tokens forbidding it.

Examples:
- a shell-less orchestrator does not need "do not use shell";
- a role whose delegation tool exposes only approved worker roles does not need a list of forbidden models;
- a read-only reviewer does not need repeated warnings against editing if mutation tools are absent.

State an authority constraint only when the receiver could otherwise take the action and the distinction matters to this task.

### 6. Prefer the permitted path over the forbidden space

Describe what to do and where to operate. Use negative instructions only for a nearby, plausible action that cannot yet be prevented mechanically and would materially damage the task.

Bad:

`Do not change server APIs, providers, contracts, routing, the ChatGPT side, or build a new controller.`

Better:

`Implement and test Return-to-Strategy in the timeline UI using the existing message-context and local-API paths.`

The second prompt avoids introducing unrelated architectural possibilities into the model's search space.

### 7. Avoid implementation anchoring unless it is evidence

Distinguish known constraints from hypotheses.

- Exact file/path/function names are useful when the task is specifically about them or prior recon established them.
- Otherwise give a starting point or acceptance condition and let the agent inspect the implementation.
- Review prompts should not repeat the builder's implementation story unless that story itself is the claim being tested.

### 8. Write an observable completion condition

Prefer mechanical or evidentiary stopping conditions:

- focused test passes;
- reproduction established;
- relevant checks pass;
- finding recorded with evidence;
- issue contains result and unresolved blocker;
- independent reviews completed and synthesized.

Avoid large completion-report schemas. Ask only for information not already retained in Crosslink or visible in the diff/test output.

### 9. Compress the rendered prompt

Delete anything that does not change execution.

Apply these tests:

- **Fresh-context test:** Does the receiver need this fact, and can it discover it from available context/tools? If discoverable, omit unless discovery is unusually costly or error-prone.
- **Concept-introduction test:** Does this sentence introduce a concept the agent otherwise would not need? If yes, remove it unless it is required.
- **Authority test:** Is this already mechanically enforced? If yes, omit it.
- **Duplication test:** Is this stable procedure already in the role/skill or stable meaning already in project knowledge? If yes, reference/select it rather than restating it.
- **Anchoring test:** Am I telling a reviewer where I expect the bug to be? Remove unnecessary hypotheses.
- **Report test:** Will this information already exist in Crosslink, Git, or test output? If yes, do not demand it again.

Formatting should optimize machine consumption: dense paragraphs, short headings only when they aid parsing, few blank lines, no explanatory preamble written for a human reader.

## Operation guidance

### Orchestrate

Include:
- bounded objective;
- current run model/delegation policy;
- Crosslink state location when relevant;
- completion condition.

For review orchestration, the prompt must either:
- name the reviewer models to launch; or
- ask the orchestrator to propose a small set of cost-efficient models suited to the review operation before launch.

Do not leave reviewer selection implicit. Model choice is part of the review design because different models have materially different review behavior, cost, and strengths.

Let the orchestrator decide decomposition within its allowed delegation surface.

### Recon

Ask for facts needed by a subsequent decision or implementation. Return exact evidence/edit points when useful. Recon should not become speculative redesign.

### Implement

State the desired state and governing acceptance evidence. Include exact implementation constraints only when established. Require the smallest appropriate verification.

### Verify

Start from the existing claim/change. Run the narrow checks that can establish or falsify it. Permit corrections only when the receiver is authorized. Record unresolved uncertainty rather than padding the prompt with predicted edge cases.

### Adversarial review

Keep the framing aggressive and open:

`Adversarially review <target> against <claim/spec>. Inspect all relevant code and dependencies and use whatever tests or experiments help falsify it. Look for incorrect behavior, hidden assumptions, shortcuts, regressions, and unjustified complexity.`

Prefer free investigation over a long checklist. Known regressions belong in tests; the reviewer should search beyond them.

Useful result fields: severity, evidence, confidence, and whether the item is a confirmed defect or uncertainty.

Independent panel members should receive the same unanchored review target before synthesis. Panel composition and model routing belong in the orchestration layer, not each specialist prompt.

Reviewer independence is a structural provenance rule:

- a model family must not review code produced by the same model family;
- the same model family may act as an independent clean-room reviewer of code produced by a different model family;
- multiple reviewers may share a model family when they are reviewing another family's artifact, provided their contexts are independently instantiated;
- reviewers must not receive peer-review outputs before their independent pass; synthesis receives those outputs afterward;
- enforce provenance, context isolation, and withheld peer outputs structurally through routing/session state rather than instructions such as "do not read the other reviewers' work."

Reviewer selection must never be left unspecified. The review-orchestrator prompt must either name the reviewer models or explicitly ask the orchestrator to recommend cost-efficient models suited to the task before launching them.

The reviewer prompt normally does not need the reviewer's model identity. The orchestration layer should decide eligibility from recorded artifact/model provenance.

### Ontology review

Use the dedicated Ontology Reviewer role. Supply only the target plus relevant canonical context.

Minimal invocation:

`Ontology-review <target> against the supplied canonical context. Report material conceptual inconsistencies only.`

The role definition supplies the reasoning domain and output shape; the task prompt should not reproduce its checklist.

### Synthesize

Provide completed independent findings and the decision required. Ask the synthesizer to reconcile evidence, disagreements, confidence, and required next action. Do not ask it to rerun the original review unless evidence is incomplete.

## Failure modes

Do not force compression when shared semantics are insufficient. If the prompt cannot be made safely compact:

- add the smallest missing context;
- identify the missing canonical term/boundary;
- request an ontology review if the ambiguity is conceptual;
- ask the orchestrator/human to resolve a genuine decision;
- leave an explicit uncertainty rather than inventing project meaning.

## Output

Produce:

1. the compact prompt to send to the agent;
2. only when useful, a short list of context references that should accompany it.

Do not include an explanation of how the prompt was compressed unless explicitly requested.
