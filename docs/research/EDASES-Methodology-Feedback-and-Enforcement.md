---
title: "EDASES/ASES Methodology Feedback and Enforcement Architecture"
program: EDASES
layer: Research
document_type: Research Record
status: Experimental
authority: Experimental
canonical_repository: edases

depends_on:
  - Documentation Standard

related_documents:
  - EDASES-topic-Methodology-Research.md
  - EDASES-topic-Git-Based-Engineering-Systems.md

consumed_by:
  - ASES methodology development
  - Execution engine research programme

supersedes: []

superseded_by: []

last_updated: 2026-08-10
---

# EDASES/ASES Methodology Feedback and Enforcement Architecture

**Status:** Draft — architectural concept
**Purpose:** Define how methodology discovered through live projects can be applied immediately, captured automatically, and fed back into EDASES for research without requiring a separate manual coordination process.

## 1. Problem

EDASES develops methodology by observing the behavior of real software-engineering projects. Those projects are simultaneously consumers of ASES methodology and experimental environments through which new methodology is discovered.

This creates a recurring problem.

A project may expose an immediate contradiction between the intended methodology and its execution environment. For example, ASES may imply that an agent should have access to a particular command while the project's execution policy denies it. The project needs to be fixed immediately so that work can continue.

However, the same incident may contain valuable methodological information. The implementation may have diverged from the methodology, the methodology may have been underspecified, or the execution system may lack a mechanism for expressing the requirement.

If the discovery remains buried in the working session, the information can be lost or fail to propagate to other projects.

The system therefore needs to support two activities simultaneously:

1. **Immediate intervention:** fix the live project so that experimentation can continue.
2. **Methodological feedback:** preserve the incident and its context so that EDASES can later determine what it means.

These activities must not depend on one another. Research should not block execution, and execution should not depend on a human remembering to report every methodological discovery.

## 2. Core principle

The system should use a **push-driven feedback loop with a project-local ASES interface**.

Projects should not normally be monitored by continuously sweeping their repositories for interesting information. Instead, the Execution layer should produce structured methodology-relevant events at the point where they occur.

The project repository provides the durable record of those events. Git provides the existing durable transport and synchronization mechanism. EDASES consumes the resulting events for research.

The conceptual loop is:

```
EDASES
   │
   │ methodology
   ▼
 ASES
   │
   │ applicable rules
   ▼
Execution
   │
   │ applies / verifies methodology
   ▼
```

Live Project
│
│ observations, incidents, interventions
▼
.ases/events/
│
│ git push
▼
ASES ingestion
│
▼
EDASES

This makes EDASES → ASES → Execution → Project → EDASES a closed learning loop.

## 3. `.ases/` as the project integration boundary

Each participating project should contain a small `.ases/` directory.

It should not become a second project knowledge base. Its purpose is to define the project's relationship with ASES and provide a durable interface through which methodology state and methodology-relevant events can be represented.

A possible structure is:

```
.ases/
  manifest.yaml
  events/
  incidents/
  state/
```

The exact structure is intentionally provisional.

The important invariant is:

> A project containing `.ases/` exposes a standard interface to the ASES/EDASES system.

The manifest can identify the applicable ASES methodology revision and project-specific configuration.

## 4. Events rather than repository inference

The system should prefer explicit structured events over asking EDASES to infer what happened by examining an entire repository.

For example, an execution-policy contradiction might produce an event conceptually equivalent to:

```
type: methodology.conformance_failure
project: project-a
rule: execution.command_permissions
description: >
  Command X was denied despite the applicable methodology
  permitting its use.
intervention: execution_policy_patched
commit: <commit>
```

The event should be generated as close as possible to the event that caused it.

This is particularly important for discoveries made during agent sessions. The system should not rely on the human or agent later remembering that an important methodological observation occurred.

## 5. Methodology incidents

A useful first-class event type is the **methodology incident**.

A methodology incident represents a situation in which:

* execution contradicts the intended methodology;
* methodology is insufficiently specified;
* an execution mechanism cannot express a methodological requirement;
* a project deliberately deviates from the methodology;
* or live project behavior exposes a previously unknown methodological problem.

An incident is not itself an ASES methodology change.

It is evidence for EDASES.

For example:

```
methodology incident
      │
      ├── immediate project fix
      │
      └── later EDASES investigation
```

This allows the project to continue without requiring the research program to reach a conclusion first.

## 6. Immediate fixes and methodological research are separate paths

The system should explicitly support two paths after an incident.

### Execution path

```
problem discovered
    ↓
immediate intervention
    ↓
project continues
```

### Research path

```
incident captured
    ↓
EDASES analysis
    ↓
finding / hypothesis
    ↓
possible ASES methodology change
```

A methodology incident may ultimately produce no methodology change. It may reveal a project-specific problem, an implementation bug, an incorrect assumption, or a limitation that requires further research.

