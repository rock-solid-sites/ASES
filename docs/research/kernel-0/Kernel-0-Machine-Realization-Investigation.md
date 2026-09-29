---
title: Kernel-0 Machine Realization Investigation
program: EDASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 573
baseline_commit: c34d08413b2cca4f4a6add986c5b5c04e739b24f
depends_on:
  - Kernel-0 Machine-Adjacent Realization Input Packet
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
consumed_by:
  - Kernel machine realization formalization and experiments
related_documents:
  - EDASES Phase I Core Substrate Closure
  - EDASES Work Unit Component Design
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Kernel-0 machine realization investigation

Three realization families survive: **a confined abstract machine**, **a native protected authority machine**, and **a digital authority appliance**. A certificate-checking boundary can reduce trusted computation in any of them. No unique winner follows: the families exchange assumptions about language confinement, privileged machine behavior, and circuit/device behavior. The smallest useful comparison is a common finite Work Unit policy and one genuinely mediated effect, including loss and recovery, rather than complete competing engines.

The irreducible path is an interpretation of the policy and observations, retained distinguishable state, coherent whole commitment, and non-bypassable control of the claimed effects. A general OS, database, compiler, instruction set, scheduler, cryptography, clock-based authority, and distributed agreement are not individually necessary. Their removal does not remove the correctness obligations they were carrying.

This is an architectural research result, not a realization-conformance proof or production selection. It preserves the supplied Kernel semantics. The assurance argument reaches formal machine-code or digital circuit models in the cited prior art; it does not reach unconditional correctness of a fabricated physical machine.

## Input provenance and context boundary

The reasoning branch starts at `c34d08413b2cca4f4a6add986c5b5c04e739b24f`, the fetched tip of `codex/kernel-machine-realization-input` on 2026-09-29. The packet's semantic baseline is `8d158e3e82d5811e420c80cc6c9664d3ae4a6088`. Git blob identities were checked against the packet before reasoning.

| Input at the branch start | Git blob | Scope read |
| --- | --- | --- |
| [Input packet](./Kernel-0-Machine-Realization-Input-Packet.md) | `8e76ff7821d638cd5c3c5cba57461543416c329f` | Full |
| [Abstract semantics](./Kernel-0-Abstract-Semantics.md) | `fd2a485dba3805884fc394b093a61daa60719072` | Full |
| [Verification obligations](./Kernel-0-Verification-Obligations.md) | `7c1d9b198b34c360dd6e8d7d4795704811cfdfa3` | Full |
| [Phase-I closure](../../architecture/core-substrate/Phase-I-Closure.md) | `a82482b1718a652a39a5a2bb179797f92908380d` | Selected §§1, 2, 7, 8, 9 |

Additional repository context is limited to these recorded expansions:

| Added source | Exact scope and reason it could change the result |
| --- | --- |
| Phase-I closure, same blob | §4: §7 refers to this section for protected attachment contracts. Needed to distinguish use-time authority from a previously committed exact obligation; this determines whether an output gate must cancel delayed actions. Historical experiments mentioned there are not adopted as fresh evidence. |
| [Work Unit component design](../../architecture/EDASES%20Work%20Unit%20Component%20Design.md), blob `22c98dbabdaed7f41d656209a6ce96269dde8390` | §D only: §7 requires W.D boundary observations without enumerating them. Identity/genesis, creator, project, containment, granted resources, attached capabilities/agent and boundary state must remain interpretable without executing the interior. This constrains the abstraction and recovery relation. |
| [AGENTS](../../../AGENTS.md), blob `4e284d23966bdcb16e6394b715665dc3d4cecff1`; [ORIENTATION](../../../ORIENTATION.md), blob `9423fa71597f5a525bfd29378978b6daacbcfc22`; [Documentation Standard](../../standards/Documentation%20Standard.md), blob `15c47446695686b19d5e4e67325dd45e0592aa7f` | Operational instructions and document metadata only; not extra semantic premises. Closure front matter/introduction and repository filenames were incidentally visible during navigation; historical realization arguments were not imported. |

The packet reports provisional authority/recovery refinements through `ad24f856a` on `codex/stage1-authority-recovery`. That branch was not retrieved. Current reassessment on recovery, continued accounting of surviving allocations, and sealing not proving safe destruction are carried as provisional conditions; the final analysis will identify where each matters.

## 1. Comparison rule and fixed assurance profile

A candidate is compared under the **same** policy, observations, finite capacities, failure events and protected effect contracts. An assumption is a proposition that must be true, not a software package name. Separate:

- **Required operational correctness:** behavior on which the result depends, even when proved.
- **Undischarged premises:** correctness, environment or physical facts still assumed.
- **Assurance machinery:** specification adequacy, logic, proof/checker implementation, encodings and evidence-to-deployment correspondence.

