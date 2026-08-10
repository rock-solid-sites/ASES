---
title: "Read-Only Boundary Work as Active Methodology — Interaction with Open EDASES Research Areas"
program: EDASES
layer: Research
document_type: Research Finding
status: Active
authority: Experimental
canonical_repository: edases

depends_on:
  - Documentation Standard
  - EDASES-topic-microVMs.md
  - EDASES-topic-Containers-and-Environment.md

related_documents:
  - agent-tooling-and-permission-enforcement.md
  - agent-tooling-and-permission-enforcement-reviewed.md
  - read-only-role-crosslink-allowlist.md
  - Workflow Topology Design and Reasoning Record.md

consumed_by:
  - Execution engine research programme
  - ASES methodology development
  - Read-only permission-boundary follow-on work

implements: []

supersedes: []

superseded_by: []

last_updated: 2026-08-10
---

# Read-Only Boundary Work as Active Methodology

> **Purpose.** This document is a research-layer finding on the relationship
> between the read-only permission-boundary work
> (#314/#320/#326/#330/#331/#334/#340/#342/#344) and the open EDASES research
> areas recorded in the topic retrospectives `EDASES-topic-microVMs.md` and
> `EDASES-topic-Containers-and-Environment.md`. It argues that the technical
> fix for the read-only roles is not merely a tools-side repair: the process
> it defines produces research-relevant observations that feed directly into
> the research layer's open execution-context questions, and into what the
> future Execution layer — a not-yet-existing project layer whose concrete
> shape is undetermined — will eventually need to enforce. The technical work
> is therefore a **methodology-feedback loop**.
>
> **Status.** This is a research finding with authority **Experimental**: it
> records observations from active tools-side work and a provisional
> interpretation of those observations against the research abstraction. It
> does not redefine any research concept and does not propose methodology.
> It is offered as input to the open questions in the topic retrospectives.
>
> **Sources.** Primary sources are the Crosslink issues listed in the metadata
> and the two topic retrospectives plus the documentation standard. Issue
> numbers refer to the Crosslink issue tracker. Where a claim is a
> source-verified fact it is stated as such; where it is an interpretation it
> is explicitly marked. What was explicitly **not** tested is collected in
> section 8.

---

## 1. The Finding in One Paragraph

The EDASES research layer abstracts the execution of engineering work as
`Agent → Execution Request → Execution Harness → Evidence`, and asks what
isolation guarantees an execution harness must provide. The read-only
permission-boundary work is **tools-side evidence about that abstraction's
isolation requirement** for the reviewer and auditor roles: in today's stack
the agent process is *not* an execution harness — no Execution layer exists
yet — and isolation is enforced by permission blocks and guard plugins inside
the agent process, not by a substrate between agent and repository. The topic
retrospectives' open questions do not cover this case — they ask about
containers, microVMs and Nix, not about the four-role permission model, the
`--pure` bypass, guard plugins or crosslink allowlists. If the technical fix
chain (deny-by-default capability boundary #342/#344, durability process #330,
verified fail-closed sync guard #336/#337) successfully defines a workable
process that addresses the reviewers' concerns **and** produces observations
that feed back to the research layer, then that fix is methodology-relevant,
not merely tooling. This document records how, and what the feedback data
points are.

---

## 2. The Permission-Boundary Work: What Was Done

The read-only permission-boundary work is a chain of connected tasks,
recorded as Crosslink issues. Each step both documents and sharpens the
read-only role design.

| Issue | What it established |
|---|---|
| **#314** | Current-state write-up of the agent tooling / permission-enforcement system for external review (`agent-tooling-and-permission-enforcement.md`). Documents the four-role permission model, the three guard plugins, the enforcement layers, and the identified problem areas. |
| **#320** | Full-context reviewed document merging the original claims with 8 adversarial reviews (`agent-tooling-and-permission-enforcement-reviewed.md`). Establishes that reviewer and auditor are read-only **by construction** as a design goal. |
| **#326** | Cross-reviewer synthesis tabulating the 8 reviews. The reviewers unanimously flagged that the advertised read-only property was overstated by the broad grants (`opencode *`, `git *`, `cargo *`, `npm *`) and recommended a deny-by-default least-privilege capability boundary for read-only roles. |
| **#330** | Process finding: checkpointing is durability, not reporting. Cadence derives from a ~5-minute loss-tolerance budget; the commit stream (builders) and the comment+sync position stream (read-only roles) are ground truth. Establishes the durability primitive the read-only roles depend on. |
| **#331** | Review (hy3) of the updated checkpoint process against the playbook — produced MUST-FIXes that drove the durability amendments. |
| **#334** | Review (hy3, follow-up) comparing the tripn-astro `read-only-role-crosslink-allowlist` finding against the #330 process change — produced MUST-FIXes for the ASES agent definitions. |
| **#340** | Amendment of the ASES agent definitions per #334: reviewer sync grant, knowledge-write scoping (knowledge delete removed), narrow crosslink allowlist mirroring tripn-astro Option B. Committed `21cfb6d8`/`d0e42659`. |
| **#342** | The deny-by-default capability boundary **proposal** (read-only investigation, no config change): exact per-grant keep/narrow/remove allowlists, the bypass matrix, the `--pure` mechanism verified at source, tradeoffs, and a verification plan. |
| **#344** | Implementation of #342 (in flight at the time of writing): narrow the read-only role grants to the approved band-aid. |

Two supporting verification tasks are part of the same work because they
underwrite the durability premise:

| Issue | What it established |
|---|---|
| **#336** | Static verification of the `ade6146b` fail-closed sync guard on deployed binaries: **PASS** — guard present in source and in the deployed binary (`0.9.0-beta.1+a87bd513`). |
| **#337** | Level-2 isolated behavioral test of the guard in a scratch environment: **DEMONSTRATED-FAIL-CLOSED** — a local-only comment survives a sync refused on a stale-hub checkpoint. |

The central technical finding of #342, verified at source, is the two-layer
enforcement model:

1. **Layer 1 — the agent permission block** (`.opencode/agents/{reviewer,auditor}.md`):
   deny-by-default (`"*": deny` plus prefix allows). **This is the load-bearing
   read-only boundary.**
2. **Layer 2 — the crosslink-guard plugin** (`.crosslink/hook-config.json`):
   per-type git blocklists, `allowed_bash_prefixes` pass-throughs, and an
   active-issue gate. **This layer is not a deny-by-default bash boundary** in
   the agent context — relaxed mode allows any non-blocked command.

And the `--pure` bypass mechanism, also verified at source
(`fork/opencode-src/packages/opencode/src/plugin/index.ts:179`):
`const plugins = flags.pure ? [] : (cfg.plugin_origins ?? [])`. The three
guard plugins load from `plugin_origins`, so `opencode run --pure` empties
all three; `internalPlugins()` is a separate auth-only set that contains none
of the guards. A read-only role granted `opencode *` could therefore spawn a
guardless `--agent builder` session in one command — the read-only boundary
evaporates.

---

## 3. The Research Abstraction: Agent → Execution Harness → Evidence

The topic retrospectives establish the conceptual relationship the read-only
work operationalizes.

`EDASES-topic-microVMs.md` (section 3) records the preferred conceptual model:

```text
Agent
    │
    ▼
Execution Request
    │
    ▼
Execution Harness
    │
    ├── Local process
    ├── Container
    ├── MicroVM
    └── Remote executor
    │
    ▼
Evidence
```

The microVM is not the agent's identity or cognitive environment; it is the
agent's **execution harness**. The strongest architectural abstraction to
emerge from the discussion is not "microVM" but **execution context**
(section 19.4): an isolated, controlled environment in which engineering
actions can be performed and from which evidence can be collected, where a
microVM is one possible implementation.

`EDASES-topic-Containers-and-Environment.md` (section 3) reaches the parallel
conclusion that containers are execution **substrates**, not architectural
concepts; the methodology should specify required properties of an execution
environment rather than prescribing a runtime.

The research questions these documents leave open are:

- `EDASES-topic-microVMs.md` §20: what isolation guarantees ASES actually
  requires; whether isolation is required at all execution boundaries or only
  for particular classes of activity; what "reproducible execution" means
  operationally; how much environment state must be captured; whether
  environments should be persistent or ephemeral; whether snapshot/resume is
  methodological or convenience; whether containers suffice; when microVM
  isolation justifies its complexity; whether Nix's reproducibility model is
  materially better than pinned images; whether one architecture can support
  multiple backends; what evidence should be associated with an execution
  context; whether environment specifications should be versioned objects.
- `EDASES-topic-Containers-and-Environment.md` §14: what exactly an
  Engineering Environment is; whether Nix is the appropriate implementation;
  how environment identity should work; how environment requirements should be
  expressed; how much persistence is appropriate; how security levels should
  map to execution substrates.

Note that the microVMs abstraction explicitly includes **Local process** as
one of the four execution-harness options. The research does not examine what
isolation guarantees a Local-process harness can provide; its attention is on
the stronger substrates (container, microVM, Nix).

---

## 4. How the Tools-Side Boundary Work Informs the Open Research Areas

The read-only permission-boundary work is **tools-side evidence** that
informs the research-layer execution-context abstraction. It is **not** a
realization of that abstraction, and it is **not** the future Execution
layer. The current stack (opencode fork, crosslink fork, guard plugins,
claude wrapper, rtk, agent definitions, permission blocks) is Tools-side: a
general warehouse for forks, plugins, wrappers and hacky constructions. The
Execution layer is a **future, not-yet-existing project layer** that will
enforce ASES methodology; its concrete shape (possibly a state-machine-based
agent harness, possibly something else) is **undetermined**. We are
developing methodology as we go, and this document must not close options
prematurely.

The correspondence between the research abstraction and the current stack is
therefore not a realization mapping. The table below records, for each
research abstraction, the **tools-side observation** the current work
produces — an observation the undetermined Execution-layer design should
account for:

| Research abstraction (topic docs) | Tools-side observation (current stack) |
|---|---|
| Agent (role with a reasoning capability) | Four-role permission model: orchestrator / builder / reviewer / auditor (`.opencode/agents/*.md`) |
| Execution Request | Dispatch via `crosslink kickoff` / swarm with a chosen agent type |
| Execution Harness | **Absent.** The current stack has no Execution layer and no harness construct; the agent process is not a harness. The boundary is a permission block (Layer 1) plus guard plugins (Layer 2) inside the agent process. This absence is itself an observation: it shows what the future Execution layer must supply. |
| Isolation | The deny-by-default permission boundary: `edit: deny`, `task: deny`, narrow `bash` allowlists for reviewer/auditor — observed inside the agent process, not between agent and repository |
| Evidence | Durable positions: `crosslink issue comment` + `crosslink sync` — the read-only roles' commit primitive (#330) |

The research asks what isolation guarantees ASES requires and abstracts
`Agent → Execution Harness → Evidence`. The permission-boundary work does not
instantiate that abstraction; it observes what happens when the abstraction
is **unimplemented** — when the boundary must sit *inside* the agent process
because there is no harness and no substrate. The read-only guarantee is a
property of the permission block, not of any external boundary.

This matters for the research because the tools-side observations are real
and feed the Execution-layer requirements: the observed failure modes (the
broad grants of #314–#326, the `--pure` escape of #342, the durability gaps
of #330/#340) and observed requirements (the deny-by-default consensus of the
8-reviewer wave, the narrow allowlists of #334/#340, the fail-closed sync
guard of #336/#337) are evidence that the future Execution layer's design
should account for — not a premature realization of that layer.

---

## 5. The Gap: What the Research Questions Do Not Address

The permission gaps are **not** addressed by the current research questions.
This is a precise claim, and it needs to be stated precisely.

The topic retrospectives' open questions concern **execution-substrate
isolation**: whether containers/microVMs/Nix provide sufficient isolation and
reproducibility, how environments should be specified and identified, how much
state to capture, which substrate to pick. They do not address:

- the four-role permission model and its per-role capability grants;
- the `--pure` bypass — a flag that disables the enforcement plugins;
- guard plugins and their enforcement semantics (two-layer model of §2);
- crosslink allowlists as the durable-position surface for read-only roles;
- deny-by-default versus allow-by-default permission semantics inside the
  agent process;
- how read-only is enforced when there is no execution harness — when the
  boundary is only a permission block inside the agent process, with no
  substrate between agent and repository.

The last point is the sharpest form of the gap. The research abstraction
`Agent → Execution Harness → Evidence` lists **Local process** as a harness
option (microVMs §3), but every open question about isolation is posed at the
substrate level. The abstraction does not yet specify:

> **How is read-only enforced when no Execution layer exists — when there is
> no container, no microVM, no Nix sandbox between the agent and the
> repository, and the only boundary is inside the agent process?**

That is the case the current tools stack lives in. The research leaves it
open, and the tools-side work discovered it is non-trivial: a permission block
is not automatically an isolation boundary, because (a) the block's own grants
can be too wide (`opencode *` re-admits session-spawning), (b) the enforcement
plugins can be disabled by a flag (`--pure`), and (c) the durability surface
can be incomplete (no `sync` → positions stay local). Each of these was found
by the tools-side work, not by the research questions.

This is a **tools-side gap the research leaves open** — not a
contradiction of the research, and not a failure of it. The research
abstraction was built to discuss substrates; the tools-side observations are
the part of the design space the abstraction has not yet covered, and they
are inputs the future Execution layer's design should account for.

---

## 6. How Solving This Becomes Active Methodology: The Feedback Loop

The key thesis: if the technical fix successfully defines a **workable
process** — one that (a) addresses the reviewers' concerns and (b) produces
observations that feed back to the research layer — then the fix is
methodology-relevant, not just tooling. Observations from Tools-side work
feed the research questions, and the future Execution layer — whose concrete
shape is undetermined — will eventually enforce the methodology these
observations inform. The mechanism is a feedback loop:

```text
Tools-side problem (read-only roles not actually read-only)
    ↓
Technical fix chain (#342 band-aid + #330 durability process
                      + #336/#337 verified sync guard)
    ↓
Workable process (deny-by-default read-only, durable positions,
                  verified fail-closed primitives)
    ↓
Observations about execution-context requirements
    ↓
Feed back to open EDASES research questions (microVMs §20, Containers §14)
    ↓
Inform the future Execution layer (shape undetermined)
```

The direction of the loop is legitimate under the project's abstraction
rules: research should not depend on implementation, but tools-side
**observations** are evidence and may inform research (AGENTS.md, Evidence
and Reasoning Certainty principles). The observations below are offered as
evidence for the open questions — not as methodology, not as redefinitions
of the research abstraction, and not as a premature realization of the
Execution layer.

### 6.1 Feedback data point 1 — per-role-class isolation requirements

The boundary work produced an empirical answer to microVMs §20.1 ("What
isolation guarantees does ASES actually require?"): **the guarantees are
role-class-dependent, not uniform**.

- **Reviewer and auditor** need read-only evidence access — `git diff`,
  `git log`, `git show`, `git status` for evidence verification (confirmed in
  the tripn-astro allowlist finding and preserved in the #342 proposal's
  narrowed git allowlist). They do **not** need code execution
  (`cargo`/`npm` removed), session spawning (`opencode *` removed), or
  issue-lifecycle powers (never granted).
- **Builder** needs full write access to the repository — implementation work
  requires it.
- **Neither read-only role should spawn sessions** — the `--pure` escape
  exists precisely because a read-only role with `opencode *` could spawn a
  guardless builder session. The requirement is negative: a read-only role's
  execution context must not be able to mint new execution contexts.

This is a concrete, observed, role-class-scoped isolation requirement — the
kind of input the research asks for but did not have.

### 6.2 Feedback data point 2 — evidence and traceability of durable positions

The #330 durability process and the #340/#334 allowlist work established that
**comment+sync is the commit** for read-only roles: the durable position
stream on the Crosslink hub is the read-only roles' only write surface, and
the sync guard (#336/#337) is the verified primitive that makes it safe
(fail-closed: a stale-hub checkpoint refuses to drop local comments).

This is a direct empirical input to microVMs §20.11 ("What evidence should be
associated with an execution context?"): in the current tools stack, the
evidence channel is the **position stream** — structured, durable, ordered,
traceable to its producer. The read-only roles' evidence *is* their positions,
and the traceability requirement is what motivated the sync grant and the
fail-closed guard.

### 6.3 Feedback data point 3 — the execution-context properties the work implies

The `--pure` finding implies a property the research abstraction has not yet
stated:

> **An execution context's isolation guarantee must be a property of the
> context itself, not of a permission block that a flag can disable.**

The #342 proposal's verdict — remove `opencode *` from read-only roles — is
a tools-side choice, but the requirement it encodes is research-relevant:
when no Execution layer exists and the boundary must sit inside the agent
process, that boundary must be a **real boundary**, not a permission block.
A flag that empties the enforcement layer (`--pure`) demonstrates that a
permission-block-only boundary is not a boundary at all. This is precisely
the "required guarantees, not prescribed technology" framing of the topic
docs (microVMs §16): the methodology should say "the execution context must
not be escapable by a harness flag", and leave the future Execution layer —
whose shape is undetermined — to decide how.

### 6.4 Why this makes the fix methodology-relevant

The distinction the operator's framing draws is: a fix that merely changes
config is tooling. A fix that changes config **and** produces observations
feeding the research's open questions is both — the config change is the
tools-side part, and the process it defines (threat model stated,
deny-by-default, durable positions, verified primitives) is the
methodology-relevant side. The same work product carries both, and the
observations are what the future Execution layer's design should account
for.

---

## 7. What a Workable Process Must Demonstrate to Count as Methodology

For the technical fix to count as methodology (not just tooling), the
process it defines must demonstrate three things. These are stated as
acceptance criteria for the ongoing work:

1. **The reviewers' concerns are addressed.** The threat model is stated
   (what each grant enables today — the #342 bypass matrix), the boundary is
   deny-by-default (the permission block becomes the load-bearing boundary
   that cannot be re-expanded by a flag), and identity is fail-closed (an
   unresolved or ambiguous state refuses rather than falls open — the
   #336/#337 sync-guard behavior, generalized).

2. **The durability primitive is verified, not assumed.** The sync guard is
   demonstrated working (source presence #336 + isolated behavioral test
   #337: comment survives a refused sync), and the position stream is the
   ground truth for read-only roles at the ~5-minute durability cadence
   (#330).

3. **Observations are fed back to EDASES.** The role-class isolation
   requirements (§6.1), the durable-position evidence channel (§6.2), and the
   real-boundary requirement (§6.3) are recorded as research inputs —
   this document is one such record — and the open execution-context
   questions are updated or answered with them.

If all three hold, the read-only boundary work is active methodology: a
live, evidence-producing **tools-side** source whose observations inform the
execution-context abstraction and the future Execution layer's design. If
any fails, the work remains a tools-side repair with an unfulfilled feedback
promise.

---

## 8. What Was Not Tested / What Remains Open

Consistent with the project's negative-space disclosure discipline:

- **#344 was in flight** at the time of writing; the deny-by-default boundary
  had been proposed and approved but not yet verified at runtime. The §7
  criteria 1–2 are therefore expectations, not observations, for the
  post-#344 state.
- **The `--pure` escape was source-verified, not empirically executed.**
  The claim rests on the fork's plugin loader (`plugin/index.ts:179`) and the
  config resolution mapping the `plugin` array to `plugin_origins`; it was
  not demonstrated by running `opencode run --pure` in a live read-only
  session.
- **The research-layer side of the feedback loop is not yet closed.** This
  document records observations; the topic retrospectives have not yet been
  updated with them, and no research question has yet been answered from
  them. The feedback loop's research half is proposed, not observed.
- **Whether the boundary survives the next agent-runtime change is untested.**
  The `--pure` finding suggests that any future flag, plugin-loading change, or
  permission-matcher change can re-open the boundary; no regression
  discipline for the boundary itself was established beyond the #342
  verification plan.
- **The substrate question remains open.** Even a fully working in-process
  boundary is not a container/microVM boundary; the research questions about
  substrates (when is a stronger substrate worth its complexity) are
  untouched by this work.

---

## 9. Conclusion

The read-only permission-boundary work is a **methodology-feedback loop**. The
fix is tools-side — permission blocks, guard-plugin semantics, allowlists, a
sync guard. But the process it defines produces research-relevant observations
that feed the open execution-context questions of the microVMs and Containers
retrospectives: isolation requirements are role-class-scoped; the durable
position stream is the read-only roles' evidence channel; and an execution
context whose boundary can be disabled by a flag is not a boundary. The
technical work therefore does not merely repair the read-only guarantee — it
begins to answer what the research abstraction left open: how read-only is
enforced when no Execution layer exists and the boundary must sit inside the
agent process.

The workable process counts as methodology when the reviewers' concerns are
addressed (threat model stated, deny-by-default, fail-closed identity), the
durability primitive is verified (sync guard demonstrated), and the
observations feed back to EDASES. The first two are the tools-side part of
the loop; the third is the research side. The future Execution layer — whose
concrete shape (possibly a state-machine-based agent harness, possibly
something else) is undetermined — will eventually enforce the methodology
these observations inform. This document is a first step on the third.
