---
title: "EDASES Topic: MicroVMs"
program: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Finding
canonical_repository: edases

depends_on:
  - Documentation Standard
  - EDASES Phase 4 Retrospective

related_documents:
  - EDASES-topic-Containers-and-Environment.md

consumed_by:
  - Execution engine research programme
  - ASES methodology development

last_updated: 2026-08-10
---

# EDASES topic: MicroVMs

**Retrospective**

## 1. Context

This discussion examined whether microVM technology—and, subsequently, Nix/NixOS—has a meaningful role in EDASES.

The discussion began from the current EDASES architecture, in which:

```text
EDASES
Research Programme
        │
        ▼
ASES
Methodology
        │
        ▼
Execution Engine
Implementation
```

EDASES is concerned with research and evidence. ASES is the methodology derived from that research. The execution engine is an implementation of ASES and must not redefine the methodology.

A central architectural principle is that reasoning is the primary engineering artifact. Observations, assumptions, findings, decisions, challenges and validations are intended to remain explicit and traceable. Software and execution are outputs of that reasoning rather than the project's fundamental object of interest.

The immediate question was therefore not whether EDASES should use microVMs, but whether microVMs solve a problem that the emerging execution-engine architecture actually has.

---

# 2. Initial MicroVM Question

The discussion was prompted by two announcements supplied for consideration:

* Tangled's announcement concerning **Spindle MicroVMs**
* AWS's announcement concerning **isolated sandboxes with full lifecycle control using microVMs**

The initial observation was that microVMs are increasingly being used for AI-oriented execution environments, particularly where systems need to execute potentially untrusted or AI-generated code while providing strong isolation and controllable lifecycle management.

The first important conclusion was:

> **MicroVMs are probably not a foundational architectural component of EDASES, but they could be an important execution primitive.**

This distinction became the central framing for the rest of the discussion.

---

# 3. MicroVMs as an Execution Harness

An earlier formulation of the EDASES architecture had considered multiple types of agents:

```text
Builder agent
Verifier agent
Adversarial reviewer
Research agent
Implementation agent
Testing agent
Architecture reviewer
```

As these agents perform increasingly autonomous work, they eventually need somewhere to execute software.

The earlier assessment identified several broad execution approaches:

```text
Local execution
    ↓
VPS execution
    ↓
Container execution
    ↓
MicroVM execution
```

Each progressively improves isolation, at the cost of additional infrastructure and complexity.

The particularly interesting model was:

```text
Orchestrator
    ↓
Create isolated review sandbox
    ↓
Provide repository / relevant artifacts
    ↓
Agent executes tools and tests
    ↓
Produce review / evidence
    ↓
Destroy or preserve sandbox
```

The microVM is not the agent's identity or cognitive environment. It is the agent's **execution harness**.

This separation was considered important.

The preferred conceptual relationship is therefore:

```text
Agent
    │
    ▼
Execution Request
    │
    ▼
Execution Harness
    │
    ├── Local process
    ├── Container
    ├── MicroVM
    └── Remote executor
    │
    ▼
Evidence
```

Rather than:

```text
Agent
    ↓
MicroVM
```

The former keeps reasoning and execution separate.

---

# 4. Why Isolation Matters

The principal immediate value of microVMs is isolation.

An autonomous agent may need to:

* modify files
* compile software
* run arbitrary commands
* install dependencies
* execute tests
* inspect binaries
* run security tools
* execute generated scripts
* launch services
* perform potentially destructive experiments

Allowing those activities directly on the host creates risks:

* corruption of shared state
* accidental modification of unrelated artifacts
* leakage between tasks
* contamination of later experiments
* damage to the development environment
* possible interaction with production resources

A disposable isolated execution environment substantially reduces these risks.

This makes microVMs particularly attractive for tasks such as:

```text
Implementation validation
Testing
Adversarial review
Security analysis
Bug reproduction
Generated-code execution
Research experiments
```

The earlier discussion therefore concluded that **isolation is a plausible execution-engine requirement even if microVMs themselves are not an architectural requirement**.

---

# 5. Execution Context Rather Than "MicroVM per Task"

The initial formulation was "microVM per task."

The discussion subsequently refined this into a more general concept:

> **Execution context**

An execution context represents an isolated environment in which a piece of engineering work can be performed.

Some contexts may be short-lived:

```text
Create
    ↓
Run tests
    ↓
Collect evidence
    ↓
Destroy
```

Others may be long-lived:

```text
Create
    ↓
Investigate bug
    ↓
Modify environment
    ↓
Run experiments
    ↓
Suspend
    ↓
Resume
    ↓
Continue investigation
```

Therefore, the conceptual abstraction should not assume a particular lifecycle.

