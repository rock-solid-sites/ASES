//! Native owned-child evidence for intent-backed termination and capacity release.
//! Every child is this fixed test binary; no arbitrary executable or PID is adopted.
use ases_resource_control::{
    now, AdvisoryNextStep, BeginLaunchResult, Claim, Environment, LaunchExitObservation,
    LaunchObservation, Meter, ProcessExitStatus, ProcessIdentity, Proposal,
    RecordLaunchExitResult, RecordLaunchObservationResult, ResumeLaunchProfile,
    RecordedJobState, Store,
};
use ases_resource_control::catalog::Account;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::os::unix::process::ExitStatusExt;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, ExitStatus, Stdio};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
struct WorkerEvidence {
    pid: u32,
    start_token: String,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
struct WaitEvidence {
    process: ProcessIdentity,
    status: ProcessExitStatus,
    raw_code: Option<i32>,
    raw_signal: Option<i32>,
    controller_pid: u32,
    worker_pid: u32,
}

fn account() -> Account {
    Account {
        id: "term-account".into(), provider: "local".into(), payer_ref: "local-test".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec!["term-project".into()],
        source: "synthetic-native-termination-test".into(), observed_at: now(), ttl_seconds: 3600,
    }
}

fn meter() -> Meter {
    Meter {
        id: "term-meter".into(), account: "term-account".into(), provider: "local".into(),
        product: "fixed-test-worker".into(), period: "termination-test".into(), unit: "units".into(),
        limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-termination-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false,
    }
}

fn environment() -> Environment {
    Environment {
        id: "term-env".into(), account: "term-account".into(), provider: "local".into(),
        max_parallel: 1, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-termination-test".into(),
    }
}

fn proposal(job: &str) -> Proposal {
    Proposal {
        job_id: job.into(), account_id: "term-account".into(), project_id: "term-project".into(),
        environment_id: "term-env".into(), estimated_wall_seconds: 300,
        claims: vec![Claim { meter_id: "term-meter".into(), amount: 50 }],
        paid_spend_cap_micros: None, paid_spend_cap_currency: None, forecast_context: None,
    }
}

fn setup(dir: &Path, job: &str) -> (PathBuf, i64) {
    let db = dir.join("control.sqlite");
    let mut store = Store::open(&db).unwrap();
    store.register_account(&account()).unwrap();
    store.register_meter(&meter()).unwrap();
    store.register_environment(&environment()).unwrap();
    let revision = store.catalog_version().unwrap();
    let p = proposal(job);
    store.reserve(&p, revision, now()).unwrap();
    store.acknowledge(job, &format!("ack-{job}"), revision, now()).unwrap();
    drop(store);
    (db, revision)
}

fn begin(store: &mut Store, job: &str, launch: &str, revision: i64) {
    assert!(matches!(store.begin_launch(job, launch, revision, now()).unwrap(),
        BeginLaunchResult::DispatchGranted(_)));
}

fn process_start_token(pid: u32) -> String {
    let stat = fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap().to_string()
}

fn worker_alive(identity: &ProcessIdentity) -> bool {
    let Ok(stat) = fs::read_to_string(format!("/proc/{}/stat", identity.pid)) else { return false };
    let Some((_, tail)) = stat.rsplit_once(") ") else { return false };
    let mut fields = tail.split_whitespace();
    let Some(state) = fields.next().and_then(|v| v.chars().next()) else { return false };
    let Some(token) = fields.nth(18) else { return false };
    matches!(state, 'R' | 'S') && token == identity.start_token
}

fn worker_test_child(marker: &Path, release: &Path, mode: &str) -> Child {
    Command::new(std::env::current_exe().unwrap())
        .args(["--exact", "termination_fixed_worker", "--nocapture"])
        .env("ASES_TERMINATION_WORKER_MODE", mode)
        .env("ASES_TERMINATION_MARKER", marker)
        .env("ASES_TERMINATION_RELEASE", release)
        .stdout(Stdio::null()).stderr(Stdio::null()).spawn().unwrap()
}

fn wait_for(path: &Path) {
    let until = Instant::now() + Duration::from_secs(10);
    while Instant::now() < until {
        if path.exists() { return; }
        thread::sleep(Duration::from_millis(10));
    }
    panic!("native worker/controller did not reach gate: {}", path.display());
}

fn read_worker(path: &Path) -> WorkerEvidence {
    serde_json::from_slice(&fs::read(path).unwrap()).unwrap()
}

fn identity(worker: &WorkerEvidence) -> ProcessIdentity {
    ProcessIdentity { pid: worker.pid, start_token: worker.start_token.clone() }
}

struct Release(PathBuf);
impl Drop for Release { fn drop(&mut self) { let _ = fs::write(&self.0, b"release\n"); } }

fn status_from_child(status: ExitStatus) -> ProcessExitStatus {
    if let Some(code) = status.code() {
        ProcessExitStatus::Code { code }
    } else {
        ProcessExitStatus::Signal { signal: status.signal().expect("unix child exit has code or signal") }
    }
}

fn balances(store: &mut Store) -> Vec<(String, i64, i64)> {
    store.balances(now()).unwrap().into_iter()
        .map(|b| (b.meter_id, b.active_reserved_remaining, b.available)).collect()
}

fn persist(name: &str, value: Value) {
    if let Some(dir) = std::env::var_os("ASES_TERMINATION_EVIDENCE_DIR") {
        let dir = PathBuf::from(dir);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join(name), serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

fn source_hashes() -> Value {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut result = serde_json::Map::new();
    for relative in ["src/lib.rs", "tests/native_launch.rs", "tests/resume_view.rs", "tests/native_termination.rs"] {
        let digest = Sha256::digest(fs::read(root.join(relative)).unwrap());
        result.insert(relative.into(), json!(format!("{digest:x}")));
    }
    Value::Object(result)
}

// This test is launched only by the fixed helper/controller test below.
#[test]
fn termination_fixed_worker() {
    let Ok(mode) = std::env::var("ASES_TERMINATION_WORKER_MODE") else { return };
    let marker = PathBuf::from(std::env::var_os("ASES_TERMINATION_MARKER").unwrap());
    let release = PathBuf::from(std::env::var_os("ASES_TERMINATION_RELEASE").unwrap());
    let evidence = WorkerEvidence { pid: std::process::id(), start_token: process_start_token(std::process::id()) };
    let mut file = OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file, &evidence).unwrap();
    file.write_all(b"\n").unwrap();
    file.sync_all().unwrap();
    if mode == "hold" {
        let until = Instant::now() + Duration::from_secs(20);
        while !release.exists() && Instant::now() < until { thread::sleep(Duration::from_millis(10)); }
        std::process::exit(0);
    }
    let code = mode.strip_prefix("exit-").unwrap().parse::<i32>().unwrap();
    std::process::exit(code);
}

#[test]
fn native_termination_controller_helper() {
    if std::env::var("ASES_TERMINATION_CONTROLLER_MODE").as_deref() != Ok("wait-before-observe") { return; }
    let db = PathBuf::from(std::env::var_os("ASES_TERMINATION_DB").unwrap());
    let marker = PathBuf::from(std::env::var_os("ASES_TERMINATION_MARKER").unwrap());
    let release = PathBuf::from(std::env::var_os("ASES_TERMINATION_RELEASE").unwrap());
    let waited = PathBuf::from(std::env::var_os("ASES_TERMINATION_WAITED").unwrap());
    let gate = PathBuf::from(std::env::var_os("ASES_TERMINATION_GATE").unwrap());
    let mut store = Store::open(&db).unwrap();
    let revision = store.catalog_version().unwrap();
    begin(&mut store, "waited-job", "waited-launch", revision);
    let mut child = worker_test_child(&marker, &release, "hold");
    wait_for(&marker);
    let worker = read_worker(&marker);
    let process = identity(&worker);
    assert_eq!(store.observe_launch("waited-job", "waited-launch",
        &LaunchObservation::Started { process: process.clone() }, now()).unwrap(),
        RecordLaunchObservationResult::Started);
    fs::write(&release, b"release\n").unwrap();
    let wait_status = child.wait().unwrap();
    let typed_status = status_from_child(wait_status);
    let evidence = WaitEvidence { process, status: typed_status,
        raw_code: wait_status.code(), raw_signal: wait_status.signal(),
        controller_pid: std::process::id(), worker_pid: worker.pid };
    fs::write(&waited, serde_json::to_vec_pretty(&evidence).unwrap()).unwrap();
    fs::write(&gate, b"child-wait-returned-exit-not-yet-recorded\n").unwrap();
    // Parent kills this exact controller after its Child::wait and before it
    // can call observe_launch_exit; EOF is only a bounded harness escape.
    let mut line = String::new();
    let _ = std::io::stdin().read_to_string(&mut line);
}

#[test]
fn finalize_while_owned_fixed_worker_is_live_never_releases_slot() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), "live-job");
    let mut store = Store::open(&db).unwrap();
    begin(&mut store, "live-job", "live-launch", revision);
    let marker = dir.path().join("live-worker.json");
    let release = dir.path().join("live-worker.release");
    let _release = Release(release.clone());
    let mut child = worker_test_child(&marker, &release, "hold");
    wait_for(&marker);
    let worker = read_worker(&marker);
    let process = identity(&worker);
    assert!(worker_alive(&process), "exact child identity must still be live before finalization attempts");
    assert_eq!(store.observe_launch("live-job", "live-launch",
        &LaunchObservation::Started { process: process.clone() }, now()).unwrap(),
        RecordLaunchObservationResult::Started);
    let events_before = store.event_log(Some("live-job")).unwrap();
    let balances_before = balances(&mut store);
    let job_before = store.job("live-job").unwrap();
    let mut terminal_results = Vec::new();
    for outcome in ["cancelled", "completed", "failed", "interrupted"] {
        terminal_results.push((outcome.to_string(), store.finalize("live-job", outcome, now()).unwrap_err().to_string()));
        assert_eq!(store.job("live-job").unwrap(), job_before);
        assert_eq!(balances(&mut store), balances_before);
        assert_eq!(store.event_log(Some("live-job")).unwrap(), events_before);
        assert!(worker_alive(&process), "rejected finalize must not stop or adopt the child");
    }
    let second = proposal("occupied-slot-job");
    assert!(store.reserve(&second, revision, now()).is_err(),
        "another job cannot acquire the one occupied environment slot/reservation");
    assert_eq!(store.event_log(None).unwrap().iter().filter(|e| e["job_id"]=="occupied-slot-job").count(), 0);
    fs::write(&release, b"release\n").unwrap();
    let child_status = child.wait().unwrap();
    assert_eq!(child_status.code(), Some(0));
    persist("live-finalize-rejections.json", json!({
        "source_sha256":source_hashes(),"job_before":job_before,"events_before":events_before,
        "balances_before":balances_before,"worker":worker,"worker_alive_during_rejections":true,
        "terminal_rejections":terminal_results,"second_reservation_rejected":true,
        "worker_child_wait_code":child_status.code(),"events_after":store.event_log(Some("live-job")).unwrap(),
        "balances_after":balances(&mut store)
    }));
}

