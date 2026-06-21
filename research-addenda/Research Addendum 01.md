# EDASES Research Addendum 01

## Architectural Reframing & Harness Strategy

### Purpose

This addendum records significant architectural insights that emerged during discussion after publication of the initial EDASES Charter v4, Research Program v4, Assumption Register v4, and Research Handoff.

These findings have not yet been formally validated and should be treated as working hypotheses for future investigation.

---

# 1. Reframing the Core Question

The project originally began from the question:

> Which coding harness should serve as the foundation of the system?

Examples considered:

* OpenCode
* OpenClaudia
* CodeWhale

As discussion progressed, the question evolved into:

> What kind of system is actually required to satisfy EDASES objectives?

This distinction is important.

The first question assumes an existing harness architecture is fundamentally suitable.

The second question treats that assumption as unproven.

---

# 2. New Architectural Hypothesis

## AH-001

### Hypothesis

EDASES requirements may not align with the design assumptions of existing coding harnesses.

### Rationale

Most existing harnesses appear optimized for:

Human Programmer
↔ AI Assistant
↔ Repository

EDASES appears increasingly optimized for:

Principal
→ Organization
→ Roles
→ Agents
→ Verification
→ Outcomes

The central actor changes from:

"Programmer"

to:

"Principal"

This may require different architectural priorities.

---

# 3. Harnesses As Subsystems

A recurring observation is that many of the most valuable developments in historical projects occurred outside code-generation tooling.

Examples include:

* CLAUDE.md evolution
* Session handoffs
* Retrospectives
* Issue tracking
* Crosslink adoption
* Multi-agent coordination
* Multi-model coordination

These developments improved project outcomes without directly improving code generation.

### Working Hypothesis

Harnesses may ultimately be execution engines rather than the architectural center of the system.

---

# 4. Proposed System Layers

A possible EDASES architecture consists of multiple layers.

## Organizational Layer

Responsible for:

* Task coordination
* Role management
* Workflow management
* Information flow

Potential tools:

* Crosslink
* Future organizational registries

---

## Knowledge Layer

Responsible for:

* Persistent project memory
* Historical learning
* Decision capture
* Knowledge reuse

Potential tools:

* Documentation systems
* Knowledge graphs
* Evidence registries

---

## Capability Layer

Responsible for:

* Model evaluation
* Capability tracking
* Routing decisions
* Workforce composition

Potential tools:

* Capability Registry
* Benchmark systems

---

## Verification Layer

Responsible for:

* Testing
* Review
* Formal verification
* Confidence generation

Potential tools:

* Thermite
* VDD systems
* Test orchestration

---

## Execution Layer

Responsible for:

* Code generation
* Tool execution
* File modification

Potential tools:

* OpenClaudia
* OpenCode
* CodeWhale
* Future harnesses

---

## Principal Layer

Responsible for:

* Oversight
* Evidence review
* Decision support
* Progress visibility

Potential tools:

* Dashboards
* Reports
* Verification artifacts

---

# 5. Progressive Externalization

A major pattern emerged during discussion.

Historical workflow evolution appears to follow:

Chat Sessions
→ Session Notes
→ CLAUDE.md
→ Handoffs
→ Retrospectives
→ Structured Tracking
→ Crosslink
→ Multi-Agent Coordination

This pattern suggests a broader principle.

## AH-002

### Hypothesis

Project success improves as important information is progressively externalized from model memory into persistent organizational systems.

### Implications

The value of Crosslink may not be Crosslink itself.

The value may be that Crosslink is one implementation of a broader externalization pattern.

Future systems should evaluate whether they increase or decrease organizational memory.

---

# 6. Harness Landscape Analysis

A new research phase is proposed.

## Objective

Evaluate existing harnesses against EDASES requirements before selecting an architectural foundation.

### Deliverables

#### Harness Evaluation Framework

Evaluate:

* Organizational intelligence
* Knowledge management
* Verification support
* Capability awareness
* Principal experience
* Operational characteristics

#### Harness Capability Matrix

Map:

Requirements
↔ Existing Solutions
↔ Missing Capabilities

#### Benchmark Suite

Standardized tasks for comparing harnesses across:

* Planning
* Coordination
* Verification
* Cost efficiency
* Knowledge persistence
* Principal visibility

---

# 7. New Research Questions

## HS-001

### Assumption

Requirements-driven harness evaluation produces better architectural decisions than selecting a foundation based on preference or popularity.

Status:
Plausible

---

## HS-002

### Research Question

Do existing coding harness architectures align with EDASES requirements?

Status:
Unknown

Priority:
High

---

## HS-003

### Research Question

Should a coding harness be the foundation of EDASES, or merely one subsystem within a larger organizational platform?

Status:
Unknown

Priority:
High

---

# 8. Reinterpretation of Existing Evidence

The strongest evidence collected so far may not support conclusions about:

* Specific models
* Specific harnesses
* Specific frameworks

Instead, current evidence appears to support conclusions about:

* Organizational design
* Information flow
* Knowledge persistence
* Role specialization
* Verification accessibility

This suggests that future research should prioritize these domains before making major implementation commitments.

---

# 9. Current Working Conclusion

The project should not currently assume that:

* OpenCode is the correct foundation.
* OpenClaudia is the correct foundation.
* CodeWhale is the correct foundation.
* Any existing harness architecture is sufficient.

The purpose of future harness research is not to identify the "best harness."

The purpose is to determine:

1. Which capabilities already exist.
2. Which capabilities are missing.
3. Whether existing harness architectures align with EDASES objectives.
4. Whether EDASES requires an architectural layer above current harness designs.

This remains an open question and should be treated as a first-class research topic.