A possible execution-context interface was sketched as:

```text
ExecutionContext
    create()
    execute()
    snapshot()
    resume()
    destroy()
```

Not every backend would necessarily support every operation.

A simple local backend could ignore snapshotting, while a microVM backend could provide efficient snapshot and resume capabilities.

This reinforces the principle that the methodology should specify **required guarantees**, not prescribe the implementation technology.

---

# 6. MicroVMs and Evidence

The discussion then moved from isolation to a potentially more important EDASES concern: **evidence quality**.

EDASES treats engineering reasoning and epistemic relationships as first-class. Therefore, simply recording:

```text
Tests passed.
```

is weaker than recording the circumstances under which the tests passed.

A more useful evidence package might contain:

```text
Finding
    ↓
Evidence
    ├── Test report
    ├── Coverage report
    ├── Execution transcript
    ├── Inputs
    ├── Outputs
    └── Environment description
```

The execution environment can therefore become part of the evidence.

For example:

```text
Environment
    OS: Ubuntu 24.04
    Python: 3.13.x
    Compiler: GCC 15.x
    Repository: commit abc123
    Dependencies: ...
```

This gives a future agent or researcher information about **the conditions under which the observation was produced**.

The important conceptual development was therefore:

> Isolation is one reason to use microVMs; reproducible execution conditions may be an even more important reason for EDASES.

---

# 7. Spindle and NixOS

The Spindle announcement repeatedly references NixOS.

This prompted a second question:

> If microVMs are useful for EDASES, how relevant is Nix/NixOS?

The discussion concluded that **Nix may ultimately be more conceptually relevant to EDASES than microVMs**, although for a different reason.

The distinction was framed as:

```text
MicroVMs
    → isolation

Nix
    → reproducibility
```

MicroVMs provide an isolated machine-like execution environment.

Nix provides a way of describing and constructing software environments reproducibly.

This matters because EDASES is concerned not merely with executing something successfully, but with preserving the evidence surrounding that execution.

---

# 8. "The Environment as a Reproducible, Declarative Artifact"

A key concept introduced during the discussion was:

> **An execution environment can itself be a reproducible, declarative artifact.**

This was clarified to mean that the environment stops being something implicitly assembled by a person and instead becomes something explicitly specified.

A traditional environment might be created procedurally:

```text
Install Ubuntu
Install Python
Install Node
Install PostgreSQL
Clone repository
Install dependencies
Configure tools
Run tests
```

The resulting environment is largely an undocumented consequence of those actions.

A declarative approach instead describes the desired environment:

```text
OS: Ubuntu 24.04
Python: 3.13
Node: 24.x
PostgreSQL: 17
Compiler: GCC 15
Repository: commit abc123
Tools:
    pytest
    mypy
    clang-tidy
```

The specification describes what should exist.

An environment-building system then realizes that specification.

This changes the environment from an implicit prerequisite into an explicit engineering artifact.

---

# 9. Environment Provenance

The relevance to EDASES becomes clearer when environment specifications are connected to evidence.

Instead of:

```text
Observation:
Tests passed.
```

the system could retain:

```text
Observation:
Tests passed.

Evidence:
    Test report
    Coverage report
    Execution transcript

Environment:
    OS
    Compiler
    Runtime
    Dependencies
    Repository revision
```

The environment therefore becomes part of the provenance of the observation.

A more complete evidence relationship can be represented as:

```text
Observation
    ↓
Evidence Package
    ├── Reasoning
    ├── Inputs
    ├── Outputs
    ├── Execution transcript
    └── Environment specification
```

This is particularly compatible with the project's emphasis on explicit epistemic relationships and traceability.

---

# 10. Environment Identity

The discussion extended this idea to the possibility of treating an environment similarly to a versioned source artifact.

Conceptually:

```text
Environment #7f91

Ubuntu 24.04
Python 3.13.2
PostgreSQL 17.3
OpenSSL 3.5.0
Repository abc123
...
```

Rather than asking someone to reconstruct the environment from instructions, another agent or researcher could ask the execution engine to recreate the environment associated with a particular evidence package.

The conceptual workflow becomes:

```text
Execution Specification
        ↓
Environment
        ↓
Execution
        ↓
Evidence
```

rather than:

```text
Execution
        ↓
Unspecified machine state
        ↓
Evidence
```

This is potentially valuable for research reproducibility as well as software engineering.

---

# 11. Nix as a Possible Implementation

The discussion explicitly rejected making Nix a mandatory architectural dependency.

EDASES is intended to remain independent of implementation technologies. The methodology should therefore not say:

```text
Use Nix.
```

It could instead specify a requirement such as:

```text
The execution environment must be reproducible.
```

An implementation could satisfy that requirement through:

