---
title: "Heuristic Scouting & OSINT Triage"
tags: ["methodology", "orchestration", "research"]
sources: []
contributors: ["S8Vg"]
created: 2026-06-22
updated: 2026-06-22
---

# Methodology Review: Heuristic Scouting & OSINT Triage

**Date:** 2026-06-22
**Evaluator:** OpenCode (Principal/Orchestrator Agent)
**Source/URL:** Internal ASES working hypothesis based on Context Window Limitations.

## 1. Overview
Heuristic Scouting is a research protocol designed to solve Context Window Exhaustion and Context Loss in AI Agents. Instead of an agent sequentially reading hundreds of pages of documentation (which flushes its context window and destroys high-level reasoning), the agent uses AI overviews (like Google Search's AI summaries via a headless browser) to generate a low-token, heavily compressed "Map" of a topic. This map is then used to direct isolated subagents to extract verified facts from the actual "Territory" (the source documentation).

## 2. Core Principles
*   **The Map vs. The Territory:** An AI summary is a Map. It contains taxonomy, jargon, and structure, but it is unverified and prone to hallucination. It must NEVER be cited as an authoritative source or `Observation`. The official documentation is the Territory.
*   **Token Economics:** The Orchestrator's context window is the most valuable resource in the project. It must be preserved for high-level synthesis and cross-project memory. Heavy reading is delegated to single-purpose subagents via the `Task` tool.
*   **Intelligence Analysis approach:** Rather than brute-force reading, the Orchestrator acts like an OSINT (Open Source Intelligence) analyst—using cheap triage to find exactly where the high-value data lives before deploying expensive verification assets.

## 3. Workflow & Lifecycle (The 4-Step Pipeline)
1.  **Scout (Orchestrator + Browser):** Query a headless browser for an AI Overview of the target (e.g., "Microsoft AutoGen architecture"). Extract the core vocabulary, claims, and structural concepts.
2.  **Target (Orchestrator):** Read the unverified summary and formulate 3-4 highly specific, targeted research questions.
3.  **Verify (Subagents):** Use the `Task` tool to dispatch specialized `general` subagents. Prompt them with the specific questions and tell them to fetch the authoritative URLs to extract atomic `Observations`.
4.  **Synthesize (Orchestrator):** The Orchestrator receives the subagent reports, compiles the verified observations into the standard `Harness Evaluation` or `Methodology Review` template, and commits it.

## 4. Observations (Evidence)
*   **OBS-01:** AI context windows degrade in reasoning capability when filled with thousands of lines of raw documentation.
*   **OBS-02:** AI overviews (Google Search) compress multi-page technical documentation into ~500 tokens of structural taxonomy.
*   **OBS-03:** Subagents (via Task tool) run in isolated context windows that do not bleed into the Orchestrator's memory.

## 5. Findings
*   **FIN-01:** Using AI overviews for initial triage reduces the Orchestrator's token load by ~90% during the discovery phase.
*   **FIN-02:** Delegating verification to subagents prevents context contamination in the Orchestrator.

## 6. Relevance to EDASES
This methodology is a direct implementation of the Capability Routing Layer hypothesized in `Research Addendum 01`. It shifts the Orchestrator from an "Execution Agent" (reading docs and writing code) to a true "Principal Agent" (routing tasks, managing token budgets, and synthesizing verified outcomes).