#[test]
fn waited_exit_observation_is_durable_separate_and_releases_capacity_only_on_finalize() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), "exit-job");
    let mut store = Store::open(&db).unwrap();
    begin(&mut store, "exit-job", "exit-launch", revision);
    let marker=dir.path().join("exit-worker.json");
    let release=dir.path().join("exit-worker.release");
    let _release=Release(release.clone());
    let mut child=worker_test_child(&marker,&release,"hold");
    wait_for(&marker);
    let worker=read_worker(&marker);
    let process=identity(&worker);
    store.observe_launch("exit-job","exit-launch",&LaunchObservation::Started{process:process.clone()},now()).unwrap();
    let balances_before_exit=balances(&mut store);
    let events_before_exit=store.event_log(Some("exit-job")).unwrap();
    for label in ["cancelled","completed","failed","interrupted"] {
        assert!(store.finalize("exit-job",label,now()).is_err());
    }
    fs::write(&release,b"release\n").unwrap();
    let child_status=child.wait().unwrap();
    let exit=LaunchExitObservation{process:process.clone(),status:status_from_child(child_status)};
    assert_eq!(exit.status,ProcessExitStatus::Code{code:0});
    assert_eq!(store.observe_launch_exit("exit-job","exit-launch",&exit,now()).unwrap(),RecordLaunchExitResult::Recorded);
    assert_eq!(store.job("exit-job").unwrap()["state"],"RUNNING");
    assert_eq!(balances(&mut store),balances_before_exit,"observing exit does not release capacity");
    let after_exit=store.event_log(Some("exit-job")).unwrap();
    assert_eq!(after_exit.iter().filter(|e|e["kind"]=="LAUNCH_EXIT_OBSERVED").count(),1);
    assert!(after_exit.len()>events_before_exit.len());
    drop(store);

    let mut cold=Store::open(&db).unwrap();
    assert_eq!(cold.observe_launch_exit("exit-job","exit-launch",&exit,now()).unwrap(),RecordLaunchExitResult::Replay);
    let view=cold.resume_view("exit-job").unwrap();
    assert_eq!(view.state,RecordedJobState::Running);
    assert_eq!(view.profile,ResumeLaunchProfile::Intent);
    assert_eq!(view.present_liveness,ases_resource_control::PresentLiveness::Unknown);
    assert_eq!(view.advisory_next_step,AdvisoryNextStep::FinalizeObservedExit);
    assert_eq!(view.evidence.outcome.as_ref().unwrap().kind,"LAUNCH_EXIT_OBSERVED");
    let projection=serde_json::to_vec(&view).unwrap();
    assert!(projection.len()<=2048,"termination evidence view {} bytes",projection.len());
    let exit_event=cold.event_log(Some("exit-job")).unwrap().into_iter()
        .find(|e|e["kind"]=="LAUNCH_EXIT_OBSERVED").unwrap();
    assert_eq!(exit_event["event_id"],"launch-exit:exit-job");
    assert_eq!(exit_event["payload"]["launch_id"],"exit-launch");
    assert_eq!(exit_event["payload"]["process"],serde_json::to_value(&process).unwrap());
    assert_eq!(exit_event["payload"]["status"],serde_json::to_value(&exit.status).unwrap());
    let event_raw: String = rusqlite::Connection::open(&db).unwrap().query_row(
        "SELECT payload FROM events WHERE id=?1", ["launch-exit:exit-job"], |row| row.get(0)).unwrap();
    assert_eq!(view.evidence.outcome.as_ref().unwrap().payload_sha256,
        format!("{:x}", Sha256::digest(event_raw.as_bytes())));
    let before_read = cold.event_log(Some("exit-job")).unwrap();
    assert_eq!(view, cold.resume_view("exit-job").unwrap(), "view is stable and read-only");
    assert_eq!(before_read, cold.event_log(Some("exit-job")).unwrap(), "view adds no event");
    assert!(matches!(cold.begin_launch("exit-job", "exit-launch", revision, now()).unwrap(),
        BeginLaunchResult::RunningObservation { .. }), "observed exit never grants a second dispatch");
    let final_result=cold.finalize("exit-job","completed",now()).unwrap();
    assert_eq!(final_result,"CLOSED");
    assert_eq!(cold.finalize("exit-job","completed",now()).unwrap(),"CLOSED_REPLAY");
    assert_eq!(cold.observe_launch_exit("exit-job","exit-launch",&exit,now()).unwrap(),RecordLaunchExitResult::Replay);
    let final_events=cold.event_log(Some("exit-job")).unwrap();
    assert_eq!(final_events.iter().filter(|e|e["kind"]=="LAUNCH_EXIT_OBSERVED").count(),1);
    assert_eq!(final_events.iter().filter(|e|e["kind"]=="FINALIZED").count(),1);
    let balances_after_finalize=balances(&mut cold);
    assert!(balances_after_finalize[0].1 < balances_before_exit[0].1,
        "only finalization releases the reservation");
    let next=proposal("next-slot-job");
    cold.reserve(&next,revision,now()).unwrap();
    cold.acknowledge("next-slot-job","ack-next-slot",revision,now()).unwrap();
    assert!(matches!(cold.begin_launch("next-slot-job","next-slot-launch",revision,now()).unwrap(),
        BeginLaunchResult::DispatchGranted(_)));
    persist("observed-exit-finalize.json",json!({
        "source_sha256":source_hashes(),"worker":worker,"child_wait_code":child_status.code(),
        "exit_observation":exit,"events_before_exit":events_before_exit,"events_after_exit":after_exit,
        "exit_event":exit_event,"balances_before_exit":balances_before_exit,
        "balances_after_observation":balances_before_exit,"balances_after_finalize":balances_after_finalize,
        "cold_replay":"Replay","finalize":final_result,"finalize_replay":"CLOSED_REPLAY",
        "resume_view":view,"resume_view_bytes":projection.len(),"next_launch_dispatch_granted":true
    }));
}

