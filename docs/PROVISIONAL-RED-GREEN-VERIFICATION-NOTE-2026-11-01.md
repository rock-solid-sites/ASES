# Provisional ASES methodology note: red–green verification

**Status: PROVISIONAL — for future methodology discussion, not a final global rule.**

The resource-solver research exposed a verification gap: passing regression and negative-input tests were sometimes reported without evidence that the tests would fail on the unfixed implementation.

Proposal for discussion: require a recorded **RED → GREEN → REFACTOR → MUTATION** sequence for correctness changes. A valid test should fail for the intended behavioral reason before the fix, pass after it, and fail again when the original defect is reintroduced in isolation. Pair rejection tests with valid neighboring cases to prevent reject-everything implementations. Capture commands, revisions, failure evidence, and remaining coverage gaps.

**Scope today:** apply this protocol to the resource-solver / allowance-admission research. Do not retroactively label earlier tests as red–green verified solely because they currently pass. Historical fixes may be audited using retrospective mutation tests, clearly distinguished from original red-before-green evidence.

Detailed project record: [Resource Solver Red Green Mutation Verification 2026-11-01](research/Resource%20Solver%20Red%20Green%20Mutation%20Verification%202026-11-01.md).

**Open questions for later:** which changes require mutation testing, whether CI should enforce mutation score thresholds, how to handle tests of probabilistic algorithms, and what evidence is sufficient for an independent reviewer.
