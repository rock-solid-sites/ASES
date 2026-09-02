//! CLI entry for ad-hoc invariant verification without Kani.
//!
//! `cargo run -p stop-button-kani` prints a summary of all Phase5 invariants
//! and exits non-zero if any fail. This is the thin runner for CI that does
//! not have `kani` installed — `cargo test` already covers the same predicates,
//! but this binary gives a single human-readable line per invariant for the
//! operator's verification log.

use stop_button_kani::{is_permitted, next_state, walk, Event, State, EVENTS, STATES};

fn check(name: &str, ok: bool) -> bool {
    if ok {
        println!("  PASS {name}");
    } else {
        println!("  FAIL {name}");
    }
    ok
}

fn main() {
    let mut all_ok = true;

    // Counts
    let permitted = STATES.iter().flat_map(|s| EVENTS.iter().map(move |e| is_permitted(*s, *e))).filter(|&b| b).count();
    all_ok &= check("permitted == 16", permitted == 16);
    all_ok &= check("forbidden == 28", 4 * 11 - permitted == 28);

    // I5 idle idempotence
    all_ok &= check("idle STOP_CLICK→idle", next_state(State::Idle, Event::StopClick) == Some(State::Idle));
    all_ok &= check("idle INTERRUPT_API→idle", next_state(State::Idle, Event::InterruptApi) == Some(State::Idle));

    // I5 interrupting idempotence
    all_ok &= check("interrupting STOP_CLICK→interrupting", next_state(State::Interrupting, Event::StopClick) == Some(State::Interrupting));
    all_ok &= check("interrupting INTERRUPT_API→interrupting", next_state(State::Interrupting, Event::InterruptApi) == Some(State::Interrupting));

    // P-PF5 settlement exclusivity
    all_ok &= check("Settled only from Interrupting", {
        let mut ok = true;
        for &s in &STATES {
            let p = is_permitted(s, Event::Settled);
            if s == State::Interrupting {
                ok &= p && next_state(s, Event::Settled) == Some(State::Idle);
            } else {
                ok &= !p;
            }
        }
        ok
    });
    all_ok &= check("DONE/ERROR only from Running", {
        let mut ok = true;
        for &s in &STATES {
            for e in [Event::Done, Event::Error] {
                let p = is_permitted(s, e);
                ok &= if s == State::Running { p } else { !p };
            }
        }
        ok
    });

    // Confirming never idle
    all_ok &= check("confirming never→idle", {
        let mut ok = true;
        for &e in &EVENTS {
            if let Some(nxt) = next_state(State::Confirming, e) {
                ok &= nxt != State::Idle;
            }
        }
        ok
    });

    // No drift: BFS reachable stays in enum
    all_ok &= check("BFS no drift", {
        let reachable = {
            use std::collections::HashSet;
            let mut reachable: HashSet<State> = HashSet::new();
            let mut frontier = vec![State::Idle];
            reachable.insert(State::Idle);
            for _ in 0..6 {
                let mut next_frontier = vec![];
                for &s in &frontier {
                    for &e in &EVENTS {
                        if let Some(nxt) = next_state(s, e) {
                            if reachable.insert(nxt) {
                                next_frontier.push(nxt);
                            }
                        }
                    }
                }
                frontier = next_frontier;
                if frontier.is_empty() { break; }
            }
            reachable
        };
        reachable.iter().all(|s| STATES.contains(s))
    });

    // Primary path
    all_ok &= check("primary path idle→idle", walk(&[Event::PromptSubmit, Event::StopClick, Event::Yes, Event::Settled]) == Some(State::Idle));
    all_ok &= check("esc bypass", walk(&[Event::PromptSubmit, Event::EscEsc]) == Some(State::Interrupting));

    println!();
    if all_ok {
        println!("All Phase5 invariants PASS (Kani-equivalent, without kani toolchain).");
    } else {
        eprintln!("Some invariants FAIL — see above.");
        std::process::exit(1);
    }
}
