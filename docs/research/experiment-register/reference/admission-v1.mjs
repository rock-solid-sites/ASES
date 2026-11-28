// Draft research reference, not a deployed authorization boundary.
export function evaluateAdmission(plan, control) {
  // Experimental pure reference predicate. All control facts are supplied by the
  // trusted controller AFTER verification. This function is not a dispatcher,
  // authenticator, content-hash verifier, reservation store, or scientific oracle.
  const block = (reason) => ({status:"BLOCK", reason});
  const obj = x => x !== null && typeof x === "object" && !Array.isArray(x);
  const str = x => typeof x === "string" && x.trim().length > 0;
  const digest = x => typeof x === "string" && /^[a-f0-9]{64}$/.test(x);
  const keys = ["runs","wall_seconds","model_requests","completion_tokens","cash_microusd"];
  const limit = x => obj(x) && Object.keys(x).length === keys.length &&
    keys.every(k => Object.hasOwn(x,k) && Number.isSafeInteger(x[k]) && x[k] >= 0);
  const fits = (a,b) => keys.every(k => a[k] <= b[k]);
  const actions = {ACCEPT:"ADMIT",REDUCE:"REVISE",REUSE:"USE_EVIDENCE",
    IMPLEMENT:"TRANSFER",DEFER:"DEFER",REJECT:"CLOSE"};
  if (!obj(plan) || !obj(control) ||
      !["experiment_id","decision_id","parent","objective","prior_search",
        "uncertainty","least_method","scope","stop","evidence_home"].every(k=>str(plan[k])) ||
      !["DECISION","EXPLORATORY"].includes(plan.kind) ||
      !Array.isArray(plan.evidence) || !plan.evidence.every(str) ||
      !obj(plan.outcomes) || !["positive","negative","inconclusive"].every(k=>str(plan.outcomes[k])) ||
      plan.outcomes.positive.trim() === plan.outcomes.negative.trim() ||
      !limit(plan.limits) || plan.limits.runs < 1 || plan.limits.wall_seconds < 1 ||
      (plan.limits.model_requests === 0) !== (plan.limits.completion_tokens === 0)) {
    return block("INVALID_REGISTRATION");
  }
  // revision is the SHA-256 of the exact frozen plan bytes, NOT a digest
  // asserted by the plan. Adapter must parse those verified bytes only.
  const rev = control.verified_revision;
  if (!digest(rev) || rev !== control.active_revision ||
      control.experiment_id !== plan.experiment_id ||
      control.decision_id !== plan.decision_id || control.parent !== plan.parent) {
    return block("IDENTITY_OR_REVISION_MISMATCH");
  }
  if (control.state !== "OPEN") return block("DECISION_OR_EXPERIMENT_NOT_OPEN");
  if (control.stop_reached !== false) return block("STOP_REACHED_OR_UNKNOWN");
  const q = control.qualification;
  if (!obj(q) || q.revision !== rev || !str(q.receipt) ||
      !["READY","REUSE","IMPLEMENT","BLOCKED"].includes(q.status)) {
    return block("QUALIFICATION_MISSING_OR_STALE");
  }
  if (q.status !== "READY") return block("QUALIFICATION_" + q.status);
  const policy = control.review_policy;
  if (!obj(policy) || policy.revision !== rev ||
      typeof policy.required !== "boolean" || !str(policy.reason) || !str(policy.receipt)) {
    return block("REVIEW_POLICY_UNKNOWN");
  }
  const auth = control.authority;
  if (!obj(auth) || auth.revision !== rev || auth.experiment_id !== plan.experiment_id ||
      auth.decision_id !== plan.decision_id || auth.status !== "AUTHORIZED" ||
      !["NORMAL","MANUAL_REVIEW_EXCEPTION"].includes(auth.mode) || !str(auth.receipt) ||
      (auth.mode === "MANUAL_REVIEW_EXCEPTION" && !str(auth.reason))) {
    return block("AUTHORITY_MISSING_OR_STALE");
  }
  let reviewReason = policy.required ? "REVIEW_MISSING" : null;
  const review = control.review;
  if (review !== null && review !== undefined) {
    // A stale/malformed attempted review is not silently ignored.
    if (!obj(review) || review.revision !== rev || !str(review.receipt) ||
        !["COMPLETE","INCOMPLETE","FAILED"].includes(review.status)) {
      return block("REVIEW_RECORD_INVALID_OR_STALE");
    }
    // A COMPLETE review must have a string verdict before coercive key lookup or waiver logic.
    if (review.status === "COMPLETE" && typeof review.verdict !== "string") {
      return block("REVIEW_RECORD_INVALID_OR_STALE");
    }
    if (review.status !== "COMPLETE") reviewReason = "REVIEW_INCOMPLETE";
    else if (review.independent !== true) reviewReason = "REVIEW_INDEPENDENCE_UNVERIFIED";
    else if (!Object.hasOwn(actions,review.verdict) ||
             review.action !== actions[review.verdict] || review.meaning_checked !== true) {
      reviewReason = "REVIEW_ACTION_CONFLICT_OR_UNCHECKED";
    } else if (review.verdict !== "ACCEPT") reviewReason = "REVIEW_" + review.verdict;
    else reviewReason = null;
  }
  if (reviewReason && auth.mode !== "MANUAL_REVIEW_EXCEPTION") return block(reviewReason);
  const dispatch = control.dispatch;
  if (!obj(dispatch) || !str(dispatch.id) || dispatch.revision !== rev ||
      dispatch.claim_state !== "UNCLAIMED" || !str(dispatch.ledger_receipt)) {
    return block("DISPATCH_ALREADY_CLAIMED_OR_UNVERIFIED");
  }
  if (!limit(dispatch.request) || !limit(dispatch.remaining) ||
      dispatch.request.runs < 1 || dispatch.request.wall_seconds < 1 ||
      (dispatch.request.model_requests === 0) !== (dispatch.request.completion_tokens === 0) ||
      !fits(dispatch.remaining,plan.limits) || !fits(dispatch.request,dispatch.remaining)) {
    return block("ENVELOPE_EXCEEDED_OR_UNKNOWN");
  }
  return {status:"ELIGIBLE_FOR_ATOMIC_CLAIM", revision:rev,
    experiment_id:plan.experiment_id, decision_id:plan.decision_id,
    dispatch_id:dispatch.id, request:{...dispatch.request},
    review_disposition:reviewReason ? "MANUAL_EXCEPTION:"+reviewReason :
      review ? "ACCEPT" : "NOT_REQUIRED"};
}
