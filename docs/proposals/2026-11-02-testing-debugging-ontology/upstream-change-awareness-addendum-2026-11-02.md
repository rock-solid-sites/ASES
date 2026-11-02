---
title: Upstream Change Awareness — Proposed ASES Methodology Addendum
program: ASES
document_type: Methodology Proposal
status: Draft
authority: Experimental
last_updated: 2026-11-02
related_documents:
  - AGENTS.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/debugging-and-fault-isolation-method.md
  - docs/proposals/2026-11-02-testing-debugging-ontology/testing-and-assurance-method.md
---

# Upstream Change Awareness — Proposed Addendum

**Status:** Proposal for the testing, debugging, and assurance methodology. A concise rule was separately committed to AGENTS.md (563ed46); this document does not automatically promote the proposal bundle or authorize automatic upgrades.

## 1. Motivation and incident

The CodeGraph Rust resolution investigation progressed through version comparisons, reproduction, and possible local remediation before identifying relevant upstream work. CodeGraph [PR #3014](https://github.com/colbymchenry/codegraph/pull/3014) had merged on October 29, 2026 (merge commit 4955eac9589a5923c819f6590ac90002cf3e8582). It addressed Rust use-binding scope and module path resolution, including tests on multiple repositories. We should have discovered that work before considering an independent patch.

The existence of that PR does **not** establish that our exact reproduction passes on the merge commit, or that the fix was included in our installed release. These require independent verification. The incident exposes a sequencing problem: the inexpensive hypothesis that upstream has already solved the issue was tested too late.

## 2. Principle

Upstream awareness is a recurring source of evidence within the existing ASES workflow, **not a new development phase**. Before expensive investigation, workaround, local patch, or upstream contribution, establish whether relevant external work already exists. Refresh that evidence at material decision boundaries. Use the cheapest discriminating check, disclose search limits, and avoid unnecessary repeated polling.

## 3. Triggers and scope

Apply when a failure, limitation, API mismatch, performance issue, or proposed feature concerns third-party dependencies, frameworks, CLIs, MCPs, SDKs, cloud APIs, forks, or external repositories. Run a quick upstream pass at investigation entry, after narrowing a root cause, before implementing a fix, and before submitting a contribution. Refresh during prolonged investigations if upstream may have changed. Do not require repository-wide release research for routine changes unrelated to third-party behavior.

## 4. Diagnostic protocol

### A. Establish the actual running version

Identify the component and authoritative upstream repository. Record the *executing* binary or service version, source commit if available, installation path, lockfile/image digest, and relevant wrappers. Distinguish CLI, native kernel, WASM, desktop, daemon, MCP wrapper, cached process, and fork. A manifest version does not prove which binary is running.

### B. Establish distinct upstream states

Capture the installed version, newest published release, upstream default-branch commit, candidate fixing PR/commit, and any downstream patch. A merged fix is not necessarily released; a released fix is not necessarily installed; an installed fix is not necessarily executing.

### C. Search by symptom and cause

Search changelogs, releases, open and merged PRs, issues, and recent commits. Use both the observed error and the suspected mechanism, including affected function names and synonyms. A negative search is bounded evidence, not proof that no fix exists. Preserve the query scope, search time, source URLs and relevant commit hashes.

### D. Run the smallest comparison

Where a plausible fix exists, preserve the minimal reproduction. Compare the failing installed version against the exact candidate upstream artifact, ideally in an isolated checkout. Include a control for unrelated behavior when relevant. Upstream CI evidence supports plausibility but cannot substitute for local verification. Avoid upgrading a production environment merely to investigate.

### E. Decide with explicit classification

Possible dispositions: fixed upstream and released; merged but unreleased; relevant open PR; partial or adjacent fix; no relevant change found; upstream regression; inaccessible or uncertain. Choose upgrade, pin, wait, workaround, incremental patch, or further diagnosis based on observed evidence and risk. Never automatically upgrade or claim a repair solely because a PR was merged.

## 5. Relationship to ASES methods

**Development:** before creating a custom workaround or reimplementing dependency functionality, verify whether upstream already offers the capability. Tie adoption to actual requirements and compatibility.

**Debugging:** include "already fixed upstream" among competing falsifiable hypotheses. Check early and again before intervention, but continue to verify the original user-facing outcome.

**Testing and assurance:** keep baseline and candidate results separate, retain cross-version controls, and record what has not been tested. Upstream tests are evidence about upstream's environment, not proof of ours.

**Epistemology and ontology:** distinguish the claims "reported", "proposed", "merged", "released", "installed", "executing", "verified", and "user outcome restored". Confusing these is a category error. Do not impose an ontology reviewer on every dependency check.

**Orchestration:** one bounded upstream reconnaissance task can precede expensive builder work. Share its timestamped evidence across agents instead of repeating the same searches.

## 6. Evidence record

A lightweight incident record should include:

- Component, repository and actual running artifact/version.
- UTC check time, latest release/tag and upstream commit.
- Search terms and sources, candidate issue/PR/commit links.
- Baseline reproduction result, candidate result and regression controls.
- Interpretation, certainty, limitations and explicitly untested surfaces.
- Decision, responsible actor, and event triggering the next refresh.

This can live alongside existing ASES incident records; a new database or service is not required.

## 7. Freshness and cost

Prefer event-driven refreshes at decision boundaries over arbitrary continuous polling. A long-running investigation may additionally require a time-based freshness threshold, determined empirically from the change rate of the dependency. Cache reusable upstream evidence and its timestamp. Measure search overhead, useful hits, false leads, avoided duplicate work, and instances where upstream searching delays a cheaper local test. Avoid adding infrastructure until a simple process demonstrates value.

## 8. Failure modes

- Checking releases only misses merged but unreleased fixes.
- Searching an error string only misses root-cause changes.
- Treating a similar PR as an exact fix produces false confidence.
- Assuming an updated manifest means an updated daemon is running confuses surfaces.
- Automatically tracking upstream HEAD can introduce new regressions.
- Treating an empty search result as proof of absence overstates certainty.
- Repeated broad polling consumes resources without changing decisions.
- Submitting a patch without refreshing upstream risks duplicate contributions.
- Treating draft proposals as binding changes confuses document authority.

## 9. Proposed pilot

**Case 1 — CodeGraph:** reproduce the Rust issue on the affected release and compare against the PR #3014 merge commit, including a control; separately verify whether a published release contains it.

**Case 2 — genuine unfixed defect:** ensure a bounded negative upstream search permits continued local diagnosis and a justified patch.

**Case 3 — misleading similar fix:** ensure an adjacent upstream PR does not trigger a false "resolved" conclusion without the exact red/green comparison.

Acceptance criteria: relevant upstream work is found before expensive duplication; genuine unfixed problems are not blocked; claims remain appropriately qualified; and overhead is proportionate to the avoided cost.

## 10. Reconciliation and adoption

The short upstream-awareness rule already added to AGENTS.md is the immediate operational baseline. This proposal supplies the detailed rationale and testable design. Reconcile it with the draft debugging and assurance methods, run the pilots, and promote only demonstrated improvements into canonical documentation. Avoid copying the entire protocol into multiple role instructions; reference one shared rule instead.
