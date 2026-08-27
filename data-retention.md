---
title: "Data Retention Policy"
tags: []
sources: []
contributors: ["OL2r"]
created: 
updated: 
---


# Data Retention Policy

Session data (reasoning traces, evidence, transcripts) implements the preservation requirements of the Methodology to Requirements Mapping Specification and is retained indefinitely in cold archive once exported.

Hot/cold split: live databases hold recent sessions for tooling; weekly export produces compressed JSONL plus uncompressed index under ~/opencode-archive/, synced off-server via rclone. Extraction-before-pruning: old sessions are cleared from the server only after (1) export verified by destination-side read-back and (2) mining epics have extracted capability and failure data. Worktrees, tmux sessions and rotated logs follow the kick-down cleanup convention and are pruned at session wind-down regardless of archive state.

Deletion gates: nothing is deleted unless the verification log shows green. See scripts/wind-down.py and .design/session-archive-wind-down.md.
