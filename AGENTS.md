# Agent Operating Rules

This document outlines the operational rules and behavioral guardrails for AI agents working within the ASES project repository.

## 1. Zero-Context Agent Requests ("Clean Room" Sessions)

When the user requests that a task be performed by a "fresh" or "new" agent instance (e.g., a background task, an adversarial reviewer, or a swarm subagent), this is typically done to ensure the task is executed with **zero prior context**. 

**Rule:** If a specific agent, model, or subagent tool call fails (e.g., due to an API error, missing model, or platform issue), the active agent **MUST STOP AND ASK THE USER FOR DIRECTION.**

*   **DO NOT** silently substitute the current agent instance to perform the task.
*   **DO NOT** fall back to using the current conversational context to answer on behalf of the failed agent.
*   **DO NOT** assume the user wants you to proceed anyway. 

The integrity of multi-round adversarial reviews and capability mapping relies on clean-room isolation. If a tool like `task` or a subagent like `gemini-pro-reviewer` fails, report the exact error and wait for the user to decide the next step.

## 2. Methodology & Evidence Traceability
Agents must respect the `Source -> Observation -> Finding -> Assumption -> Decision -> Outcome` lineage described in the `README.md`. When generating new documents, agents must explicitly link back to the originating files in the `sources/` or `observations/` directories.

## 3. Fallback: Native API Clean Room Execution

If built-in tools for launching subagents or isolated tasks fail (such as the `task` tool encountering database errors), agents should use **Native API Clean Room Execution**.

This involves writing a standalone Python script (e.g., in `/tmp/opencode/`) that uses `urllib.request` to directly query the target model's API. This guarantees a completely fresh context window and bypasses local tooling bugs.

**Execution Pattern:**
1. Extract the target model's API key from the environment (e.g., `NVIDIA_API_KEY`, `DEEPSEEK_API_KEY`, `GOOGLE_API_KEY` from `~/.bashrc` or `~/.config/chat-ui/secrets.env`).
2. Write a lightweight Python script that reads the necessary context files from disk.
3. Construct the API payload and use `urllib.request.urlopen` to execute the POST request.
4. Capture the model's response and write it to a Markdown file in the project (e.g., `.design/reviews-6.md`).

This technique was successfully pioneered in prior sessions (e.g., `/tmp/opencode/nvidia_glm51_review.py`) to conduct adversarial reviews when standard tools failed.

## 4. Adversarial Consensus vs. Project Authority

When conducting adversarial reviews, capability mappings, or multi-model evaluations, agents must remember that **an adversarial consensus is a finding, not a mandate.**

If multiple models agree on an architectural flaw or propose a unified solution (even if they unanimously reject the current specification):
*   **DO NOT** automatically update the repository's core specifications or charters to reflect the adversarial consensus.
*   **DO NOT** preemptively create new documentation directories or project plans based on adversarial output.
*   **DO** record the synthesis and findings in the appropriate research directories (e.g., `syntheses/` or `adversarial-reviews/`).
*   **DO** wait for explicit human direction before treating adversarial findings as definitive changes to the project plan. The human orchestrator retains absolute authority over the project's direction.
