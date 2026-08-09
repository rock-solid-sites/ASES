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
ChatGPT Web
### Review

````
I would **not carry on with the current permission-enforcement architecture as the long-term solution**. I would keep the four-role workflow and Crosslink topology, but **move the security boundary down one or two layers and substantially simplify the in-process enforcement machinery**.

The document has crossed an important threshold: this is no longer a case of "a few permission bugs to fix." The evidence shows that the architecture is trying to establish **repository integrity and authority isolation using mechanisms that live inside the same agent execution environment they are supposed to constrain**. That is the wrong boundary for the property you actually want.

The strongest indication is that the reviewers independently converge on three failed properties: indirect writes, role identity, and enforcement-plane integrity. The current system satisfies direct write-tool denial reasonably well, but not repository immutability or authority isolation. 

## My recommendation

I would change the architecture from:

> **Agent → Opencode permissions → plugins → Crosslink guard → repository**

to approximately:

> **Agent process → isolated execution environment → capability-controlled gateway → persistent project state**

with the important distinction that **the agent should not possess the authority necessary to alter the mechanism enforcing its own restrictions**.

In practical terms, I would aim for:

```text
                         TRUSTED CONTROL PLANE
                    ┌───────────────────────────┐
                    │ Operator / Orchestrator   │
                    │                           │
                    │ Crosslink                 │
                    │ Workflow state            │
                    │ Policy / capability grant │
                    └─────────────┬─────────────┘
                                  │
                         explicit capability
                                  │
                    ┌─────────────▼─────────────┐
                    │ Execution Supervisor      │
                    │                           │
                    │ creates isolated runtime  │
                    │ mounts appropriate state  │
                    │ controls network / tools  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │ Agent Sandbox              │
                    │                           │
                    │ Builder                   │
                    │ Reviewer                 │
                    │ Auditor                  │
                    │                           │
                    │ Cannot modify supervisor  │
                    │ or its policy             │
                    └─────────────┬─────────────┘
                                  │
                       controlled artifact path
                                  │
                    ┌─────────────▼─────────────┐
                    │ Project State             │
                    │                           │
                    │ git / artifacts / DB      │
                    └───────────────────────────┘
```

The exact implementation could still use Opencode, Crosslink, containers, worktrees, etc. The important change is **where authority resides**.

---

# Why I would make that change

There are four particularly serious findings.

### 1. The Builder can modify the enforcement plane

This is the architectural deal-breaker.

The document confirms that Builder has unrestricted `edit` and `bash`, while the enforcement configuration is live mutable state. In particular, `hook-config.json` is read on every resolution, `.opencode/plugins/*.ts` are themselves writable, and `.active-issue` is an ordinary file trusted by the guard. 

That means the architecture has:

```text
Builder
   │
   ├── modifies code
   │
   └── can modify the thing deciding what Builder is allowed to do
```

You can patch individual files and add more guards, but you are fighting the fundamental topology.

A real security boundary should instead look like:

```text
Builder ─────X────> enforcement configuration
                         ▲
                         │
                 trusted supervisor
```

The document itself essentially arrives at this conclusion, suggesting read-only mounts, separate users, or a trusted computing base. 

I would take that recommendation much further and make it the architectural direction.

---

### 2. The system is accumulating enforcement mechanisms rather than reducing authority

You currently have:

* Opencode native permissions
* `orchestrator-guard`
* `crosslink-guard`
* `rtk-guard`
* wrapper behavior
* Crosslink configuration
* `--allowedTools`
* environment-based identity
* session-event identity
* `.active-issue`
* user-level Opencode plugin
* global model configuration
* external binaries
* MCP permissions
* launch-mode differences
* container-mode differences

The document explicitly identifies security-relevant configuration as being distributed across nine places. 

That is a warning sign.

The system has reached the point where **the enforcement mechanism itself is becoming a system that needs to be audited**.

The reviewers found:

* a dead/dormant security mechanism;
* a wrapper silently dropping a security flag;
* a container path behaving differently from the local path;
* identity resolution failing open;
* plugin ordering not established;
* a mutable enforcement configuration;
* an incomplete MCP deny list;
* an allowlist that isn't actually a deny boundary;
* `--auto` changing permission semantics;
* deployed/source version divergence.

These aren't random bugs. They are symptoms of **security policy being distributed across too many layers with ambiguous authority**.

The document's own invariant 7 captures this particularly well: the desired configuration invariant is not satisfied because there isn't one authoritative implementation path. 

I would therefore resist the temptation to make the current system "more sophisticated."

I'd make it **smaller**.

---

# 3. The role model is actually good; the enforcement mechanism is the problem

I would **not throw away the four roles**.

The conceptual division is sound:

```text
Orchestrator
    │
    ├── Builder
    │
    ├── Reviewer
    │
    └── Auditor
```

And the distinction between:

* who plans,
* who implements,
* who reviews,
* who independently audits

is useful to EDASES/ASES.

The problem is trying to express those distinctions primarily through:

```text
"this process has these tools,
 except this plugin intercepts some,
 except this wrapper modifies some,
 except Crosslink interprets some,
 except container mode does something else..."
```

Instead, I would make the **execution environment itself embody the role**.

For example:

### Reviewer

Give Reviewer:

* repository snapshot/worktree
* read-only filesystem
* no write capability
* no credentials capable of modifying project state
* restricted network
* no ability to launch another privileged agent

Then you don't need to prove that `git checkout`, `npm run`, `cargo`, `python`, `opencode --pure`, etc. are all harmless.

If Reviewer can execute:

