---
title: Compact read-only continuation view
program: EDASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Experimental
canonical_repository: ases
depends_on:
  - PACKET.md
related_documents:
  - ../phase-i-launch-intent/REPORT.md
---

# Result

`Store::resume_view(job)` returns a typed, Serialize-only projection from one
deferred SQLite read transaction. It includes stable job/account/project/
environment identity, recorded state and profile, job/current catalog revisions,
the exact launch ID, a fixed pair of launch/outcome event pointers with payload
SHA-256 digests, and advisory next-step guidance. It does not return event
arrays, forecast context, transcripts, mutable authority, or a dispatch grant.
The view type has no `Deserialize` implementation and is not accepted by
`begin_launch` or observation methods.

Recorded state and present liveness are separate fields. Present liveness is
always `unknown`; a retained `LAUNCH_STARTED_OBSERVED` event proves only that the
trusted adapter recorded a start observation. It says nothing about whether the
process is alive now. The view does not inspect or signal PIDs, infer completion,
release a reservation, finalize a job, or trigger a launch.

Advice reflects the supported stored state: `AUTHORIZED` may proceed to the
authoritative `begin_launch`; `LAUNCHING` requires outcome observation or
reconciliation; intent-backed `RUNNING` needs process/completion observation;
mock `RUNNING` remains explicitly mock; terminal work gets no new-dispatch
advice. Missing or contradictory authorization, profile, intent, observation,
or terminal evidence returns an error rather than a guessed projection. An
unlaunched `CLOSED` job cannot be summarized as completed or failed merely
because a matching terminal row was injected.

# Evidence

The source runtime pin is `34be0f8eba606596aec6371d6e418fb08bdda011`; per-file
SHA-256 values are embedded in the native histories. The largest supported
identity fixture produced a 1,716-byte serialized terminal view with both
evidence pointers. A separate fixture retained a 262,144-byte forecast context
in the original store while projecting 338 bytes.

Five semantic tests passed. They cover compactness, large-context exclusion,
maximum identifiers, mock/intent distinction, missing or conflicting evidence,
terminal/outcome consistency, exact payload digests, stale catalog display and
rejection of admission using the old revision. Four native tests passed. The
controller-kill-before-spawn history reopens as `LAUNCHING` with a 520-byte
pending view and the original reservation. In the second history, a fixed test
worker was live when its controller was killed. The worker then exited through
the bounded test release gate; the recorded state became `RUNNING` after a
trusted start observation, while the 699-byte view still reports unknown
present liveness. A catalog refresh moved the current revision from 3 to 4 while
the job revision and launch evidence pointer stayed unchanged. Repeated views
and pending/running replays produced no event changes, reservation releases or
second worker starts. Evidence includes raw job/balance/event views, controller
kill signal, worker PID/start token, compact projections, byte lengths and
source hashes in [evidence/final](evidence/final).

Exact offline commands:

```sh
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --offline --manifest-path resource-control/Cargo.toml --test resume_view -- --nocapture
CARGO_HOME=/workspace/.toolchains/ases-launch-rust/cargo RUSTUP_HOME=/workspace/.toolchains/ases-launch-rust/rustup ASES_LAUNCH_EVIDENCE_DIR=/workspace/ases-resume/docs/research/phase-i-resume-view/evidence/final /workspace/.toolchains/ases-launch-rust/cargo/bin/cargo test --offline --manifest-path resource-control/Cargo.toml --test native_launch
```

# Limits

The view is advisory context, not recovery input or authority. Only
`begin_launch` performs current checks and can issue the one dispatch grant.
The recorded state and evidence are read from the local SQLite store; current
store custody and the trusted local adapter remain premises. The adapter
observation truth is not verified by this projection. No external provider,
model, transport, or production recovery path was exercised.
