---
title: Paseo Role Capability Matrix — Initial Compatibility and Enforcement Record
program: EDASES
layer: Research
document_type: Design Record
status: Draft
authority: Experimental
canonical_repository: edases

depends_on:
  - docs/research/agent-tooling-and-permission-enforcement-reviewed.md
  - docs/research/read-only-role-crosslink-allowlist.md
  - docs/research/regression-testing-orchestrator-compliance.md
  - docs/research/Workflow Topology Design and Reasoning Record.md
  - docs/research/EDASES Review Methodology.md
  - .opencode/permissions.md
  - .opencode/agents/orchestrator.md
  - .opencode/agents/builder.md
  - .opencode/agents/reviewer.md
  - .opencode/agents/auditor.md
  - .opencode/plugins/orchestrator-guard.ts
  - .opencode/plugins/crosslink-guard.ts

external_implementation_baseline:
  repository: https://github.com/getpaseo/paseo
  commit: 0d05584d044f5a72212d509ead7af0532dd105e2
  inspected: 2026-10-03

last_updated: 2026-10-03
---

# Paseo Role Capability Matrix — Initial Compatibility and Enforcement Record

> **Purpose.** Define a practical role-capability target for using Paseo as a
> better temporary execution harness than the previous OpenCode setup. The role
> definitions come from ASES/EDASES work; Paseo provider aliases, Agent Profiles,
> provider-native permissions, MCP servers and workspaces are temporary ways to
> approximate those roles.
>
> **Scope.** This is explicitly **not** an attempt to recreate the future EDASES
> Execution Engine, Kernel or Work Unit inside Paseo, nor to obtain proof-grade
> authority guarantees from a stopgap harness. The goal is narrower: preserve
> useful role separation, remove obviously unnecessary capabilities, prevent
> common accidental/model-initiated boundary crossings where Paseo can do so
> cheaply, and regression-test the important failures already encountered in
> OpenCode. Prefer native Paseo/provider features over new infrastructure.
>
> **Historical-role rule.** Project-specific roles and role variants should be
> retained as historical role records even when future reuse is uncertain.
> Repeated patterns may later be factored into general role templates and
> member templates. This preserves tested operational knowledge without forcing
> every useful project role into the eventual universal role taxonomy.

## 1. Design direction

The immediate target is a Paseo compatibility layer for the role design:

```text
canonical role record
    |
    +-- semantic responsibility
    +-- authority class
    +-- context policy
    +-- capability contract
    +-- delegation policy
    +-- persistence/output policy
    +-- routing/review policy
    +-- conformance tests
            |
            v
      Paseo role adapter
            |
    +-------+----------------+----------------+
    |                        |                |
provider-native          narrow MCP/API     Paseo tool
permissions/sandbox     semantic menu       policy
    |                        |                |
    +------------------------+----------------+
                             |
                         workspace /
                         worktree
```

Paseo is a stopgap execution harness. It should preserve the useful parts of the
current role design while remaining cheap to configure, test and replace.

The governing implementation preference is:

> **Use Paseo and provider-native restrictions first. Remove capabilities that a
> role plainly does not need. Add a narrow MCP/API wrapper only when a concrete
> recurring boundary cannot be expressed adequately with the existing controls
> and the wrapper is substantially simpler than the old OpenCode guard stack.**

A role is still not defined by a bag of tools, but this Paseo programme does not
need to implement every semantic capability as a formally authorized operation.

## 2. Initial role set

This first matrix covers the four roles whose present-day purpose is clear
enough to implement and test immediately.

### 2.1 Orchestrator

The Orchestrator is the **only normal top-level role** and the default for every
new session.

Responsibilities:

- receive the user/strategy task;
- directly read a deliberately selected set of required full documents;
- receive most other context as summaries, retrieved fragments, or worker
  reports;
- explicitly request a full document when the summarized context is
  insufficient;
- decompose and delegate bounded work;
- choose worker role/profile/model according to routing policy;
- supervise worker lifecycle and failures;
- integrate findings and decisions;
- update project/canonical documentation and knowledge;
- surface decisions to the user.

It should not silently become an implementation worker. Direct project mutation
is not part of its normal role.

### 2.2 Builder

