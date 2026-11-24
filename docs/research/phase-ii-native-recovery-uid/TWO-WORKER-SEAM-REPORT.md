---
title: Two-worker fixed-interface conformance probe
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Implementation Report
status: Blocked before runtime
last_updated: 2026-11-24
---

# Two-worker fixed-interface probe

## Claim and scope

The probe adds a bounded `worker-seam` case to the existing #38 fixed mediated write route. It starts two distinct UID2001 worker processes under the existing UID2000 manager and sends identical `{"op":"write","payload":request_id}` request shapes with distinct fresh IDs. The checker records the exact owner/F4 inputs and durable readbacks. No execution identity, new authority state, or owner policy was added. The intended claim is limited to whether this existing interface distinguishes two worker processes; it does not claim replacement execution semantics.

## Source and runtime result

Code is based directly on #38 head `0bd51a34700164a5eb77efe98158fa37d1a74e23`; probe commit is `130e760d26020d93534c1235cd09ac4728a73638`. `run_uid_recovery.py` requires the exact local image `sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335`. The required image is absent. The runner stopped at `docker image inspect`, before source staging, container creation, or worker requests. The raw runner output is in `evidence/two-worker-seam-01/preflight.json`.

The #38 packet prohibits image pull/build/substitution for this route. Therefore no two-worker result or durable result is claimed. The preflight capture also records an absent-container cleanup check; no processes or task containers were left running.

## Host-variant decision

PR #84's `verify_probe.py` is a source-bound direct native owner/F4 process fixture, but its owner subprocesses inherit the caller's UID. It does not exercise UID-separated worker custody. This host is UID/GID 1000 with no effective/permitted capabilities and `NoNewPrivs=1`; its UID/GID maps expose only the caller's single identity, and `unshare -Ur true` fails because `/proc/self/uid_map` is read-only. Docker reports vfs, but the required pinned image inventory is empty. A direct same-UID run would not satisfy the custody question and was not run as a substitute. Details are captured in `evidence/two-worker-seam-01/host-variant.json`.

## Verification

`python -m py_compile` passed for the changed fixture and checker files before commit. `git diff --check` passed. The #38 runtime itself did not run; its only result is the recorded preflight failure. No worker request, owner transition, or durable write occurred.