This prevents every operational bug fix from becoming an immediate methodology revision.

## 7. Methodology as an executable specification

ASES should distinguish between requirements that are primarily descriptive and requirements that can be mechanically checked.

Potential categories include:

* descriptive requirements;
* procedural requirements;
* executable requirements;
* evaluative requirements.

Executable requirements are particularly valuable because they allow the Execution layer to test whether implementation conforms to methodology.

For example:

```
ASES:
  command X must be available

         ↓

Execution conformance check

         ↓

   PASS / FAIL
```

A methodology change can therefore eventually become not merely documentation but an executable constraint.

This creates a direct relationship between methodology and enforcement.

## 8. Conformance, divergence, and intentional override

The system should distinguish at least three states:

### Conforming

The project implementation agrees with the applicable methodology.

### Divergent

The implementation differs unintentionally from the methodology.

### Overridden

The project intentionally differs from the general methodology and records the reason.

This is preferable to treating every difference as a versioning or rollout problem.

For example, a project might intentionally restrict a capability for a project-specific reason. That should be represented as an explicit exception rather than silently modifying the project's execution policy.

## 9. Git as durable transport

The normal synchronization path can use the existing Git workflow:

```
Execution creates event
      ↓
event stored in .ases/
      ↓
git commit
      ↓
git push
      ↓
ASES ingestion
      ↓
EDASES
```

The repository remains the durable source of the event.

The remote ingestion mechanism is a transport and indexing mechanism, not the only copy of the information.

This means the system remains recoverable if the ingestion service is unavailable.

A later synchronization process can replay events from Git.

## 10. Idempotent ingestion

Every event should have a stable unique identifier.

If the same event is transmitted more than once, ASES should recognize that it has already been received rather than creating duplicate observations.

This allows network retries, CI retries, and manual resynchronization to be safe.

The desired property is:

```
event created once
     ↓
transmitted zero or more times
     ↓
represented once in EDASES
```

## 11. Push-driven operation with reconciliation

The normal path should be event-driven rather than based on continuous repository sweeping.

For GitHub-hosted projects, a GitHub Action could initially perform the synchronization after a push. Other Git transports or local hooks could eventually provide the same interface.

However, a periodic audit/reconciliation mechanism should exist as a recovery path.

The distinction is:

```
Normal operation:
    push → event ingestion

Recovery:
    audit → discover missing events → reconcile
```

This makes the system both efficient and resistant to automation failures.

## 12. Bidirectional flow

The feedback loop should eventually operate in both directions.

Project → EDASES:

```
incidents
observations
conformance failures
interventions
validation results
```

EDASES → ASES → Project:

```
research findings
methodology changes
clarified requirements
new conformance rules
```

The project therefore does not need to be manually informed of every methodological discovery. Its ASES state can indicate when its applicable methodology has changed.

## 13. Separation of responsibilities

The initial conceptual responsibilities are:

| Layer           | Responsibility                                      |
| --------------- | --------------------------------------------------- |
| EDASES          | Research, evidence, findings, hypotheses, synthesis |
| ASES            | Generalized methodology                             |
| `.ases/`        | Project's ASES integration boundary                 |
| Execution       | Apply and verify methodology                        |
| Git             | Durable project history and transport               |
| Synchronization | Deliver structured events to ASES/EDASES            |
| Crosslink       | Coordinate project work and state                   |

None of these systems needs to become the universal repository of project knowledge.

## 14. Minimal initial implementation

The first implementation should remain deliberately small.

The minimum useful system is:

```
.ases/manifest.yaml
.ases/events/
ases CLI
ASES event ingestion
```

The CLI might eventually expose:

```
ases status
ases check
ases incident
ases sync
```

The first end-to-end experiment should use an actual methodology/execution contradiction.

For example:

```
ASES requirement
      ↓
execution policy incorrectly denies capability
      ↓
conformance failure
      ↓
immediate execution fix
      ↓
methodology incident automatically recorded
      ↓
git commit
      ↓
git push
      ↓
ASES receives event
      ↓
EDASES can analyze the incident
```

If this can occur without adding a significant procedural burden to live development, the architecture is demonstrating its intended value.

## 15. Architectural objective

The objective is not to create a centralized methodology-management bureaucracy.

The objective is to make methodology **observable, enforceable, recoverable, and continuously improvable** while live projects remain the primary experimental environment.

The desired end state is therefore:

```
EDASES
  research
    ↓
ASES
  methodology
    ↓
Execution
  enforcement
    ↓
Projects
  experimentation
    ↓
Structured evidence
    ↓
EDASES
```

The system should make the feedback loop automatic enough that useful methodological discoveries are difficult to lose, while remaining lightweight enough that immediate project work never has to wait for the research process.
