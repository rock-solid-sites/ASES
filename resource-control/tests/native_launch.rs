//! Native local-process crash boundaries for the opt-in launch-intent API.
//! Both controller and worker are this fixed test binary; no shell or caller
//! supplied executable is invoked.
use ases_resource_control::{
    now, BeginLaunchResult, Claim, Environment, LaunchObservation, Meter,
    ProcessIdentity, Proposal, RecordLaunchObservationResult, Store,
};
use ases_resource_control::catalog::Account;
use serde::{Deserialize, Serialize};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::os::unix::process::ExitStatusExt;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};
use tempfile::TempDir;

#[derive(Debug, Serialize, Deserialize)]
struct WorkerEvidence {
    pid: u32,
    start_token: String,
}

fn proposal(job_id: &str) -> Proposal {
    Proposal {
        job_id: job_id.into(), account_id: "acct-native".into(),
        project_id: "project-native".into(), environment_id: "env-native".into(),
        estimated_wall_seconds: 300,
        claims: vec![Claim { meter_id: "meter-native".into(), amount: 50 }],
        paid_spend_cap_micros: None, paid_spend_cap_currency: None,
        forecast_context: None,
    }
}

fn setup(dir: &Path, job_id: &str) -> (PathBuf, i64) {
    let db = dir.join("control.sqlite");
    let mut store = Store::open(&db).unwrap();
    store.register_account(&Account {
        id: "acct-native".into(), provider: "local".into(), payer_ref: "local-test".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec!["project-native".into()],
        source: "synthetic-native-test".into(), observed_at: now(), ttl_seconds: 3600,
    }).unwrap();
    store.register_meter(&Meter {
        id: "meter-native".into(), account: "acct-native".into(), provider: "local".into(),
        product: "fixed-worker".into(), period: "test-period".into(), unit: "worker-units".into(),
        limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false,
    }).unwrap();
    store.register_environment(&Environment {
        id: "env-native".into(), account: "acct-native".into(), provider: "local".into(),
        max_parallel: 1, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-test".into(),
    }).unwrap();
    let p = proposal(job_id);
    let revision = store.catalog_version().unwrap();
    store.reserve(&p, revision, now()).unwrap();
    store.acknowledge(job_id, "native-ack", revision, now()).unwrap();
    drop(store);
    (db, revision)
}

fn process_start_token(pid: u32) -> String {
    let stat = fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let tail = stat.rsplit_once(") ").unwrap().1;
    tail.split_whitespace().nth(19).unwrap().to_string()
}

fn process_state(pid: u32) -> Option<(char, String)> {
    let stat = fs::read_to_string(format!("/proc/{pid}/stat")).ok()?;
    let tail = stat.rsplit_once(") ")?.1;
    let mut fields = tail.split_whitespace();
    let state = fields.next()?.chars().next()?;
    let start_token = fields.nth(18)?.to_string();
    Some((state, start_token))
}

fn wait_for_file(path: &Path) {
    let until = Instant::now() + Duration::from_secs(10);
    while Instant::now() < until {
        if path.exists() { return; }
        thread::sleep(Duration::from_millis(10));
    }
    panic!("controller did not reach its durable gate: {}", path.display());
}

fn source_hashes() -> serde_json::Value {
    let root=PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut hashes=serde_json::Map::new();
    for relative in ["src/lib.rs","tests/control.rs","tests/native_launch.rs"] {
        let bytes=fs::read(root.join(relative)).unwrap();
        let digest=Sha256::digest(bytes);
        hashes.insert(relative.into(),json!(format!("{digest:x}")));
    }
    json!(hashes)
}

