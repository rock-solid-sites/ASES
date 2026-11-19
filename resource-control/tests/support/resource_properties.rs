use ases_resource_control::{now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::catalog::Account;

/// Independent integer budget oracle over the ACTUAL SQLite-backed resource-control Store.
/// The 100-unit boundary, fresh provider account and isolated process-local temporary DB
/// are explicit fixture choices; they do not establish real provider-resource behavior.
pub fn verify_claim_sequence(claims: &[u8]) -> Result<(), String> {
    let dir = tempfile::tempdir().map_err(|e| e.to_string())?;
    let path = dir.path().join("resource-property.sqlite");
    let at = now();
    let mut store = Store::open(&path).map_err(|e| e.to_string())?;
    store.register_account(&Account {
        id: "acct-property".into(), provider: "local".into(), payer_ref: "fixture".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec!["assurance".into()],
        source: "test-fixture-only".into(), observed_at: at, ttl_seconds: 3600,
    }).map_err(|e| e.to_string())?;
    store.register_meter(&Meter {
        id: "core".into(), account: "acct-property".into(), provider: "local".into(),
        product: "fixed-fixture".into(), period: "fixture-period".into(), unit: "units".into(),
        limit: 100, guard: 0, observed_at: at, ttl_seconds: 3600,
        source: "test-fixture-only".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false,
    }).map_err(|e| e.to_string())?;
    store.register_environment(&Environment {
        id: "env".into(), account: "acct-property".into(), provider: "local".into(),
        max_parallel: 64, observed_at: at, ttl_seconds: 3600,
        source: "test-fixture-only".into(),
    }).map_err(|e| e.to_string())?;
    let revision = store.catalog_version().map_err(|e| e.to_string())?;
    let mut expected_used = 0_i64;

    for (index, &amount_u8) in claims.iter().enumerate() {
        if amount_u8 == 0 || amount_u8 > 80 {
            return Err(format!("out of declared generator bounds: amount={amount_u8}"));
        }
        let amount = u64::from(amount_u8);
        let job_id = format!("job-{index}");
        let proposal = Proposal {
            job_id: job_id.clone(), account_id: "acct-property".into(),
            project_id: "assurance".into(), environment_id: "env".into(),
            estimated_wall_seconds: 60,
            claims: vec![Claim { meter_id: "core".into(), amount }],
            paid_spend_cap_micros: None, paid_spend_cap_currency: None,
            forecast_context: None,
        };
        let before_events = store.event_log(None).map_err(|e| e.to_string())?.len();
        let before_balance = store.balances(at).map_err(|e| e.to_string())?
            .into_iter().find(|b| b.meter_id == "core")
            .ok_or("missing budget meter before reservation")?.available;
        let predicted_accept = expected_used + i64::from(amount_u8) <= 100;
        let actual = store.reserve(&proposal, revision, at);
        if actual.is_ok() != predicted_accept {
            return Err(format!("step={index} amount={amount} expected_accept={predicted_accept} actual={actual:?} remaining={before_balance}"));
        }
        if let Ok(receipt) = actual {
            if receipt.replayed {
                return Err(format!("step={index} first admission was reported as replay"));
            }
            expected_used += i64::from(amount_u8);
            let first_events = store.event_log(None).map_err(|e| e.to_string())?.len();
            let replay = store.reserve(&proposal, revision, at).map_err(|e| format!("step={index} exact-ID replay failed: {e}"))?;
            if !replay.replayed { return Err(format!("step={index} exact-ID replay created another reservation")); }
            if store.event_log(None).map_err(|e| e.to_string())?.len() != first_events {
                return Err(format!("step={index} replay appended an event"));
            }
        } else if store.event_log(None).map_err(|e| e.to_string())?.len() != before_events {
            return Err(format!("step={index} rejected request appended event"));
        }
        let after = store.balances(at).map_err(|e| e.to_string())?.into_iter()
            .find(|b| b.meter_id == "core").ok_or("missing budget meter")?;
        if after.available != 100 - expected_used || after.active_reserved_remaining != expected_used {
            return Err(format!("step={index} budget conservation failure: expected_remaining={} actual_remaining={} expected_reserved={} actual_reserved={}",
                100 - expected_used, after.available, expected_used, after.active_reserved_remaining));
        }
        if !predicted_accept && before_balance != after.available {
            return Err(format!("step={index} rejected request changed available capacity"));
        }
    }

    // A wrong catalog revision must neither admit nor mutate durable state, even if units remain.
    let stale = Proposal {
        job_id: "wrong-revision".into(), account_id: "acct-property".into(),
        project_id: "assurance".into(), environment_id: "env".into(),
        estimated_wall_seconds: 60, claims: vec![Claim { meter_id: "core".into(), amount: 1 }],
        paid_spend_cap_micros: None, paid_spend_cap_currency: None, forecast_context: None,
    };
    let events_before = store.event_log(None).map_err(|e| e.to_string())?.len();
    if store.reserve(&stale, revision + 1, at).is_ok() {
        return Err("stale catalog revision unexpectedly admitted".into());
    }
    if store.event_log(None).map_err(|e| e.to_string())?.len() != events_before {
        return Err("stale catalog version appended event".into());
    }
    drop(store);
    // A real SQLite reopen: reservation history must survive process-local Store destruction.
    let mut reopened = Store::open(&path).map_err(|e| e.to_string())?;
    let final_balance = reopened.balances(at).map_err(|e| e.to_string())?.into_iter()
        .find(|b| b.meter_id == "core").ok_or("meter missing after reopened SQLite")?;
    if final_balance.available != 100 - expected_used ||
        final_balance.active_reserved_remaining != expected_used {
        return Err(format!("reopened store lost reservations expected_remaining={} actual={}",
            100 - expected_used, final_balance.available));
    }
    Ok(())
}
