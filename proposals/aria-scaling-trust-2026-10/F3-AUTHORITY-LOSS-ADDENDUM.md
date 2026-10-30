# F3 authority-loss milestone — grant evidence update (October 30, 2026)

Source: https://github.com/rock-solid-sites/ASES/blob/04600b1b45e6510665bdc3108db9d51f6b2f8c56/research/phase-i-protected-work-unit-f3/authority-loss/REPORT.md

**Verified within the declared host-test profile:** A confined worker read a sentinel through its authorized mediator, the combined authority-holder/mediator process was terminated and observed to exit, and the worker continued 392,488 counted CPU iterations. A subsequent request through the retained socket received no protected bytes; a direct file read, symlink read, and no-op write-open were denied. A deliberately weakened configuration where a surviving mediator retained cached authorization returned the protected bytes, and the detector flagged that failure. The independent Luna verifier reportedly reproduced the selected test; this is not a clean-room cross-family F5 review.

**Limits:** One worker, one holder/mediator, selected local file attachment, specified host and Landlock rules. Arbitrary alternate routes, descriptor passing, descendants, network and external sink effects, directory mutation behavior, accepted-byte storage and recovery, partial access-control updates, hostile peers and full Work Unit lifecycle were not demonstrated. The formal F2 T05 case remains prepared-only pending independent host-fixture integration.

**Grant implication:** This is meaningful evidence of rapid incremental progress on a hard boundary question using constrained compute and model budgets. It supports an ambitious early prototype goal; it does not establish a reusable deployment-ready security substrate or justify an extrapolated timeline from short commit bursts. Recalibrate the proposed work plan from the existing research, and put the funded year toward further assurance, portability and unresolved research.

**Applicant identity:** Independent individual PI, new and not-yet-selected research identity; unrelated business excluded. Temporary coding/research agents are tools, not team members.
