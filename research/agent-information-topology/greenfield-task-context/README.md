# ASES task-context topology: greenfield format experiment

**Experimental. Not current agent instructions, approved ASES methodology, a live resolver or a new required document layout.**

This prototype starts from the task, applicable authority and producer-consumer evidence boundaries. It **does not** make old `AGENTS.md`, `SESSION-START.md`, role documents or a permanent start/end ritual prerequisites.

- [PROPOSAL.md](PROPOSAL.md) — semantic objects, typed edges, resolver/view contract, optional adapters, minimization requirements and falsification criteria.
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

**Next decision:** The completed static comparison favors task-scoped manual or lightweight structured packets **without a mandatory persisted graph** for routine work. Test the contract on real, non-sensitive work and review its failure modes before accepting the format; graph resolution should remain an optional scale-specific pilot, not an architectural prerequisite.

**Independent evidence remains separate:** WNASES-18/PR #64 is the offline policy-publishing pilot with Codex Cloud Luna blocked; WNASES-19/PR #63 investigates OpenCode runtime exposure. Neither dictates this greenfield format and neither is considered complete because of these fixture tests.
