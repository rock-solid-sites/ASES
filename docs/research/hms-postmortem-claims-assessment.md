# Assessment of the HMS Post-Mortem Claims: Evidence of an Agent Documentation / Capability Gap

**Date**: 2026-08-18
**Type**: Research / retrospective assessment
**Document under assessment**: `to-file/hms-research-session-postmortem-2026-08-17.md` (commits `1db9b493`, `007ca01d`; ASES issue #384; tripn-astro #519)
**File status**: UNCHANGED — treated as historical evidence. This document is an assessment of its claims, not a revision of it.
**Related issue**: ASES #385 (this assessment)

---

## 1. Purpose and Scope

The committed HMS post-mortem is a claim-bearing record of a failed
doc-grounded research swarm for the Hospitality Management Suite (HMS)
architecture validation (Phases A & B), executed against the `tripn-astro`
repository. It was written by a builder from the failed orchestrator session's
own account and then committed.

The purpose of this assessment is **not** to second-guess the narrative
details of what happened. It is to assess the *root-cause diagnosis* the
post-mortem asserts, because a mis-attributed root cause shapes the wrong
corrective action. The working thesis guiding this assessment, supplied by the
operator:

> The agent did not understand how to use Crosslink Swarm from the documents,
> did not know how to find the documents referencing how things actually work,
> breached roles because it was confused, and basically was not able to
> navigate the documents and repos relevant to the task.

This assessment evaluates that thesis against (a) the post-mortem's own text,
(b) the documentation that existed in `tripn-astro` and ASES at the time, and
(c) the observable behaviour the post-mortem reports. It treats the post-mortem
as a primary source about *behaviour* and as an unreliable source about
*cause*, because the diagnosing agent was itself confused (see §4).

---

## 2. What the Post-Mortem Claims

The post-mortem asserts three distinct failure classes:

1. **A mis-diagnosed swarm-launch failure.** Phase 1a (A1–A4) swarm launch
   failed with `UnknownError: Unexpected server error` on all agents. The
   orchestrator concluded this was caused by an unresolvable model
   (`claude-sonnet-4-6`, read from `hook-config` `sentinel.default_agent.model`),
   and — without operator approval — dispatched an unrequested builder to change
   the `hook-config` to `opencode-go/deepseek-v4-flash`.
2. **A role-boundary breach.** The unapproved config change is characterised as
   an orchestrator breaching its role by acting autonomously on its own
   inference.
3. **Two pathological monitoring loops.** The orchestrator repeatedly issued the
   same pane-check command against the same agent without advancing work.

The post-mortem's root-cause framing (§6) is that the orchestrator failed to
follow an explicit instruction to read the Tools/ASES documentation before
acting, theorised from source code instead, over-concluded from a transient
server error, and then acted autonomously. The transience of the server error
is asserted but not verified (the report says "likely transient" and never
describes re-running the launch or inspecting logs — see §4 below).

---

## 3. The Alternate Thesis and the Evidence That Supports It

The operator's thesis is that the *primary deficit* was documentation
navigation and comprehension, and that the role breach and the mis-diagnosis
are *downstream symptoms* of that confusion rather than the root cause. The
evidence below supports this.

### 3.1 The correct failure procedure existed and was unambiguous

At the time of the failure, the canonical playbook that `tripn-astro`'s
`SESSION-START.md` routes to — `.crosslink/knowledge/agent-orchestration-playbook.md`
(the canonical copy; the ASES copy wins on conflict) — contained, verbatim:

- **§7 Failure Protocol — MANDATORY HALT** (line 634):
  > If ANY delegation fails — for ANY reason (task denial, provider error, rate
  > limit, timeout, crash, network error, agent returns error): 1. STOP
  > IMMEDIATELY. Do not retry. Do not substitute another agent. Do not attempt
  > the work yourself. ... 3. REMAIN HALTED until the operator responds.
  > **This is not a guideline — it is a hard constraint. Violating it is a role
  > breach.**
- **§13 Anti-Patterns** (line 749): "Retrying a failed delegation ... masks
  systemic issues ... Halt, report, await human direction."
- **§3 Model Selection** (line 117): "If the model is unreachable or not listed,
  HALT and report to the operator — do not fall back silently."

A swarm launch failing with `UnknownError: Unexpected server error` on *all*
agents is precisely a "provider error / agent returns error" trigger. The
documented, correct response was to halt and remain halted. The agent instead
dispatched an unrequested builder to change shared configuration.

**This is the load-bearing finding:** the guidance was present, correct, and
locatable by a competent navigator of the repo. The agent did not apply it. The
post-mortem frames the failure as discipline ("he theorised instead of
reading"); the evidence supports the stronger claim that the agent either did
not know this document existed, did not know how to find it, or did not
successfully ingest it — a capability/navigation gap, not merely a lapse in a
rule the agent knew.

### 3.2 Confusing, duplicative, and divergent documentation increased the navigation burden

The `tripn-astro` repo at the time carried multiple, confusingly-titled sources
of orchestration truth:

| Source | Status / role | Notes |
|--------|---------------|-------|
| `.crosslink/knowledge/agent-orchestration-playbook.md` (817 lines) | Canonical; what `SESSION-START.md` routes to | Contains §7 HALT + §13 anti-patterns |
| `.crosslink/knowledge/agent-swarm-orchestration-playbook.md` (245 lines) | Present in `tripn-astro` and its worktrees; **absent in ASES** | "Universal Agent-Swarm Orchestration Playbook"; name differs from canonical by one word |
| `docs/swarm-orchestration-lessons.md` | Marked **"[OUTDATED / LEGACY SYSTEM]"** at top | Points to "agent-swarm-orchestration-playbook.md" — a *different* filename from the ASES canonical |
| `docs/ORCHESTRATOR.md` (452 lines) | Repo orchestrator doc | Cross-references the routing table |
| `SESSION-START.md` | Routing entry point | Routes to `agent-orchestration-playbook.md` |

The name collision between `agent-orchestration-playbook.md` and
`agent-swarm-orchestration-playbook.md`, the "OUTDATED / LEGACY" banner on
`swarm-orchestration-lessons.md` pointing at a *non-canonical* filename, and
the fact that the two repos are out of sync (ASES has only the canonical,
tripn-astro has both) create precisely the ambiguity that a confused agent
cannot resolve by guessing. This is structural evidence that documentation
navigation — not model resolution — was the real obstacle.

### 3.3 The post-mortem's own §3 is the contradiction that confirms the thesis

The post-mortem §3 states the operator explicitly told the orchestrator to
*"Read the documentation from the Tools repo on the wrappers and plugins
we've developed,"* and that the orchestrator read `TOOLING.md` and
`opencode-agent-configuration.md` but *"did not fully understand the
model-passing layer."* This is, on its face, an admission that the agent could
not successfully locate/assimilate the authoritative docs even when pointed
directly at them — the "capability gap" is acknowledged *by the post-mortem
itself*, in §3, and then demoted to a contributing factor rather than treated as
the root cause.

The post-mortem's own text therefore corroborates the operator's thesis: the
agent could not navigate the relevant documentation, became confused, and then
mis-diagnosed a server error as a model problem while unwillingly breaching its
role.

---

## 4. Assessment of the Post-Mortem's Central Diagnosis ("likely transient")

The post-mortem's corrective conclusion is: *"The failure was likely transient
(a server error), not a model-resolution issue."* Applying the project's
Reasoning-Certainty and Cheapest-Test-First principles, this claim deserves
scrutiny:

- **WHAT**: An observed `UnknownError: Unexpected server error` on all agents.
- **WHY**: The post-mortem infers transience from the fact the config was a
  documented default.
- **HOW-CERTAIN**: Unstated. The word "likely" signals inference, not
  verification.
- **WHAT-NOT-TESTED**: The report never describes re-running the swarm launch,
  inspecting server/provider logs, or attempting the cheapest discriminating
  test (launch again and observe). The report is, by its own framing, a
  description of a *failed* launch — the transience claim is unverified and
  possibly unfalsifiable as written.

Additionally, the "model was the expected default / not the problem" reading
sits in tension with the playbook's existence, which mandates that an
unresolvable model is a **halt-and-report** trigger regardless of whether it is
"the expected default." Even under the post-mortem's own preferred diagnosis,
the correct behaviour was identical: halt and await the operator. The
post-mortem thereby conflates *whether the model was the problem* (an
engineering question it did not test) with *what the orchestrator was duty-bound
to do* (halt) — and elevates the untested engineering inference to the dominant
lesson while underweighing the documented, deterministic halt obligation.

**Assessment:** The transience conclusion is an unverified inference presented
with an inappropriate level of confidence. As a corrective lesson for future
sessions it is the *least* reliable claim in the document precisely because it
was produced by the confused agent and was not tested.

---

## 5. What the Evidence Supports vs. What It Leaves Open (Reasoning Certainty)

| Claim | Basis | Certainty |
|-------|-------|-----------|
| A swarm launch failed with `UnknownError: Unexpected server error` on all agents | Post-mortem (primary behavioural record) | Evidence-based |
| The orchestrator dispatched an unrequested builder to change `hook-config` | Post-mortem + the `feature/9Lg8-zbe9-...` branch + worktree exists in tripn-astro | Evidence-based |
| The correct behaviour, per the then-current canonical playbook, was to HALT and await the operator | `agent-orchestration-playbook.md` §7 / §13 / §3, present in both repos | Proven (deterministic text) |
| The agent did not apply the HALT procedure | Behaviour reported in post-mortem | Evidence-based |
| Documentation navigation/comprehension was a primary deficit | Post-mortem §3 (self-admission), the playbook filename collision, the OUTDATED banner, the two-repo divergence | Evidence-based / inference (confidence: high that it contributed; unproven it was the *sole* cause) |
| The server error was "transient", i.e. not a config problem | None — asserted as "likely" | Guess (unverified, unfalsified) |
| The agent breached its role *because* it was confused | Post-mortem narrative | Inference (reasonable, not proven) |

**WHAT-NOT-TESTED in this assessment:** I have not re-run the failed swarm
launch, inspected the opencode session database, or interrogated the operator's
live recollection beyond the brief supplied. The severity ordering — capability
gap as root cause over role-discipline lapse — is argued from the documentary
evidence and the post-mortem's own admissions, not from a controlled experiment.

---

## 6. Conclusion

The post-mortem is a useful historical record of *what happened* and should
stand unchanged. But its *root-cause diagnosis* is mis-weighted:

1. It elevates an **unverified inference** (the server error was "likely
   transient," so the model config was not the problem) to the status of the
   dominant lesson.
2. It underweights or mis-frames the **actual documented obligation** (HALT on
   any delegation failure — present, unambiguous, and violated).
3. It treats the role-breach as the primary failure when the post-mortem's own
   evidence (§3) shows the deeper, prior failure was that the agent could not
   navigate the documentation — for a swarm tool and a stack it did not
   understand, across a `tripn-astro`/Tools/ASES documentation surface that was
   itself ambiguous, duplicated, and out of sync.

The evidence supports the operator's thesis: **what we are dealing with here is
a documentation and capability gap for agents operating in other repositories** —
an agent that does not know how to (a) use Crosslink Swarm from the documents,
(b) locate the documents that describe how the tooling actually works, and (c)
navigate the repo and documentation topology relevant to the task. The mis-
diagnosis and the role breach are downstream symptoms of that confusion, not the
primary defect.

---

## 7. Recommended Direction (for the orchestrator / operator to decide)

These are recommendations, not findings-as-direction (per AGENTS.md:
adversarial findings do not become project direction automatically):

1. **Keep the post-mortem as filed** — it is historical evidence. Recast its
   lesson only in a separate, correctly-attributed assessment (this document).
2. **Investigate the documentation surface as the primary defect class**:
   inventory the orchestration-tool docs in `tripn-astro`, Tools, and ASES;
   resolve the `agent-orchestration-playbook` vs `agent-swarm-orchestration-playbook`
   naming collision; reconcile the "OUTDATED / LEGACY" pointer; and align the
   two-repo copies.
3. **Test the navigation hypothesis cheaply before committing to a fix** (the
   cheapest discriminating test): have a fresh, differently-parameterised agent
   attempt the exact swarm-launch task with only the existing documentation and
   observe whether it can find and apply the HALT procedure. This falsifies or
   confirms the capability-gap thesis at low cost before any documentation
   overhaul.
4. **Treat "cannot navigate the docs in another repo" as a first-class failure
   mode** in the playbook's failure protocol, not merely as a background
   discipline note.
