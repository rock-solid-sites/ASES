---
title: Kernel-0 Machine Realization Family Reduction
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 573
baseline_commit: 09d7d3854d2210fb668b30feae102a0ea25ee1b3
depends_on:
  - Kernel-0 Machine Realization Investigation
  - Kernel-0 Machine Realization Evidence Record
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
consumed_by:
  - Kernel machine realization formalization and experiments
related_documents:
  - Kernel-0 Machine-Adjacent Realization Input Packet
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Kernel-0 machine realization family reduction

## Continuation boundary

This continuation attacks the classification before T0–T6 begins. It starts from `09d7d3854d2210fb668b30feae102a0ea25ee1b3`: [investigation](./Kernel-0-Machine-Realization-Investigation.md), blob `81aefad8cee1c3be4158c1bcccc8976333762025`; [evidence record](./Kernel-0-Machine-Realization-Evidence.md), blob `3f09a5bf7a84f46acdbb1873f315fcee1b39bdbb`. The packet, selected semantic/profile sources, recorded expansions and provisional-delta conditions remain exactly those pinned by that investigation. No additional repository or external source is needed for this classification attack. No downstream prototype, model or independent review has been launched.

## 1. Result: replace the family partition with an explicit assurance structure

**The three-family classification does not survive as an irreducible partition.** F1 is a way to constrain untrusted behavior; F2 is an instruction-based implementation; F3 mixes a digital implementation with a requirement that verification reach its digital interface. The same machine can satisfy all three descriptions.

The smallest justified architectural classification is **one physically enforced, stateful authority/commitment schema**, parameterized by its admitted interference, effect topology, loss domains and assurance boundary. This is a common realization schema, **not a proved equivalence class of physical realizations**. Different configurations can still have incomparable assumptions. Two materially different **assurance cases** must remain visible:

- **Execution-contract cut:** the argument assumes a lower executor/platform contract, such as an interpreter, ISA/protection or device contract.
- **Digital-model cut:** that behavior is checked down to a specified circuit/handshake model; physical implementation and any unchecked model/tool links remain assumed.

These are possible stopping points, not two irreducible machine species. A native interpreter can have a digital-model proof; a hardwired appliance can have only an assumed functional contract. Neither the word native nor digital tells the consumer which case applies. Multiple intermediate cuts are possible.

F1 is eliminated as a separate physical family. F2/F3 remain useful implementation descriptions and potentially independent assurance paths, but their categorical irreducibility is withdrawn. **No assumption-preserving physical replacement of every native machine by every direct circuit, or conversely, is established.** The reduction removes a misleading partition; it does not turn missing lower proofs into evidence.

## 2. What counts as a reduction

Fix the policy, required successful histories, consumer observations, protected effect/authorization events, capacities and selected failures from the original investigation. Also fix what hostile external actions the implementation must tolerate. A transformation cannot succeed by dropping a sink, treating accepted bytes as candidates, excluding an allowed attacker action, or redefining engine loss to spare its sole copy of state.

Represent an assurance case by its physical system `P`, admitted environment `U`, failure projection `F`, observations `O`, residual assumptions `A`, and refinement argument `Π`. An assumption-preserving reduction must map **all** those elements, retain bounded successful behavior, and require no new unproved premise. There are three different operations:

1. **Regroup/combine a description or proof:** the physical machine and assumptions are unchanged.
2. **Discharge a premise:** supply a proof/validation of a previously assumed lower behavior, including its own residual assumptions.
3. **Replace machinery:** construct another physical realization and establish its effect, interference and loss correspondence.

Only the first follows from composing existing relations. For example, if `R_PD` relates physical behavior to a digital model and `R_DK` relates that model to the target, define `R_PK(p,k)` by the existence of a related `d`. Composition retains the premises of both relations. If a relation is merely assumed, composition does not verify it. A composed trace argument also needs the original progress/non-vacuity and failure correspondence; safety inclusion alone does not establish those.

This rule prevents the false argument that any two universal machines are interchangeable. Computability says nothing about stale ingress, a live writable alias, irreversible IO or a reset destroying retained contents.

