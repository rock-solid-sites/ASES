---
title: "External-family verifier routing — no Projektor dispatch assumption"
version: 0.1.0-experimental
status: proposed-unverified
authority: run-scoped-design
run_id: ASES-SOL-CTRL-A-20261113
---

# Cross-family reviewers: Luna executes the route, Sol owns verdicts

**No live cross-family route is claimed.** Work Notes/Projektor can log work and reports; they are NOT assumed to launch models or bridge runtimes. External review is an optional independent gate until a bounded live test verifies actual authenticated execution.

## Routing preference

### A. Stateless external-model review (preferred when tools are unnecessary)

A Luna dispatcher assembles a bounded **blind review packet** from frozen requirements, source pins, implementation source/diff, necessary adjacent contracts and interface material, plus requested claim/falsification obligations. **Do not include builder's rationale, green-test narrative, known predicted weak points or peer review output.** The dispatcher invokes an approved external-family inference endpoint directly (or a headless OpenCode reviewer with all tools disabled when a working route already exists). Cloud compute is unnecessary when the request is only an LLM inference call. Even with no reviewer tools, Luna performs all input retrieval and output persistence.

The reviewer returns severity-ranked falsifiable findings, explicit counterexample suggestions, missing facts and a verdict qualified as **static cross-family analysis**. A tool-free review does **not** claim that code compiled, that native histories were run, or that the model searched the full repository. A separate Luna can turn the proposed falsifiers into executable tests; Sol weighs both results.

### B. Tool-using external-family review (only when justified)

A Luna launcher provisions an explicitly approved, bounded sandbox and runs a configured OpenCode model against a read-only or isolated checkout. Use a narrow review agent with edits, destructive operations and network side effects disabled, plus finite time/CPU/tokens. Only allow reproducible test execution when the review genuinely needs to exercise behavior. Preserve exact source refs, run command, provider/model provenance, console traces, findings and cleanup receipt.

**Candidate executors (NOT live/authorized):**
- **Modal:** first feasibility candidate; the account inventory reports user-confirmed account and previously functional local CLI, but no current credit/usage or sandbox launcher validation.
- **Daytona/E2B:** accounts are user-reported in registry; neither current balance, access path nor launch authorization has been verified.
- **GitHub Actions:** alternative isolated runner with its own billing/account attribution; not automatically approved for a new model secret.
- Do not use Projektor/Work Notes as an execution transport until a real dispatcher has been implemented and verified.

The ASES provider registry in PR #44 records product APIs and account evidence separately; `known_accounts_v1.json` is **not** live billing authority. The dedicated provider launcher must verify real credentials/permissions, quota, allowed network egress, model entitlement and cleanup. Do not invent credentials or commit secrets. No new paid/chargeable resources are authorized by this document.

## Minimal preflight performed by Luna, not Sol

1. **Tool-free route:** verify that an approved external model family/provider can receive a tiny nonsensitive test prompt and return a signed or directly observed identity/version response from actual API metadata, not its own self-claim. Require no repository content in the capability check.
2. **Sandbox route if needed:** verify one approved tiny job with a controlled time/expense ceiling, selected provider SDK/CLI, isolated filesystem and cleanup receipt; test headless `opencode run --model provider/model --agent reviewer` only after confirming an actual enabled model and credentials. If sandbox creation is chargeable and no approval or existing free entitlement is verified, do not launch.
3. For a real review, create a content-bounded blind packet and record its SHA; store raw reviewer output and model dispatch provenance outside parent context. A separate verification Luna converts material findings to tests.
4. Return to Sol only `CLAIM | CROSS-FAMILY FINDINGS | EXECUTABLE FOLLOW-UP | UNCERTAINTY | REFS` in <=250 words. The external reviewer **does not** directly accept or merge changes; Sol applies the precommitted acceptance criteria.
5. If the route fails, record the exact failure and fall back to a distinct Luna verifier labeled same-family; do not claim heterogeneous review.

## Independence and data boundary

No tools creates useful model independence but not automatic evidence sufficiency. Independent review needs adequate implementation context; a narrow input packet must contain every relevant interface and preserve exact source provenance. Let the reviewer ask for missing context via Luna, not secretly expand its authority. A review can find logical defects without runtime tools; actual process safety or concurrency claims ultimately require runnable controls and source/cut observation.

Avoid streaming whole private repositories or credentials into an unverified provider API. Use the smallest necessary source bundle and check provider data handling before transmission.

## Local constraints and relationship

Primary orchestrator uses subagent coordination only; Luna owns all invocations, packaging, capture, Git and Work Notes records. Independent external-family verification is preferred once *working*, not required as a fictitious successful step. The user may choose an external model provider; do not assume availability or automatically charge their account.

Provider discovery: `research/provider-registry/known_accounts_v1.json` and PR #44's registry mapping. Worker skill references: `skills/prompt/SKILL.md@0.5-draft`; Strategy-to-Builder canonical build method. Separate review modes must respect zero-context/post-build adversarial method.
