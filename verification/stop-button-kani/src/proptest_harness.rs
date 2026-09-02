//! Rust `proptest` property harness — the Rust half of Verified Spec Phase5 proptest hardening.
//!
//! The TS harness (`stop-button-proptest.test.ts` via fast-check) and this Rust
//! harness are the two carriers of the same properties (P-PF3..P-PF5, §5 I4/I5).
//! Either one failing indicates a bug or a spec needing refinement — both feed
//! back through VSDD Phase 4 (§IV), exactly as spec §3b.4 prescribes.
//!
//! Run: `cargo test` (200 cases per property, seed-agnostic shrinking).

#[cfg(test)]
mod tests {
    use crate::{is_permitted, next_state, walk, Event, State, EVENTS, STATES};
    use proptest::prelude::*;

    fn arb_state() -> impl Strategy<Value = State> {
        prop_oneof![
            Just(State::Idle),
            Just(State::Running),
            Just(State::Confirming),
            Just(State::Interrupting),
        ]
    }

    fn arb_event() -> impl Strategy<Value = Event> {
        prop_oneof![
            Just(Event::PromptSubmit),
            Just(Event::StopClick),
            Just(Event::Yes),
            Just(Event::No),
            Just(Event::Esc),
            Just(Event::Dismiss),
            Just(Event::EscEsc),
            Just(Event::InterruptApi),
            Just(Event::Done),
            Just(Event::Error),
            Just(Event::Settled),
        ]
    }

    fn arb_event_seq(len: usize) -> impl Strategy<Value = Vec<Event>> {
        prop::collection::vec(arb_event(), 0..len)
    }

    proptest! {
        #![proptest_config(ProptestConfig { cases: 200, .. ProptestConfig::default() })]

        #[test]
        fn pf3_state_gating_every_step_respects_is_permitted(seq in arb_event_seq(20)) {
            let mut cur = State::Idle;
            for ev in seq {
                let permitted = is_permitted(cur, ev);
                let nxt = next_state(cur, ev);
                if permitted {
                    prop_assert!(nxt.is_some(), "{:?}:{:?} permitted must have next", cur, ev);
                    cur = nxt.unwrap();
                } else {
                    prop_assert!(nxt.is_none(), "{:?}:{:?} forbidden must be None", cur, ev);
                    break;
                }
            }
        }

        #[test]
        fn pf4a_idempotence_idle(seq in arb_event_seq(20)) {
            let mut cur = State::Idle;
            for ev in seq {
                if let Some(nxt) = next_state(cur, ev) {
                    if cur == State::Idle && (ev == Event::StopClick || ev == Event::InterruptApi) {
                        prop_assert_eq!(nxt, State::Idle, "idle {:?} must stay Idle", ev);
                    }
                    cur = nxt;
                } else {
                    break;
                }
            }
        }

        #[test]
        fn pf4b_idempotence_interrupting(seq in arb_event_seq(20)) {
            let mut cur = State::Idle;
            for ev in seq {
                if let Some(nxt) = next_state(cur, ev) {
                    if cur == State::Interrupting && (ev == Event::StopClick || ev == Event::InterruptApi) {
                        prop_assert_eq!(nxt, State::Interrupting, "interrupting {:?} must coalesce", ev);
                    }
                    cur = nxt;
                } else {
                    break;
                }
            }
        }

        #[test]
        fn pf5_settlement_exclusivity(seq in arb_event_seq(20)) {
            let mut cur = State::Idle;
            for ev in seq {
                let permitted = is_permitted(cur, ev);
                if permitted {
                    if ev == Event::Settled {
                        prop_assert_eq!(cur, State::Interrupting, "Settled only from Interrupting");
                        prop_assert_eq!(next_state(cur, ev), Some(State::Idle));
                    }
                    if ev == Event::Done || ev == Event::Error {
                        prop_assert_eq!(cur, State::Running, "{:?} only from Running", ev);
                    }
                    cur = next_state(cur, ev).unwrap();
                } else {
                    break;
                }
            }
        }

        #[test]
        fn pf6_total_function_agreement(s in arb_state(), e in arb_event()) {
            prop_assert_eq!(next_state(s, e).is_some(), is_permitted(s, e));
        }

        #[test]
        fn pf7_no_drift_any_seq_stays_in_enum(seq in arb_event_seq(50)) {
            let result = walk(&seq);
            if let Some(s) = result {
                prop_assert!(STATES.contains(&s), "walk result {:?} must be one of STATES", s);
            }
        }

        #[test]
        fn pf8_confirming_never_idle(seq in arb_event_seq(20)) {
            let mut cur = State::Idle;
            for ev in seq {
                if let Some(nxt) = next_state(cur, ev) {
                    if cur == State::Confirming {
                        prop_assert_ne!(nxt, State::Idle, "Confirming:{:?} must not go to Idle", ev);
                    }
                    cur = nxt;
                } else {
                    break;
                }
            }
        }

        #[test]
        fn pf9_yes_only_from_confirming_and_esc_esc_limited(seq in arb_event_seq(20)) {
            let mut cur = State::Idle;
            for ev in seq {
                let permitted = is_permitted(cur, ev);
                if permitted && ev == Event::Yes {
                    prop_assert_eq!(cur, State::Confirming, "Yes only from Confirming");
                }
                if permitted && ev == Event::EscEsc {
                    prop_assert!(
                        cur == State::Idle || cur == State::Running,
                        "EscEsc permitted only from Idle/Running, got {:?}", cur
                    );
                }
                if permitted {
                    cur = next_state(cur, ev).unwrap();
                } else {
                    break;
                }
            }
        }

        #[test]
        fn count_invariants_permitted_16_forbidden_28(_dummy in 0u8..1) {
            let permitted = STATES.iter().flat_map(|s| EVENTS.iter().map(move |e| is_permitted(*s, *e))).filter(|&b| b).count();
            prop_assert_eq!(permitted, 16);
            prop_assert_eq!(4 * 11 - permitted, 28);
        }
    }
}
