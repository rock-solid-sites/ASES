---
title: "EDASES Topic: Containers and Environments"
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
  - EDASES-topic-microVMs.md

consumed_by:
  - Execution engine research programme
  - ASES methodology development

last_updated: 2026-08-10
---

# EDASES topic: Containers and Environments

**Retrospective**

## 1. Context

This discussion examined Docker, Podman, and other execution technologies in the context of the EDASES project, particularly the eventual execution engine for the ASES methodology.

The starting question was whether Docker or Podman—or another containerization technology—would be appropriate for an agentic programming workflow.

The discussion subsequently shifted from comparing container runtimes to a more fundamental architectural question:

> What role should an execution environment play within EDASES?

That distinction proved important. The conclusion was that containers are probably **implementation mechanisms rather than architectural concepts**, while the specification and reproducibility of an engineering environment may deserve first-class treatment.

This is consistent with the current EDASES architecture, which explicitly separates:

```text
EDASES
Research
    ↓
ASES
Methodology
    ↓
Execution Engine
Implementation
```

The architecture states that the execution engine implements ASES and that implementation decisions should trace back to methodological requirements. It also explicitly maintains implementation independence. `ARCHITECTURE.md` states that the conceptual architecture does not prescribe the implementation architecture of the execution engine.

---

## 2. Initial Investigation: Containerization for Agentic Programming

The initial comparison considered Docker, Podman, containerd, Incus, Kubernetes, Firecracker, gVisor, Kata Containers, Nix, and Dev Containers.

The relevant requirements for an agentic programming workflow were identified as including:

* disposable development environments
* execution of arbitrary or potentially untrusted generated code
* dependency installation
* supporting services such as databases
* reproducibility
* parallel execution
* resettable environments
* CI/CD compatibility
* isolation and security

This led to a distinction between **developer-facing container tooling** and **secure execution infrastructure**.

### Docker

Docker was identified as the strongest compatibility baseline because of its ecosystem, Compose support, IDE integration, prebuilt images, networking, volumes, and broad adoption.

However, Docker's traditional daemon architecture introduces a significant security consideration for autonomous agents, particularly when agents can execute arbitrary generated commands and potentially interact with the Docker socket.

Docker therefore remains an important compatibility target but is not necessarily the ideal conceptual foundation for the execution engine.

### Podman

Podman was identified as particularly attractive for local agentic development because of its daemonless and rootless architecture.

The important architectural property is not merely Docker compatibility, but the ability to avoid giving an autonomous agent access to a privileged global daemon.

Podman therefore appeared to be a strong candidate for a **local execution backend**.

### Other execution technologies

Other technologies were considered according to their position on the isolation/complexity spectrum:

* **containerd** — lower-level container runtime, appropriate for infrastructure rather than direct developer interaction.
* **Incus** — system containers and lightweight VMs, potentially useful for richer persistent environments.
* **Firecracker** — microVM isolation, especially attractive for highly untrusted or large-scale agent execution.
* **gVisor** — stronger isolation while retaining container-oriented workflows.
* **Kata Containers** — container-compatible execution backed by lightweight VMs.
* **Kubernetes** — primarily relevant once execution needs to scale across many workers.
* **Dev Containers** — useful as a project-level environment specification and developer tooling abstraction.

The conclusion was that there is unlikely to be one universally correct execution technology.

---

## 3. The Important Architectural Distinction

The first major conclusion was:

> Containers should be treated as execution substrates, not as architectural concepts of EDASES.

The existing architecture does not describe an execution engine in terms of Docker, Podman, VMs, or any other runtime. Instead, the execution engine is responsible for executing methodology, maintaining engineering state, preserving reasoning, coordinating AI capabilities, and enforcing methodological correctness.

Consequently, an implementation could conceptually expose an abstract execution-provider layer:

```text
Execution Engine
        │
        ▼
Execution Provider
        │
        ├── Podman
        ├── Docker
        ├── Firecracker
        ├── Kubernetes
        ├── Incus
        └── Local Process
```

The methodology should specify required properties of an execution environment rather than prescribing which runtime supplies them.

This preserves the project's existing implementation-independence principle.

---

## 4. Execution Environments as Isolated Workspaces

The discussion then considered how environments could map onto engineering activities.

Instead of treating the entire software project as one persistent container, individual engineering activities could receive isolated workspaces:

```text
Requirement Analysis
        ↓
Environment A

Architecture Review
        ↓
Environment B

Implementation
        ↓
Environment C

Verification
        ↓
Environment D
```

The environment would be:

* reproducible
* attributable
* isolated
* resettable
* disposable where appropriate

The important distinction is that **the reasoning does not live inside the container**.

The container provides computational resources for an activity. The EDASES knowledge architecture remains responsible for preserving observations, assumptions, findings, decisions, challenges, validations, and other epistemic relationships.

