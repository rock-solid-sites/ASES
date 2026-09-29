---
title: Kernel-0 Machine Realization Evidence Record
program: EDASES
layer: Research
document_type: Research Evidence Record
status: Experimental
authority: Derived
canonical_repository: ASES
crosslink_issue: 573
baseline_commit: c34d08413b2cca4f4a6add986c5b5c04e739b24f
depends_on:
  - Kernel-0 Machine-Adjacent Realization Input Packet
consumed_by:
  - Kernel-0 Machine Realization Investigation
related_documents:
  - Kernel-0 Abstract Semantics
  - Kernel-0 Verification Obligations
implements: []
implemented_by: []
supersedes: []
superseded_by: []
last_updated: 2026-09-29
---

# Kernel-0 machine realization evidence record

This record supports the [investigation](./Kernel-0-Machine-Realization-Investigation.md). Repository input provenance and justified context expansions are recorded there. External sources instantiate or challenge derived requirements; they do not define Kernel semantics. All external retrieval below occurred on **2026-09-29** using the Exa Search skill.

## Search coverage and stopping rule

Reviewed **80 search-result entries across 14 queries**, grouped into five workstreams below. Exact-URL deduplication leaves **77 URLs**; that is a discovery count, not 77 validated studies. Publication mirrors and alternative versions were grouped under the selected original source. Seventeen selected source URLs support the twelve evidence entries below. Primary author papers, author project descriptions and official documentation support substantive claims; search ranking and secondary summaries do not.

The search was requirement-led: find alternative ways to interpret a finite policy, exclude bypasses, retain state across the selected loss, connect behavior to machine code/circuits, and reduce correlated assurance assumptions. It was not an exhaustive bibliography or product comparison. Once further candidates fit an existing family or changed only an optional stronger failure profile, the remaining uncertainty was turned into specific discriminators.

| Workstream | Exact queries, in order within the stream | Requested result count |
| --- | --- | --- |
| S1 — Native and language paths | `Research papers end to end verified systems software hardware refinement instruction set circuits complete mediation minimal trusted computing base`; `Original papers verified interpreter CakeML bootstrapped compiler WebAssembly sandbox proof memory safety external calls`; `site:sel4.systems verification proof assumptions binary compiler hardware boot DMA official`; `VeriWasm USENIX 2022 sandbox verifier untrusted compiler Lucet machine code theorem` | 10 + 5 + 5 + 5 |
| S2 — Checking, isolation and enforcement | `Research papers proof carrying code untrusted operating system verified reference monitor capability revocation complete mediation hardware`; `Original paper proof carrying code Necula small checker untrusted code safety policy translation validation`; `Simplex runtime assurance architecture verified safety controller decision module cannot enforce liveness external effects`; `Keystone open source secure enclave framework threat model trusted hardware untrusted operating system persistent rollback` | 10 + 5 + 5 + 5 |
| S3 — Recovery correspondence | `Original research crash refinement durable linearizability verified storage FSCQ volatile memory process crash recovery` | 5 |
| S4 — Digital to physical boundary | `Original papers verified hardware synthesis circuits refinement physical assumptions asynchronous metastability arbiters`; `Kami verified hardware compiler semantics preserving hardware synthesis CompCert proof RTL netlist`; `site:cl.cam.ac.uk metastability synchronizers arbiter cannot guarantee bounded time physical circuit` | 5 + 5 + 5 |
| S5 — Assurance diversity | `Original paper N version programming independence failures Knight Leveson diverse double compiling Wheeler`; `site:dwheeler.com trusting trust diverse double compiling source corresponds executable assumptions` | 5 + 5 |

Full-page/PDF extraction was used after discovery, with bounded extraction lengths and targeted inspection of theorem scope, assumptions and limitations. This is **not** a claim to have read every page of every paper. Exact inspected scope follows. No cited proof development was executed, no repository implementation was structurally audited, and no vendor configuration was deployed. No performance number from these works is used to rank the families.

## E1. Verified compilation

