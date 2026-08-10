---
title: Read-Only Role Crosslink Allowlist — Repository Role-Permission Change (2026-08-09)
programme: EDASES
layer: Research
document_type: Research Record
status: Active
authority: Finding
canonical_repository: edases

depends_on:
  * Documentation Standard

consumed_by:
  * Future agent sessions
  * Orchestrator workflow reviews
  * .opencode/permissions.md maintainers

related_documents:
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/research/agent-tooling-and-permission-enforcement.md
  - docs/research/agent-tooling-and-permission-enforcement-reviewed.md
  - docs/ORCHESTRATOR.md

supersedes: []

last_updated: 2026-08-10
---

# Read-Only Role Crosslink Allowlist — Repository Role-Permission Change (2026-08-09)

> **Purpose.** This record documents a permission change made 2026-08-09 in the
> tripn-astro monorepo: a narrow Crosslink bash allowlist was added to the
> reviewer and auditor agent definitions, changing their `bash: deny` to a
> scoped allowlist. The change fixes a harness defect in which read-only roles
> could not post their own positions or verdicts, forcing every verdict through
> an orchestrator relay and making agent drops expensive. This record captures
> the problem with session evidence, the exact change, the rationale, the
> option tradeoff that produced it, the atomization lesson, and the workflow
> impact.
>
> **Sources.** Primary sources: tripn-astro issue #440 (harness-defect writeup),
> issue #445 (implementation issue), commit `79b35eac` (merged `8612f766`),
> the Crosslink knowledge page `read-only-role-crosslink-access`, and the live
> agent definitions `.opencode/agents/reviewer.md` and `.opencode/agents/auditor.md`.
> The workflow-topology vocabulary (position-emitting agents, durable store,
> flag-only AUDITOR) is from the Workflow Topology Design and Reasoning Record.

---

## 1. The Problem

### 1.1 The harness gap: read-only agents had no way to persist their output

The tripn-astro orchestration workflow splits authority by role: builders
write project files; reviewer and auditor are **read-only, flag-only** roles
that verify and judge. The role separation is enforced structurally in the
agent definitions (`.opencode/agents/*.md`) — `edit: deny`, `task: deny`, and
until 2026-08-09, `bash: deny`.

The design intent was airtight: a read-only agent that is physically unable
to write files is read-only. But it had a blind spot. The only durable store
in the workflow is the **Crosslink hub** — positions and verdicts live as
comments on issues, and the hub is the store positions must survive in after
the producer is gone (Workflow Topology §5.1). Yet the two read-only roles
had **no Crosslink access at all**:

- no `crosslink issue comment` (cannot post a verdict or position),
- no `crosslink issue show` (cannot read the issue they were dispatched on),
- no `crosslink knowledge search/list/add/edit/delete` (cannot read or write
  knowledge pages),
- no `crosslink session status` and, for the auditor, no `crosslink sync`
  (cannot maintain live issue-stream state).

A read-only role could therefore **produce** a verdict only in its final
message — the one artifact that is not durable. Everything durable required
the orchestrator.

### 1.2 Dropped work: observed three times on 2026-08-09

The defect was observed repeatedly in a single day's audit runs (PSI
#438/#439 audits; reported in detail in issue #440):

- **`9Lg8-3eZm`** (Phase 1 auditor) — parked at the shell prompt without
  writing `DONE`; the orchestrator could not even relay its verdict because
  the agent parked before the evidence arrived.
- **`9Lg8-R3da`** (continuation auditor) — parked pre-verdict; every verdict
  accepted the config array and one-file diff **on relay**, unverifiable
  in-sandbox because the continuation worktree branched from a base commit
  that predated the commit under audit and the auditor had no git.
- **`9Lg8-dLdE`** (continuation auditor) — verdict relayed by orchestrator.
- **`9Lg8-GpBh`** (continuation auditor) — mitigated with a verdict-first
  protocol (verdict as the first message, from relayed evidence alone, before
  verification), which delivered a complete APPROVE-WITH-PRECONDITIONS but was
  a workaround, not a fix.

In every case the agent had no bash and no Crosslink; it could not write
`.kickoff-status`, could not post to the issue, and could not even read the
issue. Verdicts existed only in the agent's final message, and a mid-task drop
lost all in-context work — context died with the agent. The agent that parked
at the shell prompt without posting was indistinguishable from a dead one:
the staleness trigger never fired because read-only worktrees wrote no
heartbeat either.

### 1.3 The relay bottleneck