```bash
python3 whatever.py
```

but the entire repository filesystem is mounted read-only, the interesting question becomes much smaller.

That is an enormous reduction in proof burden.

---

# 4. "Read-only" should become an OS/filesystem property

This is probably the single biggest architectural change I'd make.

Currently you're trying to establish:

> Reviewer cannot modify repository state.

by proving that dozens of commands cannot cause modification.

That's backwards.

Instead:

> Reviewer runs with repository state mounted read-only.

Then:

```text
git reset
git checkout
git config
npm install
python3 -c ...
cargo run ...
opencode --pure ...
```

can mostly become irrelevant to the integrity property.

They might still be dangerous for other reasons, but they no longer automatically violate:

> Reviewer cannot modify the project artifact.

This directly addresses the distinction the document makes between:

* A — tool denial
* B — repository immutability
* C — authority isolation. 

Your current architecture is largely attempting to prove A and infer B/C.

I'd establish B physically and then deal with C separately.

---

# What I would put outside the agent

I'd introduce a small **Execution Supervisor** / **Agent Runtime**.

Not another giant policy engine.

Something much more boring:

```text
ExecutionRequest {
    run_id
    role
    model
    repository
    revision
    capabilities
    network_policy
    resource_limits
}
```

The supervisor:

1. validates the request;
2. creates the execution environment;
3. mounts the correct project state;
4. applies the role's filesystem/network capabilities;
5. launches Opencode;
6. captures the result;
7. destroys the environment;
8. returns artifacts/results to Crosslink.

Crucially, the Builder does not get access to the supervisor's control interface except through whatever narrow protocol is explicitly necessary.

That gives you a much cleaner trust hierarchy:

```text
                 TRUSTED
                    │
        ┌───────────┴───────────┐
        │                       │
   Supervisor              Crosslink
        │
        │ creates
        ▼
     Sandbox
        │
        ├── Builder
        ├── Reviewer
        └── Auditor
```

---

# This also changes how I would think about Crosslink

I would **not make Crosslink the security boundary**.

Crosslink is very valuable as the **workflow/state/coordination plane**.

Its job can be:

* issue state
* agent identity
* session state
* kickoff
* work assignment
* result reporting
* locks
* orchestration
* provenance
* audit trail

But I would avoid making:

> "Crosslink hook successfully parsed this shell command"

the thing upon which repository integrity depends.

The current document demonstrates why. The guard has to understand shell commands, git semantics, agent identity, session events, configuration overlays, sentinels and launch modes. `allowed_bash_prefixes` isn't even a denial boundary in practice. 

Crosslink should answer:

> **What is this agent supposed to be doing?**

The execution environment should answer:

> **What is this process physically capable of doing?**

Those are different questions.

---

# I would also eliminate the "identity resolution" problem rather than fix it

Current:

```text
session events
      ↓
environment
      ↓
config fallback
      ↓
default builder
```

The document confirms that this can resolve an unknown role to Builder, with the resulting configuration allowing operations that Reviewer/Auditor should not have. 

I wouldn't spend much time making this resolution algorithm cleverer.

Instead:

```text
Supervisor launches:

agent_id = 7f...
role = reviewer
capability_profile = reviewer-v3
```

and the runtime gets those properties from a trusted launch context.

If role identity cannot be established:

```text
DENY
```

Not:

```text
probably builder
```

That becomes a trivial invariant.

---

# I would remove `--allowedTools` from the architecture

At least for now.

The current implementation is exactly the sort of thing I would classify as **architectural debt rather than a feature waiting to be completed**.

The local path drops it; the container path may enforce it; its generated list is not role-specific; and its current base list contains capabilities that would actually be inappropriate for Reviewer/Auditor. 

That is too much ambiguity for too little value.

Either:

1. make it a real, tested, per-role capability mechanism, **or**
2. delete it.

I'd choose **2 initially** and let the supervisor/sandbox provide the stronger boundary.

---

# Containers vs microVMs

This is where I'd make a more nuanced decision.

I **would not jump straight to microVMs as a prerequisite**.

A containerized runtime can already solve a large portion of the problem:

```text
Reviewer container
  /workspace → read-only
  /output    → controlled writable volume
  network    → restricted
  credentials → minimal
  runtime   → disposable
```

For Builder:

```text
Builder container
  /workspace → writable
  policy     → outside container
  credentials → limited
```

That would be a dramatic improvement over the current arrangement.

However, if EDASES ultimately wants to make a strong claim against **actively malicious/misaligned agents**, rather than merely buggy agents, then I'd expect the architecture to eventually move toward a stronger isolation boundary such as a microVM.

The document correctly identifies that the threat model is currently unresolved, and that this distinction changes the significance of virtually every finding. 

So I would make the architecture **VM/container agnostic**:

```text
Execution Supervisor
        │
        ├── container backend
        │
        └── microVM backend
```

Start with containers.

Don't make the EDASES architecture depend on Docker, Podman, Firecracker, etc.

---

# What I would keep

I would preserve quite a lot.

### Keep the role topology

```text
Operator
   ↓
Orchestrator
   ↓
Builder
   ↓
Reviewer
   ↓
Auditor
```

### Keep Crosslink

But reposition it as workflow/state coordination rather than the ultimate security boundary.

### Keep worktrees/snapshots

They're valuable for isolation and provenance.

### Keep RTK

The document actually establishes a useful property here: RTK is non-authoritative. Removing it should affect performance/token consumption, not authorization. 

That's exactly how an optimization should behave.

### Keep Opencode

