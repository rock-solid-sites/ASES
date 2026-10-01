---
title: Kernel-0 Direct RTL Realization Experiment
program: EDASES
layer: Research
document_type: Research Protocol
status: Active
authority: Derived
canonical_repository: ASES
depends_on:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
  - Kernel-0 Finite Model
  - Kernel-0 Re-Minimization After Stronger Profiles
consumed_by:
  - Kernel-0 direct RTL realization experiment
related_documents:
  - Kernel-0 Evidence Packet
  - Kernel-0 Reasoning Phase Result
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-10-01
---

# Kernel-0 Direct RTL Realization Experiment

## Purpose

Test whether the already-derived Kernel-0 semantics are tractable as a **direct fixed low-level state-transition machine**, without assuming a processor, stored program, interpreter, operating system, software runtime, scheduler, or general runtime programmability inside the trusted realization.

This is an implementation-discriminating research experiment. It does **not** claim that RTL, synchronous logic, FPGA fabric, or any particular circuit technology is the final minimal substrate. The first goal is to make the Kernel functional and testable at a level substantially below a conventional software implementation, then record which mechanisms the realization actually forces.

## Same-ref rule

All governing inputs for one run must be read from the **same repository ref/commit as this protocol**. Do not mix main, an older Kernel-0 commit, a historical implementation branch, or cached copies unless the experiment explicitly records the comparison.

If a fresh agent is given this protocol, it should follow the source hierarchy below instead of discovering a context set from the wider repository.

## Source hierarchy for this experiment

### Normative semantic inputs

These define what the realization must mean.

1. [Kernel-0 Abstract Semantics](./Kernel-0-Abstract-Semantics.md)
2. [Kernel-0 Verification Obligations](./Kernel-0-Verification-Obligations.md)

The realization may choose representations and mechanisms, but it must not silently revise these semantics to fit an implementation.

### Bounded executable target and oracle

These define the first concrete profile to realize.

3. [Kernel-0 Finite Model](./Kernel-0-Finite-Model.md)
4. [kernel0_finite_model.py](./kernel0_finite_model.py)

The finite model is a bounded consumer instantiation, not the universal Kernel. Its encoded state, proposal alphabet, policy choices, and bounds are the target for this first tractability experiment. The Python model is reference/assurance apparatus, not part of the trusted low-level realization.

### Reduction constraint

5. [Kernel-0 Re-Minimization After Stronger Profiles](./Kernel-0-Re-Minimization.md)

Use this to prevent concrete mechanisms from earlier experiments from being promoted into Kernel primitives without necessity. In particular, prior uses of Python, JSON, SQLite, Unix processes, transactions, generation-like labels, global serialization, or other realization machinery do not establish requirements for this experiment.

### Immediate research result carried forward

Recent executable-substrate work established only a realization contract, not a final physical architecture: semantic configurations must have faithful concrete embodiments; completed advancement must expose exactly the designated semantic successor; step boundaries must be preserved; and actual execution requires explicit realization assumptions. A smallest executable witness is not automatically a substrate adequate for Kernel-0.

This experiment therefore tests a stronger practical question: whether the **specified bounded Kernel-0 transition system itself** can be realized directly as fixed low-level transition logic.

## Default exclusions

Do not load or continue earlier realization architectures unless a concrete obstruction in this experiment requires comparison.

The following are outside the default input set:

- Kernel-0-Realization-Comparison.md
- Kernel-0-Realization-Experiment.md
- Kernel-0-Realization-Conformance.md
- Kernel-0-Stronger-Realization.md
- crash/recovery, protected external-effect, composition, generalization, and whole-history assurance implementations beyond what the bounded target itself requires
- Work Unit implementation/design material
- Observer, Processor, Orchestrator, scheduling, general execution-engine, and higher-layer architecture

They remain valid provenance or stronger-profile evidence. They are excluded here to avoid inheriting solved implementation choices as premises.

## Realization target

Realize the bounded finite-model transition behavior as fixed low-level logic with an explicit correspondence of the form

~~~text
encoded authoritative state S
        +
encoded presented proposal I
        ↓
fixed transition logic
        ↓
encoded next authoritative state S'
        +
resolved outcome
~~~

The transition law is fixed by the build. Inputs are data presented to that law; they are not executable programs and cannot redefine the law at runtime.

The initial realization may use synchronous RTL and ordinary simulation/synthesis tooling as **laboratory apparatus**. Any clock, simulator, synthesis tool, FPGA configuration mechanism, host process, testbench, or formal checker must be classified as either realization assumption or assurance scaffolding rather than silently becoming a Kernel primitive.

## Required correspondence

At minimum, define an explicit encoding/decoding between the RTL-visible state and the finite model's authoritative state and inputs.

For every well-formed state/proposal combination within the declared finite-model bounds:

1. a committed RTL transition must decode to the same authoritative successor as the reference model;
2. a denied proposal must leave decoded authoritative state unchanged;
3. no partial or intermediate hardware state may be exposed as an additional authoritative Kernel transition;
4. the next resolved operation must begin from the last completed authoritative state;
5. all retained finite-model invariants must hold after every completed transition;
6. no transition outside the declared bounded input/state semantics may be counted as evidence of equivalence.

If exact exhaustive equivalence is impractical for the chosen encoding, record the precise obstruction rather than weakening the claim silently.

## Tractability evidence

The experiment should produce enough evidence to answer whether direct processorless realization is practical for the bounded Kernel target:

- explicit state encoding and state-bit count;
- fixed transition-logic structure;
- required sequencing or completion machinery, if any;
- simulation/formal equivalence evidence against the reference model;
- synthesis result and basic resource measurements when a synthesizable realization is produced;
- the trusted assumptions introduced by the realization;
- a mechanism ledger classifying each mechanism as semantic requirement, realization choice, or assurance scaffolding;
- any Kernel behavior that unexpectedly forces iteration, storage, serialization, arbitration, configurable logic, or another stronger mechanism.

The experiment is successful even if it falsifies direct RTL tractability, provided the obstruction is demonstrated against a specific required Kernel behavior.

## Escalation rule

General runtime programmability is **not** part of the baseline.

Do not introduce a processor, interpreter, stored program, general programmable controller, or equivalent trusted mechanism merely for implementation convenience. If fixed structural logic proves inadequate or unreasonably intractable, first identify:

1. the exact required Kernel transition or property that causes the obstruction;
2. why structural composition or finite fixed logic cannot realize it adequately;
3. the weakest additional mechanism that would remove the obstruction.

Limited sequencing, handshaking, buffering, or configurable structure may be considered only when a concrete need is established and recorded. General programmability is the last escalation, not the starting architecture.

## Non-goals

This experiment does not attempt to establish:

- the universally weakest physical computing substrate;
- asynchronous or clockless minimality;
- production FPGA/hardware architecture;
- independent power-loss or storage-recovery guarantees not present in the bounded target;
- exactly-once external effects;
- Work Unit adequacy beyond the finite profile;
- arbitrary program execution;
- a final EDASES execution engine.

## Stopping condition

Stop the first experiment when either:

- a direct low-level realization has a documented mapping to the bounded finite model, passes the strongest practical bounded equivalence checks, and has a synthesis/tractability record; or
- a concrete, reproducible obstruction demonstrates which stronger mechanism is required.

Do not broaden the architecture to solve later layers before this result is recorded.
