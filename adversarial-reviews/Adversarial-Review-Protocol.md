# Adversarial Review Protocol

Every phase of the project requires strict verification before signoff. This includes a three-stage review process:
1. **Builder Review:** The original implementer verifying that the code meets the specification.
2. **Verifier Review:** An independent validation of the implementation's functionality and logic.
3. **Adversarial Review:** An active attempt to break, subvert, or corrupt the system using the checklist below.

## Adversarial Review Checklist

### Interface Contract Attacks
- [ ] nil returns
- [ ] malformed returns
- [ ] partial returns
- [ ] unexpected enums

### Data Quality Attacks
- [ ] whitespace
- [ ] empty strings
- [ ] invalid Unicode
- [ ] duplicate IDs

### Network Attacks
- [ ] timeout
- [ ] retry
- [ ] rate limit
- [ ] transient outage

### State Attacks
- [ ] duplicate execution
- [ ] interrupted execution
- [ ] partial writes
- [ ] stale state

### Migration Attacks
- [ ] old schema versions
- [ ] missing fields
- [ ] forward compatibility

### Scale Attacks
- [ ] 10× expected volume
- [ ] 100× expected volume

### Operational Attacks
- [ ] missing secrets
- [ ] revoked credentials
- [ ] disabled APIs

## Project Insights: Most Likely Failing Assumptions in Production

During an adversarial review of a system integrating with multiple external data sources (such as Museum APIs), the most critical and likely assumption to fail in production is:

**Assumption: "Third-party APIs will honor their data schemas, rate limits, and availability guarantees."**

Why this fails:
* **Contract Violations:** APIs frequently alter their JSON shapes without versioning (e.g., suddenly returning a single object where an array was expected, or returning `null` for fields previously guaranteed to be strings).
* **Silent Rate Limiting:** Instead of returning standard HTTP 429 Too Many Requests, upstream sources may drop TCP connections, hang requests indefinitely, or return generic 503s.
* **Corrupted Payloads:** Text fields (like `Artist` or `Title`) will inevitably contain embedded HTML, non-printable characters, encoded entities, or mismatched encodings that bypass simplistic `!= ""` checks.
* **Pagination & Seeding Bugs:** Functions expecting uniform random distributions via pagination or offset logic will break when museums change their underlying search index, limit max offsets, or deprecate deep pagination.

**Defensive Posture:** All external adapter boundaries must assume the data is actively malicious or deeply malformed. 
