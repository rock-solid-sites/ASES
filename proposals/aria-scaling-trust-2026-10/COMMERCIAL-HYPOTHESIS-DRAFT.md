# Commercial hypothesis — ARIA Scaling Trust / ASES
**Draft only. Confirm with ARIA's official commercial-hypothesis template and applicant-specific facts before upload.**

## Problem / payer
Organizations deploying agents to handle valuable digital tasks need reliable limits on delegated authority, timely revocation, exact mapping from approved policies to concrete effects, and evidence they can inspect or reproduce. Existing security policies and model instructions can diverge from real host authority (e.g. already-held descriptors); independently validating the entire agent stack is costly. This is the business/engineering need the funded component would test—not a claimed set of paying customers.

Potential users: open-source agent frameworks, enterprise AI infrastructure providers, safety teams at cloud/robotics companies, security testing organizations, and public-interest or UK-based research institutions. These are prospective categories, not verified customers or partners.

## Proposed value
A permissively licensed, reusable **authority-to-effect enforcement and conformance component** could reduce the cost of integrating agents with constrained resources and auditing whether revocation, process replacement and continuity claims really hold. The component would supply explicit effect contracts, narrow host adapters, positive and hostile conformance tests, machine-readable execution observations, and an honest trust-assumption/unsupported-route inventory.

## Differentiation
Focus on the often-overlooked gap between verified policy/protocol decisions and the actual file, service, credential or hardware effect. The approach joins a minimal current-state authority relation with live fail-closed enforcement tests and recoverable Work Unit evidence. It complements, rather than duplicates, security protocol design/negotiation and TEE sandbox products; comparative performance and TCB measurements remain to be collected.

## Adoption and sustainability hypothesis
The foreground core will be MIT and Apache-2.0 dual-licensed as required. Public reference tests and adapters lower integration barriers. Potential long-run revenue, without enclosing the core, could come from integration engineering, support, independently verified assessment services, and specialized deployments, but **none is currently validated**.

## Discriminating tests
- At least two independently developed agent harnesses can use the published interface without relying on private orchestrator state or vendor-specific model behavior.
- Measured engineering effort to integrate one supported protected attachment is documented; cost and latency compared against unprotected baseline.
- Adversarial test suites detect concrete bypasses and stale permissions; successful authorized work continues.
- External adopters reproduce the exact reference tests and identify at least one useful integration gap.
- Potential adopters provide direct feedback about whether the component solves a material operational problem and how they would support maintenance or integration.

## Commercial risks
- Teams may prefer a larger existing sandbox or security platform despite a smaller trusted boundary.
- The actual trustworthy host boundary might be too costly to engineer or prove across supported routes.
- Procurement and adoption may demand certifications/SLAs beyond the funded research period.
- Permissive licensing is essential to ARIA's goals, but does not itself guarantee maintainers, contributors or paid service demand.

## Near-term validation
Before any market sizing or revenue claim, conduct focused conversations with UK and international agent-security practitioners, supply public benchmark/test results, invite reproducible external runs, and measure implementation effort and threat-model mismatch. No invented TAM, sales pipeline, revenue or confirmed partnership.