The Builder is the normal implementation/mutation role.

Responsibilities:

- inspect the bounded implementation target;
- edit/create project artifacts;
- use shell/build/test tools required by the task;
- run relevant verification;
- return evidence, blockers and candidate project-knowledge updates.

Builder may be explicitly selected by the user as a top-level session role, or
created by an Orchestrator. A Builder selection must be **session-local and
non-sticky**: the next new session returns to Orchestrator by default.

Builder does not automatically receive unrestricted web or delegation
authority. External sites and services should be limited to what the task
requires where practical.

### 2.3 Reviewer

The Reviewer is a bounded artifact-conformance role:

> Given an object, the request/specification for that object, and relevant
> acceptance tests/checks, determine whether the object is what was requested
> and works as requested.

Responsibilities:

- read the request/specification and finished artifact;
- inspect relevant diffs/implementation;
- run bounded, approved tests or other minor verification tools;
- report mismatches, missing evidence and residual uncertainty;
- append findings/candidate knowledge updates for Orchestrator attention.

Reviewer is read-only with respect to project artifacts and canonical project
knowledge. Reviewer cannot delegate a Builder or otherwise acquire mutation
authority transitively.

Reviewer may be explicitly user-selected as a top-level role, but the selection
must not become the next-session default.

### 2.4 Researcher

The Researcher is an information-acquisition role.

Responsibilities:

- search and retrieve external information;
- inspect enough selected project context to understand the research question;
- return sourced evidence and a concise synthesis;
- append candidate project-knowledge items for Orchestrator attention.

Researcher normally has broader information authority than Builder but much
less project/execution authority:

- broad web/search access;
- project read as required;
- little or no arbitrary shell;
- no project mutation;
- no implementation-agent delegation;
- no canonical project-knowledge mutation.

## 3. Roles still under refinement

These remain valuable historical/design records but are not yet frozen as Paseo
MVP profiles:

- **Auditor** — process/evidence/provenance and claim-vs-evidence divergence;
  earlier design used one role with in-flight and post-hoc phases.
- **Verifier** — current working hypothesis: composition/integration correctness;
  determine whether already accepted components work together as the larger
  system requires. This is distinct from re-reviewing each component.
- **Ontology Reviewer** — specialist review operation for conceptual identity,
  distinctions, ownership, lifecycle, boundaries and semantic drift; likely a
  member/specialization of the review family rather than a new authority class.
- Other project-specific reviewer, builder and researcher variants.

The role-justification criterion remains useful: create a durable distinct role
when it occupies a distinct capability/authority point and guards a distinct
failure class. Otherwise prefer a member/specialization or operation within an
existing role family.

## 4. Capability dimensions

The current work suggests at least five independent dimensions. A role profile
should not infer one from another.

| Dimension | Example range |
| --- | --- |
| Artifact authority | none -> read -> bounded mutation -> broad mutation |
| Execution authority | none -> named tests -> bounded commands -> shell |
| Information authority | supplied context -> selected sources -> broad web |
| Delegation/control authority | none -> status only -> bounded worker launch -> lifecycle control |
| Project-knowledge authority | read -> append candidate -> canonical update |

This matters because, for example:

- Builder may have shell and mutation but only selected external sites.
- Researcher may have broad web access while remaining project-read-only.
- Reviewer may run named tests without gaining general shell.
- Orchestrator may update canonical knowledge while lacking implementation
  mutation authority.

## 5. Paseo enforcement surfaces at the inspected baseline

Baseline: `getpaseo/paseo@0d05584d044f5a72212d509ead7af0532dd105e2`.

The current implementation exposes the following useful stopgap mechanisms.

### 5.1 Derived provider identities

Paseo provider overrides can extend a built-in provider and independently set
provider options, environment, model catalog, `disallowedTools`, and a Paseo
tool policy.

These derived provider IDs are a useful **runtime enforcement identity**, for
example:

```text
ases-orchestrator-opencode
ases-builder-opencode
ases-reviewer-opencode
ases-researcher-opencode
```

They are not the canonical role definitions.

### 5.2 Paseo tool catalog policy

Per exact provider ID, Paseo can:

- inject the full Paseo tool catalog;
- remove selected tools through `disabledTools`;
- remove the whole catalog through `enabled: false`.

Disabled Paseo tools are omitted when the catalog is constructed. This is a
meaningful application-level removal, but Paseo's own documentation correctly
states that it is **not a host security boundary for an agent with shell
access**.

### 5.3 Provider-native controls

Paseo passes provider-specific options through to the underlying agent.

At the inspected baseline, relevant examples include:

- **OpenCode:** per-tool `allow / ask / deny` permission maps, including
  `read`, `edit`, `bash`, `task`, web and external-directory controls.
- **Codex:** `sandbox_mode` (`read-only`, `workspace-write`,
  `danger-full-access`), workspace-write roots/network controls,
  `web_search`, and `features.multi_agent_v2`.
- **Claude:** `allowedTools` / `disallowedTools`, native sandbox controls,
  filesystem read/write restrictions, network-domain allowlists and
  `allowUnsandboxedCommands`.

The same semantic role capability may therefore compile to different
provider-native settings.

### 5.4 Per-agent MCP servers

`AgentSessionConfig` accepts `mcpServers`, which Paseo translates to the
provider's supported MCP mechanism. This is the preferred place to represent
small provider-neutral semantic menus such as:

```text
document.read_required
document.request_full
agent.delegate_builder
agent.delegate_reviewer
agent.status
agent.cancel
project.finding.append
project.knowledge.read
project.knowledge.update
test.run_named
```

The exact eventual menu remains to be designed. The important constraint is
that MCP/API operations should express semantic authority rather than merely
wrap unrestricted shell commands.

### 5.5 Workspaces/worktrees

Paseo workspaces and Git worktrees provide useful operational separation and
lifecycle management. They are not, by themselves, a security boundary against
a same-user process with sufficient filesystem access.

### 5.6 Agent Profiles

Paseo Agent Profiles bundle provider/model/mode/thinking/features plus
human/model-facing "When to use" notes.

For ASES they should be treated as **routing/convenience objects**, not authority
definitions. A profile may select an `ases-reviewer-*` enforcement provider,
but the saved profile itself is not the source of the Reviewer boundary.

No canonical host setting designating an Agent Profile as the immutable
new-session default was identified in the inspected source. The requirement
"new session -> Orchestrator unless the user explicitly selects another role"
should therefore be treated as an ASES conformance requirement that may need a
small Paseo UI/plugin/default-selection change.

## 6. Initial semantic capability matrix

Legend:

- **Y** — normal role capability.
- **B** — bounded/named form only.
- **N** — absent by default.
- **U** — user-explicit top-level selection only.
- **A** — append/candidate only, not canonical mutation.

| Semantic capability | Orchestrator | Builder | Reviewer | Researcher |
| --- | :---: | :---: | :---: | :---: |
| Default top-level session | **Y** | N | N | N |
| Explicit user-selected top-level session | Y | **U** | **U** | optional U |
| Receive required full task docs | **Y** | B | **Y** | B |
| Request additional full document | **Y** | B | B | B |
| Read bounded project artifacts | **Y/B** | **Y** | **Y** | B |
| Broad repository exploration | N/B | **Y** | B | B |
| Project artifact mutation | N | **Y** | N | N |
| Arbitrary shell | N | **Y** | N | N |
| Named/bounded test execution | B | **Y** | **B** | N/B |
| Broad web search/retrieval | N | B | N/B | **Y** |
| Selected external documentation/sites | B | **B** | B | **Y** |
| Launch Builder | **Y** | N | N | N |
| Launch Reviewer | **Y** | N | N | N |
| Launch Researcher | **Y** | N | N | N |
| Launch arbitrary agent/profile | N | N | N | N |
| Inspect worker status/activity | **Y** | N | N | N |
| Cancel/kill owned worker | **Y** | N | N | N |
| Directly control unrelated agents | N | N | N | N |
| Read project knowledge | **Y** | B | **Y** | B |
| Append finding/candidate knowledge | **Y** | **A** | **A** | **A** |
| Update canonical project knowledge/docs | **Y** | N | N | N |
| Change role/authority policy | N by default | N | N | N |
| Merge/deploy/publish consequential state | separate explicit policy | N by default | N | N |