A verified mediator remains essential to operational correctness. Its proof replaces an unsupported assertion about its behavior with a conditional theorem; it does not make a failed mediator harmless. An untrusted compiler is possible when its particular output is checked against the required theorem. A compiler advertised as verified is insufficient if the deployed binary, foreign calls, configuration or initialization lie outside that theorem.

Candidate A dominates B only if, for the same claim, A's residual premises require no stronger correctness and its checked relations cover at least the same observations. Incomparable assumptions stay incomparable. A small unverified circuit is not automatically better than a larger verified software boundary, and fewer proof layers can increase the difficulty of auditing the remaining correspondence. No numerical TCB score is justified here.

The selected profile includes executor/attachment loss, engine/authority-process loss while protection and retained storage survive, loss during commitment and lost replies, cold sealed recovery and explicit replacement. It includes actual finite successful create/grant/accept/replace/recover/continue histories and the additional §7 witnesses. It excludes unconditional machine/power-loss recovery, silent rollback/corruption detection, hostile physical hardware, partitioned availability, arbitrary exactly-once sinks and D3 computation-stop deadlines. D1/D2 sealing still governs new affected capability admission/use and outward protected effects. Baseline exclusion of covert channels does not excuse a direct unmediated read or write.

**Provisional-delta dependency:** current reassessment is used by recovery obligation O5; continued allocation accounting by R6/O5; sealing not authorizing destruction by R6/O4. Each is already conservatively supported by selected C3/C5/C7/C8 and §7. Nothing here depends on additional conclusions from the unreviewed branch, and no final review outcome is presumed. A review changing one of those three conditions reopens its identified obligation, not the entire family search.

## 2. Derived requirements and the smallest retained functions

| ID | Derived requirement and necessity witness | Target provenance |
| --- | --- | --- |
| R1 | Bind the exact proposal, policy, affected current domain and input interpretation. `I` alone is insufficient: writing the wrong authorized value may preserve all invariants but violate `E`. Missing dependencies cannot be repaired by a sound proof about the supplied subset. | Kernel parameters/resolution; verification adequacy; closure C1/C2/C9 |
| R2 | Preserve enough non-confusable state to distinguish work, authority and required observations. Reusing an old ingress identity while old requests survive can restore invalid authority. A finite machine may refuse exhaustion before aliasing. | Kernel authority/continuity; C4/C6/C11; added W.D |
| R3 | Establish one coherent validation/effect order across every interacting commitment. Serial execution is sufficient, not necessary. A physical critical section is insufficient if DMA, a second core, live referents or sink acceptance can change premises outside it. | Kernel authority/order; invariants 1–4; C2/C13 |
| R4 | Make every accepted change, actionable crossing and selected protected sink event non-bypassable, including retained handles, administrative policy, alternate buses and recovery routes. A stored seal cannot prevent an outstanding direct write. | Protected-meaning closure; C3/C5/C10/C13 |
| R5 | Retain required bytes, boundary information and whole outcomes independently of the selected lost actor. A digest without the only copy of its referent fails continuity. Publish success only after the failure-profile recovery point. | Continuity; C5/C7/C11/C12 |
| R6 | Interpret the finite Work Unit policy: containment remains well-founded; restrictions apply through the full path; grants do not arise from containment; allocations remain bounded; sealed moves do not widen latent rights; removal preserves dependents. | Closure §7, C3–C5/C8; provisional allocation/disposal conditions |
| R7 | Establish valid bootstrap/current management and, where claimed, non-transferable physical-source binding. A transport principal shared by the old and replacement producers cannot distinguish their requests. | Kernel authority; trusted assumptions; closure §4 |
| R8 | Fail closed under the selected loss and permit useful bounded success when healthy. A hang or deny-all implementation is not an adequate realization. Recovery cannot manufacture a current state from an ambiguous image. | Closure §1.1 and §7 non-vacuity; C7/C9 |

These collapse to four functions, not four compulsory components: **interpret/admit**, **retain/commit**, **mediate/protect**, and **establish current ingress/activation**. Guard premises obtained from outside need an additional fact contract for source, truth, completeness and timing. That contract cannot be replaced with a signature proving only who asserted the fact.

For the baseline, retained RAM in a surviving protection domain is a possible store: process loss does not imply power loss. It must retain the bytes and commitment metadata, protect them against stale actors, and outlive the engine being restarted. Ordinary engine-private RAM fails. Nonvolatile storage becomes necessary only if the selected failure destroys all retained volatile representations; choosing it adds controller, flush and persistence-domain obligations. A full filesystem or database is not forced by continuity.

No universal machine primitive named atomic commit is required. A representation may use an immutable prepared state and one recoverable selector, a log, a verified update protocol, or an equivalent construction. In every case the interruption outcomes and visible effects must refine permitted whole endpoints. The correctness of the selector/protocol is a surviving obligation; calling it a register does not prove it.

## 3. The common refinement target

