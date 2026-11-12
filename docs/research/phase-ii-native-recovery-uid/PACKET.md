# Native recovery commands inside the existing UID custody route

ASES-4 priority B follow-through, parent draft #36 at82390c76. Reuse the actual
#27 root launcher / UID2000 manager / UID2001 worker route and native #30 stack.
Verify that the new privileged reconcile/observe commands fit that same actual
boundary; no new authority model or worker management surface is introduced.

## Runtime route and bounded launch

The pinned existing local base image is
sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335.
Read-only preflight confirmed it exists, size119614344 bytes, driver=vfs.
Avoid repeated build layers: create ONE uniquely named/labeled container from
that exact image, docker-cp an explicitly staged source tree into /opt/owned-src,
then start/attach it. No image build/pull/publish, host bind mount, socket mount,
port exposure or broad workspace copy. Preserve /opt/probe/driver.py from the
pinned image. Normalize staged directories/files to755/644 and root ownership.
Copy only the prior run_uid.py explicit runtime Python set plus the new recovery
modules/gated wrapper and this fixture's files. Record copied file hashes.

Use explicit local Docker socket, clear task-local DOCKER_HOST/CONTEXT/TLS vars,
network none, CPU1, memory512m, pids32, drop ALL caps then only CHOWN,
DAC_OVERRIDE, SETUID, SETGID, and no-new-privileges. No configuration/credentials
changes. Remove only the exact labeled task container at completion/failure;
base image and other objects remain untouched. This keeps VFS storage bounded.

Reuse the real base Child/preexec/mediate helpers. Manager UID2000 owns actual
Child handles for its kernel services and recovery commands; root launcher has
no CAP_KILL and must not signal adopted PIDs. Worker/descendant credentials,
groups, CapEff/CapPrm and NNP come from actual /proc status, not invented fields.
Bounding-set values are observations, not assumed zero. Worker has no writable
regular authority FD or direct controller/witness socket access.

## Actual native cases

Run two sequential native fixtures inside the container: (1) after-append EOF
with owner status local, requiring strict reconcile; (2) actual fsync-before-owner
callback gate/kill with status reserved and a complete event, requiring explicit
observe_local. Use actual setup_native_f3/NativeF4 and the existing test-only gate
wrapper; never install acceptance/owner outcomes or journal bytes manually.
The witness remains the same live private manager-owned service during recovery.

Before recovery, UID2001 requests manager operations through the worker pipe;
strict root mediation rejects them before forwarding. It also directly invokes
both real CLI files with the known owner root/request ID, and tries the private
sink/witness endpoints. Require real protected-store PermissionError/EACCES or
an equivalent actual OS denial. Import/syntax failures never count as custody.
The new CLIs catch errors into JSON, so inspect structured stdout as well as
stderr. Record worker and fork/exec descendant status and actual FD access.
Compare actual owner selection/material/journal/witness cut before/after denied
requests; observation timestamps need not be equal.

The trusted manager then invokes the correct actual recovery command under
UID2000. It settles one event with no append, confirmed by real witness protocol
and owner state. Ordinary cold startup accepts the matching cut but remains
sealed. Replace/activate current F4 authority explicitly before testing new use.
Perform real native seal/move/activation: a new worker ID with freshly derived
native epoch/selector and current F4 version reaches native path denial, no append.
An old accepted ID is observed with its EXACT original protected journal payload,
not a newly generated envelope: the manager may recover that payload from the
actual request index/journal. Worker chooses only its bounded request ID, never
manager operations, payload metadata, token, pair, credential or graph.

## Ownership and evidence

New fixture/controller/worker/driver/runner and focused raw checker live only in
this directory. Existing production source should stay unchanged. Capture the
actual Docker invocation/identity, kernel UIDs/caps/FD facts, source file hashes,
manager/worker requests/replies, direct CLI refusal, native selected records,
actual one-effect journal, witness proof and recovery transitions. Negative
controls must reject an allowed worker management result and a fabricated
recovery success with unchanged pending owner status. Preserve bounded failed
attempts; no broad inventory, independent CI or backup administration.

WHY: join the actual native recovery interface to the demonstrated custody route.
WHAT: the same UID-separated processes, protected stores and real native APIs.
HOW CERTAIN: experimental until both actual native fixtures/checker pass.
WHAT NOT TESTED: hostile same-UID/root, deliberate writable-FD leaks (existing
bypass remains), host loss, arbitrary programs, general confinement or new
manager credential provisioning. No production workload or service exposure.
