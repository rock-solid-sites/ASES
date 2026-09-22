---
title: Strategy-to-Builder Integration Packet Method - Derivation
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Derived
canonical_repository: ases
related_documents:
  - docs/methodology/ASES Bounded Project Build Method.md
  - skills/prompt/SKILL.md
last_updated: 2026-09-22
---

> Evidence/derivation record. Non-normative; the canonical method is `docs/methodology/ASES Bounded Project Build Method.md`.

# Strategy-to-Builder Integration Packet Method

**Status:** reusable reference  
**Purpose:** minimize builder search, design work, and implementation discretion by moving as much solvable work as practical into strategy before build execution.

## 1. Core principle

Use the strategy phase to decide **what should exist, how it should behave, which existing mechanisms should be reused, and which implementation choices can be settled in advance**.

The builder should receive the smallest remaining task:

> integrate predetermined components into the real project, resolve only concrete environment incompatibilities, and verify the finished behavior.

This is not appropriate for every task. It works best when requirements can be stabilized before implementation and when relevant source code, APIs, UI behavior, or comparable implementations can be inspected in advance.

The method deliberately pushes work "left" from build execution into strategy.

## 2. When to use it

This method is a strong fit when several of these are true:

- the desired user-visible behavior can be stated clearly before implementation;
- the existing project can be inspected before the builder starts;
- open-source or internal implementations already solve parts of the problem;
- much of the logic is deterministic or pure;
- interfaces between components can be defined in advance;
- UI flows can be mocked or prototyped independently;
- expensive agent reasoning during implementation is undesirable;
- the builder should have little authority to redesign the product.

Use a lighter version when only some of these conditions hold.

Do **not** force this process when the implementation itself is exploratory, when critical constraints can only be discovered inside the live environment, or when freezing design early would create more rework than it prevents.

## 3. Preserve task semantics first

Before optimizing anything, identify:

- the user-selected target;
- the required behavior;
- settled constraints;
- the observable completion condition.

Do not replace the requested interaction with an easier implementation abstraction.

Example:

- requirement: save the conversation whose sidebar menu was clicked;
- incorrect optimization: save the currently open conversation because its ID is easier to obtain;
- correct optimization: find the smallest reliable mechanism that preserves clicked-row identity.

Implementation convenience never outranks task semantics.

## 4. Reconnaissance before build

Inspect the current project and relevant existing implementations before assigning the builder.

The goal is not broad research. It is to answer implementation-reducing questions:

- What useful code already exists in the target project?
- Which existing pieces should be preserved?
- Which old assumptions or prototypes are now superseded?
- Which external implementations already solve exact subproblems?
- Which parts of those implementations are actually relevant?
- What can be copied, adapted, simplified, or avoided entirely?

Prefer direct source inspection over documentation when the question is about implementation mechanics.

Record exact files, functions, selectors, API paths, or source revisions when they materially reduce builder uncertainty.

## 5. Reduce external sources to mechanisms

Do not hand entire upstream projects to the builder if only small parts matter.

For each source implementation:

1. identify the exact mechanism that satisfies a requirement;
2. identify unrelated machinery;
3. extract or rewrite only the useful portion;
4. remove fallbacks or assumptions that violate the target semantics;
5. pin the source revision used as evidence when useful.

The output of reconnaissance should look like:

| Requirement | Source mechanism | Keep | Remove |
|---|---|---|---|
| Native menu injection | Existing sidebar menu observer | trigger resolution, menu detection, insertion | folder system, drag/drop, unrelated menus |
| Authenticated fetch | Existing exporter API client | session token, account header, conversation fetch | format framework, archive/delete actions |
| Backup state | Existing export timestamp map | ID → last successful update time | generic storage abstraction |

The builder should ideally receive the reduced mechanism, not a request to rediscover it.

## 6. Necessity review every component

Before freezing the design, challenge every proposed component with:

> What requirement fails if this component is removed?

Then ask:

> Can the same requirement be satisfied with something smaller, native, or already present?

Every surviving component should justify itself.