#[test]
fn controller_reaped_child_without_recording_exit_stays_unresolved_until_explicit_observation() {
    let dir=tempfile::tempdir().unwrap();
    let (db,_revision)=setup(dir.path(),"waited-job");
    let marker=dir.path().join("waited-worker.json");
    let release=dir.path().join("waited-worker.release");
    let waited=dir.path().join("wait-evidence.json");
    let gate=dir.path().join("controller-after-wait.gate");
    let mut controller=Command::new(std::env::current_exe().unwrap())
        .args(["--exact","native_termination_controller_helper","--nocapture"])
        .env("ASES_TERMINATION_CONTROLLER_MODE","wait-before-observe")
        .env("ASES_TERMINATION_DB",&db).env("ASES_TERMINATION_MARKER",&marker)
        .env("ASES_TERMINATION_RELEASE",&release).env("ASES_TERMINATION_WAITED",&waited)
        .env("ASES_TERMINATION_GATE",&gate).stdin(Stdio::piped()).stdout(Stdio::null())
        .stderr(Stdio::null()).spawn().unwrap();
    let controller_pid=controller.id();
    wait_for(&gate);
    let raw_wait:WaitEvidence=serde_json::from_slice(&fs::read(&waited).unwrap()).unwrap();
    assert_eq!(raw_wait.raw_code,Some(0));
    assert_eq!(raw_wait.raw_signal,None);
    assert_eq!(raw_wait.controller_pid,controller_pid);
    assert_eq!(raw_wait.process.pid,raw_wait.worker_pid);
    controller.kill().unwrap();
    let controller_status=controller.wait().unwrap();
    assert_eq!(controller_status.signal(),Some(9));

    let mut cold=Store::open(&db).unwrap();
    let before_events=cold.event_log(Some("waited-job")).unwrap();
    assert_eq!(before_events.iter().filter(|e|e["kind"]=="LAUNCH_EXIT_OBSERVED").count(),0);
    let before_view=cold.resume_view("waited-job").unwrap();
    assert!(matches!(before_view.advisory_next_step,
        AdvisoryNextStep::ObserveProcessOrCompletion));
    let before_balances=balances(&mut cold);
    for label in ["cancelled","completed","failed","interrupted"] {
        assert!(cold.finalize("waited-job",label,now()).is_err(),
            "controller's wait evidence is not durable until explicitly supplied");
    }
    assert_eq!(before_events,cold.event_log(Some("waited-job")).unwrap());
    assert_eq!(before_balances,balances(&mut cold));
    let exit=LaunchExitObservation{process:raw_wait.process.clone(),status:raw_wait.status.clone()};
    assert_eq!(cold.observe_launch_exit("waited-job","waited-launch",&exit,now()).unwrap(),RecordLaunchExitResult::Recorded);
    let after_observation=cold.resume_view("waited-job").unwrap();
    assert_eq!(after_observation.advisory_next_step,AdvisoryNextStep::FinalizeObservedExit);
    assert_eq!(cold.finalize("waited-job","failed",now()).unwrap(),"CLOSED");
    persist("controller-wait-before-observe.json",json!({
        "source_sha256":source_hashes(),"controller_pid":controller_pid,
        "controller_exit_signal":controller_status.signal(),"gate":fs::read_to_string(gate).unwrap(),
        "raw_child_wait":raw_wait,"exit_event_absent_before_reopen":true,
        "resume_before_observation":before_view,
        "finalize_rejections_before_observation":["cancelled","completed","failed","interrupted"],
        "explicit_observation":"Recorded","final_resume_view":after_observation
    }));
}

