---
title: Which changes of managerial authority preserve a compact seal record?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Which changes of managerial authority preserve a compact seal record?

Suppose a Work Unit retained the minimum state required to answer future seal queries under its current release policy. A change in managerial authority can make discarded distinctions observable. Two questions have different costs: deciding whether one known migration is lossless, and deciding which earlier histories can ever be distinguished along a branching succession of policy changes. [Fixed-policy state minimization](How-much-seal-state-survives.md)

## One migration needs a pairwise check

Keep the same n veto causes. Each release command clears its specified subset. Write E_i for the old set of commands that clear cause i and F_i for its new set. Old and new commands need not have the same names. Migration preserves the actually asserted causes and changes only the permitted release operations. Query and management replies follow the fixed-policy contract.

An exact translator from **every reachable old minimum summary** to the new minimum summary exists if and only if

```text
for all causes i,j: if E_i is a subset of E_j, then F_i is a subset of F_j.
```

Necessity compares the states with causes {i} and {i,j}. Old minimization identifies them whenever E_i is contained in E_j. Under the new policy their summaries agree precisely when F_i is contained in F_j. For sufficiency take each minimal clause in the old summary, pick any cause representing it, replace it by that cause's F, then minimize. Equal old signatures have equal new signatures by both directions of the test. Every discarded old superset still maps to a new superset, so the result equals direct minimization of the original causes. This gives a translator and a two-history counterexample on failure. A single new release command must clear an upward-closed set in the old inclusion preorder if all other commands stay fixed. Authority changes involving permanently blocked causes enter the same test through empty signatures.

This result concerns the ability to implement the new *future* contract after a known transition. It requires neither storing the original set of causes nor replaying their full assertion history when the condition passes. A failure cannot be fixed by merely changing the schema version on the old summary.

## Why separately correct summaries can be insufficient

Let A and B be two policy modes. Cause p is unreleasable in both. Cause a can be cleared only in A; b only in B. Compare histories {p} and {a,b}. They yield identical observable behavior if confined forever to A, and also if confined forever to B. Even the pair of both independently minimized summaries fails to distinguish them. In A clear a, move to B, clear b and query. Only the second history now permits the effect.

This example distinguishes an immediate choice of one permanent policy from a sequence that can combine their respective operations. If modes can be visited freely without changing the asserted facts, an exact summary can instead use all available mode-qualified release commands at once. Every release subset used to distinguish two initial states can be realized by visiting its modes. If some upgrades foreclose other branches, that union may preserve distinctions that no permitted execution can observe.

## Distinguishability with constrained upgrades

Fix an explicit finite directed graph of modes, a start mode, and the release subsets available at each vertex. Upgrades and assertions acknowledge independently of the causes. They never silently clear old causes. Two initial veto sets X and Y are distinguishable exactly when, in one direction, a walk can clear all of Y while preserving some cause i in X. To test a chosen i, retain only releases that do not clear i. At each visited mode take the union of their clearable causes. A walk distinguishes when that coverage contains Y. Newly asserted causes can be omitted from a witness: they add the same outstanding facts to both runs; a query that permits on one side cannot depend on a surviving newly asserted cause. A witness with no releases or an initially empty side is included.

In a strongly connected component all its modes can be visited before taking a chosen outgoing edge. Thus a certificate is a choice of direction, cause i and one forward path of components in the acyclic condensation graph. Check its coverage in polynomial time. With a linear succession of freely visitable modes the coverage calculation is direct. On a general branching upgrade graph the decision problem is NP-complete.

For hardness, take a Boolean formula in conjunctive normal form. Give Y one asserted cause per clause and X a single permanently asserted cause p. For each variable create one layer with two mutually exclusive successor modes, representing true and false. Lead each choice to the next layer. Its release command clears the clause causes satisfied by the selected literal. A walk can clear every clause exactly when one consistent truth assignment satisfies the formula. A distinguishing prefix extends to a full assignment, since further choices cannot invalidate already satisfied clauses. All states and commands in this reduction are explicit and polynomial in the input. This proves worst-case complexity for existence of a distinguishing continuation under declared upgrade paths. It is independent of the cost of one-step migration.

## Evidence

`python3 docs/research/kernel-0/seal_policy_evolution.py` compares the pairwise test with direct summary tables for every pair of three-cause, two-command policies. Of 4,096 migrations, 874 admit exact translation and 3,222 lose a distinction. For every passing pair the representative-based translator reconstructs each reachable new summary. A paired transition search including new assertions checks the two-mode counterexample. A separate test compiles all 256 subsets of the eight nonempty nontautological clauses on two variables into upgrade graphs. Reachability agrees with truth-assignment enumeration on 95 satisfiable and 161 unsatisfiable formulas. [Executable checks](seal_policy_evolution.py)

These are representation and assurance results for a fixed observable management interface. If management actions reveal which cause was cleared, upgrades create new vetoes, or the operator requires causal attribution after recovery, a different equivalence is needed. The result identifies when a change to CONNECT's management operations changes what ISOLATE must durably preserve, even if the current user-facing allow/deny predicate stays identical.
