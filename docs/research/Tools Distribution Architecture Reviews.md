Tools Distribution Architecture — One-Shot Reviews

---
ChatGPT:
Yes. My recommendation is **a hybrid centered on Option D, with one important addition from B**: treat Tools as a versioned source/distribution repository, but **do not force every artifact through the same distribution mechanism**.

The evidence in the briefing is unusually strong because the observed drift is not just a few accidental mismatches. The artifacts have diverged in *different directions*, and the oldest copy is sometimes labeled canonical. That is exactly what you would expect when the architecture permits multiple writable copies of the same logical artifact.

## 1. Diagnosis: copy-out really is the structural problem

I agree with the root diagnosis, with one qualification:

> **The problem is not merely "copies"; it is multiple writable authorities for the same logical artifact.**

A copied artifact can be perfectly safe if it is genuinely generated and nobody treats it as a source. The dangerous configuration is:

```text
Tools/foo        ──copy──> ASES/foo
       │
       ├─────────copy──> tripn/foo
       │
       └─────────copy──> live/foo
```

where all four locations can subsequently be edited.

That creates an information problem: after divergence, there is no mechanically knowable answer to "which one is correct?"

Your evidence demonstrates this particularly well:

* ASES has the newest guard implementation.
* the supposedly canonical Tools copy is oldest.
* the live wrapper is ahead of the repository wrapper.
* the deployed model plugin is ahead of its repository source.
* `plugin.ts` and `dynamic-models.ts` have separately evolved.

This isn't primarily a discipline failure. **Discipline is being asked to compensate for an architecture that permits ambiguity.**

The layer split is not the root problem either. Three repositories could coexist perfectly well if each artifact had exactly one authoritative locus and consumers had deterministic references/installations.

So I would phrase the diagnosis as:

> **The system lacks a single authoritative locus per artifact and a deterministic mechanism for deriving every consumer instance from that locus.**

That is more precise than "copy-out is bad," and it points toward the right architecture.

---

# 2. Option A — put everything into `crosslink`

This is attractive because it solves the problem very decisively.

### Strong arguments for A

The strongest argument is not actually "fewer files." It is:

> **`crosslink init` already has a working deployment model.**

The project already knows how to:

1. embed resources,
2. build them into an executable,
3. deploy them,
4. reproduce that deployment.

Extending that mechanism means you're not inventing another package manager.

It also gives a very strong consistency property:

```text
crosslink source
      ↓
   binary
      ↓
crosslink init
      ↓
consumer
```

There is no ambiguity about which version was installed.

For the crosslink-owned resources, I think this is clearly the right model.

### Strong arguments against A

The strongest objection is **ownership and release coupling**, not binary size.

A guard plugin or OpenCode model plugin is conceptually a reusable Tool. `crosslink` is a Rust application that happens to consume some of those things.

If you put them into the binary, you have implicitly declared:

> "The release lifecycle of this OpenCode plugin is the release lifecycle of crosslink."

That is a surprisingly consequential architectural decision.

You then get:

```text
change TypeScript plugin
    ↓
rebuild Rust binary
    ↓
install/update binary
    ↓
crosslink init
```

instead of:

```text
change Tool
    ↓
install Tool version
```

For an AI-agent infrastructure project whose tooling is likely to change rapidly, that coupling will become annoying.

### My judgment

**Good for crosslink-owned resources. Bad as the universal distribution architecture.**

I would actually use part of A:

> Keep hooks, commands, MCP resources, and crosslink-specific rules embedded in crosslink if crosslink genuinely owns them.

I would not make crosslink the warehouse for OpenCode/Claude tooling merely because it already has an embedding mechanism.

---

# 3. Option B — versioned Tools bundles

This is architecturally very sound.

The particularly good part is the distinction between:

```text
Tools release
       ↓
generated installation
       ↓
consumer
```

and:

```text
Tools/foo
       ↓
copied foo
       ↓
someone edits copied foo
```

The **pin** is valuable. It establishes an answer to:

> "Which version of the tooling is this consumer supposed to be running?"

That is much stronger than merely detecting that two files have different hashes.

I particularly agree with replacing the proposed runtime state machine with an installation invariant.

A runtime guard saying:

> "Your copy differs from Tools, therefore I am now in State 2 and will kill the session"

is treating a distribution problem as a runtime correctness problem.

Better:

> "This installation claims to be Tools version X. Is it actually a valid installation of X?"

That's an install/CI concern.

### The main weakness

I agree with the criticism that a full release/package ecosystem might be excessive for this fleet.

You have approximately:

* 3 methodology/layer repos,
* 1 client,
* 1 fork,
* 1 primary operator/machine.

You don't need npm-level infrastructure to achieve the important properties.

I'd therefore steal the **principles** from B without necessarily building its entire machinery.

Something as simple as:

```text
.tools-version
```

or:

```text
.tools-pin
```

plus a manifest generated from that exact Tools revision is probably enough initially.

### My judgment

**Excellent architectural principle; potentially overengineered implementation.**

I would incorporate B into D.

---

# 4. Option C — no copies, references only

This has the cleanest theoretical property.

If:

```text
consumer/foo → Tools/foo
```

then the entire class of "Tools/foo and consumer/foo have different contents" disappears.

That's genuinely elegant.

But I think the reviewers correctly identified that it is **too dependent on filesystem/tooling semantics that have not yet been established**.

The important questions aren't philosophical. They're empirical:

* Does OpenCode load a plugin through a symlink correctly?
* Does Claude's machinery tolerate the proposed arrangement?
* What happens in worktrees?
* What happens when the repository is moved?
* What happens in CI?
* What happens on another machine?
* Does `crosslink init` overwrite the same path?
* Can the Tools repository be absent while the consumer is being used?

If the answer to those questions is "yes, cleanly," C becomes extremely attractive.

But until tested, I wouldn't make the architecture depend on it.

There's also a conceptual issue with symlinks: they turn a **repository dependency** into a **filesystem dependency**.

That is often wonderful for a single developer machine and surprisingly awkward everywhere else.

### My judgment

**Best theoretical drift elimination, but not sufficiently portable as the primary architecture without successful experiments.**

I would test it, not adopt it blindly.

---

# 5. Option D — three artifact classes

This is the option I find most compelling.

The key insight is:

> **There isn't actually one distribution problem. There are several kinds of artifacts pretending to be one problem.**

That's important.

For example, a user-level OpenCode plugin is fundamentally different from a repository-local methodology rule.

Trying to make both obey:

```text
Tools → copied into repo
```

is what creates much of the awkwardness.

## Class 1: genuinely machine-global tooling

If `crosslink-guard.ts`, wrappers, and model plugins are truly identical across repositories on a machine, then **having one machine-level copy is superior to having four repository copies**.

That directly follows from your strongest empirical observation:

> the artifacts that exist only once stayed current.

That's an unusually useful architectural experiment already performed by the system itself.

The caveat is that the intended runtime loading semantics need testing.

## Class 2: repo-local materialized resources

Skills/hooks/commands/MCP resources often really do need to exist in a repository.

For those, copying isn't inherently wrong.

The important distinction is:

> **materialization, not source duplication.**

A generated copy is fine:

```text
Tools @ abc123
       ↓
   installer
       ↓
generated consumer files
```

provided the consumer files are not treated as independently authored source.

A pin plus generated manifest is a reasonable lightweight implementation.

## Class 3: layer-owned policy

This is absolutely right.

Rules and methodology policy should not be secretly overwritten by a tooling warehouse.

The distinction:

```text
Tools = capability
layer repo = policy
```

is architecturally healthy.

I'd go even further: **policy should be allowed to configure a capability without becoming a fork of the capability.**

That gives you a clean boundary.

### My judgment

**Best of the five as a conceptual architecture.**

It matches the actual semantics of the artifacts instead of imposing one distribution mechanism on everything.

---

# 6. Option E — managed copy-out

I would implement this **only as the immediate stabilization step**, not the destination.

The good part is that it is boring.

Boring is valuable right now because you have known correctness bugs. A complicated migration system introduced simultaneously with bug fixes is risky.

But I would specifically avoid investing too much in the proposed State 0 → State 1 → State 2 machinery.

The important invariant should eventually be:

```text
source/version → deterministic installation
```

not:

```text
installation → continuously self-policing runtime state machine
```

A hash manifest is useful.

A runtime warning can be useful during migration.

But a permanent runtime state machine is evidence that the underlying distribution mechanism still isn't trustworthy.

### My judgment

**Good migration architecture; poor final architecture.**

---

# 7. What I would actually build — Option F

I would call the resulting architecture **single-source, typed-locus distribution**.

It is essentially:

**D + the versioning discipline from B + the ownership boundary from A.**

Something like this:

```text
                         ┌──────────────────────┐
                         │       Tools          │
                         │ versioned source     │
                         └──────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
       machine-global       generated repo       explicitly-owned
          tooling              artifacts          crosslink payload
                │                   │                   │
                ▼                   ▼                   ▼
       ~/.local/bin       ASES / tripn / etc.       crosslink init
       ~/.config/...     pinned + generated
```

And independently:

```text
ASES policy ───────────→ ASES
tripn policy ──────────→ tripn
crosslink policy ──────→ crosslink
```

The critical rule would be:

> **Every artifact has exactly one source of authority. Consumers either reference it, install it, or generate it. They never become another source.**

That is the architectural invariant I would document.

---

# 8. I would also change one thing about "canonical Tools"

I would be careful with the phrase "Tools is canonical."

It is only meaningful if Tools is canonical **per artifact**.

For example:

| Artifact                         | Authority                     |
| -------------------------------- | ----------------------------- |
| OpenCode guard plugin            | Tools                         |
| CLI wrapper                      | Tools                         |
| model plugin                     | Tools                         |
| shared skill                     | Tools                         |
| layer methodology rules          | ASES                          |
| tripn application policy         | tripn                         |
| crosslink-specific embedded rule | crosslink                     |
| generated model cache            | generated from defined source |
| local machine configuration      | machine/user config           |

That prevents the warehouse from gradually becoming a second methodology repository.

---

# 9. The correctness bugs should be fixed independently

Yes, with one qualification: the **specific fixes should be independent**, but the *desired location* of the fixed code may change after the architecture decision.

### Hook precedence

Definitely fix immediately.

This is an actual semantic bug:

```text
blocked_git_commands
       ↓
checked first
       ↓
git merge rejected
```

even though the role-specific configuration says the orchestrator may perform it.

This isn't distribution drift; it's incorrect policy evaluation.

The correct precedence needs to be explicitly defined, e.g.:

```text
specific role/type policy
    overrides
global default policy
```

or whatever semantics the project actually intends.

I'd add a regression test so this cannot return.

### `plugin.ts` / `dynamic-models.ts`

Also fix independently.

Near-duplicate implementations of policy are another form of architectural drift, even if they happen to live in the same repository.

The best fix is not merely "sync them."

It is:

> **one implementation, one responsibility, one source.**

### `models-cache.json`

Treat this as generated state, not a manually maintained artifact.

The real question is:

> What is the deterministic source and regeneration operation?

Once that exists, the cache should be visibly generated and preferably disposable.

### `freeZenModels`

Also fix, but I would first decide whether it is:

* a manually curated policy list,
* a generated compatibility list,
* or a runtime discovery filter.

Right now it sounds like it has accidentally become all three.

That is why the UX is confusing.

---

# 10. One subtle issue: the drift detector itself can become drift

This is the strongest criticism I have of the interim plan.

You're proposing to add:

```text
manifest
sync script
state machine
promotion command
checks
```

to solve the problem.

Those are themselves new pieces of infrastructure that can diverge.

You could end up with:

```text
Tools
  ↓
sync-tooling.sh
  ↓
manifest
  ↓
consumer
  ↓
drift detector
```

and eventually discovering that the **drift detector's understanding of the distribution contract has drifted from the distributor**.

That's why I'd make the eventual system considerably simpler:

```text
Tools revision
     ↓
installer
     ↓
generated files
     ↓
verification
```

The fewer persistent mechanisms involved, the better.

---

# 11. Which option wins for this particular scale?

For a large fleet, I would lean much harder toward B/package-style distribution.

For this project, I think **D wins because the fleet is small and heterogeneous**.

The project has exactly the circumstances where D pays off:

* single primary operator,
* essentially one machine,
* several repositories,
* different artifact semantics,
* one existing user-level success case,
* an existing crosslink deployment mechanism,
* no need for enterprise-scale dependency distribution.

You don't need to solve "how do 10,000 machines consume this package?"

You need to solve:

> "How do I make it impossible for myself to accidentally maintain four different copies of the same thing?"

D answers that directly.

---

# 12. What I would do immediately

I would sequence the work like this:

### Phase 1 — stop the bleeding

Do the four correctness fixes now:

1. hook precedence;
2. consolidate model-plugin implementation;
3. establish deterministic model-cache regeneration;
4. repair/document whitelist semantics.

At the same time, reverse-sync the newest known implementations into Tools, but explicitly record which source won for each artifact.

### Phase 2 — establish ownership

Create an artifact-locus table in Tools/ASES that says, mechanically:

```text
artifact → owner → distribution mode
```

No artifact should be allowed to exist without an answer.

### Phase 3 — test the assumptions

Before migrating anything substantial, test:

* user-level OpenCode guard plugin loading;
* symlinked plugin loading;
* behavior with Tools moved to another path;
* clean checkout on another machine;
* worktree behavior;
* `crosslink init --force` behavior;
* whether crosslink embedding can cleanly accommodate only crosslink-owned resources.

### Phase 4 — implement D+B-lite

Use:

* **single user-level copies** for genuinely machine-global tools;
* **Tools commit pins + generated manifests** for repo-local materialization;
* **in-repo source** for layer-owned policy;
* **crosslink embedding** only for crosslink-owned resources.

