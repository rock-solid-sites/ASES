#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results
rustc --version > results/toolchain.txt
cargo --version >> results/toolchain.txt
echo 'hegeltest =0.53.1; proptest =1.12.0' >> results/toolchain.txt
cargo generate-lockfile > results/lockfile-generation.log 2>&1
cp Cargo.lock results/Cargo.lock
cargo test --locked --no-run --lib --test proptest_compare --test hegel_compare > results/build.log 2>&1
cargo test --locked --lib > results/controls.log 2>&1

failures=0
: > results/summary.jsonl
for engine in proptest_compare hegel_compare; do
  for mutant in baseline accept-any actor-only partial-side-effect; do
    start=$(date +%s%3N)
    set +e
    ASES_MUTANT="$mutant" RUST_BACKTRACE=0 cargo test --locked --test "$engine" -- --nocapture > "results/$engine-$mutant.log" 2>&1
    exit_code=$?
    set -e
    end=$(date +%s%3N)
    elapsed=$((end-start))
    marker=false
    if grep -q 'COUNTEREXAMPLE:' "results/$engine-$mutant.log"; then marker=true; fi
    qualified=true
    expected=detected
    if [ "$mutant" = baseline ]; then
      expected=passed
      if [ "$exit_code" -ne 0 ]; then qualified=false; fi
    elif [ "$exit_code" -eq 0 ] || [ "$marker" != true ]; then
      qualified=false
    fi
    printf '{"engine":"%s","mutant":"%s","expected":"%s","exit_code":%d,"elapsed_ms":%d,"counterexample_marker":%s,"qualified":%s}\n' "$engine" "$mutant" "$expected" "$exit_code" "$elapsed" "$marker" "$qualified" >> results/summary.jsonl
    echo "$engine / $mutant => rc=$exit_code marker=$marker qualified=$qualified elapsed_ms=$elapsed"
    if [ "$qualified" != true ]; then failures=$((failures+1)); fi
  done
done
if [ "$failures" -ne 0 ]; then
  echo "$failures experiment arms failed acceptance; inspect results logs" >&2
  exit 1
fi
