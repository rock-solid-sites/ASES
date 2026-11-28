---
title: When does delegated authority remain grounded after withdrawal?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Kernel-0-Evidence-Packet.md
  - docs/research/kernel-0/Reparenting-and-surviving-withdrawals.md
  - docs/research/kernel-0/Minimum-revalidation-at-commit.md
related_documents:
  - docs/research/astra-followup-20261125/frontier-comparison/ROUND2-COMPARISON.md
last_updated: 2026-11-28
---

# When does delegated authority remain grounded after withdrawal?

Two roles can give each other a live entitlement while a third issuer originally supplies the right. Withdraw the issuer. An engine that keeps a role live whenever it has one currently live supporter can retain both roles indefinitely. Both local checks still pass. Neither role then has a derivation from a current issuer. This possibility is specific to recursively resolved delegation. A design with explicit acyclic grant incarnations can avoid it structurally. [Compared kernel candidates](../astra-followup-20261125/frontier-comparison/ROUND2-COMPARISON.md)

## One finite positive model

At one coherent owner cut let V be a finite set of distinct authority claims. These claims bind action, resource, scope and, where relevant, incarnation. Let B be the claims supplied by currently valid independent roots. Let R be a set of authenticated, currently admissible rules P→v, where P is a finite set of prerequisite claims and v is one conclusion. Rules may use several independent approvals conjunctively and may allow alternatives by sharing a conclusion. Policy validity, scope attenuation and which roots are independent are premises. A rule without prerequisites has root-equivalent power and must be administered accordingly.

Let F(X)=B ∪ {v | some rule P→v has P⊆X}. Iterate from the empty set until saturation G. G is exactly the set with finite proofs whose leaves are B or explicit empty-premise rules. Each inclusion in the iteration constructs a finite proof by using earlier inclusions. Every finite proof is included by induction on its height. Monotonicity gives termination and the least fixed point. An effect explicitly promised to require a grounded derivation must use G or an independently verified proof within G.

Consider B={r} and rules r→x, x→y, y→x. Initially G={r,x,y}. Remove r and keep the rules. G becomes empty. A cache that removes r and merely decrements a support counter for x sees x still supported by y and y still supported by x. The cached state {x,y} is another fixed point. Any verifier that checks only the local equation for this state accepts it. Explicitly grounding a proof in current independent issuances is the missing obligation. Local cycle detection alone can also reject too much. Add another live root s and rule s→y; now both x and y remain valid through a finite current proof despite the cycle. [Delegation and authenticated principals, Lampson et al.](https://www.microsoft.com/en-us/research/publication/authentication-in-distributed-systems-theory-and-practice/) · [Recursive materialization under deletion, Motik et al.](https://www.cs.ox.ac.uk/boris.motik/pubs/mnph19maintenance-revisited.pdf)

## Which cached claims need reconsideration?

Fix two coherent snapshots with roots B₀,B₁ and rules R₀,R₁. Start with an exactly grounded cache G₀ for the first. Make a directed graph placing p→v for every p∈P in every rule P→v in the union of both rule sets. Mark all changed roots and every changed rule's head. Let D contain the marks and their reachable vertices. Then:

- Outside D, the grounded answer is unchanged. No rule with a head outside D changed. Its prerequisites are also outside D, because an edge from D would make the head reachable. Its fixed-point calculation is thus independent of D and identical in both snapshots.
- Inside D, discard cached answers and saturate under the new roots and rules, treating the agreed values outside D as fixed boundary inputs. This gives the exact new grounded state. Boundary inputs already have complete proofs without D, so any derived inside proof expands to a full grounded proof. Conversely, restricting any full proof to the induced calculation merely replaces outside subproofs by proved premises and still derives its conclusion.
- With this choice of marks, either single graph gives **exactly the same reachability region** as their union. For example every union edge absent from the new graph came from a removed rule, and its destination is already a marked head. Along any union path, discard everything before the last such edge and start from its marked destination. The rest is a path in the new graph. The old graph has the symmetric argument for added rules. Thus the verifier can traverse the currently available graph if it can enumerate every changed head. Traversing from changed roots alone is insufficient when rules can change. An omitted head can lose its only support even with every independent root unchanged.

This is a conservative restart region, not a claim that every reachable vertex changes. An independently maintained live proof for a particular claim can be reused when all of its needed bounds survive. A read materialization must still reflect a coherent root and rule cut. An effect cannot consume a proof once it has become stale. The same-source incarnation, scope and commit-time revalidation remain necessary even with correct fixed-point calculation. [Commit observations](Minimum-revalidation-at-commit.md)

## Structural elimination and what it costs

If each new grant references only exact, already existing immutable grant incarnations in a strictly earlier well-founded issuance order, delegation edges cannot form a cycle. In a finite dependency DAG, the fixed point is unique and can be determined in topological order. A work-list using active root and rules counts can propagate changes without circular retention, provided a rule's count changes when any prerequisite changes and every relevant edge is covered. The trusted order is a construction property of issuances. A timestamp supplied by the grant recipient is not a witness of it.

This arrangement can support named account or role cycles as application data while keeping actual derivations acyclic. It treats a proof of the old role incarnation as permanently dependent on that incarnation. It cannot emulate an entitlement that silently retargets a prerequisite to the latest role grant after an upstream withdrawal. Retargeting must be a new authorized issuance or an explicit dynamic policy feature. A governor-only direct grant eliminates the recursive problem entirely if autonomous delegation is outside the intended contract.

The cost moves across time. A single root can support n otherwise independent queried claims, each independently affected by its own policy changes. With one fully materialized answer per claim and no additional shared freshness test on use, withdrawing that root can require changing every answer before a fresh admission is allowed. A proof-at-use scheme or a trusted common invalidation epoch can avoid rewriting every entry at withdrawal, while placing verification or refresh on uses. These are placement trade-offs. The proof gives no runtime benchmark or cache layout requirement.

**Disposition.** The results qualify the delegation choice, without selecting recursive rules or a grant representation. A dynamic delegated model requires grounded policy semantics and an issuance/currentness proof at the effect cut. An acyclic incarnation model avoids circular support for the narrower policy contract. A focused future implementation check would start from the root-withdrawal counterexample and a retained independent-root control, with withdrawal and effect ordered at the actual owner. W5/W6 on the pinned native stack still lack an authenticated replacement interface. This analysis launches no runtime experiment.
