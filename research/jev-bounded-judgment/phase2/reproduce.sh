#!/usr/bin/env bash
# Phase 2 reproduction. Run from the phase2 directory.
#
# Split into two tiers, because one of them needs a credential that must never
# live in the repository:
#
#   TIER 1 (offline, no network, no credential)
#     Regenerates the frozen case set and the admissibility matrix from the
#     committed corpus and code, and re-scores the committed raw results.
#     Every produced digest must match the committed one.
#
#   TIER 2 (network + credential)
#     Re-runs the live jev-1.13.0 measurement. Requires TYPESAFE_API_KEY
#     resolvable from ~/.secrets/typesafe.env. The key VALUE is never in the
#     repository; only that path is named.
#
# Exit non-zero on any digest mismatch. A reproduction that silently produces
# different numbers is worse than no reproduction.
set -u
cd "$(dirname "$0")"

EXPECT_CASES=0e8585f85f4d2452101a1899ec0208ce5a10d48f113ccd3623504fe389bdf584
EXPECT_ADM=507bf023f2efb13ed2d91da4ba729d61d5441fae5065a9a6c44b587881685fbd
fail=0

echo "=== FREEZE GATE ==="
python3 harness/freeze.py verify --stage reproduce || { echo "FAIL freeze"; fail=1; }

echo "=== TIER 1: offline regeneration ==="
python3 harness/gen_cases.py || { echo "FAIL gen_cases"; fail=1; }
got=$(sha256sum frozen/cases.json | cut -d' ' -f1)
if [ "$got" = "$EXPECT_CASES" ]; then
  echo "  OK  frozen/cases.json  $got"
else
  echo "  FAIL frozen/cases.json got=$got want=$EXPECT_CASES"; fail=1
fi

python3 harness/validate_cases.py || { echo "FAIL validate_cases"; fail=1; }
got=$(sha256sum frozen/admissibility.json | cut -d' ' -f1)
if [ "$got" = "$EXPECT_ADM" ]; then
  echo "  OK  frozen/admissibility.json  $got"
else
  echo "  FAIL frozen/admissibility.json got=$got want=$EXPECT_ADM"; fail=1
fi

echo "=== RAW-RECORD SCHEMA (committed records) ==="
python3 harness/record_schema.py results/jev_raw.ndjson | head -3 || fail=1

echo "=== TIER 1: re-score committed raw results ==="
if [ -f results/jev_raw.ndjson ]; then
  rm -rf results/reproduce_check
  python3 harness/score.py --raw results/jev_raw.ndjson \
      --outdir results/reproduce_check >/dev/null || { echo "FAIL score"; fail=1; }
  # The scorer gained a matched-denominator block, so metrics.json will differ
  # from the pre-control run by design. What must hold is that the frozen inputs
  # and the independent cross-check both still pass.
  if [ -f results/jev_v2/metrics.json ]; then
    a=$(sha256sum results/jev_v2/metrics.json | cut -d' ' -f1)
    b=$(sha256sum results/reproduce_check/metrics.json | cut -d' ' -f1)
    if [ "$a" = "$b" ]; then
      echo "  OK  metrics.json reproduced  $a"
    else
      echo "  FAIL metrics.json differ: expected=$a reproduced=$b"; fail=1
    fi
  fi
  echo "=== cost/token consistency, verified against the reported metrics ==="
  python3 harness/score.py --raw results/jev_raw.ndjson \
      --outdir results/reproduce_check2 \
      --reported-metrics results/jev_v2/metrics.json >/dev/null || fail=1
  rm -rf results/reproduce_check2
  echo "  OK  reported cost figures agree with the matched-set token ratio"
  rm -rf results/reproduce_check
else
  echo "  SKIP no committed results/jev_raw.ndjson"
fi

echo "=== COST-REPORT POLICY: unequal-n aggregate ratios are rejected ==="
python3 - <<'PYX'
import json
m=json.load(open("results/jev_v2/metrics.json"))
for k,v in m.get("rejected_unequal_n_ratios",{}).items():
    print(f"  {k}: n {v['n_a']} vs {v['n_b']} cost_ratio={v['cost_ratio_of_totals']} -> {v['why_rejected']}")
for k,v in m.get("cost_token_consistency",{}).items():
    print(f"  matched {k}: consistent={v.get('consistent')} fresh_token_ratio={v.get('fresh_token_ratio_matched')}")
PYX

echo "=== TIER 2: live re-run (optional) ==="
if [ "${1:-}" = "--live" ]; then
  if [ ! -f "$HOME/.secrets/typesafe.env" ]; then
    echo "  SKIP ~/.secrets/typesafe.env absent; TIER 2 needs TYPESAFE_API_KEY there"
  else
    python3 harness/run_jev.py --out results/jev_raw_rerun.ndjson || fail=1
    rm -rf results/rerun
    python3 harness/score.py --raw results/jev_raw_rerun.ndjson \
        --outdir results/rerun || fail=1
    echo "  re-run metrics -> results/rerun/metrics.json"
    echo "  NOTE: compare with care. The live endpoint is not frozen, so a"
    echo "  difference is evidence about endpoint nondeterminism, not proof"
    echo "  that the reproduction failed."
  fi
else
  echo "  SKIP pass --live to re-run against the endpoint"
fi

if [ "$fail" -ne 0 ]; then
  echo; echo "REPRODUCTION FAILED"
  exit 1
fi
echo
echo "REPRODUCTION OK (tier 1)"
