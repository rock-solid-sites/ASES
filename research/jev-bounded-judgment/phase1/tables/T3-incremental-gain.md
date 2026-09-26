# T3 — Incremental gain over the cheapest preceding mechanism

Mechanism cost order is normative (`schema.md` 3.1): prior -> rule -> lexical -> jev -> general_model. So **Jev's cheapest preceding mechanism is `lexical`** and that is the headline row.

Pairing: cases where BOTH mechanisms produced a usable label on an ANSWERABLE case. Unanswerable cases are excluded here and handled by the false-confidence column of T1/T2. `b` = challenger right / incumbent wrong, `c` = the reverse (McNemar cells). **No significance test is claimed** — at n<=50 the cheapest-test-first bar forbids it.

## T3a — chain

| scope | mechanism | vs | n paired | acc | prev acc | delta | McNemar |
|---|---|---|---|---|---|---|---|
| ALL | prior | — | — | — | — | — | floor (cheapest mechanism) |
| ALL | rule | prior | 50 | 78.0% | 44.0% | +34.0pp | b=28 c=11 |
| ALL | lexical | rule | 50 | 58.0% | 78.0% | -20.0pp | b=4 c=14 |
| ALL | jev | lexical | 50 | 98.0% | 58.0% | +40.0pp | b=20 c=0 |
| ALL | general_model | jev | 50 | 100.0% | 98.0% | +2.0pp | b=1 c=0 |
| area A | prior | — | — | — | — | — | floor (cheapest mechanism) |
| area A | rule | prior | 22 | 72.7% | 59.1% | +13.6pp | b=9 c=6 |
| area A | lexical | rule | 22 | 59.1% | 72.7% | -13.6pp | b=3 c=6 |
| area A | jev | lexical | 22 | 100.0% | 59.1% | +40.9pp | b=9 c=0 |
| area A | general_model | jev | 22 | 100.0% | 100.0% | +0.0pp | b=0 c=0 |
| area B | prior | — | — | — | — | — | floor (cheapest mechanism) |
| area C | prior | — | — | — | — | — | floor (cheapest mechanism) |
| area C | rule | prior | 16 | 68.8% | 37.5% | +31.2pp | b=10 c=5 |
| area C | lexical | rule | 16 | 75.0% | 68.8% | +6.2pp | b=1 c=0 |
| area C | jev | lexical | 16 | 93.8% | 75.0% | +18.8pp | b=3 c=0 |
| area C | general_model | jev | 16 | 100.0% | 93.8% | +6.2pp | b=1 c=0 |
| area D | prior | — | — | — | — | — | floor (cheapest mechanism) |
| area D | rule | prior | 12 | 100.0% | 25.0% | +75.0pp | b=9 c=0 |
| area D | lexical | rule | 12 | 33.3% | 100.0% | -66.7pp | b=0 c=8 |
| area D | jev | lexical | 12 | 100.0% | 33.3% | +66.7pp | b=8 c=0 |
| area D | general_model | jev | 12 | 100.0% | 100.0% | +0.0pp | b=0 c=0 |
| split train | prior | — | — | — | — | — | floor (cheapest mechanism) |
| split train | rule | prior | 18 | 77.8% | 55.6% | +22.2pp | b=8 c=4 |
| split train | lexical | rule | 18 | 66.7% | 77.8% | -11.1pp | b=2 c=4 |
| split train | jev | lexical | 18 | 100.0% | 66.7% | +33.3pp | b=6 c=0 |
| split train | general_model | jev | 18 | 100.0% | 100.0% | +0.0pp | b=0 c=0 |
| split dev | prior | — | — | — | — | — | floor (cheapest mechanism) |
| split dev | rule | prior | 15 | 73.3% | 33.3% | +40.0pp | b=10 c=4 |
| split dev | lexical | rule | 15 | 53.3% | 73.3% | -20.0pp | b=0 c=3 |
| split dev | jev | lexical | 15 | 93.3% | 53.3% | +40.0pp | b=6 c=0 |
| split dev | general_model | jev | 15 | 100.0% | 93.3% | +6.7pp | b=1 c=0 |
| split test | prior | — | — | — | — | — | floor (cheapest mechanism) |
| split test | rule | prior | 17 | 82.3% | 41.2% | +41.2pp | b=10 c=3 |
| split test | lexical | rule | 17 | 52.9% | 82.3% | -29.4pp | b=2 c=7 |
| split test | jev | lexical | 17 | 100.0% | 52.9% | +47.1pp | b=8 c=0 |
| split test | general_model | jev | 17 | 100.0% | 100.0% | +0.0pp | b=0 c=0 |

## T3b — Jev against every other mechanism, whole grid

| comparison | incumbent | n paired | jev acc | incumbent acc | delta | McNemar |
|---|---|---|---|---|---|---|
| jev vs prior | prior | 50 | 98.0% | 44.0% | +54.0pp | b=28 c=1 |
| jev vs rule | rule | 50 | 98.0% | 78.0% | +20.0pp | b=10 c=0 |
| jev vs lexical | lexical | 50 | 98.0% | 58.0% | +40.0pp | b=20 c=0 |
| jev vs general_model | general_model | 50 | 98.0% | 100.0% | -2.0pp | b=0 c=1 |

> T3b is the honest comparator set. `jev vs lexical` is the cheap-baseline question the brief asks; `jev vs general_model` is the one that decides the brief's actual question, because both mechanisms are free-tier and the general model was available to the user anyway. A negative delta there means Jev adds nothing over a free chat model on this corpus.

MECHANISMS is ordered by cost (schema.md 3.1) and that order is normative, so 'cheapest preceding mechanism' is well defined. Pairing is restricted to cases where BOTH mechanisms produced a usable label on an ANSWERABLE case; unanswerable cases are excluded here and handled by m1.false_confidence_rate and m4 instead. discordant_b/c are the McNemar cells; no significance test is claimed.

jev vs prior/rule/lexical is the cheap-baseline question (area A of the brief). jev vs general_model is the honest comparator: both are free-tier, and if the free chat model matches Jev then Jev's gain is over a mechanism the user could have run anyway.
