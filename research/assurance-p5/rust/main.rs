//! Minimal P5 *research-only* crash recovery simulator.
//! No production billing, provider APIs, or multi-process locking.
//! Append and fsync occur before ACK in correct mode; early_ack deliberately violates that order.
use std::collections::HashSet;
use std::fs::{self, OpenOptions};
use std::io::{self, BufRead, Write};
use std::path::Path;

#[derive(Default)]
struct Ledger {
    reserved: i64,
    charged: i64,
    entries: usize,
    ids: HashSet<String>,
}

fn replay(path: &str) -> Result<Ledger, Box<dyn std::error::Error>> {
    let mut ledger = Ledger::default();
    if !Path::new(path).exists() { return Ok(ledger) }
    for line in fs::read_to_string(path)?.lines() {
        let parts: Vec<_> = line.split('|').collect();
        if parts.len() != 3 || parts[0].is_empty() || parts[0].len() > 12
            || !parts[0].chars().all(|c| c.is_ascii_alphanumeric()) {
            return Err("malformed journal entry".into());
        }
        let units: i64 = parts[1].parse()?;
        let charge: i64 = parts[2].parse()?;
        if units <= 0 || charge < 0 { return Err("invalid journal amount".into()) }
        ledger.reserved = ledger.reserved.checked_add(units).ok_or("reserved overflow")?;
        ledger.charged = ledger.charged.checked_add(charge).ok_or("charged overflow")?;
        ledger.entries += 1;
        ledger.ids.insert(parts[0].to_string());
    }
    Ok(ledger)
}

fn marker(value: &str) -> io::Result<()> {
    println!("{value}");
    io::stdout().flush()
}
fn gate() -> Result<(), Box<dyn std::error::Error>> {
    let mut line = String::new();
    io::stdin().lock().read_line(&mut line)?;
    if line.trim() != "GO" { return Err("checkpoint release denied".into()) }
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match args.as_slice() {
        [command, path] if command == "inspect" => {
            let state = replay(path)?;
            println!("STATE|{}|{}|{}|{}", state.reserved, state.charged,
                     state.entries, state.ids.len());
        }
        [command, path, mode, hook, id, units, charge, capacity, cap, consent]
        if command == "apply" => {
            if !["correct", "duplicate", "early_ack"].contains(&mode.as_str())
                || !["none", "before", "after_sync", "after_ack"].contains(&hook.as_str()) {
                return Err("unknown mode or hook".into());
            }
            if id.is_empty() || id.len() > 12
                || !id.chars().all(|c| c.is_ascii_alphanumeric()) {
                return Err("bad ID".into());
            }
            let units: i64 = units.parse()?;
            let charge: i64 = charge.parse()?;
            let capacity: i64 = capacity.parse()?;
            let cap: i64 = cap.parse()?;
            let paid_opt_in = match consent.as_str() {
                "true" => true, "false" => false, _ => return Err("bad opt-in".into())
            };
            let state = replay(path)?;
            if mode != "duplicate" && state.ids.contains(id) {
                marker("DUPLICATE")?;
                return Ok(());
            }
            if units <= 0 || charge < 0 || capacity < 0 || cap < 0
                || (charge > 0 && !paid_opt_in)
                || state.reserved.checked_add(units).is_none_or(|v| v > capacity)
                || state.charged.checked_add(charge).is_none_or(|v| v > cap) {
                marker("DENY")?;
                return Ok(());
            }
            if hook == "before" {
                marker("PREPARED")?;
                gate()?;
            }
            if mode == "early_ack" {
                marker("ACK")?;
                if hook == "after_ack" { gate()?; }
            }
            let mut file = OpenOptions::new().create(true).append(true).open(path)?;
            let entry = format!("{id}|{units}|{charge}\n");
            file.write_all(entry.as_bytes())?;
            file.sync_all()?; // fsync, not a simulated power-loss guarantee
            if hook == "after_sync" {
                marker("DURABLE")?;
                gate()?;
            }
            if mode != "early_ack" {
                marker("ACK")?;
                if hook == "after_ack" { gate()?; }
            }
        }
        _ => return Err("usage: inspect JOURNAL | apply JOURNAL MODE HOOK ID UNITS CHARGE CAPACITY SPEND_CAP OPT_IN".into())
    }
    Ok(())
}
