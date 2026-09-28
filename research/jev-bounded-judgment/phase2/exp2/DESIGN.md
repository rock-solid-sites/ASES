# Experiment 2 — shared-state multi-question economics (design, not yet executed)

**Status:** design only. Experiment 1 must be independently verified before this
begins, per the execution contract.

## Question

**Does shared-state evaluation reduce tokens, cost, or latency without
materially changing the judgments?**

## Arms

| arm | requests | content |
|---|---|---|
| **S** separate | one per case | that case's single question over that case's frozen state |
| **B** batched | one per shared-state group | the same questions, unchanged, in one request over the shared state |

Question meanings, criteria, model version and state are matched. The only
difference is how many requests carry the same state text.

## Case selection

Cases are grouped by the frozen state they consume. In Phase 2 the state is the
whole module source, so every case from one module legitimately shares one
state. Grouping is by `module`, which is a property of the frozen case set, not
a choice made after seeing results.

**No question may be batched if its answer is needed to construct a later
question.** Phase 2's cases are independent single judgments over one state, so
none has that dependency. This is asserted mechanically, not assumed: the
builder fails if any case's question text references another case's id.

## Measures

Answer/distribution equivalence, input usage, cost, end-to-end latency and tail,
failures, throughput. Matched question sets and matched denominators throughout;
the cost/token consistency check is retained.

## Stop condition

Frozen, executed, reproducible from committed material, independently verified.
