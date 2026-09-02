//! Pure stop-button statechart — Rust mirror of
//! `fork/opencode-src/packages/tui/src/component/prompt/stop-button-machine.ts`
//!
//! This is the Kani verification target: the deterministic, side-effect-free
//! `next_state(state, event) -> Option<State>` that the shell interprets.
//! All invariants in `crate::invariants` are pure predicates over this function
//! and are proven by Kani (bounded model checking) and falsified by proptest
//! (property-based testing) — the two halves of Verified Spec Phase5 §3b.4.
//!
//! Source fidelity: Verified Spec §4.3 Permitted Transitions (16 entries),
//! §5 Invariants I4/I5, and Conformance Suite §5-8. The 4 states and 11 events
//! match the TS source exactly; the encoding is intentionally identical so that
//! any drift between the two mirrors is a spec violation.
//!
//! The file is `no_std`-friendly and has zero I/O imports.

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum State {
    Idle,
    Running,
    Confirming,
    Interrupting,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Event {
    PromptSubmit,
    StopClick,
    Yes,
    No,
    Esc,
    Dismiss,
    EscEsc,
    InterruptApi,
    Done,
    Error,
    Settled,
}

pub const STATES: [State; 4] = [State::Idle, State::Running, State::Confirming, State::Interrupting];
pub const EVENTS: [Event; 11] = [
    Event::PromptSubmit,
    Event::StopClick,
    Event::Yes,
    Event::No,
    Event::Esc,
    Event::Dismiss,
    Event::EscEsc,
    Event::InterruptApi,
    Event::Done,
    Event::Error,
    Event::Settled,
];

/// Authoritative permitted-transition table — Verified Spec §4.3 (16 entries).
/// `None` means forbidden (the complement is exactly 28 entries = 4*11-16).
pub fn next_state(state: State, event: Event) -> Option<State> {
    match (state, event) {
        // idle — §4.3
        (State::Idle, Event::PromptSubmit) => Some(State::Running),
        (State::Idle, Event::StopClick) => Some(State::Idle),
        (State::Idle, Event::InterruptApi) => Some(State::Idle),
        (State::Idle, Event::Esc) => Some(State::Idle),
        (State::Idle, Event::EscEsc) => Some(State::Idle),

        // running — §4.3
        (State::Running, Event::StopClick) => Some(State::Confirming),
        (State::Running, Event::EscEsc) => Some(State::Interrupting),
        (State::Running, Event::Done) => Some(State::Idle),
        (State::Running, Event::Error) => Some(State::Idle),

        // confirming — §4.3
        (State::Confirming, Event::Yes) => Some(State::Interrupting),
        (State::Confirming, Event::No) => Some(State::Running),
        (State::Confirming, Event::Esc) => Some(State::Running),
        (State::Confirming, Event::Dismiss) => Some(State::Running),

        // interrupting — idempotent until SETTLED (I5)
        (State::Interrupting, Event::StopClick) => Some(State::Interrupting),
        (State::Interrupting, Event::InterruptApi) => Some(State::Interrupting),
        (State::Interrupting, Event::Settled) => Some(State::Idle),

        _ => None,
    }
}

pub fn is_permitted(state: State, event: Event) -> bool {
    next_state(state, event).is_some()
}

/// Walk a sequence from Idle, returning the terminal state or None if a forbidden edge was hit.
/// Mirrors the TS `walk` helper in stop-button-proptest.test.ts.
pub fn walk(events: &[Event]) -> Option<State> {
    let mut cur = State::Idle;
    for &ev in events {
        match next_state(cur, ev) {
            Some(nxt) => cur = nxt,
            None => return None,
        }
    }
    Some(cur)
}

pub mod kani_harness;
pub mod proptest_harness;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn permitted_count_is_16() {
        let mut count = 0;
        for s in STATES {
            for e in EVENTS {
                if is_permitted(s, e) {
                    count += 1;
                }
            }
        }
        assert_eq!(count, 16);
    }

    #[test]
    fn forbidden_count_is_28() {
        let mut count = 0;
        for s in STATES {
            for e in EVENTS {
                if !is_permitted(s, e) {
                    count += 1;
                }
            }
        }
        assert_eq!(count, 28);
    }

    #[test]
    fn primary_path_idle_to_idle() {
        assert_eq!(
            walk(&[Event::PromptSubmit, Event::StopClick, Event::Yes, Event::Settled]),
            Some(State::Idle)
        );
    }

    #[test]
    fn esc_bypass() {
        assert_eq!(walk(&[Event::PromptSubmit, Event::EscEsc]), Some(State::Interrupting));
    }
}
