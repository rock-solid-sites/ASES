# Initial harness assumptions falsified, not product failure

Executed sourcefb6a80e. Actual5 histories completed and raw retained. Checker failed:
it expected literal `zero`, whereas actual accepted bytes are `accepted\0zero\n`;
it also assumed establishment left content absent. Original core candidate explicitly
establishes with accepted zero content. Raw bootstrap ACKs already expose that fact.
Thus prepared-before-COMMIT correctly recovered prior content, not nonexistent state.
This is a coordinator harness/setup error, not holder loss or a product defect. Preserve
attempt1 raw/check stderr and source revision, do not call it a passing test.

Corrected preregistration before next behavior run: bootstrap establishes/grants with
an accepted BOOTSTRAP observation bundle in the same SQLite transaction. Tested accept
uses different one bytes. Atomic prepared cut must retain previous ACKed zero plus
BOOTSTRAP bundle, not erase it. Atomic post-COMMIT A/B retain new one plus respective
required tuple. Split post-COMMIT retains new one with stale zero/BOOTSTRAP bundle;
consumer explicitly reports incompatible observations/unknown required tuple, instead
of treating previous evidence as current. Split uninterrupted control installs correct
new tuple then ACKs. Read-only checker compares actual explicit request bytes and
prior trusted ACK observations, not guessed content labels. This is a stronger prior-
ACK retention control and a torn metadata-binding counterexample, not schema adoption.
Recovery still receives no original tuple. Other original limits remain; no authenticity
or C11/F1 closure. Original source is exactly inspectable atfb6a80e.