The Orchestrator's project-read entry is deliberately `Y/B`: it receives the
required documents directly and may read more when specifically needed, but
broad implementation exploration should normally be summarized/delegated
rather than becoming the Orchestrator's routine mode.

## 7. Paseo realization matrix

The following table is the first implementation-oriented mapping. "Known
bypass/limitation" is mandatory: an enforcement claim is incomplete without it.

| Semantic capability / boundary | Paseo representation | Provider-specific enforcement | Expected conformance test | Known bypass / limitation |
| --- | --- | --- | --- | --- |
| **Orchestrator is new-session default** | Default new-agent selection to ASES Orchestrator profile/provider | N/A | Start fresh session after using Builder/Reviewer; role must be Orchestrator | No native immutable default Agent Profile was identified; likely small UI/plugin/default-selection change |
| **Specialist choice is explicit and non-sticky** | Builder/Reviewer profiles visible but never persisted as next default | N/A | Select Builder, close/start new session; new session must revert to Orchestrator | UI state/preferences may currently remember model/settings; must test actual app behavior |
| **Orchestrator direct document set** | Required documents attached/injected in task; narrow document MCP for later reads | Provider-independent | Orchestrator can read supplied full docs without delegating | Document packaging/retrieval policy still needs implementation |
| **Orchestrator additional full-doc request** | Narrow `document.request_full` / retrieval operation | Provider-independent MCP/API | Given summary only, explicit full-doc request returns exactly requested doc | A raw filesystem read tool would widen this boundary |
| **Orchestrator cannot implement directly** | Remove mutation tools; no generic shell; read-only or no-shell provider mode | OC: edit deny + bash deny/bounded. Codex: read-only. Claude: disallow Write/Edit/Bash + sandbox | Direct write/edit/shell mutation attempts fail | Same-user/provider escape possible if any unrestricted shell/alternate tool remains |
| **Orchestrator can delegate approved roles** | Selected Paseo agent tools or preferably narrow delegation MCP/API | Disable generic launch paths not required | Launch Builder/Reviewer/Researcher succeeds; arbitrary role/provider launch fails | Paseo `create_agent` is broader than desired; semantic wrapper may be preferable |
| **Orchestrator owns worker lifecycle** | status/activity/cancel/kill subset | Paseo tool policy | Status/cancel owned child succeeds; unrelated-agent control fails | Stock Paseo tools may address arbitrary agent IDs; ownership scoping may require wrapper/plugin |
| **Orchestrator canonical-knowledge update** | Narrow project-knowledge MCP/API | Provider-independent | Update accepted project doc/knowledge through approved operation | Raw filesystem/Crosslink access would be broader than semantic operation |
| **Builder project mutation** | Worktree/workspace + provider-native writable mode | OC edit/bash allow as needed. Codex workspace-write. Claude allowWrite project roots | Create/modify target file succeeds inside assigned workspace | Worktree is not host isolation; same-user shell may reach outside unless sandboxed |
| **Builder shell** | Provider-native shell | OC bash; Codex workspace-write shell; Claude Bash under sandbox | Required build/test commands run | Highest-risk role; unrestricted shell can bypass application-level catalog restrictions |
| **Builder web limited to selected sites** | Provider sandbox/network allowlist where available; otherwise dedicated retrieval MCP | Claude strict domain allowlist strongest. Codex network policy/proxy where available. OC may need web deny + semantic retrieval | Approved docs site reachable; unrelated site unavailable | Provider parity incomplete; OpenCode free-tier anti-abuse may react to restrictive surfaces |
| **Builder cannot delegate** | Remove Paseo agent-control tools; disable provider-native subagents | OC `task: deny`; Codex `multi_agent_v2: false`; Claude disallow Agent | Paseo create-agent absent; direct provider subagent attempt denied | Must test each provider; provider-native delegation is separate from Paseo tool injection |
| **Builder candidate-knowledge append only** | Narrow append-only MCP/API | Provider-independent | Append candidate succeeds; canonical update call unavailable | If raw Crosslink/filesystem access exists, boundary can be bypassed |
| **Reviewer project read-only** | Read-only workspace/provider sandbox; no mutation Paseo tools | OC edit deny + restricted bash. Codex read-only. Claude deny Write/Edit + sandbox denyWrite | Native write/edit, git-write and filesystem mutation attempts all fail | Application restriction is not proof of authority isolation if shell/other executable mutation path remains |
| **Reviewer bounded tests** | Prefer named `test.run_named` semantic tool or tightly scoped provider commands | Provider-specific command allowlist where reliable | Approved test executes; arbitrary command fails | Generic shell parser/allowlist risks repeat OpenCode command-routing complexity |
| **Reviewer cannot delegate** | No Paseo agent control; provider-native delegation disabled | Same as Builder no-delegation controls | Direct and indirect delegation attempts fail | Must include confused-deputy/transitive-write tests, not only tool discovery |
| **Reviewer append finding only** | `project.finding.append` / candidate sink | Provider-independent | Finding persists; knowledge edit/update unavailable | Sink must not expose issue lifecycle, dispatch or arbitrary knowledge mutation |
| **Researcher broad web** | Web/search provider capability or dedicated research MCP | Profile/provider selected for broad information access | Search/retrieve arbitrary relevant public source succeeds | External content is untrusted; prompt-injection exposure is intentionally higher |
| **Researcher no project mutation** | Read-only provider mode; no mutation/delegation tools | Same read-only controls as Reviewer | Direct/indirect project-write attempts fail | Broad web plus same-user shell must not coexist accidentally |
| **Researcher candidate append only** | Same append-only sink | Provider-independent | Candidate item persists; canonical update denied | Same as Reviewer |
| **Role authority survives model/provider change** | Role-specific provider identities/config compiler | Compile equivalent restrictions for each provider | Same role on OC/Codex/Claude passes same authority tests | Provider mechanisms are not semantically identical; unsupported enforcement must be marked, not assumed |
| **Hidden/disabled tool is also unusable** | Catalog filtering plus execution-side/provider rejection | Provider and MCP execution boundary | Fabricated direct invocation of disabled operation fails | Catalog hiding alone is insufficient; must test actual invocation path |
| **Child role cannot alter parent role** | Paseo parent/child identity + role-specific launch config | No shared mutable role scalar in adapter | Concurrent child actions do not change parent effective permissions | Regression inspired by OpenCode #204; must be tested under concurrency |
| **Restart/resume does not widen authority** | Persist role/provider config; defaults reapply on resume | Provider options deep-merged on launch/resume | Restart/resume retains same denied capabilities | Changes to provider defaults can intentionally change future resume; provenance/versioning needed |
| **Role cannot silently self-upgrade settings** | Remove/update-agent or mode-switch authority from non-Orchestrator roles | Paseo tool policy + provider controls | Builder/Reviewer cannot switch to full-access mode/model profile to gain tools | Stock `update_agent` / `set_agent_mode` are powerful and should be removed from workers |
| **Paseo catalog restriction is not called host isolation** | Documentation + tests | N/A | Security record distinguishes representation/app enforcement/host confinement | Fundamental stopgap limitation until stronger container/Work Unit boundary |

