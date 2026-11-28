---
version: 2026-11-24.1
title: Repository Overview
program: EDASES
layer: Research
document_type: Introduction
status: Active
authority: Derived
canonical_repository: edases
supersedes: README.md (previous version)
last_updated: 2026-11-24
---

> **Current ASES documentation:** [documentation navigation and audit index](docs/README.md), [current operational skills](skills/current/README.md) and the [canonical task-scoped information method](docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md). This repository also preserves EDASES research and historical material; its presence alone does not make it an active agent instruction.
# EDASES
**Epistemically-Driven Agentic Software Engineering System.**
EDASES is a research programme investigating how non-programmers can safely and effectively use heterogeneous AI systems to engineer software.
The project explores how software engineering can move from conversational interaction with individual AI models to structured, evidence-driven collaboration between humans, AI systems and automated tooling.
The long-term objective is to develop a methodology that is:
* verifiably safe at every stage
* evidence-driven rather than opinion-driven
* independent of any individual AI model or provider
* mechanically enforceable wherever practical
* capable of evolving through empirical research

## Project Structure

The project consists of three closely related layers.

### EDASES — Research

EDASES is the research programme.
Its purpose is to investigate, evaluate and validate improved approaches to AI-assisted software engineering through experimentation and evidence.
The outputs of EDASES are research findings rather than software.

### ASES — Methodology

The Agentic Software Engineering System (ASES) is the methodology produced by the EDASES research programme.
ASES defines how AI-assisted software engineering should be conducted.
It is intentionally independent of any particular implementation, AI provider or software platform.

### Execution Engine

The execution engine is a software implementation of the ASES methodology.
Its purpose is not to replace software engineers, but to execute and enforce the methodology mechanically by:
* maintaining engineering state
* preserving reasoning and evidence
* coordinating heterogeneous AI capabilities
* reducing predictable human and AI error
* supporting efficient software engineering workflows

The execution engine is an implementation of ASES, not the methodology itself.

## Research Focus

Current research investigates questions including:
* How can reasoning remain traceable throughout software engineering?
* How should epistemic relationships be represented and preserved?
* How can AI capabilities be evaluated objectively?
* How should multiple AI systems collaborate effectively?
* How can software engineering methodology be executed mechanically rather than procedurally?

## Repository Organisation

This repository contains research, methodology and implementation planning.
Canonical documentation is organised by abstraction level rather than implementation status.

The [empirical testing laboratory](testing/README.md) contains experimental assurance procedures, cross-project lessons and minimal counterexample pointers. It is **not** an independent canonical method; active methodology remains under `docs/methodology/`.

New contributors should begin with:
1. `ORIENTATION.md`
2. `docs/standards/Documentation Standard.md`
3. The foundational documents referenced from the orientation guide

AI contributors select the applicable sources through the [current documentation index](docs/README.md) and [current skills](skills/current/README.md). AGENTS.md is a compatibility adapter, not an additional mandatory read.

## Current Status

The project combines current methodology, experimental component engineering and continuing research. The [Execution Engine Vision](docs/architecture/Execution%20Engine%20Vision.md) distinguishes established Kernel/Work Unit requirements from the separate November native authority and Rust execution experiments. These draft experiments are not a deployed integrated engine. [Historical architecture and experiment evidence](docs/historical/Engine%20Architecture%20and%20Experiment%20History.md) explains the earlier designs and current work pointers.

Recent work has established:
* a separation between research (EDASES), methodology (ASES) and implementation
* reasoning as the primary object of interest rather than source code history
* epistemic relationships as the foundation of engineering knowledge
* levels of abstraction as the organising structure of the project
* methodology execution as the next stage of research

## Contributing

Contributions should follow the project's documentation standards and methodology.

Please read `ORIENTATION.md` before making architectural, methodological or implementation changes.

AI agents should select relevant current sources and verify task-specific authorization using the task-scoped method; do not load historical instructions as active policy.

## License

See the accompanying LICENSE file for licensing information.

## Documentation

Project documentation follows a common documentation standard that defines document classification, abstraction layers, dependencies and relationships.

Contributors should begin with:
1. `ORIENTATION.md`
2. `docs/standards/Documentation Standard.md`

The orientation guide introduces the project structure, while the documentation standard defines how canonical project knowledge is represented.