## 3. Follow each candidate to its lowest boundary

| Candidate and reduction attempt | Lowest trusted boundary and result |
| --- | --- |
| **F1 implemented as software → native authority implementation** | Include the interpreter/validator, exact executable, imports, retaining domain and platform. The native program processes adversarial language input as data. Its language proof is a factor of its whole native-behavior argument. No MMU or arbitrary-native-guest assumption is added merely by regrouping this existing machine. The dedicated trusted-program subcase of F2 already admits this structure. Language confinement remains an obligation but ceases to define a separate physical family. |
| **F1 implemented directly as a language machine → digital appliance** | If the device directly implements the confined operations, there need be no conventional native ISA beneath them. The language is the device's behavioral contract; the circuit must realize that contract and all relevant IO/loss behavior. This is an F1/F3 overlap, not a fourth family or proof that the device is correct. |
| **F2 → description as a digital machine** | Compose the actual processor, loaded program, memory, protection and devices. Its digital state includes instruction decoding/program state. Regrouping leaves every ISA/protection, IO and physical assumption intact. It does **not** satisfy the old F3 requirement for checked circuit-level behavior unless that missing correspondence is supplied. The remaining distinction is the assurance cut, not an irreducible native authority function. |
| **F3 → native execution of an equivalent transition function** | A CPU can be proposed to evaluate the same finite transition function, but that introduces its executable/ISA, IO and loss-domain obligations. The direct-circuit case does not imply them. This is not an unconditional assumption-preserving physical reduction. It is a candidate replacement requiring evidence. |
| **F2 → specialized circuit without the ISA abstraction** | For a finite configuration the processor/program behavior can be described jointly, without a reusable ISA specification. A joint proof can establish the target directly. Replacing the actual hardware by specialized logic is a further step; it must preserve all hostile inputs, interruption points and retained-state domains. Neither correctness nor failure preservation follows from specialization alone. |

Thus the overlap is substantive, not just terminology: a language machine's confinement can be implemented by the same native instructions and proved through the same digital circuit. Conversely, **flattening an assurance graph is not shrinking its trusted assumptions**. The original F3 membership rule classified an embedded processor differently depending on whether its circuit proof existed; that is evidence status, not a new necessary architecture.

The common schema has a nontrivial necessity argument. Remove trustworthy distinctions between current and invalid authority and the required old-denied/new-accepted histories become indistinguishable. Remove protected continuing state and selected loss destroys required observations. Allow an uncontrolled route to change accepted meaning and an otherwise perfect transition proof admits a forbidden physical history. These facts require physically enforced constraints on state/effect evolution, independently of whether the implementation has a named checker, interpreter or protection unit. They do not require one component or one global order for unrelated effects.

## 4. Is a fourth family hidden by the reduction?

Three apparent alternatives were tested conceptually:

- **Everything correct by construction, with no separate runtime monitor.** All reachable transitions of the trusted realization satisfy the guarded policy. This is allowed: `G/E/I` are semantic conditions, not mandatory separate calls. Its correctness argument must cover arbitrary admitted proposals and current authority updates. It is an integrated configuration of the same schema, not a monitor-free physical trust claim.
- **An untrusted generator supplies certified transitions.** The checker and accepting state/effect boundary still need current binding, retention and non-bypassability. A stateless checker given an old valid certificate cannot distinguish histories separated by revocation unless current information is supplied by a trusted source. Moving that source to a sink or remote service retains it in the combined boundary.
- **Distributed or diverse cooperating enforcers.** Their joint state, gates and recovery relation can be represented as a product/composition while preserving each fault assumption. Distribution and one-of-several-correct assurance can be architectural, but do not require a fourth computational family. Describing the composition as one logical machine must not replace independent physical faults with a single fail-stop assumption.

No fourth irreducible family is exposed within the examined scope. This does not establish an exhaustive taxonomy of physical media. None of the deductions authorizes replacing an unverified physical transducer by a digital model without a correspondence premise.

## 5. Which distinctions remain architectural?

