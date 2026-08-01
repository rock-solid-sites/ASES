# SESSION-START — read this first (every session)

This is the routing entry point. Its only job is to point you at the right
information. Read it once, then follow the pointers. If a pointer doesn't
resolve, see §5 — the doc is stale, not you.

---

## 1. What this repo is

- `ORIENTATION.md` — the three layers (EDASES research / ASES methodology /
  Execution Engine). Everything maps to one of these. Read fully.
- `AGENTS.md` — the canonical operational rules governing every session
  (crosslink tracking mandatory, reasoning-before-artefacts, evidence vs
  inference, model discipline). Read fully.
- `ARCHITECTURE.md` + `README.md` — repo layout and project overview.
- `docs/ORCHESTRATOR.md` — orchestrator contract (plan/delegate/gate; never
  implement). Read if you are in the orchestrator role.

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
| Launching or orchestrating agents (kickoff OR swarm) | **`agent-orchestration-playbook.md`** (knowledge) — the shared playbook covering both tiers + when each applies |
| Multi-agent / swarm specifically | `crosslink-subagent-orchestration.md` (knowledge, CLI reference) + `docs/ORCHESTRATOR.md` |
| Adversarial review | `crosslink-adversarial-review.md` (knowledge) + `docs/crosslink-adversarial-review.md` |
| Launching a background agent | the in-repo `kickoff` skill (`.claude/skills/kickoff/SKILL.md`) |
| Long-running processes / OOM risk | `server-memory-management.md` (knowledge) |

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
