# F3 mediator revocation probe checkpoint (incomplete)

Resume verification: branch `research/phase-i-protected-work-unit-f3-20261029` at origin-verified `62b19e21e2d36ecef9bc4387089a35ec670fd484`; existing Crosslink session #2 remains active on #10. Latest report and Landlock result confirm direct path and one symlink were denied, mediated read returned fixture bytes, and an inherited FD remained readable. Do not repeat that experiment.

## Bounded test

In a new disposable `exp3/` directory, test one narrow configuration: a child is restricted via Landlock in the pre-exec path before it runs test code; it receives a retained local socketpair channel only (no target descriptor). A trusted sibling mediator opens/closes the fixture per operation. First authorized read returns the sentinel; supervisor revokes mediator authorization while both child and socket stay alive; second request must be denied with zero bytes. The child separately attempts direct target and symlink opens, expected EACCES. A preopened-FD bypass is run only as an independent negative-control child and is never passed to the restricted child.

Keep runtime <=90 seconds and use only the disposable fixture and local socketpair. If Landlock setup/exec confinement cannot be achieved without privileges/host policy, or the mediator cannot deny after revocation, preserve the exact output and stop. No general runtime/lifecycle work or F3 acceptance. Preserve `exp1/run/`; F1 partial and F5 independent review outstanding.