This follows directly from the project's stated principle that reasoning is the primary engineering artefact and that epistemic relationships should remain explicit and traceable.

---

## 5. Containers as Experimental Laboratories

A second useful conceptualization emerged from the research-oriented nature of EDASES.

EDASES is explicitly an experimental research programme. Its outputs include research findings, conceptual models, evaluation frameworks, and capability assessments.

This suggests treating execution environments as **laboratories for engineering experiments**.

For example:

```text
Research Question
        ↓
Experiment Definition
        ↓
Specified Environment
        ↓
Execution
        ↓
Evidence
        ↓
Evaluation
```

A reproducible environment allows an experiment to be rerun under substantially identical conditions.

This is particularly relevant to AI capability evaluation, adversarial testing, and execution-engine research.

---

# 6. The Nix Question

The most significant shift in the discussion came from asking whether the level of environmental specification being proposed actually points toward **Nix**.

The answer was yes.

The distinction became:

> Containers answer "where does this execute?"
> Nix answers "what exactly is this execution environment?"

This reframed the role of containerization.

The earlier concept of an **Execution Environment** contained requirements such as:

* isolation level
* reproducibility
* required capabilities
* trust level
* persistence
* provenance

Those properties are more naturally represented by a declarative environment specification than by a container runtime itself.

Nix therefore appeared unusually well aligned with the EDASES requirements being discussed.

---

## 7. Nix as Environment Definition

Rather than defining an environment procedurally:

```text
Install Ubuntu
Install Rust
Install Node
Install PostgreSQL
Install testing tools
...
```

the environment could be represented declaratively.

Conceptually:

```text
Engineering Environment
    │
    ├── language/tool versions
    ├── system dependencies
    ├── services
    ├── build requirements
    └── auxiliary tools
```

Nix could then realise that specification.

This matters particularly for agentic workflows because autonomous agents are poor places to accumulate uncontrolled imperative state.

Instead of an agent repeatedly performing setup commands, the execution engine could request a named or versioned environment and materialize it deterministically.

Conceptually:

```text
Agent
  │
  ▼
Environment: ases-rust-web-v4
  │
  ▼
Nix
  │
  ▼
Reproducible Environment
```

The agent therefore consumes an environment rather than being responsible for constructing it.

---

## 8. Environment as an Engineering Artefact

The discussion suggested that an **Engineering Environment** may deserve to become a first-class concept in the eventual execution-engine model.

A preliminary conceptual definition was:

> An immutable, versioned specification describing the computational context required to perform an engineering activity.

Potential properties include:

* reproducible
* content-addressed
* attributable
* traceable
* executable

This would fit naturally with the project's existing treatment of reasoning and epistemic relationships as first-class engineering knowledge.

An engineering activity could conceptually reference an environment:

```text
Decision D-42
    │
    └── uses → Environment E-17
                    │
                    └── realised by → Nix specification
```

This creates an additional provenance relationship between engineering reasoning and the computational conditions under which that reasoning was operationalized or validated.

The discussion did **not** establish this as a finalized ASES concept. It was identified as a promising architectural direction requiring further research.

---

# 9. Nix and Containers Are Complementary

The conclusion was not that Nix should replace containers.

Instead, they occupy different layers:

```text
Knowledge / Engineering State
        │
        ▼
Engineering Environment Specification
        │
        ▼
Nix
        │
        ▼
Realised Environment
        │
        ▼
Podman / Docker / Firecracker / VM
```

Under this model:

**Knowledge model**

Defines why an environment is required and its relationship to the engineering activity.

**ASES**

Could eventually define what properties an environment must provide.

**Nix**

Provides one mechanism for precisely defining and reproducing the environment.

**Container/VM runtime**

Provides isolation and execution.

**Execution engine**

Orchestrates the entire lifecycle.

This is considerably cleaner than making Docker or Podman part of the methodology itself.

---

# 10. Potential Execution Architecture

A possible implementation architecture emerging from the discussion was:

```text
                    EDASES / ASES
                          │
                          ▼
                Engineering Activity
                          │
                          ▼
              Environment Specification
                          │
                          ▼
                       Nix
                          │
                    Realisation
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Podman       Firecracker    Docker
             │            │            │
             └────────────┴────────────┘
                          │
                          ▼
                     Execution
                          │
                          ▼
                     Evidence
```

The exact technology choices remain unresolved.

The important architectural property is that the execution engine does not need to know that a particular methodology requirement was satisfied specifically by Podman or Nix.

It needs to know that the required environment properties were satisfied and that the resulting execution is attributable and reproducible to the degree required by the activity.

---

# 11. Implications for Security

The container discussion also surfaced an important distinction between **environment reproducibility** and **execution isolation**.

They are related but separate concerns.

Nix can specify what exists in an environment.

It does not, by itself, solve the problem of securely executing arbitrary AI-generated code.

That remains the responsibility of the execution substrate.

Thus:

