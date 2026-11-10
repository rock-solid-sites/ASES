# UID-separated native L5 custody probe

## Result

The new container route demonstrated a bounded custody boundary for the
selected original L5 manager when every authorized management path launches
through the trusted root driver and the fixed exclusive-guard manager. The
manager ran as UID/GID 2000. The D-write worker and a fork/exec descendant ran as
UID/GID 2001, with no supplementary groups, zero effective/permitted
capabilities, and `NoNewPrivs=1`. The trusted root driver had exactly
`CHOWN`, `DAC_OVERRIDE`, `SETUID` and `SETGID` in its effective, permitted and
bounding sets. The image copy of the native source, worker, manager wrapper,
supervisor and driver was root-owned, with directories mode 0755 and files mode
0644.

Eight native histories passed. A worker request on the allowed D path reached
the original L5 manager through the supervisor and wrote the expected
`allowed-payload` bytes. After native move and activation attenuated D to
read-only, the same mediated D-write reached the original manager and was
denied. The worker could not choose a move/activation operation on its pipe;
the driver refused that request without changing the current record.

UID 2001 direct write, chmod, lock unlink, store-root rename, manager-source
modification and setuid-to-2000 attempts failed. Direct launch of the original
manager failed while reading the private selector. Manager `/proc` descriptor
access failed. The worker inspected its own descriptors using `fstat` and
`F_GETFL`; it observed no writable store descriptor, its invalid-FD write
returned `EBADF`, and its direct path write returned `EACCES`. The independent
checker derived writable store descriptors from the raw target paths and
access modes, and rejected missing or contradictory FD evidence. Direct-attack
snapshots include the selected record, effect and accepted object bytes and
hashes; those bytes, the store-root inode and the lock inode remained unchanged.

The root driver intentionally lacks `CAP_KILL`. A root-owned-code supervisor
running as UID 2000 owned the native manager process and actually sent SIGKILL
and waited for it at both the pre-selector and post-selector gates. A fresh
authorized manager then made native progress from the selected old or new whole
state. A concurrent guarded manager received `writer-busy`. A separate fixture
passed a writable record FD to UID 2001 with `pass_fds`; the worker wrote
through it despite the path permissions. This verifies why the production
launcher path must close all store FDs before worker exec.

The outside-boundary control also passed as expected: an unguarded original
manager running under the same store-owning UID committed a move while the
guarded manager held the lock. This confirms that the demonstrated exclusion
depends on controlling every authorized UID-2000 launch path. It does not
confine hostile code already running as UID 2000.

## Execution and evidence

The task used the managed Docker daemon explicitly at
`unix:///var/run/docker.sock`: Docker 28.4.0, `vfs`. The native run used one
unique named `--rm --network=none` container based on
`python@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b`,
with CPU, memory and PID bounds, all capabilities dropped before adding the
four required root-driver capabilities, and `no-new-privileges`. It had no
mounts, published ports or privileged flag. The successful image ID was
`sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335`;
the minimal build-context digest was
`6ddaa35216666d449de179a164841e1c91cbee7031adfd6d89024986ab3dddbe`. The
context contained ten files: the driver, supervisor, worker, Dockerfile,
ignore file and five pinned L5 sources.

The pinned native L5 commit is `51b34aface9340b7e6821b8c40dc62ca38da15e2`.
The L5 manager, L5 integration, L1 and conformance fixture SHA-256 values are
preserved in `evidence/attempt-08/raw.json` alongside process identities, capability
sets, statuses, record bytes, expected object bytes, path/lock device and inode
numbers, owner kill/reap results and the full container command. The
independent raw checker passed all eight cases, checked all four UID/GID slots
for the driver, manager, worker and descendant, five native source hashes and
the ten-file context. Eight altered evidence controls were rejected, including
an effective-root identity and missing or inconsistent FD evidence.

Failed setup/instrumentation attempts are retained under `evidence/attempt-*`.
The earlier chmod-after-chown `EPERM` remains preserved in
`evidence/feasibility.json`; the corrected fixture sets modes before chown.
The first Docker build tried Buildx's default cache under the read-only
`/home/agent/.docker`; the successful retry used Docker's legacy local builder
for this network-free build and left `DOCKER_CONFIG` and registry credentials
untouched. Other retained attempts record a fixture-path mistake, the expected
root `EPERM` when trying to kill UID 2000 without `CAP_KILL`, a malformed
mutant command and runs superseded because their context contained Python
bytecode or lacked final evidence fields. The final accepted run used the
minimal ten-file context and the UID-2000 supervisor.

## Boundary and untested cases

This is evidence for a local, disposable container fixture with a trusted
Docker daemon/host, root driver, fixed owner supervisor, native source and
complete control of the guarded UID-2000 launch route. It retains the prior
accepted-object fixture/import assumption. The deliberate same-UID bypass is
outside the boundary. It does not establish confinement of arbitrary code
running as UID 2000, native F3 acceptance, completeness of production
entrypoints, host/Docker administrator isolation, protection against all
container-runtime failures, physical power-loss durability, or a global
security guarantee.
