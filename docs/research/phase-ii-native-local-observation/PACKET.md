# Observe a durable native effect before completing its publication

ASES-4 A/B continuation, parent draft #35 at5571530a. Preserve its default
strict reserved-only refusal. Add a separate explicit manager command for the
genuine crash window after F4 journal fsync but before the native owner's
record_local_effect callback. This is observation of an existing effect, not
admission, reservation creation, guessed sequence, or a new effect state.

## Actual source boundary

phase-i-effect-admission/admission_sink.py calls the original emit_locked and
only then admission.after_append(event). The pinned original emit_locked loops
actual writes and fsyncs before returning. native_sink.NativeAdmission's
callback next calls the protected Session.record_local_effect. A crash between
those instructions leaves a complete indexed native journal effect and an
owner status reserved with payload hash but no sequence. The current explicit
reconciler deliberately refuses that state; do not silently broaden its CLI.

## Opt-in API and proof

New `observe_local.py OWNER_ROOT REQUEST_ID` reuses the existing reconciler.
It derives the existing protected attachment and takes the same existing F4
writer guard. No caller sequence, payload, certificate, cut, endpoint, force flag,
new journal/table, or status meaning. Default reconcile.py still rejects reserved.
A narrow internal opt-in parameter may share its real parser/validation/protocol.

Require exactly the same complete validated final native effect, unique request
index, one pending effect, exact payload hash, retained historical registration
and F1 world, live owned material, immutable presented/reserved generations,
attachment identities and bound private witness as the local profile. For a
reserved target, no sequence may already be asserted. Its historical admission
reservation record must independently match the actual journal payload.

Before any owner mutation, freshly establish that the witness is exactly the
preceding or full local cut under the existing narrow profile. Then recheck
owner reservation/binding and actual journal bytes under the real locks. Derive
the sequence only from that actual parsed journal event and call the existing
Session.record_local_effect, durably selecting local status. Thereafter use the
existing one-CAS/fresh-confirmation/native-settlement flow. No current write grant
is issued, and no F1 or L6 material is changed. Already local/published paths are
idempotent observations under the existing reconciler's rules.

A reserved record with no actual matching journal effect remains unresolved:
do not infer definitely-no-effect, cancel the reservation, or unblock disposal.
Torn journals, unrelated witness cuts, additional pending effects, mismatched
hash/sequence/registration and unsupported attachments also remain refused
without mutation. A valid current witness prefix by itself is insufficient.

Capture phase-aware uncertainty if local observation selection or later
publication/settlement is interrupted. Permit an explicit test-only gate after
local observation/before publication, plus the existing after-publication gate.
A restart may finish the now-local effect through the ordinary strict command
without another append or duplicate observation. No cross-store atomicity claim.

## Required native histories

Use a test-only wrapper of the actual native sink that pauses immediately before
NativeAdmission.after_append records the owner sequence, after the real parent's
emit_locked/fsync. It must only insert a gate and then call the original method;
no copied state machine, fixture-installed local observation, or fake journal.
Kill that retained sink process at the gate. Capture complete journal seq4 versus
owner reserved/no sequence and unchanged preceding witness. Show default
reconcile refusal, then opt-in actual sequence observation/publication/settlement,
with unchanged journal bytes and exactly one effect.

Exercise a changed current world with identical content (retaining the old
world/registration), plus actual source sealing/movement. Historical observation
must not require the old world to remain current or regrant write. A fresh
current-envelope/current-version use remains denied, while old exact-ID lookup
remains an observation. If adding the new world requires a native state sequence,
use the actual F1 and owner APIs and preserve their exact results.

Kill the observer after local selection/before publication, then resume through
strict reconcile with no second observation/CAS/append. At the existing guarded
pre-append gate, kill a genuinely reserved-only request with no journal event;
opt-in must refuse and retain its pending dependency. Include a mismatched-payload
negative control. Rerun the parent's full native reconciliation probe once against
the shared implementation to show default strict behavior and prior cases remain.

WHY: recover an existing durable commit through its actual authoritative journal.
WHAT: same replay/index, owner reservation, writer guard and typed local callback.
HOW CERTAIN: experimental until real fsync-gap histories pass.
WHAT NOT TESTED: hostile same-UID/root, arbitrary rollback/power loss, absence-based
reservation cancellation, missing-witness repair, remote exactly-once delivery,
generalized F3 semantics or automatic grant revival.
