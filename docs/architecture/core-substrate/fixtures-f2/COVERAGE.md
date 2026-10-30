# F2 coverage matrix ? Agent C

Scope: this increment adds executable abstract-replay histories for selected portions of T01?T04 and T06?T10. `executed` means replayed by the independent `f2lib.py` reference model only. It does not mean a host/runtime fixture was executed. Raw observations and mutated-run outputs are in `results.json`.

| Trace | Coverage in this increment | Status | Known gap |
|---|---|---|---|
| T01 | Ancestor-only grant denial; child-only grant denial; full-path read positive; ancestor-check mutation | executed | No explicit write/path enumeration or concrete route test |
| T02 | Replacement position advance followed by stale old-generation claim; source-binding mutation | executed | No before/after commit race pair or new-ingress x continuation witness |
| T03 | Reuse of represented old capability; source-binding mutation | executed | Physical source binding/bearer secrecy require runtime evidence; not tested here |
| T04 | Two unit-capacity reservations; capacity-check mutation; independent order commit positive | executed | Three-way cyclic separately validated commitments not yet fixtured |
| T05 | ? | blocked | Engine-loss retained routes and CPU-only positive control not fixtured |
| T06 | Exact checked-byte substitution rejected under binding; trusted-copy positive survives producer loss; content-binding mutation | executed | Abstract replay only; no filesystem swap or real producer-loss evidence |
| T07 | Pre-preparation interruption; acknowledged commit with lost reply survives crash/recovery; WAL-before-ack mutation | executed | Only these two abstract endpoints; no concrete crash/storage fault injection |
| T08 | Restore old authentic snapshot after y/revocation; fresh credentials followed by untrusted-currentness discovery leaves unit sealed | executed | Abstract model only; rollback resistance is expressly outside the baseline premise |
| T09 | Wrong-root, incomplete-content, and incompatible-interpretation images are quarantined/refused | executed | No real parser/decoder or storage-image corruption path |
| T10 | Recovery lost after validation; rediscovery/revalidation before fresh activation | executed | No duplicate external-effect/revived-channel check beyond modeled state |
| T11 | ? | blocked | Sealed move with latent restriction and D witness not fixtured |
| T12 | ? | blocked | Empty-check race, coupled-move recovery, and half-effect rejection not fixtured |
| T13 | ? | blocked | Interrupted dependent disposition and stale-reference exposure not fixtured |
| T14 | ? | blocked | Authentic pre-revocation derivation submit/recompute positive not fixtured |
| T15 | ? | blocked | Omitted graph, phantom child, and complete-empty removal not fixtured |
| T16 | ? | blocked | Scoped observation and qualified model-judgment variants not fixtured |
| T17 | ? | blocked | Unknown sink retry, immutable read, and missing-currentness cases not fixtured |
| T18 | ? | blocked | Exact-obligation versus use-current external-effect profiles not fixtured |
| T19 | ? | blocked | Indistinguishable lost-reply histories and sink contract distinction not fixtured |
| T20 | ? | blocked | Isolated-holder takeover/resume conflict histories not fixtured |
| T21 | ? | blocked | Cache deletion/half-derivation recovery and historical output witness not fixtured |
| T22 | ? | blocked | Boundary metadata, routes, management authority, and information-flow cases not fixtured |
| T23 | ? | blocked | Unaccepted durable candidate confinement and ephemeral scratch separation not fixtured |
| T24 | ? | blocked | Ordered/rejected/partial ACL policy changes, out-of-band broadening, and open-access observation not fixtured |

## Discriminating mutations executed

- T01 `ancestor_checking=false`: the child-only grant reaches the intended stale-authority fault and admits, violating expected denial.
- T02 `source_binding=false`: the stale position claim is admitted.
- T03 `source_binding=false`: reuse of the represented old capability is admitted.
- T04 `capacity_check=false`: the second reservation exceeds capacity.
- T06 `content_binding=false`: substituted bytes are admitted.
- T07 `wal_before_ack=false`: acknowledgement may occur while the committed journal lacks the value.

These mutations are controls on the abstract oracle, not implementation mutants. The matrix is intentionally not an aggregate T01?T24 passing claim. Tests requiring a host, process, descriptor, concrete route, storage rollback, or ACL remain unexecuted until such an independent fixture harness is available.
