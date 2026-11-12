# Native pending admission bound — baseline report

## Question and method

The baseline uses the pinned original sources at commit `b0bb224acb737c08b718dd84603739f8358651c4`. It drives the real F1 accept, L5/L6 owner, NativeAdmission, managed F4 sink, Unix witness, JSONL journal, and the inherited `guarded` gate. Each request envelope is rebuilt from the actual current owner snapshot immediately before submission. At the genuine gate, the experiment closes the sink's actual stdin, causing the inherited guard to observe EOF; no owner state, envelope, event, or result is injected.

The raw source hashes and two complete captures are under `evidence/baseline/`. `run-01` is retained as an initial sequencing attempt: its reconciler calls ran while the live sink still held the writer guard, and its attempted cold restart was also blocked by that live sink. `run-02` is the corrected baseline: it stops the real sink before invoking recovery CLIs or starting a cold replacement. Both captures retain the same pinned source commit and hashes.

## Observations

In `run-02`, two distinct fresh IDs each reached a real `GATE` frame at stage `guarded` in the same actual sink process. EOF after each gate returned `native-effect-requires-reconciliation`. The owner retained both IDs as `reserved`, with no sequence; the journal remained byte-for-byte unchanged and contained no `effect_accepted` event. The witness's full current cut remained the same as the pre-request cut.

Strict reconcile and observe-local both refused request A with `target-effect-is-not-final-event`. After the sink was stopped, their calls left owner records, F1, journal bytes, and witness current cut/revision unchanged. No eventless reservation was cancelled or cleared.

In the separate `normal_B_after_unknown` history, A reached the same guarded EOF and remained reserved. After the actual old sink exited, ordinary cold recovery accepted the unchanged cut. Actual F4 `/replace` and `/activate` reopened the sink; a newly derived current-generation B envelope then completed normally. B's effect became `published` at its actual journal sequence while A remained `reserved`. This confirms the baseline permits a later normal fresh-ID effect while the original eventless reservation is unresolved.

One packet expectation does not match the pinned source: `seal` commits while pending reservations exist. `dispose_child` is refused with `pending-in-domain-effect`, and its owner selection is unchanged. The baseline therefore establishes a disposition guard, but not a seal guard. No source change was made to alter this behavior.

## Interpretation

The hypothesis is confirmed for the exercised history: the original owner can accumulate multiple eventless reserved effects, and a subsequent new ID can publish while an earlier reservation remains unresolved. The existing reconcile and observe commands refuse the eventless reservations without mutation.

This supports testing the packet's conservative new-ID admission bound. It does not establish that an eventless reservation can be recovered, cancelled, or safely erased. The unresolved original reservation remains held. The observed ability to seal while pending is explicitly outside the proposed change unless root redirects scope.

## WHAT-NOT-TESTED

No host or power failure, external publisher, arbitrary same-UID actor, eventless reservation repair, automatic rollback, or universal confinement claim was tested. No pinned production source has been modified. The fixed parent histories and prototype checks have not yet run.