There is no evidence here that Opencode itself needs to be replaced. The problem is relying on its permission machinery as the ultimate security boundary.

### Keep model policy

But treat model selection as **policy**, not as the capability boundary. The document itself notes this distinction: model-selection control isn't equivalent to agent-capability control. 

---

# The architecture I'd target

I'd probably end up with five conceptual layers:

### Layer 0 — Host / Trusted Runtime

Small, privileged, boring.

Responsible for:

* launching sandboxes
* resource limits
* filesystem mounts
* network policy
* credential injection
* lifecycle
* integrity of runtime components

Agents cannot modify it.

### Layer 1 — Execution Environment

One disposable environment per agent run.

Its role determines:

* writable paths
* mounted artifacts
* network
* credentials
* available services
* resource limits

### Layer 2 — Agent Harness

Opencode lives here.

Its native permissions become **defense in depth**, not the fundamental security boundary.

If Opencode has a bug, the sandbox still protects the repository.

### Layer 3 — Workflow / Coordination

Crosslink.

Responsible for:

* issues
* sessions
* agent roles
* kickoff
* delegation
* locks
* results
* provenance

### Layer 4 — Persistent State

Git repository, artifact store, knowledge, databases, etc.

Writes happen through controlled transitions rather than arbitrary agent access wherever possible.

---

# This would also simplify the permission model enormously

Instead of this:

```text
Reviewer:
  edit deny
  bash:
    git *
    ls *
    cat *
    cargo *
    npm *
    ...
```

you could eventually have something closer to:

```yaml
reviewer:
  filesystem:
    workspace: read-only
    output: write
  network:
    mode: restricted
  credentials: []
  delegation: none
```

Builder:

```yaml
builder:
  filesystem:
    workspace: read-write
    output: write
  network:
    mode: project-policy
  credentials:
    - required-build-credentials
  delegation: none
```

Auditor:

```yaml
auditor:
  filesystem:
    workspace: read-only
    output: write
  network:
    mode: restricted
  credentials: []
  delegation: none
```

That's a much more tractable capability matrix.

And importantly, it aligns directly with the **Model Capability Matrix** direction you've already identified for EDASES: define capabilities first, then map models/roles/tools/runtimes onto them, rather than encoding security accidentally through command prefixes.

---

# The migration I'd actually recommend

I would **not rewrite everything immediately**.

I'd do this in four phases.

### Phase 1 — Freeze and simplify the existing system

Before building the new runtime:

* stop adding new guard layers;
* fix the documented MUST-FIX factual errors;
* explicitly declare current enforcement **defense-in-depth, not a security boundary**;
* add adversarial tests for the current system;
* make identity fail closed;
* remove or disable dead `--allowedTools` machinery;
* protect or relocate the most obviously mutable trust-root files.

The purpose isn't to perfect the old architecture.

It's to make its failure modes measurable while the replacement is built.

The document explicitly notes that there is currently **no in-repo unit/integration test suite for the guards**, and several of the most interesting bypasses haven't been executed. 

### Phase 2 — Build a minimal container execution backend

Don't integrate everything.

Prove one property:

> Reviewer cannot modify the repository, even when given arbitrary shell execution.

That should be the first architectural acceptance test.

Something like:

```text
launch reviewer
    ↓
container
    ↓
read-only workspace
    ↓
run hostile test suite
    ↓
attempt:
  git checkout
  git reset
  git config
  rm
  python
  npm
  cargo
  opencode --pure
    ↓
repository remains byte-for-byte unchanged
```

If that works, you've eliminated a huge class of current reasoning.

### Phase 3 — Move authority-sensitive operations outside the sandbox

For example:

```text
Agent
  │
  │ "commit artifact X"
  ▼
Supervisor
  │
  ├── validate capability
  ├── validate active Crosslink issue
  ├── validate repository state
  └── perform commit
```

Now Builder doesn't need unrestricted Git authority simply because it happens to be the implementation agent.

This is particularly attractive for EDASES because **commit, merge, push and state transitions are workflow operations**, not inherently "coding tools."

### Phase 4 — Evaluate microVMs

Once the capability model works in containers, ask:

> What threats remain because the container is not a sufficiently strong isolation boundary?

If the answer is "none that matter for the current EDASES threat model," stay with containers.

If the answer is "we need meaningful resistance to hostile/misaligned agents," swap the backend for a microVM.

That keeps the architecture stable while the isolation technology evolves.

---

# One thing I would explicitly *not* do

I would **not** spend the next several iterations turning `crosslink-guard.ts` into a sophisticated shell-security parser.

The document already gives you the reason:

* broad shell families;
* interpreter trampolines;
* command substitution;
* redirection;
* Git's enormous mutation surface;
* `git -C`;
* nested Opencode;
* MCP;
* launch-mode differences;
* fail-open plugin behavior.

You'd be building a miniature mandatory-access-control system inside a TypeScript hook.

That's an enormous amount of complexity to reproduce functionality the operating system/container runtime is already much better positioned to provide.

The reviewers' proposed "deny-by-default" git policy is a reasonable **interim mitigation**, but I would treat it as a bridge to the new architecture rather than the destination. 

---

# Bottom line

**Moderate refactor:** keep the current architecture and harden every guard.

**What I recommend:** **architectural refactor of the enforcement boundary, while preserving the workflow architecture.**

I would characterize the resulting design as:

> **Crosslink defines authority; the execution supervisor enforces capabilities; the sandbox enforces physical isolation; Opencode permissions provide defense in depth; Git/worktrees provide artifact isolation and provenance.**

