# Orchestrator cleanup amendment ? 2026-10-29

Correction to `process-cleanup-2026-10-29.md`: after that note was written, the orchestrator observed the agent-owned duplicate processes PID 94571 (`python3 timing_event_model.py`) and PID 95473 (`python3 -u timing_event_model.py --deadline 1500`) continuing to consume CPU. The orchestrator issued `kill -TERM 94571 95473`. A subsequent process check showed that no `timing_event_model.py` processes remained. The then-current bounded run PID 96292 had already exited before that check. No unrelated process was signalled.

The only experiment evidence retained in this worktree is `correspondence-run.log`, whose last observed progress is `independent: state-word 0/4194304, offers 0, 0.0s`. The correspondence search did not complete before the Phoenix Grove provider returned HTTP 402 for insufficient credits. No timing-reduction conclusion is claimed from that incomplete run.
