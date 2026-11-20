---
title: Agent Information Topology - OpenCode Exposure Pilot, 2026-11-20
program: ASES
layer: Research
document_type: Research Finding
status: Experimental
authority: Experimental
canonical_repository: ases
last_updated: 2026-11-20
---

# WNASES-19 — OpenCode instruction-exposure observations

**Status:** A bounded real-CLI discovery experiment completed; model-visible instruction injection, actual behavior and OpenCode 2.x remain untested. This evidence does not authorize modification of current agent configuration or promotion of ASES policy.

## Source, route and outputs

- Experiment source: public ASES commit 91817f642b1ca88c58df4bb5191d092ec2d2201d.
- Execution: GitHub Actions in rock-solid-sites/ases-plugins, temporary branch research/wnases-agent-topology-probe-20261120, repository checkout with no persisted Git credentials.
- Installed runtime reported OpenCode 1.19.6, installed using the existing opencode-ai npm package. No model credentials were supplied to the CLI-discovery jobs, and no language-model call was made in those jobs.
- First discoverability run: https://github.com/rock-solid-sites/ases-plugins/actions/runs/44664354935
- Repeated run with directly retrievable sanitized metrics: https://github.com/rock-solid-sites/ases-plugins/actions/runs/44664779334
- Configuration differential run: https://github.com/rock-solid-sites/ases-plugins/actions/runs/44665205592
- Separate independent Phoenix Grove GLM *design-text* review: https://github.com/rock-solid-sites/ases-plugins/actions/runs/44664481674 . The job validated that a substantive report was delivered and stored it in the run summary. Its full findings were not retrieved by this coordinating chat; no reviewer conclusion is incorporated here.

## Executed discovery controls

The discovery probe created synthetic project directories with valid project skills and called OpenCode CLI debug skill in each directory, under the same Actions job.

| Input | CLI exit | Current canary listed | Retired canary listed |
| --- | --- | --- | --- |
| Clean synthetic project, current skill only | 0 | Yes | No |
| Cluttered synthetic project, same current skill and a retired .claude/skills item | 0 | Yes | **Yes** |
| Pinned ASES checkout, original project configuration, first pass | 124 timeout at 55 s | Not measured | Not measured |
| Pinned ASES checkout with project configuration disabled, first pass | 0 | Not applicable | Not applicable |

**Supported finding:** A superseded but syntactically discoverable file in .claude/skills is included in the OpenCode 1.19.6 skill discovery catalog in the cluttered fixture. The filename or metadata marking it retired did not remove it from that catalog. This demonstrates discovery only, not that its full instructions entered a model turn or influenced task quality.

The config inspection returned exit 0 and included an instructions field, consistent with the ASES .opencode/opencode.json reference to SESSION-START.md. Static source inspection also found four legacy plugin references and a filesystem MCP command targeting a retired local absolute path. Their effect on startup has NOT been established.

## Differential diagnosis of the original timeout

A fresh, credential-free Actions run temporarily edited the *ephemeral checkout* of .opencode/opencode.json and restored it after testing. All five variants exited 0 under a 28-second bound:

| Variant | Exit | Captured output bytes |
| --- | --- | --- |
| Original | 0 | 174578 |
| Remove MCP definitions | 0 | 174578 |
| Remove plugins | 0 | 174578 |
| Remove both MCP and plugins | 0 | 174578 |
| Remove explicit instructions | 0 | 174578 |

This repeat **does not support blaming any particular legacy plugin, MCP path or instruction setting** for the earlier timeout. Cold-start behavior, caching and intermittent external work were not independently controlled. Identical output size is not evidence that all effective prompts were identical.

## Architecture implication

A future policy publication and exposure-checking tool should assess *physical discovery and loading paths* in each tested harness, not rely on model instructions to disregard files described as historical. For OpenCode 1.19.6, the synthetic test provides a concrete negative control: a retired skill whose name appears in the discoverable catalog.

The current operational Skills MCP dispatcher was separately checked via read-only HTTP:
https://raw.githubusercontent.com/rock-solid-sites/ASES/main/skills/current/README.md .
It lists six current ASES skill sources. This is a distinct installed ChatGPT skill source, not a guarantee that Codex/OpenCode run it or that the experimental Knowledge Index has indexed its MCP URI.

## Required future experiments (not executed here)

1. On at least two clean runs per fixture, obtain instrumented or reliable model-visible instruction traces to distinguish metadata discovery from actual injection. Include an independent negative marker and a task with a measurable affected decision, not only a self-report.
2. Repeat on the user's actual OpenCode 2.x launch route. Package and discovery rules are version-dependent. Verify the exact runtime, global skills and nested AGENTS scope before generalizing this 1.19.6 result.
3. Measure source/skill selection overhead with stable versions and quality controls; test a minimal context against an otherwise identical contaminated context.
4. Independently complete WNASES-18's project-local policy publication pilot. Then reconcile both sets of evidence before altering root AGENTS.md or removing historic active discovery trees.

**Boundaries:** No actual ASES policy, production source, provider account, user environment, Work Notes backend or other project repo was changed. Work Notes WNASES-19 owns subsequent execution-state updates. This report is an experimental candidate for the registered final directory, offered in a draft PR; its presence does not authorize a merge or active-config cleanup.
