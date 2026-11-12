//! P4 minimal stateful research implementation. NOT a production admission gate.
//! Stale-snapshot mode is an intentionally broken experimental counterexample.
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::io::{self, Read};
use std::sync::{Arc, Barrier, Mutex, atomic::{AtomicUsize, Ordering}};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    id: String,
    units: i64,
    charge_cents: i64,
    paid_opt_in: bool,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Trial {
    capacity: i64,
    spend_cap_cents: i64,
    requests: Vec<Request>,
}
#[derive(Clone, Default)]
struct State {
    reserved: i64,
    charged_cents: i64,
    committed: HashSet<String>,
    accepted_count: usize,
}
#[derive(Serialize)]
struct Output {
    accepted_count: usize,
    rejected_count: usize,
    reserved: i64,
    charged_cents: i64,
    unique_commit_count: usize,
    workers_reached_barrier: usize,
    per_request_accepted: Vec<bool>,
    measured_delay_us_min: u128,
    measured_delay_us_sum: u128,
    elapsed_us: u128,
}

fn allowed(t: &Trial, req: &Request, snapshot: &State) -> bool {
    req.units > 0 && req.charge_cents >= 0
        && (req.charge_cents == 0 || req.paid_opt_in)
        && !snapshot.committed.contains(&req.id)
        && snapshot.reserved.checked_add(req.units).is_some_and(|v| v <= t.capacity)
        && snapshot.charged_cents.checked_add(req.charge_cents)
            .is_some_and(|v| v <= t.spend_cap_cents)
}
fn apply(current: &mut State, req: &Request) {
    current.reserved += req.units;
    current.charged_cents += req.charge_cents;
    current.committed.insert(req.id.clone());
    current.accepted_count += 1;
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    let (stale, delay_us) = match args.as_slice() {
        [a, mode, b, n] if a == "--mode" && b == "--delay-us" =>
            (match mode.as_str() {
                "safe" => false, "stale" => true,
                _ => return Err("mode must be safe or stale".into())
            }, n.parse::<u64>()?),
        _ => return Err("usage: p4 --mode safe|stale --delay-us N".into())
    };
    if delay_us > 10_000 { return Err("delay must be <= 10000us".into()); }
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    let trial: Trial = serde_json::from_str(&input)?;
    if trial.capacity < 0 || trial.spend_cap_cents < 0
        || trial.requests.is_empty() || trial.requests.len() > 16 {
        return Err("invalid bounded trial".into());
    }
    let start = Instant::now();
    let count = trial.requests.len();
    let trial = Arc::new(trial);
    let current = Arc::new(Mutex::new(State::default()));
    let barrier = Arc::new(Barrier::new(count + 1));
    let ready = Arc::new(AtomicUsize::new(0));
    let mut handles = Vec::new();
    for (index, req) in trial.requests.iter().cloned().enumerate() {
        let t = Arc::clone(&trial);
        let state = Arc::clone(&current);
        let gate = Arc::clone(&barrier);
        let ready_ctr = Arc::clone(&ready);
        handles.push(thread::spawn(move || {
            let before = if stale { Some(state.lock().unwrap().clone()) } else { None };
            ready_ctr.fetch_add(1, Ordering::SeqCst);
            gate.wait();
            let mut lock = state.lock().unwrap();
            let started_pause = Instant::now();
            if delay_us > 0 { thread::sleep(Duration::from_micros(delay_us)); }
            let observed_pause = started_pause.elapsed().as_micros();
            let granted = allowed(&t, &req, before.as_ref().unwrap_or(&lock));
            if granted { apply(&mut lock, &req); }
            (index, granted, observed_pause)
        }));
    }
    barrier.wait();
    let mut ordered = vec![false; count];
    let mut min_delay = u128::MAX;
    let mut total_delay = 0u128;
    for h in handles {
        let (index, granted, actual_pause) = h.join().map_err(|_| "worker panicked")?;
        ordered[index] = granted;
        min_delay = min_delay.min(actual_pause);
        total_delay += actual_pause;
    }
    let state = current.lock().unwrap();
    let output = Output {
        accepted_count: state.accepted_count,
        rejected_count: count - state.accepted_count,
        reserved: state.reserved,
        charged_cents: state.charged_cents,
        unique_commit_count: state.committed.len(),
        workers_reached_barrier: ready.load(Ordering::SeqCst),
        per_request_accepted: ordered,
        measured_delay_us_min: min_delay,
        measured_delay_us_sum: total_delay,
        elapsed_us: start.elapsed().as_micros(),
    };
    println!("{}", serde_json::to_string(&output)?);
    Ok(())
}
