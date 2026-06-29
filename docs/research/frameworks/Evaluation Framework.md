# Evaluation Framework

## Status

**Research Framework**

This document defines how EDASES evaluates both the ASES methodology and its implementations. It establishes the success criteria for research, ensuring that methodological evolution is driven by empirical evidence rather than intuition or process accumulation.

---

# Purpose

A methodology cannot be evaluated solely by whether it is followed.

A methodology is successful only if it measurably improves software engineering outcomes.

The purpose of this framework is to define the criteria by which EDASES determines whether ASES produces better software engineering results than alternative approaches, and whether proposed changes represent genuine improvements.

---

# Evaluation Philosophy

ASES is not intended to maximise documentation, process, or automation.

Its purpose is to maximise the ability of non-programmers to direct heterogeneous AI systems to produce software safely, efficiently and reliably.

Every methodological rule, implementation feature and architectural decision should ultimately support that objective.

---

# Primary Research Objective

The central research question of EDASES is:

> How can a methodology and supporting execution system enable non-programmers to use heterogeneous AI agents to engineer software that is safe, effective and economically viable?

All evaluation criteria derive from this objective.

---

# Evaluation Layers

Evaluation occurs at three distinct levels.

```text
Implementation
        ↓
Methodology
        ↓
Research
```

Each level answers a different question.

---

# Level 1 — Implementation Evaluation

Question:

> Does the implementation faithfully execute ASES?

Evaluation focuses on software behaviour rather than methodology.

Examples include:

- methodology rules enforced correctly
- invalid state transitions prevented
- required validation performed
- orchestration recommendations generated
- operational state maintained correctly
- repository integrity preserved

A technically successful implementation may still implement a poor methodology.

---

# Level 2 — Methodology Evaluation

Question:

> Does ASES improve software engineering practice?

Evaluation focuses on engineering outcomes rather than implementation features.

Evidence may include improvements in:

- software quality
- engineering consistency
- requirement traceability
- defect prevention
- architectural stability
- review effectiveness
- recovery after interruption
- successful collaboration between humans and AI systems

Methodological changes should only be adopted when supported by evidence.

---

# Level 3 — Research Evaluation

Question:

> Is EDASES producing validated knowledge?

Evaluation focuses on research quality.

Examples include:

- hypotheses tested
- findings replicated
- assumptions challenged
- methodology revisions justified
- experiments reproducible
- evidence traceable

The objective is the production of trustworthy knowledge rather than the accumulation of documentation.

---

# Primary Success Criteria

ASES should improve software engineering in the following areas.

## Safety

The methodology should reduce the probability that incorrect software progresses without detection.

Examples include:

- earlier identification of errors
- explicit validation
- traceable justification
- controlled promotion
- reduced propagation of incorrect assumptions

---

## Effectiveness

The methodology should increase the likelihood that produced software satisfies its intended purpose.

Measures may include:

- requirement satisfaction
- architectural consistency
- implementation correctness
- successful completion of engineering tasks

---

## Accessibility

ASES exists to enable software engineering by people who are not professional programmers.

Evaluation should consider:

- ability to complete projects
- dependence on programming expertise
- clarity of workflow
- cognitive burden placed on users

---

## Mechanical Error Reduction

The execution system should eliminate opportunities for predictable human and AI error wherever practical.

Examples include preventing:

- missing validation
- unsupported decisions
- orphaned reasoning
- inconsistent state
- forgotten assumptions
- invalid workflow progression

Errors prevented mechanically are preferable to errors prevented procedurally.

---

## Efficiency

ASES should reduce the resources required to engineer software.

Measures include:

- token consumption
- duplicated reasoning
- unnecessary model invocation
- unnecessary human intervention
- repeated context reconstruction

---

## Throughput

The methodology should reduce the time required to progress from idea to validated software.

Measures may include:

- project completion time
- review turnaround
- iteration speed
- parallelisation of AI work
- recovery from interruptions

---

## Model Interoperability

ASES should function independently of any individual AI model.

Evaluation should consider:

- successful substitution of models
- heterogeneous orchestration
- resilience to changing model capabilities
- portability across providers

---

# Research Principles

Every proposed methodological change should answer five questions.

## 1. What problem does it solve?

The problem should be clearly identified.

---

## 2. What evidence supports it?

Evidence should exist before adoption.

---

## 3. How will improvement be measured?

Success must be observable.

---

## 4. What cost does it introduce?

Costs may include:

- additional work
- increased complexity
- computational expense
- reduced usability

---

## 5. Under what circumstances should it be removed?

Methodological rules are provisional.

Rules should be removed when evidence no longer supports their continued use.

---

# Rejecting Process Inflation

ASES rejects process that exists solely to support itself.

Every activity should ultimately contribute to one or more of the primary success criteria.

If an activity cannot demonstrate measurable value, it should be reconsidered.

The methodology should evolve toward greater effectiveness with the minimum necessary process.

---

# Experimental Validation

EDASES validates ASES through experimentation.

Typical experiments may compare:

- different orchestration strategies
- alternative review workflows
- automation approaches
- execution engine behaviour
- AI model combinations
- implementation techniques

Experimental outcomes inform subsequent revisions to ASES.

---

# Evidence Hierarchy

Not all evidence carries equal weight.

Evidence should be considered in approximately the following order.

1. Replicated experimental results
2. Successful application across multiple projects
3. Controlled case studies
4. Individual project observations
5. Expert judgement
6. Speculation

Higher-quality evidence should take precedence when methodology changes are proposed.

---

# Continuous Improvement

ASES is expected to evolve.

Methodological revisions should be based on accumulated evidence gathered through practical application, experimentation and review.

The objective is not methodological stability.

The objective is continual improvement supported by evidence.

---

# Relationship to Other Documents

This document defines how success is measured.

The Concept: Levels of Abstraction document defines where evaluation occurs within the project structure.

The ASES methodology defines the current process being evaluated.

The Methodology-to-Requirements Mapping derives software capabilities from that methodology.

Execution Engine implementations provide the mechanisms through which the methodology is enacted and evaluated.


# Relationship to Process

This document defines what is evaluated and why; individual experiments should define how those outcomes are measured and what constitutes a statistically or practically meaningful improvement.