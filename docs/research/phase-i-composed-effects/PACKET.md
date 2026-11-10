# Composed admission and retry semantics

Frozen 2026-11-10 after separate local verification: admission `671ecc09`
(19 histories), retry `16e6460f` (11 histories). Original native sources remain
the pinned F1/L5/L6 and receipt F4 sources. This is a test-only adapter joining
the two isolated repair candidates, not a global integration proof.

## Required distinction

An **original new effect** requires current accepted subject/evidence, L5 path
authority and L6 liveness at the local append, plus the original flat F4 authority.
An **identical retry of an already accepted effect** is an outcome observation;
it appends nothing and does not claim current permission for a new effect. After
local append and lost reply, subsequent source disposition/revocation does not
erase the retained original effect. A fresh live witness exact-cut check can
support observing it without a second append. Do not make new effects eligible
by routing them through the historical-result path.

The trusted local fixture boundary may read retained results after revoke. A
production information-access policy is absent and not inferred. A conflicting
payload under the same ID is an identity conflict, not a new authorization.
New IDs still cross every current guard. All original import/custody/witness
assumptions remain; this adapter does not repair their missing native interfaces.

## Minimal implementation

Reuse retry's replay-derived `RetryState` as the base managed state inside the
admission sink. The existing receipt-aware outer state checks the live cut;
the retry path either returns the old observation with zero append or delegates
new work to original managed use. Only the latter reaches admission's
`emit_locked(effect_accepted)` hook and its F1→L5→L6 guarded view. No second
identity table, cache, authority epoch, journal or scheduler is added.

Do not rewrite original sources or loosen either guard for the composition.
Disposable Python reuse is narrower than translating the native processes; its
mechanical evidence is raw current state and real append/publication/replay.

## Discriminators

- Valid new effect actually appends and publishes.
- Source-denied new effect fails with no append; retry-only candidate by itself
  remains a negative control and publishes under the narrower flat contract.
- Actual witness reply suppression leaves one accepted effect; identical retry
  after native L6 disposition/removal returns original observation with zero
  new bytes. A new ID from that now-dead source fails.
- Same behavior across real cold sink restart, with retained journal identity
  and fresh witness match; no historical admission is retrospectively invalidated.
- Native F4 revoke after acceptance still permits the declared historical result
  observation; new ID denies under current flat authority.
- Equal ID/different payload returns conflict unchanged, including after source
  invalidation; no accidental reinterpretation as an audit or obligation.
- Local append without publication, or actual witness rejection, never becomes
  a successful observation or another append; cold mismatch remains refused.

Run positive, negative, restart and receipt-loss histories with independent raw
checking and altered controls. Record exact which proposition each result proves.
No universal native identity, global disposition, remote cancellation, external
exactly-once delivery, durable witness or enforced all-writer custody is claimed.

## Integration falsifier and correction

The initial native composition retained one local event after publication
rejection, but the outer cut guard refused a duplicate before retry state ran.
Its generic `local_control_committed=false` reply lacked the original event
context, and a known conflicting payload also received only unavailable-cut.
The adapter now wraps that outer return boundary: known local ID conflicts
refuse before remote observation; an unavailable exact retry reports the prior
local sequence/commit and `new_local_effect=false`, never a successful remote
observation. No new event is appended. Retain the initial trace and run the
discriminator again against this specific correction.
