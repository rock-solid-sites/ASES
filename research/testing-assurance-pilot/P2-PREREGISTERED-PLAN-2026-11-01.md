---
title: EDASES Assurance Pilot P2 — Trip'n Monitor, Instrument Sensitivity and Evidence
program: EDASES
layer: Research
document_type: Preregistered Experiment Plan
status: Frozen Before New P2 Test Execution
authority: Experimental
canonical_repository: ases
date_frozen: 2026-11-01
source_substrate: TripN-Chill-Zone/tripn-astro (private)
---
# P2 — Trip'n production-invariant monitor assurance pilot

This plan is frozen before **new** synthetic-source mutations or CI checks. Historical evidence identified during discovery is explicitly **retrospective**, not an outcome predicted in ignorance of the past. ASES Testing and Assurance Method remains DRAFT; no policy promotion or production change is authorized by this experiment.

## Object, boundaries and existing observed context

- Existing private GitHub repo: `TripN-Chill-Zone/tripn-astro`, production branch `master`.
- Target: `.github/workflows/production-invariant-check.yml` and `scripts/check-production-invariants.mjs` at `974d8224ac5376720793d9ead57b08b061573312`.
- Workflow is read-only for its DNS/HTTPS probes but **writes issues** when simulated/real failures are seen; do NOT dispatch or rerun the existing workflow just to test the method. Production-facing requests and alert side effects are out of scope.
- Retrospective inventory: 195 recorded workflow executions since 2026-09-24. 188 success and 7 failure: 1 intentional synthetic alert test, 5 instances of Pages comparison hostname DNS status 2 (with apex checks passing), 1 single-request HTTPS timeout (with other checks passing). These classes were observed before this plan; they are not forward predictions or proof that the site never failed.
- Historic last inspected successful run: `41325554309` (2026-11-01T16:17:22Z, 6/6 live checks and 6/6 self-test fixtures). No workflow run artifact was listed in GitHub Actions for that run.
- Relevant historical run IDs: 36019429914 (synthetic), 38879127430, 39650858614, 40681057745, 40734859136, 40949737192, 40978536537.
- No real booking, payment, Cloudflare DNS write, incident issue write, or production deployment will occur in P2.

## Attributable claims and questions

- **T1 — Observable failed site fingerprint:** `checkSiteResponse` rejects a Cloudflare-looking HTTP 200 response that has a nominal valid site marker but **also contains** the forbidden `website has been stopped` marker. A neighboring normal Cloudflare-looking response with the valid site marker must pass. This claim is derived from the detector's existing `FORBIDDEN_BODY_MARKERS` logic; it is not an invented new site requirement.
- **T2 — Instrument sensitivity:** the legacy six-case `--self-test` is expected to reject a fixture with a LiteSpeed server and stopped page; the question is whether that check **actually exercises the forbidden marker guard**, rather than rejecting due to an unrelated server/header/required-marker check.
- **T3 — DNS Cloudflare provenance:** if the Cloudflare ranges endpoint is unavailable, `checkDnsAnswers` may accept an otherwise unknown, nonobsolete address. This is a proposed **evidence-boundary finding**, not an approved fail-closed requirement or automatic product bug.
- **T4 — Preserve heterogeneous outcomes:** historical scheduled checks must be classified by individual observable failure, not merely workflow success/failure. An error resolving the alternate comparison hostname is **not automatically an apex outage**.
- **T5 — Archive independence:** a GitHub run with no archived artifacts cannot meet the proposed complete external-retention requirement merely because GitHub retains log URLs. Distinguish extracted evidence copies from complete raw-archive copies.
- **T6 — Reviewer reconstruction:** ask whether a fresh reviewer can reconstruct T1–T5 from frozen records, exact revisions and raw output without relying on the author's interpretation. No independent person/model is enlisted yet; report NOT_DONE rather than simulated independence.

## Prospective falsifiers, controls and lowest-cost method

**No production-facing checks will be triggered.** Use a one-off GitHub Actions workflow in a non-default `research/ases-assurance-p2-2026-11-01` branch. Run Node's local `checkSiteResponse` and `checkDnsAnswers` functions against synthetic fixtures. The test harness explicitly injects `--self-test` into the imported module's arguments to prevent its otherwise automatic `runLiveChecks` path.

- Baseline valid fixture: 200, `server: cloudflare`, `cf-ray: test`, body contains `Hostels in Tirana` and none of the forbidden strings: expect pass.
- Baseline violating fixture: same headers/status and required site marker, but body also contains `website has been stopped`: expect reject for **forbidden marker**, not for another missing requirement.
- Targeted mutant: in an ephemeral copy, change the single `const forbidden = FORBIDDEN_BODY_MARKERS.find(...)` expression to `const forbidden = undefined;`. No code is written back to `master`.
- Predicted discriminatory outcome: **legacy six self-tests still pass the mutant** (so the old test is insensitive to this guard), while the new neighboring positive/negative control passes baseline but catches mutant acceptance of the violating fixture. Report divergence rather than upgrading all tests to a global policy.
- DNS boundaries: external address outside specified Cloudflare ranges (e.g. documentation-only `203.0.113.7`) is rejected when ranges supplied. With ranges absent, inspect whether same address is accepted; do not require a fail-closed verdict because no authorized guarantee has yet specified it.
- Capture compiler/runtime versions, source SHA, before-run plan SHA when possible, exact fixture outcomes, mutation replacement and stdout, suite runtime and artifact bytes.
- No broader mutation campaign, network probe or full-suite rewrite is justified for this discriminator.

**Falsifiers:** baseline fails valid case; baseline accepts the mixed forbidden response; mutant is already caught by the old self-test; new targeted test fails valid neighbor or misses the mutant; fixture cannot be executed without network; runner/checkout inaccessible; evidence not retrievable. Classify infrastructure failures as ERROR or BLOCKED, not detection RED.

## Interpretation, retention and stop criteria

- Retrospective history supports a decomposition of 7 failures; not a prediction or measured uptime.
- GitHub's historical workflow run records include run, job and log references; latest audited run has zero artifacts. External archive is **NOT_VERIFIED**.
- Only record P2 experiment as PASS after CI genuinely completes and both positive/negative controls meet expected outcomes. Save machine-readable test outputs and a hash/metadata index outside the native provider, without copying private Trip'n source or secrets into the public ASES repository.
- If GitHub connector cannot execute new CI safely, stop at historical evidence analysis; do not dispatch production action.
- Methodological adoption remains **DEFER** until independent reviewer exercise, complete retention export and substantive second-substrate results.
