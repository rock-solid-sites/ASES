# HMS chat — testing/debugging proposal application (2026-11-02)

**Status:** Cross-conversation report for comparison, not a handoff, ASES policy change or proof of benchmark validation.

The HMS prototype discussion reviewed all seven files in this proposal bundle and adopted a **project-local pilot** in [HMS Prototype Testing and Debugging Process](https://github.com/rock-solid-sites/HMS/blob/prototype/minimum-operational-slice-20261101/docs/HMS-PROTOTYPE-TESTING-AND-DEBUGGING-PROCESS-2026-11-02.md). Its integration suite now links to that process. The ASES proposal documents remain experimental; no new ASES-wide gate or automatic specialist-review requirement was authorized.

## Useful ideas integrated into HMS
- **Claim-first, cheapest discriminating evidence:** identify the actual acceptance surface, competing explanations, pre-run predictions and the smallest experiment that changes a decision. Reuse existing evidence before new infrastructure.
- **Qualified checks, not green-check substitution:** valid and invalid neighboring controls, independent oracle where feasible, targeted mutation for important guards, and explicit distinctions among execution outcome, evidential sufficiency and authorized acceptance.
- **Fault-boundary isolation:** distinguish Codex environment, package install, GitHub workflow trigger/run/test, Cloudflare deployment/browser, Beds24 response/normalization/mapping, projection and rendered user interaction. An upstream success is not downstream acceptance.
- **Reasoning and CI evidence preservation:** preserve predictions, raw outcomes, negative/null results, revision, runner, artifacts and archive completeness. GitHub native retention is not the durable archive; provider and schema remain to be validated.
- **HMS conceptual distinctions:** Beds24 room type versus physical room versus bed; reservation versus assignment; provider payment status versus HMS guest ledger; staff availability versus shift. The two calendars may share timeline rendering but not allocation/overlap rules.
- **No unnecessary phases:** the three-view HMS prototype retains its existing G0–G7 build sequence, with each gate made evidence-producing rather than adding another development lifecycle. Proposed ontology design and conformance roles are selective, not mandatory or asserted to be deployed.

## Concrete pilot
G0 starts with the smallest strict TypeScript/Astro scaffold, one accepted and one rejected reservation fixture, a local run and a GitHub Actions run, with exact commands, revision and preserved results. Subsequent gates test domain contracts, a shared staffing/property timeline, guest financial table, three-view browser workflow, deployed preview, read-only Beds24 mapping, and staff workflow parity. A fixture test cannot claim live provider booking/payment settlement; a build cannot claim deployed browser acceptance.

## Limits and feedback
This is **documentation adoption only**: no executed G0 test, no verified independent reviewer, no empirical evidence that the proposed method improves diagnosis yet. The pilot should measure hypotheses eliminated per probe, false conclusions avoided, cost/time, test sensitivity, retention completeness and handoff usefulness. Avoid universal mutation thresholds, mandatory stress, large reviewer panels or a fixed storage vendor without evidence.

**Placement:** Saved on ASES `main` alongside the proposal folder as a report for future reconciliation. The proposal bundle itself remains on its proposal branch and is not promoted by this note.
