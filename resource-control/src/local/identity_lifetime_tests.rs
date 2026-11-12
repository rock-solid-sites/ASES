//! Bounded observation-fault histories for an actual LocalSupervisor Child.
//!
//! The reader can offer a synthetic stale token after the owned Child has
//! exited and been reaped. That token is deliberately not an OS observation
//! and does not imply that a second process or PID reuse occurred.

use super::{LocalProfile, LocalSupervisor};
use crate::catalog::Account;
use crate::{now, BeginLaunchResult, Claim, Environment, Meter, ProcessIdentity, Proposal, Store};
use serde_json::Value;
use std::cell::RefCell;
use std::collections::BTreeMap;
use std::path::PathBuf;
use std::rc::Rc;
use std::thread;
use std::time::{Duration, Instant};

const ACCOUNT: &str = "identity-lifetime-account";
const PROJECT: &str = "identity-lifetime-project";
const ENVIRONMENT: &str = "identity-lifetime-environment";
const METER: &str = "identity-lifetime-meter";
const INJECTED_STALE_TOKEN: &str = "injected-stale-token-not-from-procfs";

#[derive(Clone, Copy)]
enum ReaderMode { Fail, Stale }

struct Fixture {
    _dir: tempfile::TempDir,
    store: Store,
    supervisor: LocalSupervisor,
    profile: LocalProfile,
    revision: i64,
    job: String,
    launch: String,
    reader_mode: Rc<RefCell<ReaderMode>>,
}

