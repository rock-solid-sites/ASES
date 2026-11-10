# Unsupported selected interpretation — before/after result

The append-admission adapter originally relied on L5 `graph_valid`, which does
not validate the selected record's schema version. Five real native process
histories confirmed the consequence: valid schema 1 and injected future integer,
string, boolean and missing schemas all reached F4 acceptance/publication
(HTTP 201). Each request presented the actual updated selected-record hash, so
these were not accidentally blocked by stale generation comparison.

The isolated correction requires a selected record object with an **integer**
schema exactly 1 before evaluating its current path. The corrected native run
still admits schema 1 (201), while all four unsupported representations return
409 `unsupported-l5-interpretation` with identical before/after journal bytes.
The boolean case matters: Python equality alone would consider True equal to 1.

`check.py` independently decodes captured selected records, verifies their bytes
and hashes against the request, and compares actual native replies/journal
effects before and after. Both altered controls reject: fabricated success for
future schema, and a wrong selected-record digest. Compressed complete raw
captures and the resulting verdict are in `evidence/`.

These are explicitly injected unknown-recovery-image controls. They are not
native authorized policy migrations and do not retroactively contradict L5's
original supported-profile claim. They expose a refusal obligation in the new
adapter, under Closure C7/C9 and Verification T09. No general migration,
arbitrary corruption repair, native identity issuer, physical confinement or
global refinement proof follows. All other test-only import/cooperative-writer
and current-storage/witness assumptions remain unchanged.

Reproduce using a new output directory:

```sh
python3 -B docs/research/phase-i-interpretation/probe.py --out /tmp/ases-profile-new
python3 -B docs/research/phase-i-interpretation/check.py docs/research/phase-i-interpretation/evidence/before.json.gz docs/research/phase-i-interpretation/evidence/after.json.gz
```

WHY: parsing valid-looking fields does not establish supported interpretation.
WHAT: five before/five after native histories, exact source-generation binding,
append/publication observations and two altered controls. HOW CERTAIN:
evidence-based for these finite malformed-image variants. WHAT-NOT-TESTED:
other schema migrations/fields, arbitrary corruption, malicious storage,
physical power loss, or promotion to a production/canonical policy.