fn persist_evidence(name:&str,value:serde_json::Value) {
    if let Some(root)=std::env::var_os("ASES_LAUNCH_EVIDENCE_DIR") {
        let root=PathBuf::from(root);
        fs::create_dir_all(&root).unwrap();
        fs::write(root.join(name),serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

struct ReleaseWorker(PathBuf);
impl Drop for ReleaseWorker {
    fn drop(&mut self) { let _=fs::write(&self.0,b"release\n"); }
}

fn controller_helper() {
    let mode = std::env::var("ASES_LAUNCH_HELPER_MODE").unwrap_or_default();
    if mode != "before-spawn" && mode != "after-spawn" { return; }
    let db = std::env::var_os("ASES_LAUNCH_HELPER_DB").unwrap();
    let gate = PathBuf::from(std::env::var_os("ASES_LAUNCH_HELPER_GATE").unwrap());
    let marker = PathBuf::from(std::env::var_os("ASES_LAUNCH_HELPER_MARKER").unwrap());
    let release = PathBuf::from(std::env::var_os("ASES_LAUNCH_HELPER_RELEASE").unwrap());
    let mut store = Store::open(db).unwrap();
    let revision = store.catalog_version().unwrap();
    let permit = store.begin_launch("native-job", "native-launch", revision, now()).unwrap();
    assert!(matches!(permit, BeginLaunchResult::DispatchGranted(_)));

    if mode == "after-spawn" {
        // Fixed harmless worker: this exact test binary runs one marker-writing
        // test. No executable or argument is accepted from a request.
        let _worker = Command::new(std::env::current_exe().unwrap())
            .args(["--exact", "native_fixed_worker", "--nocapture"])
            .env("ASES_LAUNCH_HELPER_MODE", "worker")
            .env("ASES_LAUNCH_HELPER_MARKER", &marker)
            .env("ASES_LAUNCH_HELPER_RELEASE", &release)
            .stdout(Stdio::null()).stderr(Stdio::null())
            .spawn().unwrap();
        let until = Instant::now() + Duration::from_secs(10);
        while !marker.exists() && Instant::now() < until { thread::sleep(Duration::from_millis(10)); }
        assert!(marker.exists(), "fixed worker did not write its start evidence");
    }
    fs::write(gate, if mode == "before-spawn" { "intent-durable" } else { "worker-spawned" }).unwrap();
    // Parent test kills this controller at the gate. It has not recorded an
    // outcome observation; EOF is also a test harness escape hatch.
    let mut line = String::new();
    let _ = std::io::stdin().read_line(&mut line);
}

#[test]
fn native_controller_helper() { controller_helper(); }

#[test]
fn native_fixed_worker() {
    if std::env::var("ASES_LAUNCH_HELPER_MODE").as_deref() != Ok("worker") { return; }
    let marker = PathBuf::from(std::env::var_os("ASES_LAUNCH_HELPER_MARKER").unwrap());
    let release = PathBuf::from(std::env::var_os("ASES_LAUNCH_HELPER_RELEASE").unwrap());
    let evidence = WorkerEvidence { pid: std::process::id(), start_token: process_start_token(std::process::id()) };
    let mut file = OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file, &evidence).unwrap();
    file.write_all(b"\n").unwrap();
    file.sync_all().unwrap();
    // Survive controller death until the parent writes the scoped cleanup file,
    // but never outlive a failed harness indefinitely.
    let until=Instant::now()+Duration::from_secs(10);
    while !release.exists() && Instant::now()<until { thread::sleep(Duration::from_millis(10)); }
}

fn launch_controller(dir: &TempDir, db: &Path, mode: &str) -> (std::process::Child, PathBuf, PathBuf, PathBuf) {
    let gate = dir.path().join("controller.gate");
    let marker = dir.path().join("worker-starts.jsonl");
    let release = dir.path().join("worker.release");
    let child = Command::new(std::env::current_exe().unwrap())
        .args(["--exact", "native_controller_helper", "--nocapture"])
        .env("ASES_LAUNCH_HELPER_MODE", mode)
        .env("ASES_LAUNCH_HELPER_DB", db)
        .env("ASES_LAUNCH_HELPER_GATE", &gate)
        .env("ASES_LAUNCH_HELPER_MARKER", &marker)
        .env("ASES_LAUNCH_HELPER_RELEASE", &release)
        .stdin(Stdio::piped()).stdout(Stdio::null()).stderr(Stdio::null())
        .spawn().unwrap();
    (child, gate, marker, release)
}

#[test]
fn controller_kill_before_spawn_reopens_as_pending_without_redispatch() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), "native-job");
    let (mut child, gate, marker, release) = launch_controller(&dir, &db, "before-spawn");
    let _release=ReleaseWorker(release);
    let controller_pid=child.id();
    wait_for_file(&gate);
    child.kill().unwrap();
    let controller_exit=child.wait().unwrap();
    assert!(!marker.exists(), "worker must not have spawned before the gate");

    let mut reopened = Store::open(&db).unwrap();
    assert_eq!(reopened.begin_launch("native-job", "native-launch", revision, now()).unwrap(),
        BeginLaunchResult::PendingObservation { job_id: "native-job".into(), launch_id: "native-launch".into() });
    assert_eq!(reopened.begin_launch("native-job", "native-launch", revision, now()).unwrap(),
        BeginLaunchResult::PendingObservation { job_id: "native-job".into(), launch_id: "native-launch".into() });
    assert!(reopened.finalize("native-job", "cancelled", now()).is_err());
    assert_eq!(reopened.job("native-job").unwrap()["state"], "LAUNCHING");
    let balances=reopened.balances(now()).unwrap();
    let events=reopened.event_log(Some("native-job")).unwrap();
    persist_evidence("before-spawn-kill.json",json!({
        "source_pin":"1fd05d896dde11f185610a4718c1245cfad1ffca",
        "source_sha256":source_hashes(),"controller_pid":controller_pid,
        "controller_kill_signal":controller_exit.signal(),"gate":fs::read_to_string(gate).unwrap(),
        "worker_marker_exists":marker.exists(),"reopen_begin_result":"PendingObservation",
        "finalize_attempt":"rejected","job":reopened.job("native-job").unwrap(),
        "balances":balances,"events":events
    }));
}

