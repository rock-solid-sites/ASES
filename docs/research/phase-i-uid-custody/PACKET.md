# L5 store custody through a trusted launcher and distinct worker UID

Frozen 2026-11-10 after the new route's cheapest discriminator. Earlier P2
Landlock/user-namespace probes remain unchanged. The managed local Docker daemon
is available at unix:///var/run/docker.sock (28.4.0, vfs, builtin seccomp); the
cloud-runtime Docker skill describes this provided route. No daemon or host
configuration is changed. This justifies revisiting the precisely recorded
blocker with a different, now-demonstrated execution boundary.

## Feasibility actually observed

Pinned image `python@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b`.
In a --rm, network-none container, trusted driver UID0 created a private
UID2000 store. UID2001 worker had CapPrm/CapEff=0 and NoNewPrivs=1: direct write
returned EACCES(13), setuid(2000) returned EPERM(1), and owner bytes remained
exact. First setup attempt chmod-after-chown failed because root lacked FOWNER;
ordering chmod before ownership transfer fixed that fixture setup. No FOWNER or
privileged container is required.

## Exact boundary and mechanism

Use one finite temporary container with no host bind mounts, no Docker socket,
no published ports, network none, CPU/memory/pid bounds. Pin and record the image
digest and original L5/#11 source hashes. Only copy minimal test sources into
the build context; never the whole repo, credentials, environment or Docker config.

Trusted root launcher has only CHOWN, DAC_OVERRIDE, SETUID, SETGID capabilities.
Its code/policy and the provided Docker daemon/host are in the TCB. It creates
the store and stable lock under a non-worker-writable parent, sets modes before
chown, and launches the **fixed** original #11 exclusive-guard manager as UID2000.
Every supported authorized management entrypoint is this guarded launch path.
Untrusted interior processes and their descendants run as UID2001, no groups,
zero effective/permitted caps, NoNewPrivs=1. They receive no writable store or
guard descriptors and cannot become the store UID or rewrite the launcher.
Their source code being readable does not confer a route into the protected store.

The worker's mediated D-write route is a supervisor-created pipe association.
The trusted driver forwards only a validated D-write request to the native
manager's stdin; it never gives the worker that management stream or accepts
caller-chosen op/role/source labels as management. All actual path/ceiling checks
and effect bytes come from original L5 code. Unsupported management requests on
the worker route refuse without calling native management. Avoid a new generic
daemon/API; this is a bounded disposable integration probe.

Root/store-owning UID compromise, external Docker/host administrator and an
unguarded UID2000 writer are explicitly outside this boundary. Preserve that
outside-boundary bypass as a control. Do not claim arbitrary hostile same-UID
store-owner confinement, native F3 acceptance, or production all-route assurance.
The existing trusted accepted-object fixture/import assumption remains visible.

## Required discriminators

- Valid mediated D write on an allowed native path actually writes expected bytes;
  moved/attenuated native path refuses D write after native move/activation.
- UID2001 directly launches original unguarded manager and attempts direct write,
  chmod, lock unlink/recreate and root rename: denied, stable root/lock inode and
  accepted bytes unchanged. Its fork/exec descendant and setuid attempt fail to
  acquire store authority. /proc access to owner descriptors refuses.
- The worker route cannot request move/grant/activation; legitimate trusted
  management still succeeds. Guarded authorized contender refuses busy.
- Actual UID2000 owner kill/reap before selector and after selector releases the
  guard; fresh authorized owner makes valid native progress from old/new whole
  state. Do not infer death from an old PID/status flag.
- Correct close_fds launcher leaves no writable store FD; an intentional bad
  pass_fds mutant lets UID2001 write through a preopened FD despite DAC. Separate
  fixtures ensure this control does not corrupt another test's preconditions.
- A deliberately unguarded UID2000 original writer still bypasses flock. This
  marks the trusted-owner boundary and does not negate UID2001 exclusion.

Use actual processes/files/inodes/caps/UIDs and raw failures in the container,
then a separate raw checker outside it. Preserve instrument failures distinctly.
No host configuration, privileged mode, production deployment, provider/model
workload, persistent container, CI or independent review. New result is conditional
on this explicit trusted launcher/UID separation; do not rewrite earlier evidence.
