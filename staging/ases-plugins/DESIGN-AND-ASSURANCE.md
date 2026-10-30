# End-to-end plugin design and assurance

## Requirement: prove the whole path

A successful artifact build is not a successful plugin. Begin each bounded change with an observable user outcome, then trace backwards through the mechanisms that must exist to realize it. For each boundary record: required property; mechanism/owner; evidence that the mechanism exists; evidence it works in the exact client; missing or externally controlled assumptions; smallest counterexample; acceptance test. Classify as VERIFIED, PRESENT-UNVERIFIED, MISSING, EXTERNAL-UNRESOLVED or NOT APPLICABLE. Do not freeze a design with an unexplained mandatory transition.

## ChatGPT skills/plugin lifecycle

User request → client eligibility/activation → discovery → selection → skill instructions loaded → instructions applied → user-visible conforming output.

A manually loadable skill proves only loading capability. An installed plugin proves only availability. A dispatcher instruction does not itself ensure dispatcher selection. The installed ASES Workflow v0.1.0 missed automatic invocation despite accessible skill files. Its generic metadata, empty keywords and dispatcher dependency are hypotheses to test, **not a confirmed root cause**. The repair must demonstrate fresh-chat invocation with the original failed prompt, ordinary paraphrases, unrelated task types and negative controls. If platform discovery cannot be made sufficiently reliable, report the limitation and investigate an explicit invocation mechanism rather than claiming automatic behavior.

## MCP lifecycle

Requested ChatGPT operation → compatible client/product → connector registered → active → transport reachable → authenticated/authorized → tool schema discovered → genuine ChatGPT-originated invocation → backend effect observed → domain-level acceptance and security preserved.

For each stage use PASS, FAIL, BLOCKED or NOT TESTED, with redacted evidence and the cheapest next discriminating test. Backend CLI success, Connected labels, tool listing and HTTP 200 are not end-to-end proof. Check the exact target client separately when web/desktop/mobile behavior differs. Correlate request IDs with backend logs where appropriate. Distinguish 401/403, transport, registration, unsupported client capability and discovery failures.

## State-model applicability

Apply the canonical State-Model Applicability and Reuse Method at behavior specification time. The plugin installation/activation/version lifecycle and release gating are PRIMARY candidates. Discovery/selection and MCP authentication/connection lifecycles may be SUPPLEMENTARY where externally controlled. Prompt content generation need not be a state machine. Specify guards, forbidden traces, ordering, recovery, authoritative versus observed state and actual resource settlement only where they improve precision or testing. Reject state-model machinery that adds no material guarantee.

## Realization and reuse

Apply the canonical Constraint-Driven Realization and Assurance Selection Method: first establish falsifiable safety/correctness/performance constraints and evidence, then search without preselecting technology. Reuse known working connector routes, plugin package formats, test harnesses and canonical skills; do not copy obsolete deployments or inherit entire architectures. A source-of-truth migration requires a single explicit authority decision, provenance and regression evidence.

## Verification architecture

Create initially failing tests for required but absent transitions. Use staged protocol/unit tests and real client end-to-end tests; preserve test fixtures and execution evidence. Release gates should fail closed when critical client tests cannot run, while distinguishing BLOCKED from FAIL. Manual acceptance observations must be recorded with exact client, request, expected/actual selection and output, time and release version. Test not only the happy path but forbidden success claims and security regressions.

A release is ACCEPTED only if the exact claimed behavior is demonstrated at its required boundary. If the client platform does not expose reliable invocation telemetry, state the evidence limit and rely on repeatable observable behavior without pretending certainty about internal selection.

## Canonical methodology references

- `rock-solid-sites/ASES/docs/methodology/ASES Bounded Project Build Method.md`
- `rock-solid-sites/ASES/docs/methodology/State-Model Applicability and Reuse Method.md`
- `rock-solid-sites/ASES/docs/methodology/Implementation Realization and Assurance Selection Method.md`
- `rock-solid-sites/ASES/skills/custom-mcp-connector/SKILL.md`
- `rock-solid-sites/ASES/skills/prompt/SKILL.md`

These are references, not copies. The monorepo should not silently redefine them.
