# Actual publication outcome versus missing receipt

Freeze from `26db6db361be986cdd168045f510f5567ee9df53` before source change/execution.
Prior rejected-publication case retained local z but witness stayed on the older cut;
startup correctly refused. Competing hypothesis: all missing publication receipts imply
that divergence. Alternative: witness update occurred, reply was lost, and actual local
cut already matches the witness, permitting conditional recovery without discarding z.

Smallest test extends the disposable witness with one explicit fault: consume a one-shot
flag only after successful CAS update, log the actual published reply and suppression,
then close the real HTTP connection without sending a response. Sink stays unchanged;
its ordinary transport exception must return503/local committed, no success ACK. Do
not substitute a fabricated successful/failed response or feed observer digest to it.

Three histories: (1) ordinary publication positive; (2) actual successful publication
with lost reply, then next same-process request and real same-file restart/new acceptance/
second cold restart; (3) rejection before update, later no-append and startup refusal,
retaining the local record. Each begins actual create/grant/activate and earlier x ACK.
For loss, require live witness revision/digest advance, sink transport-error evidence,
no successful z ACK, then fresh-nonce check of actual current cut before later acceptance.
Do not infer absence from no success ACK or force a permanent latch for matching state.

Record caller, wire/transport result, local bytes, witness suppression/update, process
identity/times, exact source/executable identities and missing-evidence/mutation controls.
At most two owned children active;256MiB inherited cap and finite process waits. Source
and packet committed before execution. Default witness behavior remains unchanged.

Conditional live witness/current-root/cooperative-single-writer/genesis premises persist;
same host, no witness power loss/source authentication/nonrollback establishment. Z is
an unACKed local committed event, not a success-ACKed event or absence of effect. This
does not reconcile a genuinely older witness cut, establish maximal availability, or
prove a general distributed protocol/C7/F4/F1 obligation. Next inspect source identity/
root custody or a new governing obligation rather than repeat arbitrary field faults.
