---
title: Tools Distribution Architecture — Synthesis of One-Shot Reviews
program: EDASES
layer: Research
document_type: Synthesis
status: Active
authority: Derived
canonical_repository: edases

depends_on:
  - docs/research/tools-distribution-architecture-review-input.md
  - docs/research/Tools Distribution Architecture Reviews.md
  - docs/research/agent-tooling-and-permission-enforcement-reviewed.md

consumed_by:
  - Tools/monorepo drift remediation planning (#365 and descendants)
  - Execution-engine UI research programme (tooling distribution decisions)

supersedes: []
last_updated: 2026-08-15
---

# Tools Distribution Architecture — Synthesis of One-Shot Reviews

> **Purpose.** This document synthesizes the seven independent one-shot
> architectural reviews collected in
> `docs/research/Tools Distribution Architecture Reviews.md` (2,874 lines).
> Each review was a response to the self-contained briefing in
> `docs/research/tools-distribution-architecture-review-input.md` (the drift
> problem, the interim `sync-tooling.sh` plan, Options A–E, and six discussion
> questions). This synthesis identifies each reviewer and position, maps
> convergence and divergence, assesses strength/risk per position with
> cross-reviewer support, states the recommended synthesis with the open
> decision points, and records WHAT-NOT-TESTED.
>
> **Grounding rule.** Every claim below cites reviewer + section (and, where
> useful, line spans of the reviews file). Line spans refer to
> `Tools Distribution Architecture Reviews.md` as of 2026-08-15. Where a
> claim is this synthesis's inference rather than a reviewer's statement, it
> is marked **[inference]**.

---

## 1. Reviewer identification and positions

The issue description for #373 anticipated "8+ named reviewers … plus a large
unlabeled review." The actual file contains **seven labeled reviews**; the
"large" review is Qwen3.8-Max (lines 1559–2873), and it is labeled. There is
**no unlabeled section** in the file as read. Section spans:

| Reviewer | Lines | Length | Explicit recommendation |
|----------|-------|--------|--------------------------|
| ChatGPT | 4–730 | ~727 | **Option F = D + lightweight B + selective A** (single-source, typed-locus distribution) |
| Deepseek V4 Pro 0813 | 733–1012 | ~280 | **D+E hybrid** with lightweight B-style pinning (an "Option F": classed source-of-truth + generated materialization) |
| Claude Sonnet 5 High | 1015–1035 | ~21 (dense) | **D as base, upgraded with C for the one artifact class where it is low-risk** (wrappers) |
| Gemini 3.6 Flash | 1038–1177 | ~140 | **D + lightweight pinning** (B's single-command deterministic release discipline) |
| GLM-5.2 | 1180–1427 | ~248 | **D implemented in phases**, with E's sync-tooling.sh repurposed as D's Class-2 mechanism; bug fixes immediately |
| Kimi Instant | 1431–1556 | ~126 | **Option D+** = D (foundation) + C (Class 1 via symlinks) + B's generated-artifact discipline (Class 2) |
| Qwen3.8-Max | 1559–2873 | ~1315 | **D as the organizing principle, C as preferred materialization where executed-tested, B-lite invariants, E only as migration bridge** (Option F: ownership-plane distribution with link-first materialization) |

### 1.1 ChatGPT (L4–730)

- **Diagnosis.** Agrees with the root diagnosis but qualifies it: the problem
  is not "copies" but **"multiple writable authorities for the same logical
  artifact"** — after divergence there is no mechanically knowable answer to
  "which one is correct" (L11–43). Sharpened: the system "lacks a single
  authoritative locus per artifact and a deterministic mechanism for deriving
  every consumer instance from that locus" (L43–44). The layer split is not
  the root problem (L39).
- **Per-option verdicts.** A: good for crosslink-owned resources, bad as the
  universal distribution architecture (L118–127). B: excellent principle,
  potentially over-engineered implementation; steal the principles, not the
  machinery (L174–207). C: best theoretical drift elimination, but not
  portable as the primary architecture without successful experiments; test
  it (L225–250). D: "best of the five as a conceptual architecture" (L329–
  333). E: good migration architecture, poor final architecture; avoid
  over-investing in the State 0→1→2 machinery (L337–369).
- **Recommendation (Option F).** "Single-source, typed-locus distribution" =
  **D + the versioning discipline from B + the ownership boundary from A**
  (L371–411). The critical rule: "Every artifact has exactly one source of
  authority. Consumers either reference it, install it, or generate it. They
  never become another source" (L406–409).
- **Key extra findings.** (a) "Canonical Tools" is only meaningful **per
  artifact** — an artifact-locus table (artifact → authority) prevents the
  warehouse becoming a second methodology repository (L414–435). (b) The
  drift detector itself can become drift: manifest, sync script, state
  machine, promotion command, checks are new pieces of infrastructure that
  can diverge (L508–555). (c) The correctness bugs should be fixed
  independently, but the *desired location* of the fixed code may change
  after the architecture decision (L438–441). (d) Sequencing: Phase 1 stop
  the bleeding (four fixes + reverse-sync), Phase 2 ownership table, Phase 3
  test assumptions, Phase 4 implement D+B-lite, Phase 5 remove transitional
  machinery (L584–638).

### 1.2 Deepseek V4 Pro 0813 (L733–1012)

- **Diagnosis.** Mostly correct but refined: the real problem is
  **"unmanaged, unchecked, ambiguous-source copy-out"** — copy-out is not
  inherently bad; what is missing is a clear source of truth, a
  version/pin, a checksum/manifest, and the rule that consumer copies are
  generated artifacts, not editable sources (L736–749). The layer split is
  not the cause (L747).
- **Per-option verdicts.** A: not a good primary target — it would create a
  badly shaped ownership boundary (L766–767). B: good discipline if the
  project grows, too heavy as the next step (L779–780). C: too risky and
  operator-hostile at this stage; test later if ever (L792–793). D: best
  conceptual target, but adopt conditionally with a concrete migration path
  (L805–806). E: excellent migration vehicle, not a good end state (L818–
  819).
- **Recommendation.** A **hybrid of D and E, with lightweight B-style
  pinning** (L825–829). Proposed target architecture has **four classes**:
  (1) machine-global single-copy at user level (wrappers, model plugins,
  guard plugins) deployed from Tools via a `tools install --user` command
  with a user-level manifest — the guard-plugin move is conditional on a
  user-level-loading verification (L837–866); (2) per-repo generated
  materialization via `.tools-pin` (Tools commit hash) + a committed
  generated sha256 manifest, with `--check` failing on mismatch (L870–891);
  (3) layer-owned policy, never synced (L895–906); (4) crosslink-owned
  embedded resources — Tools should not pretend to own what crosslink owns
  (L909–918).
- **Key extra finding.** Explicitly **rejects the State 0→1→2 promotion
  machine**: "at this scale, that is more ceremony than needed. Once the
  manifest is committed, a mismatch should simply mean 'generated tree is
  dirty; run sync.' A hard fail in `--check` is sufficient" (L891).
- **Migration steps.** Reverse-sync first, fix bugs immediately, implement
  user-level install, remove per-repo copies of Class-1 artifacts, add pins
  and manifests for Class-2, define sync/init ordering (L922–944).

### 1.3 Claude Sonnet 5 High (L1015–1035)

- **Diagnosis.** "Copy-out is structurally flawed" is close but imprecise;
  the actual failure mode is **"duplication with an undefined edit
  direction"** — copies with no enforced single edit-direction and no
  verification step will drift the first time someone is in a hurry (L1018).
  The single-copy model plugin survived not because copies are evil but
  because there was only one place to edit (L1018).
- **Per-option verdicts.** A: rejected outright — the coupling argument is
  real and disqualifying (ownership-boundary violation, not a performance
  one) (L1020). B: rejected outright — full versioned-release pipeline is
  infrastructure sized for a team, not a single operator (L1022). C: not a
  full replacement, but **yes as a partial one** — wrappers are plain
  executable scripts with no plugin-loader involved, so symlinking them is
  zero-risk today; the risky part is symlinking plugins whose loader
  behavior is untested (L1024). E: don't ship as end state, but ship its
  bug fixes this week regardless (L1016).
- **Recommendation.** Adopt D's three-class split as the permanent
  structure, but treat **Class 1 as two sub-cases**: wrappers get symlinked
  into Tools **now** (Option C today, zero risk); model plugins and guard
  plugins stay D-style (install-from-Tools discipline) **until a five-minute
  spike verifies symlinked plugin loading**; if it works, promote them to
  symlinks too and Class 1 disappears entirely as a copy-out problem
  (L1026). Class 2 (skills, hooks, commands, mcp) stays pinned copy-out with
  a generated sha256 manifest (L1026). Class 3 stays in-repo, never synced
  (L1026).
- **Key extra finding.** Guard plugins are "your permission-model enforcement
  layer, which is the worst place in the whole system to be running on an
  untested code path" (L1024). Verification order matters: (1) symlinked
  plugin loading, (2) user-level guard-plugin loading + role resolution,
  (3) `crosslink init --force` collateral, (4) crosslink embedding
  feasibility (deprioritized) (L1030–1034).

### 1.4 Gemini 3.6 Flash (L1038–1177)

- **Diagnosis.** Yes, with an essential distinction: the failure is
  **"unversioned, bidirectional copy-out without forced synchronization or
  an immutable single source of truth"** (L1043–1045). The fundamental
  design flaw is **mixed locality ownership**: machine-global artifacts were
  placed inside individual repos, repo-local artifacts were partially
  embedded into the binary, and canonical sources were treated as advisory
  (L1049–1053).
- **Per-option verdicts (explicitly scored).** A: ❌ Over-Engineered &
  Poorly Coupled (L1061–1063). B: ⚠️ Valid for Teams, Over-Engineered for
  Single-Operator (L1067–1069). C: ⚠️ Fragile Boundaries & Operational
  Friction (L1073–1075). D: ✅ Strongest Foundation & Correct Architecture
  (L1079–1081). E: ⚠️ Necessary Short-Term Step, Insufficient End State
  (L1085–1087).
- **Recommendation.** **Option D + lightweight pinning** (L1091–1093). The
  artifact-locus plan is four classes: (1) machine-global (wrappers, model
  plugins, guard plugins) at `~/.local/bin` + `~/.config/opencode/plugins/`
  installed via `Tools/install.sh` (L1118–1120); (2) repo-materialized
  (skills, hooks, MCP) via `sync-tooling.sh` from a pinned Tools commit +
  generated `.tools-manifest.json` (L1121); (3) repo-owned policy — zero
  syncing (L1122); (4) binary-embedded — strictly limited to crosslink
  internal utilities (L1123).
- **Execution roadmap.** Phase 1 fix independent bugs (hook-config
  precedence, plugin consolidation, cache + whitelist maintenance); Phase 2
  verification (four gaps: user-level guard loading, crosslink hook/command
  overrides, symlink compatibility fallback, binary embedded limits);
  Phase 3 deployment (upstream reverse sync, `Tools/install.sh`, downstream
  cleanup, sync script) (L1127–1177).

### 1.5 GLM-5.2 (L1180–1427)

- **Diagnosis.** The right direction, wrong precision: the system has
  **multiple physical copies of each artifact with no defined canonical
  source, no enforced flow direction, and no reconciliation mechanism**
  (L1185–1187). The drift table itself shows the flow is live→ASES→Tools —
  Tools is the *sink*, not the source (L1191–1193). The single-copy
  precedent proves the drift mechanism is **physical multiplicity**, not
  copy-out per se (L1196).
- **Per-option verdicts.** A: attractive in theory but **contradicted by the
  project's own evidence** — item 7 shows the embed-and-init model has
  already drifted in this project, so "drift becomes structurally
  impossible" is falsified (L1208–1217). B: correct architecture for a
  larger fleet, over-engineered for this one; versioning adds detectability,
  not elimination; B's CI-based enforcement is moot without CI (L1221–1232).
  C: structurally the purest, practically the riskiest; the untested
  assumptions are load-bearing — if any one fails, the option fails
  completely (L1238–1246). D: the most surgical and evidence-based option;
  degrades gracefully — if user-level guard loading fails, guard plugins
  fall back to Class-2 pinned copy-out (L1254–1263). E: acceptable as a
  stabilization measure, not an end-state; "who watches the watchmen?"
  (L1269–1273).
- **Recommendation.** **D implemented in phases, with E's sync-tooling.sh
  repurposed as D's Class-2 mechanism**, and the bug fixes done immediately
  and independently (L1279). Importantly, GLM **argues against a hybrid**:
  "multiple mechanisms for the same artifact class is the *current*
  problem"; D is already a hybrid (three mechanisms for three classes).
  Adding more mechanisms doesn't help (L1290–1294).
- **Key extra findings.** (a) Option F — "Accept reality: live locations are
  canonical; Tools is the versioned snapshot" — formalizes the observed
  workflow; but F is a *refinement* of D's Class 1, not a fundamentally
  different architecture; D and F differ only in flow direction, to be
  decided by a Phase-2 workflow audit (L1351–1376). (b) Ten verification
  gaps; gaps 1 (user-level guard loading), 2 (`crosslink init --force`
  collateral), and 9 (does init deploy guard plugins?) are **blocking** for
  D (L1384–1397). (c) Phase 4 optional upgrade: if symlink tests pass, Class
  1 upgrades from install to symlink — "C applied to one class, where it's
  safe" (L1323–1327).

### 1.6 Kimi Instant (L1431–1556)

- **Diagnosis.** "Copy-out is structurally flawed" is the correct primary
  diagnosis; sharpened to **"copy-out without an enforced, verifiable single
  source of truth"** — no provenance metadata, no generation boundary, no CI
  gate (L1438–1440). The layer split is not the problem (L1442).
- **Per-option verdicts.** A: violates separation of concerns; dev loop
  unacceptable; turns crosslink into an accidental monolith (L1448–1450).
  B: over-engineered — "like using Kubernetes to run a personal blog"; still
  leaves copies (L1452–1454). C: the only option that structurally
  eliminates physical copies; but submodules are painful and symlinks are
  machine-absolute, untested, and collide with `crosslink init` (L1456–
  1458). D: the only option that **explains the evidence** — the single-copy
  whitelist is a natural experiment; least invasive (L1460–1462). E:
  institutionalizes drift; "managed decay," not a solution (L1464–1466).
- **Recommendation.** **Option D+** = D as foundation + **C for Class 1
  implementation (symlinks)** + B's generated-artifact discipline for Class
  2 (L1472–1498). Class 1: symlinks to the Tools working tree (single
  machine makes absolute symlinks safe) (L1480). Class 2: `.tools-pin` +
  `tools-materialize` using `git show <pin>:<path>` + committed
  `.tools-manifest` (sha256) + **a pre-commit hook that rejects commits
  modifying materialized files** (L1481). Class 3: never synced (L1482).
  Crosslink fork: strip all OpenCode/Claude-specific resources from the init
  payload; embed only crosslink-native resources (L1484–1486).
- **Key extra findings.** (a) Novel insight: "for one person on one machine,
  symlinks are not fragile — they are the simplest possible correct
  solution"; prior reviewers proposed D but stopped short of symlinks for
  Class 1, defaulting to "install discipline" (a euphemism for managed
  copy-out) (L1516–1518). (b) A more radical Option F: investigate whether
  OpenCode/Claude support a user-level project configuration overlay
  (`~/.config/opencode/projects/<repo>/`), which could eliminate even
  Class-2 per-repo copies (L1520). (c) Fallbacks: if user-level or symlink
  loading fails, fall back to D's original Class-1 single-copy with an
  install script (L1539).

### 1.7 Qwen3.8-Max (L1559–2873) — the large review

- **Diagnosis.** Yes, sharpened: **"The system lacks artifact authority and
  unidirectional distribution. Copy-out drifts because copies are treated as
  sources"** (L1594–1596). Seven specific failure mechanisms listed: multiple
  writable copies, no enforced flow direction, no source/generated
  distinction, no pinning, two overlapping distribution mechanisms (Tools +
  `crosslink init`), live mutation of deployed files, no cheap promote path
  (L1584–1593). Discipline is necessary but not sufficient — the architecture
  must make the correct action easier than the incorrect action (L1608–1616).
- **Challenge to the settled structure.** Tools' placement **outside** the
  monorepo may preserve the cross-repo atomicity problem that causes drift;
  if the pin/lockfile discipline becomes painful, consider bringing Tools
  into the monorepo or a workspace-level meta-repo (L1632–1645). This is the
  only reviewer to challenge the repo-of-repos placement of Tools.
- **Per-option verdicts.** A: reject as the general architecture; use
  embedding only for genuinely crosslink-owned resources (L1673–1707). B:
  don't adopt full now; adopt **B-lite** — pin Tools commit, generate
  manifest, `tools doctor`, fail when dirty (L1747–1769). C: **should be the
  preferred implementation mechanism wherever executed tests prove it safe**;
  use local link-creation scripts and checked-in manifests rather than
  checked-in absolute symlinks (L1804–1861). D: adopt as the architectural
  frame (L1915–1935). E: use only as the migration path; "'Already approved'
  is not a strong architectural argument. It is a strong schedule argument"
  (L1962–1970).
- **Recommendation.** Hybrid: **D as the model, C as the preferred
  materialization mechanism, B-lite for pinning/verification, E only as the
  transition plan** — "canonical-source, locus-based distribution with
  link-first materialization" (L1974–1982). Option F named: **"ownership-
  plane distribution with link-first materialization"** — four planes:
  source, runtime, policy, verification (L2762–2812).
- **Core principles (six).** One writable source per artifact; deployed
  copies are generated or linked; direction of flow explicit; prefer links
  over copies on this machine (tested); checksums and pins for anything
  materialized; detect problems at install/check time, not primarily at
  runtime (L1986–2059).
- **Artifact-by-artifact recommendations.** Guard plugins: code → Tools,
  hook-config/role policy → layer-owned, runtime locus user-level if
  supported (L2064–2102). Wrappers: machine-global single-copy, symlink
  preferred, never edit live (L2105–2151). Model plugins: machine-global;
  consolidate `plugin.ts`/`dynamic-models.ts`; models-cache and whitelist
  become generated artifacts with a regeneration command (L2154–2210).
  Skills: symlink or generated pinned copy; resolve the `crosslink init`
  ownership conflict (L2212–2245). Hooks/commands/MCP: **every deployed
  resource must have a visible source in either crosslink or Tools** — binary
  embedding is a transport mechanism, not the only source of truth (L2247–
  2286). `.crosslink/rules/`: never sync (L2288–2302). Hook-config:
  layer-owned, validated by a shared validator; **the schema should reject
  ambiguous precedence** rather than only fixing the list overlap (L2304–
  2330). `.ases/`: do not distribute until it is real (L2332–2346).
- **Implementation model.** A thin Tools CLI (`tools doctor`, `tools link`,
  `tools install`, `tools promote`, `tools update-models`) + a consumer
  lockfile (`tools_commit`, materialization mode per artifact, checksums)
  (L2365–2447). Six-phase migration: freeze → canonical source → critical
  tests → choose materialization per class → replace sync with doctor →
  enforcement (L2686–2759).
- **Strongest/weakest arguments.** Strongest overall: "Single-copy artifacts
  stayed current. Multi-copy artifacts drifted" — favors reducing writable
  loci (L2474–2479). Weakest overall: "drift can be solved primarily by
  discipline" — it cannot; current drift is rational behavior in a system
  with multiple writable loci (L2512–2517).

---

## 2. Convergence map

### 2.1 Converged diagnosis (7/7)

All seven reviewers **accept the root diagnosis with refinement** — none
rejects "copy-out is structurally flawed," but all sharpen it. The converged
diagnosis is:

> **The failure is not copying per se; it is multiple writable copies with no
> enforced single source of truth, no defined edit direction, no pinning, and
> no verification.**

- ChatGPT: "multiple writable authorities for the same logical artifact" (L13).
- Deepseek: "unmanaged, unchecked, ambiguous-source copy-out" (L740).
- Claude: "duplication with an undefined edit direction" (L1018).
- Gemini: "unversioned, bidirectional copy-out without forced synchronization
  or an immutable single source of truth" (L1045).
- GLM: "no defined canonical source, no enforced flow direction, and no
  reconciliation mechanism" (L1187).
- Kimi: "copy-out without an enforced, verifiable single source of truth"
  (L1440).
- Qwen: "lacks artifact authority and unidirectional distribution" (L1596).

**The layer split is explicitly exonerated by every reviewer** (ChatGPT L39,
Deepseek L747, Claude L1018 implied, Gemini L1049 via "mixed locality
ownership" being a distribution problem not a layering problem, GLM L1198,
Kimi L1442, Qwen L1620–1630).

### 2.2 Converged empirical anchor (7/7)

Every reviewer cites the **single-copy precedent** — the user-level
model-whitelist plugin stayed current while every N-place artifact drifted —
as the strongest evidence that drift is structural to physical multiplicity
(ChatGPT L278–282; Deepseek L738; Claude L1018; Gemini L1080; GLM L1194–1196;
Kimi L1461; Qwen L1599–1602, L2476–2479). ChatGPT calls it "an unusually
useful architectural experiment already performed by the system itself"
(L282); Qwen calls it the strongest argument in the entire briefing (L2476).

### 2.3 Option D is the converged target (7/7)

Every reviewer recommends **Option D (three-class artifact locus) as the
architectural frame** — either pure D, D+E, D+C, D+pin, or D as the
organizing principle of a hybrid (see §1). No reviewer recommends A, B, C,
or E as the end state. The three-class split itself is accepted verbatim by
all seven: (1) machine-global single-copy, (2) per-repo materialized,
(3) layer-owned policy. Gemini: "Strongest Foundation & Correct
Architecture" (L1079); GLM: "the most surgical and evidence-based option"
(L1254); Kimi: "the only option that explains the evidence" (L1461); Qwen:
"the only option that begins with the right question: *what is the correct
locus of this artifact?*" (L1917–1929).

### 2.4 Option E is interim-only (7/7)

All seven classify the interim `sync-tooling.sh` plan as **acceptable
stabilization, not the destination** (ChatGPT L339, L367; Deepseek L818–819;
Claude L1016; Gemini L1085; GLM L1273; Kimi L1464–1466; Qwen L1962–1970).
Common reasons: it is still managed copy-out; the state machine and manifest
become artifacts that themselves need maintenance; drift remains detected,
not prevented.

### 2.5 Option A is rejected as the general architecture (7/7)

All seven reject A as the universal mechanism; the disqualifying argument is
**ownership and release coupling**, not binary size (ChatGPT L86–116; Deepseek
L761–767; Claude L1020; Gemini L1061–1063; GLM L1210–1217; Kimi L1448–1450;
Qwen L1673–1707). GLM adds the strongest counter-evidence: the embed-and-init
model has *already drifted* in this project (item 7), so A's "drift becomes
structurally impossible" is falsified (L1208–1217). All allow A **only for
genuinely crosslink-owned resources** (ChatGPT L124–126; Deepseek L909–918;
Gemini Class-4 L1123; Qwen L1699–1707; Kimi L1484–1486).

### 2.6 Option B full is rejected; B-lite is adopted (7/7)

All seven agree the full immutable-bundle release pipeline is over-engineered
for a single-operator, ~5-repo fleet (ChatGPT L176–185; Deepseek L777–781;
Claude L1022; Gemini L1067–1069; GLM L1225–1232; Kimi L1454; Qwen L1733–
1743). All seven **adopt B's invariants in lightweight form**: a Tools commit
pin + a generated/committed sha256 manifest + "consumer copies are generated
artifacts" + install/check-time detection (ChatGPT L187–201; Deepseek
L883–889; Claude L1026; Gemini L1121; GLM L1320–1321; Kimi L1481; Qwen
L1747–1769).

### 2.7 Option C is test-gated (7/7)

All seven see C's drift-impossible property as attractive, and all seven gate
it on **executed tests of symlinked plugin loading** (ChatGPT L225–250;
Deepseek L790–793; Claude L1024; Gemini L1073–1075; GLM L1240–1246; Kimi
L1456–1458; Qwen L1804–1861). Divergence (see §3) is only about how much C to
use *now*: Claude (wrappers only), Kimi (all Class 1), Qwen (wherever
executed-tested).

### 2.8 Correctness bugs are independent (7/7)

All seven agree the four correctness fixes — hook-config precedence,
`plugin.ts`/`dynamic-models.ts` consolidation, models-cache regeneration,
whitelist verification — are **independent of the architecture choice and
should proceed immediately** (ChatGPT L438–441; Deepseek L947–956; Claude
L1028; Gemini L1134–1141; GLM L1330–1343; Kimi L1503–1510; Qwen L2520–2565).
The nuance (Deepseek, Qwen): the architecture decision changes **how the fix
propagates and how many copies need it**, not whether it is needed (Deepseek
L956; Qwen L2530–2535).

### 2.9 Reverse-sync first (7/7)

Every reviewer's migration path begins with **reverse-syncing the newest
live/ASES copies into Tools** to establish Tools as the true canonical source
before anything else (ChatGPT Phase 1 L597; Deepseek step 1 L924–926; Gemini
Phase 3.1 L1173; GLM Phase 1 L1306–1310; Kimi L1503–1510 implied by "fix live
first, then propagate"; Qwen Phase 1 L2696–2706).

### 2.10 Verification gaps converge (7/7)

The same four verification gaps recur in every review: (1) user-level
guard-plugin loading, (2) symlinked plugin loading, (3) `crosslink init
--force` collateral, (4) crosslink binary embedding feasibility (ChatGPT
L644–673; Deepseek L964–987; Claude L1030–1034; Gemini L1146–1166; GLM
L1384–1397; Kimi L1528–1538; Qwen L2571–2683). GLM marks 1, 2, and 9 as
**blocking** for D (L1397); Kimi marks 1 and 2 as blocking Class 1 (L1528–
1533); Claude orders them by what actually blocks a decision (L1030–1034).

---

## 3. Divergence map

### 3.1 Class-1 mechanism: symlinks-now vs user-level single-copy vs test-first

| Position | Reviewers | Mechanism |
|----------|-----------|-----------|
| Symlink Class 1 now | Kimi (all Class 1), Claude (wrappers only) | Kimi: `~/.local/bin/*` and `~/.config/opencode/plugins/*` → Tools (L1480). Claude: wrappers symlinked now, guard/model plugins after a five-minute spike (L1024, L1026). |
| User-level single-copy + install discipline | Deepseek (conditional), Gemini, ChatGPT (as D), GLM (default) | One copy at user level; Tools is the versioned upstream; deploy by explicit command (Deepseek L837–866; Gemini L1118–1120; ChatGPT L274–284; GLM Phase 3 L1318–1321). |
| Symlinks after tests pass (fast-follow) | Claude (plugins), GLM (Phase 4 optional), Qwen (preferred where tested), ChatGPT (test C first) | If symlink plugin loading works, Class 1 upgrades from install to symlink (GLM L1323–1327; Claude L1026; Qwen L1857–1861). |

This is the sharpest divergence. Kimi frames the disagreement directly:
reviewers proposed D but "stopped short of using symlinks for Class 1,
defaulting instead to 'install discipline' (a euphemism for managed
copy-out)" (L1518). Claude's counter-qualification: the guard plugins are the
worst place to run an untested code path (L1024) — which is why Kimi's
symlink-everything is the riskiest form and Claude's wrappers-only is the
safest.

### 3.2 Flow direction: Tools→live vs live→Tools

- **Most reviewers assume Tools→live** (D's default): Tools is canonical;
  install from Tools; never edit live (ChatGPT L406–409; Deepseek L858;
  Gemini L1120; Claude L1026; Kimi L1480; Qwen L2013–2026).
- **GLM alone formalizes live→Tools** as Option F: the drift table shows live
  copies are consistently ahead; live user-level locations are the de-facto
  sources; Tools is the versioned snapshot (L1351–1374). GLM folds F into D:
  "D and F are the same option with a different flow-direction policy," to be
  decided by a Phase-2 workflow audit (L1376, L1415).

### 3.3 Hybrid vs pure D

- **GLM argues against hybrid**: "multiple mechanisms for the same artifact
  class is the current problem" — D is already a hybrid (per-class); adding
  more mechanisms doesn't help (L1290–1294).
- **Everyone else proposes an explicit hybrid** (D+E, D+C, D+pin,
  D+C+B-lite) — see §1. The apparent disagreement dissolves on closer
  reading: GLM's objection is to *multiple mechanisms per artifact class*,
  and every other proposal assigns exactly one mechanism per class. **[inference]**
  The dispute is terminological, not substantive: "hybrid" across classes
  (all agree) vs "hybrid" within a class (all reject).

### 3.4 Guard-plugin locus: user-level vs per-repo fallback

- **User-level preferred** by most, conditional on verification (Deepseek
  L860–864 conditional; Gemini L1118; GLM gaps 1/9; Kimi L1528; Qwen L2076).
- **Claude is most cautious**: guard plugins stay D-style install-from-Tools
  until the symlink spike passes; they are the permission-enforcement layer —
  worst place for an untested code path (L1024).
- **Fallback agreed by all**: if user-level loading fails, guard plugins
  become Class-2 per-repo generated artifacts (Deepseek L864; GLM L1263,
  L1316; Kimi L1539; Claude L1026).

### 3.5 State-machine disposition

- **Reject/drop**: Deepseek (L891 — "more ceremony than needed"; hard fail in
  `--check` is sufficient); Qwen (L1570 — "no runtime-copy drift state machine
  as the primary control"; L2462 — "Do not make the guard-plugin state machine
  the primary architecture"; detection at install/check time); ChatGPT
  (L345–363 — avoid investing in the machinery; a permanent runtime state
  machine is evidence the distribution mechanism isn't trustworthy).
- **Retire for Class 1, keep narrowed for Class 2**: GLM (L1425).
- **Accept as interim only**: Claude (L1016 — ship bug fixes, not the machine
  as end state); Kimi (L1490 — pre-commit hook instead of runtime machine).
- Gemini does not address the state machine directly; its `.tools-manifest
  .json` + install-step is the install-time analog (L1121).

### 3.6 Tools placement (repo-of-repos)

- **Qwen is the only reviewer to challenge the settled structure**: Tools
  outside the monorepo may preserve the cross-repo atomicity problem; if
  coordination becomes painful, consider bringing Tools into the monorepo or
  a workspace-level meta-repo (L1632–1645). Not required now; requires a
  pin/lockfile discipline either way.
- All other reviewers accept Tools as a sibling warehouse (ChatGPT L39;
  Deepseek L747; GLM L1198; Kimi L1442; Gemini implicit).

### 3.7 Whitelist policy

- **Qwen is the only reviewer to prescribe a policy**: either (A)
  discovery-first with a blocklist for known-bad models, or (B) a curated
  whitelist with mandatory refresh validation and visible staleness
  (L2187–2208). All others say "fix/verify" without choosing (ChatGPT L496–
  504; Deepseek L954; Gemini L1140; GLM L1302; Kimi L1508).

### 3.8 Machinery scale (Tools CLI vs Makefile vs scripts)

- Qwen proposes a thin `tools` CLI (`doctor/link/install/promote/update-
  models`) + consumer lockfile (L2367–2447).
- Gemini proposes `Tools/install.sh` (L1174).
- Deepseek proposes a `tools install --user` command (L854–857).
- ChatGPT/GLM explicitly warn against building any sophisticated release
  service (ChatGPT L629–631; GLM L1225–1232).
- **[inference]** These differ in naming and packaging, not in substance —
  all are thin wrappers around link/copy/verify/promote operations.

---

## 4. Strength / risk assessment per position

### 4.1 Option D (three-class artifact locus) — the converged position

**Strength (cross-reviewer).**
- Evidence-based: generalizes the one proven non-diverged pattern (user-level
  single copy) (Deepseek L800; GLM L1254; Kimi L1461; Qwen L1886).
- Respects artifact heterogeneity: one distribution mechanism for everything
  is too coarse (ChatGPT L260; GLM L1252; Qwen L1882–1895).
- Graceful degradation: if the key untested assumption fails (user-level guard
  loading), only one artifact class moves to a different mechanism — unlike C,
  where a failed assumption breaks the whole option (GLM L1263, L1411; Deepseek
  L803–806).
- Least invasive, keeps repo-of-repos intact (Deepseek L800; Kimi L1461; Qwen
  L1891–1895).

**Risk.**
- Depends on untested user-level guard-plugin loading + role resolution
  (7/7 flag; Claude L1024, L1032; GLM gap 1 L1386; Kimi L1528).
- Class 2 remains copy-out (pinned); drift is detected via git diffs, not
  eliminated (ChatGPT L292–308; GLM L1260; Kimi L1462).
- Requires "never edit live" discipline for Class 1 — the same class of
  discipline that failed before, though on a much smaller surface (GLM L1259;
  Deepseek L744–745; Qwen L1608–1616).

### 4.2 D+ / D+C (Kimi) and C-as-preferred (Qwen) — link-first variants

**Strength.**
- Drift eliminated by construction for Class 1; single edit point (Kimi L1480,
  L1518; Qwen L1788–1800).
- Minimal machinery; matches single-operator reality (Kimi L1516–1518).
- Qwen's refinement (local link script + checked-in manifest instead of
  checked-in absolute symlinks) neutralizes the portability objection (L1821–
  1855).

**Risk.**
- Symlinked plugin loading is untested — the critical gap (all; Kimi L1533;
  Qwen L1804–1810).
- Machine-absolute paths break on a second machine/CI/containers (Deepseek
  L790; Gemini L1075; GLM L1243).
- `crosslink init` may clobber symlinked `.claude` paths (GLM L1242; Kimi
  L1458; Qwen L1811–1813).
- Claude's specific risk: symlinking the permission-enforcement layer before
  testing is the worst-case placement of an untested code path (L1024).

### 4.3 E (interim sync-tooling.sh) — the migration bridge

**Strength.**
- Works today; already adversarially reviewed; fixes the correctness bugs;
  no untested runtime behavior (Deepseek L812–814; Gemini L1085–1087; Qwen
  L1947–1952).
- Lowest-risk immediate stabilization while the end-state tests run (ChatGPT
  L339–343; GLM L1269).

**Risk.**
- Still managed copy-out; drift remains possible and detected after the fact
  (Deepseek L815–816; Kimi L1464–1466).
- The State 0→1→2 machine and manifest are new artifacts that themselves
  need maintenance — the drift detector can drift (ChatGPT L508–555; GLM
  L1271).
- Institutionalizes the wrong end state if never revisited (Kimi L1466; Qwen
  L1962–1970).

### 4.4 A (binary embedding) — rejected as general

**Strength (limited).**
- Single channel, structurally drift-free *for embedded artifacts*, reuses
  the proven `init` mechanism (ChatGPT L55–80; Gemini L1062; Qwen L1659–1669).
- Defensible **only** for genuinely crosslink-owned resources (all).

**Risk / disqualifier.**
- Ownership-boundary violation: crosslink becomes the accidental owner of
  OpenCode/Claude tooling (ChatGPT L86–116; Claude L1020; Kimi L1450; Qwen
  L1673–1675).
- Release-cadence coupling: a 1-line TS change forces a Rust rebuild
  (Deepseek L761; GLM L1213; Kimi L1450).
- GLM's falsification: the embed-and-init model has already drifted (item 7),
  so the "drift impossible" claim is contradicted by the project's own
  evidence (L1208–1217).

### 4.5 B full (immutable bundles) — rejected; B-lite adopted

**Strength (of the invariants).**
- Install-time failure instead of runtime drift; pin answers "which version is
  this consumer supposed to run?" (ChatGPT L154–158; Qwen L1721–1726).
- Prevents live-copy-silently-becomes-canonical (B's deliberate promote/import)
  (Qwen L1725–1726; Deepseek L774).

**Risk / disqualifier (full form).**
- Over-engineered for 3 layer repos + 1 client + 1 fork on one machine
  (ChatGPT L176–185; Kimi L1454; Qwen L1733–1735).
- Still copies; versioning adds detectability, not elimination (GLM L1228;
  Kimi L1454).
- B's CI-based enforcement is moot without CI (GLM L1229; Qwen L1739–1741).
- The discipline ("consumer copies are generated artifacts") is the same kind
  that failed before — versioning doesn't make it self-enforcing (GLM L1230).

### 4.6 C full (references-only) — elegant, gated

**Strength.**
- The only option that structurally eliminates physical copies (Kimi L1457;
  GLM L1238; Qwen L1788).
- For a single machine, symlinks are much less risky than for a distributed
  team (Qwen L1792; Kimi L1516–1518).

**Risk.**
- Load-bearing untested assumptions: if any one fails, the option fails
  completely (GLM L1246).
- Portability: machine-absolute paths, worktrees, CI, another machine
  (ChatGPT L242–244; Deepseek L790; Gemini L1075; Qwen L1808–1810).
- Submodule UX costs (GLM L1244; Kimi L1458; Qwen L1814).
- Conflicts with `crosslink init` regenerating `.claude` resources (GLM L1242;
  Kimi L1458).

### 4.7 GLM's Option F (live-as-canonical) — the flow-direction challenge

**Strength.**
- Honest about the observed workflow: live copies are consistently ahead;
  no discipline inversion required (GLM L1353–1374).
- One-way flow (live→Tools) matches actual behavior; no "reverse-sync"
  concept needed (GLM L1359–1363).

**Risk.**
- Live locations are not git-tracked → no version history for the actual
  source (GLM L1368).
- Degrades to D when the single-machine assumption breaks (GLM L1366).
- Confuses future contributors who clone Tools expecting current tooling
  (GLM L1367).
- GLM itself folds F into D: same option, different flow policy, decided by
  workflow audit (L1376, L1415).

---

## 5. Recommended synthesis

### 5.1 The converged position

The seven reviews converge on a single family of recommendations:

> **Target architecture: Option D (three-class artifact locus). Migration
> bridge: Option E (sync-tooling.sh) — interim only. Pinning/verification:
> B-lite (Tools commit pin + generated committed sha256 manifest).
> Link-first materialization: Option C where executed tests prove it safe.
> Option A: rejected as general architecture (crosslink-owned resources only).
> Correctness bugs: fixed immediately and independently.**

Every component of this position carries 7/7 cross-reviewer support (see §2);
the only open items are the execution-order questions in §5.3.

### 5.2 The strongest defensible version (with rationale)

Building on the convergence, the strongest defensible synthesis is a
**phased D with staged C promotion**, taking Claude's risk-ordering (L1024,
L1030–1034), Deepseek's rejection of the promotion machine (L891), GLM's
blocking-gap discipline (L1397), and Qwen's link-script/manifest refinement
(L1821–1855):

1. **Phase 0 — Fix the correctness bugs now, regardless of architecture**
   (7/7): hook-config precedence, plugin consolidation, models-cache
   regeneration, whitelist verification. Fix in the live copy first, then
   propagate (Kimi L1503–1510; Deepseek L947–956). For the precedence bug,
   prefer Qwen's schema-level fix — the config schema should reject
   ambiguous blocked∩gated overlap (Qwen L2091–2101, L2326–2330) — over a
   one-line list edit, because the overlap is a schema ambiguity, not a
   config typo (Qwen L2089–2090).

2. **Phase 1 — Reverse-sync** newest live/ASES artifacts into Tools and make
   Tools the true canonical source (7/7; §2.9). Record which source won per
   artifact (ChatGPT L597; GLM L1306–1310).

3. **Phase 2 — Run the blocking verification tests before choosing Class-1
   mechanics** (GLM L1397; Kimi L1528–1533; Claude L1030–1034):
   1. User-level guard-plugin loading + role resolution;
   2. Symlinked plugin loading (OpenCode/Claude);
   3. `crosslink init --force` collateral (what it overwrites, whether it
      destroys symlinks/generated files, whether its payload can be reduced);
   4. Whether `crosslink init` deploys guard plugins (GLM gap 9 — determines
      Class-1 vs Class-2 assignment).

4. **Phase 3 — Implement D's three classes, with staged C promotion**:
   - **Class 1 (machine-global)** — start with user-level single-copy +
     install-from-Tools discipline for guard/model plugins (D's safe default,
     Deepseek L837–866; GLM L1318–1321), and **symlink the wrappers now**
     (Claude L1024 — zero-risk because wrappers are plain executable
     scripts). After the symlink test passes, **promote Class 1 to symlinks**
     via a local link script + checked-in manifest (Qwen L1821–1855; GLM
     L1323–1327) — not checked-in absolute symlinks.
   - **Class 2 (per-repo materialized)** — pinned copy-out: `.tools-pin`
     (Tools commit hash) + generated committed sha256 manifest; mismatch
     means "generated tree is dirty; run sync" (Deepseek L891); optionally a
     pre-commit hook rejecting edits to generated files (Kimi L1481). **No
     permanent State 0→1→2 runtime state machine** (Deepseek L891; Qwen
     L1570/L2462; ChatGPT L345–363).
   - **Class 3 (layer-owned policy)** — never synced; `.crosslink/rules/`
     explicitly excluded (7/7; Qwen L2288–2302).
   - **Class 4 (crosslink-owned embedded)** — source of truth in the crosslink
     repo; Tools stops pretending to own init-deployed snapshots (Deepseek
     L909–918); every deployed resource has a visible git source (Qwen
     L2254–2260).

5. **Phase 4 — Retire the transitional machinery** once the new topology
   works: delete old duplicate copies and the runtime drift state machine
   (ChatGPT L632–636); replace `sync-tooling.sh` with `tools doctor/link/
   install/promote`-style thin tooling (Qwen L2367–2447; Deepseek L854–857)
   or equivalent Makefile targets.

6. **Phase 5 — Enforcement (optional, after a clean period)**: turn warnings
   into hard failures, add pre-commit and session-start checks, remove
   redundant copies (Qwen L2751–2759; Kimi L1490).

### 5.3 Open decision points for the operator

1. **Flow direction for Class 1: Tools→live (D default) vs live→Tools
   (GLM's F).** Decided by a workflow audit, not assumed (GLM L1376, L1415):
   is the single-machine assumption durable (GLM gap 7), and what is the
   actual frequency of tooling changes (GLM gap 8)? If the operator edits
   live and rarely remembers to push back, F's live-as-canonical is more
   honest initially; D's Tools-as-canonical is the better target state for
   reproducibility (GLM L1370–1374).

2. **Class-1 materialization: user-level copy first vs symlinks now.** The
   cheap discriminating test is the symlink plugin-loading spike (Claude
   L1024 — "five-minute spike"; Kimi L1533; Qwen L1804–1810). Wrappers can
   be symlinked immediately regardless; guard/model plugins wait for the
   test result. If symlinks fail, user-level single-copy remains correct
   (Claude L1026; Kimi L1539).

3. **Guard-plugin locus: user-level vs per-repo Class-2 fallback.** Gated on
   verification gap 1 (user-level guard loading + four-role `by_type`
   resolution) and gap 9 (does init deploy guard plugins) (Claude L1032;
   GLM L1397; Deepseek L860–864). If user-level loading fails, guard plugins
   become Class-2 generated artifacts (7/7 fallback).

4. **State-machine disposition for Class 2: drop entirely vs keep narrowed.**
   Deepseek (L891) and Qwen (L1570/L2462) say drop; GLM (L1425) says keep a
   narrowed version for Class 2; ChatGPT (L345–363) says don't invest.
   Recommendation **[inference, from 3-of-4 positions]**: keep `--check` as a
   hard-failing verification command, drop the promotion state machine.

5. **Tools placement: sibling warehouse vs in-monorepo.** Qwen alone
   challenges the settled repo-of-repos (L1632–1645). Default: keep Tools
   sibling with the pin/lockfile discipline; revisit only if cross-repo
   coordination becomes painful.

6. **Whitelist policy: discovery-first blocklist vs curated-with-refresh.**
   Qwen's Policy A (discovery-first, blocklist of known-bad) avoids stale
   allowlists hiding new models; Policy B (curated + mandatory refresh
   validation) keeps curation with visible staleness (L2187–2208). Operator
   choice; either beats the current undocumented fail-closed trap.

7. **Machinery scale: `tools` CLI vs Makefile targets vs scripts.** All are
   thin wrappers; the operator should pick the form that is least likely to
   be skipped (the failure mode of B's ceremony, GLM L1225).

---

## 6. WHAT-NOT-TESTED

The following claims in the reviews and this synthesis were **not
executed-tested** as of 2026-08-15 (compiled from every reviewer's
verification-gap list):

1. **User-level guard-plugin loading.** Whether OpenCode loads guard plugins
   from `~/.config/opencode/plugins/` identically to repo-local plugins, and
   whether four-role `by_type` resolution reads per-repo hook-config from the
   working directory (ChatGPT must-test 1; Deepseek gap 1; Claude gap 2;
   Gemini gap 1; GLM gap 1 [blocking]; Kimi gap 1 [blocking]; Qwen 10.1).
2. **Symlinked plugin loading.** Whether OpenCode/Claude resolve symlinked
   plugin files/imports without silent failure (ChatGPT must-test 2; Deepseek
   gap 2; Claude gap 1; Gemini gap 3; GLM gap 4; Kimi gap 2 [blocking]; Qwen
   10.2).
3. **Symlinked skills/hooks/commands/MCP loading.** Whether agent runtimes
   load symlinked directories/files in `.claude/` and `.opencode/` (Qwen
   10.3; ChatGPT must-test 2 partial).
4. **`crosslink init --force` collateral.** Exactly what it overwrites,
   preserves, destroys (symlinks/generated files), and whether its payload can
   be reduced (ChatGPT must-test 3; Deepseek gap 3; Claude gap 3; Gemini gap
   2; GLM gap 2 [blocking]; Kimi gap 3; Qwen 10.4).
5. **Whether `crosslink init` deploys guard plugins** (determines Class-1 vs
   Class-2 assignment) (GLM gap 9 [blocking]; Qwen 10.4 partial).
6. **Crosslink binary embedding feasibility.** Whether `build.rs` can embed
   TypeScript plugins/wrappers and deploy to user-level paths (ChatGPT
   recommended; Deepseek gap 4; Claude gap 4 [deprioritized]; Gemini gap 4;
   GLM gap 3; Kimi gap 4 [low priority]; Qwen 10.5).
7. **Guard plugin self-check through symlink/user-level path.** Whether the
   plugin sees the symlink path or resolved path, and whether sha256 matching
   still works (Qwen 10.6; Kimi L1539 fallback implies).
8. **Clean bootstrap.** Clone repos → one bootstrap command → verify artifacts
   → doctor passes → session starts (ChatGPT recommended 4; Qwen 10.7 — "the
   most important integration test").
9. **models-cache regeneration.** No working regeneration mechanism exists;
   whether a deterministic regeneration command can be built and rerun
   cleanly (all; Deepseek gap 7; Qwen 10.8).
10. **Whitelist refresh behavior.** The staleness was reproduced (refresh
    returns 5 vs 7 entries); the fix behavior (new models appear, dead
    entries removed) is not tested (all; Deepseek gap 8).
11. **Sync-script idempotency / manifest stability.** Whether repeated sync
    produces identical hashes; file-mode and line-ending stability (Deepseek
    gap 6).
12. **CI presence.** Whether any repo has CI to enforce B's "generated output
    is dirty → fail" invariant (GLM gap 6; Qwen L1739–1741). If no CI exists,
    enforcement must be local (pre-commit hook, session-start check).
13. **Single-machine assumption durability.** Whether the operator may acquire
    a second machine (GLM gap 7; Qwen L1792). Affects symlink viability and
    D-vs-F flow direction.
14. **User-level project configuration overlay.** Whether OpenCode/Claude
    support `~/.config/opencode/projects/<repo>/` overlays that could
    eliminate Class-2 per-repo copies (Kimi L1520 — "worth a quick check of
    the documentation").
15. **`crosslink init` behavior with existing/symlinked/gitignored paths and
    unknown extra files** (Qwen 10.4 full matrix).
16. **Wrapper quoting/path handling** (spaces, tmux options,
    `CROSSLINK_AGENT_TYPE`, fork-identity guard behavior) (Deepseek gap 5).

The four blocking tests for the D migration (items 1, 4, 5 above plus
symlink loading item 2) are the cheapest discriminating tests to run before
committing Class-1 mechanics (GLM L1397; Kimi L1528–1533; Claude L1030–1034).
