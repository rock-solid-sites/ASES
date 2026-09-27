# Phase 2 frozen manifest

Frozen **before** any measured run. Every digest below is asserted at run time;
a mismatch must abort rather than produce a result.

## Corpus (vendored CPython stdlib, PSF-2.0)

| file | bytes | sha256 |
|---|---|---|
| `shlex.py` | 13501 | `42ab6060f316e121e374e6621d8c1c98b8db323903c3df289a810c45a8ae46a7` |
| `json_encoder.py` | 16074 | `06b881b824f71e95d72af4ab865de4c35553e791b6d959a125caac61401cc350` |
| `textwrap.py` | 19772 | `e1541a31ac906294f915cadd0d780e1e5b256dc1897b560cdaf3fbf46d104cf0` |
| `dataclasses.py` | 56390 | `fa2e3728d8184954479c6fcd17015a5e0c176850f18f119f5c548fca49019441` |
| `configparser.py` | 54612 | `df56496e25906c42f7599e7237b1c8e33eb6e9a9a5590cad55e2907492bba88a` |
| `_distractor_uuid.py` | 27500 | `75bdfdbbb57c7a50e0252997621308be79a535ceb1eb6ba01a462b7e7ffdf19d` |

`_distractor_uuid.py` is the irrelevant-context distractor only; it is never
the subject of a question. It was chosen for **zero symbol overlap** with the
five subject modules (240 symbols checked), so appending it cannot make any
question ambiguous.

## Code

| file | sha256 |
|---|---|
| `harness/extract.py` | `649a48094d0c4f3cd36aa558bf8006bee0abf6294ef52775ca0eab74f55f64ec` |
| `harness/gen_cases.py` | `2a4e68b64dba819f1bdce987cda9af47acf60fe23436a68ffc3813fbbd57cac9` |
| `harness/represent.py` | `f83c75a35ae33f85aa008b3c7a2f8da14b9fff2d26a84b719a907115badce174` |
| `harness/run_jev.py` | `5364858ecffcce16546ceb8fe9f3ae5e38967a2b88ee86e1cf28fca193e8457e` |
| `harness/score.py` | `02fad774f180794ff8eb6387cb2555ba1c9596714a1673ced4571e8e551a29ef` |
| `harness/validate_cases.py` | `fa0083461b43e939423d779918a580a4d731da040825fe853283c12c4191e241` |

## Frozen case set

- `frozen/cases.json` — 67 cases
  sha256 `0e8585f85f4d2452101a1899ec0208ce5a10d48f113ccd3623504fe389bdf584`
- `frozen/admissibility.json` — admissibility matrix
  sha256 `507bf023f2efb13ed2d91da4ba729d61d5441fae5065a9a6c44b587881685fbd`

### Composition

| ctype | n |
|---|---|
| `direct_call` | 25 |
| `param_rebound` | 10 |
| `call_path2` | 7 |
| `unused_import` | 5 |
| `nesting_conjunction` | 5 |
| `string_literal_probe` | 5 |
| `unanswerable_semantic` | 5 |
| `unanswerable_runtime` | 5 |

Ground truth: 33 `yes`, 24 `no`, 10 not-derivable.

### Admissibility

| condition | admissible |
|---|---|
| `raw` | 57 |
| `struct` | 52 |
| `raw_ic` | 57 |
| `struct_ic` | 52 |

- **52 cases comparable** (admissible under both `raw` and `struct`)
- **0 struct-only**
- **5 raw-only** — the `string_literal_probe` cases. This is the designed
  evidence-removal probe and it fired: structure carries no string literals, so
  a literal-presence question is not answerable from it. Evidence removal is
  therefore demonstrated, not assumed away.
- **10 unanswerable** under every condition, never scored

## Gate results at freeze time

```
GT mismatches     : 0     (every answerable ground truth independently
                         re-derived from the AST by validate_cases.py,
                         which does not read the generator's gt_basis)
leak findings     : 0     (no field name asserts a queried proposition; no
                         ground-truth value appears as a labelled answer;
                         params and assigned_locals are emitted separately so
                         the conjunction is not precomputed)
all admissibility invariants hold
```

## Two generator bugs the gate caught before any run

Recorded because the gate earning its keep is a result, not a formality.

1. **10 ground-truth mismatches.** The `direct_call` FALSE cases were built by
   enumerating *existing* call edges and labelling them `no`. Every one of the
   ten was a real edge. Fixed by enumerating (caller, callee) over real symbols
   and filtering to pairs with no edge.
2. **`struct` admissibility was 0 for every case.** The required-evidence
   predicates read `c["caller"]` while the case schema nests those under
   `c["params"]`, so every predicate raised and was caught as `False`. This
   would have silently produced a benchmark with **no comparable cases at all**.

A third defect was found and fixed in the same pass: call edges from nested
functions were attributed to the enclosing method, which would have made "does
X directly call Y" true whenever a closure inside X called Y.

## Reproduction

```bash
cd research/jev-bounded-judgment/phase2
python3 harness/gen_cases.py        # regenerates frozen/cases.json
python3 harness/validate_cases.py   # regenerates frozen/admissibility.json, must exit 0
python3 harness/run_jev.py --out results/jev_raw.ndjson
python3 harness/score.py --raw results/jev_raw.ndjson --outdir results/jev
```

`gen_cases.py` and `validate_cases.py` are deterministic: no RNG, no clock, no
host paths. Re-running them must reproduce the two frozen digests above exactly.
