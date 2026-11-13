---
title: "LAUNCH"
version: 0.3.0-experimental
status: experimental
authority: run-scoped
run_id: ASES-SOL-CTRL-A-20261113
supersedes_revision: eaf0d2c5092c1c1627e1ef79188378d1237f3e37
---

# Paste into a NEW Codex Cloud session

**Before launch:** select repository `rock-solid-sites/ASES` and base branch `research/sol-controlplane-a-20261113` if the Codex UI permits. If the new task starts on `main`, the experimental skill directory is not available automatically; first delegate to a worker to fetch the branch and instructions. This launch file itself is not a Codex startup mechanism.

## Compressed user prompt

> Activate experiment `ASES-SOL-CTRL-A-20261113` and the repo skill `$ases-sol-controlplane-a`. Primary agent operates as control plane only: directly use *only* subagent coordination; delegate all file reads, shells, research, code, testing, Git, Work Notes, hashes and summaries to Luna-class workers. A worker should read `.agents/skills/ases-sol-controlplane-a/BRIEF.md` and `PACKETS.md`, refresh current PR/ASES-4 state, then log in ASES-8, and return a <=250-word decision packet. Parent chooses WHAT/WHY, **precommits verification obligations, compares separate builder and verifier Luna packets, and alone decides ACCEPT/REVISE/UNVERIFIED**. Workers implement and independently test HOW; no builder self-certification. Run the queue continuously while quota permits, checkpoint with Git and Work Notes; no merges or production actions. Independent CI/review is assigned outside this session. Measure direct parent tool calls and parent/child usage for comparison with the prior hands-on run.

## Startup verification

Luna should verify Codex Cloud host/environment, repo+branch, skill file accessibility, actual delegated Git/Work Notes capabilities, source baseline, Work Notes lease and the first short decision packet. A parent that needed to run a shell to activate the experiment counts as a treatment deviation. If the skill is not accessible, use this prompt to delegate a recovery read rather than silently claiming it was loaded.

Do not ask the model to state its own model/provider/effort; select models in the host UI/launch configuration. For the child, use runtime-selected economical Luna model(s) with known tool permissions.