## 8. Provider compilation sketch

This is illustrative, not yet a committed configuration.

### 8.1 Reviewer semantic contract

```text
artifact read       yes
artifact mutate     no
general shell       no
named tests         yes
web                 default no
delegation          no
candidate append    yes
canonical update    no
```

Possible temporary compilation:

**OpenCode**
- `read: allow`
- `edit: deny`
- `task: deny`
- `external_directory: deny`
- web denied unless task requires it
- `bash`: preferably deny and expose named tests through MCP; otherwise exact
  bounded commands only.

**Codex**
- `sandbox_mode: read-only`
- `web_search: disabled`
- `features.multi_agent_v2: false`
- named tests preferably outside generic shell via semantic tool.

**Claude**
- disallow Write/Edit/Agent and generic Bash if named-test tooling is available;
- sandbox enabled with `failIfUnavailable: true`;
- filesystem write denied;
- network denied or narrowly allowlisted.

Paseo:
- `paseoTools.enabled: false` unless a small status/read capability is genuinely
  required;
- inject only the ASES review MCP menu.

### 8.2 Builder semantic contract

```text
artifact read       yes
artifact mutate     yes
shell               yes
web                 selected/needed
delegation          no
candidate append    yes
canonical update    no
```

Paseo:
- remove all generic agent-control tools;
- disable provider-native subagents;
- assign a dedicated worktree;
- apply provider sandbox/network restrictions where available;
- inject candidate-finding/project-context MCP operations as needed.