That is substantially more defensible than:

> **Crosslink + Opencode + wrappers + plugins collectively try to infer whether a shell command is safe.**

The current document is actually valuable because it has demonstrated why the latter is becoming untenable. The most important evidence isn't any individual bypass; it's that **three of the core proposed invariants are fundamentally outside what the current architecture can reliably guarantee**: indirect-write prevention, role identity, and delegation/authority isolation. 

I would therefore **stop treating the existing permission system as the thing to perfect and start treating it as the compatibility/defense-in-depth layer that the new execution architecture will progressively make less important**.

The next design artifact I would create is not another permission configuration. It should be an **EDASES Execution Boundary / Capability Architecture** document defining the trust boundaries, capabilities, sandbox contract, supervisor responsibilities, and invariants before choosing Docker/Podman/Nix/microVM implementation details.

````

## Review 5

### Model
Claude Sonnet 5
### Review

````
I'd change the architecture, not just work the MUST-FIX list. The review set converged on something more serious than a punch list of bugs: the enforcement mechanism itself has a ceiling, and that ceiling is below what the four-role design is trying to buy.

The load-bearing finding is 3.7 (claim g), reinforced by 3.1 and 3.6. Builder has `edit: allow` plus unrestricted bash, and nothing in the system — not the plugins, not the `.md` frontmatter, not file permissions — stops builder from editing `.crosslink/hook-config.json`, the plugin source in `.opencode/plugins/*.ts`, or forging the `.active-issue` sentinel. That's not a missing check to add to a list; it's a self-modifying trust root. Every other guarantee in the document (gated commits, blocked git subcommands, the allowlist) is downstream of config that the one role those guarantees exist to constrain can rewrite. You cannot patch your way out of that inside the current design — you can only patch individual escape routes, which is exactly what eight reviews' worth of findings already did, and there's no reason to believe the ninth review won't find another one. Claim (a)'s `opencode run --pure` finding makes the same point from the other direction: reviewer and auditor are granted `opencode *`, and `--pure` disables every plugin, so the entire crosslink-guard/orchestrator-guard enforcement layer is one documented flag away from not existing for the session. Prefix-matched shell strings checked by an in-process plugin are not a security boundary against a misaligned agent; they're a speed bump against a buggy one.

That distinction is the actual crux, and it's claim (k) — no threat model exists. Whether to refactor depends entirely on which failure mode this system is for. If the goal is catching honest mistakes (a builder that runs the wrong git command, a stale model ID, silent hangs), the current layered-guard approach is proportionate and the section 4.3 list is exactly the right next work — fix the counts, close the MCP gap, document `--auto`, fail closed on identity, ship it. But the fact that you built four separate roles with a dedicated read-only reviewer and auditor only makes sense if the intent is resilience against a misaligned or compromised agent, and against that threat model, string-matching enforcement that the privileged role can edit isn't a weaker version of the goal — it's a different goal that happens to look similar.

If it's the latter, the fix is moving the write boundary outside the agent's process rather than adding more entries to blocklists:

- Reviewer/auditor should run against a filesystem the OS or container runtime makes non-writable — a read-only bind mount or a git worktree checked out read-only — so the boundary holds regardless of which command, interpreter, or trampoline gets used. This replaces claim (a) entirely instead of chasing its instances.
- Enforcement config (`hook-config.json`, the plugin `.ts` files, the sentinel) should not live in builder's writable scope. Put it on the orchestrator side, or behind a small broker process builder talks to but doesn't have filesystem access to, so claim (g) becomes structurally impossible rather than merely undocumented.
- Git write authority should route through that same broker rather than trusting the agent's own process to self-restrict — this also fixes claim (f)'s fail-open identity problem for free, since an unresolved identity just doesn't get a token rather than falling back to the base (effectively builder) config.
- Identity resolution should fail closed by construction (deny by default) rather than defaulting to `agent.type: "builder"` when session data is missing.

That's a real chunk of work — it touches the plugin architecture, probably the kickoff container path, and the trust relationship between builder and the config store — but it's not a rewrite of crosslink, opencode, or the four-role model, all of which are fine. I'd sequence it as: get the operator to commit to a threat model explicitly (open question 6.1 in the doc), then decide. If it's "honest mistakes," ship the MUST-FIX list as-is. If it's "misaligned agent," do the isolation refactor first — the eight reviews' worth of blocklist patches are largely wasted effort under that model, since the next bypass is always one interpreter away.
````

## Review 6

### Model
GLM-5.2
### Review

````
# Assessment: Carry On or Refactor?

## Short Answer

**Do not carry on with the current plan as-is.** The review process was excellent — it surfaced that the architecture does not achieve its stated goal and, more importantly, that the gap between the goal and the implementation is *structural*, not documentary. Documentation corrections (fixing counts, qualifying claims, adding a threat model section) are necessary but insufficient. You need a **targeted architectural refactor** focused on one root cause: **the trusted computing base is mutable by the roles it constrains.**

---

## The Fundamental Problem

The system's stated goal (§2.1) is:

> Permissions enforced by the tooling — rather than merely requested in prose. An agent that is told "you are read-only" but is physically able to write files is not read-only.

The review proved this is false in the most damaging way possible: not through an exotic bypass, but through the system's own normal operation. The problems cascade from a single architectural error:

**The enforcement mechanism lives inside the threat surface it guards.**

Specifically:

1. **The builder can edit the enforcement configuration.** `hook-config.json`, the `.active-issue` sentinel, the guard plugin source files, and the agent `.md` files are all in-repo, and the builder has `edit: allow` + unrestricted `bash`. The guard plugins read this config live on every call. This is a self-modifying trust root — the one role the four-role split exists to constrain can rewrite its own constraints before anyone notices. (Claim (g), 6/8 reviewers, confirmed.)

2. **The guard plugins run inside the agent's own process.** `opencode run --pure` (documented in `--help`, available to any role with `opencode *` in its bash grant, which is all four roles) starts a session with no plugins loaded. This is a one-command bypass of the entire plugin layer. (Claim (a), 8/8 reviewers.)

3. **Identity resolution fails open to the highest privilege.** When the system can't determine who an agent is, it defaults to `builder` — the least restrictive role. The "FAIL-CLOSED" log label is a misnomer; it describes logging, not posture. An unresolved reviewer or auditor can commit. (Claim (f), 7/8 reviewers.)

4. **The "denying surface" isn't a denying surface.** `allowed_bash_prefixes` is an allow-fast-path — matching returns ALLOW immediately, but *not* matching falls through to relaxed-mode allow or active-issue allow. It never denies. The "three surfaces in agreement" framing was wrong; there is effectively one bash-denying surface (the native `.md` block), and even that is bypassable via `--pure`. (Claim (e), confirmed by source reading.)

5. **Every kickoff agent runs with `--auto`**, which the wrapper itself equates to `--dangerously-skip-permissions`. All `ask`-graded permissions become allows. (Claim (h), 4/8 reviewers but confirmed.)

These are not configuration bugs. They are consequences of trying to enforce a security boundary using code that runs in the same process, reads mutable config from the same filesystem, and defaults to permissive when it can't determine state.

---

## What's Worth Keeping

The review revealed that several components are well-designed for their actual (non-security) purpose:

- **The four-role model** (orchestrator/builder/reviewer/auditor) is a sound organizational concept. The problem isn't the roles; it's that the enforcement doesn't match the labels.
- **crosslink as a state hub** (issue tracker, session management, agent identity) is a reasonable orchestration backbone. The issue is that its guard hooks are advisory, not authoritative.
- **rtk-guard** is correctly designed as fail-open and non-authoritative — it's a performance optimization, not a security control, and it doesn't pretend to be one. This is the one component whose stated properties match its implementation.
- **The review process itself** — 8 adversarial reviews, merged with direct source verification, epistemic honesty about what was and wasn't tested — is exemplary. Keep this process regardless of what you do with the architecture.
- **The `claude` wrapper's model enforcement** (rejecting implicit/default model names) is a useful operational control, even if it's not a security boundary.

---

## Recommended Approach: Move the Trust Boundary Outside the Agent Process

### Principle

The enforcement of "who can write what" must be enforced by something the agent **cannot influence at runtime**. This means either the OS (file permissions, separate users, containers, namespaces) or a separate process the agent cannot signal or edit.

### Concrete Changes (in priority order)

**1. Decide the threat model first. (Prerequisite, not implementation.)**

Every finding's severity depends on whether the adversary is an honest-but-buggy agent or a misaligned/compromised one. This is Open Question #1 in the document and it must be answered before any architectural work. My recommendation based on the review evidence:

- If **honest-but-buggy**: the current architecture is over-engineered for what it achieves. Simplify dramatically — the `--auto` injection, the fail-open identity, and the mutable config are still bugs, but the broad bash grants and `--pure` escape are tolerable. Fix the bugs, narrow the grants moderately, and stop calling it "structural enforcement."
- If **misaligned/compromised**: the current architecture provides no meaningful boundary. You need OS-level isolation (below).

The original document's own framing ("structural, not aspirational") implies the stronger model, which the implementation cannot support.

**2. Move enforcement config and plugins outside the builder's write surface.**

This is the single highest-impact change. Options, from lightest to heaviest:

