# Version validation control

Preregistered at `26ee0d06b`. All 180 parameterized schedules completed. The reader accepts only equal, even samples; rejected attempts withhold their value and are not retried in this model.

| Publication protocol | Accepted with coherent cut | Accepted without coherent cut | Rejected |
| --- | ---: | ---: | ---: |
| Whole successor, version increment at commit | 24 | 0 | 36 |
| Split successor, version increment only at end | 14 | 10 | 36 |
| Split successor, odd version at first field and even at last | 8 | 0 | 52 |

The late-version counterexamples read partial publication and complete validation before the version changes. The bracketed control excludes them within this model because version change and the corresponding field visibility are explicitly a single event; the reader also has ordered version and field events. The whole control demonstrates that validation can detect the earlier cross-commit read in this finite setting. Rejections include coherent attempts and no liveness, eventual retry, wraparound, compiler/memory ordering, crashes, multiple readers/writers, or actual implementation is tested. No specific mechanism is established as necessary. Raw traces include every accepted and rejected attempt and its interval cut candidates.

The run counts 180 schedules, 1,260 per-case state cuts and 1,080 event steps, under caps of 180/1,260, 10 s and 1 GiB; elapsed Python time 0.0062 s, peak RSS 9,600 KiB. Case-cap-3 and cut-cap-15 negative controls exit 2 with exact next case. Replay: `timeout 10s bash -c 'ulimit -v 1048576; python3 -u docs/research/kernel-0/timing-reduction/evidence/version_validation_scan.py'`.

SHA-256 script `b746fa893d01c9782bb6206ba4ba17bc40afd628f8e30924af26748c90cd9831`; full log `e7e26870d5f564d359ee9e53a162b95a3a5fbd823b0da0be9acfa1644fb6af77`; case truncation `947c8a7165941efe69ac77f8689bf5fbda9daaf3453e5c787eda0748a2d3c2f2`; cut truncation `2c7a6c5791b5e61d8832287f6e6b63750d9cb06bda3535c13942f97dde6126ba`.

Next discriminator: an ABA/wraparound control in the whole-commit validation model, using two commits that return the small version to its sampled value. This probes an explicitly untested assumption before combining validation with stale-currentness schedules.