### 8.3 Orchestrator semantic contract

```text
required docs       full direct access
other context       summarized/retrieved default
artifact mutate     no
generic shell       no
delegation          approved role menu
worker lifecycle    owned subtree
candidate append    yes
canonical update    yes
```

The key design question is whether to expose selected stock Paseo tools
(`create_agent`, `send_agent_prompt`, `get_agent_status`, `cancel_agent`,
etc.) or put a narrower ASES semantic facade in front of them. Because stock
tools can address more state than the role ideally owns, the facade is likely
the cleaner long-term-compatible option.

### 8.4 Researcher semantic contract

```text
project read        bounded
artifact mutate     no
shell               none/minimal
web                 broad
delegation          no
candidate append    yes
canonical update    no
```

The researcher should normally receive broad information tools but a smaller
execution surface than Builder.

## 9. Conformance-test seed set

These tests are implementation-independent descriptions. The Paseo test suite
should instantiate them for every supported provider/profile combination.

### Session/root invariants

- **SESSION-01** — A fresh session starts as Orchestrator.
- **SESSION-02** — Builder/Reviewer require an explicit user choice.
- **SESSION-03** — Specialist choice is not sticky across new sessions.
- **SESSION-04** — Delegated children never become detached/top-level merely by
  provider behavior.

### Role-identity invariants

- **IDENT-01** — Child activity cannot change the parent's effective role.
- **IDENT-02** — Parallel children of different roles retain distinct authority.
- **IDENT-03** — Resume/restart preserves the effective role contract.
- **IDENT-04** — Changing model/provider cannot silently widen role authority.

### Orchestrator invariants

- **ORCH-01** — Required full documents are directly available.
- **ORCH-02** — Additional full document access requires an explicit request.
- **ORCH-03** — Normal implementation mutation is unavailable.
- **ORCH-04** — Approved worker roles can be launched.
- **ORCH-05** — Unapproved/arbitrary worker launch fails.
- **ORCH-06** — Orchestrator can update canonical project knowledge through the
  approved interface.
- **ORCH-07** — Worker status/lifecycle operations cannot control an unrelated
  principal if ownership scoping is implemented.

### Builder invariants

- **BUILD-01** — Assigned project mutation succeeds.
- **BUILD-02** — Required shell/build/test work succeeds.
- **BUILD-03** — Agent delegation is unavailable.
- **BUILD-04** — Canonical project-knowledge mutation is unavailable.
- **BUILD-05** — Candidate/attention append succeeds.
- **BUILD-06** — Network access matches task/profile policy rather than defaulting
  to unrestricted web.

### Reviewer invariants

- **REV-01** — Reviewer can read the request and artifact.
- **REV-02** — Reviewer can run approved bounded tests.
- **REV-03** — Direct mutation tools fail.
- **REV-04** — Indirect mutation paths fail.
- **REV-05** — Reviewer cannot delegate a Builder or another mutating principal.
- **REV-06** — Reviewer can append its own finding/candidate.
- **REV-07** — Reviewer cannot update canonical project knowledge.
- **REV-08** — A fabricated invocation of a hidden/disabled mutation operation
  fails at execution rather than merely being absent from discovery.

### Researcher invariants

- **RES-01** — Broad external search/retrieval works.
- **RES-02** — Project mutation fails.
- **RES-03** — Implementation-agent delegation fails.
- **RES-04** — Candidate knowledge append succeeds.
- **RES-05** — Canonical project-knowledge update fails.

### Cross-role/confused-deputy invariants

- **XROLE-01** — Read-only roles cannot cause project mutation transitively
  through Paseo, provider-native subagents, MCP, Crosslink, shell or another
  agent.
- **XROLE-02** — A worker cannot change its own mode/profile/settings to obtain
  higher authority.
- **XROLE-03** — A role-specific semantic MCP tool validates role/ownership at
  execution and does not trust only the model-visible menu.
