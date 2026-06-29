---
title: Repository Overview
program: EDASES
layer: Research
document_type: Introduction
status: Active
authority: Derived
canonical_repository: edases
supersedes: README.md (previous version)
---
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

New contributors should begin with:
1. `ORIENTATION.md`
2. `docs/standards/Documentation Standard.md`
3. The foundational documents referenced from the orientation guide

AI contributors should additionally read:
* `AGENTS.md`

## Current Status

The project is currently transitioning from exploratory research toward the design of a methodology execution engine.

Recent work has established:
* a separation between research (EDASES), methodology (ASES) and implementation
* reasoning as the primary object of interest rather than source code history
* epistemic relationships as the foundation of engineering knowledge
* levels of abstraction as the organising structure of the project
* methodology execution as the next stage of research

## Contributing

Contributions should follow the project's documentation standards and methodology.

Please read `ORIENTATION.md` before making architectural, methodological or implementation changes.

AI agents should additionally follow the instructions contained within `AGENTS.md`.

## License

See the accompanying LICENSE file for licensing information.

## Documentation

Project documentation follows a common documentation standard that defines document classification, abstraction layers, dependencies and relationships.

Contributors should begin with:
1. `ORIENTATION.md`
2. `docs/standards/Documentation Standard.md`

The orientation guide introduces the project structure, while the documentation standard defines how canonical project knowledge is represented.