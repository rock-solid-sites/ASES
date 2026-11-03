# Run record

All source runs used the pinned worktree at commit `651a740bea2d1e25ed221ba541d8f7a9d0166913`. The five primary sources were SHA-256 checked before execution and matched the hashes in `First-Verdict.md`; they remained unchanged. Python was invoked as `python3` from `/workspace/ases-f1-check`.

## Bounded commands and results

The four probe commands used this exact wrapper, with `probe` set in turn to `capacity_competition.py`, `snapshot_witness.py`, `two_store_crash_cuts.py`, and `exact_authority_cuts.py`:

```sh
timeout 20s bash -c 'ulimit -v 524288; python3 "$1"' _ "docs/research/phase-i-f1/$probe"
```

Each exited 0. The wrapper capped each at 20 seconds and 512 MiB virtual memory. The Python child outputs and stderr files are preserved in `raw/<probe-without-py>.stdout.json` and `.stderr.txt`. Their search-limit/truncation fields are retained in the JSON.

The full finite comparator command was:

```sh
timeout 40s bash -c 'ulimit -v 1048576; python3 docs/research/phase-i-f1/phase_i_f1_model.py --output docs/research/phase-i-f1-check/raw/phase_i_f1_model.json'
```

It exited 124 at the 40-second cap, under a 1 GiB virtual-memory limit. Stdout and stderr are preserved; no model result JSON was produced. The timeout is a truncated run, not a test failure or pass.

The paired-stale discriminator source is preserved as [`raw/paired_stale_authority_witness.py`](./raw/paired_stale_authority_witness.py), and its raw JSON result is [`raw/paired_stale_authority_witness.json`](./raw/paired_stale_authority_witness.json). It was run with:

```sh
timeout 10s bash -c 'ulimit -v 262144; python3 docs/research/phase-i-f1-check/raw/paired_stale_authority_witness.py'
```

It exited 0 under 10 seconds and 256 MiB, using disposable temporary files only.

A supplementary model-context diagnostic imported `phase_i_f1_model.py` and called `explore(REFERENCE, ctx)` for `capacity-one`, `currentness-image`, and `two-loss-currentness`, with a 20-second/512-MiB wrapper. It exited 0; raw output is `raw/focused_model_contexts.json`. Its first import attempt omitted registration in `sys.modules`, so Python's dataclass loader raised `AttributeError`; the import harness was corrected and the bounded diagnostic rerun. The diagnostic called a whole-model semantic-check helper on partial alphabets, so those context-inapplicable check results are not used as evidence.

## Preserved observation files

- `capacity_competition.stdout.json` / `.stderr.txt`
- `snapshot_witness.stdout.json` / `.stderr.txt`
- `two_store_crash_cuts.stdout.json` / `.stderr.txt`
- `exact_authority_cuts.stdout.json` / `.stderr.txt`
- `paired_stale_authority_witness.py` / `.json` / `.stderr.txt`
- `phase_i_f1_model.stdout.txt` / `.stderr.txt`
- `focused_model_contexts.json` / `.stderr.txt`

Empty stderr files are retained to distinguish clean exits from omitted capture. Process exit codes and timeout controls are summarized above. No agent run, production service, privileged state, or repository implementation was changed.
