# Concrete → proposed abstract transition map

Research mapping, not a new specification. Comparator: Phase-I-Closure §7 C1–C13 and
Phase-I-Verification F1/F3/F4 at `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a`.
Exact source paths/hashes are in the capture's `sources/source-index.json` and `raw.json`.

An abstract state for this investigation retains **separate** accepted content and opaque
observations, object identity and bytes, containment and latent rights, inventory and
physical material, sink authority, local effects, publication and knowledge of receipt.
Equality of content hashes is insufficient for equality of accepted observation worlds.

## Native interfaces and trust boundaries

| Interface | Native identity types | Trusted inputs and assumptions | Missing cross-component binding |
| --- | --- | --- | --- |
| F1 C11 | root/profile/schema in SQLite; integer channel context; two admitted content strings; four opaque string observations | Supervisor associates inherited socket with context and supplies truthful observations; current SQLite file/interpretation, runtime and host trusted | No L5 unit/object, L6 dependency identity or F4 authority version; observations are optional on cold holder configuration. |
| L5 | fixed names P/C/Q/D; accepted identity string and object path/hash/size; fixed W-L5 ingress | Trusted current filesystem/manager, static test credential, one holder; atomic replaces under a surviving host | No F1 acceptance verifier; no native L6 lifecycle link; no F4 use-point fencing. Matching credential is not physical manager authentication. |
| L6 | one implicit unit per root, no unit-ID column; flat lowercase object name; accepted/candidate kind; hash/size/disposed | Trusted management input, complete flat enclosing root, all cooperative writers take BEGIN IMMEDIATE; SQLite FULL/DELETE | Equal bytes do not distinguish F1 opaque evidence worlds; `x` is only an adapter alias; L5's graph/store are not inventoried. |
| F4 | flat constant C/p; integer authority version and holder label; opaque request ID/payload; witness root string, nonce and typed cut | Trusted bootstrap/publisher/witness, live witness memory, stable-root writer-lock inode, local management channel, journal and host | Descendant, acceptance provenance and L6 unit lifecycle are not admission inputs; copied payload identity confers no authority. |

The envelope used here is an **adapter-defined data type**, not a type accepted as
authority by these interfaces. The aliases are retained for observation; the harness
does not promote them into Kernel definitions. Source truth, current applicability,
host isolation and retention are distinct obligations.

## Transition observations

