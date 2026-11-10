---
title: Commit-point F1/L5/L6 effect admission experiment
program: EDASES
layer: Research
document_type: Investigation
status: Experimental
authority: Derived
last_updated: 2026-11-10
---

# Bounded result

The original native denial/publication discrepancy is reproduced from Codex
Cloud. L5 denies the attenuated descendant write while original F4 returns 201
and the witness publishes it. The authorized neighboring native write succeeds.
The complete original 16 integration + 2 recovery histories are preserved in
`../phase-i-cloud-baseline/`; the source pins match PRs #10 and #11.

The isolated append hook admits useful effects and rejects tested invalid
compositions **before any new journal bytes**. The final fresh capture contains
19 histories, checked from native process frames, journal bytes, selected L5
records, SQLite observations and witness exchanges. Three deliberately altered
raw-evidence controls are rejected. No independent review or CI was performed.

## What changed and why

`admission_sink.py` wraps the original receipt-aware F4 sink rather than replacing
its HTTP, flat authority, journal append/fsync, witness CAS or replay. Its
`emit_locked(effect_accepted)` hook acquires F1 BEGIN IMMEDIATE, the #11 L5
management-writer lock, and L6 BEGIN IMMEDIATE in that order. It rereads the
accepted subject and exact opaque evidence, retained pair, current selected L5
generation/full-path authority/actual bytes, and live non-disposed L6 dependency.
These guards remain held through the original local append and fsync.

The test supervisor supplies a fixed import/root configuration; request paths or
hashes cannot substitute for that configuration. Expected L5 generation is only
a comparison input. Actual current path permission is recomputed. A journaled
admission certificate describes the tested inputs; it is not a reusable bearer
capability. An audit or exact-obligation route is refused by this port, rather
than relabeling a denied descendant effect.

This is the smallest tested local slice, not an adopted native ASES integration.
The missing interfaces and assumptions are explicit in `PACKET.md`.

## Discriminating observations

| History | Observed result |
| --- | --- |
| Current accepted pair, writable active D, live x | 201, one local effect, exact journal published |
| Native sealed move retaining read ceiling, activation | Native D write denied; append port returns 409, no new journal bytes |
| Old selector, followed by native move/activation | Old generation refused; this is a sealed-to-active selector test, not native revocation of formerly enabled L5 authority |
| Valid L6 x removed after request preflight, before guard | Native disposal/removal commits; paused request then refuses with no append |
| F1 explicitly reaccepts same bytes with different opaque world at preflight gate | F1 selected pair changes; stale F4 request refuses with no append |
| Changed F1 content requested without an acceptance bundle | Native #11 wrapper denies, prior pair survives; subsequent valid F4 neighbor returns 201 |
| Wrong subject/world/epoch/import, changed root, unknown L6 material | Refused with unchanged journal |
| Admission paused with all guards held | F1 and L6 writers receive lock failures; guarded L5 contender refuses; original request resumes successfully |
| Actual kill before append | No effect; cold F4 startup succeeds |
| Actual kill after append/fsync, before publication | One local effect, no reply, old witness; cold F4 refuses divergent cut |
| EOF/error after append | HTTP 503/recovery-required, one retained local effect; never a no-effect 409 |
| Real witness publication with its reply suppressed | HTTP 503 while remote cut matches local effect; cold recovery succeeds |

The stale F1 observation and interleaved L6 removal cases demonstrate actual
invalidation before append. L5's pinned native API has no active-route revoke/seal
operation; this experiment does not invent one and call it native.

## Reproduction and evidence

Run `bash docs/research/phase-i-effect-admission/reproduce.sh <new-output-dir>`.
The script executes native processes and a separate raw checker. Final capture:
`evidence/cloud-05`; `raw.json.gz` preserves its compact complete process/byte
record; evaluation and file digests are indexed in `evidence/MANIFEST.json`.
Earlier harness failures remain under `evidence/instrumentation-failures`.
Source pins are in each raw capture and the unchanged original source index.

## Claim boundary

WHY: admission and the local irreversible effect now share a guarded current
view within the participating-writer profile. WHAT: real component processes,
current state readback, positive/negative neighbors, three interruption/failure
boundaries, remote reply loss and altered-evidence controls. HOW CERTAIN:
evidence-based for these finite native histories. WHAT-NOT-TESTED:

- The import is **test-only**, not a native F1→F3 acceptance certificate. Native
  components do not establish the alias or a protected shared owning domain.
- Opaque observation truth, configuration authenticity, current same-root stores
  and host/runtime/storage correctness remain trusted premises.
- L5 writers must participate in the stable guard. The separate custody probe
  demonstrates an unguarded writer bypass; this is not enforced single-writer
  custody or complete native confinement.
- L6 liveness is its local inventory domain, not proof of global Work Unit
  disposition. The lifecycle experiment separately includes L5 material/children.
- A local accepted effect may publish later after source state changes. This
  experiment requires authority at local journal acceptance, not cancellation
  at remote visibility. Neither exactly-once delivery nor durable witness
  nonrollback, physical power loss, arbitrary schedules or production adoption
  is claimed. Retry identity is tested separately in the opt-in F4 candidate.

These limits block promotion to a native global integration proof; they do not
invalidate the demonstrated before/after local admission discriminator.
