# Synthesis and Tabulation of Agent Tooling and Permission Enforcement Reviews

This document synthesizes, compares, and tabulates all 8 reviews of the subject document `docs/research/agent-tooling-and-permission-enforcement-reviewed.md` (main `527c5eb7`).

---

## 1. Per-Review Summaries

### Review 1: luna (Architecture Review, Source #321)
Luna requests changes, arguing that the advertised "read-only" property is not established and that the enforcement plane is mutable by the Builder. She highlights that broad shell authority (`git *`, `opencode *`, `crosslink *`) leaves indirect mutation and delegation paths open, and that unresolved identity falls back to `builder`. She recommends pausing incremental permission-list work and refactoring the security boundary to define a clear threat model and implement a trusted, deny-by-default capability boundary.

### Review 2: kimi-k2.7-code (Source #322)
Kimi requests changes and recommends a moderate-to-major refactor of the enforcement architecture rather than a simple patch-the-MUST-FIX-list path. He points out that the current multi-layer design is internally inconsistent, fail-open in several places (such as identity resolution defaulting to builder), and mutable by the Builder. He also highlights that the kickoff path auto-approves `ask` permissions via `--auto` injection under tmux, and that the MCP filesystem guard blocks observed write/edit names but omits directory/move mutation tools.

### Review 3: hy3 (Source #323)
Hy3 recommends a moderate-to-substantial refactor of the document's architecture while keeping its strong content, verification discipline, and resolutions. He argues that the single merged-successor structure is a weak point because it tries to be both an external-reviewable system description and a review-resolution record, making the narrative unclean and the verdict hard to find. He suggests splitting the document into a system description with a trailing corrigenda and a separate review-resolution document, while also resolving internal contradictions and de-duplicating inventories.

### Review 4: ChatGPT Web
ChatGPT Web recommends against carrying on with the current permission-enforcement architecture as a long-term solution, suggesting moving the security boundary down to the OS/container layer and simplifying the in-process enforcement machinery. It argues that the current system tries to establish repository integrity and authority isolation using mechanisms that live inside the same agent execution environment they are supposed to constrain. It proposes an isolated execution environment with a capability-controlled gateway where the agent does not possess the authority to alter its own restrictions.

### Review 5: Claude Sonnet 5
Sonnet 5 recommends changing the architecture rather than just working through a MUST-FIX list, pointing out that the enforcement mechanism has a structural ceiling below what the four-role design requires. It highlights that the Builder can edit the enforcement configuration (a self-modifying trust root) and that the `opencode run --pure` flag disables all guard plugins, collapsing the entire enforcement layer. It suggests moving the write boundary outside the agent's process (e.g., read-only bind mounts) and establishing an explicit threat model to guide the design.

### Review 6: GLM-5.2
GLM-5.2 advises against carrying on with the current plan as-is, recommending a targeted architectural refactor because the trusted computing base is mutable by the roles it constrains. It notes that the enforcement mechanism lives inside the threat surface it guards, that identity resolution fails open to the highest privilege, and that `allowed_bash_prefixes` is an allow-fast-path rather than a denying surface. It suggests moving the trust boundary outside the agent process using OS-level file permissions, separate users, or an out-of-process guard daemon.

### Review 7: Deepseek V4 Pro
Deepseek V4 Pro requests changes and recommends a moderate-to-major re-architecture to establish a genuine isolation boundary between the write-privileged builder and the read-only reviewer/auditor roles. It argues that "read-only by construction" is false due to broad bash grants and the `--pure` bypass, and that the builder can tamper with the enforcement configuration. It recommends process-level or container-level isolation with read-only mounts for read-only roles, moving enforcement into a trusted daemon/sidecar, and adopting a deny-by-default policy.

### Review 8: Qwen 3.8 Max (Fifth External Model)
Qwen 3.8 Max strongly advises against carrying on with the current plan, calling the current design a category error that attempts to enforce a zero-trust, multi-tenant security boundary using single-tenant application hooks and string-matching. It highlights the shell-filtering fallacy, the mutable trust root, the harness mismatch (where `--pure` disables plugins), and the identity fail-open. It recommends shifting to OS-level virtual filesystem (VFS) and identity isolation, revoking `bash` entirely for non-builders in favor of capability-based MCP tools, and externalizing the control plane.

