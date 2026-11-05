# Actual sealed move publication interruption

Freeze fromcc7574fc057755863fd0f0bab227e77e535d0eaf before implementation/execution.
Same-ref Verification T12/F4 and Closure section7: sealed C moves P→Q with dependent D,
retaining old effective restrictions. Recovery must select an old or new whole relation,
not an invariant-valid half effect. Existing policy/manager overlap tests do not cover
actual interruption inside the original single-holder publication sequence.

Reuse unchanged l5_integrated.manager_roundtrip, commit, load_current, graph_valid,
permissions, enabled, verified_content and synthetic test_post_move_grant.setup. It
constructs an existing accepted-x fixture, NOT new L1-L5 acceptance/native confinement.
No Landlock invocation. All records/objects disposable; same test-only credential/trusted
current filesystem/single-holder premises, no source authentication/host failure claim.

Original strong move in three retained os.replace wrapper gates: before prepared full
record replaces its final name; after that record replacement but before CURRENT; after
actual CURRENT replacement before commit returns/manager reply. Capture path/bytes/
selector/process/caller evidence, SIGKILL/reap, drain stdout to EOF. Fresh process given
root only reopens CURRENT, validates graph/content, reports sealed whole state. First two
cuts must select exact old relation; third exact new relation/ceilings despite no observed
move ACK. Private .tmp/unselected records must not override CURRENT.

After each cold observation, separately authorized original activation then one mediated
test D-write request uses full current enabled/permissions guard; old P-read or new
retained read ceilings must deny, accepted x remains exact. No native worker enforcement
inferred. Uninterrupted original move must return COMMITTED with exact new state before
cold recovery; separate P-read/write activation/write is the concrete effect positive.

Mutation: publish C.parent=Q as one current record BEFORE ceilings, gate/kill before
second whole completion; resulting graph valid/sealed, but fresh activation permits a
concrete owned D-write. This controlled split publication is not an original L5 defect.
It must discriminate the whole-result obligation beyond graph validity alone.

Expected6 histories/12 children/max1 active;256MiB,<=3s frame waits, whole<=45s.
Commit sources before execution; retain source/executable identity, exact bytes and raw
caller/manager wire/gates/EOF/process metadata. Missing event evidence INCOMPLETE, wrong
whole state VIOLATION. No fsync added to original helper, physical power-loss/durable
storage claim, concurrent-writer/credential safety, other transitions or full F3/F4/T12
closure. Next genuinely new boundary or independent check, not another identical cut.
