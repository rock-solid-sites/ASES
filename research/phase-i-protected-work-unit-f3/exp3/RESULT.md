# F3 mediator authorization-revocation result (2026-10-30)

Executed `mediator_revocation.py` from the disposable `exp3/` directory with an outer 20-second timeout (the bounded requested limit was 90 seconds). All test subprocesses exited normally and were reaped.

## Exact disposition

The restricted test child was launched with `preexec_fn` applying Landlock ABI 1, PR_SET_NO_NEW_PRIVS, and an empty read_file/read_dir policy before exec of its test code. The only descriptor deliberately passed to that child for target interaction was its retained end of a local socketpair to the mediator; no target file descriptor was passed. Rules allowed only the system read paths needed for the Python executable/runtime. The child then observed:

```json
{"direct_target":{"detail":"Permission denied","errno":13,"result":"denied"},"initial_request":"OK revocable-mediator-sentinel","after_revoke_request":"DENY authorization-revoked","symlink_alias":{"detail":"Permission denied","errno":13,"result":"denied"}}
```

The trusted mediator opened the fixture for the initial authorized READ, read the sentinel, closed that descriptor, and returned the bytes. It notified the supervisor; the supervisor changed the mediator's current authorization state to revoked and received `REVOKED` while the child and client socket remained alive. The next READ, sent by the same child over the same retained socket, received `DENY authorization-revoked` with no fixture bytes. The mediator logged `authorization_after_control: false` before processing that second request.

Separate negative control, not the restricted child: an independent unconfined child was deliberately given a preopened fixture FD and read `b'revocable-mediator-sentinel\\n'`. This demonstrates why the preopened-FD route is forbidden. No such FD was passed to the Landlock child.

One initial harness setup attempt failed before exec: `landlock_add_rule` returned EINVAL for `/etc/ld.so.cache` because the test helper requested READ_DIR on a file. The helper was corrected to grant READ_FILE only on that file and READ_FILE|READ_DIR on system directories; the setup diagnostic then reported `LANDLOCK_SETUP_OK`, and the bounded test above completed. This was a harness rights-mask correction, not a host or kernel policy failure.

## Trusted boundary and limits

For this tested configuration, the trusted mediator owns the target pathname access and mutable authorization state; the confined child owns only its socket endpoint for attachment operations. The supervisor's control endpoint can revoke mediator authorization. Landlock denies the child's tested direct target and one in-tree symlink opens. A still-connected socket is not itself a durable authorization: the mediator checked current state per request and denied the post-revocation operation.

This test proves neither revocation of bytes already returned nor protection against descriptors accidentally passed before confinement. It covers one child, one target, one symlink, two read requests, and a local socketpair. It does not test hostile peers, duplicate/inherited mediator channels, writes, races, complete path aliases, mediator compromise, or a full lifecycle. The negative control confirms that an FD crossing the trust boundary bypasses the demonstrated per-operation authorization. Do not generalize this small configuration into F3 acceptance.

No sudo, package install, sysctl/host policy change, `/tmp`, production service, real credentials, or non-loopback network was used. No production or unrelated process was inspected or altered.

## Next step / disposition

This minimal configuration enforced current authorization for the next mediated operation; retain it as a narrow mechanism result and stop here. Do not build a general proxy/bodyguard/runtime or lifecycle implementation. Reconcile future lifecycle work with B's partial F1 model. F1 remains incomplete, F5 independent review remains outstanding, and F3 acceptance is not claimed.