#[test]
fn signal_exit_comes_only_from_exact_owned_child_and_keeps_signal_typed() {
    let dir=tempfile::tempdir().unwrap();
    let (db,revision)=setup(dir.path(),"signal-job");
    let mut store=Store::open(&db).unwrap();
    begin(&mut store,"signal-job","signal-launch",revision);
    let marker=dir.path().join("signal-worker.json");
    let release=dir.path().join("signal-worker.release");
    let mut child=worker_test_child(&marker,&release,"hold");
    wait_for(&marker);
    let worker=read_worker(&marker);
    let process=identity(&worker);
    store.observe_launch("signal-job","signal-launch",&LaunchObservation::Started{process:process.clone()},now()).unwrap();
    assert!(worker_alive(&process));
    child.kill().unwrap(); // Exact std::process::Child handle; no arbitrary PID is signalled.
    let child_status=child.wait().unwrap();
    assert_eq!(child_status.signal(),Some(9));
    let exit=LaunchExitObservation{process:process.clone(),status:ProcessExitStatus::Signal{signal:9}};
    assert_eq!(store.observe_launch_exit("signal-job","signal-launch",&exit,now()).unwrap(),RecordLaunchExitResult::Recorded);
    let event=store.event_log(Some("signal-job")).unwrap().into_iter()
        .find(|e|e["kind"]=="LAUNCH_EXIT_OBSERVED").unwrap();
    assert_eq!(event["payload"]["status"],serde_json::to_value(&exit.status).unwrap());
    assert_eq!(store.resume_view("signal-job").unwrap().advisory_next_step,AdvisoryNextStep::FinalizeObservedExit);
    store.finalize("signal-job","interrupted",now()).unwrap();
    persist("signal-exit.json",json!({"worker":worker,"exact_child_kill":true,
        "child_wait_signal":child_status.signal(),"exit_observation":exit,"event":event}));
}