- **Read-only bind mount:** Mount `.opencode/plugins/`, `.crosslink/hook-config.json`, and `.crosslink/.active-issue` as read-only in the agent's filesystem namespace. The builder literally cannot `edit` them. Lowest effort, highest immediate payoff.
- **Separate Unix user:** Run the guard daemon and its config under a different user account. Agents run as a user that can read but not write the enforcement plane.
- **Out-of-process guard:** Move the permission-checking logic out of the opencode plugin (which runs in the agent's Bun runtime) and into a separate process (a crosslink daemon) that the agent can only communicate with via a narrow IPC protocol. The agent sends "can I do X?" and gets yes/no. It cannot edit the daemon's config or code.

**3. Fix fail-open → fail-closed for identity resolution.**

Change `resolveAgentType` to return a deny-by-default state (or throw) when identity cannot be determined, rather than falling back to `builder`. Add a `by_type.builder` entry to `hook-config.json` if you want the builder config to be explicit rather than the implicit default. This is a small code change with large security impact.

**4. Block or scope the `--pure` escape.**

Either:
- Patch the opencode fork to disallow `--pure` for non-builder agents, or
- Remove `opencode *` from reviewer/auditor bash grants and replace it with the specific read-only opencode subcommands they actually need (likely just `opencode models *`), or
- Have the guard daemon intercept `opencode run` calls and reject `--pure` for non-builder sessions.

**5. Fix the `--auto` injection.**

The wrapper unconditionally injects `--auto` for every tmux session, which is every kickoff agent. Either:
- Remove the `--auto` injection and handle permission prompts another way (e.g., a pre-approval list in the guard daemon), or
- Patch opencode so `--auto` only bypasses the consent prompt, not the `.md` permission engine (if this isn't already the case — it's currently unverified, per claim (h) WHAT-NOT-TESTED).

**6. Narrow the reviewer/auditor bash surface.**

Replace broad family grants with specific read-only operations:
- `git *` → `git status`, `git diff`, `git log`, `git show`, `git branch`, `git worktree list` (the exact list already exists in `allowed_bash_prefixes`)
- `cargo *` → `cargo test`, `cargo check`, `cargo clippy` (no `cargo run`, no `cargo build` scripts)
- `npm *` → `npm test`, `npm ls` (no `npm run`)
- `opencode *` → remove entirely or scope to `opencode models`
- `crosslink *` → scope to `crosslink issue show`, `crosslink session status` (no `kickoff`, no `swarm`)

Or accept that these roles are not read-only and rename them accordingly — "analysis" rather than "review," with the understanding that they can mutate state through indirect paths.

**7. Complete or remove `--allowedTools`.**

A dead security control is worse than no control because it creates false confidence (ChatGPT #9). Either:
- Implement it end-to-end with per-role, least-privilege surfaces (the current implementation gives all agent types the same surface, including `Write` and `Edit`), or
- Remove the construction code from `launch.rs`/`prompt.rs` and document that opencode's native `.md` + guard daemon is the sole enforcement surface.

**8. Add `create_directory` and `move_file` to `BLOCKED_TOOLS`.**

This is a one-line fix in `orchestrator-guard.ts`. The review proved these MCP tools exist on the server and are not blocked. Do this immediately regardless of the larger architectural decisions.

---

## What Not to Do

- **Do not just fix the documentation.** Correcting the counts, qualifying the claims, and adding a threat-model section are necessary but they document a system that doesn't achieve its goal. The review's highest-confidence finding (8/8) is that "read-only by construction" is false — rewording it to "direct-write-tool-denied" is honest but doesn't make the system more secure.
- **Do not add more plugin layers.** The current architecture already has five enforcement layers and the review showed they compose poorly (allow-fast-paths that don't deny, fail-open identity, `--pure` bypass, `--auto` overriding `ask`). Adding a sixth layer to patch a gap in the fifth is the wrong direction.
- **Do not try to solve this with more configuration.** The config already lives in nine places with overlay merging, local overrides, and hard-coded defaults. More config increases the attack surface and the drift risk.

---

## Effort Estimate

| Change | Effort | Impact |
|--------|--------|--------|
| Add `create_directory`/`move_file` to `BLOCKED_TOOLS` | 5 minutes | Closes the MCP gap |
| Fix fail-open → fail-closed identity | 1-2 hours | Eliminates the most dangerous runtime bug |
| Narrow reviewer/auditor bash grants | 2-4 hours | Makes "read-only" approximately true |
| Block `--pure` for non-builders | 4-8 hours (fork patch) | Closes the one-command bypass |
| Read-only mount of enforcement config | 1 day | Moves trust boundary outside agent |
| Out-of-process guard daemon | 1-2 weeks | Fundamentally fixes the trust boundary |
| Container-per-role isolation | 2-4 weeks | Strongest isolation, highest effort |

The first four items can be done immediately and address the most severe findings. The last two are the architectural refactor that would make the system's stated goal achievable.

---

## Bottom Line

The review process was the most valuable thing this effort produced — it proved the architecture doesn't work and explained exactly why. The architecture itself needs to move its trust boundary outside the agent process. Start with the quick wins (items 1-5 in the table), decide the threat model, and then commit to either the read-only-mount approach (if the threat model is honest-but-buggy) or the out-of-process daemon / container isolation approach (if it's misaligned). Do not publish the corrected document as if it describes a working security system — it describes a system with good intentions and structural holes, and the next step is to fix the holes, not document them more accurately.
````

## Review 7

### Model
Deepseek V4 Pro
### Review

````
Based on the reviewed document, I would **not carry on with the current plan as-is**. The architecture has fundamental integrity and trustworthiness gaps that make the stated security goal—structural enforcement of read‑only/reviewer‑only roles—unachievable without a significant re‑architecture. Patching the existing stack would continue to fight the same systemic weaknesses.

Here’s a concise diagnosis and a recommended approach.

---

## Why the current plan is unsound

The document’s own reviewed findings (8/8 agreement on key points) make it clear that the system’s permissions are not truly enforced:

1. **“Read‑only by construction” is false**  
   Reviewer and auditor have broad bash grants (`git *`, `opencode *`, reviewer also `cargo *`/`npm *`) that can mutate the repository. The plugin‑based blocklists are finite, prefix‑based, and easily bypassed—especially via `opencode run --pure` which disables all guard plugins entirely. This alone collapses the entire role split.

2. **Identity resolution fails open to the most privileged role**  
   If the agent’s identity cannot be resolved, the system defaults to `builder`—the very role with unrestricted writes and git commit capability. This is fail‑open, not fail‑closed, and the per‑session event delivery can be lost or raced.

3. **The builder can modify enforcement configuration**  
   Because the builder has `edit: allow` and unrestricted `bash`, it can directly edit `.crosslink/hook-config.json`, the `.active-issue` sentinel, the guard plugin source files, and even the wrapper scripts. All enforcement lives inside the same trust boundary that the builder controls.

4. **No explicit threat model**  
   The system assumes agents are “honest‑but‑buggy,” but the permission model and the language of the original document (“physically able to write files”) imply an adversarial or at least misaligned agent. Under an honest‑mistake model the architecture is over‑engineered; under an adversarial model it is wholly insufficient.

5. **Fragile, distributed enforcement surface**  
   Security‑relevant configuration is scattered across nine locations (agent `.md` files, hook‑config files, environment variables, wrapper scripts, user‑level plugins, source code, etc.). There is no single source of truth, and the system relies on the correct composition of many independent, unverified mechanisms.

6. **Dormant/dead controls mask the real posture**  
   `--allowedTools` is constructed but dropped on the local execution path, creating a false assurance. The wrapper silently injects `--auto` under tmux, auto‑approving `ask`‑graded permissions without documentation.

These problems are **architectural**, not just implementation bugs. The current system attempts to build a security boundary using a pile of ad‑hoc scripts and plugins inside a single user account, with no trusted computing base, no integrity checks, and no meaningful isolation between roles.

---

## What should be done instead

I recommend a **different approach**—a moderate‑to‑major re‑architecture that establishes a **genuine isolation boundary** between the write‑privileged builder and the read‑only reviewer/auditor roles. The key principle is: **the builder must not be able to touch the enforcement mechanisms, and the read‑only roles must not be able to touch the repository at all, regardless of what commands they are allowed to execute.**

### Concrete alternative architecture

1. **Process‑level or container‑level isolation**  
   Run the builder, reviewer, and auditor in **separate Linux user namespaces or containers**, each with distinct file‑system mounts:
   - **Reviewer/Auditor**: the repository is mounted **read‑only**, and no path that could modify it is writable. Even if they execute `git push`, `cargo run`, or `opencode run --pure`, it will fail because the OS enforces the read‑only mount.
   - **Builder**: has a writable working copy but **no write access to enforcement configuration** (hook‑config, sentinel files, agent definitions, plugin source). The builder’s container mounts the configuration as read‑only from a separate, trusted volume that only the orchestrator/operator can modify.
   - **Orchestrator/Operator**: runs in the trusted host environment, manages the configuration, and invokes the other roles via the container runtime.

2. **Move enforcement into a trusted daemon / sidecar**  
   Instead of in‑process TypeScript plugins that run inside opencode’s Bun runtime (which the builder can bypass or disable), create a small, separate **policy daemon** that intercepts all tool calls before they reach the host. The daemon knows the role of the calling process (by PID namespace or authenticated token) and enforces a deny‑by‑default policy. It is the **only** path to modify the repository. The builder cannot edit its binary, config, or logs.

3. **Deny‑by‑default, allow‑by‑exception**  
   Abandon the current `git *` + blocklist approach for read‑only roles. Instead, explicitly enumerate the exact set of read‑only commands a reviewer/auditor may run (e.g., `git status`, `git diff`, `cat`, `ls`) and block everything else at the OS/mount level. Bash itself can be restricted to a read‑only, sandboxed shell.

4. **Atomic, signed role assignments**  
   Use a short‑lived, cryptographically signed token that the orchestrator generates to launch each agent. The policy daemon validates the token on every request, binding the session to a specific role and expiration time. This eliminates the fail‑open identity resolution problem and makes the system resilient to event‑stream races.

5. **Immutable enforcement config**  
   Store all security‑relevant configuration (blocklists, allowlists, role definitions) in a version‑controlled, signed directory outside the builder’s reach. The policy daemon loads it at startup and cannot be reloaded without an authenticated operator command.

6. **Drop the wrapper‑script layering**  
   The `claude` wrapper currently drops `--allowedTools`, injects `--auto`, and enforces model whitelists in an un‑auditable bash script. Replace it with a thin, audited launcher that simply invokes opencode with the correct role token and environment, leaving enforcement to the daemon/container runtime.

---

## Bottom‑line recommendation

**Do not carry on with incremental fixes to the current plugin‑and‑wrapper architecture.**  
The review evidence shows that the system’s core promise (“reviewer and auditor are read‑only by construction”) is falsified, and the underlying design cannot be made trustworthy through patches alone.

Instead, **refactor the enforcement boundary to OS‑level isolation**—containers with read‑only mounts for read‑only roles and a separate, tamper‑proof policy enforcement point. This approach directly satisfies the “physically unable to write” criterion the original document set for itself, and it maps cleanly to the agreed‑upon security invariants (ChatGPT’s ten invariants, Qwen’s threat model requirements).

The migration can be phased: start by containerising the reviewer/auditor paths with a read‑only repo mount, while keeping the existing plugin guards as a defense‑in‑depth layer for the builder. Then gradually move all enforcement logic into a dedicated policy daemon and eliminate the fragile wrapper. This path offers a real security improvement without a full rewrite of the agent orchestration logic.

If you need assistance scoping the work or designing the container layout, I’m happy to elaborate.
````

## Review 8

### Model
Qwen 3.8 Max
### Review

````
Based on the exhaustive review documented in the report, **you should not carry on with the current plan.** The architecture requires a fundamental refactor of the enforcement plane.

The document brilliantly exposes a category error in the current design: you are attempting to enforce a **zero-trust, multi-tenant security boundary** using **single-tenant application hooks and string-matching**. As the 8 reviewers established, "structural enforcement" is mathematically impossible when the subject (the Builder) has write access to the laws that govern it (`hook-config.json`, plugins), and when the "read-only" roles possess a shell (`bash: allow`) that can trivially bypass prefix-blocklists via interpreters (`npm run`, `cargo run`, `python -c`) or git config manipulation.

To achieve your goal of true structural authority isolation, you must shift from **Application-Level Interception** to **OS-Level Isolation and Capability-Based Tooling**.

### 1. The Core Architectural Fallacies (Why the Current Plan Fails)

*   **The Shell-Filtering Fallacy (Claims a, e, g):** Giving a read-only agent `bash: allow` and trying to constrain it with `allowed_bash_prefixes` or `blocked_git_commands` is unsecurable. You are attempting to parse shell ASTs with regex. A reviewer can simply run `git config core.hooksPath /tmp/evil` or `npm run build` (which executes arbitrary JS). You cannot block these without blocking the entire shell, at which point the shell is useless.
*   **The Mutable Trust Root (Claim g):** The enforcement plane (`.opencode/plugins/*.ts`, `.crosslink/hook-config.json`, `.active-issue`) lives inside the workspace the Builder is explicitly allowed to edit. A Builder can simply rewrite the config to allow `git push` or delete the guard plugin before executing a command. Structural enforcement is impossible when the subject can edit the law.
*   **The Harness Mismatch (Claim b, d, h):** `opencode` is a developer productivity tool, not a hypervisor. Relying on its `tool.execute.before` hooks means security is entirely dependent on event delivery order and undocumented flags. The fact that `opencode run --pure` completely disables your plugin layer proves that your security boundary is a suggestion, not a physical wall.
*   **The Identity Fail-Open (Claim f):** Identity resolution relies on `chat.params` or env vars that, if lost or delayed, default to the most privileged role (`builder`). In a security architecture, an identity failure must result in a denial (fail-closed), not a promotion.

### 2. The Recommended Architecture: "Zero-Trust Sandboxing & Capability-Based MCP"

To achieve the "read-only by construction" property, you must stop trying to *monitor* the agent's commands and start *restricting its physical environment*.

#### A. OS-Level VFS and Identity Isolation (The Hard Boundary)
*   **Identity:** Stop relying on `CROSSLINK_AGENT_TYPE` or session IDs. Run each agent role as a distinct OS user (e.g., `uid_builder`, `uid_reviewer`) or in isolated containers (gVisor/Firecracker).
*   **Filesystem:** The Reviewer and Auditor containers must mount the repository **strictly Read-Only at the kernel level** (e.g., `mount -o ro,bind`). It does not matter what `git` command the AI hallucinates; the VFS will return `EROFS` (Read-only file system).
*   **Network:** Reviewer/Auditor environments should have a black-hole network namespace or strictly proxied egress. This eliminates the data exfiltration risk that `webfetch: allow` currently creates.

#### B. Eradicate the Shell for Non-Builders (The Tool Boundary)
*   **Revoke `bash` entirely** for Reviewer and Auditor roles.
*   If the Reviewer needs to read a file, it calls a dedicated MCP tool `read_file(path)`.
*   If it needs to see a diff, it calls `get_git_diff(base, head)`.
*   If it needs to run tests, it calls `execute_test_suite()`, which the Orchestrator executes in the *Builder's* sandbox and returns the stdout/stderr to the Reviewer.
*   **Why this works:** You cannot bypass an MCP tool that only exposes `git diff`. The attack surface drops from "infinite bash permutations" to "a handful of strict, auditable RPC calls."

#### C. Externalize the Control Plane
*   The policies (`hook-config.json`) and the enforcement binaries must **not** live in the target workspace.
*   They should be injected at runtime from an immutable, read-only volume or an external Policy Engine (like Open Policy Agent). The Builder can write code, but it physically cannot write the rules that govern its execution.

#### D. Cryptographic Handshakes (Replacing Kickoff)
*   Instead of passing `--allowedTools` through a wrapper that drops it, the Orchestrator provisions a short-lived, cryptographically signed JWT for the Reviewer/Auditor upon instantiation.
*   The MCP servers and tool-gateways validate this JWT. The agent physically cannot invoke a tool its token doesn't permit, regardless of what flags it tries to pass to the CLI.

### 3. Phased Migration Plan

You cannot pivot overnight without disrupting the workflow. Implement this in three phases:

**Phase 1: Stop the Bleeding (Immediate Triage)**
*   **Fix the Fail-Open:** Change the default identity resolution from `builder` to `deny`. If the system doesn't know who is asking, the answer is "no."
*   **Lock the Trust Root:** Change OS-level file permissions so that `.opencode/plugins/` and `.crosslink/` are owned by `root` (or a dedicated `admin` user) and are **read-only** for the `builder` user.
*   **Kill the Sentinel Fast-Path:** Remove the `.active-issue` fast-path trust. Force every commit gate check to query the Crosslink DB via a read-only API to prevent sentinel forgery.

**Phase 2: Containerize the Roles**
*   Wrap the `claude`/`opencode` invocations in Docker/Podman.
*   Pass the repo as a `read-only` volume for Reviewer/Auditor containers.
*   Drop the `--auto` injection from the wrapper; explicitly map `ask` permissions to `deny` for non-interactive background runs.

**Phase 3: The MCP Transition**
*   Develop a custom, read-only MCP server specifically for the Reviewer/Auditor that provides safe abstractions (`search_code`, `get_ast`, `run_linter`).
*   Deprecate `bash` access for these roles entirely.
*   Once the MCP tools are stable, remove the `crosslink-guard` and `orchestrator-guard` TS plugins for these roles, as the OS-level and MCP-level boundaries will have made them redundant.

### Summary
The current document is a masterclass in adversarial review, but it is essentially an autopsy of a "bolt-on" security model. You have reached the end of the line for application-hook enforcement. To achieve the structural guarantees the EDASES program requires, you must push the enforcement **down the stack** to the OS/Kernel layer and push the interaction model **up the stack** to strict, capability-based MCP tools.
````

