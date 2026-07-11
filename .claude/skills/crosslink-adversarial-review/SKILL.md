---
name: crosslink-adversarial-review
description: Use when the user says "review this", "/review", "send this for review", "run a review", "have this reviewed", "adversarial review", "swarm review", or asks for a code/design audit with adversarial scrutiny. Launches parallel review agents via crosslink swarm review, then optionally runs fix agents. Does NOT trigger on "pre-commit review" or "review my changes" (that's the review-pre-commit skill). Does NOT trigger on "review this code for bugs" (that's direct LLM review, not crosslink swarm).
---

# Crosslink Adversarial Review

You are about to run a structured adversarial review using `crosslink swarm review`. This launches parallel review agents across codebase partitions, each with a specific scrutiny mandate.

## Decision: Which kind of review?

- **Adversarial review** (`adversarial` mandate): Ha-satan / loyal accuser. Hunts for architectural flaws, incorrect assumptions, design anti-patterns. Use for design docs, architecture changes, methodology validation.
- **Security review** (`security` mandate): Trust boundaries, injection surfaces, credential handling, auth bypass paths.
- **Robustness review** (`robustness` mandate): Crash paths, resource leaks, edge-case handling, error recovery.
- **Correctness review** (`correctness` mandate): Logic errors, race conditions, data integrity, spec conformance.

If the user didn't specify, ask which mandate. If they said "adversarial review" or gave no specifics, default to `adversarial`.

## Not this skill

- Pre-commit quality gate → use the `review-pre-commit` skill
- Architectural code review (SOLID, complexity) → use the `qa` skill
- Informal "can you look at this code?" → just read the file and respond; no swarm needed

## Procedure

1. Verify crosslink is available: `crosslink --version`. If not, tell the user to install it.

2. Check what's changed (vs main):
   ```bash
   git diff --name-only origin/main..HEAD
   ```
   If nothing changed, review starts from HEAD's filesystem state.

3. Launch the review:
   ```bash
   crosslink swarm review --mandate <adversarial|security|robustness|correctness> --agents 4 --file-issues
   ```
   - `--agents N`: Number of parallel review agents (default: 4)
   - `--file-issues`: Auto-create crosslink issues for each finding
   - `--doc <path>`: Optional — consolidate findings into a design document

4. Monitor progress:
   ```bash
   crosslink swarm review-status
   ```

5. After review completes, review findings:
   ```bash
   crosslink issue list --label review-finding
   ```

6. Optionally launch fix agents for findings:
   ```bash
   crosslink swarm fix --from-label review-finding --max-agents 6
   ```

## Full pipeline (review + auto-fix)

For an end-to-end review-to-fix pipeline in one command:
```bash
crosslink swarm pipeline --mandate adversarial --auto-fix --auto-file-issues
```

## Reference

For comprehensive documentation: `crosslink knowledge show adversarial-review`
