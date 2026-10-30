# Lifecycle L0 ? candidate and fixed observations

Status: design candidate only; no L0?L7 lifecycle execution or F3 closure claim.

## Pinned inputs

- F3 starting HEAD: `04600b1b45e6510665bdc3108db9d51f6b2f8c56`.
- Frozen packet: `origin/planning/ases-phase-i-work-unit-lifecycle-20261030` at `415a03fe660f902cfffed6662d1a5982416ee9da`.
- F1: `d227a22b9bbc0732881bf58f6933ce46fddc08fa`; accepted-x continuity and currentness remain abstract, with storage and holder assumptions.
- F2: `5fb690d4ba7544a4a7eb5fce9ca1e54485543d64`; 46 abstract replays, T05 prepared-only, and no concrete storage or ACL conformance.
- Canonical derived target read from `codex/execution-engine-roadmap`: `Phase-I-Verification.md` ?4?5 and `Phase-I-Closure.md` ??1?4, 7.

## Candidate realization boundary

One serialized authority/mediator process owns all lifecycle policy and protected-record mutation. The selected attachment is local immutable byte content exposed only through a retained Unix socket endpoint; the existing F3 Landlock worker setup is a candidate for worker path confinement, not presumed complete confinement. The prior `authority-loss` H=M result is only a candidate for process-loss denial: it demonstrated one target path, one symlink, one retained socket, direct path denial and O_WRONLY-open denial. Arbitrary aliases, hostile descriptor passing, descendants, network, credentials, mappings, and filesystem mutation effects remain unsupported/outside this profile unless individually tested. No physical source-binding claim is made.

Protected state candidate: a complete versioned state image and accepted byte objects inside `lifecycle/lab/`, owned by the authority process and inaccessible to the worker. A whole update prepares a complete replacement image and accepted object, then publishes one current selector by same-filesystem atomic rename; acknowledgement follows that selector publication. The recovery reader must parse only the published image and its referenced immutable objects, check schema/version and hashes, rebuild inactive/sealed state, and never use runner-held expected state. Failure before selector publication means old state; after publication means new state even if the reply is lost. Malformed, missing, unsupported, or hash-mismatched material refuses recovery while retaining confinement.

Currentness trust premise: the host kernel and local filesystem preserve the latest published selector across **process termination while the host remains running**; the authority process is the sole writer; no concurrent or external writer is in scope. This is not a rollback-resistant or machine-crash/power-loss guarantee. No fsync result or process-death observation will be described as power-loss durability. The test runner may issue explicit management commands and observe process/PID outcomes but must not carry accepted records or inject reconstructed policy into a fresh authority process.

## Independent expected observations fixed before execution

- Start with P/C inactive, empty, and no grant. A protected use absent a full-path grant denies without bytes/effect.
- Use literal distinct byte strings `x = b'F3-lifecycle-x-v1\n'` and `y = b'F3-lifecycle-y-v1\n'`; accepted hash/readback must match SHA-256 of those exact values, and x != y.
- Every acceptance acknowledgement must follow publication of both the exact bytes and provenance/current boundary state. The holder/recovery reader, not the worker or test oracle, supplies readback.
- After replacement publication, retained W1 ingress denies and fresh W2 ingress reads x.
- After H=M kill and wait/reap, the worker's CPU-only continuation may occur, but the retained socket and direct/alias protected paths return no protected bytes.
- Cold recovery from files alone yields sealed state before any execution route. Explicit management activation creates a fresh ingress; old ingress remains denied; x remains readable and y can then be accepted/read.
- C's move P?Q is one whole sealed update; post-activation read remains allowed and the previously denied write remains denied.
- Removal while accepted/dependent data exists denies. Explicit logical disposition precedes current complete dependency check and removal. No physical-erasure claim.

## Route and enforcement questions to execute

| Route | Candidate status / required evidence |
|---|---|
| Protected record/object path | Authority-only; worker direct and symlink opens must be attempted under Landlock. |
| Open/inherited FDs | No protected FD passed; inspect worker descriptors and try a deliberate forbidden-FD negative control if feasible. |
| Local IPC | Retained socket is mediated per request; test old/fresh ingress across replacement and H death. SCM_RIGHTS and hostile peer behavior must be disabled or tested before claiming closure. |
| Child processes | Not part of the success route; no descendant authority is allowed by the declared fixture. Verify or exclude worker spawning. |
| Network, credentials, shared memory/mappings, external sinks | Disabled/not tested and outside the declared attachment profile; no full-confinement claim. |
| Live OS policy | Landlock is applied before worker exec and remains part of the trusted host boundary. Partial setup and host administrative policy change are not tested; setup failure must abort before worker execution. |

## Gate disposition and restart cursor

L0 remains a design candidate, not a passed implementation gate. Crosslink session #42 is the active session bound to issue #10 and is being used as instructed; no new session was started. L1 now has a separate bounded result at `l1/RESULT.md`: the process-local selector and live mediator path succeeded for one read-only accepted-content flow under the limited profile and process-death-only filesystem premise. This does not establish selector behavior across holder death or any L2+ property. Continue at L2 only after checkpointing L1; preserve the profile limits in that result.
EOF
