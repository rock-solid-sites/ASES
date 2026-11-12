# Explicit reconciliation of one locally admitted, unpublished native effect

ASES-4 A/B continuation. Parent draft #30 at
f7b16ddbf34034ce1a0967c37cd92d5869f7e399. The existing after-append EOF history
leaves one complete local effect, native owner status local, and a witness at
the preceding cut. Ordinary cold startup correctly refuses that mismatch.
Preserve that default behavior. Add an isolated privileged F4-side command for
this exact case; never infer publication or discard the complete local effect.

## Source basis and cheapest discriminating check

The existing current-authority check is explicitly at local journal append.
The normal cut wrapper publishes after that append; it does not re-admit D at
publication. Existing native settlement already consumes the actual journal,
protected owner reservation and fresh witness proof. A historical local effect
may therefore be published without granting a new current use. Pending effects
prevent native material/domain disposal until settlement.

A read-only check against the retained native-25 after-append-EOF fixture used
`native_sink.composed.retry.RetryState(journal, True)`: it parsed four actual
events, one indexed effect at seq4, replayed authority active/version1, and left
all1927 journal bytes unchanged. Reuse that parser, not a new journal model.

## Command and authority

New experimental `reconcile.py OWNER_ROOT REQUEST_ID` derives the journal,
private witness Unix endpoint and root from the existing protected native
sink_binding. No caller cut, payload, pair, certificate, published flag, path
substitution, TCP fallback, new witness initialization or force option.
The native owner/host identity remains the trust boundary; do not expose this
as a worker route. Only the existing private Unix attachment profile is in scope.

Require existing attachment paths and parent device/inode identities to match.
Take the exact existing F4 sink-writer.lock exclusively/nonblocking before
parsing or contacting the witness; an active sink or reconciler must exclude
this command. Never create a missing journal/attachment or alter journal bytes.
Use the actual RetryState parser/index and its mutex. A thin read-only subclass
may add the existing cut representation and fresh nonce-bearing witness exchange;
it must not replace state replay or confer authority from caller metadata.

## Narrow supported transition

Require a complete validated bounded journal whose final line is exactly the
target native effect, unique in the real request index. Require its actual
payload hash/domain/registration/world bindings and protected owner effect
status local with the same sequence/hash. Other pending effects, reserved-only
unknowns, torn/corrupt journals and unsupported attachments remain refused.
For local-to-published transition, retained F1 evidence and live owned material
remain required. An already-published observation may survive normal source
disposition, but only while the fresh witness exactly matches the full cut; it
can never advance a prefix from an old receipt. Current D write permission is
not re-granted or used as a substitute for the historical event.

Freshly query the bound witness with root/nonce/revision validation. Its current
cut must either equal the full actual journal cut, or equal exactly the prefix
before that one final effect, with identical replayed authority. No arbitrary
prefix, control-event suffix or unrelated/missing witness may be advanced.
The presented generation in the original envelope and admission.presented_l5
is intentionally distinct from admission.l5 after reservation publication;
validate the appropriate retained records without treating them as aliases.
When at the exact preceding cut, issue at most one existing /publish CAS from
that observed prefix/revision to the exact full local cut. Then use a fresh
/check to confirm the target; publication reply loss never permits blind CAS
retry or an invented successful receipt. If the cut already matches, do not
publish again. A published owner record is replayable only with matching current
witness proof; never repair witness rollback from a prior receipt alone.

Reuse native_sink.settle_from_native_sink with the actual replayed State under
its mutex and the exclusive writer guard. Avoid holding Owner.locked while
calling that helper (it takes its own guards). Its protected reservation keeps
disposal blocked during the staged publication/settlement gap. Revalidate bytes
and attachment at every effect boundary. No cross-store atomicity is claimed.
Only confirmed publication may select owner status published. Never append an
effect, activate F4, mutate F1/L6 material, or grant current write permission.

## Required actual histories and controls

Reproduce the real after-append EOF and cold refusal first. While the original
sink owns the writer guard the command must refuse without changes. Stop that
known test process, retain the same witness, and reconcile the one effect.
Show unchanged journal/event count, actual CAS/fresh proof, owner settlement,
ordinary cold startup now valid but sealed, exact-ID historical lookup and
current-version fresh-ID denial after actual source seal/move/activation.
Pending disposal must refuse before settlement; explicit normal disposition
may proceed afterward without erasing F1 observations.

Kill the owned command after confirmed witness publication but before owner
settlement (an explicit test-only gate is allowed). A rerun or normal supported
exact retry must settle the same event without another CAS/append. Also test
actual witness publication reply loss, mismatched/non-prefix witness, corrupt
tail, reserved-only state and a changed attachment. Keep exact responses and
unchanged-state refusals; never weaken the profile to make a test pass. Capture
raw journal/owner/witness bytes/records, nonce exchanges and process/gate frames.

WHY: close the retained pending-effect recovery gap without confusing local
admission, remote publication and current use. WHAT: existing native owner,
actual replay parser, writer guard, witness CAS and settlement helper.
HOW CERTAIN: experimental until bounded native histories pass.
WHAT NOT TESTED: hostile same-UID/root, missing witness recovery, arbitrary
rollback/power loss, remote exactly-once delivery, universal repair, or new
Kernel/F3 disposal semantics. Default cold startup continues to refuse mismatch.
