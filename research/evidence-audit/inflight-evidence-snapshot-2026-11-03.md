---
title: In-Flight Evidence Audit Snapshot — 2026-11-03
program: EDASES
layer: Research
document_type: Research Observation
status: Experimental
authority: Research
canonical_repository: ases
related_documents:
  - docs/proposals/2026-11-02-testing-debugging-ontology/README.md
  - docs/ORCHESTRATOR.md
  - docs/methodology/ASES Bounded Project Build Method.md
  - docs/methodology/Implementation Realization and Assurance Selection Method.md
  - docs/research/EDASES Review Methodology.md
last_updated: 2026-11-03
---

# In-flight evidence audit snapshot

Read-only snapshot at 2026-11-03 19:43 UTC. This is an audit report, not policy or an adoption decision. The review did not change source in the monitored worktrees and did not read the F3 review context until its first verdict was recorded at `a89944c05`.

## Proposal guidance and canonical baseline

The testing/debugging/ontology package on `origin/proposal/testing-and-assurance-method-2026-11-01` labels itself a draft with no adopted policies or automatic gates. At ASES main `e63ff28d9`, the draft `testing-and-assurance-method.md` is absent at that path; the folder contains discussion and research-result records instead. The main reconciliation note likewise says no role, API, evidence schema, gate, or provider was adopted. The bundle is useful as optional experimental guidance for this run, not as binding policy.

The underlying evidence distinctions already present in canonical sources are sufficient for this audit: AGENTS requires observations, interpretations, findings and recommendations to remain distinct, claim-boundary WHY/WHAT/HOW-CERTAIN/WHAT-NOT-TESTED disclosure, and cheapest discriminating tests. The Bounded Project Build Method retains VSDD or project-specific verification rather than adding a competing phase. ORCHESTRATOR Phase 1 Auditor checks position claims against artifact evidence; it is a bounded structural join, not a truth proof. EDASES Review Methodology distinguishes findings and recommendations from the human decision. The proposal's finer run/oracle/archive classifications can help describe evidence, but do not introduce new roles, policy, or gates here.

## Worktree observations at snapshot

| Worktree / tip | Evidence observed | Boundaries or divergence to retain |
| --- | --- | --- |
| `ases-kernel`, `ec2539717e79824b06d0e3ff5d733e6ea9f05a90`, clean and tracking origin | Bounded model tests retained raw results, scripts, caps, incomplete controls and prior failed assertions. Paired-state scans report 26 mismatches for `rights`, 4 for `rights+parents`, and 0 among 8 comparable cases for `rights+parents+data`. Capture/publication cuts distinguish whole-path controls from mixed/split mutations. Partial-consumer trace has two serial controls and one failing partial-plus-blind-write mutation. | These consume the same frozen semantic oracle. “Independent” serial replay means a separately enumerated operation order, not an independently implemented semantics. The latest partial-publication result explicitly scopes its failure to the combination of exposed partial state and blind remaining write. No physical timing, RTL correspondence, global contract or implementation behavior is established. |
| `ases-f1`, `6fc793d86843977938625543c2334463f011c52a`, clean and tracking origin | A finite binding model was followed by local Linux Unix-socket tests. Descriptor-transfer output distinguishes connection-time peer PID from per-message sender PID. The proxy experiment then shows direct-peer identity accepts a one-hop old-origin request forwarded by the replacement, while refusing the old process when it sends directly. | These are one-run mechanism observations under the stated Linux/kernel/supervisor premises. They do not establish original-initiator authentication, production protected effects, PID durability, F1/F3 acceptance or a policy against proxying. The reports preserve the conclusion limits. |
| `ases-cross-layer`, `74f01670f7d499d8c2ad1dd62776003ef757c471` (observed tip), four commits ahead of origin plus untracked F4 result/stdout/exit files | Earlier F2 artifact reports 46 abstract replays, 2 prepared-only, and 16 mutations discriminated. T18 added a local loopback sink with positive, stale-order and detached-check mutation controls. F4 then recorded pre-accept kill, accepted-before-ACK kill, uninterrupted positive, and early-ACK mutation with fresh-process journal recovery. | Preserve “46 executed + 2 prepared-only,” not 48 executed. T18/F4 are disposable loopback sink behavior, not F3, host confinement, production, arbitrary sink or power-loss evidence. F4 shows accepted-before-ACK with one recovered effect and no client success; no retry was attempted, so duplicate suppression/exactly-once is untested. At this snapshot F4 output files existed but were untracked; source/preregistration were committed. |

No matching test process was visible during the 19:43 status check. This is a point-in-time process observation and says nothing about prior completed runs or later work.

## Digest checks and their scope

The following current file bytes matched digests recorded by their respective reports/manifests:

- Kernel: `parent_projection_probe.py` `089ddd…76929b`; its raw log `b2c30f…441f9`; `pair_projection_scan.py` `917c3e…7f3c6`; expanded log `35b63e…d193d`; `capture_publication_cuts.py` `d71fd7…64e35`; full and truncated logs `ff27ab…8373e`, `d8f9ec…85d13`; and `partial_consumer_serial.py` `6c1289…a0ee`, complete/truncated logs `4289f5…3ec91`, `47d75a…1cba2`.
- F1: `source_binding_experiment.py` `7ab186…41cd4` and raw output `9d3cb4…b5743`; `unix_source_mechanism.py` `f7c19a…5b374` and output `16831d…f147f`; proxy script/output `e7ea6f…62d35`, `b684dd…1c58b`.
- Cross-layer F2: T05 output and exit-code file match manifest digests `ccc95b…53fe` and `5feceb…57e9`.