Let `K_W` be the supplied Kernel transition relation instantiated with the frozen finite Work Unit policy. It is not a new Kernel. Let `M` be a candidate transition system including trusted memory, protection configuration, retained contents, ingress, relevant device queues, and selected sinks. `Env` describes admissible outside actions and the exact failure domain. Required observations include W.D, continuity position, protected effects and commit/deny/pending knowledge.

The desired statement is conditional contextual trace refinement:

```text
Env assumptions ∧ Init_M(m0) ∧ deployment correspondence
    ⇒ every protected/consumer observation of M || Env
       is explained by an allowed history of K_W.
```

Use a relation `R(m, σ, h)` with history/auxiliary state when necessary, rather than insisting on a total pointwise mapping from every intermediate machine state. Internal copying and preparation may stutter; visible partial authoritative effects may not. Different encodings of the same state must preserve every required future permission and continuity observation. A simulation relation can establish trace inclusion, but the exact forward/backward or prophecy technique is a downstream proof choice; a naive forward simulation is not presumed sufficient for every concurrent candidate.

| Obligation | Required relation/evidence |
| --- | --- |
| O1 — Adequacy and initialization | `R(m0,σ0,h0)` and `I(σ0)`; policy and observation interpretation includes every R1–R8 distinction; bootstrap is distinct from recovery. The meaning of all denied, unsupported and exhausted requests is declared. |
| O2 — Whole effects and order | Every concrete protected event maps to a permitted whole commitment with `G ∧ E ∧ I` on a coherent current view. Denial maps to no protected effect attributable to that proposal. Preserve completed-before-initiated precedence and exclude three-way cycles and omitted negative/range dependencies. |
| O3 — Environment closure | Untrusted executor/driver steps either stutter at the protected interface or invoke a mediated admissible transition. Prove this against arbitrary malformed requests and prohibited bypass attempts, not merely well-behaved API clients. |
| O4 — Structural policy and observations | Map boundary metadata, actual exposure, retained content and latent future rights. Sealed relocation must preserve/narrow rights on later activation, not just compare two empty currently enabled sets. Removal orders with concurrent dependent creation. |
| O5 — Crash/recovery refinement | At every selected interruption point, recovery yields an observationally compatible current cut including accepted/irrevocable effects and required bytes. Recover sealed, account for survivors, reassess current rights, and exclude old routes before activation. Unknown material cannot justify positive admission. |
| O6 — Sink correspondence | Identify the precise concrete decision/use/acceptance event. Map resource, destination, quantity, bytes and operation exactly. Bind input validation to the bytes actually retained or acted upon; model queues and previously committed obligations. |
| O7 — Non-vacuity and bounded completion | Exhibit all required successful histories, and termination of supported invoked handlers under the stated healthy finite conditions. Refine observable outcomes, not just safety predicates. No scheduler fairness or deadline is added. |
| O8 — Artifact and machine correspondence | Bind proof/model to exact binary/netlist, configuration, policy, initialization, device interfaces and active deployed image; state the lowest assumed interface and every unchecked translation below it. |