#[test]
fn controller_kill_after_fixed_worker_spawn_reopens_pending_until_observed() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), "native-job");
    let (mut child, gate, marker, release) = launch_controller(&dir, &db, "after-spawn");
    let _release=ReleaseWorker(release.clone());
    let controller_pid=child.id();
    wait_for_file(&gate);
    child.kill().unwrap();
    let controller_exit=child.wait().unwrap();

    let records = fs::read_to_string(&marker).unwrap();
    let lines: Vec<_> = records.lines().collect();
    assert_eq!(lines.len(), 1, "exactly one fixed worker process started");
    let worker: WorkerEvidence = serde_json::from_str(lines[0]).unwrap();
    assert_ne!(worker.pid, 0);
    assert!(!worker.start_token.is_empty());
    assert!(matches!(process_state(worker.pid),Some((state,ref token))
        if matches!(state,'R'|'S') && token==&worker.start_token),
        "fixed worker must still be alive after its controller is killed");

    let mut reopened = Store::open(&db).unwrap();
    assert_eq!(reopened.begin_launch("native-job", "native-launch", revision, now()).unwrap(),
        BeginLaunchResult::PendingObservation { job_id: "native-job".into(), launch_id: "native-launch".into() });
    assert_eq!(fs::read_to_string(&marker).unwrap().lines().count(), 1,
        "pending observation must not spawn a second worker");
    fs::write(&release,b"release\n").unwrap(); // Scoped file gate releases worker; no PID signal is used.
    let until = Instant::now() + Duration::from_secs(10);
    loop {
        match process_state(worker.pid) {
            None | Some(('Z', _)) => break,
            Some((_, ref token)) if token != &worker.start_token => break,
            _ if Instant::now() < until => thread::sleep(Duration::from_millis(10)),
            state => panic!("fixed worker cleanup timed out: {state:?}"),
        }
    }
    assert_eq!(reopened.observe_launch("native-job", "native-launch",
        &LaunchObservation::Started { process: ProcessIdentity { pid: worker.pid, start_token: worker.start_token.clone() } }, now()).unwrap(),
        RecordLaunchObservationResult::Started);
    assert!(matches!(reopened.begin_launch("native-job", "native-launch", revision, now()).unwrap(),
        BeginLaunchResult::RunningObservation { .. }));
    let balances=reopened.balances(now()).unwrap();
    let events=reopened.event_log(Some("native-job")).unwrap();
    persist_evidence("after-worker-spawn-kill.json",json!({
        "source_pin":"1fd05d896dde11f185610a4718c1245cfad1ffca",
        "source_sha256":source_hashes(),"controller_pid":controller_pid,
        "controller_kill_signal":controller_exit.signal(),"gate":fs::read_to_string(gate).unwrap(),
        "worker_start_count":lines.len(),"worker_alive_at_controller_kill":true,
        "worker_identity":worker,"worker_exit_observed_after_release_file":true,
        "pending_reopen_did_not_spawn_again":true,"observation":"Started",
        "job":reopened.job("native-job").unwrap(),"balances":balances,"events":events
    }));
}
