# Security and adversarial modeling

Use Alloy to expose trust assumptions and find attack-shaped counterexamples. A fact models an environmental guarantee; it does not implement the protection in deployed code.

## Separate trust boundaries

Model these concepts independently when they affect the claim:

- trusted server-side credential or session ownership;
- untrusted request-supplied identities, tokens, and payloads;
- attacker knowledge, observation, guessing, or replay capability;
- transport and origin guarantees;
- successful authentication, authorization, and state-changing events.

Treat a capability as unforgeable only if an explicit knowledge or possession rule makes it so. State what is omitted: entropy, expiry, replay protection, CSRF, XSS, secure-cookie flags, endpoint compromise, and implementation conformance.

## Simple web-attack case study

The published model is a 2018 pre-Alloy-6 model. It combines browser and server data in ordered `State` atoms and labels transitions with `INIT`, `LOGIN`, `BUY`, and `STUTTER`. Read [legacy-migration.md](legacy-migration.md) before porting its syntax.

Its useful lesson is not “the web is safe.” It is that counterexamples expose unstated trust assumptions:

1. Eve’s credential fields are unconstrained, so Alloy may choose Alice’s credentials for Eve. Unconstrained means attacker-chosen, not absent.
2. Adding a no-shared-credential assumption blocks that trace.
3. Eve can then use Alice’s active token because buying checks whether a token has a cart, not whether the presented token belongs to the acting browser.
4. Adding a token-to-browser binding assumption blocks that second trace within the checked scope.

Source-model caveats:

- the `digest` function is identity, not cryptography;
- the model’s `HTTPS` fact represents token possession/binding, not TLS;
- the trace contains no observation or theft event, so the attacker effectively guesses or supplies arbitrary values;
- cart ownership and contents are mixed in one heterogeneous relation;
- client cookies and trusted server state share one state container, blurring the trust boundary;
- the published prose mentions an `EveBuying` command that is not present in the source.

The assertion named `Evil` forbids every state attributed to Eve, not specifically a successful login or purchase. Prefer precise claims such as `AttackerCannotLogin` and `AttackerCannotBuy` tied to event success.

## Attack-and-repair workflow

1. Run a witness showing legitimate behavior succeeds.
2. Run or check for the attack before adding the protection.
3. Preserve the failing command as a regression case.
4. Add one justified assumption or design control.
5. Re-run both the legitimate witness and the unchanged security assertion.
6. Report omitted attacker powers and the exact scope/horizon.

After every security fact, rerun a nontrivial legitimate witness. Otherwise an inconsistent fact can make “no counterexample” vacuously true.

## Claim design

Tie properties to observable success, not attacker presence:

```alloy
assert AttackerCannotPurchase {
  traces implies always no Attacker.(Store.purchased)
}
```

If the model records failed requests, do not forbid all attacker actions. Distinguish attempted, authenticated, authorized, and committed events.

Do not patch a counterexample until classifying it as a model fault, missing real-world assumption, or actual design vulnerability.
