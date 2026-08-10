---
title: Clean Room Execution Guide
program: ASES
layer: Methodology
document_type: Guide
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - AI Orchestration Guide
  - Documentation Standard

consumed_by:
  - AGENTS.md

related_documents:
  - AI Capability Registry

supersedes: []
last_updated: 2026-08-10
---

# Clean Room Execution Guide

## Purpose

This guide describes how to obtain independent AI analysis when isolation from an existing conversational context is required.

A clean room execution ensures that an AI model performs reasoning without influence from prior discussion, intermediate conclusions or repository history beyond the information explicitly provided.

---

# When to Use Clean Room Execution

Clean room execution is appropriate when:

* conducting adversarial reviews;
* evaluating independent reasoning;
* comparing multiple AI models;
* validating methodology;
* measuring capability objectively;
* investigating alternative architectural approaches.

It should not be used for routine repository maintenance where continuity of context is beneficial.

---

# Principles

A clean room execution should satisfy the following principles:

* independent context;
* reproducible inputs;
* explicit prompts;
* isolated reasoning;
* preserved outputs.

The objective is to maximise independent analysis.

---

# Required Inputs

Every clean room execution should define:

* the objective;
* the supplied documentation;
* the expected output;
* any evaluation criteria;
* any constraints.

Only these materials should be available to the reviewing model.

---

# Isolation Requirements

The reviewing model should not have access to:

* previous review results;
* conclusions from other reviewers;
* repository history beyond supplied material;
* human interpretations not included in the prompt.

Independent reasoning is the primary objective.

---

# Execution Methods

Clean room execution may be achieved through any mechanism providing genuine contextual isolation.

Examples include:

* launching a new AI conversation;
* using an isolated background agent;
* invoking a model through a provider API;
* executing an external orchestration workflow.

The implementation mechanism is less important than preserving contextual independence.

---

# Tool Failure

If the preferred execution mechanism fails:

1. Report the failure.
2. Preserve any completed work.
3. Explain why the failure occurred.
4. Request further instruction.

Do not silently substitute an execution that violates clean room isolation.

---

# Native API Execution

Where repository tooling cannot provide isolated execution, direct invocation of an AI provider's API may be used.

Typical workflow:

1. Obtain credentials from the configured execution environment.
2. Create a standalone script or workflow.
3. Supply only the intended review materials.
4. Execute the request.
5. Preserve the complete output.
6. Record the execution method for reproducibility.

Implementation details are intentionally omitted from this guide, as they are environment-specific.

---

# Recording Results

Each execution should record:

* execution date;
* model identifier;
* execution method;
* supplied inputs;
* prompt;
* generated output;
* reviewer observations.

This information supports reproducibility and later evaluation.

---

# Relationship to the Methodology

Clean room execution is an operational technique supporting the ASES methodology.

It is not itself part of the methodology, nor is any specific implementation technology mandated.

Future execution engines may automate this process while preserving the same underlying principles.

---

# Evolution

As orchestration tooling evolves, the mechanisms described in this guide may change.

The defining characteristics of clean room execution are contextual independence, reproducibility and explicit evidence—not any particular software implementation.
