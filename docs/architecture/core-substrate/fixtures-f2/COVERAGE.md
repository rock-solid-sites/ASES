# F2 coverage matrix - Agent C

Scope: this increment adds executable abstract-replay histories for selected portions of T01 through T24. `executed` means replayed by the independent `f2lib.py` reference model only. It does not mean a host/runtime fixture was executed. Raw observations and mutated-run outputs are in `results.json`.

| Trace | Coverage in this increment | Status | Known gap |
|---|---|---|---|
| T01 | Ancestor-only grant denial; child-only grant denial; full-path read positive; ancestor-check mutation | executed | No explicit write/path enumeration or concrete route test |
| T02 | Replacement position advance followed by stale old-generation claim; source-binding mutation | executed | No before/after commit race pair or new-ingress x continuation witness |
| T03 | Reuse of represented old capability; source-binding mutation | executed | Physical source binding/bearer secrecy require runtime evidence; not tested here |
| T04 | Three separately validated proposals with cyclic precedence are all refused; disjoint independent proposal commits; common-order weakening admits the cycle | executed | Bounded abstract trace only; not exhaustive over all proposal graphs |
| T05 | Explicit event sequence prepared for engine death with retained route and CPU-only positive control | prepared-only | Requires real process/descriptor mediation and independent live-computation observation; excluded from replay totals |
| T06 | Exact checked-byte substitution rejected under binding; trusted-copy positive survives producer loss; content-binding mutation | executed | Abstract replay only; no filesystem swap or real producer-loss evidence |
| T07 | Pre-preparation interruption; acknowledged commit with lost reply survives crash/recovery; WAL-before-ack mutation | executed | Only these two abstract endpoints; no concrete crash/storage fault injection |
| T08 | Restore old authentic snapshot after y/revocation; fresh credentials followed by untrusted-currentness discovery leaves unit sealed | executed | Abstract model only; rollback resistance is expressly outside the baseline premise |
| T09 | Wrong-root, incomplete-content, and incompatible-interpretation images are quarantined/refused | executed | No real parser/decoder or storage-image corruption path |
| T10 | Recovery lost after validation; rediscovery/revalidation before fresh activation | executed | No duplicate external-effect/revived-channel check beyond modeled state |
| T11 | Sealed move read positive for C/D; per-step observations show latent write denial; weakened move mutation loses the restriction and admits write | executed | Abstract replay only; no concrete structural/ACL route test |
| T12 | Whole-effect coupled move positive; child created after empty check blocks removal and retains containment; stale-empty-check mutation strands child | executed | Abstract model only; recovery interruption/half-effect variants remain unfixtured |
| T13 | Candidate/dependent disposition then removal; retained-reference removal refusal (runner now checks delete reason) | executed | No interrupted recovery between individual disposition steps or real stale-handle probe |
| T14 | Pre-revocation snapshot denied after revocation; fresh healthy snapshot positive | executed | Abstract derivation only; authentic runtime provenance not established |
| T15 | Omitted graph cannot prove emptiness; correct empty enumeration followed by phantom child blocks removal; complete current empty boundary is removed; stale-check mutation strands phantom | executed | Abstract relation enumeration only |
| T16 | Model confidence without explicit authority is denied | executed | Scope-limited observation and expressly authorized qualified-decision variants not fixtured |
| T17 | Lost sink reply leaves outcome unknown and permissive retry flags duplicate possibility; independent read positive | executed | No irreversible-write guard profile that authorizes/restricts retry by policy |
| T18 | Exact-obligation later delivery executes; separate use-current sink-order case is preserved prepared-only | mixed: executed + prepared-only | f2lib has no sink-side current-authority ordering event; no use-current safety claim |
| T19 | Permissive profile accepts twice; at-most-once contract yields accepted count 1 and `duplicate_possible=false`; disabling contract yields count 2 and true | executed | Abstract sink contract only; no concrete sink effect evidence |
| T20 | Isolated-holder takeover refused; first acceptance allowed and second conflicting acceptance denied; disabling holder exclusion admits it | executed | Abstract replay only; no physical fencing/exclusion witness |
| T21 | Killed partial derivation denied; recomputed derivation positive | executed | No accepted historical output/evidence retention witness |
| T22 | Interior parent edit denied; metadata-separation mutation admits it; creator metadata alone gives no write authority | executed | No exposed-route/completion export/parent-code management runtime cases |
| T23 | Unaccepted candidate blocks removal; accepted candidate disposition allows removal; accepted-only mutation admits incomplete delete | executed | Ephemeral scratch teardown remains unfixtured |
| T24 | Ordered revocation-before-use denied with `ac_ordering=false` mutation admitting use; out-of-band state is classified inconsistent with revoked Kernel state and disclosed outside boundary; weakened consistency mutation misclassifies it | executed | No open-handle invalidation observation or concrete ACL enforcement evidence |

## Discriminating mutations executed

- T01 `ancestor_checking=false`: the child-only grant reaches the intended stale-authority fault and admits, violating expected denial.
- T02 `source_binding=false`: the stale position claim is admitted.
- T03 `source_binding=false`: reuse of the represented old capability is admitted.
- T04 `capacity_check=false`: the second reservation exceeds capacity.
- T04 `common_order=false`: all three cyclic proposals commit.
- T06 `content_binding=false`: substituted bytes are admitted.
- T07 `wal_before_ack=false`: acknowledgement may occur while the committed journal lacks the value.
- T19 `sink_at_most_once=false`: retry results in a second accepted sink effect and `duplicate_possible=true`.
- T12 `stale_empty_check=true`: the concurrent child is stranded using stale empty evidence.
- T15 `stale_empty_check=true`: the phantom created after enumeration is stranded.
- T24 `ac_ordering=false`: post-revocation use is admitted under broadened policy.
- T24 `ac_consistency_checking=false`: out-of-band broadening is misclassified as consistent with revocation.
- T20 `holder_exclusion=false`: the second conflicting acceptance is admitted.
- T22 `metadata_separation=false`: an interior edit changes parentage.
- T23 `complete_domain_checking=false, check_accepted_only=true`: deletion ignores an unaccepted durable candidate.

These mutations are controls on the abstract oracle, not implementation mutants. Latest runner snapshot: 46 abstract histories executed, 2 prepared-only (T05 and T18 use-current), and 0 blocked; 16 mutations discriminate their named faults. The matrix is intentionally not an aggregate T01 through T24 passing claim. Tests requiring a host, process, descriptor, concrete route, storage rollback, or ACL remain unexecuted until such an independent fixture harness is available.
