# Potentially producer-exposed C11 consumer check

## Pre-run record

This check was prepared at source commit `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`, before executing the holder probe. I read `Phase-I-Closure.md` §3 and the C11/C12 rows in §7, plus the specified C11 service/probe/check sources and the inherited Kernel-0 service/recovery holder. Before the pre-run record, I ran the broad search `rg -n -C 4 'C11|C12|Phase-I-Closure' docs`. It searched the whole `docs` tree and may have surfaced matching snippets from prohibited producer outputs; the tool reported truncated output, and I cannot determine which matching files/snippets were visible. I did not intentionally open the producer preregistration, result, attempt, raw, or check outputs, or the coordinator ledger/index. Strict clean-room isolation therefore cannot be assured. Treat this as a potentially producer-exposed reproduction/adversarial source check, not a clean-room independent reproduction. The source-based pre-run prediction was recorded before the probe, but it does not repair this exposure risk.

The selected contract is that required trusted consumer observations are retained with the accepted content whose acceptance commits. If content and required observations are persisted separately, process death after the content commit but before the second commit may leave accepted content without its required evidence; that would violate C11's required observability across covered loss. A same-transaction write should recover either the prior acknowledged pair or the new committed pair. Killing before `COMMIT` should leave the prior pair intact. A fresh reader with no original observation tuple should expose the persisted result. Two worlds may carry distinct trusted observation tuples while sharing the same Kernel view; observation retention must preserve their distinction.

Predicted primary outcomes:

* `atomic-A` and `atomic-B`: accepted content plus each world’s distinct observations recover as an available pair after a post-commit, pre-ack process kill; their Kernel views match while their required observations differ.
* `split-gap`: content commits, then process death before the delayed evidence transaction; recovery shows the new content with an incompatible prior evidence bundle and no required observations for the newly accepted content. This is the predicted C11 counterexample.
* `atomic-before`: process death after the evidence insert but before content `COMMIT` rolls back both writes, preserving the earlier acknowledged bootstrap pair.
* `split-ack`: uninterrupted acceptance and delayed evidence commit complete before the caller receives its acknowledgement, yielding an available pair. This is a positive ordering control, not proof the split design is safe under process death.

The probe records real process boundaries and the actual inherited holder gate. The specific stored observations are trusted fixture inputs, not claims about provenance authenticity or truth. Process `SIGKILL` tests process termination on the running host; it does not test power loss or media failure. This is a narrow experimental contract check, not a schema/minimality result, full C11/F1 closure, or formal cross-family claim.

Inputs pinned before execution:

| Input | SHA-256 |
| --- | --- |
| `docs/research/phase-i-f1/c11-sqlite/c11_service.py` | `864e43153e069247c6c2557dc5cb2ce7c51795c612a20515c2be0cb82c9a2c28` |
| `docs/research/phase-i-f1/c11-sqlite/probe.py` | `c6f2e7de00754ec310e00cafc60b527d34609d4ead68c1b5be4a0fce1fdcd627` |
| `docs/research/kernel-0/kernel0_recovery_service.py` | `f5fd5e1118046dd8fd6d3357d56f9bcad91e8fe572f5bf4706dc7c8fd0b3ff13` |
| `docs/research/kernel-0/kernel0_service.py` | `f11c54b9318a54512487d087b10aeb2878a111bffe8cc8fa58391f4e716c2084` |

The supplied `check.py` was inspected as task input, but the audit below is separately authored and does not import or execute it.

## Result

The one primary probe ran once on Linux 6.18.57, Python 3.12.14, SQLite 3.53.1, with a 256 MiB address-space cap. Its execution pin is the recorded source commit `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`; the raw output SHA-256 is `b77f7a9a7c20be0af6caf89debf2bf450bfdb48f0e8763244bb03205ad6dc182`.

The separately authored read-only audit found the predicted counterexample. In `split-gap`, the inherited holder reached its actual `durable` gate after the Kernel row's content `UPDATE` and first `COMMIT`. The supervisor killed and reaped that writer before its response, so the caller received no acknowledgement. A fresh holder with no observation tuple in its configuration and a separate read-only SQLite reader both saw the committed new content, but the only observation row still named the prior `accepted\0zero\n` content; the consumer query returned `incompatible_required_observations` and no required tuple. Its transaction trace has one content update and one commit, with no new evidence insert.

The controls behaved as predicted. `atomic-A` and `atomic-B` both died after the actual `durable` gate and before caller acknowledgement; each fresh recovery exposed the new content with its respective full trusted tuple. Their serialized Kernel views have the same SHA-256 (`feaf9b3efd728119b71d013995f7cba9c3117ced661cb50b8e03794c2a09405b`), while the evidence rows and required tuples differ. `atomic-before` died at `prepared`, after both SQL writes but before `COMMIT`; recovery retained the earlier acknowledged bootstrap content/evidence pair. `split-ack` completed its second evidence commit before returning a successful acknowledgement. Every independent SQLite read reported `integrity_check = ok` and agreed with the fresh holder response.

The new finding concerns the acceptance contract supplied by the delayed evidence transaction. The inherited Kernel-0 holder accepts establishment with its zero content, then commits a later `accept` by updating the Kernel view and returning only after that transaction commits. The C11 wrapper in `split` mode writes the matching observations only after that first commit. Process death between them leaves the holder's own committed content intact and the caller uncertain, which fits the holder's behavior; the wrapper fails the selected C11 requirement that the newly accepted content and required consumer evidence be retained as one accepted pair. The atomic mode ties both writes to the holder's existing transaction and survives the same cut. The prior acknowledged bootstrap tuple is essential to expose the mismatch: the test does not assume that the holder begins with no content or evidence.

## Broader C11 scope gap

The bounded source/raw review found that the observation table has one row (`id=1`) and `write_observations` uses `ON CONFLICT(id) DO UPDATE`; each new acceptance replaces the prior bundle. The probe demonstrates the bootstrap tuple remains available after a pre-COMMIT kill, but it does not check whether that earlier bundle remains required after a later successful acceptance. The selected test establishes coupling of the latest accepted content to its latest supplied tuple; it does not establish retention of all historically required observations.

The probe supplies `identity_genesis`, `created_by`, and `project` as opaque strings in per-world writer configuration. It does not establish that these values name a stable Work Unit, that they remain unchanged across acceptances, or which historical values must remain observable. Therefore the latest-only row is a concrete broader retention question under C11, while this evidence does not decide whether overwriting an earlier tuple violates the requirement. Neither stable Work Unit identity nor a historical observation policy was demonstrated.

The evidence establishes retention of the supplied trusted opaque observations under process termination on the same live host. It does not establish provenance truth or authenticity, and `SIGKILL` does not simulate physical power loss. It says nothing about schema or minimum representation, full C11 or F1 closure, or formal cross-family coverage.

The separately authored read-only audit is in `audit.py`; its output SHA-256 is `316314278829b99e08615fd01622fb080e6960a247557b3dedbc76721c7b107e`. Its recorded review class is potentially producer-exposed reproduction/adversarial source check, not clean-room independent reproduction. The audit asserts the actual SQL trace order, the inherited gate and caller acknowledgement state, recovery without original observations, fresh independent SQLite row/view reads, distinct real tuples under identical core views, and the latest-only source behavior described above. The supplied `check.py` was not executed.
