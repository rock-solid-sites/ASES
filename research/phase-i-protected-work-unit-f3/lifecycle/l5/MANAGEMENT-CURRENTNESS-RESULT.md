# Management currentness result

**Status: assumption-stress counterexample for the frozen helper interface; not an in-profile exploit or L5 acceptance.** The experiment was preregistered in `MANAGEMENT-CURRENTNESS-PREREGISTRATION.md` before execution. Raw trace is `management-currentness-raw.json`.

## Observation

The fresh-current positive control committed two authentic records through `manager_roundtrip`:

| Operation | Resulting record | SHA-256 | Current authority observation |
| --- | --- | --- | --- |
| Authorized sealed move C→Q | `record-000002.json` | `3b3b3ce50ad8ae8bbecb568a1bdbe720be9126aee1d267468f6cb9c6b35fb04e` | C parent Q; no ingress |
| Authorized activation | `record-000003.json` | `1ac02330f7bd2ecdc00d41ae8f0e88dfbf69851befdc43e61a779d1f098efee7` | C parent Q; ingress W-L5; activation event retained |

The test then submitted an authorized move using the unchanged authentic bootstrap state object captured before those transitions. The helper returned `COMMITTED`, advanced `CURRENT` from `record-000003.json` to `record-000004.json`, and published the stale move state. The new record SHA is the same as the earlier move record (`3b3b…fb04e`); the selected record has no current ingress and contains only `bootstrap` and `authorized_sealed_whole_move`, so the activation event/state from record 3 is absent.

This demonstrates that `manager_roundtrip` plus `commit` does not bind its caller-supplied `st` to the current selector before committing. However, the experiment directly retained and resubmitted a stale Python object through the helper argument. The declared profile is single-holder, and no in-profile caller path was demonstrated that lets a stale object reach that holder. Treat stale-view freshness as an assumed single-holder property unless such a path is established; do not label this an in-profile exploit.

## Activation route coverage

In the safe moved case, `authorize_activate` is submitted through `manager_roundtrip`; the trace above shows that fresh-current activation commits. The integrated positive control in `l5_integrated.py` still directly changes activation fields and commits outside that handler. Therefore activation-through-manager has a bounded positive path, but the implementation's positive control does not establish that every activation route is forced through the handler. The manager also takes a caller-supplied state object, so its activation inherits the currentness limitation above.

## Next discriminator

Before claiming authorized activation coverage, use a disposable test to make the integrated positive control request activation through the same handler and require the emitted event, current selector, and activated record to agree. Include a currentness-preserving negative control that attempts activation from a stale pre-move state after a newer selector exists; expected outcome is denial with byte-identical selector/state. Keep the single-holder assumption explicit if the helper still cannot identify the supplied state as current.

## Bounds and untested areas

Three manager calls, two successful transitions, one stale replay, one temporary record root, no worker and no host confinement. No cryptographic authentic-record verification, concurrent manager, IPC-delivered stale request, stale-state acquisition path, storage crash, or live F3 route is tested. Landlock unavailability means this remains a policy experiment only.