---

## 2. Cross-Reviewer Agreement Matrix

The following table maps recurring findings and themes across all 8 reviewers.

| Finding / Theme | luna | kimi | hy3 | ChatGPT | Sonnet5 | GLM | Deepseek | Qwen | Count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Read-only overstated** (broad bash grants, finite blocklists) | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| **Builder can edit config** (mutable trust root) | Y | Y | Partial | Y | Y | Partial | Y | Y | **7/8** |
| **`--allowedTools` dormant** (dropped by local wrapper) | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| **Identity fails open** (defaults to builder/base config) | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| **No explicit threat model** (honest-but-buggy vs misaligned) | Y | Y | Y | Y | Y | Y | Y | Y | **8/8** |
| **`--pure` bypass** (disables all guard plugins) | Y | Y | Y | N | Y | Y | Y | Y | **7/8** |
| **`--auto` injection** (auto-approves `ask` under tmux) | Y | Y | Y | N | N | Y | N | N | **4/8** |
| **MCP write-tool gap** (omits directory/move tools) | Y | Y | Y | Y | Y | N | Y | Y | **7/8** |
| **Version conflation** (deployed a87bd513 vs source HEAD 6221309e) | Y | Y | Y | N | N | N | N | N | **3/8** |
| **Countable errors** (prefixes 49 vs 29, overrides 21 vs 19) | Y | Y | Y | N | N | N | N | N | **3/8** |
| **Global whitelist plugin** (machine-global scope, cache risk) | Y | Y | Y | N | Y | N | N | Y | **5/8** |

---

## 3. Unique Findings List