* Nix
* container images
* VM images
* devcontainers
* another reproducible environment mechanism

Nix could then be one particularly strong implementation.

This maintains the existing abstraction boundary:

```text
Methodology
    ↓
Requirement
    ↓
Execution Architecture
    ↓
Technology
```

rather than:

```text
Technology
    ↓
Methodology
```

---

# 12. Nix and the Declarative Model

One reason Nix appeared especially interesting was its conceptual similarity to the broader EDASES approach.

Procedural environment construction looks like:

```text
Run command A
Run command B
Run command C
Run command D
```

A declarative model instead specifies:

```text
This is the environment required.
```

The execution system determines how to realize it.

This mirrors the distinction between methodology and implementation already present in EDASES:

```text
Methodology
    specifies what must be achieved
          ↓
Execution Engine
    determines how to achieve it
```

The similarity does not establish that EDASES should use Nix, but it makes Nix an especially interesting technology for research.

---

# 13. Docker versus Nix

The discussion then examined how the concept differs from Docker.

The simplified distinction developed was:

```text
Docker
    → package and execute an application consistently

Nix
    → describe and reproduce a software environment
```

Docker's primary artifact is an image.

A Dockerfile might contain:

```dockerfile
FROM ubuntu:24.04

RUN apt install python3
RUN pip install pytest

COPY . /app
```

The resulting image becomes the runtime artifact.

Nix instead places greater emphasis on the declarative specification and dependency graph from which the environment is constructed.

This leads to an important distinction:

> Docker allows reproducibility; Nix makes reproducibility much closer to a first-class design objective.

Docker images can be highly reproducible if dependencies and inputs are carefully pinned. Docker itself does not guarantee that a Dockerfile rebuilt later will necessarily produce the same environment.

---

# 14. Docker, Nix and MicroVMs as Complementary Layers

The discussion ultimately treated the three technologies as addressing different concerns rather than as direct alternatives.

A useful conceptual model is:

```text
Nix
    ↓
Environment construction / reproducibility

Docker
    ↓
Container packaging / execution

MicroVM
    ↓
Machine-level isolation
```

They can potentially be composed.

For example:

```text
Environment specification
        ↓
Nix
        ↓
Environment artifact
        ↓
MicroVM
        ↓
Isolated execution
        ↓
Evidence
```

Docker could occupy the execution layer instead, or not be involved at all.

The important architectural distinction is between:

1. **what environment is required,**
2. **how that environment is constructed,**
3. **where it is executed,**
4. **what evidence is produced,**
5. **how that evidence relates to the reasoning process.**

These should not be collapsed into a single technology.

---

# 15. Emerging Execution-Engine Model

By the end of the discussion, a possible execution architecture had emerged conceptually:

```text
Reasoning Engine
        │
        ▼
Execution Specification
        │
        ▼
Environment Builder
        │
        ├── Nix
        ├── Container image
        └── Other mechanism
        │
        ▼
Execution Backend
        │
        ├── Local process
        ├── Container
        ├── MicroVM
        └── Remote executor
        │
        ▼
Evidence
        │
        ▼
Reasoning / Epistemic Graph
```

This is not an architectural decision. It is a conceptual model resulting from the discussion.

Its significance is that it separates concerns which might otherwise become entangled.

---

# 16. What Should and Should Not Become Methodology

A recurring conclusion was that EDASES should specify **guarantees rather than technologies**.

Potential methodology-level requirements might eventually concern:

* isolation
* reproducibility
* controlled execution
* environment provenance
* evidence capture
* lifecycle management
* rollback or reset
* traceability between execution and reasoning

The methodology should not prematurely require:

* Firecracker
* Spindle
* Nix
* NixOS
* Docker
* a particular cloud provider

For example:

```text
Good abstraction:

"Execution of untrusted artifacts must occur within
an appropriately isolated execution context."

Bad abstraction:

"Execute every artifact in a Firecracker microVM."
```

Similarly:

```text
Good abstraction:

"Evidence-producing execution must record sufficient
environment information to reproduce the execution."

Bad abstraction:

"All environments must be Nix flakes."
```

The former preserves implementation independence.

---

# 17. Agent Identity versus Execution Environment

One particularly important architectural distinction was that **agents should not be equated with their execution environments**.

An agent represents a reasoning capability or role.

An execution environment represents where actions are performed.

Therefore:

```text
Agent
    ↓
Execution Request
    ↓
Execution Context
```

is preferable to:

```text
Agent = VM
```

This prevents cognitive state, methodological state and operating-system state from becoming unnecessarily coupled.

An agent could potentially use multiple execution contexts during one task.

Conversely, an execution context could potentially be used by multiple bounded activities under appropriate controls.

