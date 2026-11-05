# Stored local latent versus effective path predicate

Frozen after79cf4a2. Original full-driver checkpoint reports C8 helper false but no
witness detail. First-context invariant result remains zero; neither fact decides
protected future widening. Cheapest named trace within containment-and-grants:
grant P SINK R, grant C SINK RW, seal C, move C to Q. Source predicts C latent R,
descendant D local latent RW but effective latent chain R, so the helper's local<=chain
predicate fails. Competing interpretations: actual future write widening; or a stronger
representation predicate than effective path constraints require in this trace.

Continue with actual Q grant/activate C, descendant grant RW/write attempts, read
grant/read positive, then seal/move D to P, activate D, widen P grant RW and retry D RW/
write. Reference should deny widening while read succeeds. Single latent_preserved=False
mutation should permit write under the same reachable schedule; report nondiscrimination
or other prerequisite failures honestly. Unrestricted P/C/D RW/write positive ensures
route/current source premise is usable. Parent AT-05 self-move is prior evidence;
this followup targets descendant plus later relocation/grant, not a repeated self test.

Record all actual prefix outcomes/states, local/effective latent, original helper C8
predicate, guard/oracle/resolve and invariant outputs. No broad BFS rerun. A failing
stored-local predicate is not automatically a demonstrated C8 effect failure; nor can
a passing finite use set prove universal safety. No canonical representation/checker
repair, minimality, physical host, power loss or full F1 acceptance. Next distinguish
actual effect counterexample from helper applicability before proposing changes.
