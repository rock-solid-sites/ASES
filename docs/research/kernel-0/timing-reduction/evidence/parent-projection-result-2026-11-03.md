# Bounded parent-projection discriminator (2026-11-03)

Source: `9d0ecf1edbb7eb00e8ace4b2a4cf3e8ae65973c2`. `git log --all -- docs/research/kernel-0/timing-reduction` found no later modification among fetched refs. This is research evidence, not a timing or physical-realization result. The November 2 testing/debugging proposal report was used for claim-first, neighboring-control and raw-evidence guidance, not as policy.

## Prediction and observation

Hypothesis: `_other_value` leaves the fourth parent unchanged, so `minimal_style` cannot discover a dependency on that parent. Prediction: two legal states with identical rights and different fourth parent yield the same selected projection, but parent restriction cascades differently. Control: the full view distinguishes those inputs. The script constructs both states through successful catalog requests; it checks legality, identical other fields, membership of the target request in the catalog, full-view distinction, and the two successor outcomes. It checks independent and coupled profiles (exclusive cannot admit this pair of active rights). Both predicted pairs occurred: both restrictions commit, but resulting child rights are 1 versus 0. Selected style is `rights` in both. Consequently the selected view is insufficient to determine the visible successor in these fixtures. This is stronger than the earlier observation that the existing same-state correspondence comparison is vacuous, but does not characterize a globally minimal view.

## Replay and bounds

From worktree root: `{ time timeout 50s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/parent_projection_probe.py'; } > docs/research/kernel-0/timing-reduction/evidence/parent-projection-probe.log 2>&1`. Exit 0. Four legal input states, four target resolutions, two profiles, explicit cap 100 input states; four construction resolutions plus establishment/grants are setup. Wall-clock external timeout 50 s, address-space limit 1 GiB. Python reports 0.0094 s and 11,904 KiB peak RSS in the recorded run. The initial `/usr/bin/time` invocation failed because that executable is unavailable; its raw launch failure is retained separately and did not execute the fixture. Shell `time` supplies the replay's external timing.

Fixture SHA-256 `089ddd489bb5a0a26473d94f74d28decba7093cdacd83afbbe79737a3c76929b`; raw log `b2c30f92706e09273f7e9c377c3e845459bc7e56e2fa746c4cd70ebc93b441f9`; inherited harness `595c7ff9a4a7350476edd316e9af20a88d4ed78277f74cd82dae15dcac534fcf`.

## Limits and next discriminator

This checks the frozen Python oracle against paired legal/reachable fixtures; it does not compare RTL, prove observational sufficiency for other styles, examine exclusive-profile pairs, or model torn capture and partial publication. It does not establish or refute the proposed overall timing contract. A next bounded discriminator should compare legal state pairs sharing a proposed mask across outcome and projected whole-successor, including both valid and deliberately insufficient masks and profile-sensitive cases. A parent perturbation alone cannot turn the existing same-state oracle-vs-itself traversal into a correspondence proof. Add an actual inner deadline and state/offer bounds before attempting a larger scan.