#[test]
fn wrong_identity_status_profile_and_pending_exit_observations_are_atomic() {
    let dir=tempfile::tempdir().unwrap();
    let (db,revision)=setup(dir.path(),"control-job");
    let mut store=Store::open(&db).unwrap();
    begin(&mut store,"control-job","control-launch",revision);
    let code0=LaunchExitObservation{process:ProcessIdentity{pid:1234,start_token:"synthetic-token".into()},
        status:ProcessExitStatus::Code{code:0}};
    assert!(store.observe_launch_exit("control-job","control-launch",&code0,now()).is_err(),
        "pending/no-start exit cannot close unknown creation result");
    assert!(store.observe_launch_exit("control-job","wrong-launch",&code0,now()).is_err());
    let process=code0.process.clone();
    store.observe_launch("control-job","control-launch",&LaunchObservation::Started{process:process.clone()},now()).unwrap();
    let started_events=store.event_log(Some("control-job")).unwrap();
    let started_balances=balances(&mut store);
    assert!(store.observe_launch_exit("control-job","wrong-launch",&code0,now()).is_err());
    let wrong_pid=LaunchExitObservation{process:ProcessIdentity{pid:process.pid+1,start_token:process.start_token.clone()},
        status:ProcessExitStatus::Code{code:0}};
    assert!(store.observe_launch_exit("control-job","control-launch",&wrong_pid,now()).is_err());
    let wrong_token=LaunchExitObservation{process:ProcessIdentity{pid:process.pid,start_token:"other-token".into()},
        status:ProcessExitStatus::Code{code:0}};
    assert!(store.observe_launch_exit("control-job","control-launch",&wrong_token,now()).is_err());
    assert!(store.observe_launch_exit("control-job","control-launch",&LaunchExitObservation{
        process:process.clone(),status:ProcessExitStatus::Code{code:256}},now()).is_err());
    assert!(store.observe_launch_exit("control-job","control-launch",&LaunchExitObservation{
        process:process.clone(),status:ProcessExitStatus::Signal{signal:0}},now()).is_err());
    assert!(store.observe_launch_exit("control-job","control-launch",&LaunchExitObservation{
        process:process.clone(),status:ProcessExitStatus::Signal{signal:65}},now()).is_err());
    assert_eq!(started_events,store.event_log(Some("control-job")).unwrap());
    assert_eq!(started_balances,balances(&mut store));

    let exact=LaunchExitObservation{process:process.clone(),status:ProcessExitStatus::Code{code:0}};
    assert_eq!(store.observe_launch_exit("control-job","control-launch",&exact,now()).unwrap(),RecordLaunchExitResult::Recorded);
    let recorded=store.event_log(Some("control-job")).unwrap();
    assert_eq!(recorded.iter().filter(|e|e["kind"]=="LAUNCH_EXIT_OBSERVED").count(),1);
    assert_eq!(store.observe_launch_exit("control-job","control-launch",&exact,now()).unwrap(),RecordLaunchExitResult::Replay);
    let changed_status=LaunchExitObservation{process:process.clone(),status:ProcessExitStatus::Code{code:1}};
    assert!(store.observe_launch_exit("control-job","control-launch",&changed_status,now()).is_err());
    assert!(store.observe_launch_exit("control-job","control-launch",&wrong_pid,now()).is_err());
    assert_eq!(recorded,store.event_log(Some("control-job")).unwrap());

    let mock_dir=tempfile::tempdir().unwrap();
    let (mock_db,_mock_revision)=setup(mock_dir.path(),"mock-job");
    let mut mock_store=Store::open(mock_db).unwrap();
    mock_store.launch_mock("mock-job","mock-launch",now()).unwrap();
    let mock_events=mock_store.event_log(Some("mock-job")).unwrap();
    assert!(mock_store.observe_launch_exit("mock-job","mock-launch",&exact,now()).is_err());
    assert_eq!(mock_events,mock_store.event_log(Some("mock-job")).unwrap());

    store.finalize("control-job","completed",now()).unwrap();
    assert_eq!(store.observe_launch_exit("control-job","control-launch",&exact,now()).unwrap(),RecordLaunchExitResult::Replay,
        "exact exit replay remains observational after finalization");
    assert!(store.observe_launch_exit("control-job","control-launch",&changed_status,now()).is_err());
    assert_eq!(recorded.len()+1,store.event_log(Some("control-job")).unwrap().len());
}

