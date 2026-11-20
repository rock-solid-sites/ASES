---
title: Minimal Evidence Event Contract — P6 Research Draft
program: EDASES
document_type: Experimental Conceptual Record
status: Research draft; not adopted or universal
authority: Experimental
last_updated: 2026-11-02
---

# Minimal typed evidence events: preliminary research contract

The [P6 experiment](P6-RESULTS-2026-11-02.md) tested a **small typed event envelope** using the independently preserved original failed and successful P5 CI artifacts. Its purpose is to stop different *kinds of statements* being accidentally represented by a single boolean or status. This contract is not canonical ASES vocabulary, a resource-ledger schema, or a universal JSON Schema.

## Separation by meaning

| Type | What it says | What it cannot establish alone |
| --- | --- | --- |
| `EXECUTION` | A CI job ran and the runner's aggregate suite outcome | The product violated a requirement, or the oracle was valid |
| `ASSERTION` | Checks compared actual with expected values, including their failures | Whether any failed check was *supposed* to fail on a planted mutant |
| `INSTRUMENT` | An attributable interpretation of whether the test oracle/fixture was qualified | The implementation is correct or a reviewer independent |
| `CLAIM` | A bounded interpretation tied to claim ID, scope and preceding evidence | Human acceptance or universal correctness |
| `ARCHIVE` | ZIP/manifest provenance, exact original byte count, digest and accessible copy | Semantic truth of contained statements |
| `REVIEW` | Whether an actual independent review occurred, with route/context provenance if so | An independent reviewer can be presumed from a packet or second CI runner |
| `CORRECTION` | A new interpretation or corrected source revision linked to an earlier run | Permission to alter or replace the original failed result |
| `DECISION` | An authorized outcome, **or explicit NOT_RECORDED** | Authorization that does not exist or the builder's recommendation |

These are **discriminated events**, linked by run ID, event ID, attribution and evidence references. Their ordering supports a later interpretation without rewriting an earlier observation. A P6 container record has no single overloaded `status` representing all eight concepts.

In P5, **a successful overall CI job still contained failed individual checks** because the test deliberately ran known bad candidates. A green suite can have RED negative controls. Conversely, the initial failed P5 run did not prove a software defect because its ordinary correct-implementation test had a mistaken expected value. Run status, individual check status and interpretation are three different propositions.

## Reference verification and anti-overclaim checks

The prototype implementation is [evidence_semantics_p6.py](evidence_semantics_p6.py). It uses only the Python standard library, reopens P5's two original archival ZIPs, checks SHA-256 and ZIP CRC, reads `results/p5.json`, and creates typed P5 observation records. Later research assessments are labeled `RESEARCH_INTERPRETATION`; no independent model or human acceptance is claimed.

It enforces the selected local controls: nonblank source/run identifiers, event kinds, unique IDs, linked run identity, nonempty evidence references, checks with coherent failed-count versus assertion result, claim references to already-seen evidence, specific archive-proof fields for VERIFIED_COMPLETE, no completed independent review without provenance fields, and no ACCEPT/REVISE/DEFER/REJECT/ESCALATE field without an attributed authorized actor.

**Limits are important.** The validator checks structures and selected internal relationships. It does *not* independently verify that a supplied reviewer route is real, that a string naming an authorized actor truly grants authority, that a reference points to the correct claim, that evidence isn't fabricated, or that a test oracle is semantically correct. It is not a universal proof engine. A later conformance reviewer or authority service must perform those separate checks when the risk warrants them.

## Record retention and future solver interface

Do not require a single database, provider, language or event broker. Initially, compact typed JSON can associate project-owned raw artifacts with their actual run, claim, test and interpretation IDs. Corrected interpretations should append a new record linking the earlier one, rather than altering past observations. A provider-native CI success flag is just an execution observation.

For the proposed Resource Solver, similar *distinctions* should remain structural: proposed resource usage, authorization, reservation, actual runtime/usage, provider report, settlement and reconciliation must never collapse into one `spent` or `success` value. **This document does not implement solver accounting or dictate the solver's data model.** The solver will temporarily own lifecycle timestamps and observations itself; capture streams can later be transferred to an Observer without redefining authority. An Orchestrator's assertion that a task finished is evidence from an agent, not confirmation of provider accounting.

Unresolved before any schema adoption: authoritative claim identifiers, clock and ordering semantics, how event references are verified, legitimate corrections/deletion rules, privacy/access classes, reporter/model identity, human authorization proof, provider reconciliation semantics, and durable artifact-storage ownership. These questions must be evaluated against the proposed testing/debugging/ontology roles rather than solved by inventing a large registry.

**Research decision:** retain the event-type separation as a candidate and continue measuring marginal benefit. No canonical policy, Orchestrator role, Resource Solver interface or production configuration changed.