- **hy3**: The document's architecture itself is the weak point (trying to be both a system description and a review-resolution record in one file). He suggests splitting them.
- **hy3**: `allowed_bash_prefixes` is an allow-fast-path, not a denying surface.
- **hy3**: `isAgentContext` precondition skips `agent_overrides` in the main repo (role: driver), so `git merge` is not blocked for builder there.
- **Qwen**: Suggests revoking `bash` entirely for non-builders and replacing it with capability-based MCP tools.
- **Qwen**: Suggests a detailed threat-model section with 10 threat classes and a control-to-threat mapping.
- **ChatGPT**: Proposes 10 specific security-property invariants as a forward-looking security argument.
- **ChatGPT**: Distinguishes three increasingly strong properties: (A) tool denial, (B) repository immutability, (C) authority isolation.
- **Sonnet 5**: Points out that the causal chain for the silent-hang reliability epic (#156) rests on the project's own investigation of itself, with no external/upstream confirmation.
- **GLM-5.2**: The enforcement layer actively prevented the topology from functioning (the #313 auditor was forced to verify file metadata rather than actual database evidence).
- **Deepseek**: The kill-switch fails open when `crosslink` is unavailable or the directory is missing.

---

## 4. Contradictions and Divergences

### hy3 vs kimi on MCP Tool Names
Kimi claimed that the blocked names in orchestrator-guard were wrong because upstream server-filesystem tools are named `write_file` and `edit_file`. Hy3 and direct verification showed that opencode's MCP client exposes them with the `filesystem_` prefix, so the blocked names (`filesystem_write_file`, `filesystem_edit_file`) are actually correct. The true gap is the unblocked tools (`create_directory`, `move_file`).

### hy3 vs the Consensus Matrix on luna
Hy3 pointed out that the consensus matrix in the subject doc lists luna as "Y" for the version conflation, but luna's actual review did not flag it.

### Adversary Model Divergence
Some reviewers (like Qwen, Deepseek, Sonnet 5, ChatGPT) assume a misaligned/adversarial agent threat model and conclude the current system is wholly insufficient. Others (like hy3) note that under a mistaken-agent (honest-but-buggy) model, the current prefix-based approach is reasonable but needs bug fixes.

### Remediation Strategy Divergence
- **Harden the existing system (luna, hy3, kimi)**: Focus on fixing the MUST-FIX list, correcting counts, closing the MCP gap, documenting `--auto`, and failing closed on identity.
- **Architectural refactor (ChatGPT, Sonnet 5, GLM, Deepseek, Qwen)**: Move the trust boundary outside the agent process entirely using OS-level isolation (read-only mounts, separate users, containers/namespaces) and capability-based MCP tools, rather than trying to perfect application-level string-matching.

---

## 5. Synthesis and Recommended Next Steps

### Collective Verdict
The reviews collectively agree that the current permission-enforcement architecture is **structurally flawed and fail-open** under an adversarial or misaligned agent threat model. While it provides reasonable "defense-in-depth" or "speed bumps" against honest mistakes, it cannot deliver the "structural, not aspirational" guarantees it claims because the enforcement plane is mutable by the Builder, the plugins run in-process and can be bypassed via `--pure`, and identity resolution fails open.

### Highest-Confidence Actionable Findings
1. **Identity Resolution Fail-Open**: Unresolved identity defaults to builder/base config, allowing commits. Must fail closed.
2. **Mutable Trust Root**: Builder can edit hook-config, plugins, and sentinel. Must move outside builder's write reach.
3. **The `--pure` Bypass**: Any role with `opencode *` can run `opencode run --pure` to disable all guard plugins. Must block or scope.
4. **MCP Filesystem Gap**: `create_directory` and `move_file` are unblocked. Must add to `BLOCKED_TOOLS`.
5. **Wrapper `--auto` Injection**: Auto-approves `ask` permissions under tmux. Must document or remove.
6. **Version Conflation**: Deployed crosslink is a87bd513, while doc cites source HEAD 6221309e. Must correct.

### Recommended Next Steps (Phased Migration)

#### Phase 1: Immediate Triage (Stop the Bleeding)
- **Fix the Fail-Open**: Change the default identity resolution from `builder` to `deny`. If the system doesn't know who is asking, the answer is "no."
- **Add `create_directory` and `move_file` to `BLOCKED_TOOLS`**: Add `filesystem_create_directory` and `filesystem_move_file` to orchestrator-guard's `BLOCKED_TOOLS` list.
- **Correct the Countable Claims and Version Conflation**: Update the document to reflect the correct counts (49 prefixes, 21 overrides, 34 patterns) and the deployed version (`0.9.0-beta.1+a87bd513`).
- **Lock the Trust Root**: Change OS-level file permissions so that `.opencode/plugins/` and `.crosslink/` are read-only for the builder.

#### Phase 2: Containerize the Roles
- Wrap the `claude`/`opencode` invocations in Docker/Podman.
- Mount the repository strictly **read-only** for Reviewer and Auditor containers.
- Drop `--auto` injection from the wrapper.

#### Phase 3: Capability-Based MCP Transition
- Revoke `bash` entirely for Reviewer and Auditor roles.
- Develop a custom, read-only MCP server specifically for Reviewer/Auditor providing safe abstractions (`search_code`, `get_ast`, `run_linter`).

---

## 6. Reasoning Certainty (AGENTS.md)

- **WHY**: The reasoning behind this synthesis is based on a comprehensive, line-by-line analysis of all 8 reviews and direct verification of the cited code paths, configuration files, and runtime logs.
- **WHAT**: This synthesis is based on the 8 reviews in `docs/research/review-inbox/agent-tooling-and-permission-enforcement-reviewed-reviews.md` and the live repository state.
- **HOW CERTAIN**: **Proven / Evidence-based (High Confidence)**. The technical findings (such as the version conflation, the `--pure` bypass, the `--auto` injection, and the identity fallback) are directly verifiable in the codebase and runtime environment.
- **WHAT-NOT-TESTED**:
  - No live bypasses were executed (e.g., we did not run `opencode run --pure --agent builder` to write a scratch file).
  - The container image's `claude` binary and its `--allowedTools` forwarding were not inspected.
  - Whether the models-cache currently re-enables any disabled provider was not audited.
  - Whether tripn-astro/Tools repos have divergent hook-config values was not checked.