| Distinction | Why it matters after reduction |
| --- | --- |
| What untrusted actors can actually do | If arbitrary native instructions can address authoritative memory, language safety of another actor cannot protect it. Confinement-by-construction versus a separately restricted execution domain changes the interference contract. Neither may silently narrow the required environment. |
| Who owns each protected effect and current authority observation | Physical separation, shared memory, mediation at the sink, and surviving queued actions can produce different bypass/order premises. Component names do not decide them. |
| Which failure destroys which state or gate | This determines whether accepted bytes survive and affected routes fail closed. Combining services or synthesizing a circuit may change this relation even if ordinary executions match. |
| Mutable code/configuration and independent approval paths | An available reprogramming route is authority-relevant. Independent veto paths change the fault argument only with exact effect/state binding and a non-bypassable combined gate. |
| Language, ISA, compiler, RTL and proof decomposition | These are representation/assurance choices until they change one of the contracts above. Their unchecked correctness requirements are real and must remain listed; naming them does not establish a necessary family. |

**Language confinement can be the lowest meaningful authority-specific boundary.** Consider a dedicated evaluator whose only untrusted inputs are confined instructions/data, whose imports are entirely mediated, and whose accepted state survives the selected engine loss. Assuming its exact native/digital execution is correct, no second policy-enforcing MMU or reference monitor is necessary: the evaluator's allowed operations enforce authority. A direct language-executing circuit gives the same conclusion without a conventional ISA.

It cannot be the bottom of an unconditional physical assurance argument. Correct execution, retained memory, IO, initialization and absence of bypass still connect that language contract to the device. This is not proof that another **authority layer** is necessary. A generic reliable execution substrate and a separate authorization mechanism are different propositions. If hostile native execution, a privileged writer or an uncontrolled import exists, the proposed evaluator-only construction fails its premise; additional enforcement must be shown.

**Direct digital can genuinely remove optional machinery**, such as a stored-program interpreter, code loader or general instruction decoder, when those mechanisms are absent from the realized circuit. It does not remove the need for correct interpretation of current permissions, complete effect control and continuity. Those obligations are realized in state encoding, gates, memory and reset/IO protocols. A direct proof can also bypass an ISA abstraction on unchanged processor hardware; that removes a proof dependency, not the physical processor. Whether either action reduces residual assumptions depends on the proved links and physical premises, not the lower-looking diagram.

## 6. Common assumptions, additional assumptions and dominance

All candidates require the same **operational obligations**: adequate policy/observation interpretation, current authority discrimination, coherent whole effects, non-bypassable protection and retention through the selected loss. These may be checked and are not all irreducible axioms. Every assurance case still needs a justified initial/current authority origin and a connection between its lowest model and actual physical behavior within the declared environment. Logic/checker premises apply to whichever proof evidence is used; no runtime proof checker is universally required.

Additional correctness demands depend on configuration: interpreter/parser/imports for interpreted work; ISA/privilege/firmware or instruction decoding where used; synthesis/model extraction/configuration for a circuit toolchain; cryptographic and remote-currentness premises only when those mechanisms are used; communication and separate fault premises for distributed enforcement. The optional external-fact and physical-source-binding obligations keep their original scope. No code generator, MMU, processor ISA, clock-based authority or cryptography is common to every candidate.

There is **no unconditional strict dominance between the named families**. Physical correctness of circuit A does not imply correctness of CPU B; correctness of B does not imply A. The following narrower comparisons are justified:

1. **Regrouping is equivalence, not improvement.** Same device, environment and proof leaves means the same trust demand, regardless of how many boxes are drawn.
2. **Specialized correctness can strictly weaken a premise.** On a fixed device, correctness for every program/configuration implies correctness for the exact reachable execution envelope. The converse need not hold: an unused instruction can be faulty while all permitted executions remain correct. This is a strict logical reduction only if the supposedly unused behavior cannot be reached through any admitted guest, interrupt, reset or device interference. Both native and direct-digital arguments can use it; it is not F3's exclusive advantage.
3. **Closing a lower proof gap conditionally improves assurance.** With unchanged physical premises, observations, failures and assurance foundation, proving the execution contract removes the need to accept it separately without evidence. This is discharge of an obligation, not automatically strict logical weakening: if retained premises `B` entail contract `C`, then `B ∧ C` and `B` are logically equivalent. Strict assumption dominance instead needs a demonstrated implication in one direction only, as in item 2. Added unchecked encodings, solvers or changed physical failure assumptions can defeat even the claimed assurance improvement.
4. **Removing a mechanism conditionally reduces required correctness.** If its function is unnecessary for the fixed claim, its removal preserves all required successes/effects/loss behavior, and no replacement assumption is added, its independent correctness obligation disappears. Removing an ISA decoder by replacing a CPU is not by itself evidence that these conditions hold.