Do not initially build a sophisticated release service.

### Phase 5 — remove transitional machinery

Once the new topology works, delete the old duplicate copies and the permanent runtime drift state machine.

The goal should be to make drift **impossible or immediately attributable**, rather than merely detectable after the fact.

---

# 13. Verification gaps: what I would require before committing

I'd rank the proposed experiments like this.

### Must-test

**1. User-level guard plugin loading**

This determines whether the most important part of D is actually viable.

Test:

* guard loads at user level;
* role detection still works;
* repository-specific configuration is respected;
* multiple repositories behave correctly;
* failure modes are sane.

**2. Symlinked plugin loading**

This determines whether C is worth retaining as an optional optimization.

Test both user-level and repo-level symlinks.

**3. `crosslink init --force` collateral effects**

This is critical regardless of the final architecture because crosslink currently participates in the deployment graph.

Establish exactly:

* what it overwrites;
* what it preserves;
* whether it can destroy generated/symlinked resources;
* whether its payload can be cleanly reduced.

### Strongly recommended

**4. Clean-machine reproduction**

Take a clean checkout and install everything from Tools at a specified revision.

If that isn't reproducible, you don't yet have a distribution architecture.

**5. Crosslink embedding feasibility**

Not merely "can Rust embed this?"

Test:

> Can we embed crosslink-owned resources without making Tools-owned resources implicitly crosslink-owned?

That is the actual architectural question.

### Useful but lower priority

**6. Worktree/relocation tests**

Particularly for C.

**7. Failure-mode testing**

Kill the install halfway through. Corrupt one generated file. Change the pinned revision. Remove Tools. See what happens.

Those tests reveal whether your "atomic" and "reproducible" claims are actually true.

---

# Bottom line

I would **not choose A, B, C, or E wholesale**.

I would choose **D as the architectural foundation, strengthened by B's version/pinning discipline and A's ownership principle**:

> **Tools owns reusable capabilities. Layer repositories own policy. Crosslink owns crosslink-specific embedded resources. Machine-global capabilities are installed once at user level. Repo-local capabilities are deterministically generated from a pinned Tools revision.**

The key invariant is:

> **One artifact, one authority, one installation mechanism.**

That is the real lesson from the drift evidence.

A's "single distribution channel" is too uniform.
B's "versioned distribution" is right but potentially too heavyweight.
C's "no copies" is elegant but currently rests on unverified tooling behavior.
D correctly recognizes that **different artifacts have different natural loci**.
E is the right temporary bridge, but not the destination.

So my recommendation is **Option F = D + lightweight B + selective A**.

And I would make one final architectural change to the interim plan: **don't spend much engineering effort making copy-out increasingly sophisticated.** Use `sync-tooling.sh` to get out of the current broken state, but design it explicitly as a migration mechanism toward the typed-locus architecture rather than as the next permanent subsystem.
---

---
Deepseek V4 Pro 0813:
## 1. Diagnosis check

The diagnosis is mostly correct, but it should be refined.

The evidence strongly supports “copy-out is structurally flawed” **when the copies are unmanaged, hand-editable, and have no unambiguous canonical source**. The fact that every artifact existing in N places drifted, while the one user-level single-copy artifact stayed current, is the strongest possible local evidence for this.

But the real problem is slightly more precise: **unmanaged, unchecked, ambiguous-source copy-out**. Copy-out itself is not inherently bad. Package managers, generated-file systems, and deploy scripts all copy files successfully. What is missing here is:

- a clear source of truth,
- a version/pin connecting consumer copies to that source,
- a checksum/manifest making divergence visible,
- a rule that consumer copies are generated artifacts, not editable sources.

So the layer split itself is not the cause. A sibling Tools warehouse plus three layer repos plus one client is a reasonable structure at this scale. The problem is the distribution mechanism between Tools and consumers.

I would therefore reject Option C’s conclusion that all copy-out must be eliminated. I would accept D’s classification: different artifacts need different loci and different mechanisms.

---

## 2. Option-by-option assessment

### Option A — Extend crosslink binary to embed everything

**Strongest argument for:**  
One channel, one source, one deploy command. If everything is embedded and `crosslink init` deploys it, drift becomes structurally impossible for those artifacts.

**Strongest argument against:**  
It makes crosslink the owner of OpenCode/Claude-specific tooling it was never meant to own. A change to a model plugin or wrapper then forces a Rust rebuild and binary reinstall. That couples unrelated release cadences and makes the development loop worse.

**Weak argument:**  
“Binary bloat” is a real but minor concern. The more important problem is ownership and release coupling.

**Verdict:**  
Not a good primary target. It would work, but it would create a badly shaped ownership boundary.

---

### Option B — Tools as a versioned distribution source

**Strongest argument for:**  
Reproducible, pinnable, auditable releases. Install/CI catches incomplete or tampered bundles before runtime. It prevents “live copy silently becomes canonical.”

**Strongest argument against:**  
For one operator, three layer repos, one client, and mostly text/TypeScript/bash artifacts, a full release-pipeline/bundle system is over-engineered. The consumer copies are still copies; you are managing them with more machinery rather than removing the drift pressure.

**Verdict:**  
Good discipline if the project grows to multiple operators or machines, but too heavy as the next step.

---

### Option C — Reference-based consumption, no copies

**Strongest argument for:**  
No physical copies means no copy drift by construction. It is conceptually the cleanest.

**Strongest argument against:**  
Symlinks are machine-absolute and break portability. Submodules have real UX costs with worktrees and branch switching. Most importantly, OpenCode plugin loading from symlinked/submodule paths is untested. `crosslink init` also regenerates `.claude` resources and can conflict with symlinked paths.

**Verdict:**  
Too risky and too operator-hostile at this stage. This should be tested later if ever.

---

### Option D — Three-class artifact locus

**Strongest argument for:**  
This is the most concrete and least invasive target. It uses the one proven non-diverged pattern in the current system: user-level single-copy artifacts. It also correctly observes that not every artifact belongs in a repo.

**Strongest argument against:**  
It depends on an untested assumption that guard plugins work identically when loaded from user-level config. If that fails, part of the model collapses and guard plugins must remain per-repo, which weakens the “single-copy” class.

**Verdict:**  
Best conceptual target, but it should be adopted conditionally and paired with a concrete migration path.

---

### Option E — Interim sync-tooling.sh as end state

**Strongest argument for:**  
Minimal, already reviewed, works today, and fixes the known correctness bugs.

**Strongest argument against:**  
It is still a managed copy-out system. Drift remains possible and is detected after the fact. The state machine and manifest become additional artifacts that themselves need maintenance. Five separate reviews already judged it interim, not final.

**Verdict:**  
Excellent migration vehicle, not a good end state.

---

## 3. Recommended architecture

### Recommendation: a hybrid of D and E, with lightweight B-style pinning

If forced to choose one existing letter, I would choose **D as the target**, but I would not adopt D without E as the migration path. I would also add a small pinning mechanism from B without adopting the full release-pipeline machinery.

This is effectively an **Option F**: classed source-of-truth plus generated materialization.

The project is a single-operator, single-machine setup with five relevant repos. The system should be optimized for that reality, not for a fleet. That argues strongly against submodules, symlinks, release bundles, and crosslink embedding everything.

---

## 4. Proposed target architecture

### Class 1: Machine-global single-copy artifacts

These should live at user level and be deployed from Tools.

Affected artifacts:

- `~/.local/bin/claude`
- `~/.local/bin/opencode`
- `~/.local/bin/crosslink-moe`
- `~/.config/opencode/plugins/plugin.ts`
- consolidated model plugin/dynamic model plugin
- guard plugins: `crosslink-guard.ts`, `orchestrator-guard.ts`, `rtk-guard.ts`

Tools is the canonical source.

Deployment:

- Add a `tools install --user` command/script.
- It copies the canonical files into user-level locations.
- It writes a user-level manifest, e.g. `~/.config/opencode/.tooling-manifest.json`.
- It sets executable bits where needed.
- The rule is: **edit in Tools, deploy to user level; never edit live.**

The guard-plugin move should be conditional:

- First verify that OpenCode loads user-level guard plugins identically.
- Verify that role enforcement still reads per-repo hook config correctly from the current working directory.
- If that fails, keep guard plugins as Class 2 generated per-repo artifacts.

This class is the highest-value change because the current system already proves it works: the one artifact that did not diverge was the user-level model-whitelist plugin.

---

### Class 2: Per-repo generated materialization

Some artifacts must exist inside a consumer repo for OpenCode/Claude/crosslink to load them.

Affected artifacts:

- shared skills from Tools
- any Tools-owned per-repo plugins or commands
- possibly guard plugins, if user-level loading is not viable

Mechanism:

- Keep `sync-tooling.sh`.
- Record a `.tools-pin` in each consumer repo containing the Tools commit hash used for sync.
- The script copies from the pinned Tools commit.
- It writes a generated `sha256` manifest, e.g. `.tooling-manifest.json`.
- The manifest is committed to the consumer repo.
- Generated files should have a clear header: `GENERATED FILE — DO NOT EDIT`.
- `sync-tooling.sh --check` verifies hashes and fails on mismatch.
- A guard plugin or pre-session hook may call `--check` and warn or fail.

I would **not** adopt the proposed State 0 → State 1 → State 2 promotion machine. At this scale, that is more ceremony than needed. Once the manifest is committed, a mismatch should simply mean “generated tree is dirty; run sync.” A hard fail in `--check` is sufficient.

---

### Class 3: Layer-owned policy

These stay in their repos and are never synced:

- `.crosslink/rules/`
- hook-config base
- agent definitions
- `.ases/` boundary design
- repo-specific OpenCode config

This preserves the layer ownership boundary.

---

### Class 4: Crosslink-owned embedded resources

For hooks/commands/MCP resources that crosslink already embeds:

- Treat the crosslink repo as the canonical source, not Tools.
- Do not store generated `.claude` snapshots in Tools as if they were source.
- Re-run `crosslink init` after crosslink binary updates.
- If useful, have `crosslink init` write a version marker so stale deployments are detectable.

This removes the confusion from item 7: Tools should not pretend to own resources that are actually owned by crosslink.

---

## 5. Migration steps

1. **Reverse-sync first:**  
   Move the newest guard plugins and live wrappers back into Tools. Make Tools the true canonical source.

2. **Fix correctness bugs immediately:**  
   - hook-config precedence
   - `plugin.ts` / `dynamic-models.ts` consolidation
   - models-cache regeneration
   - whitelist verification

3. **Implement user-level install:**  
   Add `tools install --user` for wrappers, model plugins, and guard plugins if verification passes.

4. **Remove per-repo copies of Class 1 artifacts:**  
   Once user-level install is working, delete the repo-local copies of wrappers, model plugins, and guard plugins.

5. **Add `.tools-pin` and generated manifests for Class 2:**  
   Update `sync-tooling.sh` to write and verify manifests. Commit manifests in each consumer repo.

6. **Define sync/init ordering:**  
   Make clear whether `sync-tooling.sh` runs before or after `crosslink init`, and document it.

---

## 6. Correctness bug fixes: scope check

The four correctness fixes are correctly scoped as independent of the architecture decision, but architecture determines where they must be applied and how many copies are affected.

- **Hook-config precedence:** Must be fixed in the canonical guard plugin. If guard plugins move to user-level, all repos receive the fix after one install. If they remain per-repo, the fix propagates through sync.
- **`plugin.ts` / `dynamic-models.ts` consolidation:** Should happen before any distribution decision; otherwise we risk propagating two already-diverged near-duplicates into more places.
- **models-cache regeneration:** Independent; needs a single regeneration mechanism. Location depends on where the model plugin lives.
- **Whitelist verification:** Independent; fix should land in the consolidated model plugin.

So: the bugs do not change the architecture choice, but the architecture choice changes how many copies need the fix and how the fix is deployed.

---

## 7. Verification gaps before committing

These should be executed-tested:

1. **User-level guard-plugin loading:**  
   Does OpenCode load guard plugins from `~/.config/opencode/plugins/` identically to repo-local plugins? Does role enforcement still read per-repo hook config?

2. **Symlink/submodule plugin loading:**  
   Only relevant if Option C is reconsidered later, but worth a quick test before final rejection.

3. **`crosslink init --force` collateral:**  
   What exactly does it overwrite or delete? Does it affect `.opencode/plugins/` or `.claude/skills/` in ways that conflict with sync?

4. **Crosslink binary embedding feasibility:**  
   Can `build.rs` embed and deploy TypeScript guard plugins/wrappers to user-level paths, or only repo-local paths? If it cannot write outside the repo, Option A cannot fully cover Class 1.

5. **Wrapper quoting and path handling:**  
   Especially spaces, tmux options, `CROSSLINK_AGENT_TYPE`, and fork-identity guard behavior.

6. **Sync script idempotency and manifest stability:**  
   Does repeated sync produce identical hashes? Are file modes and line endings stable?

7. **Models-cache regeneration:**  
   Can it be rerun cleanly and deterministically?

8. **Whitelist refresh behavior:**  
   Confirm newly added free models appear after refresh and dead entries are removed.

---

## 8. Final recommendation

I recommend the **D+E hybrid** described above:

- **D gives the correct target architecture.**
- **E gives the immediate migration path.**
- **A small `.tools-pin` plus generated manifest gives versioning without a full release system.**

I would not choose A, B, or C as the end state:

- A over-couples crosslink with OpenCode/Claude tooling.
- B over-builds distribution for a single operator.
- C introduces portability and plugin-loading risk.

The hybrid gives you:

- single-copy where the system already proves it works,
- generated pinned copies where repo-local artifacts are required,
- clear ownership for layer-local policy,
- no unnecessary release or state-machine machinery.

At this scale, that is the right balance.
---

---
Claude Sonnet 5 High:
Recommend Option D as the base, upgraded with Option C for the one artifact class where it's actually low-risk — not a full hybrid so much as D done properly, with a fast-follow verification step that lets you collapse the riskiest copy class into zero-copy where the evidence supports it. Reject A and B outright. Don't ship E as an end state, but ship its bug fixes this week regardless of which architecture wins.

**On the diagnosis (Q1):** "copy-out is structurally flawed" is close but imprecise, and the imprecision matters because it points different reviewers toward different fixes. The actual failure mode visible in your own evidence table isn't duplication — it's duplication with an undefined edit direction. Item 2 (CLI wrappers) didn't drift because someone forgot Tools existed; it drifted because a bug got fixed live under time pressure and never flowed back. That's not "copies are bad," that's "copies with no enforced single edit-direction and no verification step will drift the first time someone is in a hurry." The single-copy model-whitelist plugin didn't survive because copies are evil, it survived because there was only one place to edit, full stop. That reframing is why D beats E: D doesn't just detect drift after the fact (the warn→hard-fail state machine), it removes the ambiguity about where edits are allowed to happen in the first place.

**Why not A:** the binary-bloat argument against it is weak, but the coupling argument is real and disqualifying. Crosslink is a Rust CLI for issue tracking and orchestration; OpenCode plugins and model-provider whitelists are a different concern with a different release cadence and a different maintainer mental model. Forcing every plugin tweak through a Rust rebuild doesn't just add friction, it makes crosslink the accidental owner of tooling it has no reason to own. That's an ownership-boundary violation, not a performance one, and it'll cause exactly the kind of "who's supposed to touch this" confusion that caused the original drift.

**Why not B:** the generated-artifact discipline (never hand-edit a consumer copy, promote via a deliberate command) is the right idea and worth keeping — but wrapping it in a full versioned-release pipeline with lockfiles and compatibility metadata is infrastructure sized for a team publishing to unknown consumers, not a single operator syncing to three repos they personally control. You'd spend more effort maintaining the packaging system than the packaging system saves you.

**Why not C as a full replacement, but yes as a partial one:** eliminating copies entirely is the cleanest fix on paper, and it's actually low-risk for a chunk of the surface area — the CLI wrappers (`claude`, `opencode`, `crosslink-moe`) are plain executable scripts with no plugin-loader involved, so `~/.local/bin/opencode` can just be a symlink to `Tools/scripts/opencode` today, with no testing required, no ambiguity, no possibility of drift. The part of C that's genuinely risky is symlinking `~/.config/opencode/plugins/plugin.ts` and the guard plugins, because you don't actually know whether OpenCode's plugin loader resolves symlinked paths the same way it resolves real files — and the guard plugins are your permission-model enforcement layer, which is the worst place in the whole system to be running on an untested code path.

So the concrete recommendation: adopt D's three-class split as the permanent structure, but treat class 1 as two sub-cases instead of one. Wrappers get symlinked into Tools now — that's Option C, today, zero risk. Model plugins and guard plugins stay as D describes (install-from-Tools discipline, edit only in Tools, deploy by explicit command) until you've run a five-minute spike verifying symlinked plugin loading; if it works, promote them to symlinks too and class 1 disappears entirely as a copy-out problem. If it doesn't work, D's user-level single-copy-plus-discipline is still a real improvement over three divergent repo copies, so you haven't lost anything by trying. Class 2 (skills, hooks, commands, mcp) stays pinned copy-out with a generated sha256 manifest exactly as D describes — this is inherently repo-specific materialized content, and fighting `crosslink init`'s own embedded-resource deployment mechanism by trying to symlink these is what breaks in Option C as written. Class 3 (rules, hook-config base, agent definitions, `.ases/`) stays in-repo, never synced, no dispute there among any of the five reviewers.

**On the bug fixes (Q4):** correctly scoped as independent. The hook-config precedence bug is a logic error in how the plugin checks blocked-vs-gated lists — that's true no matter where the file lives. Models-cache regeneration and whitelist staleness are data-freshness problems, not distribution problems. Fix all four now in whatever copy is currently live, then let the distribution mechanism (whichever wins) propagate the fix once.

**Verification gaps, in the order they actually block a decision:**
1. Symlinked OpenCode plugin loading — this is the one gap that determines whether class 1 fully collapses to Option C or partially falls back to D. Test first.
2. User-level guard-plugin loading and role resolution — security-relevant, needs explicit testing (not just "the whitelist plugin worked fine") before guard plugins move user-level, since the four-role `by_type` resolution is exactly the thing that's newest in the ASES copy and least proven elsewhere.
3. `crosslink init --force` collateral — does it silently overwrite a symlinked `.claude` path, or does it error, or does it write through the symlink into Tools? This determines whether class-2 materialization and class-1 symlinks can coexist in the same repo without init corrupting one to fix the other.
4. Crosslink binary embedding feasibility — deprioritize; only worth spending time on if 1–3 come back bad enough that D+C stalls, since it's only relevant to Option A, which loses on ownership grounds independent of feasibility.
---

---
Gemini 3.6 Flash:
## Architectural Review & Recommendation

### 1. Diagnosis Check

**Is "copy-out is structurally flawed" the correct diagnosis?**

**Yes, but with an essential distinction.** The primary failure is not merely *copying* files; it is **unversioned, bidirectional copy-out without forced synchronization or an immutable single source of truth.**

In a single-operator environment, copy-out fails because human operations naturally follow the path of least friction: an operator fixes an issue where it manifests (in a downstream repo or local environment) and defers pushing it upstream. Without automated enforcement, drift is guaranteed.

The fundamental design flaw across the legacy setup is **mixed locality ownership**:

* **Artifacts that should be machine-global** (wrappers, provider plugins, guard hooks) were placed inside individual repositories.
* **Artifacts that should be repository-local** (rules, role configs) were partially embedded into shared binaries (`crosslink`).
* **Canonical sources** (`Tools`) were treated as advisory rather than as an immutable upstream source.

---

## 2. Evaluation of Options A–E

### Option A: Extend Crosslink Binary Embedding

* **Verdict:** ❌ **Over-Engineered & Poorly Coupled**
* **Pros:** Single deployment mechanism (`crosslink init`); eliminates runtime file drift within managed repos.
* **Cons:** Forces a Rust compilation step for quick TypeScript/Bash edits. Creates tight coupling between independent tooling domains (OpenCode/Claude tooling vs. Crosslink orchestration). Adding new scripts becomes high-friction.

### Option B: Tools as Versioned Bundle Distribution

* **Verdict:** ⚠️ **Valid for Teams, Over-Engineered for Single-Operator**
* **Pros:** Strict versioning, lockfiles, auditable, catches drift at CI/Install time.
* **Cons:** Introduces heavy release mechanics (versioning, packaging, lockfile management) for 3 local repos managed by one person.

### Option C: Reference-Based Consumption (Symlinks / Submodules)

* **Verdict:** ⚠️ **Fragile Boundaries & Operational Friction**
* **Pros:** Zero copy duplication; instant updates across all repos upon editing `Tools`.
* **Cons:** Submodules add heavy git workflow overhead (worktrees, head management). Symlinks break down across execution boundaries (containers, CI environments) and introduce untested path-resolution edge cases in tool environments.

### Option D: Three-Class Artifact Locus Classification

* **Verdict:** ✅ **Strongest Foundation & Correct Architecture**
* **Pros:** Resolves root cause by matching each artifact to its natural lifetime/scope. User-level execution for machine-global plugins is proven to work (`freeZenModels`). Minimizes the scope of what actually needs to be synced down to repos.
* **Cons:** Requires verification of user-level guard plugin loading in OpenCode/Claude environments.

### Option E: Interim `sync-tooling.sh` Plan

* **Verdict:** ⚠️ **Necessary Short-Term Step, Insufficient End State**
* **Pros:** Solves immediate synchronization needs; low risk; fixes active bugs.
* **Cons:** Maintains duplicate physical files that will eventually re-diverge without strict state enforcement.

---

## 3. Recommended Hybrid Architecture (Option D + Lightweight Pinning)

The optimal strategy combines **Option D (Artifact Classification)** with **Option B’s single-command deterministic release discipline**.

```
                           +------------------------+
                           |     Tools Repository   |
                           |   (Canonical Source)   |
                           +-----------+------------+
                                       |
              +------------------------+------------------------+
              |                                                 |
   [ Machine-Global Artifacts ]                       [ Per-Repo Materialized ]
              |                                                 |
              v                                                 v
  ~/.local/bin/ (Wrappers)                          sync-tooling.sh --pin <HASH>
  ~/.config/opencode/plugins/ (Guards/Models)                   |
              |                                                 v
              v                                    ASES / EDASES / tripn-astro
  Affects all execution contexts                     .claude/ & .opencode/

```

### Artifact Locus Plan

| Class | Artifact Types | Location / Mechanism | Divergence Control |
| --- | --- | --- | --- |
| **Class 1: Machine-Global** | Wrappers (`claude`, `opencode`), Model plugins (`plugin.ts`), Guard plugins | `~/.local/bin/`<br>

<br>`~/.config/opencode/plugins/` | **Single-copy at runtime.** Installed via `Tools/install.sh`. |
| **Class 2: Repo Materialized** | Shared Skills, Hooks, MCP configs | `.claude/` / `.opencode/` via `Tools/sync-tooling.sh` | **Deterministic Copy-Out.** Synced from pinned `Tools` commit hash; generated `.tools-manifest.json` tracks integrity. |
| **Class 3: Repo-Owned Policy** | Layer Rules (`.crosslink/rules/`), Role Agents, Hook Configurations | Strictly in-repo (`ASES`, `EDASES`, etc.) | **Zero Syncing.** Never managed or touched by `Tools`. |
| **Class 4: Binary Embedded** | Core orchestration logic, Session state engine | Embedded in `crosslink` binary via Rust `build.rs` | **Built-in.** Strictly limited to Crosslink-internal utilities. |

---

## 4. Execution Roadmap & Verification Requirements

```
Phase 1: Fix Independent Bugs ──► Phase 2: Verification Tests ──► Phase 3: Migration to Option D

```

### Phase 1: Independent Bug Fixes (Execute Immediately)

These issues must be resolved in `Tools` regardless of final architectural adjustments:

1. **Hook-Config Precedence (Item 6):** Ensure per-role overrides (e.g., `by_type.orchestrator.gated_git_commands`) evaluate prior to top-level `blocked_git_commands`.
2. **Plugin Consolidation (Item 3):** Merge `plugin.ts` and `dynamic-models.ts` into a single canonical module in `Tools/plugins/plugin.ts`. Include grok-ban (#347) and whitelist updates.
3. **Cache & Whitelist Maintenance (Items 4 & 5):** Rebuild `models-cache.json` generation scripts; remove stale entries from `freeZenModels`.

---

### Phase 2: Technical Verification Gaps (Required Before Phase 3)

Execute testing on the following 4 gaps before finalizing the Option D migration:

1. **User-Level Guard Plugin Loading:**
* **Test:** Move `crosslink-guard.ts` to `~/.config/opencode/plugins/`. Execute a session in a consumer repo lacking repo-level guards.
* **Verify:** Verify if OpenCode loads and enforces role permissions globally from the user-level path.


2. **Crosslink Hook/Command Overrides:**
* **Test:** Deploy a local `.claude/hooks` file while `crosslink init` runs.
* **Verify:** Confirm whether `crosslink init --force` overwrites repo-specific custom hooks or leaves non-embedded hooks intact.


3. **Symlink Compatibility (Fallback Check):**
* **Test:** Symlink `~/.config/opencode/plugins/crosslink-guard.ts` -> `~/projects/Tools/plugins/crosslink-guard.ts`.
* **Verify:** Confirm if OpenCode resolves module imports and module relative paths correctly without silent failures.


4. **Binary Embedded Limits:**
* **Test:** Inspect `crosslink/build.rs` payload size and build times when altering embedded skills/hooks.
* **Verify:** Confirm compilation overhead remains under acceptable thresholds.



---

### Phase 3: Deployment Procedure (Transition to Final State)

1. **Upstream Reverse Sync:** Move the newest updates from `ASES` (`crosslink-guard.ts`) and `~/.local/bin` (`claude`, `opencode`) back into `Tools`.
2. **Global Tooling Installation:** Run `Tools/install.sh` to link/copy Class 1 binaries and user-level plugins into `~/.local/bin/` and `~/.config/opencode/plugins/`.
3. **Downstream Clean Up:** Remove duplicated Guard plugins and Model plugins from consumer repository trees (`ASES`, `tripn-astro`).
4. **Execution of Sync Script:** Run `sync-tooling.sh --target <REPO>` to deploy Class 2 artifacts alongside generated manifest hashes.
---

---
GLM-5.2
# Architectural Review: AI-Agent Tooling Distribution Drift

## 1. Diagnosis Check

"Copy-out is structurally flawed" is the right *direction* but the wrong *precision*. The evidence supports a sharper diagnosis:

**The system has multiple physical copies of each artifact with no defined canonical source, no enforced flow direction, and no reconciliation mechanism.** The number of copies multiplies the drift surface; the absence of flow direction means edits propagate chaotically (sometimes live→Tools, sometimes Tools→live, sometimes ASES→both).

The proof is in the drift table itself:

- **Item 1**: Tools copy is the *oldest* (33.5 KB). ASES is newest (42.1 KB). If Tools were truly canonical, Tools would be newest. The actual flow is live→ASES→Tools (Tools is the *sink*, not the source).
- **Item 2**: `~/.local/bin/claude` is ahead of Tools and *has fewer bugs* than Tools. The live copy is the de-facto source; Tools is a stale backup.
- **Item 3**: Deployed `~/.config/opencode/plugins/plugin.ts` (133 lines, Aug 10) is ahead of Tools (51 lines, Jul 9). Same pattern.
- **Item 5 (whitelist)**: The single non-drifted artifact. It lives in exactly one place (user-level). It cannot drift from itself.

The single-copy precedent is the strongest evidence in the document. It proves that the drift mechanism is *physical multiplicity*, not copy-out per se. Copy-out with a clear source, one-way flow, and reconciliation works fine (package managers do it). Copy-out without those is "edit wherever and hope."

The layer split is not the cause. The fork's init payload is a separate problem. The missing discipline is a *symptom* — there's no discipline to enforce because there's no defined flow to follow.

**Refined diagnosis**: the structural fix is to reduce the number of physical copies per artifact to the minimum that the loading mechanism requires, and to make the flow direction explicit and one-way. Options C and D address this directly; A replaces copies with a single binary; B adds versioning to copies without reducing them; E manages copies without reducing them.

---

## 2. Pros/Cons Per Option

### Option A — Embed everything in the crosslink binary

**Strongest argument FOR**: `crosslink init` already distributes hooks/skills/commands/mcp/rules without drift. This is a *proven* mechanism in this exact project. One channel, one binary, one init.

**Strongest argument AGAINST**: Item 7 in the drift table. The init-deployed snapshots are gitignored on-disk copies that **already differ from the binary's current embedded resources**. So the embed-and-init model *has already drifted* in this project. "Drift becomes structurally impossible" is contradicted by the project's own evidence. The binary's embedded resources can fall behind Tools (or ahead of it) just as easily as any other copy.

**Secondary concerns**:
- Coupling: a 1-line TypeScript plugin change forces a Rust rebuild + binary release + re-init across all repos. For a single operator, this dev loop (edit → `cargo build` → `cargo install` → `crosslink init` in each repo) is real friction for a TypeScript/bash change.
- Category confusion: crosslink is an issue-tracking/orchestration CLI. Making it the distribution channel for OpenCode plugins and Claude wrappers is accidental ownership expansion.
- If Tools remains the "source for the binary," you've moved the copy problem, not eliminated it.

**Verdict**: attractive in theory, contradicted by the project's own evidence (item 7). The "single channel" argument is real but the "drift impossible" claim is falsified.

---

### Option B — Versioned distribution bundles

**Strongest argument FOR**: reproducibility and auditability. If the project grows beyond a single operator/machine, pinned bundles with lockfiles are the industry-standard answer. Install-time failure detection is strictly better than runtime drift detection.

**Strongest argument AGAINST**: scale mismatch. The fleet is 3 layer repos + 1 client + 1 fork = ~5 destinations, all on one machine, operated by one person. A release pipeline with manifests, checksums, compatibility metadata, and lockfiles for what is mostly markdown/bash/TypeScript is heavy machinery for a small fleet. The ceremony of "promote/import to create a new Tools release" for every plugin tweak will either be skipped (reintroducing drift) or become a bottleneck.

**Secondary concerns**:
- Still copies — pinned copies are still copies. Versioning adds detectability, not elimination.
- Requires CI to enforce "generated output is dirty → fail." Does this project have CI? If not, B's main enforcement mechanism has nothing to hook into.
- "Consumer copies are generated artifacts, never hand-edited sources" is a discipline requirement — the same kind of discipline that the current system lacks. Adding versioning doesn't make the discipline self-enforcing.

**Verdict**: correct architecture for a larger fleet; over-engineered for this one. Valuable as a *future direction* if the project scales, not as the current end-state.

---

### Option C — Reference-based consumption (symlinks/submodules)

**Strongest argument FOR**: drift is eliminated *by construction*. There is literally one file. No script, no manifest, no state machine, no ceremony. The single-edit-point model matches the single-copy precedent (whitelist works because it's single-copy; symlinks make everything single-copy). This is the most *elegant* solution.

**Strongest argument AGAINST**: the critical assumptions are untested, and several are likely to break:
- **OpenCode plugin loading from symlinked paths**: untested. If OpenCode resolves symlinks before loading, fine. If it doesn't (some plugin loaders use `realpath` and reject symlinks, or cache based on resolved path), the whole option collapses.
- **`crosslink init` conflict**: init regenerates `.claude/hooks`. If you symlink `.claude/hooks/some-hook` → `Tools/hooks/some-hook`, then `crosslink init` either overwrites the symlink (defeating C) or fails (breaking init). This is a *direct conflict* with an existing mechanism.
- **Machine-absolute paths**: symlinks encode `/home/user/projects/Tools/...`. Break on any other machine, in containers, in CI, after a directory rename. For a single-machine setup this is tolerable today but fragile.
- **Submodule UX**: detached HEADs, worktree complications, partial-clone issues. Known to be confusing even for experienced git users.

**Verdict**: structurally the purest, practically the riskiest. The untested assumptions are load-bearing — if any one fails, the option doesn't partially work, it fails completely. Worth *testing* the assumptions (especially symlink plugin loading) because if they work, C becomes the best long-term answer for Class 1 artifacts. But don't commit to C without those tests.

---

### Option D — Three-class artifact locus

**Strongest argument FOR**: it's the only option that *respects artifact heterogeneity*. Wrappers, model plugins, and guard plugins are machine-global (they configure a user's environment, not a repo's). Skills, hooks, and commands are per-repo (they need to be materialized where the repo lives). Rules are layer-owned (they're policy, not tooling). Forcing all three classes through one mechanism (A's binary, B's bundles, C's symlinks) is wrong for at least one class. D says: use the right mechanism per class.

**Strongest argument FOR (second)**: the user-level precedent is *proven in this project*. The model-whitelist plugin lives at `~/.config/opencode/plugins/` and is the only non-drifted artifact. This is not theory — it's evidence. D generalizes the pattern that already works.

**Strongest argument AGAINST**: the user-level guard-plugin loading is *untested*. The whitelist works at user-level, but guard plugins might be loaded differently (they might need to be in the project's `.opencode/plugins/` to intercept the right hooks). This is the same kind of untested assumption that weakens C — but it's a *narrower* assumption (one plugin type, not the whole symlink chain).

**Secondary concerns**:
- "Never edit live" discipline is required for Class 1. The user-level plugins could still be edited directly, drifting from Tools. But this is a *smaller* discipline surface than the current system (one location per artifact vs. N locations).
- Class 2 still uses copy-out (pinned). Drift is detectable (checked-in manifest shows up in git diffs) but not eliminated.
- Three mechanisms to learn (user-level install, pin-based materialization, layer-owned policy) is more cognitive load than one.

**Verdict**: the most surgical and evidence-based option. The untested assumption (user-level guard-plugin loading) is testable in isolation and, if it fails, only affects one artifact class (guard plugins fall back to Class 2 pinned copy-out). This is graceful degradation — unlike C, where a failed assumption breaks the whole option.

---

### Option E — Interim sync-tooling.sh (default)

**Strongest argument FOR**: ships today, fixes the correctness bugs, minimal new machinery, already reviewed twice. The State 0→1→2 graduated enforcement is a reasonable drift-detection mechanism. For a project that needs stability *now*, this is the lowest-risk option.

**Strongest argument AGAINST**: five independent reviewers all judged it interim. The state machine + manifest are themselves artifacts that need maintenance (who watches the watchmen?). "Managed copy-out" still requires "always edit Tools, never edit live" discipline — the same discipline the project has repeatedly failed to maintain. The reverse-sync is a one-time fix; future drift can recur because the flow direction isn't enforced, just detected after the fact.

**Verdict**: acceptable as a *stabilization* measure (stop the bleeding), not as an end-state. If the project ships E and never revisits, drift will recur — just more slowly, and detected rather than silent.

---

## 3. Recommended Option

**Recommend D, implemented in phases, with E's sync-tooling.sh repurposed as D's Class 2 mechanism, and the bug fixes done immediately and independently.**

### Why D over the others (for this scale)

The project is single-operator, single-machine, 5 destinations. At this scale:
- A's dev-loop penalty (Rust rebuild for TS changes) is real friction that will cause the operator to skip the rebuild and edit live — recreating drift.
- B's release ceremony will be skipped for small changes — recreating drift.
- C's untested assumptions are load-bearing and several are likely to conflict with `crosslink init`.
- E doesn't fix the structural problem.
- D uses the one pattern *already proven* in this project (user-level single-copy), narrows the copy-out surface to only the artifacts that genuinely need per-repo materialization, and degrades gracefully if a key assumption fails.

### Why not a hybrid

A hybrid of A+B+C+D sounds comprehensive but is actually "multiple mechanisms for the same artifact class," which is the *current problem* (each artifact has N copies via N mechanisms). The right move is to pick D's *classification* (which is a hybrid of mechanisms, but per-class, not per-artifact) and commit to it. D is already a hybrid — it's three mechanisms for three classes. Adding more mechanisms doesn't help.

The one place where a hybrid adds value: **test C's symlink loading for Class 1 artifacts as a future upgrade path.** If symlinks work for OpenCode plugin loading, Class 1 can upgrade from "install from Tools to user-level" (still a copy) to "symlink user-level → Tools" (true single-source). This is a *staged* migration, not a hybrid architecture.

### Implementation phases

**Phase 0 — Fix the bugs (immediately, independent of architecture):**
- Fix hook-config precedence (item 6): check `by_type` overrides before the global block. This is a pure logic fix.
- Consolidate `plugin.ts` and `dynamic-models.ts`: pick one, delete the other, port missing features.
- Build a `regenerate-models-cache.sh` that fetches current models and writes `models-cache.json`.
- Fix the whitelist: remove dead entries, add missing free models, add a verification step.

These are independent of where the files ultimately live. Fix them in their current locations; the architecture migration will move the fixed files.

**Phase 1 — Reverse-sync (one-time, as the interim plan proposes):**
- Push ASES guard plugins → Tools.
- Push live `~/.local/bin/*` → Tools.
- Push live `~/.config/opencode/plugins/*` → Tools.
- Tools is now the true source (momentarily).

**Phase 2 — Verification tests (before committing to D):**
- Test: does OpenCode load guard plugins from `~/.config/opencode/plugins/` (user-level)? The whitelist works there, but guard plugins may have different loading behavior.
- Test: does `crosslink init --force` overwrite `.claude/hooks`? What exactly does it touch? (Needed to confirm D's Class 2 doesn't conflict with init.)
- Test: does `crosslink init` deploy guard plugins, or are those loaded independently? (Determines whether guard plugins are Class 1 or Class 2.)
- If user-level guard-plugin loading fails: guard plugins fall back to Class 2 (pinned copy-out per repo). D still works; it just has two copy-out classes instead of one.

**Phase 3 — Implement D's three classes:**
- **Class 1 (machine-global)**: Write `install-user-tooling.sh` that copies Tools → `~/.local/bin/` and `~/.config/opencode/plugins/`. This is a one-way install (Tools → user-level), run deliberately after Tools changes. The user-level location is the *live* copy; Tools is the *git-tracked upstream*. For a single operator, this matches the actual workflow (you edit the live plugin, then snapshot to Tools — OR you edit Tools and install to live; pick one direction and stick to it).
- **Class 2 (per-repo)**: `sync-tooling.sh` (from the interim plan) but *narrowed* to only skills/hooks/commands/mcp. Checked-in `.tools-pin` (Tools commit hash) + checked-in sha256 manifest. Git diffs expose drift natively — no separate state machine needed.
- **Class 3 (layer-owned)**: rules/, hook-config base, agent definitions, .ases/ (when implemented). Never synced. Explicitly excluded from `sync-tooling.sh`.

**Phase 4 (optional, future) — Upgrade Class 1 to symlinks if Phase 2 tests pass:**
- Replace `install-user-tooling.sh` (copy) with `link-user-tooling.sh` (symlink).
- Now Class 1 is true single-source (drift impossible by construction).
- This is C applied to one class, where it's safe.

---

## 4. Undisputed Bug Fixes

The four correctness fixes are **correctly scoped as independent of the architecture choice** — with one nuance:

| Bug | Independent? | Nuance |
|-----|-------------|--------|
| hook-config precedence (item 6) | Yes | Pure logic bug. Fix the order of checks. Wherever the config file lives, the fix is the same. |
| plugin.ts / dynamic-models.ts consolidation | Yes (fix); No (locus) | The *fix* (consolidate into one file) is architecture-independent. The *locus* (where the consolidated file lives) depends on D's class assignment. Fix now in current location; migrate later. |
| models-cache regeneration | Yes (fix); No (mechanism) | The *fix* (build a regeneration script) is architecture-independent. The *trigger* (when/how regeneration runs) depends on where the cache lives and who calls it. Under D, it's a user-level script run after provider changes. Under A, it'd be a build-time step. |
| whitelist verification | Yes (fix); No (locus) | Same as models-cache. The *fix* (verify whitelist against actual free models) is architecture-independent. The *locus* depends on architecture. |

**The architecture decision changes which bugs matter in one way**: under Option A (binary embedding), the "regeneration mechanism" for models-cache becomes a build-time concern (the binary embeds the cache at build time, so regeneration must happen before `cargo build`). This makes the regeneration *more* coupled to the release process, not less. Under D, regeneration is a standalone user-level script — simpler to maintain and run independently. This is a minor point in D's favor.

**Bottom line**: fix all four bugs now, in their current locations, regardless of architecture. The architecture migration will move the fixed files; the fixes themselves don't change.

---

## 5. Option F

There is an option the five reviewers did not propose. I'll call it:

### Option F — Accept reality: live locations are canonical; Tools is the versioned snapshot

The interim plan's "reverse-sync" is treated as a one-time fix. But the drift table shows that the *live* copies are consistently *ahead* of Tools — they are the de-facto sources. Tools is consistently the *last* to receive updates. This is not a bug; it's a reflection of the actual workflow: the operator edits the live plugin (because that's what's loaded), tests it, and then (sometimes) remembers to push it back to Tools.

**Option F formalizes this**: the live user-level locations (`~/.local/bin/`, `~/.config/opencode/plugins/`) are the *canonical sources*. Tools is the *git-tracked snapshot* — a versioned backup that the operator pushes to after deliberate changes, via a `tools-snapshot.sh` script that copies live → Tools and commits. The flow is strictly one-way: live → Tools (snapshot), never Tools → live (install). Per-repo artifacts (skills, hooks) remain pinned copy-out from Tools (because they need to be materialized in each repo).

**How F differs from D**: D says "Tools is canonical, install to user-level." F says "user-level is canonical, snapshot to Tools." For a single-operator single-machine setup, F is more honest about the actual workflow. It eliminates the "reverse-sync" concept entirely — there's no "reverse" because the live location is the source.

**Pros**:
- Matches the *actual* flow (no discipline inversion needed — the operator already edits live).
- One-way flow (live → Tools) is simpler to maintain than D's install direction (Tools → live), which requires the operator to *not* edit live and instead edit Tools and re-install.
- Tools becomes an auditable release log, not a primary source — which matches how it's actually used.
- No "install" step for Class 1 artifacts — the live location IS the artifact.

**Cons**:
- If the operator gets a second machine, there's no "install from Tools" mechanism (Tools is a snapshot, not a source). You'd need to add a restore-from-snapshot script — which is basically D's install step. So F degrades to D when the single-machine assumption breaks.
- Tools is no longer "canonical" in the traditional sense. If someone clones Tools expecting to get the current tooling, they get the last snapshot, which may be behind live. This could confuse future contributors.
- The live locations are not git-tracked (they're in `~/.local/bin/` and `~/.config/`), so there's no version history for the *actual* source. Only the Tools snapshot has history, and it's only as current as the last snapshot.

**When F is better than D**: when the single-machine assumption holds and the operator's workflow is "edit live, test, snapshot." This matches the evidence in the drift table.

**When D is better than F**: when the operator's workflow should be "edit Tools, install to live" (more disciplined, more reproducible, scales to multiple machines).

**My judgment**: F is more honest about the *current* reality, but D is better as a *target* state. F is the right *interim* — formalize the current workflow (live is source, Tools is snapshot) instead of pretending Tools is canonical. Then, as discipline improves, migrate to D (Tools is source, install to live). The migration from F to D is straightforward: add an `install-from-tools.sh` script and start using it; the snapshot direction can coexist as a backup mechanism.

**However**: F is a *refinement* of D's Class 1, not a fundamentally different architecture. Both agree that user-level is the right locus for machine-global artifacts. They differ only in flow direction. For the purposes of this review, D and F are the same option with a different flow-direction policy. I'll treat them as one: **D, with the flow direction to be determined by a Phase 2 workflow audit.**

---

## 6. Verification Gaps

Before committing to D (or any option), the following claims should be executed-tested:

| # | Gap | Why it matters | How to test |
|---|-----|----------------|-------------|
| 1 | **User-level guard-plugin loading** | D's Class 1 depends on guard plugins loading from `~/.config/opencode/plugins/`. The whitelist works there, but guard plugins may have different loading behavior (hook interception vs. model filtering). | Copy a guard plugin to `~/.config/opencode/plugins/`, remove the per-repo copy, start an OpenCode session, verify the guard fires on a gated command. |
| 2 | **`crosslink init --force` collateral** | D's Class 2 (pinned copy-out for hooks/skills/commands/mcp) must not conflict with `crosslink init`. If init overwrites `.claude/hooks` unconditionally, the pinned copy-out is redundant or conflicting. | Run `crosslink init --force` in a test repo, diff `.claude/` before and after, document exactly what it touches. |
| 3 | **Crosslink binary embedding feasibility** (for Option A, if reconsidered) | Can `build.rs` embed TypeScript plugins and deploy them via init? The hooks/skills/commands are already embedded, but plugins may need different handling (they're loaded by OpenCode, not by crosslink). | Prototype embedding one plugin in the binary and deploying via init. |
| 4 | **Symlink plugin loading** (for future Phase 4 upgrade) | If symlinks work for OpenCode plugin loading, Class 1 can upgrade from copy to reference (true single-source). | Symlink `~/.config/opencode/plugins/plugin.ts` → `Tools/plugins/plugin.ts`, start a session, verify the plugin loads. |
| 5 | **`crosslink init` vs. symlinked `.claude/hooks`** (for Option C) | If init overwrites symlinks, C is doomed for hooks. If init follows symlinks, C might work. | Symlink one hook, run `crosslink init --force`, check if the symlink survives. |
| 6 | **Does the project have CI?** | Option B's "fail at CI time" is moot without CI. D's checked-in manifest is most useful when CI verifies it. | Check if any repo has `.github/workflows/` or equivalent. |
| 7 | **Is the single-machine assumption durable?** | If the operator might get a second machine, symlinks (C) break and user-level (D) needs an install step. This affects whether F (live is source) or D (Tools is source) is the right flow direction. | Ask the operator. |
| 8 | **What's the actual frequency of tooling changes?** | If wrappers/plugins change weekly, the dev loop matters (favors D/F). If monthly, the dev loop is less critical (A/B more acceptable). | Check git log in Tools and in the live locations for change frequency. |
| 9 | **Does `crosslink init` deploy guard plugins?** | If guard plugins are part of the init payload, they're Class 2 (per-repo, pinned). If they're loaded independently by OpenCode, they're Class 1 (user-level). This determines D's class assignment. | Inspect the binary's embedded resources list and the init deployment manifest. |
| 10 | **Item 7 scope**: how far have the init-deployed snapshots drifted from the binary's embedded resources? | If the drift is small (a few files), it's manageable. If large, the init mechanism itself has a drift problem that undermines Option A's "proven mechanism" claim. | Diff `Tools/.claude/hooks+commands+mcp` against a fresh `crosslink init` output. |

Gaps 1, 2, and 9 are **blocking** for D — they determine whether D's Class 1 is viable and how the classes are assigned. Gaps 4, 5 are **non-blocking** (they affect the future Phase 4 upgrade, not the initial implementation). Gaps 6, 7, 8 are **contextual** (they inform the choice but don't block it).

---

## 7. Final Recommendation

**Recommend Option D (three-class artifact locus), implemented in phases, with the correctness bugs fixed immediately and independently.**

### Summary of reasoning

1. **The diagnosis is about physical multiplicity, not copy-out per se.** The single-copy precedent (user-level whitelist) proves that reducing copies to one eliminates drift by construction. D does this for Class 1 (machine-global artifacts) and narrows the copy surface for Class 2 (per-repo artifacts).

2. **D is the only option grounded in evidence from this project.** The user-level whitelist is the one artifact that doesn't drift. D generalizes this pattern. A, B, C, and E are theoretical constructions that either contradict the project's evidence (A: init payload already drifted), over-engineer for the scale (B), rely on untested assumptions (C), or manage without fixing the structural problem (E).

3. **D degrades gracefully.** If user-level guard-plugin loading fails (the key untested assumption), guard plugins fall back to Class 2 pinned copy-out. The architecture still works; one artifact class moves to a different mechanism. Compare to C, where a failed assumption breaks the entire option.

4. **The bug fixes are independent.** Fix hook-config precedence, consolidate plugin.ts/dynamic-models.ts, build models-cache regeneration, and fix the whitelist now, in their current locations. The architecture migration moves the fixed files later.

5. **The flow direction (Tools→live vs. live→Tools) should be decided by a workflow audit (Phase 2), not assumed.** The drift evidence suggests live is the de-facto source (live copies are consistently ahead). Formalizing this (Option F's "live is canonical, Tools is snapshot") may be more honest for the current single-operator setup. But D's "Tools is canonical, install to live" is the better target state for reproducibility. The operator should choose based on whether the single-machine assumption is durable.

6. **Phase 4 (symlink upgrade for Class 1) is the path to C's elegance without C's risk.** If the Phase 2 verification tests confirm that OpenCode loads plugins from symlinked paths, Class 1 can upgrade from "copy from Tools to user-level" to "symlink user-level → Tools." This achieves C's drift-impossible property for the artifacts where it matters most, without the machine-specificity problem (because user-level symlinks point to a repo that's already on the same machine).

### What to do tomorrow

1. Fix the four correctness bugs (item 6, plugin consolidation, models-cache regeneration, whitelist verification). These are independent of architecture and should not wait.
2. Reverse-sync live → Tools (one-time, as the interim plan proposes).
3. Run the Phase 2 verification tests (gaps 1, 2, 9 from §6).
4. Based on test results, implement D's three classes.
5. Retire the interim plan's state machine for Class 1 (single-copy artifacts don't need drift detection). Keep a narrowed version for Class 2 (pinned copy-out with checked-in manifest — git diffs are the drift detector).

This is not the most elegant architecture (C is more elegant). It is not the most scalable (B is more scalable). It is not the simplest (E is simpler). It is the one that **fixes the structural problem with the least risk, grounded in evidence from this project, with a clear upgrade path if the verification tests succeed.**
---

---
Kimi Instant:
 This is a well-constructed briefing. Below is an independent architectural review addressing each discussion question, followed by a final recommendation.

---

## 1. Diagnosis check

**"Copy-out is structurally flawed" is the correct primary diagnosis.** The evidence is conclusive: every artifact with N copies has drifted; every artifact with 1 copy has not. This is not a discipline failure or a one-time execution mistake — it is an emergent property of the architecture. When an operator edits a live copy to fix a bug (e.g., the `~/.local/bin/claude` wrapper), the local fix is rational, immediate, and rewarded. The global inconsistency is deferred, invisible, and only punished later. No amount of documentation overrides this incentive structure.

However, the diagnosis can be sharpened: the root cause is not merely "copy-out," but **copy-out without an enforced, verifiable single source of truth.** The copies have no provenance metadata, no generation boundary, and no CI gate. The system relies on human memory to propagate edits, which is the exact mechanism that has already failed.

The layer split itself is *not* the problem. The repos are correctly bounded (research, methodology, execution, warehouse, client). The problem is the distribution mechanism between the warehouse (Tools) and its consumers.

---

## 2. Pros / cons per option

### Option A — Extend crosslink binary
- **Strongest argument:** It structurally eliminates drift by reducing the distribution channel to one binary and one command (`crosslink init`). This is elegant in theory.
- **Weakest / fatal argument:** It violates separation of concerns. Crosslink is a Rust CLI for issue tracking and orchestration; it should not own OpenCode plugins, Claude wrappers, or model policies. The dev loop — edit a TypeScript plugin → rebuild a Rust binary → re-init a repo — is unacceptable for iterative tooling development. It turns crosslink into an accidental monolith.

### Option B — Versioned bundles
- **Strongest argument:** Immutable bundles, checksums, and lockfiles are the theoretically correct way to distribute artifacts. Catching tampering at install/CI time is robust.
- **Weakest argument:** It is over-engineered for a single-operator, single-machine fleet of ~5 repos. A release pipeline, bundle format, and compatibility metadata for a handful of shell scripts and TypeScript guards is like using Kubernetes to run a personal blog. The cost of the machinery exceeds the cost of the drift it prevents. It also still leaves copies in consumer repos; it just manages them better.

### Option C — Reference-based consumption (submodules / symlinks)
- **Strongest argument:** It is the only option that structurally eliminates physical copies, which is the actual source of drift. Single edit point, zero propagation burden.
- **Weakest argument:** Submodules are notoriously painful even for solo operators (worktree issues, detached HEAD state, accidental commits to the submodule rather than the parent). Symlinks are machine-absolute and break on CI, containers, or any second machine the operator might use. Most critically, OpenCode/Claude plugin loading from symlinked paths is **untested** and could fail due to load-path resolution or sandboxing assumptions. The conflict with `crosslink init` overwriting `.claude/` is a real, unhandled collision.

### Option D — Three-class artifact locus
- **Strongest argument:** It is the only option that **explains the evidence.** The user-level `plugin.ts` (model whitelist) is the sole non-drifted artifact precisely because it is single-copy at user-level. This is not a coincidence; it is a natural experiment proving the hypothesis. The classification is concrete, respects the actual physics of where artifacts live, and is the least invasive.
- **Weakest argument:** Class 2 still involves copy-out (pinned, but still copy-out). The "never-edit-live" discipline remains a human requirement. The user-level loading assumption for guard plugins is strong but unverified.

### Option E — Interim `sync-tooling.sh`
- **Strongest argument:** It works today, has been adversarially reviewed twice, and fixes the correctness bugs. It is the safest short-term choice.
- **Weakest argument:** It institutionalizes drift. The warn → hard-fail state machine is complexity spent *managing* a structural problem rather than *preventing* it. It is "managed decay," not a solution. The manifest and state machine are new artifacts that will themselves require maintenance.

---

## 3. Recommended option

For this project's scale — **single operator, single machine, 3 layer repos + 1 client + 1 fork** — I recommend a **hybrid of Option D (as the architectural foundation), Option C (for Class 1 implementation), and Option B's generated-artifact discipline (for Class 2 enforcement).**

Call this **Option D+**.

### Implementation

| Class | Artifact examples | Locus | Mechanism |
|-------|-------------------|-------|-----------|
| **1. Machine-global, single-copy** | Wrappers (`claude`, `opencode`), model plugins (`plugin.ts`, `dynamic-models.ts`), guard plugins (`crosslink-guard.ts`) | User-level: `~/.config/opencode/plugins/`, `~/.local/bin/` | **Symlinks** to the Tools repo working tree (e.g., `~/.config/opencode/plugins/crosslink-guard.ts` → `~/projects/Tools/plugins/crosslink-guard.ts`). For a single-machine operator, absolute symlinks are safe and eliminate copy-out entirely. |
| **2. Per-repo materialized** | Skills, hooks, commands, MCP (`.claude/`, `.opencode/skills/`) | Consumer repo, but **generated, never hand-edited** | A `.tools-pin` file (Tools commit hash) + a `tools-materialize` script that uses `git show <pin>:<path>` from the Tools repo to write files. A `.tools-manifest` (sha256) is checked into the consumer repo so `git status` immediately exposes drift. A **pre-commit hook** rejects commits that modify materialized files. |
| **3. Layer-owned policy** | `rules/`, hook-config base, agent definitions, `.ases/` | Consumer repo, native | Never synced. Layer repos own these outright. |

### Crosslink fork
Strip all OpenCode/Claude-specific resources from the `crosslink init` embedded payload. Crosslink should embed **only** crosslink-native resources (its own rules, crosslink-specific skills). The fork should not be the distribution channel for generic AI-agent tooling.

### Why this hybrid?

- **Class 1 via symlinks (Option C)**: The operator's single-machine constraint makes symlink fragility (machine-absolute paths) a non-issue. Symlinks are simpler than "install discipline" (which is just copy-out with a different target). They make Class 1 single-copy by construction, matching the proven model-whitelist pattern.
- **Class 2 via pin + manifest (Option B's discipline, without the pipeline)**: Some artifacts must physically exist in `.claude/` or `.opencode/skills/` for tool discovery. For these, a git-commit pin is the lightest possible version lock. The pre-commit hook enforces generated-artifact discipline without requiring a full CI infrastructure.
- **Option D's classification**: The three-class split is correct because different artifacts have different binding constraints. Wrappers belong at user-level; `.claude/` configs belong in-repo; policy belongs to the layer.

### Why not pure Option C?
Symlinking the entire `.claude/` directory tree is too blunt. `crosslink init` expects to write there, and Claude may resolve relative paths from the symlink target rather than the link location. Option D's classification correctly identifies that only machine-global artifacts can be safely symlinked; per-repo tool discovery directories must be materialized.

### Why not pure Option D?
Pure Option D's Class 1 says "move to user-level... with Tools as the versioned upstream (install-from-Tools discipline, never edit-live)." But "install discipline" is still a manual copy-out step! The operator must remember to copy after editing. A symlink removes the step entirely.

---

## 4. Undisputed bug fixes

The correctness fixes are **correctly scoped as independent of the architecture choice.** Fix them immediately:

- **Hook-config precedence** (global `blocked_git_commands` overriding per-role `gated_git_commands`): This is a logic bug in the guard plugin. It exists regardless of whether the plugin lives in Tools, ASES, or `~/.config/`.
- **Plugin consolidation** (`plugin.ts` vs `dynamic-models.ts`): This is a code organization bug.
- **Models-cache regeneration**: This is a missing build/refresh step.
- **Whitelist verification**: This is stale data.

Fix these in the **live copies first** (to stop the bleeding), then propagate via the chosen architecture. The architecture decision changes *how* you propagate, not *whether* you fix the bugs.

---

## 5. Option F — what the reviewers missed

The five reviews did not fully exploit the **single-operator, single-machine** constraint. They treated the problem as if it needed to scale to a team or CI environment, which led them to reject symlinks (Option C) as too fragile and embrace heavy machinery (Option B) as "correct."

The novel insight is: **for one person on one machine, symlinks are not fragile — they are the simplest possible correct solution.** The reviewers proposed Option D but stopped short of using symlinks for Class 1, defaulting instead to "install discipline" (a euphemism for managed copy-out). Option D+ closes that gap.

A more radical Option F would be to **investigate whether OpenCode and Claude support a user-level project configuration overlay** — i.e., a `~/.config/opencode/projects/<repo>/` directory or similar. If the tools support this, even Class 2 artifacts (skills, hooks) could become user-level single copies, and the per-repo `.claude/` directories could be eliminated entirely. This is worth a quick check of the OpenCode/Claude documentation, but it should not block the D+ decision.

---

## 6. Verification gaps (priority order)

Before committing to Option D+, test these claims in this order:

1. **User-level guard-plugin loading** (blocks Class 1). Move `crosslink-guard.ts` to `~/.config/opencode/plugins/`, open a layer repo in OpenCode, and verify:
   - The plugin loads at session start.
   - It correctly reads and enforces the repo-specific hook-config (the `by_type` resolution).
   - The four-role permission model functions identically to the in-repo copy.

2. **Symlink resolution in OpenCode/Claude** (blocks Class 1 implementation). Symlink `plugin.ts` from `~/projects/Tools/plugins/` to `~/.config/opencode/plugins/`. Verify OpenCode follows the symlink and loads the file without path-resolution errors.

3. **`crosslink init --force` collateral** (blocks crosslink payload reduction). In a test repo, run `crosslink init --force` with a stripped-down payload (no OpenCode/Claude resources). Verify it does not overwrite or delete existing symlinks or materialized files in `.claude/` and `.opencode/`.

4. **Crosslink binary embedding feasibility** (low priority). Only relevant if Option A is revisited, which I do not recommend.

If **#1 or #2 fails**, fall back to Option D's original Class 1: single copy at user-level, but updated via a lightweight `tools-install` script (copy, not symlink). This is slightly weaker but still correct. If **#3 reveals destructive behavior**, adjust `crosslink init` to skip paths that contain a `.tools-managed` marker file.

---

## Final recommendation

**Adopt Option D+ (Three-class locus with symlinks for machine-global artifacts and git-pinned generated artifacts for per-repo materialized files).**

It is the only option that:
1. **Explains the existing evidence** (the non-drifted user-level whitelist);
2. **Eliminates copy-out where physically possible** (Class 1 via symlinks);
3. **Controls the remaining copy-out with verifiable provenance** (Class 2 via `.tools-pin` + manifest + pre-commit hook);
4. **Respects the actual binding constraints** of each artifact class;
5. **Avoids over-engineering** (no release pipeline, no binary bloat, no submodule UX tax);
6. **Works within the stated constraints** (single operator, single machine, repo-of-repos).

Execute the four correctness bug fixes **immediately and independently**. Then execute the verification gaps in the order listed. If the symlink tests pass, implement Class 1 with symlinks; if they fail, fall back to single-copy-at-user-level with an install script. Either path is superior to the interim copy-out model.
---

---
Qwen3.8-Max
## Executive recommendation

I would **not choose Option E as the end state**. It is a reasonable emergency stabilization measure, but it is still a copy-out system with better alarms.

I would also **not adopt Option A as the general architecture**. It solves one kind of drift by turning `crosslink` into a universal package manager, which creates ownership, cadence, and coupling problems that are worse than the original drift problem.

The best architecture for this project’s actual scale — single operator, single machine, three layer repos, one client repo, one fork — is a **hybrid**, with **Option D as the organizing principle**, **Option C as the preferred materialization mechanism where it can be executed-tested**, **Option B’s invariants in a lightweight form**, and **Option E only as the migration bridge**.

Put differently:

> **Recommended: Option D — three-class artifact locus — implemented as “symlink/user-level first, pinned generated copies where necessary, minimal lockfile/checksum discipline, and no runtime-copy drift state machine as the primary control.”**

The core rule should become:

> **Every shared artifact has exactly one writable source. Everything else is either a link, a generated artifact, or layer-owned policy. If a file can be edited in more than one place, the architecture is broken.**

---

# 1. Diagnosis check

## 1.1 Is “copy-out is structurally flawed” the right diagnosis?

Yes — but I would sharpen it.

The problem is not merely that files are copied. Copying is sometimes unavoidable, especially when a runtime expects files to exist in a particular project-local path. The deeper problem is that the current system has:

1. **Multiple writable copies** of the same artifact.
2. **No enforced direction of flow** from canonical source to deployed copy.
3. **No clear distinction between source files and generated files.**
4. **No reliable pinning of which upstream version a consumer is supposed to have.**
5. **Two distribution mechanisms** — Tools and `crosslink init` — overlapping without clear ownership.
6. **Live mutation** of deployed files, especially wrappers and plugins.
7. **No cheap, routine promote path** for when a live copy legitimately becomes newer than the canonical copy.

So the more precise diagnosis is:

> **The system lacks artifact authority and unidirectional distribution. Copy-out drifts because copies are treated as sources.**

The evidence supports this strongly. The briefing’s root observation is important:

> Every artifact that exists in N places has drifted. The single-copy artifacts stayed current.

That is not a coincidence. It is an architectural signal.

## 1.2 Is the real problem missing discipline?

Partly, but discipline is not a sufficient answer.

A system that requires perfect human discipline is fragile. If the easiest way to make the current session work is to edit the live file, the live file will eventually become the source. That is what happened with the wrappers and model plugins.

The architecture should make the correct action easier than the incorrect action:

- If a wrapper needs a fix, the operator should edit Tools and run one install/link command.
- If a guard plugin needs a feature, the change should land in Tools, then be materialized.
- If a live copy is newer, there should be an explicit `promote` operation, not an implicit assumption.

So: **discipline is necessary, but the architecture must make discipline easy.**

## 1.3 Is the layer split itself the problem?

No. The layer split is not the core problem.

The research/methodology/engine separation is reasonable. The repo-of-repos intention is also reasonable. The problem is that shared tooling sits awkwardly between:

- Tools as canonical warehouse,
- crosslink binary embedded resources,
- layer-repo local copies,
- user-level live files,
- client-repo local copies.

That is an ownership and distribution problem, not a layering problem.

## 1.4 One important challenge to the settled structure

The briefing says the repo-of-repos structure is settled, but it is explicitly open to challenge. I would not challenge the existence of the layers. I would challenge this specific point:

> If Tools is the canonical source of tooling used by the layers, keeping Tools completely outside the monorepo may preserve exactly the cross-repo atomicity problem that causes drift.

For a single-operator, single-machine environment, this is manageable with symlinks or a pin file. But if Tools changes frequently in coordination with methodology changes, having Tools in a separate repo means every meaningful tooling change may require cross-repo synchronization.

I am not saying Tools must be inside the monorepo. I am saying:

- If Tools remains separate, you need a pin/lockfile discipline.
- If that discipline becomes painful, consider bringing Tools into the monorepo or using a workspace-level meta-repo.

For now, Tools can remain a sibling warehouse, but only if the distribution mechanism is made explicit.

---

# 2. Option-by-option analysis

## Option A — Extend the crosslink binary to embed everything

### What it proposes

Move guard plugins, wrappers, agents, and other shared artifacts into the `crosslink` binary as embedded resources. `crosslink init` becomes the single distribution channel.

### Strongest arguments for

1. **Single distribution channel.**  
   There is something attractive about one command that materializes the shared environment.

2. **Structural drift reduction for embedded artifacts.**  
   If the binary is the only source and `init` is the only deployment path, copies cannot drift independently of the binary version.

3. **Reuses an existing mechanism.**  
   `crosslink init` already exists and already deploys resources.

4. **Atomicity by rebuild.**  
   A new binary version corresponds to a new tooling snapshot.

### Strongest arguments against

1. **Wrong ownership boundary.**  
   `crosslink` is a Rust CLI for issue tracking, orchestration, sessions, and repo initialization. It should not become the accidental owner of OpenCode-specific plugins, Claude wrappers, model policy, and methodology-adjacent guard logic.

2. **Bad release-cadence coupling.**  
   A small change to a shell wrapper or TypeScript plugin would require a Rust binary rebuild and redeployment. That is too heavy for iterative tooling work.

3. **Binary becomes a package manager.**  
   This turns `crosslink` into a general-purpose tooling distributor. That is a much larger responsibility than repo initialization.

4. **User-level artifacts are awkward.**  
   Wrappers belong in `~/.local/bin`. Model plugins belong in `~/.config/opencode/plugins`. Making `crosslink init` write into user-global locations is possible but dangerous. It would need careful permissions, idempotence, and conflict handling.

5. **It does not solve policy drift.**  
   Layer-owned configs, hook-config, rules, and role policies still need separate handling.

6. **It hides drift inside binary snapshots.**  
   The current item 7 problem — gitignored init-deployed snapshots differing from binary resources — shows that embedding alone does not guarantee clarity. If the binary embeds resources, their source still needs to be visible, versioned, and reviewable.

### Weakest argument in favor

The claim that this is “simpler than the interim plan” is weak. It appears simpler only because it hides complexity inside the binary. In practice, it transfers tooling distribution complexity into crosslink’s build, release, and init logic.

### Verdict

**Reject as the general architecture.**

Use embedding only for resources that are genuinely part of `crosslink` itself:

- crosslink rules defaults,
- crosslink-specific hooks,
- crosslink-specific commands,
- crosslink-specific MCP server definitions,
- initialization scaffolding.

Do **not** put general OpenCode/Claude/model-policy tooling into the crosslink binary merely to solve drift.

---

## Option B — Tools as a versioned distribution source with immutable bundles

### What it proposes

Tools publishes immutable bundles with manifests, checksums, compatibility metadata, and lockfiles. Consumers pin a bundle version. Installation is generated and atomic. Consumer copies are generated artifacts.

### Strongest arguments for

1. **Versioning and auditability.**  
   You can answer: “Which tooling version is this repo supposed to have?”

2. **Install-time failure instead of runtime drift.**  
   This is the right place to catch problems.

3. **Prevents silent live-canonical drift.**  
   A live copy cannot become canonical unless deliberately promoted into a new Tools release.

4. **Good long-term scaling path.**  
   If the project later has CI, containers, multiple machines, or more client repos, this becomes more attractive.

### Strongest arguments against

1. **Over-engineered for current scale.**  
   A full immutable release pipeline is probably too much machinery for one operator, one machine, and three layer repos.

2. **Still produces copies.**  
   Unless combined with symlinks or references, bundle installation still materializes files.

3. **Requires enforcement.**  
   Generated-artifact discipline only works if CI or local checks fail when generated files are dirty.

4. **Adds packaging overhead for small artifacts.**  
   Much of the content is markdown, shell scripts, TypeScript plugins, and JSON configs. A formal release system may add more friction than value.

### Best part of Option B

Even if you do not adopt full immutable bundles, you should adopt the **invariant**:

> A consumer’s materialized tooling state must match a pinned upstream version, and divergence should be detected at install/check time, not discovered accidentally during agent operation.

That invariant can be implemented cheaply with:

- a Tools commit pin,
- a sha256 manifest,
- a `tools doctor` command,
- a rule that generated files must not be hand-edited.

### Verdict

**Do not adopt full Option B now.**

Adopt **B-lite**:

- pin Tools commit,
- generate manifest,
- verify installed/materialized state,
- fail when dirty or mismatched.

Keep full immutable bundles as a future option if the fleet grows.

---

## Option C — Reference-based consumption, no copies

### What it proposes

Consumers reference Tools directly using symlinks or git submodules. For example:

```text
ASES/.opencode/plugins/crosslink-guard.ts -> Tools/plugins/crosslink-guard.ts
~/.local/bin/opencode -> Tools/scripts/opencode
~/.config/opencode/plugins/plugin.ts -> Tools/plugins/plugin.ts
```

### Strongest arguments for

1. **Eliminates physical copies.**  
   This is the cleanest structural answer to drift.

2. **Excellent fit for single-machine use.**  
   Since this is currently single-operator and single-machine, symlinks are much less risky than they would be in a large distributed team.

3. **Minimal machinery.**  
   No package registry, no release pipeline, no heavy sync system.

4. **Single edit point.**  
   Editing Tools immediately updates the consumer environment.

5. **Fits the observed evidence.**  
   The artifacts that stayed current were the ones with effectively one live locus.

### Strongest arguments against

1. **Runtime loading behavior is untested.**  
   This is the critical gap. OpenCode, Claude, and related tools may not load plugins, skills, hooks, or commands correctly through symlinks.

2. **Portability is poor if symlinks are checked into repos.**  
   A symlink pointing outside the repo assumes a particular filesystem layout.

3. **Crosslink init may conflict with symlinks.**  
   If `crosslink init` regenerates `.claude` hooks or commands, it may clobber links.

4. **Submodules have UX costs.**  
   Especially with worktrees, submodules are often annoying. Given the project’s apparent preference to avoid submodules, symlinks are the more plausible version of Option C.

5. **Version pinning is not automatic.**  
   A symlink to Tools does not by itself record which Tools commit the consumer was validated against. That needs a pin/lockfile.

### Important refinement

Do not use absolute symlinks checked into repos if you can avoid it.

Better patterns:

1. **Local link creation script**:

   ```text
   tools link
   ```

   creates relative symlinks or user-level links appropriate for the machine.

2. **Checked-in manifest instead of checked-in symlinks**:

   The consumer repo records:

   ```json
   {
     "tools_commit": "...",
     "artifacts": {
       ".opencode/plugins/crosslink-guard.ts": "symlink:Tools/plugins/crosslink-guard.ts"
     }
   }
   ```

   Then `tools doctor` verifies that the actual local state matches.

3. **Use symlinks for user-global artifacts**:

   ```text
   ~/.local/bin/opencode -> ~/projects/Tools/scripts/opencode
   ~/.config/opencode/plugins/plugin.ts -> ~/projects/Tools/plugins/plugin.ts
   ```

   This is very attractive if the runtime accepts it.

### Verdict

**Option C should be the preferred implementation mechanism wherever executed tests prove it safe.**

For this project’s scale, symlinks are probably the best drift-prevention mechanism. But they must be validated before becoming the architecture.

---

## Option D — Three-class artifact locus

### What it proposes

Classify artifacts by where they must live and choose the mechanism per class:

1. **Machine-global, single-copy artifacts**  
   Wrappers, model plugins, possibly guard plugins. Live user-level copy is the runtime locus; Tools is upstream.

2. **Per-repo deploy-time materialized artifacts**  
   Skills, hooks, commands, MCP files. Pinned copy-out or submodule-like materialization.

3. **Layer-owned policy**  
   Rules, hook-config, agent definitions, `.ases/` boundary. Never synced.

### Strongest arguments for

1. **It matches reality.**  
   Not all artifacts have the same correct home. A single distribution mechanism for everything is too coarse.

2. **It uses the only proven non-diverged precedent.**  
   The user-level model-whitelist plugin remained current because it had one live locus.

3. **It respects ownership.**  
   Policy stays layer-owned. Shared infrastructure lives in Tools. Crosslink-specific resources stay with crosslink.

4. **It is concrete and low-invasiveness.**  
   It does not require turning crosslink into a universal distributor or building a full release pipeline.

5. **It allows different mechanisms per artifact.**  
   This is important because wrappers, plugins, skills, hooks, and rules have different runtime expectations.

### Strongest arguments against

1. **It depends on untested assumptions.**  
   Especially:
   - user-level loading of guard plugins,
   - plugin precedence between user-level and project-level,
   - symlink loading,
   - OpenCode path-resolution behavior.

2. **It still requires a materialization mechanism.**  
   Class 2 still needs either symlinks, pinned copies, or packages.

3. **It requires discipline.**  
   “Never edit live” must be enforced by tooling and habit.

4. **It may require moving files that currently live in repos.**  
   That migration has to be done carefully.

### Why Option D is the best base architecture

Option D is the only option that begins with the right question:

> What is the correct locus of this artifact?

Instead of asking:

> How do we synchronize all copies?

or:

> How do we embed everything in one binary?

That makes it the most architecturally sound.

### Verdict

**Adopt Option D as the architectural frame.**

But implement it with Option C where possible and Option B-lite where copies are unavoidable.

---

## Option E — Interim sync-tooling.sh plan

### What it proposes

Tools becomes canonical by reverse-sync. A sync script copies canonical files into consumers. Drift detection uses sha256 manifests and a guard-plugin state machine.

### Strongest arguments for

1. **It is implementable now.**
2. **It has already survived review.**
3. **It fixes immediate correctness bugs.**
4. **It reduces drift likelihood.**
5. **It does not require untested symlink/user-level behavior.**

### Strongest arguments against

1. **It institutionalizes copies.**
2. **It detects drift rather than eliminating it.**
3. **The state machine becomes another artifact to maintain.**
4. **Runtime drift detection is late.**
5. **It still relies on the operator not editing live copies.**
6. **The sync script and manifest are themselves a distribution system that can drift.**

### Weakest argument in favor

“Already approved” is not a strong architectural argument. It is a strong schedule argument. Approval means it is acceptable as a bridge, not that it is the right destination.

### Verdict

**Use E only as the migration path.**

Do not ship E as the final architecture.

---

# 3. Recommended architecture

I recommend the following hybrid:

> **Option D as the model, Option C as the preferred materialization mechanism, Option B-lite for pinning and verification, and Option E only as the transition plan.**

Call this:

> **Canonical-source, locus-based distribution with link-first materialization.**

---

# 4. Core principles

## Principle 1: One writable source per artifact

Every shared artifact must have exactly one place where it is edited.

For most shared tooling, that source should be Tools.

For crosslink-specific resources, that source should be the crosslink fork.

For methodology policy, that source should be the layer repo.

## Principle 2: Deployed copies are generated or linked

If an artifact appears in a consumer repo or user-level config, it should be one of:

- a symlink,
- a generated file,
- a pinned installed copy,
- a layer-owned policy file.

It should never be a hidden second source.

## Principle 3: Direction of flow is explicit

The flow should be:

```text
Tools source
  -> promote/import when live changes are intentional
  -> install/link/materialize
  -> consumer runtime locus
```

Never:

```text
edit live copy
  -> forget to upstream
  -> drift
```

## Principle 4: Prefer links over copies on this machine

Because the current environment is single-operator and single-machine, symlinks are likely the simplest correct mechanism.

But this must be tested.

## Principle 5: Use checksums and pins for anything materialized

Where copying is unavoidable, the consumer should have:

```text
.tools-pin
.tools-manifest.json
```

containing:

- Tools commit SHA,
- artifact list,
- expected sha256 hashes,
- materialization mode,
- crosslink version if relevant.

## Principle 6: Detect problems at install/check time, not primarily at runtime

The guard plugin self-check can exist as a secondary safety net, but the primary checks should be:

- `tools doctor`,
- pre-session quick check,
- pre-commit check for dirty generated files,
- CI check if/when CI exists.

---

# 5. Artifact-by-artifact recommendation

## 5.1 Guard plugins

Current state: three divergent copies. ASES is newest. Tools is oldest.

### Recommended classification

Guard plugin code is shared infrastructure, but its configuration is layer/client policy.

Therefore:

- **Plugin code:** Tools.
- **Hook-config / role policy:** layer-owned.
- **Runtime loading locus:** preferably user-level if OpenCode supports it; otherwise project-local generated link/copy.

### Recommended action

1. Merge the ASES guard plugin features into Tools.
2. Make per-role `by_type` resolution configuration-driven if possible.
3. Remove consumer-specific logic from the plugin code where possible.
4. Install the canonical plugin user-level if tests pass.
5. If user-level loading fails, materialize into consumer repos as a generated artifact.
6. Fix the precedence bug in the plugin and/or config schema.

### Important design point

The fact that `git merge` appears in both role-gated and globally blocked lists is not merely a config accident. It is a sign that the policy schema needs clearer precedence rules.

The fix should not be only “remove `git merge` from one list.”

Add a validation rule:

> A command must not be present in both a hard-block list and a role-gated list unless an explicit precedence annotation exists.

Better still:

- global blocked list means hard-block for everyone;
- role-gated list means role-specific gating;
- overlap is rejected by validation.

---

## 5.2 CLI wrappers

Current state: live wrappers are ahead of Tools.

### Recommended classification

CLI wrappers are **machine-global, single-copy artifacts**.

They should not live in repos as editable copies.

### Recommended locus

```text
~/.local/bin/claude
~/.local/bin/opencode
~/.local/bin/crosslink-moe
```

### Recommended source

```text
Tools/scripts/claude
Tools/scripts/opencode
Tools/scripts/crosslink-moe
```

### Recommended materialization

Prefer symlink:

```text
~/.local/bin/claude -> ~/projects/Tools/scripts/claude
```

If symlinks cause problems, use an installer that copies from Tools and verifies checksum.

### Recommended rule

Never edit live wrappers.

If a live wrapper must be patched urgently:

1. Patch it live only as an emergency.
2. Immediately run an explicit promote/import operation.
3. Reinstall from Tools.
4. Verify checksum.

---

## 5.3 Model plugins

Current state: Tools is behind live config. `plugin.ts` and `dynamic-models.ts` have diverged.

### Recommended classification

Model plugins are **machine-global, single-copy artifacts**.

### Recommended locus

```text
~/.config/opencode/plugins/
```

### Recommended source

Tools.

### Recommended action

1. Consolidate `plugin.ts` and `dynamic-models.ts` into one canonical plugin.
2. Import the live Aug 10 behavior into Tools.
3. Remove duplicate plugin variants.
4. Install from Tools to user-level config.
5. Make `models-cache.json` and whitelist generated artifacts.
6. Add a regeneration command.

### models-cache and whitelist

The stale whitelist is not just a bug; it is a policy failure.

A whitelist that silently blocks newly available free models is a UX trap.

I recommend one of two policies:

#### Policy A: Discovery-first, blocklist for bad models

Use dynamic discovery as primary. Maintain only:

- blocked providers,
- blocked models,
- known-bad entries.

This avoids stale allowlists hiding new models.

#### Policy B: Curated whitelist with mandatory refresh validation

If a whitelist is required, then:

- it must be generated by a command,
- it must be validated against current provider/model discovery,
- dead entries must be removed automatically or flagged,
- staleness must be visible.

Do not keep a manually curated whitelist that silently acts as a fail-closed gate.

---

## 5.4 Skills

Current state: two shared crosslink skills are intended to be canonical in Tools.

### Recommended classification

Skills are shared tooling, but they are consumed project-locally by the agent runtime.

### Preferred mechanism

If OpenCode/Claude can load skills through symlinks:

```text
ASES/.claude/skills/foo -> Tools/skills/foo
```

If not:

```text
ASES/.claude/skills/foo
```

as a generated pinned copy from Tools.

### Important conflict

If `crosslink init` currently writes skills, decide ownership:

- If the skill is crosslink-specific, source belongs in crosslink.
- If the skill is general Tools-owned, crosslink should not overwrite it.

Do not allow both Tools and crosslink to own the same deployed path.

---

## 5.5 Hooks, commands, MCP servers

Current state: gitignored snapshots deployed by `crosslink init`, no canonical git source, on-disk copies differ from binary resources.

This is one of the most important structural problems.

### Recommendation

Every deployed resource must have a visible source in one of two places:

1. **Crosslink source tree** if it is crosslink-owned.
2. **Tools source tree** if it is general shared tooling.

Binary embedding may be a transport mechanism, but it should not be the only source of truth.

### For crosslink-owned resources

Keep them in the crosslink repo. Embed them during build if desired. `crosslink init` may deploy them.

But:

- source files must be visible in git,
- deployed output must carry version info,
- `init` should not silently clobber local policy.

### For Tools-owned resources

Move them to Tools.

Then either:

- symlink them where possible,
- or materialize pinned copies using the Tools installer.

`crosslink init` should either:

- not manage Tools-owned paths, or
- delegate to the Tools installer.

---

## 5.6 `.crosslink/rules/`

Current plan excludes rules from sync. I agree.

### Recommended classification

Layer-owned policy.

### Rule

Never sync `.crosslink/rules/` from Tools.

`crosslink init` may provide defaults for new repos, but existing rules should not be overwritten by generic sync.

---

## 5.7 Hook-config

### Recommended classification

Layer-owned policy.

Do not sync hook-config wholesale.

However, hook-config should be validated by a shared validator.

The validator can live in Tools or crosslink, but the config itself belongs to the layer/client repo.

### Required fix

Fix the precedence bug immediately.

Specifically:

- remove the false overlap between `blocked_git_commands` and role-gated lists, or
- change plugin precedence so explicit role gating can override global block where intended, or
- make such overlap invalid by schema.

I prefer the third option:

> The schema should reject ambiguous precedence.

---

## 5.8 `.ases/`

Current state: aspirational, not implemented.

### Recommendation

Do not distribute or sync `.ases/` until it is real.

When it becomes real, classify it carefully:

- If it is policy/boundary owned by ASES, keep it layer-owned.
- If it contains generated integration artifacts, mark them generated.
- Do not let it become another copy-out surface.

---

# 6. Proposed implementation model

## 6.1 Tools becomes the source warehouse, not a sync target

Tools should contain:

- canonical wrapper scripts,
- canonical model plugin,
- canonical guard plugin code,
- canonical shared skills,
- canonical Tools-owned hooks/commands/MCP resources if applicable,
- manifests,
- installer/doctor commands,
- model cache/whitelist generation logic.

Tools should not be treated as “one of the copies.” It is the upstream.

## 6.2 Add a thin Tools CLI

I would not build a large release system. I would build a small command, perhaps:

```text
tools
```

or a Makefile with targets:

```text
make doctor
make link
make install
make promote
make update-models
make check
```

### `tools doctor`

Checks:

- Tools repo exists and is clean.
- Pinned commit matches expected.
- Symlinks point where expected.
- Installed global files match checksums.
- Generated repo files match manifest.
- No hand-edited generated files.
- No stale duplicate plugins.
- Hook-config passes validation.

### `tools link`

Creates symlinks for artifacts where symlinks are supported.

### `tools install`

Copies artifacts where symlinks are not supported.

### `tools promote`

Explicitly imports intentional changes from live/deployed locations back into Tools.

This should be deliberate and noisy. It should show diffs and require confirmation.

No silent inference from live state.

### `tools update-models`

Regenerates:

- models-cache.json,
- free-model whitelist,
- provider suppression data,
- validation report.

---

## 6.3 Consumer lockfile

Each consumer repo that materializes Tools artifacts should have a small lockfile.

Example:

```json
{
  "tools_repo": "~/projects/Tools",
  "tools_commit": "0123456789abcdef",
  "materialization": {
    ".opencode/plugins/crosslink-guard.ts": "symlink",
    ".claude/skills/shared-skill": "symlink",
    ".claude/hooks/session-hook": "generated-copy"
  },
  "checksums": {
    ".claude/hooks/session-hook": "sha256:..."
  }
}
```

This is much lighter than a full immutable bundle system but preserves the key B invariant.

---

# 7. What to do with the interim plan

The interim plan is useful, but I would modify it.

## Keep

1. Reverse-sync the newest live/ASES artifacts into Tools.
2. Make Tools the canonical source.
3. Fix correctness bugs immediately.
4. Exclude `.crosslink/rules/` from sync.
5. Use checksums to detect divergence.

## Change

1. Do not make the sync script the permanent distribution model.
2. Do not make the guard-plugin state machine the primary architecture.
3. Prefer symlinks/user-level installation where tests pass.
4. Replace “sync all copies” with “materialize according to artifact class.”
5. Add a pin/lockfile rather than only destination manifests.
6. Add explicit `promote` instead of relying on manual reverse-sync.

---

# 8. Strongest and weakest arguments across options

## Strongest argument overall

The strongest argument in the entire briefing is empirical:

> Single-copy artifacts stayed current. Multi-copy artifacts drifted.

That strongly favors reducing the number of writable loci.

## Strongest argument for Option A

One distribution channel is genuinely attractive.

But it is only strong if `crosslink` is the correct owner of all those artifacts. I do not believe it is.

## Strongest argument for Option B

Install-time verification is better than runtime drift detection.

This is correct and should be kept in lightweight form.

## Strongest argument for Option C

No copies means no copy drift.

For a single-machine environment, this is extremely compelling.

## Strongest argument for Option D

Different artifacts have different correct loci.

This is the most realistic architectural observation.

## Strongest argument for Option E

It works now.

That is a strong transition argument, not a strong end-state argument.

## Weakest argument overall

The weakest argument is that drift can be solved primarily by discipline.

It cannot. The current drift is rational behavior in a system with multiple writable loci.

---

# 9. Are the bug fixes independent of architecture?

Mostly yes. The correctness fixes should proceed immediately.

## 9.1 Hook-config precedence bug

Independent and urgent.

This is a live functional bug. It should be fixed regardless of architecture.

However, the architecture affects rollout:

- If guard plugins remain repo-local copies, the fix must be deployed to all consumers.
- If guard plugins become user-level, the fix can be made once in the canonical plugin.

So the logic of the fix is architecture-independent, but the deployment path depends on architecture.

## 9.2 plugin.ts / dynamic-models.ts consolidation

Independent in intent, architecture-dependent in placement.

The consolidation should happen. The canonical consolidated plugin should live in Tools and be installed user-level if possible.

## 9.3 models-cache regeneration

Independent and required.

No architecture solves a stale cache if there is no regeneration mechanism.

This needs a command and a test.

## 9.4 Whitelist verification

Independent and required.

The whitelist should be validated against actual model discovery. Dead entries should be removed or marked. The UX behavior should be documented.

## 9.5 Init-deployed snapshot divergence

This one is architecture-dependent.

It cannot be fully fixed without deciding whether those resources are crosslink-owned or Tools-owned. But the immediate requirement is clear:

> Every deployed snapshot must have a canonical git source and a versioned deployment path.

---

# 10. Verification gaps that should be executed-tested

Before committing to the final architecture, I would execute-test the following.

## 10.1 User-level plugin loading

Test whether OpenCode loads plugins from:

```text
~/.config/opencode/plugins/
```

Specifically test:

- simple TypeScript plugin loading,
- guard plugin loading,
- interaction with project-level config,
- precedence if both user-level and project-level plugins exist,
- duplicate loading risk,
- error behavior when plugin throws.

This is critical for Option D.

## 10.2 Symlinked plugin loading

Test whether OpenCode/Claude accept symlinked plugin files:

```text
ASES/.opencode/plugins/crosslink-guard.ts -> Tools/plugins/crosslink-guard.ts
```

and:

```text
~/.config/opencode/plugins/plugin.ts -> Tools/plugins/plugin.ts
```

Check:

- file read,
- import resolution,
- source maps if any,
- file watching,
- realpath behavior,
- permission/execute behavior.

## 10.3 Symlinked skills/hooks/commands/MCP loading

Test whether agent runtimes load:

- `.claude/skills` symlinked directories,
- `.claude/commands` symlinked files,
- hooks symlinked into expected paths,
- MCP config files symlinked or pointing to symlinked binaries.

## 10.4 `crosslink init` behavior with existing files

Test:

- `crosslink init`
- `crosslink init --force`
- behavior when target path is a symlink,
- behavior when target path is modified,
- behavior when target path is gitignored,
- behavior when target directory contains extra files,
- whether init deletes unknown files,
- whether init overwrites layer-owned policy.

This is essential before making anything link-based.

## 10.5 Crosslink binary embedding feasibility

Only needed if Option A is kept under consideration.

Test:

- binary size impact,
- rebuild time,
- resource extraction fidelity,
- version reporting,
- whether embedded resources can be kept in sync with source tree.

Given my recommendation, this is lower priority.

## 10.6 Guard plugin self-check through symlink/user-level path

If the guard plugin checks its own loaded file, test:

- whether it sees the symlink path or resolved path,
- whether sha256 matches expected manifest,
- whether user-level installation changes its ability to read itself,
- whether multiple loaded copies cause conflicts.

## 10.7 Clean bootstrap

From a clean checkout, test:

```text
clone repos
run one bootstrap command
verify all necessary artifacts exist
verify doctor passes
start a session
```

This is the most important integration test.

## 10.8 Model cache regeneration

Test:

- provider query or discovery mechanism,
- cache write,
- whitelist validation,
- behavior when network is unavailable,
- behavior when provider list changes.

---

# 11. Recommended migration plan

## Phase 0 — Freeze and stop bleeding

1. Declare a temporary freeze on direct edits to deployed copies.
2. If emergency edits are required, mark them for immediate promote.
3. Fix hook-config precedence bug in all active consumers.
4. Consolidate model plugins in a temporary canonical location.
5. Regenerate or manually validate models-cache and whitelist enough to stop false blocking.

## Phase 1 — Establish canonical source

1. Reverse-sync newest wrappers into Tools.
2. Reverse-sync newest guard plugin behavior into Tools.
3. Reverse-sync newest model plugin behavior into Tools.
4. Consolidate `plugin.ts` and `dynamic-models.ts` in Tools.
5. Decide ownership of hooks/commands/MCP snapshots:
   - crosslink-owned, or
   - Tools-owned.
6. Remove or archive stale duplicates.

## Phase 2 — Execute critical tests

Run the verification matrix above.

The key questions are:

- Can plugins be user-level?
- Can plugins be symlinked?
- Can skills/hooks/commands be symlinked?
- Does `crosslink init` interfere?
- Does guard plugin self-check still work?

## Phase 3 — Choose materialization per class

Based on tests:

### If user-level loading works

Move wrappers and model plugins to user-level links/copies installed from Tools.

### If symlink loading works

Use symlinks for repo-local shared artifacts.

### If symlink loading fails

Use pinned generated copies from Tools with manifests.

### If both fail for a specific artifact

Keep that artifact in the interim sync model temporarily, but mark it as needing a design exception.

## Phase 4 — Replace sync with doctor

Implement:

- Tools lockfile,
- manifests,
- `tools doctor`,
- `tools link/install`,
- `tools promote`.

Use the old sync script only until the new mechanism is stable.

## Phase 5 — Enforcement

Once the system has been clean for a period:

- turn warnings into hard failures for generated-file dirtiness,
- add pre-commit checks,
- add session-start quick checks,
- remove redundant copies.

---

# 12. Option F: a different framing

If you want to name the recommended architecture as an Option F, I would describe it as:

> **Option F — Ownership-plane distribution with link-first materialization.**

It is not completely unrelated to A–E. It is a synthesis, but it changes the center of gravity.

## Option F structure

### Plane 1: Source plane

Tools and crosslink source trees contain all shared artifact sources.

No hidden binary-only resources.

### Plane 2: Runtime plane

Runtime artifacts exist only as:

- user-level single copies,
- symlinks,
- generated pinned copies.

### Plane 3: Policy plane

Layer repos own policy:

- rules,
- hook-config,
- agent role definitions,
- local workflow constraints,
- `.ases/` when implemented.

### Plane 4: Verification plane

A small doctor/manifest system verifies that runtime state matches source/pin.

This plane is not primarily the guard plugin. It is an explicit tooling command.

## Why Option F is better than A–E alone

It avoids the monoculture mistake:

- not everything belongs in crosslink,
- not everything should be a bundle,
- not everything should be copied,
- not everything should be synced.

It instead asks each artifact to declare its locus and materialization mode.

---

# 13. Specific answer to the final question

Given the drift evidence, the interim plan, and Options A–E, I recommend:

> **A hybrid architecture based on Option D, implemented with Option C where executed-tested, using Option B-lite invariants for pinning/verification, and using Option E only as the migration bridge.**

More concretely:

1. **Do not make crosslink the universal distributor.**  
   Reject Option A as the general solution.

2. **Do not build a full immutable bundle release system yet.**  
   Adopt only the lockfile/checksum/dirty-check invariants from Option B.

3. **Prefer symlinks and user-level single copies wherever runtime support is verified.**  
   This is the Option C part.

4. **Use the three-class artifact locus from Option D as the architecture.**  
   Classify every artifact explicitly.

5. **Use the current interim plan only to reverse-sync and stabilize.**  
   Do not let sync-tooling.sh become the permanent end state.

The end state should look like this:

```text
Tools
  canonical wrappers
  canonical model plugin
  canonical guard plugin
  canonical shared skills
  canonical Tools-owned hooks/commands/MCP if applicable
  manifests and doctor tooling

crosslink
  crosslink-specific embedded resources
  crosslink init for crosslink-owned scaffolding
  no ownership of general Tools artifacts

layer repos
  hook-config
  rules
  role policy
  layer-owned agent definitions
  generated/link materialization for required runtime paths

user-level runtime
  ~/.local/bin wrappers installed/linked from Tools
  ~/.config/opencode/plugins installed/linked from Tools
  one copy of global model policy

verification
  tools doctor
  lockfile/pin
  checksums for generated files
  explicit promote operation for intentional live changes
```

That architecture addresses the actual root cause: it removes multiple writable sources, makes the canonical source explicit, and makes drift a detectable violation rather than an inevitable habit.
---