| Concrete observation / linearization candidate | Proposed abstract meaning | Required premise / result |
| --- | --- | --- |
| F1 `BEGIN IMMEDIATE`; read current kernel row | Start guarded proposal | SQLite serializes the relevant local state, not other components. |
| F1 `UPDATE kernel` and `INSERT consumer_observations` within the transaction | Prepare accepted pair | Uncommitted rows are not a new accepted state. |
| F1 SQLite `COMMIT` returns, with both writes | Commit accepted pair | Observation truth is trusted input; source truth/authentication is not proven. |
| F1 prepared gate + actual SIGKILL/reap | Abort uncommitted preparation | Cold independent reader observes old content and its old binding. |
| F1 durable gate + SIGKILL before reply | Commit with unknown caller outcome | Cold reader observes new pair; absence of reply cannot map to denial. |
| Recovered F1 with no observations: `accept(other content)` commits only UPDATE | **No legal paired-accept transition** | New content plus old incompatible binding; must refuse or obtain a supported new bundle to realize that contract. |
| F1 non-accept `restrict` with a new configuration tuple | Evidence mutation on unchanged content | Not stuttering under an observation-retention map. Requires an explicit configuration/accepted-evidence lifetime rule; absent from the wrapper's interface. |
| Adapter builds L5 fixture from F1's actual accepted pair | Trusted **test-only import** | Not native F3 acceptance, authentication or a source transition proven by this experiment. |
| L5 full new record written/replaced, CURRENT still old | Private preparation / stutter | Only CURRENT selects the authoritative record; no fsync/power-loss inference. |
| L5 `os.replace(CURRENT.tmp, CURRENT)` selecting whole moved record | Sealed whole move C P→Q, D retained | Both C/D ceilings must retain old path restrictions; single current holder premise. |
| L5 separate authorized activation | Activate currently permitted route | Recompute selected full-path authority including descendant ceiling. |
| L5 D-write request | Current mediated use or denial | Observer independently intersects selected path restrictions and activation. Test worker is not a confined hostile executor. |
| Competing L5 activation overwrites record2 after mover's comparison | **No successful whole-move explanation** | Mover returns COMMITTED but cold C remains under P and active; matching receipt hash alone does not prove move meaning. Outside original single-holder premise. |
| L6 put fsyncs file and commits dependency row | Commit local accepted/candidate inventory item | Alias `x` has no native F1/L5 causal identity. All writers and enclosing root must be complete. |
| L6 file fsync; kill before dependency COMMIT | Bounded unknown material | Catalog rollback leaves x; original inventory guard retains live sealed unit and denies removal. |
| L6 disposition COMMIT then unlink | Logical disposition, then physical cleanup | Distinct steps; no atomic erasure claim. |
| L6 inventory scan under BEGIN IMMEDIATE, empty removal COMMIT | Remove **local** inventory unit | Safe against cooperative local creator; cannot infer no L5 dependents outside its domain. |
| Detached scan mutation; creator COMMIT; remover COMMIT | Invalid removal control | Physical x survives with local live=false. This is the pinned deliberate mutant. |
| L6 local removal while L5 object persists | Not global Work Unit destruction | If both are asserted to be C, lifecycle and complete-domain proof are missing. |
| F4 fresh root/cut `/check` | Establish local cut eligibility | Live trusted witness and source/root custody assumed; nonce is not source authentication. |
| F4 native journal append + fsync | Irrevocable **local** effect / obligation | Local authorization is flat C/p version only; it says nothing about D or L6 liveness. |
| Witness CAS `/publish` accepted | Publish new cut | Separate from local commit; witnesses retain state only in memory. |
| Sink validates publication response then returns 201 | Known successful published effect | Exact journal hash/revision/root/nonce observed; no inference of L5 authority from that receipt. |
| Witness updates, suppresses actual HTTP reply, sink returns 503 | Published effect, receipt unknown | Actual remote outcome differs from caller knowledge; same-ID retry creates another effect under the permissive profile. |
| Witness rejects publication after local commit | Local commit, publication refused | Later write has no new append; cold startup refuses; local record remains. |
| `/submit` rejected with wrong version, then current-version success | Volatile denial then valid commit | Rejection may consume seq=4 without a durable row. Durable sequence 1,2,3,5 is valid. |

## Why a simulation has not been established

`composition_state_explorer.py`'s `object` scalar collapses L5 import, L6 inventory and
the external alias map. There is no native transition maintaining that equality. Its
`accept_pair` makes pairing true by construction; the native cold accept without a new
bundle has no corresponding safe step. Its `attach_object` requires a delivered F1 ACK,
although an actual irrevocable accepted pair can survive a lost reply. A correct future
map must admit continuation justified by current readback, not require an ACK history
that recovery never receives.

The composition model also permits `append_event` after a moved read-only unit activates:
that step never checks `ceiling`. If the event is intended as a descendant write, its
oracle omits precisely that cross-component authority condition. If the event is a
separately authorized audit publication, accepting it can be valid, but it cannot stand
for the protected descendant effect tested here. Selecting the latter interpretation
would change the effect contract; this investigation does not make that selection.

The L5 model has one selected relation and one online holder. It cannot express two
original managers passing the same comparison and replacing the same record name.
The L6 model's one dependency bit has no representation for L5's separate retained
accepted object. The published-cut model's local/published/ACK distinction is useful,
but does not add cross-store identity or authority to the native sink.

These are domain/transition adequacy gaps. Additional model depth or repetition of the
same selected traces cannot close them. Local steps can refine separate local contracts
while their asserted common Work Unit interpretation fails C1/C2/C3/C8/C9/C10.

More precisely, the proposed relation reads the F1 pair from its two SQLite rows, L5
content/authority from CURRENT and the selected object, inventory from L6's live row,
dependencies and actual files, and local/published/known outcome from F4's journal and
wire exchange. Under the declared **use-current D-effect** interpretation, each new
F4 effect must have eligible D authority and a live owning inventory domain at its
acceptance point. The captured denial/publication history has no such step. Mapping
it to a separately authorized audit event would change the requested effect meaning.
Likewise, ignoring the incompatible F1 observation row would erase required C11
observations rather than establish refinement. These are falsifying traces for that
proposed relation, not a proof that every possible trusted composite is impossible.
