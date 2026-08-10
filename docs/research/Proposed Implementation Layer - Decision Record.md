---
title: Proposed Implementation Layer - Decision Record
program: EDASES
layer: Research
document_type: ADR
status: Archived
authority: Derived
canonical_repository: edases

depends_on: []

consumed_by: []

related_documents:
  - Clean Room Execution Guide

supersedes: []
last_updated: 2026-08-10

# Status note: Decision D1 on issue #341 superseded this record's conclusion.
# Clean Room Execution theory/setup is classified as Methodology; only its
# implementation is classified as execution/tooling.
---

I actually think you've uncovered an architectural distinction that the documentation doesn't currently express.

The Clean Room Execution Guide is neither methodology nor research. It's an implementation of methodology.

That means it belongs in the tooling layer, alongside whatever execution engine or orchestration framework you're using.

Looking at the three layers:

EDASES asks: Should independent clean-room execution exist?
ASES says: Certain evaluations require independent reasoning.
Tooling answers: Here's how Opencode (or Claude Code, etc.) achieves that.

So I'd move it out of the canonical documentation entirely.

Whether it becomes a skill or tooling documentation depends on whether it is intended to be executed or merely understood.

If it's documentation

Its audience is humans.

docs/tooling/
    clean-room-execution.md

It explains how the current tooling works.

If it's a skill

Its audience is AI agents.

.skills/
    clean-room-review/
        SKILL.md
        template.md
        scripts/

or whatever Opencode's skill layout is.

The skill contains:

when to invoke it;
what inputs it requires;
how to construct prompts;
how to invoke providers;
how to capture outputs;
failure handling.

That makes it executable knowledge rather than descriptive documentation.

Given where this project is heading—towards an execution engine that mechanically enforces methodology—I think skills are the more natural abstraction.

The progression becomes:

EDASES
    discovers that clean-room execution improves evaluation

        ↓

ASES
    requires independent review under defined circumstances

        ↓

Skill
    implements that requirement for a particular environment

        ↓

Execution Engine
    eventually automates skill invocation entirely

That fits the architecture you've been developing remarkably well.

One thing I'd also consider is introducing a new document category beneath the tooling layer:

Tooling
    Documentation
    Skills
    Templates
    Scripts

Documentation explains the tooling.

Skills operationalize the methodology.

Templates standardize inputs and outputs.

Scripts perform the implementation.

That hierarchy maps cleanly onto the distinction you've been making between methodology and implementation, and it should transfer well whether you're using Opencode today or another orchestration environment in the future. 構技実

How do we formalize that?

I think this should become part of the project architecture rather than just an implementation detail. Right now, your architecture describes documents well, but it doesn't describe executable knowledge.

I'd formalize it as a first-class distinction:

Knowledge
    │
    ├── Canonical Documents
    │       Define what is true.
    │
    ├── Derived Documents
    │       Explain what is true.
    │
    └── Executable Assets
            Implement what should happen.

The key insight is that skills are not documents. They are executable implementations of methodology.

From there, the tooling layer naturally becomes:

Tooling
│
├── Documentation
│      Human-readable guidance
│
├── Skills
│      Executable methodology
│
├── Templates
│      Standardized prompts and outputs
│
├── Scripts
│      Automation
│
└── Configuration
       Environment-specific behaviour

Then each asset type has a single responsibility:

Asset	Purpose	Changes when...
Canonical document	Defines concepts or methodology	Research changes
Guide	Explains methodology	Methodology changes
Skill	Executes methodology	Tooling capabilities change
Template	Standardizes interaction	Workflow changes
Script	Automates execution	Implementation changes
Configuration	Adapts to an environment	Deployment changes

This also gives you a clean dependency hierarchy:

Research
    ↓
Methodology
    ↓
Requirements
    ↓
Tooling Specification
    ↓
Skill
    ↓
Script

Notice the addition of Tooling Specification.

I think that's the missing abstraction. A skill shouldn't implement a methodology document directly. Instead:

ASES says: "Independent reviews must be performed in a clean room."
A Tooling Specification says: "A clean-room review capability must accept these inputs, produce these outputs, satisfy these invariants, and expose this interface."
A Skill implements that specification for Opencode.
Another Skill could implement the same specification for Claude Code.
The future Execution Engine could implement it internally without any skills at all.

That separation means your methodology never becomes coupled to a particular orchestration framework.

In fact, I'd add a fourth top-level layer to the project model—not as a replacement, but as a refinement:

EDASES
    Research

        ↓

ASES
    Methodology

        ↓

Tooling Specifications
    Platform-independent execution contracts

        ↓

Implementations
    Opencode skills
    Claude Code skills
    Scripts
    Execution Engine

The Tooling Specifications layer acts like an API between methodology and implementation. It tells implementers what a capability must do, without dictating how it is realized. As the execution engine matures, it can replace individual skills while still conforming to the same specifications, preserving both traceability and portability.