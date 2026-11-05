# Required data validated before ready

Baseline6b332ae, repaired sourcee0ba50f (exact pins/raw source hashes retained).
Reproduce baseline in isolated checkout of6b332ae using `python3 docs/research/phase-i-f1/c11-history/input-validation/probe.py baseline` before fixture exists; fixed phase uses
`python3 docs/research/phase-i-f1/c11-history/input-validation/probe.py fixed`. Feed raw
output to `.../input-validation/check.py RAW` at the final evidence pin. Checker verifies
historical source hashes at recorded execution pins and retained image digest.

WHY: presence/type validation after COMMIT cannot supply a missing required positive
premise. WHAT: actual configured holder startup, content/archive/latest SQL COMMIT or
ROLLBACK, real no-response/ACK, fresh recovery ready/query, separate diagnostic SQL
reader and original malformed image retained byte-for-byte. Certainty: executed bounded
negative controls and coordinator read-only check; no independent validation review.

Baseline missing evidence key/integer evidence: content/archive/latest COMMIT succeeds,
then consumer response unavailable. Fresh holder advertised ready but cannot provide
usable query; diagnostic rows show real malformed JSON content and integrity ok.
Well-typed positive ACKs. Same-content conflicting tuple triggers actual ROLLBACK and
no ACK, preserving prior accepted records. BASELINE-RESULT and first checker failure
preserve stderr race: partial traceback observed, terminal exception class metadata
missing; source suggests validation exception, raw does not establish its exact class.
No behavioral rerun to obtain prettier stderr. First failed read-only assertion is
an instrument requirement error, not a new product failure or evidence of no exception.

Repair validates supplied required field shape/types before endpoint startup, and
existing current/archive record shape/content-key binding before advertising ready.
Both invalid input configurations now refuse before ready; no RPC is invented after
that refusal, original ACKed pair unchanged. Valid ACK/recovery and same-content conflict
ROLLBACK controls survive. Original actual malformed database image refuses before
ready with identical before/after SHA256, not repaired or erased. Baseline/fixed each
use18 actual distinct children/max1, all reaped. Missing startup/raw-row metadata returns
INCOMPLETE. Historical same-transaction archive/latest four-case regression passes.

WHAT NOT TESTED: source/provenance authentication or truth, intrinsic identity, independent
root currentness/nonrollback, arbitrary malformed encodings, power loss, concurrent writer,
generic C9/C11/F1/PhaseI acceptance or a canonical schema. Inputs were deliberately invalid
outside completed well-typed-input premise; this extends the chosen implementation's
admission boundary rather than overturning prior qualified evidence. Current/archive
semantic consistency is checked; no claim of external semantic truth follows. Parent
holder/canonical/main unchanged. Older manifests remain attached to their source pins;
this manifest binds new guard/artifacts and actual invalid SQLite fixture.

Next discriminator: independent source/raw audit of precommit/pre-ready checks if justified,
or return to stronger still-open resource/model/Kernel questions. Do not spend the next
round expanding routine schema-field examples or retrying blocked native/platform routes.