- **XROLE-04** — A free-model/provider compatibility failure is reported as a
  compatibility failure rather than solved by silently widening the role.

## 10. Practical enforcement confidence

The Paseo work should distinguish what kind of evidence we actually have
without turning the stopgap into an authority-verification project.

### P — presentation restriction

The capability is absent from the model-visible tool/menu surface.

This is useful. It reduces accidental misuse and model confusion. It should not
be described as stronger isolation than it is.

### E — exercised enforcement

The current Paseo/provider path rejects the forbidden operation in direct
testing, including a small number of deliberately adversarial attempts.

This is the normal practical target for important role boundaries in Paseo. It
is a regression-tested property of the current configuration, not a universal
security proof.

### I — isolation/confinement

The underlying process cannot bypass the boundary even with arbitrary code
execution.

This belongs to sandbox/container/OS mechanisms and, ultimately, the future
EDASES execution substrate. It is **not a requirement for the Paseo MVP**.
Where a provider already gives useful sandboxing cheaply, use it; do not build
a new confinement system around Paseo.

The practical question for this programme is therefore:

> Does this configuration make the intended role boundary materially harder to
> cross than the old OpenCode setup, and do our tests catch the failure modes we
> already know matter?

## 11. Immediate implementation questions

The matrix leaves a small number of implementation questions to resolve before
writing the first Paseo configuration:

1. **Default-root mechanism.** What is the smallest configuration or UI change
   that makes fresh sessions default to Orchestrator and specialist choices
   non-sticky?
2. **Stock Paseo tools first.** Which existing Paseo orchestration tools are
   already good enough for the Orchestrator without adding a facade?
3. **Document access.** What is the simplest way to provide required full
   documents and occasional explicit full-document reads?
4. **Reviewer testing.** Can existing named workspace scripts or provider
   command restrictions give Reviewer enough testing ability without a general
   shell? Add a wrapper only if that is materially simpler.
5. **Candidate-knowledge append.** What existing Crosslink/MCP mechanism can be
   narrowed to append attention items without recreating a new knowledge
   service?
6. **Provider coverage.** Which useful boundaries work on the providers/models
   we actually intend to use now? Exact cross-provider parity is not required.
7. **OpenCode free-tier compatibility.** Which restrictive profiles work with
   the current free catalog without triggering anti-abuse rejection? Record
   incompatibility rather than redesigning the role around the free tier.
8. **Ownership scoping.** Test whether stock Paseo lifecycle tools are too broad
   in practice. Only add an ownership-scoped wrapper if the gap is real and
   operationally important.

## 12. Relationship to historical OpenCode controls

The OpenCode/Crosslink implementation remains useful evidence, but it is not
the target architecture.

Portable lessons retained here include:

- native permission declarations must be tested against actual execution;
- role identity must be per-session/principal, not a shared mutable scalar;
- hiding a tool is weaker than execution-time authorization;
- read-only must include indirect/transitive mutation analysis;
- the producer of a review/audit finding should have a durable append path;
- append authority does not imply issue-lifecycle, dispatch or canonical
  knowledge authority;
- dead/dormant controls must not be counted as enforcement;
- role/provider/model changes must not silently change authority;
- confused-deputy paths are first-class tests.

OpenCode-specific shell parsing, wrapper behavior and guard implementation
should not be copied unless Paseo exposes the same concrete failure.

## 13. Expected next step

Turn the seed invariants into a **small practical Paseo compatibility test
checklist** and run it against the first provider/model combinations we can use.

Classify each result as:

- **NATIVE** — Paseo/provider already behaves as desired;
- **CONFIG** — a supported setting is sufficient;
- **SMALL PATCH** — a small Paseo/plugin/wrapper change is justified;
- **EXTERNAL** — an existing sandbox/container or external service is needed;
- **DEFER** — useful for the future Execution Engine but unnecessary for this
  stopgap;
- **NOT WORTH IT** — the improvement would require disproportionate temporary
  engineering.

The purpose of the checklist is to identify the minimum configuration and small
changes needed to make Paseo clearly better than the old OpenCode harness, not
to prove the future ASES architecture in advance.