**Source:** [Fox, Myreen and Tan, Verified Compilation of CakeML to Multiple Machine-Code Targets (CPP 2017)](https://cakeml.org/cpp17.pdf). Inspected abstract, top-level correctness theorem (Figure 3), installed-code/FFI conditions, environmental interference and target-model discussion.

**Observation:** the theorem connects compiled bytes to source behaviors under machine configuration, installed-code and FFI premises; resource-limit behavior is explicit. **Use:** F1/F2 can replace general compiler-correctness assumptions with a suitable checked compilation result. **Limit:** this does not prove host calls, retention or the Work Unit policy. Boot/configuration and the physical processor remain separate links. **Certainty:** evidence-based report of the published theorem, not a locally reproduced proof.

## E2. Confinement is a different theorem from functional correctness

**Source:** [Bosamiya, Lim and Parno, Provably-Safe Multilingual Software Sandboxing using WebAssembly (USENIX Security 2022)](https://www.usenix.org/system/files/sec22-bosamiya.pdf). Inspected abstract/introduction, safety scope, environment assumptions and comparison with validation.

**Observation:** the work separates sandbox safety from full program correctness. Its assumptions include an uncorrupted environment and suitably restricted exposed APIs; denial of service, speculation and side channels are outside its stated scope. It also reports a validator specification error involving signedness. **Use:** supports F1 and the need to inspect the checker specification and host interface. **Limit:** a safe Wasm computation is not proof of current authority or correct content acceptance. **Certainty:** evidence-based; neither compiler nor validator was run here.

## E3. Protected native execution

**Sources:** seL4 Foundation, [What the Proofs Assume](https://www.sel4.systems/Verification/assumptions.html) and [Verified Configurations](https://docs.sel4.systems/projects/sel4/verified-configurations.html). Inspected both retrieved pages, including the unverified-features and per-architecture scope tables.

**Observation:** proof coverage varies by configuration. Binary verification can remove compiler/linker trust where supported. The documented boundaries include boot, hardware behavior/management, assembly and DMA conditions; current verified configurations do not cover every device-translation or debug feature. **Use:** F2 can reuse substantial isolation evidence, but only with exact configuration and system composition. **Limit:** a verified microkernel does not establish this application policy, device route revocation or retained recovery. No particular board/configuration is selected by this investigation. **Certainty:** evidence-based official scope as retrieved; no seL4 build or proof run.

## E4. Direct machine-code reasoning

**Source:** [Sammler et al., Islaris: Verification of Machine Code Against Authoritative ISA Semantics (PLDI 2022)](https://people.mpi-sws.org/~dreyer/papers/islaris/paper.pdf). Inspected introduction, non-goals/limitations, TCB discussion and the approach overview.

**Observation:** detailed Sail ISA models can underlie machine-code verification. The paper discloses single-threaded execution and address-translation limitations, and additional trust in symbolic execution/SMT, with a stronger checking path explored for RISC-V. **Use:** challenges the assumption that a high-level compiler must always be trusted. **Limit:** it cannot be cited as an already-proved concurrent MMU/DMA Work Unit system. **Certainty:** evidence-based theorem/tool boundary; no artifact reproduction.

## E5. Whole software-stack correspondence

**Source:** [Hawblitzel et al., Ironclad Apps: End-to-End Security via Automated Full-System Verification (OSDI 2014)](https://www.andrew.cmu.edu/user/bparno/papers/ironclad.pdf). Inspected abstract, §2 goals/non-goals/threat model and methodology overview.

**Observation:** remote state-machine equivalence can encompass applications, lower software and assembly-level behavior. The system assumes correct CPU/memory/chipset and secure hardware, and excludes liveness and unmodeled timing channels. **Use:** shows that F2 need not stop its argument at an application source language or trust an entire conventional OS. **Limit:** the assurance machinery and physical assumptions remain; no inheritance of its cryptographic, remote or storage guarantees into Kernel-0. **Certainty:** evidence-based published approach; no reconstructed system.

## E6. Crash refinement

**Source:** [Chen et al., Using Crash Hoare Logic for Certifying the FSCQ File System (SOSP 2015)](https://pdos.csail.mit.edu/papers/fscq:sosp15.pdf). Inspected introduction/contributions and the crash/disk specifications in §3.

**Observation:** recovery postconditions and explicit asynchronous-write/synchronization models can support compositional crash proofs. The reported executable also includes trusted Haskell/FUSE support beyond the proved filesystem model. **Use:** grounds O5 and warns against treating a persistence theorem as independent of its disk/runtime assumptions. **Limit:** baseline Kernel process-loss retention need not use a disk or claim power-loss recovery; this source does not prove the Work Unit cut. **Certainty:** evidence-based; no filesystem/crash tests run.

## E7. Direct circuit refinement

**Source:** [Athalye, Kaashoek and Zeldovich, Verifying Hardware Security Modules with Information-Preserving Refinement (OSDI 2022, Knox)](https://pdos.csail.mit.edu/papers/knox:osdi22.pdf). Inspected §§2–3 threat model/IPR, implementation/tool discussion in §6 and introductory limitations.

**Observation:** a functional interface can be related to arbitrary cycle-level digital IO, including firmware and circuit behavior. The driver interpretation is part of the specification; model extraction and solver machinery still matter. **Use:** materially introduces F3 and challenges the necessity of an ISA boundary in the proof. **Limit:** physical attacks and analog side channels are excluded; the published approach does not prove fabrication, this Work Unit policy or unrestricted scale. **Certainty:** evidence-based method and case studies; no Knox proof or FPGA experiment reproduced.

## E8. Layered circuit assurance without pretending the bridges disappear

**Source:** [Parfait, Modular Verification of Secure and Leakage-Free Systems: From Application Specification to Circuit-Level Implementation (SOSP 2024)](https://dspace.mit.edu/server/api/core/bitstreams/41ea440f-26e2-4ef2-a490-1b46ded70d0c/content). Inspected architecture/threat model, compilation discussion in §4, Knox2 in §5 and TCB in §6.

**Observation:** transitive information-preserving refinement supports modular software-to-circuit arguments. The paper expressly identifies semantic compatibility assumptions, model conversions, checker/tool dependencies and partially verified compilation machinery. **Use:** more layers can reduce proof difficulty without adding unchecked semantic gaps, provided composition is established; some actual gaps remain here. **Limit:** no claim that adopting this framework leaves only a proof-assistant kernel and physical silicon in trust. **Certainty:** evidence-based inspection of published assumptions; no proof reproduction.

## E9. Synthesis and the analog stopping boundary

**Sources:** [Choi et al., Kami (ICFP 2017)](https://adam.chlipala.net/papers/KamiICFP17/KamiICFP17.pdf), introduction and labeled-transition-system/modular reasoning definitions; [Formal verification of high-level synthesis (Vericert, 2021)](https://dl.acm.org/doi/10.1145/3485494), author-supplied abstract only; [Moore et al., Using Stoppable Clocks to Safely Interface Asynchronous and Synchronous Subsystems (2000)](https://www.cl.cam.ac.uk/~swm11/research/papers/aint2000.pdf), synchronization and bundled-data assumptions.

**Observation:** Kami supplies modular hardware reasoning; Vericert reports a proved C-to-Verilog translation. Neither observation establishes physical implementation correspondence. The clock-interface paper exposes handshake/timing and metastability concerns below a simple digital event model. **Use:** circuit and asynchronous paths replace assumptions rather than erase them. **Limit:** no synthesis/netlist equivalence, analog verification or fabrication inspection was performed; Vericert's full proof was not inspected. **Certainty:** evidence-based existence and scope, not integrated assurance.

## E10. Certification and runtime enforcement

**Sources:** [Necula's Proof-Carrying Code project description](https://people.eecs.berkeley.edu/~necula/pcc.html), overview, advantages and implementation (the page labels itself historical/out of date); [Bak et al., Real-Time Reachability for Verified Simplex Design (RTSS 2014)](https://www.taylortjohnson.com/research/bak2014rtss.pdf), abstract and introductory architecture.

**Observation:** PCC moves proof construction outside a receiver's trusted checking path. Simplex allows an uncertified controller under a verified safety/switching boundary. **Use:** motivates X and pre-effect validation/veto. **Deduction, not a source theorem:** neither a generic safety certificate nor an invariant-only veto establishes this target's exact `E`, current dependencies, retention and whole-effect ordering. **Limit:** no PCC checker, runtime monitor or plant model was implemented here. **Certainty:** evidence-based prior art plus explicit architectural deduction.

## E11. Enclave isolation is not Work Unit retention

**Source:** [Keystone, How Keystone Works: Basics](https://docs.keystone-enclave.org/en/latest/Getting-Started/How-Keystone-Works/Keystone-Basics.html), overview, provisioning, attestation and lifecycle.

**Observation:** enclave isolation depends on trusted hardware and a security monitor; the host can request enclave destruction, which clears/reclaims its private memory. **Use:** a concrete example of moving a host outside an isolation boundary while retaining specific hardware/monitor premises. **Deduction:** using that memory as the sole accepted-content holder cannot promise continuity across its destruction. Add independent retention and the relevant effect/authority contracts, or reject that configuration. **Limit:** no assertion that every TEE has the same destruction contract; no Keystone prototype or proof audit. **Certainty:** evidence-based official behavior and conditional counterexample.

## E12. Independent assurance

**Sources:** [Brilliant, Knight and Leveson, Analysis of Faults in an N-Version Software Experiment](http://sunnyday.mit.edu/papers/nver2-submitted.pdf), abstract/introduction and fault interpretation; [Wheeler, formal input for the diverse double-compiling source-correspondence proof](https://dwheeler.com/trusting-trust/dissertation/ddc.in), assumptions and goal.

**Observation:** separately developed versions can fail together more often than independence predicts. DDC states precise conditional correspondence between source and executable, including the trusted translation/environment premises. **Use:** supports an assumption-overlap audit and exact artifact checking, rather than confidence from voting or different labels. **Limit:** no failure probabilities for the proposed families, no DDC run and no independent implementation in this investigation. **Certainty:** evidence-based limits and methods; proposed diversity benefit remains unmeasured.

## Candidate disposition after discovery

| Candidate or idea | Reason for retention, factoring or non-selection |
| --- | --- |
| Verified language/interpreter and software fault isolation | Retained as F1; admission effects and host calls still need separate conformance. |
| Native verified stacks, microkernels, security monitors, separate processors | Retained under F2 with explicit placement subcases. A product name cannot substitute for proof/configuration coverage. |
| Direct RTL, verified embedded CPU/firmware, specialized finite circuits | Retained as F3 when the argument reaches digital IO, with lower tool/device gaps explicit. |
| Proof-carrying code/transition certificates; runtime assurance | Factored as X across physical families. Safety checks can reduce generator trust; they do not themselves own the physical effect. |
| Enclaves/attestation | A protection/initial-image technique within F2, not a solution to every currentness, IO or retention requirement. |
| Capability machines and capability-revocation papers | Discovery corroborates the importance of non-confusability and actual revocation. No concrete ISA is selected: the present cheapest discriminator is the exact route/use contract, not a larger architecture survey. |
| Replication/consensus, authenticated ledgers, succinct computation proofs | No baseline requirement for their stronger failure/remote-verification profiles. Potential variants, not a necessity argument or replacement for local effect ownership. |
| Recent experimental repositories or secondary/library summaries returned by search | Not admitted as evidence of conformance. Relevant primary papers were retrieved instead; unvalidated claims did not establish or eliminate a family. |
| Self-timed circuits | Retained as a timing variant of F3, not a fourth authority architecture. Physical handshakes/arbitration remain assumptions. |

**WHY:** source claims must not silently become a Kernel mechanism recommendation. **WHAT:** recorded queries, selected primary sources, their inspected scope and the investigation's explicit deductions. **HOW CERTAIN:** evidence-based architectural research. **WHAT-NOT-TESTED:** source proof reproduction, implementation conformance, physical behavior, scalability, performance, or independent review. The investigation's T0–T6 work items state what evidence would change the reduction.
