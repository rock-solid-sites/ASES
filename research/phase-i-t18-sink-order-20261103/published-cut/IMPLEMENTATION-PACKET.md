# Selected published-cut witness/ACK experiment

Frozen fromf1e8b73 before implementation/execution. Governing distinction established
by authority-cut: current authority is not whole accepted-history currentness. New
conditional profile binds exact journal bytes plus authority in a live external
published-cut witness; no canonical schema, universal nonrollback or two-store atomicity.

Reuse original managed state/strict replay/persistence/HTTP handlers unchanged. New
bounded wrapper/witness only: trusted genesis seeds empty-journal/uncreated authority
once; witness serial check/CAS publish retains current published cut and revision,
root/nonce-bound replies. Cut is five authority fields plus SHA256 of actual journal.
Validate types/presence. Sink holds same stable-root cooperative writer lock before
state validation; startup strictly replays then checks actual cut against witness
BEFORE ready, never publishes recovered local state automatically. Existing all-writer/
stable-inode/root custody premises remain; no hostile confinement.

Every changing operation checks current cut under original sink lock, executes original
local durable event/state publication, then CAS publishes exact resulting cut using
prior witness revision/cut, validates reply before success ACK. This reuses original
authorization law, not a new Kernel contract. Failed publication returns503/local
commit explicit, retains actual local event, further mutations fail closed by mismatch,
and next startup refuses. Do not drop unACKed local event to match old witness. External
witness denotes last validated published cut, not complete knowledge of an unreported
irreversible local event. Recovery/reconciliation in this divergence remains open.

Four bounded histories:
1. Actual create/grant/activate/x201/q-commit201, same-current-journal process restart,
new y201, second restart retains x/y/q; each ACK correlates with persisted bytes and
validated newer witness publication. Stale-CAS publisher control denied unchanged.
2. Same genuine acceptances, kill/reap, restore earlier authentic management prefix:
original strict parser accepts but cut check refuses before ready, witness unchanged.
3. Same accepts, change x payload and its self-hash while preserving seq/version/count:
original strict parser accepts synthetic coherent mutation; published digest refuses
before ready. This is a mutation control, not authentic accepted alternative history.
4. Witness deliberately rejects publication after x ACK, next local z event persists
but response503/local_control_committed=true; later request has no new event/ACK, cold
startup refuses mismatched current file without modification or automatic publication.
No false C7 availability/full acceptance claim from that fail-closed limitation.

Capture actual full HTTP/caller/process/journal/witness transcripts, source/executable
hashes, positive/refusal/mutation/failure and missing-evidence controls. Runtime recovery
gets path/mode/endpoint only, no observer payloads/digest. Genesis is explicit trusted
initial-state premise.<=2 owned children at once,256MiB inherited/finite waits, no new
model workers unless post-build check justified. Source/witness trust and nonrollback
across covered file rollback are premises, not proven by liveness; no machine/witness
power-loss recovery, generic C7/F4/F1 closure or physical timing/host confinement. Exact
byte binding can conservatively reject semantically equivalent reencoding; no minimality.
No broad fault matrix/repeated field tests. Next reconcile divergence only if strongest
new uncertainty; otherwise select another unfinished governing obligation.