```text
Environment correctness
        ↓
Nix

Execution isolation
        ↓
Podman / Firecracker / gVisor / Kata / VM

Methodological enforcement
        ↓
Execution Engine
```

This separation is useful because security requirements may vary by task.

A trusted formatting task might use a local rootless container.

A task involving arbitrary generated binaries could require a stronger sandbox.

A large-scale adversarial evaluation might use disposable microVMs.

The same environment specification could potentially be realised using different isolation mechanisms.

---

# 12. Implications for EDASES

This discussion reinforced several existing architectural principles rather than changing them.

### Implementation independence

The architecture explicitly states that ASES is independent of implementation technologies and that the execution engine is an implementation of the methodology.

Therefore, neither Docker, Podman, nor Nix should prematurely become methodological dependencies.

### Mechanical enforcement

The project favors mechanical enforcement wherever practical.

Declarative, reproducible environments provide a potential mechanism for mechanically enforcing environmental assumptions rather than relying on agents to follow setup instructions.

### Traceability

The project treats reasoning and epistemic relationships as primary engineering assets.

Versioned environment specifications could become another traceable artefact connected to engineering activities, decisions, experiments, and evidence.

### Research before implementation

The current project is transitioning toward methodology execution while explicitly maintaining the rule that implementation should remain guided by methodology and research.

Consequently, this discussion should not be interpreted as a decision to adopt Nix, Podman, or any other technology at this stage.

---

# 13. What Was Actually Established

The strongest conclusions from the discussion were conceptual rather than technological.

1. **Containers are execution infrastructure, not part of the conceptual EDASES architecture.**

2. **The execution engine should ideally abstract over execution substrates.**

3. **Execution environments may deserve first-class representation.**

4. **The specification of an environment is conceptually distinct from the mechanism used to execute it.**

5. **Nix is particularly relevant to the specification/reproducibility side of this problem.**

6. **Podman, Docker, Firecracker, and similar technologies are candidates for the isolation/execution side.**

7. **The environment should potentially be attributable to an engineering activity and its reasoning/evidence.**

8. **The eventual architecture may therefore be closer to "environment specification → realisation → isolated execution" than simply "run agents in containers."**

No final technology selection was made.

---

# 14. Open Questions

The discussion leaves several questions for future EDASES research.

### What exactly is an Engineering Environment?

The preliminary definition needs refinement.

It is not yet clear whether it should represent only software dependencies, or also:

* operating-system characteristics
* hardware requirements
* network topology
* credentials/capabilities
* available tools
* resource limits
* persistence
* security boundaries
* external services

### Is Nix actually the appropriate implementation?

Nix appears strongly aligned with the desired properties, but this discussion did not constitute a comparative evaluation.

Other declarative or reproducible environment systems may warrant investigation.

### How should environment identity work?

A useful future question is whether environments should be:

* versioned
* content-addressed
* immutable
* named
* linked directly to commits
* linked to methodology activities
* linked to evidence

### How should environment requirements be expressed?

ASES may eventually specify properties rather than concrete environments.

For example:

```text
Requires:
    Rust >= X
    network = disabled
    filesystem = disposable
    database = PostgreSQL
    isolation = high
```

The execution engine could then resolve those requirements to an actual realisation.

### How much persistence is appropriate?

Some activities need disposable environments.

Others may require long-lived workspaces.

The methodology may therefore need to distinguish between execution contexts rather than assuming that every task is ephemeral.

### How should security levels map to execution substrates?

The system may eventually need an explicit mapping such as:

```text
Trust level
    ↓
Required isolation
    ↓
Execution provider
```

This could allow the same abstract methodology to execute locally or remotely without changing the methodology itself.

---

# 15. Overall Retrospective

The conversation began as a technology comparison—Docker versus Podman and alternative containerization systems—but ultimately revealed that this was probably the wrong abstraction level for EDASES.

The more important architectural question is **how the execution engine represents and realizes computational environments for engineering activities**.

Containers address the execution boundary.

Nix addresses reproducible environment definition.

The execution engine coordinates both.

This produces a more coherent conceptual model:

```text
ASES
  │
  ▼
Engineering Activity
  │
  ▼
Required Environment Properties
  │
  ▼
Environment Specification
  │
  ▼
Environment Realisation
  │
  ├── Nix
  │
  ▼
Execution Substrate
  │
  ├── Podman
  ├── Docker
  ├── Firecracker
  ├── VM
  └── other provider
  │
  ▼
Execution
  │
  ▼
Evidence + Engineering State
```

The key insight is therefore not "EDASES should use Nix" or "EDASES should use Podman."

It is that **the environment itself may be an explicit, reproducible, traceable engineering artefact**, with Nix-like technology potentially providing its realization and container/VM technology providing its execution and isolation.

That distinction should be preserved in subsequent EDASES research so that infrastructure choices do not prematurely become methodology. ЖΔλ