A strict serial holder gives a simple witness for O2, stronger than the required partial order. Independently verified per-object locks or individually linearizable storage calls do not establish the combined Work Unit operation. Persistent linearizability is relevant when persistence is selected, but neither that term nor ordinary linearizability alone captures W.D observations, policy completeness, external effects and confinement. Crash Hoare logic is concrete prior art for explicit recovery postconditions, not a reason to inherit its disk model or runtime assumptions ([E6](./Kernel-0-Machine-Realization-Evidence.md#e6-crash-refinement)).

For a local mediated output, one possible concrete witness stages bounded data privately, checks the current view, commits its accepted state/obligation in retained storage, and then publishes that exact result. For a sink requiring authority at sink acceptance, a local precheck is insufficient: sink admission must share the required order or use a contract that establishes it. This distinction remains identical in all families.

## 4. Surviving realization families

These are families of conditional constructions. None is a claim that a named technology already implements Work Units. Their common minimal experiment uses finite explicit tables/bytes, serial admission, bounded encodings, cold recovery and one declared mediated attachment. This removes accidental concurrency and convenience layers before comparing the essential paths.

### F1 — A confined abstract machine

Execute untrusted work only as instructions/data of a confined language or abstract machine. The interpreter/validated executor owns access to protected state; effectful host operations go through narrow current-policy entry points. An executor cannot manufacture a native address or call an ambient OS interface. The Work Unit transition evaluator can be part of this machine or a protected service it calls.

The lowest-assumption variant avoids a JIT, general native extensions and broad foreign interfaces. A bounded interpreter may run bare-metal or on a retained trusted substrate. Language confinement can remove the need for an MMU to isolate guests, but it does **not** remove a privileged host capable of overwriting the interpreter. The host must be absent, constrained, verified or explicitly trusted.

Refinement is `K_W ← abstract machine semantics ← interpreter/validated code ← ISA model ← implementation`. The proof must show representation separation, all guest effects passing the declared entry points, and current authority at the relevant event. Static safety can justify eliding repeated checks only if its theorem includes the relevant changing policy and interference; memory safety alone is not authority correctness.

The interpreter's state and content store need a lifetime independent of a lost executor and engine. If the entire interpreter process is called the engine and holds the only state, this family fails R5; it needs a surviving protected holder or a separate recoverable store. On loss, suspended bytecode cannot reach a live host function through a leftover route. A surviving resource meter must continue accounting for surviving allocations.

**Residual assumptions:** exact bytecode/parser semantics; interpreter or safety-validator correctness; host-call meaning and bounds; any unchecked interpreter compilation/runtime; ISA and physical processor behavior; retained memory and isolation configuration; correct deployment/boot. Full application compiler correctness is unnecessary if candidate results are revalidated and sandbox escape is excluded. If exact executor computation is itself promised, that extra correctness must be proved too.

**Evidence and limit:** CakeML demonstrates compilation to modeled machine code with explicit installed-code, FFI and environment premises; it does not prove Work Unit effects. Verified Wasm sandboxing demonstrates separation of confinement assurance from complete compiler correctness and also documents specification mistakes in validators. These instantiate the language boundary, not cold recovery or currentness ([E1–E2](./Kernel-0-Machine-Realization-Evidence.md#e1-verified-compilation)).

**Smallest rejection test:** provide a guest with every permitted host call, kill/restart the engine and replay a retained call/handle. Any authoritative mutation or selected outward use outside current mediation rejects that configuration. A small import surface that closes this test keeps F1 alive; native compatibility is not a supplied requirement.

### F2 — A native protected authority machine

Run a bounded trusted state machine as native instructions. Isolate arbitrary native executors using a verified/configured protection mechanism, or place the authority machine on a separate processor with exclusive ownership of retained state and selected effects. Mediate requests through non-confusable ingress. The placement alternatives are material: a co-resident monitor relies on privilege/memory/bus isolation, while physical separation replaces much of that dependence with peripheral ownership and channel/source binding.

A microkernel, small monitor or bare-metal program are alternatives, not required stack layers. Handwritten machine code with a checked refinement can remove compiler trust; verified compilation or validation of the actual linked binary can discharge it differently. A general instruction set remains in this family, but only the used behavior plus interference/protection contract need enter a specialized proof. O3 still covers malicious executor instructions and device access, not just the trusted program's instruction subset.

The path is `K_W ← policy/state code ← exact executable + memory/IO model ← ISA/protection implementation`. For co-residence, compose application correctness with an actual isolation/configuration theorem. For a separate processor, the host's OS can be outside protected-state integrity only if it cannot access the appliance's retained state, authorize as a different origin, reflash its code, or bypass its sink. Dropping the host from integrity trust does not establish content availability if it holds the only copy.

Engine loss must leave the enforcing substrate and retained state intact. A separately restartable policy process may fail while a small surviving monitor closes admission and retains state. A bare-metal realization must define an equivalent fault boundary, such as a restartable engine domain whose reset does not reset the retaining/enforcing domain. It cannot relabel whole-device reset as harmless process loss.

**Residual assumptions:** native program refinement or direct correctness; isolation/privilege configuration and reset behavior; ISA memory ordering and atomicity; firmware/debug/DMA authority; retained-store and IO contracts; source binding; artifact installation. On commodity processors, ISA correctness and unmodeled firmware/microarchitecture remain substantial assumptions even with a verified kernel.

**Evidence and limit:** seL4's published assumptions and configuration-specific proofs show how much kernel behavior can be checked and exactly what remains, including boot and device issues. Islaris shows machine-code reasoning over detailed ISA semantics while exposing its particular concurrency/address-translation limits. Ironclad supplies whole-system state-machine correspondence with declared hardware and verification-tool assumptions. Keystone illustrates putting an OS outside enclave memory isolation; its host-driven enclave destruction is a warning that enclave memory alone is not the required retained Work Unit store ([E3–E5, E11](./Kernel-0-Machine-Realization-Evidence.md#e3-protected-native-execution)).

**Smallest rejection test:** inventory the exact native and device access routes, then test engine death and replacement while an executor retains its old handle. A route which continues new protected acceptance after the selected boundary rejects that configuration before any full engine is built.

### F3 — A digital authority appliance

Encode the finite guarded transition machine directly as a circuit with private retained state, input decoding, current-authority checks and gated outputs. A microcoded or embedded-CPU design is a hybrid: it belongs here for assurance only when the proof encompasses that processor and firmware to the digital interface. Otherwise it retains F2's ISA assumption.

A direct finite circuit can eliminate the general OS, language runtime, general compiler and even a general ISA from the execution argument. This is a genuine different path, not merely a small CPU program. The finite target and refusal-before-exhaustion make a finite-state construction possible in principle. Its circuit size, memory scale and proof tractability are unmeasured; expressibility is not evidence of affordability.

The path is `K_W ← cycle/handshake transition system ← RTL/netlist ← configured/fabricated circuit`. One must prove input/output decoding, commit state, interruption/reset semantics, memory timing, output gating and all relevant externally visible intermediate cycles. An API-level proof against friendly software misses hostile wire sequences. A synchronous implementation may use a clock; no semantic global clock is thereby required. A self-timed implementation trades clock assumptions for handshake/delay/arbitration assumptions.

The appliance can remain alive through engine loss, but its input queue is not automatically authorized to drain after that loss. Declare which requests already committed exact obligations and which require a live/current engine relationship at use. Recovery returns the controlled objects sealed and the store/current ingress relation coherent. Circuit state hosted on a device that resets whenever the engine dies fails the selected retention profile without an additional surviving representation.

**Residual assumptions:** correctness of policy encoding and refinement; any trusted RTL/model extraction or solver; synthesis, technology mapping, placement/routing, bitstream and installation correspondence not checked; clock/reset/handshake and memory contracts; actual component behavior, power and electrical environment; exclusive routing to the selected sink. An FPGA does not make these premises smaller by definition. Off-device bulk content reintroduces retention and mediation obligations at that holder.

**Evidence and limit:** Knox relates a functional specification to hostile cycle-level IO, including the firmware/circuit together. Parfait composes information-preserving refinements across layers, but explicitly retains semantic bridges and tool assumptions. Kami and Vericert show circuit-refinement/synthesis approaches; neither their existence nor a generated Verilog file proves physical fabrication or this policy. The baseline needs effect/observation refinement; stronger information-preserving relations matter only for the leakage observations actually selected ([E7–E9](./Kernel-0-Machine-Realization-Evidence.md#e7-direct-circuit-refinement)).

**Smallest rejection test:** a bounded RTL machine with retained accepted bytes and one gated output; interrupt/reset the restartable engine interface on each step between validation, commitment and output. Inspect gate-level or post-synthesis equivalence obligations before treating the shorter conceptual path as a shorter trusted path.

### X — Certificate checking as a cross-family reduction

An untrusted producer may propose `(current-input binding, q, σ′, certificate)`. A protected checker verifies the exact policy instance, completeness of relevant dependencies, `G`, `E`, `I`, and correspondence of bytes/effect. The current input binding is revalidated atomically with commitment. For tiny finite policies direct evaluation may be simpler than a proof language; a checker is not inherently a reduction.

This can remove the proposal generator, optimizing compiler, solver or expensive derivation search from **soundness** trust. Failure to generate certificates affects availability; O7 still requires successful supported histories. A proof about old state is not current permission, and a hash is not proof of data retention. Negated facts and complete containment/resource domains require evidence as well as supplied positive facts. PCC establishes the general producer/checker separation; applying it to this exact transition target remains an obligation ([E10](./Kernel-0-Machine-Realization-Evidence.md#e10-certification-and-runtime-enforcement)).

A proof-carrying execution/cryptographic proof service, authenticated log or ledger is therefore not a fourth complete physical enforcement family. It needs one of F1–F3 (or an equivalent physical mechanism) at acceptance and the protected sink. Succinct proofs may reduce verifier work but add encoding and cryptographic assumptions. No target requirement yet pays for that exchange.

## 5. Layer elimination ledger

| Layer/function considered | Reduction and surviving obligation |
| --- | --- |
| Executor, planner, Processor, UI, scheduler, tracker | Outside authority soundness when they only propose and cannot bypass R4. Successful invocation/inputs remain conditions for O7; no self-scheduling engine is needed. |
| Expensive policy search/derivation | Untrusted with checked certificates or recomputation. Truth and complete current input binding stay in the trusted argument. |
| General application compiler/JIT | Untrusted for confined candidate work if output safety is independently established. Eliminate JIT in the simplest witness. Exact trusted-code behavior still needs output verification or a compilation theorem. |
| General OS/hypervisor/runtime | Eliminate on a bare-metal/circuit path, or replace with verified/constrained functions. A surviving privileged host is not removed merely because the application never calls it. |
| MMU/capability hardware | Can be replaced by language confinement or physical separation; those substitutes must exclude all native/bus bypasses and still retain state. Capability unforgeability by itself does not establish revocation of copied authority. |
| General database/filesystem | Replace with bounded retained representation and proved interruption protocol. Content/metadata coupling, current recovery and access protection remain. |
| Durable complete event history | Not forced when a sufficient current representation retains all required C11 evidence and pending irrevocable obligations. Rebuilding derived views is allowed; dropping required provenance is not. |
| Crypto, hashes, attestation, random tokens | Not intrinsically needed for a physically bound local ingress with exact bytes and trusted initialization. Add them for explicit adversarial channels/remote identity/integrity claims; do not infer truth, currentness, retention or non-transferability from authenticity. |
| Clock, lease, heartbeat | Not needed for untimed safety on a non-bypassable stopped gate. An expiry/death deadline or remote lease adds trustworthy time and ordering assumptions. Physical circuit timing remains even without semantic time. |
| Distributed replication/consensus | Not needed for the selected single-logical-holder profile. It may support stronger loss/availability claims, but adds replica, protocol, quorum and fault assumptions without eliminating the last sink/physical boundary. |
| Compiler/synthesis/proof search tools | Outside logical soundness only where exact outputs are checked by a sound independently justified checker. Trusted translations, unchecked solver answers and theorem-to-deployment mismatches remain in the assurance base. |
| Monitor/log after the effect | May detect errors; cannot enforce no forbidden irreversible effect. Put any safety veto before the protected event and include the veto route in R4. |

The discovery of direct circuit verification changes the candidate space materially: there is no necessity argument for an OS or even an ISA between this finite semantic target and a digital machine. Conversely, the extra physical/model correspondence obligations prevent declaring direct hardware minimal merely by counting layers.

## 6. Lowest boundary: what cannot presently be discharged

For all three families, the final theorem is of the form `physical assumptions ⇒ observed refinement`. The predicate connecting measured voltages, stored charge, bus events or actuator movement to modeled bits/events is not established by a software or RTL proof.

| Boundary premise | What can be checked/reduced | What remains here |
| --- | --- | --- |
| The specified policy means the intended permissions | Formalize selected observations, challenge negative facts, supply counterexamples and success witnesses | Human adequacy judgment; no theorem that a formalization captures an unformalized intention |
| Correct installed artifact and initial authority | Check exact binary/netlist, readback/measurement, boot/configuration and proof bindings; independent build/checking | Trust in the measurement path, provisioning root and absence of an unmodeled alternate boot/debug path |
| ISA behavior | Verify selected CPU RTL against ISA or bypass the ISA with direct circuit reasoning | Actual device implements that modeled design; unused firmware/devices cannot interfere |
| RTL to circuit | Checked synthesis/equivalence, timing analysis, layout/configuration evidence | Tool gaps, fabrication/configuration integrity, cell/device model adequacy |
| Stable memory and indivisible protocol steps | Explicit width/alignment/order assumptions; crash cuts; ECC/redundancy/fault injection for a named fault model | No baseline claim against arbitrary bit flips, silent rollback or all correlated failures; controller/physical retention contract |
| Digital timing and reset | Verify clock-domain/reset protocol and fail-closed outputs; characterize synchronizers or self-timed handshakes | Electrical bounds, metastability resolution behavior, clock/power/temperature assumptions and analog faults not in the digital model |
| Physical effect correspondence | Exclusive gate ownership; validate exact device protocol and instrument actual sink acceptance | A device acknowledgment is not universally proof of physical actuation; sensors, actuators, wiring and environment need their own contract |
| Outside facts | Validate origin, integrity, freshness and ordering; independently measure where possible | Whether the physical proposition is true and the dependency domain complete |

Knox/Parfait's digital interface scope explicitly excludes physical attacks and arbitrary analog leakage; it is a closer machine boundary, not a proof below it. Asynchronous-circuit research likewise exposes timing/handshake premises rather than eliminating physical uncertainty ([E7–E9](./Kernel-0-Machine-Realization-Evidence.md#e7-direct-circuit-refinement)). Engineering margins and fault rates can support a selected physical assurance profile. They are neither unconditional proof nor part of the presently selected baseline.

A mechanism cannot recover required information if every surviving representation has been destroyed. A physical gate cannot guarantee correct effects while its own arbitrary failure is unrestricted. Redundancy helps only under a stated fault bound and sufficiently separate failure domains. These are conditional limits, not reasons to weaken the baseline to lose data silently.

## 7. Counterexamples and classification of limitations

The following are small reasoned histories, **not executed experiments or mechanically proved results**. Each states the premise that makes it discriminating.

| Finding | Smallest history/argument | Classification and consequence |
| --- | --- | --- |
| A1 — Verified transitions without exclusive effect ownership fail | Old executor keeps writable alias `p`; replacement commits; old executor writes `p`; accepted bytes change without a guarded event. Every local record can still satisfy `I`. | Concrete architectural counterexample to record-only designs in every family. Add/exhibit exclusive mediation or immutable referents; no Kernel change. |
| A2 — A safety checker may accept the wrong whole effect | `q` requests retained value `x`; producer supplies `y` satisfying `I`; checker tests only `I`; accepts `y`. | Refutes invariant-only runtime assurance as full refinement. Check `E`, exact inputs and authorization, as well as `I`. Simplex-style safety supervision is useful prior art but not an automatic solution to C1/O2. |
| A3 — Engine-death detection cannot be invented at a remote gate | Gate has identical observations in histories where the engine is dead or merely delayed; it admits a fresh action in the latter. The same decision is possible in the former. | Impossible to guarantee an instantaneous distinction under these observations while requiring that admission. Integrated no-bypass use or an explicit trusted death/fencing event closes the premise. No baseline remote timeout takeover or D3 deadline is required. |
| A4 — Queues can turn an apparent dead gate into a live route | Permission checked; request queued; engine dies or is replaced; a surviving consumer performs a new use under the old permission. | Violates use-time authority. It may be valid if the exact bounded effect had already committed under an explicitly decision-authorized contract. Declare the event; do not silently rename it after failure. |
| A5 — Authentic recovery is not necessarily current | Accept `x`, then `y`; recover genuine old image containing only `x`. No surviving observation distinguishes that image from the latest one. | Successful current recovery is impossible under that information loss. Baseline assumes a current retained cut and may refuse uncertain material; hashes/signatures do not restore `y`. |
| A6 — Finite reusable evidence plus unbounded replay | Finite representation repeats while an old request can still present it; admission has no other distinguishing state. Requiring perpetual successful replacement would eventually accept a stale identity or reject the indistinguishable new one. | Conditional finite-state indistinguishability limit. Refusal before exhaustion or trustworthy elimination of old routes fits the supplied semantics. No unbounded success promise is present. |
| A7 — Revocation cannot erase knowledge or cancel an already committed irreversible event | Authorized bytes delivered/action accepted; revoke; recipient still knows bytes or consequence appears later. | Impossible retroactive cancellation under that premise. Baseline distinguishes new use from already committed consequence and does not promise secure erasure. |
| A8 — Source-only retry cannot decide an invisible sink outcome | Sink accepted with lost reply versus sink never received; source observations identical. Retrying duplicates one; never retrying may fail eventual delivery in the other. | Stronger at-most-once plus eventual-delivery claim impossible without more sink/communication assumptions. Baseline allows uncertain knowledge; closure §4 already supplies this argument. |

No counterexample establishes that **every** credible realization of a required baseline property needs a semantic change. The immediate architectural finding is narrower and material: **the authority/effect boundary must reach the actual enforcing event, and the retention/protection fault domain must outlive the selected engine loss**. A software proof, enclave, cryptographic receipt or hardware box that fails either condition is not a smaller realization of this target.

Proof engineering for the full policy, practical memory size, per-use gate overhead, checked synthesis and formal composition are potentially expensive. They are not impossibility results. Hostile silicon, arbitrary rollback, physical-source identification over an indistinguishable shared channel and instantaneous remote failure knowledge instead require additional explicit premises or weaker selected claims; they cannot be obtained by more implementation effort alone under unchanged assumptions.

## 8. Independent paths and useful assurance diversity

F1 and F2 may share a CPU, compiler, proof assistant, host and policy parser. They are not independent just because one is called an interpreter. The strongest currently visible diversity is an independently formalized native/software realization and a direct circuit transition machine, with separately developed encoding/checking paths. Both can refine `K_W`; they need not have identical intermediate states or admit the same order of overlapping independent requests.

Useful comparison requires common input histories and observation contracts. Compare allowed trace sets or impose the same serialized witness order; raw output inequality can reflect permitted nondeterminism rather than a fault. Shared target semantics, external facts, initial authority, physical power/sinks and any common reference encoder remain common-mode premises.

Three uses have different assurance meanings:

1. **Offline cross-check:** independently encode policy and replay positive/hostile histories against each refinement relation. Disagreement finds errors or specification ambiguity; agreement is evidence, not proof or a quantified failure probability.
2. **Independent checking of artifacts/proofs:** validate an exact binary/netlist or proof with differently built tools. Diverse double-compiling addresses conditional source/executable correspondence, not source correctness; a second proof checker can reduce reliance on one implementation but not on a shared false statement.
3. **Online conjunctive authorization:** a common non-bypassable effect gate requires two independent approvals of the same exact effect against compatible current state. Under a stated fault model, one sound veto path can prevent forbidden effects. The binding, combined commitment/recovery protocol and gate are now trusted; either veto can destroy availability. Duplicate actuators executing independently are unsafe. Majority voting has a different fault assumption and no automatic benefit here.

N-version research found correlated failures despite separate development; names or organizations are not statistical independence. Record an assumption-overlap graph, including compilers, parsers, solvers, hardware, provisioning and sinks, before claiming diversity. The next work should test a deliberately different pair, not pay for three near-identical software engines ([E12](./Kernel-0-Machine-Realization-Evidence.md#e12-independent-assurance)).

## 9. Bounded cheaper work and stop conditions

These tasks are ordered by the cheapest test capable of rejecting the premise. They are assignments to prepare later, not agents launched or results already obtained.

| Work item | Bounded deliverable and smallest discriminator | Pass/stop rule |
| --- | --- | --- |
| T0 — Common semantic fixture | Formalize a finite supported policy/observation contract with two containment contexts, a sealed movable child and descendant, accepted bytes, bounded allocations, old/replacement ingress and three interacting requests. Select one mediated-use sink event. Include W.D and each §7 success witness; enumerate exact capacity bounds. | Stop on any ambiguity requiring a policy choice. Do not invent a permission rule or silently drop C1–C13. Other external contracts stay parameters, not hidden defaults. |
| T1 — Route/fault-domain audit | For each family sketch only retained state, writer identities, reset/loss boundaries and every route to accepted bytes/output. Work through A1/A3/A4 and accepted-before-loss/use-after-recovery. | Reject a configuration with an unclosed route or lost sole copy before building it. For a native option inspect actual privilege/DMA/firmware; for an interpreter inspect imports/native escape; for a circuit inspect buses/reset/queues. |
| T2 — Refinement slice | Model accept, replace, seal/recover and one attachment at instruction-independent granularity. Include write skew, three-way cycles, stale proof/input substitution, lost ack, ABA/exhaustion and loss at every preparation/commit/publication step. | A checked model must supply positive traces and mutation failures. Report exact bounds; no general correctness claim from finite enumeration. Expand to move/dispose/remove only after the first slice survives. |
| T3 — Two genuinely different lowerings | First produce one F1-or-F2 executable slice and one F3 RTL slice of the same T2 contract. State both `R` relations and their tool assumptions; check exact binary/circuit behavior where supported. | Stop if the added checker/translation or IO assumptions exceed those removed, or if supported success cannot be realized. Passing retains both paths; it does not select a product. |
| T4 — Real mediated boundary | On one selected native or language platform, kill the engine between each relevant stage; attempt retained-handle/queued/ancestor-revocation bypass; inspect actual sink acceptance and retained bytes. Recovery must continue accepted work and refuse stale authority. | Reject any record/effect mismatch. Report process-loss evidence only; do not generalize to power loss. This is the lowest-cost empirical discriminator before a complete Work Unit prototype. |
| T5 — Digital/deployment closure | For the surviving circuit slice, identify exact model extraction, RTL/netlist equivalence, reset, memory/IO timing, configuration and loaded-image evidence. Exercise malformed wire inputs and interruption cuts. | A missing lower link stays an assumption. Do not declare physical verification from RTL simulation. Proceed to device work only if the assumption ledger offers a real benefit over the software path. |
| T6 — Diversity challenge | Independently encode one hostile-history set and one checker path; introduce policy, encoding, stale-view and lower-level faults singly. Compare trace conformance, not votes. | Count only detected injected faults under stated conditions. If faults bypass both via shared input or sink, repair/record that common premise; do not claim independent reliability. |

T0–T2 are the smallest common next step. The first practical fork is T1: **can a confined language express the required finite workloads and attachment contract without broad trusted host calls, and can the selected native gate actually retain/protect state through engine loss?** If yes, keep the cheaper F1/F2 slice for empirical work. F3 remains the strongest distinct assurance path; its decisive additional question is whether exact policy plus content/IO refinement can reach a checked digital artifact with fewer residual premises, not fewer boxes. No provided workload or physical deployment evidence currently answers that question.

Reopen frontier reasoning only for a concrete failed obligation, an omitted required observation, a demonstrated lower-bound counterexample, or an explicitly selected stronger failure/effect profile. Ordinary proof completion, tool-version qualification, device tests and bounded fixture work do not require repeating the family survey.

## 10. Claim handoff and validation boundary

| Claim for downstream use | WHY | WHAT | HOW CERTAIN | WHAT-NOT-TESTED |
| --- | --- | --- | --- | --- |
| No OS, general runtime, database, ISA or semantic clock is individually required | Their functions have alternative conditional realizations | R1–R8 reduction; F1–F3; primary examples in the evidence record | Evidence-based necessity reduction, not proven global minimality | A full Work Unit circuit or executable and its costs |
| Three families survive without changing the supplied target | Each has an identifiable correspondence path and can represent a bounded state/effect gate; no family-wide baseline contradiction found | O1–O8 and candidate constructions | Evidence-based architectural alternatives | Complete conformance, adequacy and every success history |
| Actual effect ownership and independent retention are mandatory | A1/A3/A4 expose record-only and lost-domain failures | Pinned closure/Kernel obligations and explicit histories | Evidence-based; conditional logical counterexamples, not mechanized proofs | Concrete OS/device/interpreter enforcement |
| Proofs can reduce assumed tool/component correctness but do not remove the physical boundary | Output checking and refinement stop at declared models/axioms | Primary-source theorem scopes and §6 | Evidence-based | Reproduction of cited proofs, fabricated device correctness, fault rates |
| Diverse software/circuit paths are useful to investigate | Their lower assumptions can differ while the target remains common | §8 and independence literature | Evidence-based proposal; benefit unquantified | Independent implementation/review, common-mode fault experiment, probability estimates |

Validation in this run: pinned Git blob comparison; primary-source retrieval and scoped theorem/assumption inspection; structured trace/refinement reasoning; document/link/provenance and Git-diff checks. No Kernel/Work Unit model was executed, no proof artifact was built or checked, no runtime implementation was changed, and no physical experiment or independent agent review was performed. The [evidence record](./Kernel-0-Machine-Realization-Evidence.md) separates discovered candidates, inspected primary evidence and deductions.
