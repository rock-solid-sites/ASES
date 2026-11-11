//! Bounded native session consumer histories through resource-session and the
//! actual gateway. Every profile executable is this fixed test binary.
use ases_resource_control::{now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::access::Policy;
use ases_resource_control::catalog::Account;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::os::unix::net::{UnixListener, UnixStream};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::thread;
use std::time::{Duration, Instant};

const ACCOUNT: &str = "drive-test-account";
const PROJECT: &str = "drive-test-project";
const ENVIRONMENT: &str = "drive-test-environment";

fn admin_policy() -> Policy {
    Policy { administrators: vec![unsafe { libc::geteuid() }], callers: vec![] }
}

fn account() -> Account {
    Account { id: ACCOUNT.into(), provider: "local".into(), payer_ref: "drive-test-only".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec![PROJECT.into()],
        source: "synthetic-native-session-drive-test".into(), observed_at: now(), ttl_seconds: 3600 }
}

fn meter() -> Meter {
    Meter { id: "drive-test-meter".into(), account: ACCOUNT.into(), provider: "local".into(),
        product: "fixed-drive-worker".into(), period: "session-drive-test".into(), unit: "units".into(),
        limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-session-drive-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false }
}

fn environment() -> Environment {
    Environment { id: ENVIRONMENT.into(), account: ACCOUNT.into(), provider: "local".into(),
        max_parallel: 1, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-session-drive-test".into() }
}

fn proposal(job: &str) -> Proposal {
    Proposal { job_id: job.into(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(), estimated_wall_seconds: 90,
        claims: vec![Claim { meter_id: "drive-test-meter".into(), amount: 50 }],
        paid_spend_cap_micros: None, paid_spend_cap_currency: None, forecast_context: None }
}

fn setup(dir: &Path, job: &str) -> (PathBuf, i64) {
    let db = dir.join("control.sqlite");
    let mut store = Store::open(&db).unwrap();
    store.register_account(&account()).unwrap();
    store.register_meter(&meter()).unwrap();
    store.register_environment(&environment()).unwrap();
    let revision = store.catalog_version().unwrap();
    store.reserve(&proposal(job), revision, now()).unwrap();
    store.acknowledge(job, &format!("ack-{job}"), revision, now()).unwrap();
    drop(store);
    (db, revision)
}

fn profile(dir: &Path, marker: &Path, release: &Path, exited: &Path, exit_code: i32) -> Value {
    json!({
        "program": std::env::current_exe().unwrap(),
        "args": ["--exact", "session_drive_fixed_worker", "--nocapture"],
        "cwd": dir,
        "env": {
            "ASES_DRIVE_WORKER_MARKER": marker,
            "ASES_DRIVE_WORKER_RELEASE": release,
            "ASES_DRIVE_WORKER_EXITED": exited,
            "ASES_DRIVE_WORKER_EXIT_CODE": exit_code.to_string()
        },
        "account_id": ACCOUNT, "project_id": PROJECT, "environment_id": ENVIRONMENT
    })
}

struct Gateway { child: Child, socket: PathBuf }
impl Gateway {
    fn start(dir: &Path, name: &str, db: &Path, profile: &Value) -> Self {
        let socket = dir.join(format!("{name}.sock"));
        let policy_path = dir.join(format!("{name}-policy.json"));
        let profile_path = dir.join(format!("{name}-profile.json"));
        fs::write(&policy_path, serde_json::to_vec(&admin_policy()).unwrap()).unwrap();
        fs::write(&profile_path, serde_json::to_vec(profile).unwrap()).unwrap();
        let child = Command::new(env!("CARGO_BIN_EXE_resource-gateway"))
            .arg(db).arg(&socket).arg(&policy_path)
            .arg(env!("CARGO_BIN_EXE_ases-resource-control")).arg(&profile_path)
            .stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null()).spawn().unwrap();
        let until = Instant::now() + Duration::from_secs(10);
        while Instant::now() < until {
            if socket.exists() { return Self { child, socket }; }
            thread::sleep(Duration::from_millis(10));
        }
        panic!("resource gateway failed to create socket {}", socket.display());
    }
    fn kill(&mut self) { let _ = self.child.kill(); let _ = self.child.wait(); }
}
impl Drop for Gateway { fn drop(&mut self) { self.kill(); } }

struct Release(PathBuf);
impl Drop for Release { fn drop(&mut self) { let _ = fs::write(&self.0, b"release\n"); } }

fn invoke_drive(socket: &Path, job: &str, launch: &str, revision: i64, outcome: &str, budget_ms: u64) -> Output {
    Command::new(env!("CARGO_BIN_EXE_resource-drive"))
        .arg(socket).arg(job).arg(launch).arg(revision.to_string())
        .arg(outcome).arg(budget_ms.to_string())
        .stdin(Stdio::null()).output().unwrap()
}

fn invoke_client(socket: &Path, args: &[&str]) -> Output {
    let mut command = Command::new(env!("CARGO_BIN_EXE_resource-session"));
    command.arg(socket).args(args).stdin(Stdio::null()).output().unwrap()
}

fn parse_output(output: &Output) -> Value {
    serde_json::from_slice(&output.stdout).unwrap_or_else(|_| panic!(
        "expected driver/client JSON: status={:?}, stdout={}, stderr={}", output.status.code(),
        String::from_utf8_lossy(&output.stdout), String::from_utf8_lossy(&output.stderr)))
}

fn events(db: &Path, job: &str) -> Value {
    serde_json::to_value(Store::open(db).unwrap().event_log(Some(job)).unwrap()).unwrap()
}
fn balances(db: &Path) -> Value {
    serde_json::to_value(Store::open(db).unwrap().balances(now()).unwrap()).unwrap()
}
fn reserved(value: &Value) -> i64 {
    value.as_array().unwrap().iter()
        .find(|row| row["meter_id"] == "drive-test-meter")
        .and_then(|row| row["active_reserved_remaining"].as_i64()).unwrap()
}
fn worker_lines(path: &Path) -> Vec<Value> {
    fs::read_to_string(path).unwrap_or_default().lines().map(|line| serde_json::from_str(line).unwrap()).collect()
}
fn wait_for(path: &Path, timeout: Duration) {
    let until = Instant::now() + timeout;
    while Instant::now() < until {
        if path.exists() { return; }
        thread::sleep(Duration::from_millis(10));
    }
    panic!("fixed session-drive worker did not create {}", path.display());
}
fn event_count(snapshot: &Value, kind: &str) -> usize {
    snapshot.as_array().unwrap().iter().filter(|event| event["kind"] == kind).count()
}
fn release_after(path: PathBuf, delay: Duration) -> thread::JoinHandle<()> {
    thread::spawn(move || { thread::sleep(delay); fs::write(path,b"natural completion\n").unwrap(); })
}
fn source_hashes() -> Value {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut values = serde_json::Map::new();
    for file in ["src/bin/resource-drive.rs", "src/bin/resource-session.rs", "src/bin/resource-gateway.rs",
        "src/local.rs", "src/lib.rs", "tests/native_session_drive.rs"] {
        if let Ok(bytes) = fs::read(root.join(file)) {
            values.insert(file.into(), json!(format!("{:x}", Sha256::digest(bytes))));
        }
    }
    Value::Object(values)
}
fn persist(value: Value) {
    if let Some(dir) = std::env::var_os("ASES_SESSION_DRIVE_EVIDENCE_DIR") {
        let dir = PathBuf::from(dir);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join("driver-history.json"), serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

/// Fixed child used only by trusted profile; it releases on a file or timeout.
#[test]
fn session_drive_fixed_worker() {
    let Some(marker) = std::env::var_os("ASES_DRIVE_WORKER_MARKER") else { return };
    let marker = PathBuf::from(marker);
    let release = PathBuf::from(std::env::var_os("ASES_DRIVE_WORKER_RELEASE").unwrap());
    let exited = PathBuf::from(std::env::var_os("ASES_DRIVE_WORKER_EXITED").unwrap());
    let exit_code = std::env::var("ASES_DRIVE_WORKER_EXIT_CODE").unwrap().parse::<i32>().unwrap();
    let pid = std::process::id();
    let stat = fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let start_token = stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap().to_string();
    let mut file = OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file, &json!({"pid":pid,"start_token":start_token,"fixed_worker":true})).unwrap();
    file.write_all(b"\n").unwrap();
    file.sync_all().unwrap();
    let until = Instant::now() + Duration::from_secs(25);
    while !release.exists() && Instant::now() < until { thread::sleep(Duration::from_millis(10)); }
    fs::write(exited,b"released-or-timed-out\n").unwrap();
    std::process::exit(exit_code);
}

#[test]
fn native_driver_natural_nonzero_budget_cold_and_lost_reply_histories() {
    let root = tempfile::tempdir().unwrap();
    let mut histories = serde_json::Map::new();

    // Natural code-0 exit is observed by resource-session before the driver
    // sends the caller-selected semantic outcome to explicit finalize.
    let success_dir = root.path().join("natural-zero"); fs::create_dir_all(&success_dir).unwrap();
    let success_job = "drive-natural-job"; let success_launch = "drive-natural-launch";
    let (success_db, success_revision) = setup(&success_dir, success_job);
    let success_marker = success_dir.join("worker-counter.jsonl"); let success_release = success_dir.join("worker-release");
    let success_exited = success_dir.join("worker-exited"); let _success_release = Release(success_release.clone());
    let success_profile = profile(&success_dir,&success_marker,&success_release,&success_exited,0);
    let success_gateway = Gateway::start(&success_dir,"gateway-success",&success_db,&success_profile);
    let success_before = events(&success_db,success_job);
    let success_release_thread=release_after(success_release.clone(),Duration::from_millis(100));
    let success_output = invoke_drive(&success_gateway.socket,success_job,success_launch,success_revision,"completed",5000);
    success_release_thread.join().unwrap();
    let success_response = parse_output(&success_output);
    let success_after = events(&success_db,success_job);
    assert_eq!(success_output.status.code(),Some(0),"driver success: {success_response}");
    assert_eq!(success_response["ok"],true);
    assert_eq!(success_response["outcome"],"finalized");
    assert_eq!(success_response["selected_outcome"],"completed");
    assert_eq!(success_response["exit_observation"]["result"]["state"],"exit_observed");
    assert_eq!(success_response["exit_observation"]["result"]["exit"]["code"],0);
    assert_eq!(success_response["finalization"]["ok"],true);
    assert_eq!(event_count(&success_after,"LAUNCH_INTENT"),1);
    assert_eq!(event_count(&success_after,"LAUNCH_STARTED_OBSERVED"),1);
    assert_eq!(event_count(&success_after,"LAUNCH_EXIT_OBSERVED"),1);
    assert_eq!(event_count(&success_after,"FINALIZED"),1);
    assert_eq!(worker_lines(&success_marker).len(),1);
    assert!(success_exited.exists());
    assert_eq!(reserved(&balances(&success_db)),0);
    let success_history = json!({"job_id":success_job,"launch_id":success_launch,
        "command":["resource-drive",success_gateway.socket,success_job,success_launch,success_revision,"completed",5000],
        "driver_output":{"exit_code":success_output.status.code(),"stdout":String::from_utf8_lossy(&success_output.stdout),"stderr":String::from_utf8_lossy(&success_output.stderr)},
        "events_before":success_before,"events_after":success_after,
        "worker_launch_counter":worker_lines(&success_marker),"worker_exit_marker":success_exited.exists(),
        "balances_after_finalize":balances(&success_db)});
    drop(success_gateway);
    histories.insert("natural_code_zero_finalize".into(),success_history);

    // A nonzero process exit is evidence only. The selected outcome is explicit
    // input and is not inferred from the child's exit code.
    let nonzero_dir = root.path().join("nonzero"); fs::create_dir_all(&nonzero_dir).unwrap();
    let nonzero_job = "drive-nonzero-job"; let nonzero_launch = "drive-nonzero-launch";
    let (nonzero_db, nonzero_revision) = setup(&nonzero_dir,nonzero_job);
    let nonzero_marker = nonzero_dir.join("worker-counter.jsonl"); let nonzero_release = nonzero_dir.join("worker-release");
    let nonzero_exited = nonzero_dir.join("worker-exited"); let _nonzero_release = Release(nonzero_release.clone());
    let nonzero_profile = profile(&nonzero_dir,&nonzero_marker,&nonzero_release,&nonzero_exited,7);
    let nonzero_gateway = Gateway::start(&nonzero_dir,"gateway-nonzero",&nonzero_db,&nonzero_profile);
    let nonzero_before = events(&nonzero_db,nonzero_job);
    let nonzero_release_thread=release_after(nonzero_release.clone(),Duration::from_millis(100));
    let nonzero_output = invoke_drive(&nonzero_gateway.socket,nonzero_job,nonzero_launch,nonzero_revision,"failed",5000);
    nonzero_release_thread.join().unwrap();
    let nonzero_response = parse_output(&nonzero_output);
    let nonzero_after = events(&nonzero_db,nonzero_job);
    assert_eq!(nonzero_output.status.code(),Some(0),"explicit nonzero outcome finalizes: {nonzero_response}");
    assert_eq!(nonzero_response["selected_outcome"],"failed");
    assert_eq!(nonzero_response["exit_observation"]["result"]["exit"]["code"],7);
    assert_eq!(nonzero_response["finalization"]["result"]["outcome"],"failed");
    assert_eq!(event_count(&nonzero_after,"LAUNCH_EXIT_OBSERVED"),1);
    assert_eq!(event_count(&nonzero_after,"FINALIZED"),1);
    assert_eq!(worker_lines(&nonzero_marker).len(),1);
    assert!(nonzero_exited.exists());
    assert_eq!(reserved(&balances(&nonzero_db)),0);
    histories.insert("nonzero_explicit_failed_outcome".into(),json!({
        "job_id":nonzero_job,"launch_id":nonzero_launch,
        "command":["resource-drive",nonzero_gateway.socket,nonzero_job,nonzero_launch,nonzero_revision,"failed",5000],
        "driver_output":{"exit_code":nonzero_output.status.code(),"stdout":String::from_utf8_lossy(&nonzero_output.stdout),"stderr":String::from_utf8_lossy(&nonzero_output.stderr)},
        "events_before":nonzero_before,"events_after":nonzero_after,"worker_launch_counter":worker_lines(&nonzero_marker),
        "worker_exit_marker":nonzero_exited.exists(),"balances_after_finalize":balances(&nonzero_db)}));
    drop(nonzero_gateway);

    // Budget exhaustion reports recovery need while the live worker and
    // reservation remain untouched. Test cleanup later releases the worker
    // through its bounded file gate, then explicitly observes and finalizes.
    let budget_dir = root.path().join("budget"); fs::create_dir_all(&budget_dir).unwrap();
    let budget_job = "drive-budget-job"; let budget_launch = "drive-budget-launch";
    let (budget_db,budget_revision)=setup(&budget_dir,budget_job);
    let budget_marker=budget_dir.join("worker-counter.jsonl"); let budget_release=budget_dir.join("worker-release");
    let budget_exited=budget_dir.join("worker-exited"); let _budget_release=Release(budget_release.clone());
    let budget_profile=profile(&budget_dir,&budget_marker,&budget_release,&budget_exited,0);
    let budget_gateway=Gateway::start(&budget_dir,"gateway-budget",&budget_db,&budget_profile);
    let budget_before=events(&budget_db,budget_job);
    let budget_output=invoke_drive(&budget_gateway.socket,budget_job,budget_launch,budget_revision,"interrupted",150);
    let budget_response=parse_output(&budget_output);
    let budget_after=events(&budget_db,budget_job);
    assert_eq!(budget_output.status.code(),Some(3));
    assert_eq!(budget_response["ok"],false);
    assert_eq!(budget_response["outcome"],"recovery_needed");
    assert_eq!(budget_response["reason"],"budget_exhausted");
    assert_eq!(Store::open(&budget_db).unwrap().job(budget_job).unwrap()["state"],"RUNNING");
    assert_eq!(event_count(&budget_after,"LOCAL_STOP_REQUESTED"),0);
    assert_eq!(event_count(&budget_after,"FINALIZED"),0);
    assert!(reserved(&balances(&budget_db))>0);
    assert_eq!(worker_lines(&budget_marker).len(),1);
    assert!(!budget_exited.exists(),"worker is still live at budget exhaustion");
    let budget_history=json!({"job_id":budget_job,"launch_id":budget_launch,
        "command":["resource-drive",budget_gateway.socket,budget_job,budget_launch,budget_revision,"interrupted",150],
        "driver_output":{"exit_code":budget_output.status.code(),"stdout":String::from_utf8_lossy(&budget_output.stdout),"stderr":String::from_utf8_lossy(&budget_output.stderr)},
        "events_before_cleanup":budget_before,"events_after_budget":budget_after,
        "worker_launch_counter":worker_lines(&budget_marker),"worker_exited_at_budget":budget_exited.exists(),
        "balances_at_budget":balances(&budget_db)});
    fs::write(&budget_release,b"test cleanup release\n").unwrap(); wait_for(&budget_exited,Duration::from_secs(5));
    let cleanup_poll=invoke_client(&budget_gateway.socket,&["poll",budget_job,budget_launch]);
    let cleanup_poll_reply=parse_output(&cleanup_poll);
    assert_eq!(cleanup_poll_reply["result"]["state"],"exit_observed");
    let cleanup_finalize=invoke_client(&budget_gateway.socket,&["finalize",budget_job,budget_launch,"interrupted"]);
    assert_eq!(parse_output(&cleanup_finalize)["ok"],true);
    assert_eq!(reserved(&balances(&budget_db)),0);
    histories.insert("live_budget_exhaustion_no_automatic_effect".into(),json!({
        "driver_history":budget_history,
        "separate_explicit_test_cleanup":{"poll_exit_code":cleanup_poll.status.code(),"poll_stdout":String::from_utf8_lossy(&cleanup_poll.stdout),
            "finalize_exit_code":cleanup_finalize.status.code(),"finalize_stdout":String::from_utf8_lossy(&cleanup_finalize.stdout),
            "balances_after_cleanup":balances(&budget_db)}}));
    drop(budget_gateway);

    // Cold restart cannot redispatch or release capacity. The helper worker is
    // eventually released by file/timeout only; this test never adopts its PID.
    let cold_dir=root.path().join("cold"); fs::create_dir_all(&cold_dir).unwrap();
    let cold_job="drive-cold-job"; let cold_launch="drive-cold-launch";
    let (cold_db,cold_revision)=setup(&cold_dir,cold_job);
    let cold_marker=cold_dir.join("worker-counter.jsonl"); let cold_release=cold_dir.join("worker-release");
    let cold_exited=cold_dir.join("worker-exited"); let _cold_release=Release(cold_release.clone());
    let cold_profile=profile(&cold_dir,&cold_marker,&cold_release,&cold_exited,0);
    let mut hot_cold_gateway=Gateway::start(&cold_dir,"gateway-cold-hot",&cold_db,&cold_profile);
    let cold_before=events(&cold_db,cold_job);
    let first_driver=invoke_drive(&hot_cold_gateway.socket,cold_job,cold_launch,cold_revision,"completed",150);
    let first_reply=parse_output(&first_driver);
    assert_eq!(first_reply["outcome"],"recovery_needed");
    wait_for(&cold_marker,Duration::from_secs(5));
    assert_eq!(worker_lines(&cold_marker).len(),1);
    hot_cold_gateway.kill(); drop(hot_cold_gateway);
    let cold_gateway=Gateway::start(&cold_dir,"gateway-cold-restart",&cold_db,&cold_profile);
    let after_loss=events(&cold_db,cold_job);
    let cold_driver=invoke_drive(&cold_gateway.socket,cold_job,cold_launch,cold_revision,"completed",150);
    let cold_reply=parse_output(&cold_driver);
    let after_cold_invocation=events(&cold_db,cold_job);
    assert_eq!(cold_driver.status.code(),Some(3));
    assert_eq!(cold_reply["outcome"],"recovery_needed");
    assert!(matches!(cold_reply["reason"].as_str(),Some("unknown_custody"|"client_outcome_unknown")));
    assert_eq!(worker_lines(&cold_marker).len(),1,"fresh cold driver must not create another worker");
    assert_eq!(after_cold_invocation,after_loss,"cold unknown invocation adds no events or finalization");
    assert_eq!(event_count(&after_cold_invocation,"LOCAL_STOP_REQUESTED"),0);
    assert_eq!(event_count(&after_cold_invocation,"FINALIZED"),0);
    assert!(reserved(&balances(&cold_db))>0);
    let cold_history=json!({"job_id":cold_job,"launch_id":cold_launch,
        "first_driver":{"exit_code":first_driver.status.code(),"stdout":String::from_utf8_lossy(&first_driver.stdout),"stderr":String::from_utf8_lossy(&first_driver.stderr)},
        "cold_driver":{"command":["resource-drive",cold_gateway.socket,cold_job,cold_launch,cold_revision,"completed",150],
            "exit_code":cold_driver.status.code(),"stdout":String::from_utf8_lossy(&cold_driver.stdout),"stderr":String::from_utf8_lossy(&cold_driver.stderr)},
        "events_before":cold_before,"events_after_gateway_loss":after_loss,"events_after_cold_invocation":after_cold_invocation,
        "worker_launch_counter":worker_lines(&cold_marker),"worker_exit_marker_before_release":cold_exited.exists(),
        "balances_after_cold_invocation":balances(&cold_db)});
    drop(cold_gateway);
    fs::write(&cold_release,b"cold cleanup release\n").unwrap(); wait_for(&cold_exited,Duration::from_secs(5));
    histories.insert("cold_restart_unknown_no_redispatch".into(),cold_history);

    // A finalization reply can be lost after the actual Store has committed it.
    // The transport proxy relays launch/poll replies, pauses before forwarding
    // finalize so this test process can capture pre-finalize capacity, then
    // discards the real successful finalization reply.
    let lost_dir=root.path().join("finalize-reply-loss"); fs::create_dir_all(&lost_dir).unwrap();
    let lost_job="drive-finalize-loss-job"; let lost_launch="drive-finalize-loss-launch";
    let (lost_db,lost_revision)=setup(&lost_dir,lost_job);
    let lost_marker=lost_dir.join("worker-counter.jsonl"); let lost_release=lost_dir.join("worker-release");
    let lost_exited=lost_dir.join("worker-exited"); let _lost_release=Release(lost_release.clone());
    let lost_profile=profile(&lost_dir,&lost_marker,&lost_release,&lost_exited,0);
    let lost_gateway=Gateway::start(&lost_dir,"gateway-finalize-loss",&lost_db,&lost_profile);
    let proxy_path=lost_dir.join("driver-drop-finalize-proxy.sock");
    let (finalize_seen_tx,finalize_seen_rx)=std::sync::mpsc::channel();
    let (forward_finalize_tx,forward_finalize_rx)=std::sync::mpsc::channel();
    let proxy=drop_finalize_reply_once(proxy_path.clone(),lost_gateway.socket.clone(),finalize_seen_tx,forward_finalize_rx);
    wait_for(&proxy_path,Duration::from_secs(5));
    let before_driver=events(&lost_db,lost_job);
    let lost_release_thread=release_after(lost_release.clone(),Duration::from_millis(100));
    let driver_socket=proxy_path.clone();
    let driver_thread=thread::spawn(move || invoke_drive(&driver_socket,lost_job,lost_launch,lost_revision,"completed",5000));
    finalize_seen_rx.recv_timeout(Duration::from_secs(10)).expect("driver never issued finalize");
    let before_finalize=events(&lost_db,lost_job);
    let balances_before_finalize=balances(&lost_db);
    assert_eq!(Store::open(&lost_db).unwrap().job(lost_job).unwrap()["state"],"RUNNING");
    assert_eq!(event_count(&before_finalize,"LAUNCH_EXIT_OBSERVED"),1);
    assert_eq!(event_count(&before_finalize,"FINALIZED"),0);
    assert!(reserved(&balances_before_finalize)>0,"capacity remains held before real finalization request");
    assert_eq!(worker_lines(&lost_marker).len(),1);
    forward_finalize_tx.send(()).unwrap();
    let driver_output=driver_thread.join().expect("driver subprocess waiter panicked");
    lost_release_thread.join().unwrap();
    let proxy_capture=proxy.join().expect("bounded finalization-drop proxy panicked");
    let driver_reply=parse_output(&driver_output);
    let after_finalize=events(&lost_db,lost_job);
    let balances_after_finalize=balances(&lost_db);
    assert_eq!(driver_output.status.code(),Some(3));
    assert_eq!(driver_reply["ok"],false);
    assert_eq!(driver_reply["outcome"],"recovery_needed");
    assert_eq!(driver_reply["reason"],"client_outcome_unknown");
    assert_eq!(driver_reply["last_action"],"finalize");
    assert_eq!(driver_reply["client_status"],4);
    assert_eq!(driver_reply["client_reply"]["outcome"],"outcome_unknown");
    assert_eq!(proxy_capture["forwarded_finalization_once"],true);
    assert_eq!(proxy_capture["additional_connections"],0,"driver must not retry after unknown finalization");
    assert_eq!(proxy_capture["exchanges"].as_array().unwrap().last().unwrap()["request"]["op"],"local_finalize");
    assert_eq!(proxy_capture["exchanges"].as_array().unwrap().last().unwrap()["gateway_reply"]["ok"],true);
    assert_eq!(Store::open(&lost_db).unwrap().job(lost_job).unwrap()["state"],"CLOSED");
    assert_eq!(event_count(&after_finalize,"LAUNCH_EXIT_OBSERVED"),1);
    assert_eq!(event_count(&after_finalize,"FINALIZED"),1);
    assert_eq!(reserved(&balances_after_finalize),0,"actual gateway committed finalize before its reply was dropped");
    assert_eq!(worker_lines(&lost_marker).len(),1);

    // Explicit fresh resume reads durable CLOSED state after uncertainty. It is
    // outside the failed driver invocation and cannot replay finalization.
    let resume_output=invoke_client(&lost_gateway.socket,&["resume",lost_job,lost_launch]);
    let resume_reply=parse_output(&resume_output);
    assert_eq!(resume_output.status.code(),Some(0));
    assert_eq!(resume_reply["result"]["local_state"],"unknown");
    assert_eq!(resume_reply["result"]["resume_view"]["evidence"]["outcome"]["kind"],"FINALIZED");
    assert_eq!(Store::open(&lost_db).unwrap().job(lost_job).unwrap()["state"],"CLOSED");
    let lost_history=json!({"job_id":lost_job,"launch_id":lost_launch,
        "driver_command":["resource-drive",proxy_path,lost_job,lost_launch,lost_revision,"completed",5000],
        "driver_output":{"exit_code":driver_output.status.code(),"stdout":String::from_utf8_lossy(&driver_output.stdout),"stderr":String::from_utf8_lossy(&driver_output.stderr)},
        "proxy_capture":proxy_capture,"events_before_driver":before_driver,
        "events_before_finalize":before_finalize,"events_after_finalize_reply_loss":after_finalize,
        "balances_before_finalize":balances_before_finalize,"balances_after_finalize":balances_after_finalize,
        "worker_launch_counter":worker_lines(&lost_marker),
        "worker_exit_marker":lost_exited.exists(),
        "fresh_resume_after_unknown":{"exit_code":resume_output.status.code(),"stdout":String::from_utf8_lossy(&resume_output.stdout),"stderr":String::from_utf8_lossy(&resume_output.stderr)}});
    histories.insert("actual_finalize_committed_reply_lost".into(),lost_history);
    drop(lost_gateway);

    persist(json!({
        "why":"the driver is a bounded consumer of existing launch/custody/exit/finalize transitions",
        "what":"actual resource-drive -> sibling resource-session -> Unix gateway -> fixed owned test worker -> existing Store events",
        "how_certain":"experimental native histories; exact Store events, outputs, worker counters and balances retained",
        "what_not_tested":["remote providers","hostile same-UID code","whole-host loss","arbitrary programs","hard wall-time quiescence","generalized methodology automation","automatic repair of unknown outcomes"],
        "histories":histories,"source_sha256":source_hashes()
    }));
}

fn drop_finalize_reply_once(
    proxy_path: PathBuf,
    gateway_path: PathBuf,
    finalize_seen: std::sync::mpsc::Sender<()>,
    forward_finalize: std::sync::mpsc::Receiver<()>,
) -> thread::JoinHandle<Value> {
    thread::spawn(move || {
        let listener = UnixListener::bind(&proxy_path).unwrap();
        let mut exchanges = Vec::new();
        loop {
            let (mut downstream, _) = listener.accept().unwrap();
            downstream.set_read_timeout(Some(Duration::from_secs(3))).unwrap();
            downstream.set_write_timeout(Some(Duration::from_secs(3))).unwrap();
            let mut request_bytes = Vec::new();
            let mut chunk = [0u8; 1024];
            loop {
                let n = downstream.read(&mut chunk).unwrap();
                if n == 0 { break; }
                assert!(request_bytes.len() + n <= 8192, "driver client request exceeded bound");
                request_bytes.extend_from_slice(&chunk[..n]);
            }
            let request: Value = serde_json::from_slice(&request_bytes).unwrap();
            let op = request["op"].as_str().unwrap();
            if op == "local_finalize" {
                // Pause before forwarding so the test process can record the
                // durable pre-finalize state and held capacity. Proxy itself
                // has no Store or lifecycle authority.
                finalize_seen.send(()).unwrap();
                forward_finalize.recv_timeout(Duration::from_secs(10)).unwrap();
            }
            let mut upstream = UnixStream::connect(&gateway_path).unwrap();
            upstream.set_read_timeout(Some(Duration::from_secs(3))).unwrap();
            upstream.set_write_timeout(Some(Duration::from_secs(3))).unwrap();
            upstream.write_all(&request_bytes).unwrap();
            upstream.shutdown(std::net::Shutdown::Write).unwrap();
            let mut response_bytes = Vec::new();
            loop {
                let n = upstream.read(&mut chunk).unwrap();
                if n == 0 { break; }
                assert!(response_bytes.len() + n <= 8192, "gateway client reply exceeded bound");
                response_bytes.extend_from_slice(&chunk[..n]);
            }
            let gateway_reply: Value = serde_json::from_slice(&response_bytes).unwrap();
            let discard = op == "local_finalize";
            exchanges.push(json!({"request":request,"gateway_reply":gateway_reply,"reply_discarded":discard}));
            drop(upstream);
            if discard {
                drop(downstream);
                break;
            }
            downstream.write_all(&response_bytes).unwrap();
            downstream.shutdown(std::net::Shutdown::Write).unwrap();
            drop(downstream);
        }
        listener.set_nonblocking(true).unwrap();
        let until = Instant::now() + Duration::from_millis(200);
        let mut additional_connections = 0;
        let mut chunk = [0u8; 1024];
        while Instant::now() < until {
            match listener.accept() {
                Ok((mut retry, _)) => {
                    additional_connections += 1;
                    retry.set_read_timeout(Some(Duration::from_millis(100))).unwrap();
                    let _ = retry.read(&mut chunk);
                }
                Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => thread::sleep(Duration::from_millis(5)),
                Err(error) => panic!("drop proxy listener failed: {error}"),
            }
        }
        json!({"exchanges":exchanges,"forwarded_finalization_once":true,
            "actual_finalization_reply_discarded":true,"additional_connections":additional_connections})
    })
}
