---
title: Repository Review Checklist
program: EDASES
layer: Research
document_type: Checklist
status: Active
authority: Canonical
canonical_repository: edases

depends_on:
  - EDASES Review Methodology

consumed_by: []

related_documents:
  - Documentation Standard
  - ORIENTATION.md
  - ARCHITECTURE.md

supersedes: []
last_updated: 2026-08-10
---

# Repository Review Checklist

> **Local applicability clarification (2026-11-24):** This EDASES-owned repository-review checklist is retained for its conceptual, traceability and evidence questions. Upstream currency is unverified. Its original fixed orientation-file sequence and mandatory completion language reflect an earlier repository convention, not a current ASES startup or review gate. For ASES work, select relevant sources and review modes via the [current task-scoped method](../methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) and [AI Orchestration Guide](../methodology/AI%20Orchestration%20Guide.md#review-modes-and-provenance). Use the questions selectively, without biasing an independent broad review through a list of expected defects. The original body and EDASES ownership remain intact. See [testing and assurance source map](Testing%20and%20Assurance%20Source%20Map.md).

Complete this checklist before submitting a repository review.

## Orientation

* [ ] Read `README.md`.
* [ ] Read `ORIENTATION.md`.
* [ ] Read `ARCHITECTURE.md`.
* [ ] Read `AGENTS.md` (AI reviewers only).
* [ ] Read the Documentation Standard.
* [ ] Review the Canonical Terminology document.

---

## Canonical Documentation

* [ ] Identify all canonical documents relevant to the review.
* [ ] Confirm terminology is used consistently.
* [ ] Check that derived documents do not redefine canonical concepts.

---

## Abstraction

* [ ] Verify abstraction boundaries are maintained.
* [ ] Ensure implementation concerns do not appear in research or methodology documents.
* [ ] Confirm dependency direction remains correct.

---

## Consistency

* [ ] Identify duplicated concepts.
* [ ] Identify contradictory statements.
* [ ] Identify obsolete documentation.
* [ ] Identify missing cross-references.

---

## Traceability

* [ ] Verify claims are supported by evidence.
* [ ] Verify reasoning remains traceable.
* [ ] Verify findings reference supporting observations where appropriate.

---

## Architecture

* [ ] Confirm repository organisation matches the documented architecture.
* [ ] Confirm new documents occupy the correct abstraction layer.

---

## Methodology

* [ ] Verify repository content aligns with ASES.
* [ ] Identify places where methodology has diverged from canonical specifications.

---

## Recommendations

* [ ] Separate observations from findings.
* [ ] Separate findings from recommendations.
* [ ] Identify unresolved questions.
* [ ] Identify suggested follow-up work.

---

## Final Review

* [ ] Ensure conclusions are supported by evidence.
* [ ] Clearly distinguish fact from opinion.
* [ ] Record confidence where appropriate.
* [ ] Submit findings for human evaluation.
