---
title: Matched reasoning task — Kernel-0 and Work Unit continuity
version: 0.2.0
status: Experimental
authority: Derived
last_updated: 2026-11-25
---

# Kernel-0 and Work Unit continuity

## Question

We are designing a custom minimal authoritative Kernel-0 and a Work Unit architecture. Derive the smallest substrate requirements necessary for durable work, replaceable execution and safe authoritative change. What must the kernel distinguish and enforce, and what can remain outside it?

This is open architectural derivation, not selection, integration or repair of previous experimental implementations.

## Established requirements

- The kernel governs authoritative state and permitted authoritative change. A caller may request a change; its identity, instructions or declared role do not themselves confer authority. Invalid changes must not silently produce partial or different authoritative mutations.
- Execution authority is external to the executor. Authority that has ceased to be valid cannot remain usable merely because an executor or its representation still exists. Incompatible authoritative states must not coexist where exclusivity is required.
- Work Unit → Attachment Point → Execution: durable work, durable executor-facing continuity position, temporary and replaceable execution. Loss of an executor must not destroy authoritative work required for continuation. Replacement must preserve work identity while excluding superseded execution authority.
- Work Unit, Attachment Point and Execution are adequacy constraints on Kernel-0, not necessarily its intrinsic objects, state variables or primitives.
- Single, sequential and concurrent execution; shared, isolated and hybrid resources; and higher-level role profiles are configurations of the same substrate, not distinct kernel modes.
- Semantic judgment, orchestration, observation, resource planning, review, issue tracking and other higher-level functions remain outside the kernel unless a necessary authoritative guarantee demonstrates otherwise. Inactive work and attachment positions must not inherently require resident processes.
- The formal model must represent materially distinct orderings and expose relevant external facts and trusted assumptions. Model adequacy and realization conformance are separate obligations.

No language, OS, processor, database, scheduler, capability representation, persistence representation, IPC, primitive vocabulary or prior prototype is prescribed. Do not retrieve previous proposed designs, implementation branches or other participants' conclusions.

## Discriminating histories

Use these as adequacy tests, not as a proposed state representation or transition API:

1. Work W and its attachment P persist when execution X disappears. A replacement Y continues W/P without recreating work.
2. After X is superseded, X retains access to its old representation and attempts a new mutation. Y is eligible; X must not be able to mutate current authoritative state merely because it previously had authority. Historical X outcomes remain accessible as history.
3. X's new mutation races with supersession. Show the admissible orderings and why an invalid interleaving cannot produce an authoritative mutation. Do not infer authoritative order from wall-clock or transcript ordering.
4. X makes an authorized request before supersession, but an external effect or its outcome is unresolved when Y becomes eligible. Determine what guarantees can and cannot be required, how the histories differ, and which distinctions or assumptions are needed. Do not assume external exactly-once behavior or infer failure from a missing response.
5. Multiple eligible executions and different attachment positions coexist where allowed. Replacement in one position must not accidentally imply global revocation or global exclusivity unless required.

## Deliverable

Return one concise independent reasoning report:
- Derive the minimal necessary semantic distinctions, invariants and authoritative transitions (or explain why the requirements cannot be satisfied under stated assumptions).
- Show how the Work Unit architecture can be expressed over that substrate without prematurely making its concepts kernel primitives. Identify which responsibilities belong outside the kernel.
- Give counterexamples to insufficient models and an explicit trust/external-effect boundary. Distinguish necessary guarantees from policy choices and unproven assumptions.
- Give the smallest abstract falsifying histories or model-adequacy checks that would discriminate your proposal from plausible alternatives. Identify the most consequential remaining uncertainty.

Do not implement, delegate, launch agents, run tests or seek additional sources. Do not select a realization by familiarity or convenience. Treat any proposed ontology or transition relation as a hypothesis; state its necessity and limits. Stop after the bounded reasoning report.

## Requirements provenance

The supplied requirements are derived from the current Kernel-0 Evidence Packet (blob d88b807fb54fd380c8c13b2425ff98f2589d3597) and Execution Engine Vision v2026-11-24.1 (blob 2d410a86213664242e395c2bd1aaf6a4051fe1af). The histories are prospective adequacy questions derived from those requirements, including the W5/W6 replacement distinction; none is asserted to be a completed implementation test. This packet is self-contained.
