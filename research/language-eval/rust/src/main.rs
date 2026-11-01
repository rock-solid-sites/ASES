//! Intentionally small conventional Rust baseline. Not an operational admission gate.
use serde::{Deserialize, Serialize};
use std::io::{self, Read};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Case {
    id: String,
    mode: String,
    active: bool,
    verified: bool,
    evidence_current: bool,
    price_known: bool,
    capacity: i64,
    reserved: i64,
    requested: i64,
    usage: i64,
    included: i64,
    rate: i64,
    wallet: i64,
    wallet_floor: i64,
    liability: i64,
    spend_cap: i64,
    paid_opt_in: bool,
}

#[derive(Serialize)]
struct Decision<'a> {
    id: &'a str,
    accepted: bool,
    reason: &'static str,
    charge_cents: i64,
}

fn result<'a>(c: &'a Case, reason: &'static str, charge: i64) -> Decision<'a> {
    Decision { id: &c.id, accepted: reason == "admitted", reason, charge_cents: charge }
}

fn decide(c: &Case) -> Decision<'_> {
    if [
        c.capacity, c.reserved, c.requested, c.usage, c.included,
        c.rate, c.wallet, c.wallet_floor, c.liability, c.spend_cap
    ].iter().any(|n| *n < 0) || c.requested == 0 {
        return result(c, "invalid-input", 0);
    }
    if !matches!(c.mode.as_str(), "free" | "subscription" | "prepaid" | "postpaid") {
        return result(c, "invalid-input", 0);
    }
    if !c.active { return result(c, "inactive", 0); }
    if !c.verified { return result(c, "unverified", 0); }
    if !c.evidence_current { return result(c, "stale-evidence", 0); }
    if !c.price_known { return result(c, "unknown-price", 0); }
    if c.reserved > c.capacity || c.requested > c.capacity - c.reserved {
        return result(c, "capacity-exceeded", 0);
    }

    let billable = if c.mode == "free" || c.mode == "subscription" {
        c.usage.saturating_sub(c.included).max(0)
    } else {
        c.usage
    };
    let charge = match billable.checked_mul(c.rate) {
        Some(value) => value,
        None => return result(c, "arithmetic-overflow", 0),
    };
    if charge > 0 && !c.paid_opt_in {
        return result(c, "paid-opt-in-required", 0);
    }
    if c.mode == "prepaid" {
        if c.wallet < c.wallet_floor || charge > c.wallet - c.wallet_floor {
            return result(c, "wallet-floor-exceeded", 0);
        }
    } else if c.liability > c.spend_cap || charge > c.spend_cap - c.liability {
        return result(c, "spend-cap-exceeded", 0);
    }
    result(c, "admitted", charge)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut text = String::new();
    io::stdin().read_to_string(&mut text)?;
    let cases: Vec<Case> = serde_json::from_str(&text)?;
    let decisions: Vec<_> = cases.iter().map(decide).collect();
    serde_json::to_writer(io::stdout().lock(), &decisions)?;
    println!();
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn baseline() -> Case {
        serde_json::from_str(r#"{"id":"x","mode":"free","active":true,"verified":true,
        "evidence_current":true,"price_known":true,"capacity":16,"reserved":4,
        "requested":8,"usage":10,"included":20,"rate":2,"wallet":100,
        "wallet_floor":10,"liability":0,"spend_cap":100,"paid_opt_in":false}"#).unwrap()
    }
    #[test]
    fn free_does_not_imply_paid_authorization() {
        let mut c = baseline();
        c.usage = 21;
        assert_eq!(decide(&c).reason, "paid-opt-in-required");
    }
    #[test]
    fn free_included_is_admissible() {
        assert_eq!(decide(&baseline()).reason, "admitted");
        assert_eq!(decide(&baseline()).charge_cents, 0);
    }
    #[test]
    fn arithmetic_overflow_denied() {
        let mut c = baseline();
        c.mode = "postpaid".to_string();
        c.usage = i64::MAX;
        c.rate = 2;
        c.paid_opt_in = true;
        assert_eq!(decide(&c).reason, "arithmetic-overflow");
    }
}