#[test]
fn compact_resume_view_requires_typed_exit_and_closed_intent_exit_evidence() {
    let dir=tempfile::tempdir().unwrap();
    let (db,revision)=setup(dir.path(),"view-job");
    let mut store=Store::open(&db).unwrap();
    begin(&mut store,"view-job","view-launch",revision);
    let process=ProcessIdentity{pid:9876,start_token:"view-token".into()};
    store.observe_launch("view-job","view-launch",&LaunchObservation::Started{process:process.clone()},now()).unwrap();
    let started=store.resume_view("view-job").unwrap();
    assert_eq!(started.present_liveness,ases_resource_control::PresentLiveness::Unknown);
    assert_eq!(started.advisory_next_step,AdvisoryNextStep::ObserveProcessOrCompletion);
    let exit=LaunchExitObservation{process,status:ProcessExitStatus::Code{code:2}};
    store.observe_launch_exit("view-job","view-launch",&exit,now()).unwrap();
    let view=store.resume_view("view-job").unwrap();
    assert_eq!(view.advisory_next_step,AdvisoryNextStep::FinalizeObservedExit);
    assert_eq!(view.present_liveness,ases_resource_control::PresentLiveness::Unknown);
    assert_eq!(view.evidence.outcome.as_ref().unwrap().kind,"LAUNCH_EXIT_OBSERVED");
    let bytes=serde_json::to_vec(&view).unwrap();
    assert!(bytes.len()<=2048);
    store.finalize("view-job","failed",now()).unwrap();
    let closed=store.resume_view("view-job").unwrap();
    assert_eq!(closed.state,RecordedJobState::Closed);
    assert_eq!(closed.evidence.outcome.as_ref().unwrap().kind,"FINALIZED");
    drop(store);

    let conn=rusqlite::Connection::open(&db).unwrap();
    conn.execute("DELETE FROM events WHERE id='launch-exit:view-job'",[]).unwrap();
    let cold=Store::open(&db).unwrap();
    assert!(cold.resume_view("view-job").is_err(),"CLOSED intent after start without exit evidence refuses interpretation");
    drop(cold);
    let valid_exit=json!({"launch_id":"view-launch","process":{"pid":9876,"start_token":"view-token"},
        "status":serde_json::to_value(&exit.status).unwrap()});
    conn.execute("INSERT INTO events(id,job_id,kind,at,payload) VALUES (?1,?2,'LAUNCH_EXIT_OBSERVED',?3,?4)",
        ("launch-exit:view-job","view-job",now(),valid_exit.to_string())).unwrap();
    assert!(Store::open(&db).unwrap().resume_view("view-job").is_ok(),"exact exit evidence restores interpretation");
    let invalid_status=json!({"launch_id":"view-launch","process":{"pid":9876,"start_token":"view-token"},
        "status":{"kind":"code","code":256}});
    conn.execute("UPDATE events SET payload=?1 WHERE id='launch-exit:view-job'",[invalid_status.to_string()]).unwrap();
    assert!(Store::open(&db).unwrap().resume_view("view-job").is_err(),"out-of-bounds exit status refuses interpretation");
    let wrong_process=json!({"launch_id":"view-launch","process":{"pid":9877,"start_token":"view-token"},
        "status":serde_json::to_value(&exit.status).unwrap()});
    conn.execute("UPDATE events SET payload=?1 WHERE id='launch-exit:view-job'",[wrong_process.to_string()]).unwrap();
    assert!(Store::open(&db).unwrap().resume_view("view-job").is_err(),"exit process mismatch refuses interpretation");
    let wrong_launch=json!({"launch_id":"wrong-launch","process":{"pid":9876,"start_token":"view-token"},
        "status":serde_json::to_value(&exit.status).unwrap()});
    conn.execute("UPDATE events SET payload=?1 WHERE id='launch-exit:view-job'",[wrong_launch.to_string()]).unwrap();
    assert!(Store::open(&db).unwrap().resume_view("view-job").is_err(),"conflicting exit launch identity refuses interpretation");
    persist("resume-exit-view.json",json!({"resume_view":view,"resume_view_bytes":bytes.len(),
        "closed_view":closed,"missing_exit_refused":true,"conflicting_exit_refused":true,
        "present_liveness":"unknown","projection_is_serialize_only":true}));
}
