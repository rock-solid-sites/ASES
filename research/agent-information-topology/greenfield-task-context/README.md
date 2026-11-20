# ASES task-context topology: greenfield format experiment

**Research evidence, preserved as Experimental.** Its architectural recommendations were ratified in the [canonical Task-Scoped Information and Handoff Method](../../../docs/methodology/ASES%20Task-Scoped%20Information%20and%20Handoff%20Method.md) and [accepted architecture decision](../../../docs/architecture/Task-Scoped%20Information%20Architecture%20Decision%202026-11-21.md). This research folder is **not** an alternative source of operational authority, live resolver or required document layout.

This work starts from task, source authority and producer–consumer evidence boundaries. The primary proposed output is an **information contract for task-specific views**, not a mandatory graph. It **does not** make old `AGENTS.md`, `SESSION-START.md`, role documents or a permanent start/end ritual prerequisites.

- [TASK-VIEW-CONTRACT.md](TASK-VIEW-CONTRACT.md) — historical *experimental candidate* retained for provenance; the canonical method linked above now governs task views.
- [PROPOSAL.md](PROPOSAL.md) — background semantic topology, typed relationships, optional adapters and falsification criteria, reconciled with evidence favoring a lighter default.
- [EXAMPLE-GRAPH.json](EXAMPLE-GRAPH.json) — two synthetic tasks, two shared rules, one scoped project decision, source references, evidence and a position.
- [EXAMPLE-VIEWS.json](EXAMPLE-VIEWS.json) — two manually authored expected task views. The scoped override **replaces**, rather than joins, the upstream review text in task alpha; task beta keeps the upstream rule.
- [test_contract.py](test_contract.py) — standard-library regression checks. A tiny test-only resolver recomputes applicable content from typed relationships; **this is not production infrastructure**.
- [Preregistered 2×3 comparison](comparison/PRE-REGISTRATION.md) — manual, lightweight structured and graph-derived views on identical synthetic tasks. [Recorded results](comparison/RESULTS-2026-11-20.md): **all 6 pass**, total 24/24 tests. The graph shows no correctness advantage in this small static sample; manual is shortest. This does not test agent consumption.
- [First real coordination field case](field-trial/PROMPT-SOURCE-ADMISSION-2026-11-20.md) — an autonomous launch brief missed task-relevant current prompting methodology despite finding the short current skills. This led to [PR #73](https://github.com/rock-solid-sites/ASES/pull/73), which fixes the **source-admission rule**, not historical root/startup files. Fresh-chat auto-selection and model-visible loading remain unverified.


Test:

```sh
python3 -m unittest discover -s research/agent-information-topology/greenfield-task-context -p 'test_*.py' -v
```

[GitHub Actions](https://github.com/rock-solid-sites/ASES/actions/workflows/context-topology-greenfield.yml) runs the synthetic contract on this research branch. A first run found a mismatched order in the example's source-revision receipt, corrected in the following commit. No model, real agent file, hosted service, or API funding route is involved.

**Architecture decision accepted (Projektor ASES-22, 2026-11-21):** The completed synthetic comparison favors compact manual packets, with optional lightweight structure for complex handoffs, **without a mandatory persisted graph**. The real-world prompt-method omission independently demonstrates the importance of *selecting* applicable sources. The candidate was reviewed and ratified as the canonical method linked above; graph resolution remains optional and evidence-dependent. The fresh-chat automatic-invocation test is **deferred by operator direction**.

**Separate experiments:** WNASES-18/PR #64 concerns policy publication (no Luna job currently launched or queued); WNASES-19/PR #63 concerns OpenCode instruction exposure. Neither dictates this candidate format. No external model was invoked for this documentation work.
