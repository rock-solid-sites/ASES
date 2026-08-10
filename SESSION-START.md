# SESSION-START — read this first (every session)

This is the routing entry point. Its only job is to point you at the right
information. Read it once, then follow the pointers. If a pointer doesn't
resolve, see §5 — the doc is stale, not you.

**Ending a session?** See `docs/SESSION-END.md` for handoff conventions.

Model routing: before dispatching agents, consult the Model Routing Matrix (knowledge page: model-routing-matrix, or capability-mapping/Model-Routing-Matrix.md) to pick the model by task type, review lens, and token cost.

## START-SEQUENCE

- **Run `crosslink session last-handoff` on session start** — read the
  previous session's handoff notes BEFORE proceeding. Any non-durable session
  information (state, decisions, gotchas) is captured in the handoff notes,
  not in permanent docs.
- **Lock warnings are KNOWN NON-BLOCKING NOISE** — if `crosslink session work`
  reports a stale lock, do **NOT** investigate it: proceed with the task. See
  the repo's knowledge pages for details. The lock system fix is tracked
  separately (#166/#173).

---

## 1. What this repo is

- `ORIENTATION.md` — the three layers (EDASES research / ASES methodology /
  Execution Engine). Everything maps to one of these. Read fully.
- `AGENTS.md` — the canonical operational rules governing every session
  (crosslink tracking mandatory, reasoning-before-artefacts, evidence vs
  inference, model discipline). Read fully.
- `ARCHITECTURE.md` + `README.md` — repo layout and project overview.
- `docs/ORCHESTRATOR.md` — orchestrator contract (plan/delegate/gate; never
  implement) plus the four-role permission matrix. Read if you are in the
  orchestrator role.
- `.opencode/permissions.md` — snapshot of the four-role permission maps
  (Orchestrator / Builder / Reviewer / Auditor) and the git-write rules.
- `docs/research/Workflow Topology Design and Reasoning Record.md` — the
  workflow-topology design and reasoning record (two claim-testing principles;
  position-emitting agents + durable store; cheap staleness trigger; AUDITOR as
  one-role/two-phase in-flight divergence verifier; reviewer as pre-consumption
  readiness audit). Operationalized in `AGENTS.md` (principles),
  `docs/ORCHESTRATOR.md` (procedure), and
  `.crosslink/knowledge/agent-orchestration-playbook.md` (§5.8,
  dispatch-level mechanics).

## 1b. Role routing — four-role permission model

This repo runs four specialist agent roles. Which one YOU are depends on how the
session was launched (`--agent <type>`, exported as `CROSSLINK_AGENT_TYPE`):

| Role | File | Mode | Writes files? | Git write |
|------|------|------|---------------|-----------|
| **Orchestrator** | `.opencode/agents/orchestrator.md` | primary | **No** (edit deny) | `git commit` + `git merge` **gated** on an active issue; `git push`/`rebase`/`reset`/`clean`/`checkout .`/`restore .`/`stash`/`tag`/`am`/`apply`/`branch -d/-D/-m` **blocked** |
| **Builder** | `.opencode/agents/builder.md` | subagent | Yes | `git commit` gated on an active issue; destructive/push/merge blocked |
| **Reviewer** | `.opencode/agents/reviewer.md` | subagent | **No** | all git writes blocked (read-only) |
| **Auditor** | `.opencode/agents/auditor.md` | subagent | **No** | all git writes blocked (read-only) |

The git rules are enforced by `agent_overrides.by_type.<role>` in
`.crosslink/hook-config.json` via the `crosslink-guard` plugin
(`blocked_git_commands` = hard block, `gated_git_commands` = allowed with an
active Crosslink issue). The `orchestrator-guard` plugin blocks write-path tools
for every non-Builder agent. See `.opencode/permissions.md` for the full snapshot.

## 1a. Models — hard rules (read before ANY launch)

Model selection is the single most failure-prone decision in this stack. These
are hard invariants, not suggestions:

- **`--model opus` / `sonnet` / `haiku` (or omitting `--model`) will HARD-FAIL.**
  The `claude` wrapper enforces strict model validation and aborts on implicit
  or default Anthropic model names. There is no silent fallback.
- **Every launch (`crosslink kickoff run`, `swarm launch`, sentinel) must pass
  an explicit, verified model ID.**
- **You CAN and MUST verify the model catalog yourself.** `opencode models` is
  an allowed command in your sandbox. Run `opencode models opencode` (Zen free)
  and `opencode models opencode-go` (paid Go) to confirm a model ID exists
  before you launch or accept one from the operator. If the operator proposes
  a model, check it against the live list — do not take it on faith. See
  `.crosslink/knowledge/model-discipline.md` for the full rules.
- **Free Zen models are rate-limited and their limits are opaque.** They can
  be exhausted for hours at a time with no way to predict when they recover.
  A launch with a free Zen model may hang, loop, or fail mid-task. Prefer paid
  Go models (`opencode-go/*`) for agent work — they are production-grade.
  If you must use a free model, verify it launches and completes promptly, and
  be ready to fall back to a paid Go model on any rate-limit symptom.
- If a doc or agent definition names a model that `opencode models <provider>`
  does not list, that doc is stale (§5) — the live catalog is authoritative.

## 2. The stack

- Crosslink fork specifics (guard plugins, per-agent-type overrides,
  `CROSSLINK_AGENT_TYPE`, known issues): `.crosslink/knowledge/crosslink-fork.md`.
- Knowledge pages: `crosslink knowledge list` /
  `.crosslink/.knowledge-cache/` for task-specific reference.

## 3. Crosslink workflow & tooling

- Tracking is mandatory: create/claim an issue before any write
  (`crosslink quick "..." -p <pri> -l <label>` or `crosslink session work <id>`).
  Commits are gated on an active issue.
- Command forms are exact: `crosslink issue comment` / `crosslink issue intervene`
  (not `crosslink comment` / `crosslink intervene`).
- `.opencode/opencode.json` — which agents + plugins this repo loads
  (`crosslink-guard`, `rtk-guard`; see `.opencode/design/` for plugin design).
- `.crosslink/rules/*.md` — project + tracking-mode rules (auto-injected).

## 4. Situational reads (only if your task matches)

| If your task is... | Read |
|---|---|
| Launching or orchestrating agents (kickoff OR swarm) | **`agent-orchestration-playbook.md`** (knowledge) — the shared playbook covering both tiers + when each applies. Contains task-matched timeout guidance (§5.3), the mandatory checkpoint-comment progress contract (§5.4), the two-repo sync rule (§5.5), and reviewer-independence via isolated sub-issues (§5.6). Workflow-topology dispatch mechanics (position store, staleness trigger, pre-positioned AUDITOR, review-before-consume) are in §5.8 |
| Understanding the workflow-topology design (principles + reasoning record) | `docs/research/Workflow Topology Design and Reasoning Record.md` — the canonical design record; operationalized in `AGENTS.md` (principles) and `docs/ORCHESTRATOR.md` (procedure) |
| Multi-agent / swarm specifically | `crosslink-subagent-orchestration.md` (knowledge, CLI reference) + `docs/ORCHESTRATOR.md` |
| Adversarial review | `crosslink-adversarial-review.md` (knowledge) + `docs/crosslink-adversarial-review.md` |
| Launching a background agent | the in-repo `kickoff` skill (`.claude/skills/kickoff/SKILL.md`) |
| Long-running processes / OOM risk | `server-memory-management.md` (knowledge) |

## 4a. Timeouts and progress feedback (read before ANY launch)

- **Timeout is task-matched, never a blanket 1h.** Ceilings: trivial `<=10m`,
  doc/simple/review `15-20m`, port/multi-file `30m`, complex multi-phase
  `45m+` (use swarm, not kickoff). Rationale and evidence: §5.3 of
  `agent-orchestration-playbook.md` (#120's 4-file fix took ~3 min on a 40m
  timeout; timeout length is the primary problem).
- **Agents MUST post milestone checkpoint comments** (`crosslink issue comment
  <id> "[PROGRESS] state=... completed=... next=... blocker=..." --kind
  observation`) and **sync after posting** — that is the durable
  operator-facing progress channel. Session-action breadcrumbs are
  supplementary telemetry only. Cadence derives from the ~5-minute
  loss-tolerance budget (§5.4): builders commit incrementally every ~5 minutes
  of work; read-only roles treat comment+sync as their commit at ~5-minute
  cadence. The ~4 cap is not a durability throttle. See §5.4 of the playbook
  and the KICKOFF template's `Progress Check-Ins` section.
- **Stalled-agent signals:** timeout exceeded = likely stalled; no new commit
  (builder) / no new synced position (read-only) for >2x the ~5-minute budget
  = likely stalled. Do not wait blind until timeout.

## 5. The invariant (overrides everything)

If a documented command fails, or a doc contradicts the live CLI, the doc is
stale — **report it and continue via the verified command**. The live
`crosslink <subcommand>` surface is authoritative. Do not fight stale docs.

---

## Future state note (repo consolidation)

The sibling `Tools` repository (tooling catalog, guard plugins, agent
definitions, skills) is planned to consolidate into this repository. The
routing above is written to work either way. If a pointer here doesn't
resolve, check both this repo and the sibling `Tools/` repo, then search by
filename.
