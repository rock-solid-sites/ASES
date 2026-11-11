# Architectural basis and integration decisions

Source snapshot: parent 8de86a3c2e330c5d0d1b600f150334f56c928f85.
This bounded implementation does not redefine the methodology or promote a
resource-controller job to the canonical Work Unit concept.

`docs/architecture/Execution Engine Vision.md` calls for explicit state,
mechanical transition constraints and projects resuming from state rather than
reconstructed conversation (§Methodological State, §Persistent Project State).
`docs/research/Resource Solver Specification Reconciliation 2026-11-02.md` §5
separates admission, execution, accounting and evidence. It requires durable
commit before acknowledgement, distinct retry identities and reconciliation
rather than duplicate dispatch when an external launch is uncertain. Its thin
API includes controlled launch, compact status and explicit finalization.

The existing Rust implementation supplies the concrete state owner and the
launch/exit/resume transitions. The new adapter is a consumer of those APIs.
It adds the smallest missing runtime holder: actual owned Child handles and a
fixed trusted profile inside the existing Unix peer-authenticated gateway.
A stop request is a durable decision, actual wait is an observation, and
finalization is a separate semantic result/capacity decision. None stands in
for the others. The stop event shares the existing SQLite event owner rather
than introducing another journal or a scheduler.

A restart cannot preserve a standard-library Child handle. This design therefore
preserves an unknown outcome with held capacity rather than pretending a saved
PID provides ownership. A later native reconciliation/takeover route would
require an independently justified authority and exact observation interface.
This slice intentionally leaves that decision unresolved. It also retains the
existing decision-authorized dispatch semantics; current catalog revocation
after the intent does not retroactively imply termination.

The optional adapter does not give an orchestrator arbitrary launch authority.
Only the existing administrator peer role may invoke it, and its startup
profile supplies the executable and scope. Host/profile owner and executable
immutability are premises, not consequences of a command hash or JSON field.
Native tests can establish the actual local transition histories; they cannot
establish remote-provider cancellation, expense settlement, arbitrary workload
confinement or hard wall-clock quiescence.
