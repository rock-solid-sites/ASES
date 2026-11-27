---
title: Checking a history across repeated handovers
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-27
---

# Checking a history across repeated handovers

A verifier can check one ordered succession of tenures without searching the possible instants of every replacement. It needs to know what each observation says about tenure and which operations must precede others. The shape of a refusal matters. “That tenure has ended” constrains the decision to a suffix of the succession. “The installed tenure differs from the one named” may allow phases on both sides. The latter contract can require arbitrarily many probes to explain a failure.

## Interface and decision procedure

Fix a completed finite history at one continuing W/P with H completed replacements whose decision order is given. Number tenures 0 through H. For each fresh single-owner call supply the set of tenures consistent with its outcome under the stated contract. An append by tenure t requires {t}, a definitive stale reply to t requires phases greater than t, and a tenure-neutral busy reply can allow every phase. These sets express all remaining outcome conditions after local data verification. The apparatus admits read-only probes as well. Any issuer restrictions, such as grant acquisition before invocation, must already hold or supply additional edges.

Construct a directed graph with one vertex per call or replacement. Include the known replacement order, every required owner order, and response-before-invocation precedence. An owner order must reproduce the observed local data. Include any additional observed causal precedence on decisions. An observed causal link is sound only if it entails that order of decisions. For a partially observed trace, acceptance means that some completion consistent with the supplied edges works. A certificate of real-time conformance needs complete relevant real-time edges. Multiple alternative local witnesses may need separate checks if local data does not fix their order.

Give replacement j the singleton level 2j−1, for j starting at 1. A call consistent with phase p may take level 2p. Require nondecreasing levels on every edge. For an acyclic graph visit vertices in topological order. At each vertex choose the least allowed level at least as large as every predecessor's chosen level (initial lower bound zero). Fail if this choice is empty. A directed cycle independently rules out a strict decision order.

**Soundness and completeness for this interface.** A legal serialization assigns exactly such levels. Induct in topological order. Each greedy level is at most the level of the same vertex in any feasible assignment, since every predecessor's greedy level is a lower bound and the choice is the least admissible. Failure therefore rules out every assignment. Conversely, stable-sort the topological order by the chosen level. Every edge is preserved, each replacement occurs once, and each call sees a permitted phase. Per-owner effects follow the supplied witness. With ordinary call intervals and distinct endpoints, this total order also has decision instants inside the intervals. For each call the maximum invocation in the ordered prefix through that call precedes its response, since otherwise there would be a reversed real-time edge. Place successive decisions an arbitrarily small distance after these maxima, using finiteness to stay inside each interval. This extends the earlier interval test to any finite number of ordered changes. [Single-handover theorem](One-handover-across-resource-owners.md)

**Computational reduction.** Store the predecessor that last raised each bound. At a failed choice, tracing those links backward gives one path whose constraints alone are inconsistent. The first bound is zero, and each next bound is attainable as the greedy level at the previous path vertex. This makes failure replay possible without a solver or the other owners. Cycle reporting requires an ordinary cycle witness if the input graph itself is in doubt. With sorted allowed sets and binary search, choice costs O(log(1+s)) per vertex of set size s, plus linear graph traversal. For interval sets, choosing the maximum of the incoming bound and the local minimum takes constant time. Ordered buckets can emit a serialization in linear time in graph size plus H. Materializing all real-time edges can separately take quadratic space. The small Python reference favors explicit operations and uses sorting and scanning.

## When short explanations survive

Suppose the positions of the replacements relative to probe intervals are unconstrained, apart from their own known order, and the probe precedence graph is acyclic. A convex probe interval [a,b] then imposes exactly a ≤ p ≤ b. Failure occurs iff an ancestor's lower endpoint exceeds a descendant's upper endpoint (a vertex counts as its own ancestor). Induction gives the greedy phase as the maximum ancestral lower endpoint. Two observations and evidence of their precedence suffice, although the recorded causal path can itself be long. This restricted corollary does not bound arbitrary shared-effect histories.

Now allow a read-only observation “different from i” for every i, with comparisons permitted to name provisioned phase labels before selection. For any n ≥ 2 take n phases and a sequential client making n comparisons in the order 0 through n−1. All replies are “different”. Let all n−1 replacements overlap these calls and one another, with their decision order fixed. After comparison 0 the phase must be at least 1. After comparison i it must be at least i+1, by induction. The last reply is impossible. Deleting any one comparison j allows the constant phase j throughout the surviving comparisons, with the required replacements ordered before and after them. Thus there is no uniform probe-count bound for this contract even with a single client. An owner whose API compares only issued past grants and returns a definitive stale result has a different observation alphabet. Applying this family to it would require evidence that these probes can actually be issued.

## Reproduction and assurance boundary

Run `python3 docs/research/kernel-0/phase_histories.py`. For two probes and two ordered replacements the script compares greedy feasibility against direct operational replay of all serial permutations. It checks all 1,024 subsets of the ten other possible directed edges, including contradictory orders, and all 49 pairs of nonempty phase sets. Of 50,176 cases, 3,793 admit a serialization and 46,383 fail. Returned schedules and reported obstruction paths are checked. The script also checks the minimal family at 2 through 11 phases and every single-probe deletion. The general claims above follow from the arguments, independently of these finite counts. [Executable experiment](phase_histories.py)

This is a passive verification result conditional on the contract and evidence. ISOLATE and CONNECT still owe a trustworthy scope and provenance for calls and their observed effects. ORDER can use this test for a proposed shared decision order. Recovering unknown replacement order, incomplete calls, independent alternatives for local data order, and agreement between a real owner and its trace remain open. The original neutral packet explicitly separates model adequacy and realization correspondence. [Requirements](Kernel-0-Evidence-Packet.md) · [Tenure and delayed admission](Tenure-reuse-and-delayed-admission.md)
