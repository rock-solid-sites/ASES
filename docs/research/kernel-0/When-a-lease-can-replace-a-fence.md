---
title: When can a lease replace a Work Unit admission fence?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Fencing-after-membership-rollback.md
  - docs/research/kernel-0/Custody-at-an-admission-closed-cut.md
  - docs/research/kernel-0/Transferring-and-reclaiming-resource-allowances.md
last_updated: 2026-11-28
---

# When can a lease replace a Work Unit admission fence?

An unreachable owner need not reply to a fence if a trusted deadline already ensures it can no longer apply old authority. The exact wait depends on which relation between the controller's clock and the effect owner's clock is established. A deadline checked when a request is queued, or a controller timeout after losing a reply, provides no such fence. [Admission closure](Fencing-after-membership-rollback.md) · [Gray and Cheriton, *Leases*](https://web.stanford.edu/class/cs240/readings/leases.pdf)

## Tight wait under a bound on relative clock readings

At each old admission gate i, an old operation may commit only while its trusted clock reading Cᵢ(t) is strictly less than Dᵢ. For this section Dᵢ is the exact latest eligible deadline for all old authority that could still commit at i, including delayed certificates. In a conservative application an upper bound suffices. Assume all such work checks the deadline at the effect decision. The clock premise holds through the covered failure and restore. No old renewal beyond Dᵢ can be issued or used, and no writable alias bypasses the gate. A separate selector clock Cₛ(t) decides when it may expose replacement.

Suppose Cₛ(t) − Cᵢ(t) ≤ δᵢ at every relevant effect time. At selector reading s, time alone certifies closure at i when

```text
s ≥ Dᵢ + δᵢ.
```

Indeed Cᵢ(t) ≥ s−δᵢ ≥ Dᵢ. Use the maximum threshold across all paths still requiring closure. This also blocks every future old effect if the clocks at effect owners cannot go backward after that threshold. With distinct absolute error bounds εₛ and εᵢ relative to a reference clock, use δᵢ=εₛ+εᵢ. A directly justified pairwise bound can be smaller.

The threshold is tight in the model that permits the maximal relative offset and a legal extant old grant, with no other discriminating observations. For s<Dᵢ+δᵢ, choose clocks with Cᵢ(t)=s−δᵢ below Dᵢ and schedule a legitimate old commit at the open gate after the selector's purported decision. For continuous clocks, a strict gap leaves a nonzero interval after that decision. A more correlated clock model or a separate fence receipt can exclude this witness and lower the bound. With equality allowed for gate admission, use a strict threshold. For discrete clock readings or bounded quantization, prove the appropriate rounded inequality.

## Tight wait under a bound on drift

Suppose instead the clocks have arbitrary offsets. At a known anchor moment, an authenticated observation gives gate clock at least Lᵢ and selector reading S₀. A remote observation received by the selector no earlier than its actual capture can use the selector's receipt as the anchor if the gate clock is nondecreasing. Give the selector maximum rate 1+ρₛ and gate i minimum rate 1−ρᵢ relative to real elapsed time, with ρᵢ<1. At selector elapsed Δ from S₀, real elapsed is at least Δ/(1+ρₛ). Therefore the lowest possible gate reading is Lᵢ+(1−ρᵢ)Δ/(1+ρₛ), giving

```text
Δ ≥ (1+ρₛ)/(1−ρᵢ) · max(0, Dᵢ−Lᵢ).
```

Use the largest such threshold for a common anchor, or evaluate each gate's own anchor. When there is a positive gap, the bound is sharp for independent rates by taking both extremal rates and the lowest allowed starting value. Without a lower reading anchor, the initial offset can be arbitrarily far below expiry. Without a positive progress bound across failures the remote clock could pause; no bounded local wait suffices. Network delay after a genuine monotone sample can improve the actual bound when independently measured from below. Unbounded delivery time does not invalidate the conservative receipt anchor. [Bounded drift and clock skew models, van Renesse, Schneider and Gehrke](https://arxiv.org/abs/1109.5111)

## What a deadline does and does not retire

- The deadline must cover the first authoritative effect, including work queued while valid. A previous expiry check followed by a newly delayed append is outside the proof. A lease that promises the eventual delivery of an irrevocably committed obligation has a different cut: later delivery can discharge that obligation and does not become a new exercise of the old grant.
- Deadline evidence is about the latest **possible** old use. An authenticated nondecreasing clock cannot compensate for a newer renewal certificate omitted by a restored selector. Before using the threshold, establish a complete bound on escaped renewals or make every renewal depend on a retained horizon. After reboot a gate can explicitly stay closed until it re-establishes the clock premise.
- No deadline implies which old appends actually happened, what their final extent was, or whether their content survives. A time fence can close future admissions and leave custody blocked. If a scoped read is itself a consequential disclosure, its authority also needs an effect-time check.
- A budget debit can end the right to initiate new charge at the receiver while an earlier charge remains live. With one unit, let the receiver accept just before expiry and keep that unit occupied. The source sees the same expiry as in a no-redemption history. Returning the unit based only on time violates the cap in the occupied history. A timed reclamation needs a separately established end to *all* charge or complete outcome and settlement evidence, including releases. [Final custody cut](Custody-at-an-admission-closed-cut.md) · [Allowance reclamation](Transferring-and-reclaiming-resource-allowances.md)

**Disposition.** An enforced lease can substitute for an unavailable admission response under an explicit clock, renewal and effect contract. It cannot be credited from the native sink's request timeout or from process appearance alone. A future runtime discriminator must establish where its clock lives, test an admitted operation straddling expiry at the effect boundary, and test a restart that loses clock assurance or an already issued renewal. No lease mechanism or runtime trial was selected here.
