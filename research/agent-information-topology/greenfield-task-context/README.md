# ASES task-context topology: greenfield format experiment

**Experimental. Not current agent instructions, approved ASES methodology, a live resolver or a new required document layout.**

This prototype starts from the task, applicable authority and producer-consumer evidence boundaries. It **does not** make old `AGENTS.md`, `SESSION-START.md`, role documents or a permanent start/end ritual prerequisites.

- [PROPOSAL.md](PROPOSAL.md) — semantic objects, typed edges, resolver/view contract, optional adapters, minimization requirements and falsification criteria.
- [EXAMPLE-GRAPH.json](EXAMPLE-GRAPH.json) — two synthetic tasks, two shared rules, one scoped project decision, source references, evidence and a position.
- [EXAMPLE-VIEWS.json](EXAMPLE-VIEWS.json) — two manually authored expected task views. The scoped override **replaces**, rather than joins, the upstream review text in task alpha; task beta keeps the upstream rule.
- [test_contract.py](test_contract.py) — standard-library regression checks. A tiny test-only resolver recomputes applicable content from typed relationships; **this is not production infrastructure**.

Test:

```sh
python3 -m unittest discover -s research/agent-information-topology/greenfield-task-context -p 'test_*.py' -v
```

[GitHub Actions](https://github.com/rock-solid-sites/ASES/actions/workflows/context-topology-greenfield.yml) runs the synthetic contract on this research branch. A first run found a mismatched order in the example's source-revision receipt, corrected in the following commit. No model, real agent file, hosted service, or API funding route is involved.

**Future decision:** Compare one truly task-scoped view against a simple human-authored task packet. The format earns adoption only if it improves context selection, conflict reporting and evidence handoff without adding mandatory startup documents or an unnecessary service.

**Independent evidence remains separate:** WNASES-18/PR #64 is the offline policy-publishing pilot with Codex Cloud Luna blocked; WNASES-19/PR #63 investigates OpenCode runtime exposure. Neither dictates this greenfield format and neither is considered complete because of these fixture tests.