Neither full functional correctness of an untrusted proposal generator nor an explicit dynamic check on every instruction is necessary. What is necessary is that all reachable protected effects meet the changing policy. Certificate checking, static invariants and mediation are alternative proof/implementation factorizations of that obligation, with potentially different residual assumptions.

## 7. Failed reductions and semantic boundary

These minimal counterexamples delimit the result; they are reasoned, not executed:

| Proposed shortcut | Counterexample and disposition |
| --- | --- |
| F1 needs no protection regardless of environment | Add a permitted native/DMA writer to accepted memory; it changes bytes after revocation without executing the evaluator. This rejects that reduction, not language confinement under its stated environment. |
| F2 is fully circuit-verified because processors are circuits | A device violates the assumed ISA on a reachable instruction. The upper proof remains true but its premise fails. Merely renaming it F3 supplies no missing evidence. |
| Equivalent transition tables imply equivalent recovery | A new circuit shares the engine reset domain; reset erases its sole accepted-content store. The old realization retained that store. Ordinary step equivalence did not preserve the failure claim. |
| Static certification eliminates current state | Certify a grant, revoke it, replay the unchanged certificate to a checker with no trusted current observation. It cannot distinguish the pre- and post-revocation admissions. |

None forces a Kernel semantic change. Each either fails an existing conformance obligation or requires evidence for a lower premise. No branch of the analysis weakens the supplied target to rescue a candidate.

## 8. Changes to T0–T6 and handoff

| Work | Revised scope before execution |
| --- | --- |
| T0 | Keep the common finite policy and observations. Also fix the untrusted-action envelope, protected acceptance events and loss projection used when comparing configurations. No three separate semantic models. |
| T1 | Audit actual configurations and their state/effect/failure topology. Mark every proof edge and residual assumption; stop using F1/F2/F3 membership as evidence of separation. |
| T2 | Keep the common refinement slice and hostile/positive traces. Add tests that a proposed regrouping or specialization preserves failure and observation mappings. |
| T3 | **Withdraw the mandatory software-versus-RTL pair.** First select one complete assurance case. Commission a second only for a named assumption it avoids or independently checks; it may use the same physical architecture. Different labels do not establish independent assumptions. |
| T4 | Keep actual mediated-use and engine-loss tests; select their target through T1, not a preference for native or language execution. |
| T5 | Apply deployment/physical correspondence to every candidate. Deeper circuit work is justified by a specific unresolved execution/protection premise; direct hardware does not receive an automatic advantage or exemption. |
| T6 | Compare assumption overlap and fault independence, including shared semantics, stores, gates and physical domains. Use diverse implementations only where the promised difference survives that audit. |

The next discriminator is now **which residual execution/effect/retention premise a proposed lowering removes, under an unchanged claim**, rather than which of three families wins. Required success histories and R1–R8/O1–O8 remain unchanged. No T0–T6 work was executed in this continuation.

**WHY:** the original categories mix confinement, execution form and verification depth; their overlap and failed substitutions invalidate an irreducibility claim. **WHAT:** pinned F1–F3 definitions, unchanged Kernel/Work Unit obligations, explicit reduction conditions and counterexamples. **HOW CERTAIN:** evidence-based architectural reclassification with conditional logical arguments; not a mechanized equivalence or universal minimality theorem. **WHAT-NOT-TESTED:** full realization mappings, lower-platform proofs, actual devices, physical replacement equivalence, formal dominance proofs and independent review. The original evidence record supports feasibility of proof techniques; it does not prove these new reductions.
