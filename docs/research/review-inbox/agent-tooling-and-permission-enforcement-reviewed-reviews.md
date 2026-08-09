# External Reviews - agent-tooling-and-permission-enforcement-reviewed.md

Collected reviews from external models. Paste each review verbatim into its slot. Subject doc: main 527c5eb7.

## Review 1

### Model
luna
### Review

````
## Review Summary: CHANGES REQUESTED

I would **not carry on with the current enforcement plan**. I would retain the goal, but refactor the security boundary before adding more deny-list rules. The document itself shows that the advertised read-only property is not established and that the enforcement plane is mutable by the Builder.

### MUST FIX (blocking)
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:502-516` — The corrected resolution says Reviewer/Auditor are only direct-write-tool-denied, while broad `git *`, `opencode *`, `crosslink *`, and finite blocklists leave indirect mutation and delegation paths open. This invalidates “read-only by construction” as an architectural contract. Replace the broad shell authority with a deny-by-default, role-specific capability boundary; do not try to close this solely with more prefix blocklist entries.
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:921-945` — Builder can modify live hook configuration, the active-issue sentinel, and guard plugins. A mutable trust root cannot enforce the Builder/non-Builder separation. Put policy and authorization state outside Builder-writable paths (for example a separate privileged controller plus immutable/read-only mounts or equivalent OS/container isolation).
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:851-868` — Unresolved identity falls back to `builder`, and the two guards resolve identity inconsistently. This is a privilege-escalation failure mode. Make identity resolution fail closed before any security-sensitive tool call, and bind authorization to an authenticated launch/session identity rather than event-order-dependent fallback.
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:695-724` — The MCP guard blocks observed write/edit names but omits the inferred directory/move mutation tools, while the filesystem server is rooted at the main repository. Complete enumeration and deny-by-default MCP capabilities are required before claiming structural protection.
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:576-606` — `--allowedTools` is dead on the local path but active/unknown on the container path, and its generated list is identical across roles. Remove the unsupported control or implement and verify one canonical, per-role enforcement path; never leave a security-looking dormant path.

### SHOULD CONSIDER (non-blocking)
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1197-1216` — Decide and state whether the threat is accidental error or a compromised/misaligned agent. Without that decision, “structural enforcement” has no testable security target.
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1363-1416` — Use the listed MUST-FIX items as a gate, but prioritize boundary redesign over count corrections and documentation cleanup. The document correctly identifies count errors, `--auto`, allow-fast-path semantics, deployment drift, and missing tests; these are evidence that the current multi-layer arrangement is difficult to reason about, not just a collection of isolated defects.
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1426-1511` — Turn the proposed invariants into adversarial tests, especially indirect writes, delegation, identity failure, git ref/config mutation, hook composition, sentinel trust, and log integrity.