fn proposal(job: &str) -> Proposal {
    Proposal {
        job_id: job.into(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(), estimated_wall_seconds: 30,
        claims: vec![Claim { meter_id: METER.into(), amount: 5 }],
        paid_spend_cap_micros: None, paid_spend_cap_currency: None,
        forecast_context: None,
    }
}

fn fixture(label: &str) -> Fixture {
    let dir = tempfile::tempdir().unwrap();
    let mut store = Store::open(dir.path().join("control.sqlite")).unwrap();
    let at = now();
    store.register_account(&Account {
        id: ACCOUNT.into(), provider: "local".into(), payer_ref: "synthetic".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec![PROJECT.into()],
        source: "synthetic-identity-lifetime-test".into(), observed_at: at, ttl_seconds: 3600,
    }).unwrap();
    store.register_meter(&Meter {
        id: METER.into(), account: ACCOUNT.into(), provider: "local".into(),
        product: "fixed-harmless-test-program".into(), period: "test".into(), unit: "units".into(),
        limit: 20, guard: 0, observed_at: at, ttl_seconds: 3600,
        source: "synthetic-identity-lifetime-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false,
    }).unwrap();
    store.register_environment(&Environment {
        id: ENVIRONMENT.into(), account: ACCOUNT.into(), provider: "local".into(),
        max_parallel: 1, observed_at: at, ttl_seconds: 3600,
        source: "synthetic-identity-lifetime-test".into(),
    }).unwrap();
    let job = format!("identity-lifetime-{label}");
    let launch = format!("identity-lifetime-launch-{label}");
    let revision = store.catalog_version().unwrap();
    store.reserve(&proposal(&job), revision, at).unwrap();
    store.acknowledge(&job, &format!("ack-{label}"), revision, at).unwrap();
    let profile = LocalProfile {
        program: PathBuf::from("/bin/true"), args: vec![], cwd: PathBuf::from("/"),
        env: BTreeMap::new(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(),
    };
    let reader_mode = Rc::new(RefCell::new(ReaderMode::Fail));
    let mode = Rc::clone(&reader_mode);
    let mut supervisor = LocalSupervisor::default();
    supervisor.identity_reader = Box::new(move |pid| match *mode.borrow() {
        ReaderMode::Fail => Err(crate::Error::Io(std::io::Error::new(
            std::io::ErrorKind::PermissionDenied,
            "injected initial/post-spawn identity observation failure",
        ))),
        ReaderMode::Stale => Ok(ProcessIdentity {
            pid, start_token: INJECTED_STALE_TOKEN.into(),
        }),
    });
    Fixture { _dir: dir, store, supervisor, profile, revision, job, launch, reader_mode }
}

fn launch_and_reap(f: &mut Fixture) -> u32 {
    let reply = f.supervisor.launch(&mut f.store, &f.profile, &f.job, &f.launch, f.revision, now()).unwrap();
    assert_eq!(reply["state"], "unknown", "the injected first identity read must fail: {reply}");
    let key = (f.job.clone(), f.launch.clone());
    let until = Instant::now() + Duration::from_secs(5);
    loop {
        // Poll while the reader continues to fail. This uses Child::try_wait;
        // the test proceeds only after the actual owned Child was reaped.
        let _ = f.supervisor.poll(&mut f.store, &f.job, &f.launch, now()).unwrap();
        if let Some(owned) = f.supervisor.children.get(&key) {
            if owned.exited.is_some() {
                let pid = owned.child.id();
                assert!(owned.process.is_none(), "no identity was observed before reap");
                break pid;
            }
        }
        assert!(Instant::now() < until, "actual /bin/true Child did not exit and reap in time");
        thread::sleep(Duration::from_millis(2));
    }
}

fn offer_stale(f: &Fixture) { *f.reader_mode.borrow_mut() = ReaderMode::Stale; }

fn event_kinds(store: &Store, job: &str) -> Vec<String> {
    store.event_log(Some(job)).unwrap().iter()
        .filter_map(|event| event.get("kind").and_then(Value::as_str).map(str::to_owned))
        .collect()
}

fn assert_unknown_is_durable(f: &mut Fixture, reply: &Value, expected_stop_event: bool) {
    let kinds = event_kinds(&f.store, &f.job);
    let job_state = f.store.job(&f.job).unwrap()["state"].clone();
    let resume = f.supervisor.resume(&f.store, &f.job, &f.launch).unwrap();
    assert_eq!(reply["state"], "unknown",
        "post-reap reader output cannot establish exact outcome: reply={reply}; job_state={job_state}; events={kinds:?}; resume={resume}");
    assert!(!kinds.iter().any(|kind| kind == "LAUNCH_STARTED_OBSERVED"), "events: {kinds:?}");
    assert!(!kinds.iter().any(|kind| kind == "LAUNCH_EXIT_OBSERVED"), "events: {kinds:?}");
    assert_eq!(kinds.iter().filter(|kind| kind.as_str() == "LAUNCH_INTENT").count(), 1, "one durable dispatch intent: {kinds:?}");
    assert_eq!(kinds.iter().any(|kind| kind == "LOCAL_STOP_REQUESTED"), expected_stop_event, "events: {kinds:?}");
    assert_eq!(f.store.job(&f.job).unwrap()["state"], "LAUNCHING");
    let view = f.store.resume_view(&f.job).unwrap();
    assert_eq!(view.present_liveness, crate::PresentLiveness::Unknown);
    assert!(matches!(f.store.begin_launch(&f.job, &f.launch, f.revision, now()).unwrap(),
        BeginLaunchResult::PendingObservation { .. }));
    assert!(f.supervisor.finalize(&mut f.store, &f.job, &f.launch, "cancelled", now()).is_err());
    assert_eq!(f.store.job(&f.job).unwrap()["state"], "LAUNCHING", "finalize refusal preserves state");
    let balance = f.store.balances(now()).unwrap();
    let held = balance.iter().find(|row| row.meter_id == METER).unwrap();
    assert_eq!(held.active_reserved_remaining, 5, "capacity remains reserved");
    assert_eq!(held.available, 15, "available capacity remains reduced by reservation");
    assert_eq!(f.supervisor.children.len(), 1, "replay cannot dispatch a second actual Child");
}

#[test]
fn injected_stale_identity_after_reap_does_not_turn_poll_into_evidence() {
    let mut f = fixture("poll");
    let pid = launch_and_reap(&mut f);
    offer_stale(&f);
    let reply = f.supervisor.poll(&mut f.store, &f.job, &f.launch, now()).unwrap();
    assert_eq!(f.supervisor.children[&(f.job.clone(), f.launch.clone())].child.id(), pid);
    assert_unknown_is_durable(&mut f, &reply, false);
}

#[test]
fn exact_launch_replay_after_reap_does_not_dispatch_or_create_evidence() {
    let mut f = fixture("replay");
    let pid = launch_and_reap(&mut f);
    offer_stale(&f);
    let reply = f.supervisor.launch(&mut f.store, &f.profile, &f.job, &f.launch, f.revision, now()).unwrap();
    assert_eq!(f.supervisor.children[&(f.job.clone(), f.launch.clone())].child.id(), pid);
    assert_unknown_is_durable(&mut f, &reply, false);
}

#[test]
fn force_stop_after_reap_does_not_create_started_or_exit_evidence() {
    let mut f = fixture("force-stop");
    launch_and_reap(&mut f);
    offer_stale(&f);
    let reply = f.supervisor.stop(&mut f.store, &f.job, &f.launch, "stop-force", now()).unwrap();
    assert_unknown_is_durable(&mut f, &reply, true);
}

#[test]
fn graceful_stop_after_reap_does_not_create_started_or_exit_evidence() {
    let mut f = fixture("graceful-stop");
    launch_and_reap(&mut f);
    offer_stale(&f);
    let reply = f.supervisor.stop_graceful(&mut f.store, &f.job, &f.launch, "stop-graceful", 50, now()).unwrap();
    assert_unknown_is_durable(&mut f, &reply, true);
    assert_ne!(reply["term_attempted"], true, "no signal attempt without lifetime-bound identity");
    assert_ne!(reply["kill_attempted"], true, "no escalation without lifetime-bound identity");
}

#[test]
fn resume_does_not_label_unidentified_child_exit_as_observed() {
    let mut f = fixture("resume");
    launch_and_reap(&mut f);
    let before_stale = f.supervisor.resume(&f.store, &f.job, &f.launch).unwrap();
    assert_eq!(before_stale["local_state"], "unknown");
    assert_eq!(before_stale["resume_view"]["presentLiveness"], "unknown");
    offer_stale(&f);
    let reply = f.supervisor.poll(&mut f.store, &f.job, &f.launch, now()).unwrap();
    assert_unknown_is_durable(&mut f, &reply, false);
    let after_stale = f.supervisor.resume(&f.store, &f.job, &f.launch).unwrap();
    assert_eq!(after_stale["local_state"], "unknown");
}
