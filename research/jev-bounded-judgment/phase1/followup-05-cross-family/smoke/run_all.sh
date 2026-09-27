#!/usr/bin/env bash
# Sequential by design: concurrent load on free-tier models would confound the
# reliability observation this followup is required to report.
#
# Chunk size 8 (was 16). At 16, ling-3.0-flash-fin-free dropped a case, fenced
# its output and leaked reasoning into the answer stream. Applied UNIFORMLY to
# all arms so cross-arm comparability is preserved; the chunk-16 evidence is
# retained in out-chunk16-record/. Re-running at 8 also gives a free
# reproducibility check: big-pickle's 64 answers must be identical.
set -u
cd "$(dirname "$0")/.."
for spec in "opencode/big-pickle:big-pickle" \
            "opencode/ling-3.0-flash-fin-free:ling" \
            "opencode/mimo-v2.6-flash-free:mimo"; do
  mid="${spec%%:*}"; tag="${spec##*:}"
  echo "########## ARM $tag ($mid) $(date -u +%FT%TZ) ##########"
  python3 smoke/run_arm.py --model-id "$mid" --tag "$tag" \
      --chunk-size 8 --attempts 2 --outdir out
  echo "---- arm $tag exit=$? $(date -u +%FT%TZ) ----"
done
echo "ALL ARMS COMPLETE $(date -u +%FT%TZ)"
