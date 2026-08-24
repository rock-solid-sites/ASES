---
title: Lifecycle Manager - Agentic Loop Design for Swarm Sessions
program: EDASES
layer: Implementation
document_type: Design
status: Proposed
authority: Derived
parent_epic: "#423"
depends_on:
- scripts/agent-liveness.py
- scripts/liveness-watchdog.sh
- docs/SESSION-END.md
- .design/session-archive-wind-down.md
consumed_by:
- Swarm launch (EPIC #423 phases)
related_documents:
- .design/rpc-enforcement-prototype.md
- .design/chatgpt-execution-classification.md
---

# Purpose

Convert the liveness watchdog from a monitoring tool into a lifecycle manager that
owns the full per-agent loop: detect transitions, act on them, clean up after them,
and surface only decisions - not residue - to the orchestrator. This is the
pre-swarm and during-swarm infrastructure that makes a multi-agent session a
controlled experiment rather than an archaeology dig.

# Design principle

Most of what we call session-end work is per-agent-lifecycle work. If each agent
transition triggers its own automated response, the session-end ceremony shrinks
to just: thin handoff write and push recommendation.

Three-layer model:

    MODEL          semantic judgment ("I think this is acceptable")
       |
    POLICY         legal transition check ("is that a permitted move?")
       |
    EXECUTION      mechanical enforcement (admission, cleanup, kill, evidence)

# Agent lifecycle states

Each dispatched agent carries:

    LAUNCHED -> RUNNING -> COMPLETED | FAILED | KILLED | PARKED | FROZEN

Transition detection: existing watchdog verdict-diff logic (agent-liveness.py v2
six-class matrix), unchanged.

# Post-transition actions (NEW - the lifecycle manager extension)

On each detected transition, the lifecycle manager executes scoped responses:

COMPLETED (DONE marker written):
  - kickoff cleanup --only <agent> --yes (remove worktree + tmux)
  - verify deliverable exists on main or agent branch
  - append model-evidence row to registry staging file

FINISHED-UNMARKABLE (reviewer/auditor posted findings):
  - verify findings exist on working issue
  - flag worktree for operator force-sweep at wave end
  - append model-evidence row

FAILED (error exit, nonzero code):
  - preserve worktree for forensics
  - post failure alert to working issue
  - recommend relaunch-with-backup-model to orchestrator

KILLED (orchestrator stop):
  - immediate kickoff cleanup --only <agent> --yes
  - verify no orphaned worktree remains
  - log termination with evidence chain

PARKED (rate-limit signature in log tail):
  - do NOT kill (agent is correctly waiting)
  - record resume_at timestamp from retry-after header
  - if resume_at passes without activity: reclassify as FROZEN
  - alert orchestrator only if multiple agents parked simultaneously
    (indicates shared quota pool exhaustion, not individual failure)

FROZEN (LIKELY-FROZEN confirmed across >=2 cycles):
  - attach last-200-line log tail as diagnostic evidence
  - auto-kill per spiral authority (operator-granted 2026-08-24)
  - kickoff cleanup --only <agent> --yes
  - post termination record with evidence chain
  - recommend relaunch-with-backup-model to orchestrator

STALE-SUSPECT:
  - one warning cycle
  - if confirmed next cycle: escalate to FROZEN handling

# Wave-level actions (beyond per-agent)

On merge landing on main:
  - report unpushed commit count; suggest push if > threshold (#451 pattern)

On doctrine/knowledge file edit:
  - run DIS existence-validator on dependent documents (#443 spec)

On dispatch:
  - verify launch contract: model ID valid, issue exists, estimate declared,
    provenance recorded (#448 metadata flags)

On session wind-down (operator-initiated or all-agents-complete):
  - run full wind-down protocol per .design/session-archive-wind-down.md

# Implementation

Extend scripts/liveness-watchdog.sh (v2, commit 4c8ab0ba) with post-transition
actions. The verdict-diff logic already detects every state change; adding
scoped responses to each detected transition is additive, not architectural.

New script: scripts/lifecycle-manager.sh wrapping liveness-watchdog.sh with:
  - transition-action dispatch table
  - per-agent cleanup via kickoff cleanup --only
  - model-evidence staging file appends
  - push-ahead-count check on merge detection
  - DIS validator invocation on doctrine edits

All stdlib bash/python3. State in /tmp/opencode/lifecycle-state/. No daemons.
No new dependencies. The 120s polling cadence is sufficient because every action
is bounded and idempotent.

# Success criteria for swarm validation

The EPIC #423 swarm IS the test. Success means:

SC1: Every dispatched agent that completes has its worktree/tmux cleaned within
     one watchdog cycle (120s) of DONE-marker write, without human intervention.
SC2: Every agent that freezes is killed within two cycles (240s) with termination
     record and relaunch recommendation posted.
SC3: Every agent that finishes posts model-evidence to the registry staging file
     without orchestrator action.
SC4: Session-end ceremony takes <10 minutes because no accumulated residue exists.
SC5: At least one agent fails (model freeze or error) and the lifecycle manager
     handles it correctly without operator intervention - proving the agentic
     loop is resilient, not just fair-weather.

SC5 is the most important criterion: a night where nothing goes wrong proves
nothing. A night where three agents fail and the lifecycle manager catches,
kills, cleans, and recommends - without the operator noticing until the morning
summary - proves the architecture.
