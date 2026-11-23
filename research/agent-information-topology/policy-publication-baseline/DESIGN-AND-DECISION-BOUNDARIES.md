---
title: Agent Information Topology - Document Authority and Policy Publication Boundaries
program: ASES
layer: Research
document_type: Design Document
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - docs/standards/Documentation Standard.md
  - docs/research/EDASES-Methodology-Feedback-and-Enforcement.md
related_documents:
  - docs/research/Tools Distribution Architecture Synthesis.md
  - docs/research/Tools Distribution Architecture Decision Test Framework.md
last_updated: 2026-11-20
---

# Document authority, publication and effective agent context

**Purpose:** Record the smallest defensible interpretation of the ASES document and instruction distribution pilot. This is a *design/reconciliation document*, not a production policy or approval to rewrite any consumer repository. Its executable companion is the offline synthetic publisher in this directory, tracked by [draft PR #64](https://github.com/rock-solid-sites/ASES/pull/64).

## 1. Three distinct boundaries

| Boundary | Owner or mechanism | Question | Present evidence |
| --- | --- | --- | --- |
| **Authority** | Canonical ASES/EDASES documents and explicitly owned project decisions | Which rule is binding, under whose authority, at which revision? | Documentation Standard defines status, authority and dependencies; prototype source JSON is *synthetic*, not the canonical ASES policy |
| **Publication** | Deterministic generator and one consumer manifest per project | How can a reviewed shared rule be instantiated or replaced without silent drift? | Offline publisher tests demonstrate import, exact pin, extension, replacement and `--check`/ `--update`; no real consumer repository was modified |
| **Effective context** | Specific agent launcher/harness and its actually loaded paths | Which generated and unrelated instructions, skills, plugins and global rules reach an agent? | **Not proven by the publisher**. Requires an independent runtime exposure investigation; filesystem existence is not a model-visible trace |

A successful publication check is not evidence of model compliance. A correct agent answer is not evidence that no superseded content was available to the harness. A successful provider launch is not evidence that the correct instructions were loaded.

## 2. Source and consumer ownership

- **Methodology source:** ASES owns its current, approved shared agent methodology; EDASES research remains research until promoted through its proper decision process. A *draft*, *derived* or *experimental* document is never silently upgraded to canonical policy by inclusion in an index or generator.
- **Project source:** The consuming project retains explicit ownership of local requirements, permitted overrides, sensitive/private instructions, and the final local agent-facing file. A shared publisher must not overwrite unrecognized local content.
- **Published file:** One clearly designated *generated* output represents the reviewed effective project rule set; it should not be independently edited. Local corrections belong in a project-owned manifest/extension, followed by generation and a reviewable diff.
- **Read-only skill index:** The installed ASES Workflow Skills MCP dispatcher and `skills/current/README.md` link to selected current operational skills. This **is not equivalent to** importing every skill body into an OpenCode/Codex agent, and it is not a publisher or authority that can supersede project-local rules.
- **Evidence and execution metadata:** Work Notes records bounded agent tasks and destinations; GitHub owns reviewed technical source and test evidence; Projektor owns human planning. The experimental Knowledge Index is a rebuildable *read-only derived projection*, not a policy source, issue tracker, archive or live permission boundary.

The August 2026 Tools Distribution Architecture work remains useful research into **single logical ownership, drift detection and generated consumer artifacts**. It also assumes an earlier Tools monorepo, Crosslink plugin installation and now-retired VPS/user-level paths. Do **not** treat those migration instructions, artifact location decisions or infrastructure references as currently executed ASES deployment policy. The ownership of each *current* artifact class must be verified rather than transferred by analogy.

## 3. Four policy relationships and resolution rules

| Relationship | Source of effective text | Required rule |
| --- | --- | --- |
| **Verbatim** | Exact approved upstream text | Preserve content, including meaningful whitespace; no downstream paraphrase |
| **Parameterized** | Approved upstream template plus project-owned exact parameters | Reject unknown/missing substitutions, preserve source identity |
| **Extension** | Project-owned extra rule under a distinct ID | Must not silently shadow a shared rule ID |
| **Override** | Project-owned complete replacement for one upstream rule ID | Remove the *original* upstream rule from the generated output entirely; record ownership and rationale **before** production adoption |

The prototype supports these relationships for two **synthetic** consumers; its manifest records rule IDs and a SHA-256 of the exact upstream JSON bytes. It does **not** yet record a source repository/authority URI, per-rule authorizations, exception rationale, expiration, review approver, or a validated signature. The source hash detects *change against a chosen input*; it does not prove that the selected input was canonical or that the approval to override was granted.

A later real implementation should attach a project-owned reason, authorizing decision reference and review status to every exception. Do **not** add these fields merely to make this research prototype appear production ready: first test whether a minimal manifest plus Git review satisfies actual operator needs.

## 4. Drift, conflict and propagation decisions

- **Fail closed on stale source and altered generated output.** `--check` must never repair files or silently accept a new revision; `--update` is explicit and should not adopt upstream content without a reviewed pin change.
- **Duplicate/ambiguous identity is an error.** The red–green test added on 2026-11-20 confirms the baseline originally accepted duplicate JSON object keys and stripped "verbatim" whitespace. Those bugs have test-backed repairs; see [red run 44733303084](https://github.com/rock-solid-sites/ASES/actions/runs/44733303084) and [green run 44733411686](https://github.com/rock-solid-sites/ASES/actions/runs/44733411686).
- **Do not delete historic material as a substitute for proving precedence.** Retired skills and alternate global paths may still be discoverable in some harnesses. The distribution pilot must not assert that publication controls the harness's other instruction channels.
- **No automatic cross-project push yet.** Source update `->` consumer pin review `->` regenerated diff `->` local `--check` `->` independent runtime verification is a **proposed** production sequence, not a deployed sync process.
- **Evidence categories must stay distinct:** source inspected, generated artifact compared, model-visible exposure tested, agent behavior measured, and production rollout approved are different statuses. Never turn a successful unit test into a claim that the last four are proven.

## 5. Experiment evidence and independence

- **WNASES-18:** Independent Codex Cloud Luna experiment failed *before checkout* because no usable execution environment was made available. It produced no code, tests, branch or PR. The coordinator-authored [PR #64](https://github.com/rock-solid-sites/ASES/pull/64) is a separate offline baseline, **not Luna's independent result**.
- **WNASES-19:** OpenCode exposure experiments are owned and evidenced separately in [draft PR #63](https://github.com/rock-solid-sites/ASES/pull/63). Their runtime findings are not a validation of this policy publisher. Do not provide the coordinator baseline implementation to an eventual independent first-pass Luna builder before freezing that builder's output.
- **Execution finances:** Luna is reserved for authenticated ChatGPT Plus/Codex. Other approved model tests belong to OpenCode Go subscription or verified zero-price Zen; no inferred model, paid API route or fallback. No model call is needed to validate this document or the local publisher tests.

## 6. Promotion gates and cheapest remaining tests

1. **Document authority test:** for a candidate real ASES rule, identify canonical source, status, owning repository, exact revision, authorized project owner and permitted override. If those cannot be established, do not import it as binding policy.
2. **Publisher conformance test:** use a temporary synthetic manifest with conflicting overrides, duplicate identities and changed source; confirm error rather than merged or silently repaired output. These tests are partly executed; production exceptions and source-ownership controls remain unimplemented.
3. **Consumer-drift test:** in a disposable clone, change local generated instructions by hand and verify `--check` rejects without overwriting; retain the failure evidence.
4. **Harness exposure test:** independently measure whether original, override, other-root, global or retired-skill texts actually reach a *specific* agent's input. This cannot be inferred from an offline publisher.
5. **Operator decision:** compare an explicit copy-and-hash review process against a generated manifest. Adopt a publisher only if observed drift/error reduction justifies its upkeep. No production migration before that decision.

**WHAT-NOT-TESTED:** real project distribution, nested `AGENTS.md` precedence, plugin/global skill injection, source signature/approval, private project rules, multi-repository propagation and rollback, model-visible prompt contents, quality improvement and compliance under actual launchers. No new Resource Solver work, live provider experiment or unrelated streaming diagnostics are part of this document.