Possible outcomes:

- **Keep:** it directly satisfies a requirement and no smaller option works.
- **Reduce:** keep only a smaller subset of the mechanism.
- **Replace:** use a native API, pure function, or simpler dependency.
- **Defer:** useful later but not required now.
- **Remove:** no current requirement fails without it.

Apply this to:

- libraries;
- dependencies;
- services;
- APIs;
- background workers;
- persistence layers;
- queues;
- retry systems;
- UI surfaces;
- configuration;
- abstractions;
- permissions;
- data models;
- tests.

Avoid keeping architecture merely because an upstream project uses it.

## 7. Freeze behavior before implementation

Write the behavioral contract before writing the integration packet.

Specify:

- primary interactions;
- state meanings;
- failure behavior;
- persistence semantics;
- update behavior;
- selection behavior;
- retry behavior;
- output semantics;
- provider semantics;
- naming/path rules;
- what counts as success.

Prefer explicit state transitions.

Example:

```text
no successful backup
    → Never

successful backup of current update_time
    → Current

conversation update_time becomes newer
    → Changed

successful re-backup
    → Current
```

This prevents the builder from inventing semantics while coding.

## 8. Freeze UX separately

If the task has meaningful UI, strategy should own the design before build.

Use whichever level is practical:

1. text layout;
2. static mockup;
3. interactive HTML prototype;
4. real component prototype.

Resolve:

- layout;
- labels;
- controls;
- defaults;
- sorting/filtering;
- theme behavior;
- progress/error states;
- navigation;
- which surfaces are extension-owned versus host-owned;
- which settings persist.

Test the flow before handing it to the builder.

A mockup is evidence of appearance. An interactive prototype is stronger because it can expose flow problems before implementation.

Once accepted, mark the prototype as the UI reference and remove design discretion from the builder unless the real platform makes something impossible.

## 9. Write pure components in strategy when practical

If logic can be implemented and tested without the live application, do it before the builder starts.

Typical candidates:

- state classification;
- sorting;
- filtering;
- selection;
- filename sanitation;
- collision handling;
- path generation;
- output rendering;
- retry policy;
- format dispatch;
- storage/provider contracts;
- deterministic transformations.

Benefits:

- less builder reasoning;
- smaller search space;
- easier review;
- deterministic tests exist before integration;
- implementation failures are more clearly integration failures.

Do not prebuild components whose correctness depends heavily on unknown live behavior.

## 10. Define the smallest interfaces

Where multiple implementations are genuinely required, create only the abstraction demanded by current requirements.

Example:

```ts
interface StorageTarget {
  save(file: OutputFile, previousRef?: StoredRef): Promise<StoredRef>
}
```

This is justified if several providers already exist.

Do not create a provider framework, plugin system, registry, event bus, or workflow engine unless the present requirements need them.

A good abstraction removes duplication that already exists. A speculative abstraction predicts duplication that may never exist.

## 11. Separate orthogonal concerns

Keep independent choices independent.

Examples:

```text
conversation fetch
    ↓
render formats
    ↓
write destinations
```

Output format should not be coupled to storage provider.

Backup freshness should not be conflated with provider health.

ZIP packaging should not become an archival format.

UI theme should not alter the host application.

This separation often produces smaller code because each component has one reason to exist.

## 12. Predefine verification

Write test vectors before build whenever possible.

Use two levels:

### Pure/mechanical tests

Examples:

- state transitions;
- sorting directions;
- filtering;
- filename collisions;
- retry count;
- renderer branch behavior.

### User-visible/live acceptance

Test at the same abstraction level as the requirement.

Examples:

- click Conversation B's menu while Conversation A is open; verify B is saved;
- change a conversation after backup; verify `Current → Changed`;
- bulk-select three conversations; verify exactly those three outputs;
- force one provider failure; verify other providers continue.

The builder should not decide what "done" means.

## 13. Assemble one integration packet

The packet is the boundary between strategy and build.

A useful packet contains only what can materially change implementation:

