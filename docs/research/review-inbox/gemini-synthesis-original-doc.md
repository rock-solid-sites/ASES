## Review Summary: CHANGES REQUESTED (gemini-3.5-flash synthesis of 8 reviews)

### 1. Per-Review Summaries
1. ChatGPT web chat (External): strong current-state inventory but weak as an adversarial assurance document; 'read-only by construction' not established because git * / cargo * / npm * / opencode * / crosslink * allow indirect mutation and authority escalation; add indirect-mutation attack matrix + security invariants + test transitive authority.
2. Claude Sonnet 5 (External): critical — Builder can edit .crosslink/hook-config.json to loosen its own restrictions (edit:allow + unrestricted bash); #313 sqlite3 block treated as settled fact when the blocking layer was not instrumented; opencode fork justification rests on a single unconfirmed internal incident (#156); orchestrator-guard MCP tool audit incomplete; sentinel block and signing enforcement unexplained.
3. GLM-5.2 (External): default-to-builder race condition in identity resolution; arbitrary bash via allowlist bypasses (npm/cargo as trampolines); blocking sqlite3 prevents the Auditor's core function (architectural contradiction); --allowedTools surface is dead code; stacking layers created a larger attack surface than the one it attempted to close.
4. Deepseek-v4-Pro (External): Builder sandbox virtually nonexistent (can modify guard config, forge active-issue sentinels, bypass wrapper); emergency kill-switch fails open when crosslink unavailable; --allowedTools is an unenforced fiction; enforcement rests on integrity of external binaries/paths; workflow topology largely aspirational.
5. Qwen3.8 Max (External): read-only by construction overstated (git */opencode */crosslink * allow writes, config changes, nested session launches); enforcement plane mutable by Builder; identity resolution defaults to builder (fail-open); no explicit adversary model (compromised agents, prompt injection); recommend narrow sandboxed allowlists + threat-model section.
6. luna (Internal #315): git * + finite blocklist leaves unlisted mutators (git update-ref, git config) unblocked; --allowedTools no-enforcement claim overbroad (container path passes it); countable errors (29 vs 49 bash entries); model whitelist claims stronger than plugin source supports.
7. hy3 (Internal #316): deployed-binary vs source-tree version conflation (doc cites undeployed commit 6221309e; live binary 0.9.0-beta.1+a87bd513); allowed_bash_prefixes is an allow-fast-path NOT a denying surface; by_type fallback fail-open (defaults to builder); wrapper injects --auto for all tmux launches.
8. kimi (Internal #317): orchestrator-guard blocks filesystem_write_file/filesystem_edit_file but the actual MCP server exposes write_file/edit_file/create_directory/move_file — MCP leg of #33677 gap NOT closed; crosslink binary version mismatch; --allowedTools claim misses container path; orchestrator-guard lacks CROSSLINK_AGENT_TYPE env fallback.

### 2. Cross-Reviewer Agreement Matrix
| Finding / Theme | ChatGPT | Sonnet5 | GLM | Deepseek | Qwen | luna | hy3 | kimi | Count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Read-only by construction overstated | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| Builder can modify enforcement config | Partial | Y | Partial | Y | Y | N | Y | N | 6/8 |
| --allowedTools surface dormant/dead | Y | Y | Y | Y | Y | Y | Y | Y | 8/8 |
| Identity resolution fails open to Builder | Y | Y | Y | Y | Y | N | Y | Y | 7/8 |
| No explicit adversary/threat model | Y | Y | Y | Y | Y | N | Y | N | 6/8 |
| Deployed-vs-source version conflation | N | N | N | N | N | Y | Y | Y | 3/8 (all internal) |
| Countable claim errors | N | N | N | N | N | Y | Y | Y | 3/8 (all internal) |
| Wrapper injects --auto under tmux | N | N | Y | N | N | Y | Y | Y | 4/8 |
| MCP filesystem tool names mis-identified | N | Partial | N | Partial | Partial | N | N | Y | 4/8 |
| Confidentiality/exfiltration unaddressed | Y | N | N | Y | Y | N | Y | N | 4/8 |
| #313 sqlite3 treated as settled fact | Y | Y | Y | Y | Y | N | Y | N | 6/8 |
| Model-whitelist plugin global | N | Y | N | N | Y | N | Y | N | 3/8 |

### 3. Unique Findings List
- kimi: orchestrator-guard MCP tool-name mismatch; lacks CROSSLINK_AGENT_TYPE env fallback.
- hy3: allowed_bash_prefixes is allow-fast-path not enforcement; isAgentContext precondition omitted.
- Sonnet 5: fork justification rests on single unconfirmed incident (#156); model-whitelist plugin global to machine.
- GLM-5.2: stacking layers created larger attack surface.
- Deepseek: emergency kill-switch fails open when crosslink unavailable.
- luna: model whitelist claims stronger than plugin source supports (cache merge re-enables providers).

### 4. Contradictions / Divergences
- --allowedTools: doc says never enforced; luna+kimi: only true for local tmux — container path passes it directly.
- #313 sqlite3 block: doc treats as settled fact; Sonnet5+hy3: actual blocking layer was not instrumented.
- 'Strict Fail-Open': GLM-5.2 — you cannot have 'strict' fail-open security (rtk-guard).
- Mode: opencode.json says subagent; agent .md files say primary (hy3).

### 5. Synthesis + Recommended Revision Priorities
Collective view: excellent, candid current-state inventory, but the central claim (reviewer/auditor read-only by construction) is unanimously judged overstated / false confidence. System suffers 'enforcement sprawl' — overlapping, fail-open, mutable controls that do not form a hardened boundary against a compromised agent.
Highest-confidence actionable findings:
1. Deployed-vs-source version conflation — report deployed 0.9.0-beta.1+a87bd513 separately from source HEAD 6221309e.
2. Weaken read-only-by-construction; enumerate indirect paths (git config, cargo run, npm run, opencode run --pure).
3. MCP filesystem tool names — orchestrator-guard blocks wrong names; MCP leg of #33677 NOT closed.
4. Countable errors — bash 49 (not 29), agent_overrides 21 (not 19), orchestrator patterns 34 (not ~40).
5. Wrapper injects --auto (auto-approves ask permissions under tmux).
6. Qualify --allowedTools by launch mode.
MUST FIX: version mismatch, countable errors, MCP tool names, weaken read-only + indirect-mutation threat matrix, qualify --allowedTools.
SHOULD CONSIDER: dedicated threat-model section, document --auto, model-whitelist global scope, allow-fast-path behavior, isAgentContext precondition.

### WHAT-NOT-TESTED
- No bypass executed (opencode run --pure, cargo run, npm run, git config not demonstrated).
- Runtime hook ordering / throw short-circuit not measured.
- Container image claude binary / --allowedTools forwarding not verified.
- Guard logs under /tmp not read.
