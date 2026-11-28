---
title: What can native recovery restore from surviving history?
version: 0.1.0
program: ASES
layer: Research
document_type: Research Argument
status: Experimental
authority: Derived
canonical_repository: ases
depends_on:
  - docs/research/kernel-0/Native-owner-selection-rollback-result.md
  - docs/research/kernel-0/Reconstructing-a-cut-from-prepared-updates.md
  - docs/research/kernel-0/When-split-authorities-can-publish-separately.md
last_updated: 2026-11-28
---

# What can native recovery restore from surviving history?

The [R2 case](Native-owner-selection-rollback-result.md) retained the actual F4 acceptance and every immutable owner record. The retry returned an exact historical acceptance while the selected owner still lacked a settlement. This suggests a narrow repair for historical observations. Recovering current authority or proving that no effect is pending is a different problem. The following indistinguishability argument establishes the difference for the native source.

## An eventless owner decision can be absent from an intact F4 cut

Consider a common prefix of the native prototype with selected owner record S, a live domain and an active sink. Prepare the same fresh native request B in two native histories. The append guard checks the F4 base cut and owner data, then reserves B by constructing a new immutable record T. The owner writer durably installs T's file before it durably advances `CURRENT`. Choose these continuations:

1. The owner stops after the file T is durable but before it starts writing the replacement pointer. S remains selected.
2. The owner selects T, then stops at the gate before any journal append. Restore its selection to the genuine S. B was reserved at the actual owner boundary. No F4 event for B exists.

In both histories keep the immutable files, journal and F4 witness state. Lose the in-flight request's outcome and any external observation of T's actual selection. Both histories can have the same retained source directories and journal, the same S selection, the same staged T bytes, and the same unchanged F4 cut. T was a prepared record in the first history and a selected eventless reservation in the second. Physical identity of an immutable file or monotonicity of record numbering cannot distinguish those facts. An external log known to record owner selection, a crash boundary proving whether selection had occurred, or an operator decision about abandoned eventless attempts would change the available evidence. This pair follows from the write order and selection contract. It was reasoned from source and did not use a new fault injection. [Record before pointer](https://github.com/rock-solid-sites/ASES/blob/0bd51a34700164a5eb77efe98158fa37d1a74e23/docs/research/phase-ii-native-ownership/native_owner.py#L93-L113) · [Reserve before append](https://github.com/rock-solid-sites/ASES/blob/0bd51a34700164a5eb77efe98158fa37d1a74e23/docs/research/phase-ii-native-ownership/native_sink.py#L120-L139)

If the failure contract requires exact preservation of authoritatively selected pending obligations, the second history requires recognizing a pending B. The first need not retain B as pending. The difference matters because the native protected disposition checks use the set of selected effects, and PR #98 also refuses fresh requests while some effect is pending. Conversely, treating every unselected record as authoritative can invent obligations, misreport completed selection, or falsely block all progress. This is the prepared-cut ambiguity at an actual owner seam, with no alternative F4 publication order needed. It does not establish that a particular implementation has to preserve an eventless reservation after all possible failures. A rule allowing abandonment would need its own proof that no escaped capability or late effect still depends on that reservation. [Selected effect predicate](https://github.com/rock-solid-sites/ASES/blob/0bd51a34700164a5eb77efe98158fa37d1a74e23/docs/research/phase-ii-native-ownership/native_owner.py#L290-L313) · [Later admission bound](https://github.com/rock-solid-sites/ASES/blob/2358354c86a2b15e6ddbe81480d4c783a46e5a56/docs/research/phase-ii-native-pending-admission/IMPLEMENTATION-REPORT.md)

## A monotone historical projection

Let a recovery observer trust an append prefix bound to one persistent domain and specific sink. Assume a live or recovered publication witness authenticates that complete prefix, and the journal's append path was fully mediated. For an event in the prefix the observer can expose an immutable historical fact containing domain, request identity, exact payload identity, event position and accepted authority incarnation. Because the witness checks actual prefix bytes and the source supplies identity uniqueness, a repeated proof refers to the same attributed fact. The reply remains valid after replacement. The [native retry observer](https://github.com/rock-solid-sites/ASES/blob/0bd51a34700164a5eb77efe98158fa37d1a74e23/docs/research/phase-i-effect-retry/candidate.py#L57-L106) implements the narrow historical observation within its current projection. The R2 result gives native evidence for that separation.

Under these premises a separate historical index can safely accept facts that were positively proved, including facts absent from an older selected image. If the index is an observation-only projection, restoring one such fact does not change any authority to append, select, revoke, dispose or reclaim. Its state can grow with additional complete proofs. It must surface conflicts in domain, identity or exact data, and avoid a definitive absent answer when completeness for the queried window is unknown. The appender's actual policy and outcome still require proofs at their respective authority boundaries.

This suggests a smaller architecture direction than rebuilding owner state on every retry. First recover or expose history without promoting it to current authority. Then re-establish prospective admission and disposition only from a recovered, current authority cut with complete live obligations and custody. The division can be expressed through separate reply fields, typed records in one protected store, or a mediated view. Physical separation is optional. If the same repaired field both conveys history and releases outstanding dependencies, then the simple monotonicity argument no longer applies. A successful result from a historical receipt cannot stand in for authorization to take that second action.

**Frontier.** Reuse the R1 repair for a selected local record and R2 for the narrower historical observation. A repair that reconstructs an observational index can be qualified separately from recovery of fresh execution authority. The source-based lower bound rules out scanning immutable records and accepting their highest number as a proof of selection. Recovery of current owner decisions needs either surviving selection evidence or an explicit reconciliation contract that handles eventless obligations and stops old admission and release before any new authority is exposed. The choice is still a design question. No new runtime trial follows from this argument.
