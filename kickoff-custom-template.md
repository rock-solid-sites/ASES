---
title: "kickoff custom template"
tags: []
sources: []
contributors: ["OL2r"]
created: 2026-07-31
updated: 2026-07-31
---

# Kickoff Custom Template

This project uses a custom kickoff prompt template instead of the 92-line default built into crosslink.

## How It Works

The crosslink binary checks for a custom template in this order:
1. Project-specific `agent.kickoff_template` in `.crosslink/hook-config.json`
2. Global fallback at `~/.crosslink/rules/kickoff.md`
3. Built-in 92-line default (if neither is configured)

## Configuration

### Global (all projects)

Place your template at `~/.crosslink/rules/kickoff.md`. All projects will use it automatically unless overridden.

### Project-specific

In `.crosslink/hook-config.json`:

```json
"agent": {
  "kickoff_template": "rules/kickoff.md"
}
```

To skip the prompt entirely (rely on OpenCode's `instructions` config):

```json
"agent": {
  "no_template": true
}
```

## Template File

The custom template is at `~/.crosslink/rules/kickoff.md` (global) or `.crosslink/rules/kickoff.md` (project-specific). It's ~40 lines covering:
- Blocked/gated git commands
- Essential instructions (agent setup, session, plan, implement, sync)
- Code quality rules
- Final steps

## Placeholders

The template supports these placeholders, substituted at launch time:
- `{description}` — feature description or AC text
- `{issue_id}` — crosslink issue number
- `{branch_name}` — feature branch name

## Differences from Default

The default KICKOFF.md (built into the crosslink binary) includes additional sections that are conditionally injected:
- **CI Verification** — only when `--verify ci` or `--verify thorough`
- **Adversarial Self-Review** — only when `--verify thorough`
- **Spec Validation & Reporting** — only when design doc has acceptance criteria

The custom template omits these sections. They can be added back if needed.

## Upstream Status

The `agent.kickoff_template` and `agent.no_template` options are proposed in PR #44 on dollspace-gay/crosslink. The placeholder substitution and global fallback are local additions.