These checks show that the local artifact bytes match the cited digests. They do not independently prove who ran a command, that the recorded command produced those bytes, or that a log is complete. F4 had no manifest or recorded digest at this snapshot; its JSON includes raw journal hex and hashes, environment, child outcomes and assertions, while run stdout and exit code were separate untracked files.

## F3 first verdict: source claim versus recoverable run evidence

The first independent verdict is `research/phase-i-protected-work-unit-f3/reviews/autonomy-20261103-f3.md` at `a89944c0559c267c937752c6e0f2e59a03229175`. It rejects the broad claim on source-level and policy-conformance grounds: request activity/sealed checks cover D, while permission calculation walks ancestor grants/latent ceilings without denying use because an ancestor is inactive or sealed. The deliberately constructed Q-sealed/D-active state is not a worker-reachable exploit demonstrated by the three scripted cases. The report distinguishes that counterexample from native enforcement.

The native positive attempt is **not run successfully** in this review environment: stdout artifact `positive.out` is empty; the report records `preexec_fn` failure and a separate Landlock probe with ABI `-1`, errno 38 on kernel `6.18.57`. The native command's stderr and exit status were not retained, so this failure summary is report evidence rather than a recoverable raw process record.

The source/policy wrapper and modified copy remain in `/tmp/ases-f3-review-2vZwTL`: `policy_test.py` SHA-256 `ce8731…1059`, `lifecycle/l5/test_ancestor.py` SHA-256 `9f1dd2…9833`. The wrapper prints three summarized JSON lines to tool stdout and `run_case()` removes its temporary generated fixture directories. The exact output, stderr and exit code were not saved as files; the per-run `record-000010.json` cited in the verdict is consequently not recoverable from this context. The report contains the key values, and the source counterexample remains auditable from the pinned code, but the dynamic observation cannot be independently replay-checked against an original raw log.

Minimal preservation for any follow-up is one raw transcript containing the exact three JSON lines, stderr and exit code from the policy wrapper; the exact wrapper and mutated L5 source (or an immutable diff) with hashes and source base `b49e1f66`; command, Python/kernel identity, and the explicit in-memory `l1.confine` no-op. For the failed native attempt, preserve stderr and exit code or state they are unavailable. If re-executed, label it a new corroboration run; do not rewrite the first verdict as though the output had been retained at the time. This is evidence preservation advice, not a new gate.

The F3 temp context also contains historical delegation files reporting a prior `codex-pgs2`/`glm-5.3-flash` HTTP 402. This audit only read those files and initiated no provider, VPS or paid route. Keep that historical implementation attempt separate from the current authorized local tool dispatch.

## Follow-up observation — 19:45 UTC

This addendum records new results without rewriting the 19:43 snapshot.

- Kernel `3b6b880e265b189b551204be6510809bb60f2b1c` completed a partition of 20 schedules across current/stale resolution and read-before/read-after revocation. All current-resolution schedules had a serial witness; all seven stale/read-before cases lacked one, while all three stale/read-after cases had witnesses. It preserves state/schedule truncation controls. The report bounds the result to two fixed event chains and whole logical commits; executor and replay share the frozen semantic oracle, and split-field reads remain open. Script and three output digests matched the values in its result note.
- F1 `9ca53bb3c98d644c8ac65948e6bf14f2489e0feb` added one deterministic local process-loss history: the acknowledged producer and holder are killed/reaped, a fresh holder recovers retained content, authority is replaced, and a fresh executor reads from the holder. It rejects a different valid atom without changing state and accepts the holder-sourced bytes. Script/output hashes matched the report. This is a trusted local prototype and same-live-host storage result, not arbitrary-content, rollback, power-loss, physical-enforcement or F1/F3 acceptance evidence.
- Cross-layer `a71786ba958b6add8b2bfac3a1c29f1060c8f784` committed the F4 extension and its updated result/stdout/exit code; the worktree was clean and tracking origin at observation. Twenty-six assertions pass. The truncated five-byte journal control is refused by a fresh process with exit 2 and an explicit unterminated-record error, not interpreted as an empty journal. This improves recovery-reader fault sensitivity, but remains local process-death evidence after `fsync`, without power loss, production sink, or retry. Script SHA matches the embedded result (`63d521…21b23`); current result/stdout/exit file hashes are `78a10b…541ae`, `299316…f97`, and `9a271f…b86aa` respectively. The result has no separate output-digest manifest; the committed tree is the current artifact identity.

At 19:45, all three monitored worktrees were clean and tracking origin at the listed tips. No relevant live test process appeared. The F3 verdict worktree had acquired a new untracked `reviews/evidence-autonomy-20261103-f3/` directory after the verdict; this auditor did not inspect or alter it, in order to keep the reviewer evidence context separate.
