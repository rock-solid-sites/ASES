//! Native evidence for atomic cancellation before any native launch intent.
//! Copy this file to resource-control/tests only after the implementation
//! branch is pinned. The first test is the old-route baseline discriminator.
use ases_resource_control::{now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::access::{Grant, Policy};
use ases_resource_control::catalog::Account;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::os::unix::net::UnixStream;
use std::os::unix::process::ExitStatusExt;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::{Duration, Instant};

const ACCOUNT: &str = "unlaunched-cancel-account";
const PROJECT: &str = "unlaunched-cancel-project";
const ENVIRONMENT: &str = "unlaunched-cancel-environment";

fn admin_policy() -> Policy {
    Policy { administrators: vec![unsafe { libc::geteuid() }], callers: vec![] }
}

fn viewer_policy() -> Policy {
    Policy { administrators: vec![], callers: vec![Grant {
        uid: unsafe { libc::geteuid() }, role: "viewer".into(),
        accounts: vec![ACCOUNT.into()], projects: vec![PROJECT.into()],
    }] }
}

fn account() -> Account {
    Account { id: ACCOUNT.into(), provider: "local".into(), payer_ref: "cancel-test-only".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec![PROJECT.into()],
        source: "synthetic-native-unlaunched-cancellation".into(), observed_at: now(), ttl_seconds: 3600 }
}

fn meter() -> Meter {
    Meter { id: "unlaunched-cancel-meter".into(), account: ACCOUNT.into(), provider: "local".into(),
        product: "fixed-unlaunched-cancel-worker".into(), period: "unlaunched-cancel-test".into(),
        unit: "units".into(), limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-unlaunched-cancellation".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false }
}

fn environment() -> Environment {
    Environment { id: ENVIRONMENT.into(), account: ACCOUNT.into(), provider: "local".into(),
        max_parallel: 1, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-unlaunched-cancellation".into() }
}

fn proposal(job: &str) -> Proposal {
    Proposal { job_id: job.into(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(), estimated_wall_seconds: 60,
        claims: vec![Claim { meter_id: "unlaunched-cancel-meter".into(), amount: 50 }],
        paid_spend_cap_micros: None, paid_spend_cap_currency: None, forecast_context: None }
}

fn setup(job: &str, authorized: bool) -> (tempfile::TempDir, PathBuf, i64) {
    let dir = tempfile::tempdir().unwrap();
    let db = dir.path().join("control.sqlite");
    let mut store = Store::open(&db).unwrap();
    store.register_account(&account()).unwrap();
    store.register_meter(&meter()).unwrap();
    store.register_environment(&environment()).unwrap();
    let revision = store.catalog_version().unwrap();
    store.reserve(&proposal(job), revision, now()).unwrap();
    if authorized { store.acknowledge(job, &format!("ack-{job}"), revision, now()).unwrap(); }
    (dir, db, revision)
}

fn profile(marker: &Path, release: &Path) -> Value {
    json!({
        "program": std::env::current_exe().unwrap(),
        "args": ["--exact", "unlaunched_cancel_fixed_worker", "--nocapture"],
        "cwd": std::env::current_dir().unwrap(),
        "env": {"ASES_UNLAUNCHED_CANCEL_MARKER":marker,"ASES_UNLAUNCHED_CANCEL_RELEASE":release},
        "account_id":ACCOUNT,"project_id":PROJECT,"environment_id":ENVIRONMENT
    })
}

struct Gateway { child: Child, socket: PathBuf }

impl Gateway {
    fn start(dir: &Path, name: &str, db: &Path, policy: &Policy, trusted_profile: &Value) -> Self {
        let socket = dir.join(format!("{name}.sock"));
        let policy_path = dir.join(format!("{name}-policy.json"));
        let profile_path = dir.join(format!("{name}-profile.json"));
        fs::write(&policy_path, serde_json::to_vec(policy).unwrap()).unwrap();
        fs::write(&profile_path, serde_json::to_vec(trusted_profile).unwrap()).unwrap();
        let child = Command::new(env!("CARGO_BIN_EXE_resource-gateway"))
            .arg(db).arg(&socket).arg(&policy_path)
            .arg(env!("CARGO_BIN_EXE_ases-resource-control")).arg(&profile_path)
            .stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::piped()).spawn().unwrap();
        let until = Instant::now() + Duration::from_secs(10);
        while Instant::now() < until {
            if socket.exists() { return Self { child, socket }; }
            thread::sleep(Duration::from_millis(10));
        }
        panic!("resource gateway did not create socket {}", socket.display());
    }

    fn send(&self, request: &Value) -> Value { send_to(&self.socket, request) }
}

impl Drop for Gateway {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

struct Release(PathBuf);
impl Drop for Release { fn drop(&mut self) { let _ = fs::write(&self.0, b"release\n"); } }

fn send_to(socket: &Path, request: &Value) -> Value {
    let mut stream = UnixStream::connect(socket).unwrap();
    stream.write_all(serde_json::to_string(request).unwrap().as_bytes()).unwrap();
    stream.shutdown(std::net::Shutdown::Write).unwrap();
    let mut bytes = Vec::new();
    stream.read_to_end(&mut bytes).unwrap();
    serde_json::from_slice(&bytes).unwrap()
}

fn client(socket: &Path, args: &[&str]) -> Output {
    let mut command = Command::new(env!("CARGO_BIN_EXE_resource-session"));
    command.arg(socket).args(args).stdin(Stdio::null()).output().unwrap()
}

fn client_json(output: &Output) -> Value {
    serde_json::from_slice(&output.stdout).unwrap_or_else(|_| panic!(
        "resource-session did not return JSON: code={:?} stdout={} stderr={}",
        output.status.code(), String::from_utf8_lossy(&output.stdout), String::from_utf8_lossy(&output.stderr)))
}

fn launch(job: &str, launch_id: &str, revision: i64) -> Value {
    json!({"op":"local_launch","job_id":job,"launch_id":launch_id,"expected_catalog":revision})
}

fn cancel(job: &str) -> Value { json!({"op":"local_cancel_unlaunched","job_id":job}) }

fn old_finalize(job: &str, arbitrary_selector: &str) -> Value {
    json!({"op":"local_finalize","job_id":job,"launch_id":arbitrary_selector,"outcome":"cancelled"})
}

fn events(db: &Path, job: &str) -> Vec<Value> {
    Store::open(db).unwrap().event_log(Some(job)).unwrap()
}

fn balance(db: &Path) -> Value {
    serde_json::to_value(Store::open(db).unwrap().balances(now()).unwrap()).unwrap()
}

fn remaining(db: &Path) -> i64 {
    Store::open(db).unwrap().balances(now()).unwrap().into_iter()
        .find(|item| item.meter_id == "unlaunched-cancel-meter").unwrap().active_reserved_remaining
}

fn job(db: &Path, id: &str) -> Value { Store::open(db).unwrap().job(id).unwrap() }

fn wait_for(path: &Path) {
    let until = Instant::now() + Duration::from_secs(10);
    while Instant::now() < until {
        if path.exists() { return; }
        thread::sleep(Duration::from_millis(10));
    }
    panic!("bounded worker marker did not appear: {}", path.display());
}

fn worker_rows(path: &Path) -> Vec<Value> {
    fs::read_to_string(path).unwrap_or_default().lines()
        .map(|line| serde_json::from_str(line).unwrap()).collect()
}

fn worker_alive(pid: u32, token: &str) -> bool {
    let Ok(raw) = fs::read_to_string(format!("/proc/{pid}/stat")) else { return false };
    let Some((_, tail)) = raw.rsplit_once(") ") else { return false };
    let mut fields = tail.split_whitespace();
    let state = fields.next().and_then(|value| value.chars().next());
    let start = fields.nth(18);
    matches!(state, Some('R' | 'S')) && start == Some(token)
}

fn wait_until_exit(gateway: &Gateway, db: &Path, job_id: &str, launch_id: &str) -> Value {
    let request = json!({"op":"local_poll","job_id":job_id,"launch_id":launch_id});
    let until = Instant::now() + Duration::from_secs(10);
    loop {
        let reply = gateway.send(&request);
        if events(db, job_id).iter().any(|event| event["kind"] == "LAUNCH_EXIT_OBSERVED") {
            return reply;
        }
        assert!(Instant::now() < until, "bounded worker exit was not observed");
        thread::sleep(Duration::from_millis(10));
    }
}

fn source_hashes() -> Value {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut hashes = serde_json::Map::new();
    for relative in ["src/main.rs", "src/lib.rs", "src/local.rs", "src/bin/resource-gateway.rs",
        "tests/native_unlaunched_cancel.rs", "../docs/research/phase-ii-local-execution/CANCELLATION.md"] {
        if let Ok(bytes) = fs::read(root.join(relative)) {
            hashes.insert(relative.into(), json!(format!("{:x}", Sha256::digest(bytes))));
        }
    }
    let binaries = [
        ("resource-gateway", env!("CARGO_BIN_EXE_resource-gateway")),
        ("resource-session", env!("CARGO_BIN_EXE_resource-session")),
        ("ases-resource-control", env!("CARGO_BIN_EXE_ases-resource-control")),
    ];
    for (name, executable) in binaries {
        let hash = fs::read(executable).map(|bytes| format!("{:x}", Sha256::digest(bytes))).ok();
        hashes.insert(format!("binary:{name}"), json!({"path":executable,"sha256":hash}));
    }
    let test_executable = std::env::current_exe().unwrap();
    let test_hash = fs::read(&test_executable).map(|bytes| format!("{:x}", Sha256::digest(bytes))).ok();
    hashes.insert("binary:native_unlaunched_cancel_test".into(),
        json!({"path":test_executable,"sha256":test_hash}));
    Value::Object(hashes)
}

fn drop_reply_proxy(proxy_path: PathBuf, gateway_path: PathBuf) -> thread::JoinHandle<Value> {
    let listener = std::os::unix::net::UnixListener::bind(&proxy_path).unwrap();
    thread::spawn(move || {
        let (mut client_stream, _) = listener.accept().unwrap();
        client_stream.set_read_timeout(Some(Duration::from_secs(3))).unwrap();
        let mut bytes = Vec::new();
        client_stream.read_to_end(&mut bytes).unwrap();
        let forwarded_request: Value = serde_json::from_slice(&bytes).unwrap();
        let actual_gateway_response = send_to(&gateway_path, &forwarded_request);
        drop(client_stream); // Deliberately lose the committed server reply.

        listener.set_nonblocking(true).unwrap();
        let until = Instant::now() + Duration::from_millis(250);
        let mut extra_client_requests = Vec::new();
        while Instant::now() < until {
            match listener.accept() {
                Ok((mut stream, _)) => {
                    stream.set_read_timeout(Some(Duration::from_secs(1))).unwrap();
                    let mut additional = Vec::new();
                    let _ = stream.read_to_end(&mut additional);
                    extra_client_requests.push(String::from_utf8_lossy(&additional).to_string());
                }
                Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => thread::sleep(Duration::from_millis(5)),
                Err(error) => panic!("proxy accept failed after dropped reply: {error}"),
            }
        }
        json!({"forwarded_request":forwarded_request,"actual_gateway_response":actual_gateway_response,
            "additional_client_requests":extra_client_requests})
    })
}

fn persist(name: &str, value: Value) {
    if let Some(directory) = std::env::var_os("ASES_UNLAUNCHED_CANCEL_EVIDENCE_DIR") {
        let directory = PathBuf::from(directory);
        fs::create_dir_all(&directory).unwrap();
        fs::write(directory.join(name), serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

#[test]
fn unlaunched_cancel_fixed_worker() {
    let Some(marker) = std::env::var_os("ASES_UNLAUNCHED_CANCEL_MARKER") else { return };
    let release = PathBuf::from(std::env::var_os("ASES_UNLAUNCHED_CANCEL_RELEASE").unwrap());
    let pid = std::process::id();
    let stat = fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let start_token = stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap();
    let mut file = OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file, &json!({"pid":pid,"start_token":start_token})).unwrap();
    file.write_all(b"\n").unwrap();
    file.sync_all().unwrap();
    let until = Instant::now() + Duration::from_secs(20);
    while !release.exists() && Instant::now() < until { thread::sleep(Duration::from_millis(10)); }
}

/// Run this alone against the #41 source before integrating the new op. It
/// establishes the existing local-finalize gap with real preflight + Store.
#[test]
fn preflight_then_old_local_finalize_is_refused_without_mutation() {
    let (dir, db, revision) = setup("old-finalize-gap-job", true);
    let marker = dir.path().join("worker.jsonl");
    let release = dir.path().join("worker.release");
    let _release = Release(release.clone());
    let mut trusted = profile(&marker, &release);
    let missing_program = dir.path().join("not-installed-yet");
    trusted["program"] = json!(missing_program);
    let gateway = Gateway::start(dir.path(), "old-finalize-gap", &db, &admin_policy(), &trusted);

    let launch_request = launch("old-finalize-gap-job", "repair-launch-selector", revision);
    let launch_reply = gateway.send(&launch_request);
    assert_eq!(launch_reply["ok"], false, "actual filesystem preflight failure: {launch_reply}");
    assert_eq!(job(&db, "old-finalize-gap-job")["state"], "AUTHORIZED");
    let events_after_preflight = events(&db, "old-finalize-gap-job");
    assert!(!events_after_preflight.iter().any(|event| event["kind"] == "LAUNCH_INTENT"));
    let held_after_preflight = balance(&db);

    let finalize_request = old_finalize("old-finalize-gap-job", "arbitrary-selector-without-intent");
    let finalize_reply = gateway.send(&finalize_request);
    let events_after_finalize_attempt = events(&db, "old-finalize-gap-job");
    assert_eq!(finalize_reply["ok"], false, "old route must refuse a no-intent job: {finalize_reply}");
    assert_eq!(job(&db, "old-finalize-gap-job")["state"], "AUTHORIZED");
    assert_eq!(events_after_finalize_attempt, events_after_preflight, "old finalize refusal is mutation-free");
    assert_eq!(balance(&db), held_after_preflight);
    assert!(worker_rows(&marker).is_empty());

    persist("preflight-old-local-finalize-gap.json", json!({
        "source_sha256":source_hashes(), "missing_program":missing_program,
        "launch_request":launch_request,"preflight_reply":launch_reply,
        "events_after_preflight":events_after_preflight,"balances_after_preflight":held_after_preflight,
        "old_local_finalize_request":finalize_request,"old_local_finalize_reply":finalize_reply,
        "events_after_old_finalize_attempt":events_after_finalize_attempt,
        "worker_count":worker_rows(&marker).len()
    }));
}

#[test]
fn preflight_failure_cancel_replay_and_later_launch_denial() {
    let (dir, db, revision) = setup("authorized-cancel-job", true);
    let marker = dir.path().join("worker.jsonl");
    let release = dir.path().join("worker.release");
    let _release = Release(release.clone());
    let mut trusted = profile(&marker, &release);
    let missing_program = dir.path().join("not-installed-yet");
    trusted["program"] = json!(missing_program);
    let gateway = Gateway::start(dir.path(), "authorized-cancel", &db, &admin_policy(), &trusted);

    let launch_request = launch("authorized-cancel-job", "repair-launch-selector", revision);
    let preflight_reply = gateway.send(&launch_request);
    assert_eq!(preflight_reply["ok"], false);
    let events_before_old_finalize = events(&db, "authorized-cancel-job");
    let old_finalize_request = old_finalize("authorized-cancel-job", "arbitrary-no-intent-selector");
    let old_finalize_reply = gateway.send(&old_finalize_request);
    assert_eq!(old_finalize_reply["ok"], false);
    assert_eq!(events(&db, "authorized-cancel-job"), events_before_old_finalize);
    assert_eq!(job(&db, "authorized-cancel-job")["state"], "AUTHORIZED");
    let balances_before_cancel = balance(&db);

    let args = ["cancel-unlaunched", "authorized-cancel-job"];
    let cancel_output = client(&gateway.socket, &args);
    let cancel_reply = client_json(&cancel_output);
    assert_eq!(cancel_output.status.code(), Some(0), "native cancel client: {cancel_reply}");
    assert_eq!(cancel_reply["ok"], true);
    assert_eq!(cancel_reply["result"]["finalization"], "CLOSED");
    assert_eq!(cancel_reply["result"]["job_id"], "authorized-cancel-job");
    assert_eq!(cancel_reply["result"]["outcome"], "cancelled");
    assert_eq!(cancel_reply["result"]["launch_profile"], "unlaunched");
    let events_after_cancel = events(&db, "authorized-cancel-job");
    assert_eq!(job(&db, "authorized-cancel-job")["state"], "CLOSED");
    assert_eq!(job(&db, "authorized-cancel-job")["outcome"], "cancelled");
    assert!(!events_after_cancel.iter().any(|event| event["kind"] == "LAUNCH_INTENT"));
    assert_eq!(events_after_cancel.iter().filter(|event| event["kind"] == "FINALIZED").count(), 1);
    assert_eq!(remaining(&db), 0);
    assert!(worker_rows(&marker).is_empty());

    let replay_output = client(&gateway.socket, &args);
    let replay_reply = client_json(&replay_output);
    assert_eq!(replay_output.status.code(), Some(0));
    assert_eq!(replay_reply["ok"], true);
    assert_eq!(replay_reply["result"]["finalization"], "CLOSED_REPLAY");
    assert_eq!(events(&db, "authorized-cancel-job"), events_after_cancel);
    let later_launch_reply = gateway.send(&launch_request);
    assert_eq!(later_launch_reply["ok"], false, "canceled job cannot later launch");
    assert_eq!(events(&db, "authorized-cancel-job"), events_after_cancel);
    assert!(worker_rows(&marker).is_empty());

    persist("authorized-preflight-cancel-replay.json", json!({
        "source_sha256":source_hashes(),"missing_program":missing_program,
        "launch_request":launch_request,"preflight_reply":preflight_reply,
        "old_local_finalize_request":old_finalize_request,"old_local_finalize_reply":old_finalize_reply,
        "events_before_cancel":events_before_old_finalize,"balances_before_cancel":balances_before_cancel,
        "client_argv":[args[0],args[1]],"cancel_exit_code":cancel_output.status.code(),
        "cancel_stdout":String::from_utf8_lossy(&cancel_output.stdout),
        "cancel_stderr":String::from_utf8_lossy(&cancel_output.stderr),"cancel_reply":cancel_reply,
        "events_after_cancel":events_after_cancel,"balances_after_cancel":balance(&db),
        "replay_stdout":String::from_utf8_lossy(&replay_output.stdout),"replay_reply":replay_reply,
        "later_launch_reply":later_launch_reply,"worker_count":worker_rows(&marker).len()
    }));
}

#[test]
fn actual_client_loses_committed_cancel_reply_then_exact_retry_replays() {
    let (dir, db, revision) = setup("lost-cancel-reply-job", true);
    let marker = dir.path().join("worker.jsonl");
    let release = dir.path().join("worker.release");
    let _release = Release(release.clone());
    let trusted = profile(&marker, &release);
    let gateway = Gateway::start(dir.path(), "lost-cancel-reply-gateway", &db, &admin_policy(), &trusted);
    let proxy_socket = dir.path().join("lost-cancel-reply-proxy.sock");
    let proxy = drop_reply_proxy(proxy_socket.clone(), gateway.socket.clone());

    let before = events(&db, "lost-cancel-reply-job");
    let balances_before = balance(&db);
    let args = ["cancel-unlaunched", "lost-cancel-reply-job"];
    let lost_output = client(&proxy_socket, &args);
    let lost_response = client_json(&lost_output);
    let proxy_record = proxy.join().expect("drop-reply proxy panicked");
    assert_eq!(lost_output.status.code(), Some(4), "lost native cancellation reply: {lost_response}");
    assert_eq!(lost_response["ok"], false);
    assert_eq!(lost_response["outcome"], "outcome_unknown");
    assert_eq!(proxy_record["actual_gateway_response"]["ok"], true);
    assert_eq!(proxy_record["actual_gateway_response"]["result"]["finalization"], "CLOSED");
    assert!(proxy_record["additional_client_requests"].as_array().unwrap().is_empty(),
        "client must not retry after the lost cancellation response");

    let events_after_commit = events(&db, "lost-cancel-reply-job");
    assert_eq!(job(&db, "lost-cancel-reply-job")["state"], "CLOSED");
    assert_eq!(job(&db, "lost-cancel-reply-job")["outcome"], "cancelled");
    assert_eq!(events_after_commit.iter().filter(|event| event["kind"] == "FINALIZED").count(), 1);
    assert!(!events_after_commit.iter().any(|event| event["kind"] == "LAUNCH_INTENT"));
    assert_eq!(remaining(&db), 0);

    let before_replay = events(&db, "lost-cancel-reply-job");
    let replay_output = client(&gateway.socket, &args);
    let replay_response = client_json(&replay_output);
    assert_eq!(replay_output.status.code(), Some(0));
    assert_eq!(replay_response["ok"], true);
    assert_eq!(replay_response["result"]["finalization"], "CLOSED_REPLAY");
    let after_replay = events(&db, "lost-cancel-reply-job");
    assert_eq!(after_replay, before_replay, "exact retry adds no finalization/intent evidence");
    assert_eq!(after_replay.iter().filter(|event| event["kind"] == "FINALIZED").count(), 1);
    let later_launch_request = launch("lost-cancel-reply-job", "must-not-launch", revision);
    let later_launch_reply = gateway.send(&later_launch_request);
    assert_eq!(later_launch_reply["ok"], false);
    assert_eq!(events(&db, "lost-cancel-reply-job"), after_replay);
    assert!(worker_rows(&marker).is_empty());

    persist("lost-cancel-reply-history.json", json!({"source_sha256":source_hashes(),
        "cancel_client_argv":[args[0],args[1]],"events_before":before,"balances_before":balances_before,
        "lost_client_exit_code":lost_output.status.code(),
        "lost_client_stdout":String::from_utf8_lossy(&lost_output.stdout),
        "lost_client_stderr":String::from_utf8_lossy(&lost_output.stderr),
        "lost_client_response":lost_response,"proxy_record":proxy_record,
        "events_after_committed_cancel":events_after_commit,"balances_after_committed_cancel":balance(&db),
        "exact_retry_exit_code":replay_output.status.code(),
        "exact_retry_stdout":String::from_utf8_lossy(&replay_output.stdout),
        "exact_retry_response":replay_response,"events_after_retry":after_replay,
        "later_launch_request":later_launch_request,"later_launch_reply":later_launch_reply,
        "worker_count":worker_rows(&marker).len()}));
}

#[test]
fn reserved_unlaunched_job_can_be_canceled_and_replayed() {
    let (dir, db, _revision) = setup("reserved-cancel-job", false);
    let marker = dir.path().join("worker.jsonl");
    let release = dir.path().join("worker.release");
    let _release = Release(release.clone());
    let trusted = profile(&marker, &release);
    let gateway = Gateway::start(dir.path(), "reserved-cancel", &db, &admin_policy(), &trusted);
    let before = events(&db, "reserved-cancel-job");
    let balances_before = balance(&db);
    let first = gateway.send(&cancel("reserved-cancel-job"));
    assert_eq!(first["ok"], true, "RESERVED cancellation: {first}");
    assert_eq!(job(&db, "reserved-cancel-job")["state"], "CLOSED");
    assert_eq!(job(&db, "reserved-cancel-job")["outcome"], "cancelled");
    let after = events(&db, "reserved-cancel-job");
    assert_eq!(after.iter().filter(|event| event["kind"] == "FINALIZED").count(), 1);
    assert!(!after.iter().any(|event| event["kind"] == "LAUNCH_INTENT"));
    assert_eq!(remaining(&db), 0);
    let replay = gateway.send(&cancel("reserved-cancel-job"));
    assert_eq!(replay["ok"], true);
    assert_eq!(replay["result"]["finalization"], "CLOSED_REPLAY");
    assert_eq!(events(&db, "reserved-cancel-job"), after);
    persist("reserved-cancel.json", json!({"source_sha256":source_hashes(),"first_reply":first,
        "replay_reply":replay,"events_before":before,"events_after":after,
        "balances_before":balances_before,"balances_after":balance(&db)}));
}

#[test]
fn launched_live_exited_and_closed_jobs_refuse_unlaunched_cancel_unchanged() {
    // Live launch: failed cancellation leaves the exact Child alive and capacity held.
    {
        let (dir, db, revision) = setup("live-cancel-refusal", true);
        let marker = dir.path().join("worker.jsonl");
        let release = dir.path().join("worker.release");
        let _release = Release(release.clone());
        let trusted = profile(&marker, &release);
        let gateway = Gateway::start(dir.path(), "live-refusal", &db, &admin_policy(), &trusted);
        let launch_reply = gateway.send(&launch("live-cancel-refusal", "live-launch", revision));
        assert_eq!(launch_reply["ok"], true);
        wait_for(&marker);
        let worker = worker_rows(&marker);
        assert_eq!(worker.len(), 1);
        let before = events(&db, "live-cancel-refusal");
        let balances_before = balance(&db);
        let refused = gateway.send(&cancel("live-cancel-refusal"));
        assert_eq!(refused["ok"], false);
        assert_eq!(events(&db, "live-cancel-refusal"), before);
        assert_eq!(job(&db, "live-cancel-refusal")["state"], "RUNNING");
        assert_eq!(balance(&db), balances_before);
        assert!(worker_alive(worker[0]["pid"].as_u64().unwrap() as u32, worker[0]["start_token"].as_str().unwrap()));
        let stop = gateway.send(&json!({"op":"local_stop","job_id":"live-cancel-refusal","launch_id":"live-launch","stop_id":"cleanup-stop"}));
        assert_eq!(stop["ok"], true);
        let finish = gateway.send(&json!({"op":"local_finalize","job_id":"live-cancel-refusal","launch_id":"live-launch","outcome":"cancelled"}));
        assert_eq!(finish["ok"], true);
        persist("launched-live-refusal.json", json!({"source_sha256":source_hashes(),"launch_reply":launch_reply,
            "worker":worker[0],"cancel_request":cancel("live-cancel-refusal"),"cancel_reply":refused,
            "events_before":before,"balances_before":balances_before,"worker_alive_after_refusal":true,
            "cleanup_stop":stop,"cleanup_finalize":finish}));
    }

    // Exited-but-not-finalized launch still has intent history and cannot take the unlaunched route.
    {
        let (dir, db, revision) = setup("exited-cancel-refusal", true);
        let marker = dir.path().join("worker.jsonl");
        let release = dir.path().join("worker.release");
        let trusted = profile(&marker, &release);
        let gateway = Gateway::start(dir.path(), "exited-refusal", &db, &admin_policy(), &trusted);
        let launch_reply = gateway.send(&launch("exited-cancel-refusal", "exited-launch", revision));
        assert_eq!(launch_reply["ok"], true);
        wait_for(&marker);
        let worker = worker_rows(&marker);
        fs::write(&release, b"release worker\n").unwrap();
        let poll_reply = wait_until_exit(&gateway, &db, "exited-cancel-refusal", "exited-launch");
        let before = events(&db, "exited-cancel-refusal");
        let balances_before = balance(&db);
        let refused = gateway.send(&cancel("exited-cancel-refusal"));
        assert_eq!(refused["ok"], false);
        assert_eq!(events(&db, "exited-cancel-refusal"), before);
        assert_eq!(job(&db, "exited-cancel-refusal")["state"], "EXIT_OBSERVED");
        assert_eq!(balance(&db), balances_before);
        let finish = gateway.send(&json!({"op":"local_finalize","job_id":"exited-cancel-refusal","launch_id":"exited-launch","outcome":"completed"}));
        assert_eq!(finish["ok"], true);
        persist("launched-exited-refusal.json", json!({"source_sha256":source_hashes(),"launch_reply":launch_reply,
            "worker":worker[0],"poll_reply":poll_reply,"cancel_reply":refused,"events_before":before,
            "balances_before":balances_before,"cleanup_finalize":finish}));
    }

    // Even a launched job already CLOSED as cancelled is outside the unlaunched replay class.
    {
        let (dir, db, revision) = setup("closed-launched-refusal", true);
        let marker = dir.path().join("worker.jsonl");
        let release = dir.path().join("worker.release");
        let trusted = profile(&marker, &release);
        let gateway = Gateway::start(dir.path(), "closed-refusal", &db, &admin_policy(), &trusted);
        let launch_reply = gateway.send(&launch("closed-launched-refusal", "closed-launch", revision));
        assert_eq!(launch_reply["ok"], true);
        wait_for(&marker);
        let worker = worker_rows(&marker);
        let stop = gateway.send(&json!({"op":"local_stop","job_id":"closed-launched-refusal","launch_id":"closed-launch","stop_id":"closed-stop"}));
        assert_eq!(stop["ok"], true);
        let finish = gateway.send(&json!({"op":"local_finalize","job_id":"closed-launched-refusal","launch_id":"closed-launch","outcome":"cancelled"}));
        assert_eq!(finish["ok"], true);
        let before = events(&db, "closed-launched-refusal");
        let balances_before = balance(&db);
        let refused = gateway.send(&cancel("closed-launched-refusal"));
        assert_eq!(refused["ok"], false);
        assert_eq!(events(&db, "closed-launched-refusal"), before);
        assert_eq!(job(&db, "closed-launched-refusal")["state"], "CLOSED");
        assert_eq!(balance(&db), balances_before);
        persist("launched-closed-refusal.json", json!({"source_sha256":source_hashes(),"launch_reply":launch_reply,
            "worker":worker[0],"stop_reply":stop,"prior_finalize_reply":finish,"cancel_reply":refused,
            "events_before":before,"balances_before":balances_before}));
    }

    // Expiration is terminal; cancellation cannot rewrite EXPIRED as CLOSED/cancelled.
    {
        let (dir, db, _revision) = setup("expired-cancel-refusal", false);
        let mut store = Store::open(&db).unwrap();
        assert_eq!(store.expire_unlaunched(now() + 100_000).unwrap(), 1);
        drop(store);
        let marker = dir.path().join("worker.jsonl");
        let release = dir.path().join("worker.release");
        let trusted = profile(&marker, &release);
        let gateway = Gateway::start(dir.path(), "expired-refusal", &db, &admin_policy(), &trusted);
        let before = events(&db, "expired-cancel-refusal");
        let balances_before = balance(&db);
        let refused = gateway.send(&cancel("expired-cancel-refusal"));
        assert_eq!(refused["ok"], false);
        assert_eq!(events(&db, "expired-cancel-refusal"), before);
        assert_eq!(job(&db, "expired-cancel-refusal")["state"], "EXPIRED");
        assert_eq!(balance(&db), balances_before);
        persist("expired-cancel-refusal.json", json!({"source_sha256":source_hashes(),
            "cancel_request":cancel("expired-cancel-refusal"),"cancel_reply":refused,
            "events_before":before,"balances_before":balances_before}));
    }
}

#[test]
fn unlaunched_cancel_rejects_wrong_role_scope_extra_fields_and_invalid_ids() {
    let (dir, db, _revision) = setup("protocol-cancel-job", true);
    let marker = dir.path().join("worker.jsonl");
    let release = dir.path().join("worker.release");
    let trusted = profile(&marker, &release);
    let admin = Gateway::start(dir.path(), "protocol-admin", &db, &admin_policy(), &trusted);
    let before = events(&db, "protocol-cancel-job");
    let balances_before = balance(&db);

    let mut extra = cancel("protocol-cancel-job");
    extra["launch_id"] = json!("caller-selector");
    let extra_reply = admin.send(&extra);
    assert_eq!(extra_reply["ok"], false, "deny unknown request fields");
    let empty_id_reply = admin.send(&cancel(""));
    assert_eq!(empty_id_reply["ok"], false, "deny invalid job IDs");
    let missing_id_reply = admin.send(&cancel("does-not-exist"));
    assert_eq!(missing_id_reply["ok"], false, "deny unknown job ID");

    let wrong_scope_profile = json!({"program":std::env::current_exe().unwrap(),"args":[],"cwd":std::env::current_dir().unwrap(),"env":{},
        "account_id":"different-account","project_id":PROJECT,"environment_id":ENVIRONMENT});
    let wrong_scope = Gateway::start(dir.path(), "wrong-scope", &db, &admin_policy(), &wrong_scope_profile);
    let wrong_scope_reply = wrong_scope.send(&cancel("protocol-cancel-job"));
    assert_eq!(wrong_scope_reply["ok"], false, "trusted fixed-profile scope mismatch must refuse");

    let viewer = Gateway::start(dir.path(), "viewer", &db, &viewer_policy(), &trusted);
    let wrong_role_reply = viewer.send(&cancel("protocol-cancel-job"));
    assert_eq!(wrong_role_reply["ok"], false, "local cancellation requires administrator role");

    assert_eq!(events(&db, "protocol-cancel-job"), before);
    assert_eq!(job(&db, "protocol-cancel-job")["state"], "AUTHORIZED");
    assert_eq!(balance(&db), balances_before);
    persist("cancel-protocol-rejections.json", json!({"source_sha256":source_hashes(),
        "valid_shape":cancel("protocol-cancel-job"),"extra_fields_request":extra,"extra_fields_reply":extra_reply,
        "empty_job_reply":empty_id_reply,"unknown_job_reply":missing_id_reply,
        "wrong_scope_reply":wrong_scope_reply,"wrong_role_reply":wrong_role_reply,
        "events_before":before,"balances_before":balances_before}));
}

#[test]
fn two_gateway_launch_cancel_orders_and_race_have_only_observed_outcomes() {
    let mut records = Vec::new();
    // Deterministic cancellation-first history.
    {
        let (dir, db, revision) = setup("cancel-first-job", true);
        let marker = dir.path().join("cancel-first-worker.jsonl");
        let release = dir.path().join("cancel-first-release");
        let _release = Release(release.clone());
        let trusted = profile(&marker, &release);
        let launcher = Gateway::start(dir.path(), "launcher", &db, &admin_policy(), &trusted);
        let canceller = Gateway::start(dir.path(), "canceller", &db, &admin_policy(), &trusted);
        let before = events(&db, "cancel-first-job");
        let cancel_request = cancel("cancel-first-job");
        let cancel_reply = canceller.send(&cancel_request);
        let events_after_cancel = events(&db, "cancel-first-job");
        let launch_request = launch("cancel-first-job", "cancel-first-launch", revision);
        let launch_reply = launcher.send(&launch_request);
        assert_eq!(cancel_reply["ok"], true);
        assert_eq!(launch_reply["ok"], false);
        assert!(worker_rows(&marker).is_empty());
        assert_eq!(events(&db, "cancel-first-job"), events_after_cancel);
        assert_eq!(remaining(&db), 0);
        records.push(json!({"case":"deterministic-cancel-first","cancel_request":cancel_request,
            "cancel_reply":cancel_reply,"launch_request":launch_request,"launch_reply":launch_reply,
            "events_before":before,"events_after_cancel":events_after_cancel,"worker_count":0,
            "capacity_after":remaining(&db)}));
    }

    // Deterministic launch-first history; the child remains live until cleanup.
    {
        let (dir, db, revision) = setup("launch-first-job", true);
        let marker = dir.path().join("launch-first-worker.jsonl");
        let release = dir.path().join("launch-first-release");
        let _release = Release(release.clone());
        let trusted = profile(&marker, &release);
        let launcher = Gateway::start(dir.path(), "launcher", &db, &admin_policy(), &trusted);
        let canceller = Gateway::start(dir.path(), "canceller", &db, &admin_policy(), &trusted);
        let launch_request = launch("launch-first-job", "launch-first-launch", revision);
        let launch_reply = launcher.send(&launch_request);
        assert_eq!(launch_reply["ok"], true);
        wait_for(&marker);
        let worker = worker_rows(&marker);
        let before_cancel = events(&db, "launch-first-job");
        let balances_before = balance(&db);
        let cancel_request = cancel("launch-first-job");
        let cancel_reply = canceller.send(&cancel_request);
        assert_eq!(cancel_reply["ok"], false);
        assert_eq!(events(&db, "launch-first-job"), before_cancel);
        assert_eq!(balance(&db), balances_before);
        assert!(worker_alive(worker[0]["pid"].as_u64().unwrap() as u32, worker[0]["start_token"].as_str().unwrap()));
        let stop = launcher.send(&json!({"op":"local_stop","job_id":"launch-first-job","launch_id":"launch-first-launch","stop_id":"race-cleanup-stop"}));
        assert_eq!(stop["ok"], true);
        let finish = launcher.send(&json!({"op":"local_finalize","job_id":"launch-first-job","launch_id":"launch-first-launch","outcome":"cancelled"}));
        assert_eq!(finish["ok"], true);
        records.push(json!({"case":"deterministic-launch-first","launch_request":launch_request,
            "launch_reply":launch_reply,"worker":worker[0],"cancel_request":cancel_request,
            "cancel_reply":cancel_reply,"events_before_cancel":before_cancel,
            "balances_before_cancel":balances_before,"cleanup_stop":stop,"cleanup_finalize":finish}));
    }

    // Concurrent calls use distinct real gateway processes and the same Store.
    {
        let (dir, db, revision) = setup("concurrent-race-job", true);
        let marker = dir.path().join("concurrent-worker.jsonl");
        let release = dir.path().join("concurrent-release");
        let _release = Release(release.clone());
        let trusted = profile(&marker, &release);
        let launcher = Gateway::start(dir.path(), "race-launcher", &db, &admin_policy(), &trusted);
        let canceller = Gateway::start(dir.path(), "race-canceller", &db, &admin_policy(), &trusted);
        let launch_request = launch("concurrent-race-job", "concurrent-launch", revision);
        let cancel_request = cancel("concurrent-race-job");
        let barrier = Arc::new(Barrier::new(3));
        let launch_barrier = barrier.clone();
        let cancel_barrier = barrier.clone();
        let launch_socket = launcher.socket.clone();
        let cancel_socket = canceller.socket.clone();
        let launch_copy = launch_request.clone();
        let cancel_copy = cancel_request.clone();
        let launch_thread = thread::spawn(move || { launch_barrier.wait(); send_to(&launch_socket, &launch_copy) });
        let cancel_thread = thread::spawn(move || { cancel_barrier.wait(); send_to(&cancel_socket, &cancel_copy) });
        barrier.wait();
        let launch_reply = launch_thread.join().unwrap();
        let cancel_reply = cancel_thread.join().unwrap();
        let final_job = job(&db, "concurrent-race-job");
        let final_events = events(&db, "concurrent-race-job");
        let workers = worker_rows(&marker);
        if launch_reply["ok"] == true {
            assert_eq!(cancel_reply["ok"], false);
            assert_eq!(workers.len(), 1);
            assert_eq!(final_job["state"], "RUNNING");
            assert!(final_events.iter().any(|event| event["kind"] == "LAUNCH_INTENT"));
            assert!(final_events.iter().any(|event| event["kind"] == "LAUNCH_STARTED_OBSERVED"));
            assert_eq!(remaining(&db), 50);
            let stop = launcher.send(&json!({"op":"local_stop","job_id":"concurrent-race-job","launch_id":"concurrent-launch","stop_id":"concurrent-cleanup-stop"}));
            assert_eq!(stop["ok"], true);
            let finish = launcher.send(&json!({"op":"local_finalize","job_id":"concurrent-race-job","launch_id":"concurrent-launch","outcome":"cancelled"}));
            assert_eq!(finish["ok"], true);
            records.push(json!({"case":"concurrent","observed_outcome":"launch_reply_succeeded_cancel_refused",
                "launch_request":launch_request,"launch_reply":launch_reply,"cancel_request":cancel_request,
                "cancel_reply":cancel_reply,"job_before_cleanup":final_job,"events_before_cleanup":final_events,
                "worker":workers[0],"cleanup_stop":stop,"cleanup_finalize":finish,
                "capacity_after_cleanup":remaining(&db)}));
        } else {
            assert_eq!(cancel_reply["ok"], true);
            assert!(workers.is_empty());
            assert_eq!(final_job["state"], "CLOSED");
            assert_eq!(final_job["outcome"], "cancelled");
            assert!(!final_events.iter().any(|event| event["kind"] == "LAUNCH_INTENT"));
            assert_eq!(remaining(&db), 0);
            records.push(json!({"case":"concurrent","observed_outcome":"cancel_reply_succeeded_launch_refused",
                "launch_request":launch_request,"launch_reply":launch_reply,"cancel_request":cancel_request,
                "cancel_reply":cancel_reply,"job":final_job,"events":final_events,"worker_count":0,
                "capacity_after":remaining(&db)}));
        }
    }
    persist("two-gateway-launch-cancel-orders.json", json!({"source_sha256":source_hashes(),"records":records}));
}
