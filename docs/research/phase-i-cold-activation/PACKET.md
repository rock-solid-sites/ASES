# Cold activation and retained session — bounded F4 continuation slice

Frozen 2026-11-10. Original source: receipt F4 `9226cd4b`; parent #11 `1970abe2`.
Grounding: Phase-I-Closure §1.1/H2, §4/C6/C7/C12 and Verification T02/T05/T10,
plus Engine roadmap's disposable execution and cold-sealed recovery requirement.
This is an opt-in local continuation profile, not an accusation that original
F4's narrower trusted-flat-token profile promised physical producer exclusion.

## Hypothesis and smallest mechanism

Original managed F4 replays its journal's active=true and version on cold
startup. Test whether a previously issued token still admits new effects after
engine process death and recovery. Preserve an actually accepted pre-loss effect
and its exact bytes. Compare a healthy new authorized continuation.

Prototype a small subclass around the real cut sink. Every cold instance starts
with **admission sealed**, regardless of retained active bit. New use and new
obligations are refused until trusted local management completes native
replacement then native activation in that boot. Existing /replace and /activate
each keep their native append/publication order; do not invent an atomic pair.
Each recovery requires a new replacement, not just reusing the last replayed
active state. Old version cannot become current through restart. Initialization
remains distinct from recovery; no silent new journal/root or lost work.

Use only the existing trusted local manager boundary; caller labels do not
establish physical source identity. Replacement holder identity is a fixed
test-supervisor input, distinct from retained holder. New endpoint/version is
given to a new test worker. A deliberately old worker given the new version may
still pass: record that as the remaining **physical-source binding limit**, not
claiming confinement or non-transferability from an integer token.

Historical accepted effects remain retained. No pending external effect is
retroactively cancelled. This profile handles new use only and explicitly
excludes obligation endpoints. Ordinary local F4 publication/witness assumptions
remain unchanged; no new durable authority store, watchdog, scheduler or provider.
This is a disposable Python subclass reusing the native transaction/journal code.

## Discriminators

1. Original: accept x before sink death, kill/reap sink, recover same witness/root;
   old token admits a new effect (if observed), while old x remains exact.
2. Candidate: same accepted prefix, actual kill/reap, cold ready but sealed;
   old token/new-effect request denies with no new journal bytes. /activate alone
   cannot unseal. Native /replace increments version, then /activate permits a
   fresh correctly versioned effect; old version still denies. Preserve C/p and x.
3. Kill between replacement and activation, recover again: retained prefix whole,
   admission sealed; another fresh replacement required, no token resurrection.
4. Lost publication reply during replacement is not denial; exact local/remote
   readback determines permitted next operation. Do not reset state on 503.
5. An independent fixed worker's bounded CPU-only scratch progress continues
   across sink loss/sealed recovery as the D1/D2 vs optional D3 distinction.
   Its mediated new effect cannot commit until a permitted current route exists.
6. Explicitly demonstrate scope: old physical worker with newly supplied current
   token can still act under flat bearer semantics; no physical-source claim.

Use actual processes, old/new versions, native journal/witness and cold replay.
Independent raw checks plus altered controls. No host configuration, general
shell interface, external target/provider, CI, independent review or deployment.