1. **Frozen behavior contract**
2. **Current project baseline**
3. **What existing project code to preserve/supersede**
4. **Reduced external source mechanisms**
5. **Pure components already written**
6. **Minimal interfaces**
7. **UI reference**
8. **Brand/assets if relevant**
9. **State/persistence schema**
10. **Permissions/configuration**
11. **Exact test vectors**
12. **Live acceptance sequence**
13. **Known external facts that may still require live validation**
14. **Builder stopping condition**

Where useful, package actual reference files with the document rather than pasting large code sections into the builder prompt.

## 14. Builder prompt should be very small

Once the packet exists, the builder prompt should not repeat it.

A good form is:

> Implement the frozen integration packet against the existing project. Treat its behavior, UI, selected mechanisms, and acceptance cases as fixed. Reuse the supplied reduced components and preserve the identified existing code. If a live platform fact contradicts the packet, make only the smallest compatible substitution and record the concrete evidence. Stop when the packet's tests and acceptance conditions pass.

The prompt should put the builder in **integration and verification mode**, not research or product-design mode.

## 15. Reopen strategy only on evidence

After freeze, do not reopen settled decisions because the builder prefers another design.

Reopen a decision only when there is concrete evidence such as:

- a live API differs from the researched contract;
- a selector no longer exists;
- a browser permission is actually required;
- an existing component cannot satisfy the required behavior;
- a provider imposes a previously unknown constraint;
- the acceptance test exposes a semantic defect.

Then make the smallest strategy correction required and refreeze.

## 16. Anti-patterns

Avoid:

- giving the builder several repositories and saying "study these";
- asking the builder to design UI while implementing it;
- retaining entire upstream frameworks for one small mechanism;
- copying generic storage/queue/event systems into a narrow extension;
- enumerating large forbidden-feature lists instead of defining the permitted path;
- inventing abstractions for hypothetical future providers/features;
- keeping obsolete prototype architecture because it already has tests;
- treating mockup details as suggestions after they have been accepted;
- adding persistence because runtime state feels uncomfortable;
- adding concurrency before sequential execution is shown to be inadequate;
- asking implementation agents to rediscover decisions strategy already made.

## 17. Lightweight variants

The full process is optional.

### No useful upstream implementation

Skip source reduction. Perform necessity review and write the minimal components directly.

### No UI

Skip prototyping. Freeze behavioral and data contracts only.

### UI cannot be faithfully prototyped

Use a static mockup plus explicit interaction/state table.

### Live environment determines architecture

Freeze only what is known. Give the builder a bounded reconnaissance task first, then return the evidence to strategy before implementation.

### Very small change

Use only:
- semantic preservation;
- current-code inspection;
- necessity review;
- acceptance condition.

Do not manufacture a packet for trivial work.

## 18. Compact operational checklist

Before assigning a builder, ask:

- [ ] Is the actual user-selected target explicit?
- [ ] Are required behaviors frozen?
- [ ] Have we inspected the existing target code?
- [ ] Have relevant external implementations been reduced to exact mechanisms?
- [ ] Has every proposed component passed the necessity test?
- [ ] Can any component be removed, replaced with a native API, or made pure?
- [ ] Is UI design settled enough to avoid builder design work?
- [ ] Can deterministic components be written and tested now?
- [ ] Are interfaces only as abstract as current requirements demand?
- [ ] Are output, storage, state, and failure semantics separated cleanly?
- [ ] Are pure tests already specified?
- [ ] Are live acceptance tests defined at the requirement level?
- [ ] Does the integration packet contain everything the builder needs?
- [ ] Can the builder prompt now be reduced to integration + verification?
- [ ] Is the condition for reopening strategy based on concrete evidence?

## 19. Desired outcome

The ideal result is not "the builder has excellent instructions."

It is:

> **The builder has very few decisions left to make.**

Strategy owns product meaning, selection, reduction, and design.  
Pure computation is moved out of the live build where practical.  
Existing code is reused only where it earns its place.  
The builder assembles, adapts to real constraints, and verifies.

That is the point of the integration packet.