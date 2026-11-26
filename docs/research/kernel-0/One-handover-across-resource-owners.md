---
title: Can resource owners witness one Attachment Point handover?
version: 0.1.0
program: ASES
layer: Research
document_type: Experimental Result
status: Experimental
authority: Derived
canonical_repository: ases
last_updated: 2026-11-26
---

# Can resource owners witness one Attachment Point handover?

Suppose a continuing Work Unit W exposes two independently protected resources through the same Attachment Point P. X can append to either until one replacement R hands P to Y. If resource A returns a definitive stale-tenure denial to X and **after that reply** X initiates a fresh append at resource B which succeeds, R must precede the first decision and follow the second. Each resource can exhibit a legal local handover. Together they contradict the single handover promised to W. Both calls can occur entirely during R. Waiting for both resources before acknowledging R does not repair the observed history.

This is a counterexample for a particular consumer contract. Both writes are otherwise admissible. A stale-tenure reply asserts that X's tenure ended. If A may return an uninformative busy result while X remains current, that reply supplies no such evidence. Neither the neutral requirements nor the three primitive names settle which reply an implementation promises. An experiment that only compares the final contents, or only sends probes after R returns, misses the distinction.

## A finite witness for a shared decision

Fix one completed replacement and a finite history of completed, fresh single-resource calls. Record invocation and response as distinct ordered events; a sequential test client suffices to establish the crucial real-time edge. Accepting X requires a decision before R. Rejecting X for stale tenure requires a decision after R. Accepting the successor also requires a decision after R. Ignore transient busy attempts only under a contract allowing them as no-effect steps in either phase. All other data, rights and policy conditions are held fixed.

For each old-phase decision take its invocation. For each new-phase decision take its response. Let L be the latest of the old invocations and R's invocation. Let U be the earliest of the new responses and R's response. There is a common decision instant exactly when L < U, provided each resource's local history already realizes the stipulated before/after order and its content observations. Work in gaps between endpoint events. Necessity follows by putting the instant inside R, after every old invocation and before every new response. For sufficiency, put it in the open interval (L,U). At each resource use its legal local operation order. Its old-phase prefix fits before the cut and its new-phase suffix fits after it. For a finite ordered list of calls with intervals, instants can be assigned in order arbitrarily close after the running maximum of their invocations. Local feasibility ensures this maximum is below each response. Apply this construction to each prefix and suffix with the chosen cut as the extra upper or lower bound. Merge the local schedules by assigned instant. Real-time precedence is preserved, and any equal instants on independent resources can be separated in the same gap.

A failed intersection has two extremal witnesses, possibly one boundary of R. Once local adequacy holds, at most two resource observations plus R refute the common cut, however many resources or calls the history contains. This is a witness-size bound on recorded histories. A faulty program can wait for its thousandth resource to join before producing the first such history. Testing a two-resource deployment gives no program-size cutoff.
