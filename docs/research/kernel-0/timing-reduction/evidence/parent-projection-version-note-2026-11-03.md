# Historical parent-projection probe: source-version scope

`parent_projection_probe.py` and `parent-projection-probe.log` record the original unsafe style selector at commit `cbd0e22c1` (whose harness is inherited from `9d0ecf1ed`). The original probe asserts the *old defect*: `parents` is absent from both styles. At `9dc5b34dc` the harness was intentionally changed to probe that field, so running the historical script against the repaired current harness fails that assertion. This is expected source-version mismatch, not a new regression and not evidence that the old result was fabricated. Do not overwrite the historical log. The current paired scan explicitly checks both a reconstructed old unsafe selector and the repaired selector.

To reproduce the historical observation, extract the Kernel-0 subtree from `cbd0e22c1` into an isolated temporary directory and run that snapshot's probe, retaining its own sibling imports. From the repository root:

```sh
task_dir=$(mktemp -d)
git archive cbd0e22c1 docs/research/kernel-0 | tar -x -C "$task_dir"
timeout 50s bash -c 'ulimit -v 1048576; python3 -u "$1/docs/research/kernel-0/timing-reduction/evidence/parent_projection_probe.py"' _ "$task_dir"
```

Expected on the historical snapshot: `status: PASS`, four legal inputs and two detected projection counterexamples; timing and RSS may vary. To test the repaired harness instead, use `pair_projection_scan.py`; its old-selector control must omit parents and its repaired-selector control must include parents. Its rights+parents+data mask has zero mismatches only for eight compared cases in that bounded fixture; it omits other fields and is not a globally sufficient full-state view.
