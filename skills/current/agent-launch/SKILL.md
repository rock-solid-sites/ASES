---
name: agent-launch
version: 1.0.0
description: Resolve and verify ASES agent execution routes across GitHub Actions, Codespaces, Modal, and authorized model providers before launching.
status: current
---

# Agent launch and route selection

Resolve **controller**, **execution host**, **launcher**, **target provider/model**, **permissions**, **source revision**, **resource/time budget** and **durable result location** before launch. Model identity belongs in trusted caller-side settings, not in the recipient's self-identification prompt. Never silently substitute models or execution hosts.

For independent reviews, use `skills/current/review-launch/SKILL.md` and the current `ases-plugins` reviewer recipe. GitHub Actions is proven for short, bounded one-shot reviews; Codespaces/Modal are candidates for deep investigations, with workload-specific readiness to verify.

The old IT3812/VPS and Crosslink environment mentioned in `docs/methodology/Agent Model Launch Routes.md` is **historical** and must not be assumed connected or executable. Use that document only for model-provider compatibility details explicitly corroborated in current runs. Phoenix Grove's endpoint and model names are recorded in `ases-plugins/.github/reviewers/phoenix-grove.env.example`; its Actions secret is `PGS2_API_KEY`, never stored in Markdown. The operator reported all three Phoenix Grove models successfully completing reviews elsewhere on 2026-11-17.

Check the actual connected tools before claiming a remote launch can happen. Prefer the smallest approved test. On missing tool, route, account, secret or authorisation, report the precise blocker; no silent fallback. For long-running tasks, preserve durable commits/position records and validate progress rather than treating a live process as proof of work.
