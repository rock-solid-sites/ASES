# SR-YYYY-MM-DD-target-name — Selection Rationale Template

<!--
This is the canonical template for `selection-rationale/*.md` files in
the ASES project. Copy this file to the new location, then fill in the
fields below.

Filename convention: YYYY-MM-DD-target-name.md (date-slug, no sequential
SR-NNN integers; sequential integers race in multi-agent systems).

Status field values:
- Live: captured at decision time. All 8 standard fields are required.
- Reconstructed: captured after the fact. Date of decision and Evidence
  expected to validate are nullable; Date Reconstructed is required.

The linter (scripts/validate_evaluation.py, M-003 extension forthcoming)
will validate that:
- All 8 standard fields are present (or N/A - Reconstructed where allowed)
- Status is one of {Live, Reconstructed}
- Reconstructed entries explicitly call out the gap
- Rationale has a minimum length (currently 200 chars; configurable)
- Alternatives considered is non-empty

The field separators below (## Metadata, ## Rationale, etc.) are
conventional, not enforced. The linter parses the field names, not
the section structure.
-->

## Metadata

- **ID:** SR-YYYY-MM-DD-<short-target-slug>  *(matches the filename slug)*
- **Date of decision:** YYYY-MM-DD  *(or N/A — Reconstructed)*
- **Date Reconstructed:** *(Required for Reconstructed; omit for Live. Format: YYYY-MM-DD.)*
- **Decider:** <human user / agent ID>
- **Selection:** <what was chosen; should match the related Crosslink issue title>
- **Status:** Live | Reconstructed
- **Crosslink issue:** #N  *(parent issue, if applicable; e.g. the Track B epic)*

## Rationale

3–10 sentences. Freeform. Should answer: why this target/approach, what
alternatives were considered, and what does this selection enable that
alternatives do not. Each distinct factor should be identifiable as a
separate paragraph or sub-bullet for retrieval purposes.

For Live entries, this should be written before the work begins, not
after. The Reason field exists precisely to force the reasoning into the
record at the moment of decision.

## Alternatives considered

At least 1 alternative. For each: what was considered, why it was
rejected, and what would have to be true for the alternative to become
the preferred choice later. Bullet list:

- **<Alternative A>** — rejected because <reason>. Would be preferred if <condition>.
- **<Alternative B>** — rejected because <reason>. Would be preferred if <condition>.

## Evidence expected to validate

What observations would prove the choice was right? What observations
would have falsified it? This is the falsifiability check: a selection
that cannot be falsified by any observation is not a selection, it's
a preference.

- **Supports the choice if:** <observation 1>, <observation 2>, ...
- **Falsifies the choice if:** <observation 1>, <observation 2>, ...

For Reconstructed entries, both sections may be `N/A — Reconstructed`
with an explicit note explaining what is missing and why (e.g.,
"selection was made in a context whose record was not preserved").

## Cross-references

- `<path/to/related/doc.md>` — what is this and why is it relevant
- ...

## Why this entry exists (Live only; omit for Reconstructed)

A short statement of the live context in which the decision was made.
E.g., "Captured during the planning session for Track B Turn 2, before
any verification work was dispatched."

---

## Worked example: Live entry

The following is a fictional example showing what a Live entry looks
like when filled in correctly. The companion actual entry (the AutoGen
backfill) is the precedent for Reconstructed entries.

### Metadata

- **ID:** SR-2026-07-15-codename-phoenix
- **Date of decision:** 2026-07-15
- **Decider:** <human user>
- **Selection:** Codename "Phoenix" as the first production deployment target for the hospitality suite
- **Status:** Live
- **Crosslink issue:** #42

### Rationale

The Phoenix property is the smallest production deployment and has the
most direct line to the original HMS specification. It exercises the
full stack (booking, payments, housekeeping, reporting) end-to-end,
which means any architectural choices made will be tested against a
real workload rather than a synthetic one. The team has a direct
relationship with the property manager, which shortens the feedback
loop on UX issues.

### Alternatives considered

- **Driftwood Bay Resort** — has a more complex payment setup (multi-currency) that would slow initial deployment. Would be preferred as a second target once the Phoenix integration is stable.
- **The Larkspur Inn** — small enough that even Phoenix's complexity would be over-engineered; would not exercise the architectural surface needed to validate the framework.

### Evidence expected to validate

- Supports the choice if: end-to-end deployment completes within 4 weeks, payments flow works against the production gateway, the property manager reports the UX is usable without major revisions.
- Falsifies the choice if: deployment takes >8 weeks, the payment integration requires fundamental architectural changes, or the property manager's feedback indicates the framework is over-engineered for the use case.

### Cross-references

- `specifications/Hospitality Management Suite Specification.md` — the specification being deployed
- `charters/Phoenix Deployment Charter v1.md` — the operational charter for this deployment

---

## Linter expectations (M-003 forthcoming)

The Tier 1 linter (`scripts/validate_evaluation.py`) will be extended
to validate `selection-rationale/*.md` files with the following checks:

- **SR-1:** All 8 standard fields present (or `N/A — Reconstructed` for the 2 nullable ones when `Status` is `Reconstructed`)
- **SR-2:** `Status` is one of `Live` or `Reconstructed`
- **SR-3:** `Reconstructed` entries must include a `Date Reconstructed` field
- **SR-4:** `Rationale` minimum length: 200 chars
- **SR-5:** `Alternatives considered` is non-empty
- **SR-6:** Reconstructed entries must include an explicit gap callout (e.g., the phrase "no live record" or "Reconstructed from indirect evidence")

The linter will be warning-grade by default (matching the existing
harness-evaluations checks). Use `--strict` for CI enforcement.