Because the read-only roles could not post, the orchestrator had to act as
the sole writer of their positions:

- **Manual, lossy, latency-bound**: every verdict traveled from agent →
  orchestrator → issue, and the orchestrator could mis-relay, delay, or lose
  it; `9Lg8-3eZm` demonstrated the loss case.
- **A single point of failure** for the entire review/audit leg of the
  workflow.
- **Auditing the relay, not the artifact**: with evidence delivered by relay,
  the pre-consumption-readiness gate the playbook wants was partially hollow —
  the auditor audited what the orchestrator chose to relay.

---

## 2. The Decision and Exact Change

### 2.1 Decision

Grant the reviewer and auditor a **narrow Crosslink bash allowlist** so they
can post positions, verdicts, and knowledge pages at composition time —
making the read-only roles' output durable at the moment it is produced,
instead of at the moment the orchestrator relays it. `edit: deny` and
`task: deny` are unchanged: the roles still cannot touch project files and
cannot spawn subagents.

### 2.2 Exact change

Implemented in commit `79b35eac` ("feat: narrow crosslink bash allowlist for
reviewer + auditor agents [#445]"), merged in `8612f766`. Files changed:
`.opencode/agents/reviewer.md`, `.opencode/agents/auditor.md`, and the
`.opencode/permissions.md` snapshot (two rows updated to match).

**Before** (both roles):

```yaml
permission:
  edit: deny
  bash: deny
  task: deny
```

**After** — reviewer (`.opencode/agents/reviewer.md`):

```yaml
permission:
  edit: deny
  bash:
    "*": "deny"
    "crosslink issue comment *": "allow"
    "crosslink issue show *": "allow"
    "crosslink session status *": "allow"
    "crosslink knowledge search *": "allow"
    "crosslink knowledge list *": "allow"
    "crosslink knowledge add *": "allow"
    "crosslink knowledge edit *": "allow"
    "crosslink knowledge delete *": "allow"
  task: deny
```

**After** — auditor (`.opencode/agents/auditor.md`): identical to reviewer,
plus one extra allow:

```yaml
    "crosslink sync": "allow"
```

The auditor gets `crosslink sync` because the auditor acts as a continuous
monitor and needs the live issue-stream state; the reviewer does not.

**Explicitly excluded** (both roles — verified absent from the final
frontmatter):

- `crosslink quick` (issue creation),
- `crosslink issue close`,
- `crosslink issue create`,
- `crosslink kickoff` / `crosslink swarm` (agent dispatch),
- `crosslink session work` (claiming/starting work),
- `crosslink issue intervene`,
- `crosslink issue review`.

The syntax mirrors the orchestrator agent's existing bash allowlist
(`.opencode/agents/orchestrator.md`, which has `"crosslink *": "allow"`), but
scoped far narrower. Verification at implementation time: both frontmatters
parse as valid YAML (checked with pyyaml; opencode 1.18.13 has no
`agents parse` subcommand), auditor has `sync` / reviewer does not, excluded
commands are absent, orchestrator file untouched.

---

## 3. The Rationale: Why Crosslink Commands Do Not Violate Read-Only

### 3.1 "Read-only" is about repository immutability, not tool denial

The reviewed permission-enforcement analysis (agent-tooling-and-permission-
enforcement-reviewed.md) distinguishes two senses of "read-only":

- **(A) Tool denial** — the role has no write-capable tools at all.
- **(B) Repository immutability** — the role cannot modify the project's
  files or state.

The workflow's operational meaning of read-only for reviewer/auditor is (B):
their output is flag-only — they verify, judge, and flag, but they must not
change the codebase, close or create issues, claim work, or dispatch agents.
What they **must** be able to do is emit their position into the durable
store.

Crosslink commands write to the **issue database and knowledge pages** — the
workflow's durable store — not to project files. `crosslink issue comment`
appends a comment to an issue record; `crosslink knowledge add/edit/delete`
maintains knowledge pages; `crosslink session status` and `crosslink sync`
read/refresh issue-stream state. None of these touches the repository tree.
Allowing them therefore does not violate the repository-immutability
semantics that the read-only role exists to enforce.

### 3.2 Positions must be durable at composition time

The workflow topology requires every agent to emit structured positions to a
durable store, and the store must be one where positions survive the
producer's death (Workflow Topology §5.1). A role that cannot write to the
store cannot emit positions that survive it. The pre-change state made the
read-only roles the only agents in the workflow whose positions were not
durable at composition time — they depended on a second agent (the
orchestrator) to persist their output. The allowlist closes exactly that gap:
the producer writes its own position into the store, in its own words, at the
moment it is composed.

### 3.3 Agent drops become cheap

With self-posting positions, the harm of a mid-task drop is bounded. A drop
loses the agent's remaining in-context work, but it no longer loses the
positions and verdicts already emitted — those are in the store. The next
agent (or a retry) can continue from the last durable position. This is the
difference between a costly, evidence-destroying failure and a cheap,
state-preserving one.

---

## 4. Option A vs Option B: The Tradeoff

The fix was the subject of an explicit two-option discussion (issue #445 is
titled "fix #440 candidate A, option B"; candidate A in #440 proposed the
narrow crosslink-write allowlist, and the discussion narrowed the scope):

| | **Option A — full `crosslink *`** | **Option B — narrow allowlist (chosen)** |
|---|---|---|
| Grant | `"crosslink *": "allow"` for reviewer + auditor | Explicit per-command allows: issue comment/show, session status, knowledge search/list/add/edit/delete (auditor + sync) |
| Semantics | Crosslink as a whole is treated as store-access, not repo access | Crosslink is treated as store-access **only for the store operations a read-only role legitimately performs**; everything else stays denied |
| Risk | Read-only roles could create/close/claim issues (`quick`, `issue close`, `issue create`, `session work`) and dispatch agents (`kickoff`, `swarm`), silently eroding the flag-only boundary | Boundary preserved structurally — the denied commands stay structurally impossible |
| Audit story | Enforcement rests on the prompt saying "don't" | Enforcement rests on the tooling saying "can't" |
| Failure mode | A confused or prompt-violating read-only agent could mutate issue state or spawn work | A confused agent can post a comment at worst — which is its legitimate job |

**Why B won.** The whole point of the read-only roles is that their
boundaries are **structural**, not aspirational — a role told "you are
read-only" but physically able to write is not read-only (the same principle
that motivated `edit: deny` in the first place). Option A moved the critical
boundary (do not create/close/claim issues, do not dispatch) back into prose,
undoing the structural guarantee for those operations. Option B keeps the
flag-only semantics in the permission block: the agent can post positions and
maintain knowledge — its legitimate output channel — but cannot change issue
lifecycle state or dispatch agents. The narrow allowlist preserves the
structural enforcement of the boundary while fixing the durability gap.

---

## 5. The Atomization Lesson

The incident teaches a general lesson about read-only agents:

> **For a read-only agent, the only durable output is what it can post
> itself.**

Read-only roles cannot write files, so a file artifact is not a durable
output channel for them. Their positions, verdicts, and findings are durable
only if (a) they can write them to the store directly, and (b) each position
is scoped so that losing the rest of the agent's context costs nothing.

The two mechanisms that make drops cheap, applied together:

1. **Self-posting positions** — the agent writes its own verdict/position to
   the issue as it composes it (the allowlist makes this possible). No relay
   step, no second agent in the write path.
2. **Dispatch-level splitting** — split multi-concern audits into one concern
   per agent at dispatch time (standing protocol from #440). Each agent then
   owns a small position set; if it drops, the work already posted survives
   and only the small remainder is redone.

Contrast with the pre-change failure: the verdict existed only in the final
message, so the entire audit was lost with the agent, and splitting could not
help because no split portion could be persisted without a relay. The
combination — split the work so each piece is small, and let each piece post
its own result — is what converts a drop from a session-failure into a
retry.

---

## 6. The Workflow Impact

### 6.1 The orchestrator relays evidence, not verdicts

Before the change, the orchestrator was the sole writer of read-only roles'
positions: every verdict and every finding traveled through it, and a verdict
lost in the agent's dying context was unrecoverable. After the change, the
orchestrator relays **only command-level evidence** — things read-only roles
still cannot run, such as `git diff`, build output, or other shell-only
verification — not the verdicts and findings themselves. Verdicts and
positions are written by their authors directly into the store.

### 6.2 Read-only roles own their position stream

Reviewers and auditors now post their own incremental `[PROGRESS]` positions
to the issue, per the checkpoint contract, and auditors maintain live issue-
stream state via `crosslink sync`. The position stream for a review/audit leg
is durable from the moment of composition, survives producer drops, and is
auditable after the producer is gone — which is the property the workflow
topology's durable-store requirement always intended (§5.1).

### 6.3 Residual gaps (explicitly not addressed)

Issue #440 listed five candidate fixes (A–E); this change implements
candidate A only. Not addressed, and still open as optional future work:

- **B** — base continuation audits on the builder's branch so the diff under
  audit is in the sandbox (auditors still cannot run `git fetch`/`git show`);
- **C** — a kickoff prompt template for `--agent-type auditor` that strips
  builder steps 1–8 and inserts the verdict-first protocol;
- **D** — a heartbeat written by read-only worktrees so staleness triggers
  fire on parked agents;
- **E** — read-only git (`git show/log/fetch .` only) for branch-diff
  verification.

None of these blocks the allowlist change; each is independently shippable.

---

## 7. What Was Not Tested

- The allowlist was verified statically (valid YAML, exact allow set, excluded
  commands absent); it was not exercised by a live reviewer/auditor kickoff
  run at the time of this record.
- Whether the auditor's `crosslink sync` grant creates any unintended write
  surface beyond issue comments/knowledge pages is not separately tested.
- The residual gaps in §6.3 remain unimplemented and untested.

---

## 8. Follow-on Findings (2026-08-10)

The allowlist went live on 2026-08-09; the next day's production runs
surfaced three follow-on findings that sharpen the original record. They are
recorded in the same style as the sections above — evidence first, claims
scoped, untested assumptions stated.

### 8.1 Liveness / commit-cadence contract

The #453 wiring-pass stall proved the original problem (lost time) was not
fully solved by the allowlist alone. A builder ran 53 minutes on the #453
wiring pass, posted its plan, then died with **zero commits**. The allowlist
fixed durability of *emitted positions* (verdicts, findings, checkpoints —
the store-write surface of §3.2), but it did nothing for **in-progress work
that never became a position**: the 53 minutes of labor between the plan
comment and the death produced no durable artifact at all. Lost work, not
lost verdicts — a different failure class from the one §1.2 documented.

The resolution is a new process rule, recorded as the knowledge page
`agent-liveness-commit-cadence`:

- **Builder mandate**: commit at least once per 5 minutes of wall-clock time;
  per-file, per-site, and WIP commits with clear messages are acceptable.
- **Stall definition**: absence of a new commit for >10 minutes is treated by
  the auditor and orchestrator as a stall.
- **Auditor check**: every pre-positioned auditor prompt includes a liveness
  criterion — check the builder worktree `git log` periodically; if no new
  commit appears within ~10 minutes of the last, flag a stall to the
  orchestrator immediately (a divergence flag, not a verdict).
- **Orchestrator check**: worktree git state is the **primary** liveness
  signal. Kickoff status `RUNNING` only means the watchdog is alive, not the
  agent; pane output is ambiguous (a parked agent's pane can look working).

**Empirical proof — failed run vs successful re-run.** The same task/spec ran
twice. The failed run followed the old protocol: 53 minutes, 1 plan comment,
0 commits, agent died. The successful re-run followed the cadence mandate:
**3 commits in 15 minutes**. The commit stream is the discriminator — in the
window where the failed run produced nothing, the successful run produced
three durable, resumable artifacts.

### 8.2 Crosslink worktree-to-main sync gap

The §3.2 claim ("positions must be durable at composition time") and §6.2
("read-only roles own their position stream") need refinement: posts made
from agent worktrees did **not** propagate to the main issue store during
this session. The agent pane showed 8 comments on the issue; the main
repository's `crosslink issue show` showed 1. The orchestrator relayed the
remaining positions manually — reproducing the exact relay bottleneck §1.3
describes, for positions their authors had already written to their
worktree-local store.

The gap is mechanical — worktree-local Crosslink state is not automatically
synced to the hub view the main session hydrates from. It sharpens the
sync-for-auditor design decision: the auditor's `crosslink sync` grant (§2.2)
is only as good as the hub's view of worktree posts, and a position visible
in the worktree is not yet a position visible to the orchestrator. This is a
known gap for future work, noted here rather than fixed in this record.

### 8.3 Model reliability note

Free Zen models failed mid-task twice during the runs that produced these
findings (`laguna`, `nemotron`); paid Go models (`deepseek-v4-flash`,
`mimo-v2.5`) succeeded consistently. Model choice therefore interacts with
the drop-recovery story of §3.3: a drop on a free-Zen model is more likely to
be a mid-task failure whose recovery cost is a full re-run, while the paid-Go
runs completed with the commit-cadence contract intact. This is an empirical
note with a small sample, not a tested rule — the naming of models is
deliberate so future runs can confirm or falsify the split.