### NITS (optional)
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1300-1326` — The consensus matrix has attribution/count caveats that make it harder to use as a decision artifact; separate measured facts, source-derived inferences, and reviewer opinions into distinct tables.

### NOTABLE POSITIVES
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:26-55` — The document is unusually transparent about scope and evidence.
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:502-534` — It correctly retracts the strongest read-only claim and clearly records untested bypasses rather than presenting capability inference as a runtime demonstration.
- `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1515-1599` — The consolidated WHAT-NOT-TESTED list and open questions provide a strong basis for a threat-model-led redesign.

**Recommendation:** pause incremental permission-list work; define the threat model and security invariants, then implement one trusted, deny-by-default capability boundary for non-builder roles, with immutable policy state and deployment-pinned verification. Resume the plan only after the boundary passes the adversarial tests documented here.
````

## Review 2

### Model
kimi-k2.7-code
### Review

````
## Review Summary: CHANGES REQUESTED — do not carry on with the current plan as-is

I read `docs/research/agent-tooling-and-permission-enforcement-reviewed.md` end-to-end. The document is an impressive piece of review synthesis, but the architecture it describes is not one I would simply continue implementing. I would recommend a **moderate-to-major refactor** of the enforcement architecture rather than a patch-the-MUST-FIX-list path.

### Why I would not carry on as planned

The report itself demonstrates that the current multi-layer design (opencode native `.md` + `orchestrator-guard` + `crosslink-guard` + `rtk-guard` + wrapper model enforcement) is **internally inconsistent and fail-open in several places**. Continuing to layer more fixes onto this foundation risks building more sophisticated false confidence. The core architectural problems are not coding mistakes; they are authority-boundary mistakes:

- **No threat model means no falsifiable security claims.** `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1163-1216` confirms the document never states whether the adversary is an honest-but-buggy agent or a misaligned/compromised one. Until that is decided, “read-only by construction” is not a testable property.
- **The enforcement plane is mutable data for the very role it must constrain.** `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:883-957` shows the builder has unrestricted `edit` and `bash`, and there is no mechanism protecting `.crosslink/hook-config.json`, `.active-issue`, `.opencode/plugins/*.ts`, or user-level configs from the builder. A permission model whose guard config can be edited by the guarded principal is not a boundary.
- **Identity resolution fails open to the least-privileged role.** `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:811-881` confirms that an unresolved reviewer/auditor falls back to `agent.type = builder`, and because there is no `by_type.builder` entry, `git commit` becomes gated rather than blocked. The plugin logs “FAIL-CLOSED,” but the posture is fail-open.
- **The kickoff path auto-approves `ask` permissions.** `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:958-1013` documents the wrapper injecting `--auto` unconditionally under tmux, which is exactly the kickoff path. This materially weakens the `.md` permission surface.
- **Read-only is overstated to the point of being misleading.** `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:447-535` and `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:741-809` show reviewer/auditor have `git *`, `opencode *`, `crosslink *`, and reviewer also `cargo *`/`npm *`. The blocklists are finite and prefix-based, so indirect mutation (e.g., `opencode run --pure --agent builder`, `npm run`, `git config core.hooksPath`) is not ruled out.

### MUST FIX before any implementation continues

1. **Adopt an explicit threat model.** Map every control to the threats it mitigates and those it does not (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1163-1216`, Qwen §9).
2. **Make the enforcement policy immutable to the builder.** Move guard config, sentinel, and plugin logic out of the builder’s write reach — signed read-only config, separate user/mount, or a trusted computing base. The current live-read `hook-config.json` model is not acceptable (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:883-957`, Sonnet 5).
3. **Fail closed on identity resolution.** Default to deny, not builder; add a `by_type.builder` entry so the fallback is at least explicit (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:811-881`).
4. **Remove or harden the `--auto` injection.** Either stop passing `--auto` in the kickoff path, or document and accept that `ask` permissions become effective grants (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:958-1013`).
5. **Close the MCP write-tool gap.** Add `filesystem_create_directory`/`filesystem_move_file` to `BLOCKED_TOOLS` and enumerate all enabled MCP tools (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:663-739`).
6. **Reconcile deployed-vs-source crosslink versions.** Re-verify kickoff claims against the deployed binary `0.9.0-beta.1+a87bd513`, not the undeployed source HEAD `6221309e` (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:608-661`).
7. **Correct the countable/factual errors.** 49 vs 29, 21 vs 19, 34 vs ~40, and the stale seven-model whitelist (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1015-1079`, `docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1218-1294`).
8. **Replace broad bash grants for read-only roles with deny-by-default least-privilege allowlists.** “Read-only” must mean repository immutability, not merely that the write-tool primitive is blocked (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:447-535`, Qwen §9 item 4).

### SHOULD CONSIDER

- **Centralize configuration.** The report identifies nine distinct config locations (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1218-1294`). Pick one authoritative source; everything else should be generated from it or explicitly deprecated.
- **Remove or complete dead controls.** `--allowedTools` is a false-assurance surface on the local tmux path (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:536-607`). Either make it enforced end-to-end, per-role, and least-privilege, or delete it.
- **Define hook-composition invariants.** Ordering, short-circuiting on `throw`, and plugin-load-failure behavior are currently unspecified (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1487-1498`).
- **Add automated adversarial tests.** The report lists many capability-inference findings that were never exercised; the cheapest way to stop regressions is tests (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1515-1575`, Qwen §9).
- **Move model enforcement inside crosslink/opencode.** Relying on a user-editable bash wrapper is another self-modifying trust root (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1218-1294`).
- **Document the `isAgentContext` / main-repo `role: driver` gap.** In the main repo the `agent_overrides` skip, so `git merge` is not blocked for the builder there (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:145-164`).

### NOTABLE POSITIVES

- The reviewed document itself is a strong research artifact: self-contained, line-referenced, includes a cross-reviewer consensus matrix, and consistently marks what was not tested. It gives a clear map of what is broken.
- The reviewer-proposed invariants in section 5 (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1420-1511`) are a sound starting point for a refactored design.
- The verification appendix (`docs/research/agent-tooling-and-permission-enforcement-reviewed.md:1603-1737`) makes the findings externally checkable.

### Bottom line

I would **not** carry on with the current layered plan. I would refactor around a **single, external, immutable policy engine** with fail-closed identity, deny-by-default capabilities, and an explicit threat model, then validate it with adversarial tests. If the project cannot protect the enforcement config from the builder and cannot resolve agent identity reliably, the current architecture cannot deliver the “structural, not aspirational” guarantee it claims.
````

## Review 3

### Model
hy3
### Review

````
## Review Summary: DO NOT carry on as-is — keep content, refactor document architecture

**Recommendation: Do NOT carry on with the current plan as-is. Recommend a moderate-to-substantial refactor of the document's architecture — but keep the content. The single merged-successor structure is the weak point; the verification discipline and resolutions are strong and should be preserved.**

### WHY
The document assigns itself two incompatible jobs and tries to do both in one 1737-line file: (1) be the external-reviewable system description, and (2) be the review-resolution record (fold in 8 reviews, adjudicate 12 contested claims). These pull opposite ways. A system description wants a clean narrative; the review record wants attribution and contested-claim detail. Interleaving CORRECTED flags into section 2 makes the description unclean; burying resolutions inside 12 FINDINGS-heavy sections makes the verdict hard to find.

Additional problems: (a) self-containment is only partial — the #33677 gap is never defined inline, and external docs are cited as authority for a zero-context reader; (b) the document exhibits the very nine-config-locations problem it criticizes — the 49 bash prefixes / 21 git commands / 34 patterns are listed in four places that drift independently; (c) internal inconsistencies: claim (c) says luna did not flag the version conflation while the section 4 matrix lists luna Y; claim (d) frames kimi's MCP finding as refuted when only its mechanism (tool names) was wrong while its conclusion (MCP leg open) was confirmed; (d) the document identifies the missing adversary model as the core unfalsifiability but resolves claims as if the adversary is a mistaken agent without stating that as policy.

### WHAT (keep content, change structure)
1. Split the two jobs: keep the original as the system description with corrections in a trailing CORRIGENDA; put the 12-claim adjudication + consensus + invariants + what-not-tested in a separate review-resolution document.
2. Lead with resolution: each claim opens with RESOLUTION + WHY + WHAT-NOT-TESTED; attribution moves to a secondary block or appendix.
3. State the resolution policy explicitly: adopt mistaken-agent vs misaligned-agent framing in section 1 and resolve all claims under it.
4. Close self-containment gaps: define #33677 inline; quote facts instead of citing external docs; resolve or flag the mode-primary-vs-subagent contradiction.
5. De-duplicate inventories: one canonical inventory; narrative references it by line.
6. Fix the internal contradictions (luna Y vs did-not-flag; kimi refuted vs confirmed).
If a single merged document is required: reorder to put resolution summary first, add adversary-model framing, fix contradictions, cut inline config duplication.

### HOW CERTAIN
Evidence-based, high confidence on the architectural critique — rests entirely on the document's own text (full 1737-line read). Did not re-verify technical claims against live sources (task constraint: read the document ONLY).

### WHAT-NOT-TESTED
Could not run crosslink to post the result (bash-deny rule; verified by two failed attempts). Did not open the underlying config/plugin files, the original, or the other reviews (per task constraint) — assessment of the document as an artifact, not re-verification of technical claims. Did not execute any claimed bypasses.

### NOTABLE POSITIVES
The CLAIM/FINDINGS/RESOLUTION/WHY/WHAT-NOT-TESTED structure is exactly the project's reasoning-certainty discipline. Consistent propagation of (unverified)/source-derived/runtime-observed distinctions. The verified-sources appendix + 5-minute check script is a strong reproducibility asset. The consensus matrix and MUST-FIX/SHOULD-CONSIDER consolidation are genuinely useful. Section 5 invariants translate reviews into a forward-looking security argument.

**Bottom line:** the research is sound and should be carried forward; the packaging (one merged successor that is simultaneously spec + review + resolution) should be refactored before this is treated as the canonical external-reviewable record.
````

## Review 4

### Model

### Review

````
(paste the full review markdown here - replace this placeholder with the review, keeping the fence)
````

## Review 5

### Model

### Review

````
(paste the full review markdown here - replace this placeholder with the review, keeping the fence)
````

## Review 6

### Model

### Review

````
(paste the full review markdown here - replace this placeholder with the review, keeping the fence)
````

## Review 7

### Model

### Review

````
(paste the full review markdown here - replace this placeholder with the review, keeping the fence)
````

## Review 8

### Model

### Review

````
(paste the full review markdown here - replace this placeholder with the review, keeping the fence)
````