---

# 18. Parallel Validation

An additional possibility identified during the discussion was using isolated execution contexts to support independent validation.

For example, a candidate implementation could be evaluated through several environments:

```text
Candidate implementation
        │
        ├── GCC environment
        ├── Clang environment
        ├── Sanitizer environment
        ├── Security-analysis environment
        └── Fuzzing environment
```

Each execution produces evidence.

The reasoning layer then evaluates the combined evidence.

This is potentially more significant for EDASES than simply running multiple AI reviewers, because independent execution environments can provide independent empirical evidence rather than merely independent opinions.

This remains a conceptual possibility rather than an established requirement.

---

# 19. Main Conclusions

The discussion produced several provisional conclusions.

### 19.1 MicroVMs

MicroVMs should **not currently be treated as a foundational EDASES architectural requirement**.

They are, however, a strong candidate for implementing isolated execution contexts in the execution engine.

Their strongest apparent relevance is:

* untrusted or AI-generated code execution
* disposable validation environments
* adversarial testing
* security analysis
* isolated experiments
* long-lived but isolated investigation environments
* potentially snapshot/resume workflows

### 19.2 Nix

Nix appears potentially more interesting than microVMs from the perspective of EDASES's epistemic and reproducibility goals.

Its most relevant concepts are:

* declarative environments
* reproducibility
* immutable artifacts
* explicit dependency graphs
* environment construction from specifications
* reduced environmental drift

Nix should nevertheless remain a candidate implementation technology rather than a methodology-level requirement.

### 19.3 Docker

Docker remains relevant as an execution and packaging technology.

It overlaps with the problem of reproducible environments but approaches it primarily through container images and build mechanisms.

Docker, Nix and microVMs should therefore not be treated as mutually exclusive choices.

### 19.4 Execution Context

The strongest architectural abstraction identified during the discussion is not "microVM."

It is **execution context**.

An execution context is an isolated, controlled environment in which engineering actions can be performed and from which evidence can be collected.

A microVM is one possible implementation.

### 19.5 Environment Provenance

The most potentially significant idea introduced during the discussion is that an execution environment itself can become a first-class engineering artifact.

The environment can be specified, identified, reproduced and associated with evidence.

This could extend EDASES's existing emphasis on traceability from reasoning into the execution layer.

---

# 20. Questions Left Open

The discussion did not resolve whether EDASES actually requires any of these technologies.

Several research questions remain open:

1. What isolation guarantees does ASES actually require?
2. Does the methodology require isolation at all execution boundaries, or only for particular classes of activity?
3. What does "reproducible execution" need to mean operationally?
4. How much environment state must be captured for evidence to be considered reproducible?
5. Should execution environments be persistent, ephemeral, or both?
6. Is snapshot/resume a useful methodological capability or merely an implementation convenience?
7. Can containers provide sufficient isolation and reproducibility for EDASES?
8. When does microVM isolation provide enough additional value to justify its complexity?
9. Is Nix's reproducibility model materially better for EDASES than carefully pinned container images?
10. Could a future execution-engine architecture support multiple environment and execution backends without exposing their differences to ASES?
11. What evidence should be associated with an execution context?
12. Should environment specifications themselves become versioned or addressable objects in the epistemic knowledge model?

These questions belong to the research and architecture investigation rather than being answered by premature technology selection.

---

# 21. Retrospective Assessment

The discussion began with a relatively narrow question:

> "What would microVMs actually do for EDASES?"

It ended with a broader and more useful architectural question:

> **What properties must an EDASES execution environment have in order for execution to be safe, controlled, reproducible and evidentially meaningful?**

That reframing is important.

MicroVMs address one part of the problem—**isolation**.

Nix addresses another—**reproducible environment construction**.

Docker addresses another—**packaging and execution of isolated environments**.

None of these technologies should determine the methodology.

The emerging architectural direction is instead to identify the required properties of an **execution context**, then evaluate technologies against those requirements.

The most significant finding from this discussion is therefore not that EDASES should use microVMs or Nix.

It is that **the execution environment may itself need to become an explicit, traceable artifact of engineering reasoning**, alongside the inputs, actions, outputs and evidence generated within it.

That concept appears particularly compatible with EDASES's existing principle that engineering reasoning—not merely source code—is the primary object of interest.

---

## Status

This retrospective records exploratory discussion and provisional architectural reasoning.

It does **not** establish:

* a requirement to use microVMs;
* a requirement to use Nix or NixOS;
* a requirement to use Docker;
* a particular execution backend;
* or a finalized execution-engine architecture.

The appropriate next step is to investigate the required execution guarantees at the methodology and requirements levels, then evaluate microVMs, Nix, containers and alternative technologies against those requirements.
