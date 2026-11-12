//! Native Unix-gateway histories for trusted local execution.
//!
//! The gateway is the process owner under test. Its only executable is this
//! fixed test binary in a bounded helper mode; requests never supply a command
//! or process identity. Raw JSON observations are retained when the evidence
//! directory environment variable is set by the focused run.
use ases_resource_control::{now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::catalog::Account;
use ases_resource_control::access::{Grant, Policy};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::os::unix::net::UnixStream;
use std::os::unix::fs::PermissionsExt;
use std::os::unix::process::ExitStatusExt;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

const ACCOUNT: &str = "local-test-account";
const PROJECT: &str = "local-test-project";
const ENVIRONMENT: &str = "local-test-environment";

fn policy_admin() -> Policy {
    Policy { administrators: vec![unsafe { libc::geteuid() }], callers: vec![] }
}

fn policy_viewer() -> Policy {
    Policy { administrators: vec![], callers: vec![Grant {
        uid: unsafe { libc::geteuid() }, role: "viewer".into(),
        accounts: vec![ACCOUNT.into()], projects: vec![PROJECT.into()],
    }] }
}

fn account() -> Account {
    Account { id: ACCOUNT.into(), provider: "local".into(), payer_ref: "test-only".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec![PROJECT.into()],
        source: "synthetic-native-local-gateway-test".into(), observed_at: now(), ttl_seconds: 3600 }
}

fn meter() -> Meter {
    Meter { id: "local-test-meter".into(), account: ACCOUNT.into(), provider: "local".into(),
        product: "fixed-test-worker".into(), period: "local-gateway-test".into(), unit: "units".into(),
        limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-local-gateway-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false }
}

fn environment() -> Environment {
    Environment { id: ENVIRONMENT.into(), account: ACCOUNT.into(), provider: "local".into(),
        max_parallel: 1, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-local-gateway-test".into() }
}

fn proposal(job: &str) -> Proposal {
    Proposal { job_id: job.into(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(), estimated_wall_seconds: 60,
        claims: vec![Claim { meter_id: "local-test-meter".into(), amount: 50 }],
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

fn profile(_dir: &Path, marker: &Path, release: &Path, mode: &str) -> Value {
    json!({
        "program": std::env::current_exe().unwrap(),
        "args": ["--exact", "local_gateway_fixed_worker", "--nocapture"],
        "cwd": std::env::current_dir().unwrap(),
        "env": {
            "ASES_LOCAL_WORKER_MARKER": marker,
            "ASES_LOCAL_WORKER_RELEASE": release,
            "ASES_LOCAL_WORKER_MODE": mode
        },
        "account_id": ACCOUNT, "project_id": PROJECT, "environment_id": ENVIRONMENT
    })
}

struct Gateway { child: Child, socket: PathBuf }

struct Release(PathBuf);
impl Drop for Release { fn drop(&mut self) { let _ = fs::write(&self.0, b"release\n"); } }

impl Gateway {
    fn start(dir: &Path, db: &Path, policy: &Policy, profile: &Value) -> Self {
        let socket = dir.join("gateway.sock");
        let policy_path = dir.join("policy.json");
        let profile_path = dir.join("profile.json");
        fs::write(&policy_path, serde_json::to_vec(policy).unwrap()).unwrap();
        fs::write(&profile_path, serde_json::to_vec(profile).unwrap()).unwrap();
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

    fn send(&self, request: Value) -> (Value, Value) {
        let mut stream = UnixStream::connect(&self.socket).unwrap();
        let raw = serde_json::to_value(&request).unwrap();
        stream.write_all(serde_json::to_string(&request).unwrap().as_bytes()).unwrap();
        stream.shutdown(std::net::Shutdown::Write).unwrap();
        let mut bytes = Vec::new();
        stream.read_to_end(&mut bytes).unwrap();
        (serde_json::from_slice(&bytes).unwrap(), raw)
    }

    fn stop(&mut self) -> Option<i32> {
        let _ = self.child.kill();
        self.child.wait().ok().and_then(|s| s.signal()).or_else(|| {
            self.child.try_wait().ok().flatten().and_then(|s| s.code())
        })
    }
}

impl Drop for Gateway {
    fn drop(&mut self) { let _ = self.stop(); }
}

fn balances(store: &mut Store) -> Value {
    serde_json::to_value(store.balances(now()).unwrap()).unwrap()
}

fn wait_for(path: &Path) {
    let until = Instant::now() + Duration::from_secs(10);
    while Instant::now() < until {
        if path.exists() { return; }
        thread::sleep(Duration::from_millis(10));
    }
    panic!("fixed native worker did not create marker {}", path.display());
}

fn source_hashes() -> Value {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut out = serde_json::Map::new();
    for relative in ["src/bin/resource-gateway.rs", "src/local.rs", "src/lib.rs",
        "tests/native_local_gateway.rs", "tests/native_session_client.rs", "tests/native_session_drive.rs", "tests/native_termination.rs",
        "../docs/research/phase-ii-local-execution/INTERFACE.md"] {
        if let Ok(bytes) = fs::read(root.join(relative)) {
            out.insert(relative.into(), json!(format!("{:x}", Sha256::digest(bytes))));
        }
    }
    Value::Object(out)
}

fn persist(name: &str, value: Value) {
    if let Some(dir) = std::env::var_os("ASES_LOCAL_GATEWAY_EVIDENCE_DIR") {
        let dir = PathBuf::from(dir);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join(name), serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

/// Spawned by the real gateway using the fixed test-binary command in profile().
#[test]
fn local_gateway_fixed_worker() {
    let Ok(mode) = std::env::var("ASES_LOCAL_WORKER_MODE") else { return };
    let marker = PathBuf::from(std::env::var_os("ASES_LOCAL_WORKER_MARKER").unwrap());
    let release = PathBuf::from(std::env::var_os("ASES_LOCAL_WORKER_RELEASE").unwrap());
    let pid = std::process::id();
    let stat = fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let start_token = stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap().to_string();
    let raw = json!({"pid":pid,"start_token":start_token,"mode":mode});
    let mut file = OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file, &raw).unwrap();
    file.write_all(b"\n").unwrap();
    file.sync_all().unwrap();
    let bound = if mode == "bounded" { 5 } else { 20 };
    let until = Instant::now() + Duration::from_secs(bound);
    while !release.exists() && Instant::now() < until { thread::sleep(Duration::from_millis(10)); }
    std::process::exit(0);
}

#[test]
fn gateway_owns_one_fixed_child_and_stop_is_durable_exact_and_separate_from_finalize() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), "gateway-job");
    let marker = dir.path().join("worker.jsonl");
    let release = dir.path().join("worker.release");
    let _release = Release(release.clone());
    let profile = profile(dir.path(), &marker, &release, "hold");
    let gateway = Gateway::start(dir.path(), &db, &policy_admin(), &profile);
    let launch = json!({"op":"local_launch","job_id":"gateway-job","launch_id":"gateway-launch","expected_catalog":revision});
    let (launched, _) = gateway.send(launch.clone());
    assert_eq!(launched["ok"], true, "native launch response: {launched}");
    assert_eq!(launched["result"]["state"], "running");
    wait_for(&marker);
    let worker_raw = fs::read_to_string(&marker).unwrap();
    let workers: Vec<Value> = worker_raw.lines().map(|line| serde_json::from_str(line).unwrap()).collect();
    assert_eq!(workers.len(), 1, "exactly one fixed worker was spawned");
    let worker = workers[0].clone();

    let (replay, _) = gateway.send(launch.clone());
    assert_eq!(replay["ok"], true);
    assert_eq!(replay["result"]["state"], "running");
    assert_eq!(fs::read_to_string(&marker).unwrap(), worker_raw, "launch replay must not create a child");

    let mut rejected = Vec::new();
    for (field, value) in [("command", json!("/bin/true")), ("pid", json!(worker["pid"])),
        ("identity", json!({"pid":worker["pid"],"start_token":worker["start_token"]})),
        ("environment", json!({"BAD":"caller-controlled"}))] {
        let mut request = launch.clone();
        request[field] = value;
        let (reply, raw) = gateway.send(request);
        assert_eq!(reply["ok"], false, "caller field {field} must be rejected: {reply}");
        rejected.push(json!({"request":raw,"response":reply}));
    }
    assert_eq!(fs::read_to_string(&marker).unwrap(), worker_raw, "rejected inputs cannot spawn another child");

    let mut store = Store::open(&db).unwrap();
    let events_after_launch = store.event_log(Some("gateway-job")).unwrap();
    let balances_before_stop = balances(&mut store);
    let job_running = store.job("gateway-job").unwrap();
    assert_eq!(job_running["state"], "RUNNING");
    let (polled_running, _) = gateway.send(json!({"op":"local_poll","job_id":"gateway-job","launch_id":"gateway-launch"}));
    assert_eq!(polled_running["ok"], true);
    assert_eq!(polled_running["result"]["state"], "running");
    let (resume_running, _) = gateway.send(json!({"op":"local_resume","job_id":"gateway-job","launch_id":"gateway-launch"}));
    assert_eq!(resume_running["ok"], true);
    assert_eq!(resume_running["result"]["local_state"], "owned_child_unobserved");
    assert_eq!(resume_running["result"]["resume_view"]["presentLiveness"], "unknown");
    let view_bytes = serde_json::to_vec(&resume_running["result"]["resume_view"]).unwrap();
    assert!(view_bytes.len() <= 2048, "compact resume view size {}", view_bytes.len());

    // A separate actual gateway peer with an administrator grant still cannot
    // operate outside its startup profile's trusted account/project scope.
    let mismatch_dir = dir.path().join("mismatched-profile");
    fs::create_dir(&mismatch_dir).unwrap();
    let mut mismatched_profile = profile.clone();
    mismatched_profile["project_id"] = json!("different-trusted-project");
    let mismatch_gateway = Gateway::start(&mismatch_dir, &db, &policy_admin(), &mismatched_profile);
    let mismatched_requests = vec![
        json!({"op":"local_resume","job_id":"gateway-job","launch_id":"gateway-launch"}),
        json!({"op":"local_stop","job_id":"gateway-job","launch_id":"gateway-launch","stop_id":"mismatch-stop"}),
        json!({"op":"local_finalize","job_id":"gateway-job","launch_id":"gateway-launch","outcome":"cancelled"}),
    ];
    let mut mismatch_records = Vec::new();
    for request in mismatched_requests {
        let (response, raw) = mismatch_gateway.send(request);
        assert_eq!(response["ok"], false, "trusted profile scope mismatch must deny operation: {response}");
        assert!(response["error"].as_str().unwrap().contains("scope"), "scope error response: {response}");
        assert_eq!(store.job("gateway-job").unwrap(), job_running);
        assert_eq!(store.event_log(Some("gateway-job")).unwrap(), events_after_launch);
        assert_eq!(balances(&mut store), balances_before_stop);
        mismatch_records.push(json!({"request":raw,"response":response}));
    }
    assert_eq!(fs::read_to_string(&marker).unwrap(), worker_raw,
        "wrong trusted profile could not stop the child owned by the real gateway");

    let wrong_launch_request = json!({"op":"local_stop","job_id":"gateway-job","launch_id":"wrong-launch","stop_id":"wrong-stop"});
    let (wrong_launch, _) = gateway.send(wrong_launch_request.clone());
    assert_eq!(wrong_launch["ok"], false, "wrong launch selector must fail");
    assert_eq!(store.event_log(Some("gateway-job")).unwrap(), events_after_launch);
    assert_eq!(balances(&mut store), balances_before_stop);

    let stop_request = json!({"op":"local_stop","job_id":"gateway-job","launch_id":"gateway-launch","stop_id":"gateway-stop"});
    let (stopped, _) = gateway.send(stop_request.clone());
    assert_eq!(stopped["ok"], true, "stop response: {stopped}");
    assert_eq!(stopped["result"]["state"], "exit_observed");
    assert_eq!(stopped["result"]["stop_id"], "gateway-stop");
    let events_after_stop = store.event_log(Some("gateway-job")).unwrap();
    let stop_event: Vec<_> = events_after_stop.iter().filter(|e| e["kind"] == "LOCAL_STOP_REQUESTED").collect();
    assert_eq!(stop_event.len(), 1);
    assert_eq!(stop_event[0]["event_id"], "local-stop:gateway-job");
    assert_eq!(stop_event[0]["payload"]["launch_id"], "gateway-launch");
    assert_eq!(stop_event[0]["payload"]["stop_id"], "gateway-stop");
    let exit_event: Vec<_> = events_after_stop.iter().filter(|e| e["kind"] == "LAUNCH_EXIT_OBSERVED").collect();
    assert_eq!(exit_event.len(), 1, "stop records exact Child wait evidence");
    assert_eq!(exit_event[0]["payload"]["launch_id"], "gateway-launch");
    assert_eq!(exit_event[0]["payload"]["process"]["pid"], worker["pid"]);
    assert_eq!(exit_event[0]["payload"]["process"]["start_token"], worker["start_token"]);
    assert_eq!(exit_event[0]["payload"]["status"]["kind"], "signal");
    assert_eq!(exit_event[0]["payload"]["status"]["signal"], 9);
    assert_eq!(store.job("gateway-job").unwrap()["state"], "RUNNING");
    assert_eq!(balances(&mut store), balances_before_stop, "stop and exit observation retain capacity");

    let (exit_launch_replay, _) = gateway.send(launch.clone());
    assert_eq!(exit_launch_replay["ok"], true);
    assert_eq!(exit_launch_replay["result"]["state"], "exit_observed",
        "a retained/reaped Child is not reported as currently running");
    let (stop_replay, _) = gateway.send(stop_request.clone());
    assert_eq!(stop_replay["ok"], true);
    assert_eq!(fs::read_to_string(&marker).unwrap(), worker_raw);
    let conflict_request = json!({"op":"local_stop","job_id":"gateway-job","launch_id":"gateway-launch","stop_id":"different-stop"});
    let (conflict, _) = gateway.send(conflict_request.clone());
    assert_eq!(conflict["ok"], false, "conflicting stop identity must be rejected");
    assert_eq!(store.event_log(Some("gateway-job")).unwrap(), events_after_stop);
    assert_eq!(balances(&mut store), balances_before_stop);

    let (resume_exit, _) = gateway.send(json!({"op":"local_resume","job_id":"gateway-job","launch_id":"gateway-launch"}));
    assert_eq!(resume_exit["ok"], true);
    assert_eq!(resume_exit["result"]["local_state"], "exit_observed");
    assert_eq!(resume_exit["result"]["resume_view"]["advisoryNextStep"], "finalize_observed_exit");
    let finalize_request = json!({"op":"local_finalize","job_id":"gateway-job","launch_id":"gateway-launch","outcome":"completed"});
    let (finalized, _) = gateway.send(finalize_request.clone());
    assert_eq!(finalized["ok"], true, "explicit finalize response: {finalized}");
    assert_eq!(store.job("gateway-job").unwrap()["state"], "CLOSED");
    let balances_after_finalize = balances(&mut store);
    assert_ne!(balances_after_finalize, balances_before_stop, "only finalize releases reserved capacity");
    let final_events = store.event_log(Some("gateway-job")).unwrap();
    assert_eq!(final_events.iter().filter(|e| e["kind"] == "LOCAL_STOP_REQUESTED").count(), 1);
    assert_eq!(final_events.iter().filter(|e| e["kind"] == "LAUNCH_EXIT_OBSERVED").count(), 1);
    assert_eq!(final_events.iter().filter(|e| e["kind"] == "FINALIZED").count(), 1);
    drop(store);

    persist("native-gateway-stop.json", json!({
        "source_sha256":source_hashes(), "worker_raw_line":worker_raw, "worker":worker,
        "launch_request":launch, "launch_response":launched, "launch_replay":replay,
        "rejected_caller_inputs":rejected, "events_after_launch":events_after_launch,
        "poll_running":polled_running, "mismatched_trusted_profile":mismatched_profile,
        "mismatched_profile_requests":mismatch_records,
        "balances_before_stop":balances_before_stop, "resume_running":resume_running,
        "wrong_launch_stop_request":wrong_launch_request, "wrong_launch_stop_response":wrong_launch,
        "stop_request":stop_request, "stop_response":stopped, "events_after_stop":events_after_stop,
        "launch_replay_after_exit":exit_launch_replay, "stop_replay":stop_replay,
        "conflicting_stop_request":conflict_request,
        "conflicting_stop_response":conflict, "resume_after_exit":resume_exit,
        "finalize_request":finalize_request, "finalize_response":finalized,
        "balances_after_finalize":balances_after_finalize, "events_after_finalize":final_events
    }));
}

#[test]
fn actual_viewer_peer_is_denied_local_execution_without_state_change() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), "viewer-job");
    let marker = dir.path().join("viewer-worker.jsonl");
    let release = dir.path().join("viewer-worker.release");
    let _release = Release(release.clone());
    let profile = profile(dir.path(), &marker, &release, "hold");
    let gateway = Gateway::start(dir.path(), &db, &policy_viewer(), &profile);
    let mut store = Store::open(&db).unwrap();
    let before_job = store.job("viewer-job").unwrap();
    let before_events = store.event_log(Some("viewer-job")).unwrap();
    let before_balances = balances(&mut store);
    let request = json!({"op":"local_launch","job_id":"viewer-job","launch_id":"viewer-launch","expected_catalog":revision});
    let (response, raw_request) = gateway.send(request);
    assert_eq!(response["ok"], false);
    assert!(response["error"].as_str().unwrap().contains("prohibited"), "actual viewer policy denial: {response}");
    assert!(!marker.exists(), "denied peer cannot start configured native worker");
    assert_eq!(store.job("viewer-job").unwrap(), before_job);
    assert_eq!(store.event_log(Some("viewer-job")).unwrap(), before_events);
    assert_eq!(balances(&mut store), before_balances);
    let events_after = store.event_log(Some("viewer-job")).unwrap();
    drop(store);
    persist("native-gateway-viewer-denial.json", json!({
        "source_sha256":source_hashes(), "peer_uid":unsafe {libc::geteuid()},
        "peer_role":"viewer", "request":raw_request, "response":response,
        "job_before":before_job, "events_before":before_events, "events_after":events_after,
        "balances_before":before_balances, "worker_marker_exists":false
    }));
}

#[test]
fn post_intent_spawn_failure_stays_unknown_and_holds_reservation() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), "spawn-failure-job");
    let marker = dir.path().join("must-not-exist.jsonl");
    let release = dir.path().join("spawn-failure.release");
    let _release = Release(release.clone());
    let mut profile = profile(dir.path(), &marker, &release, "hold");
    // This executable passes regular-file and X_OK preflight. The kernel then
    // rejects its absent absolute interpreter after the durable intent.
    let nonexistent_interpreter = dir.path().join("absent-fixed-interpreter");
    let loader_failure = dir.path().join("loader-failure-worker");
    fs::write(&loader_failure, format!("#!{}\nexit 0\n", nonexistent_interpreter.display())).unwrap();
    fs::set_permissions(&loader_failure, fs::Permissions::from_mode(0o755)).unwrap();
    profile["program"] = json!(loader_failure);
    let gateway = Gateway::start(dir.path(), &db, &policy_admin(), &profile);
    let mut store = Store::open(&db).unwrap();
    let request = json!({"op":"local_launch","job_id":"spawn-failure-job","launch_id":"spawn-failure-launch","expected_catalog":revision});
    let (response, raw_request) = gateway.send(request.clone());
    assert_eq!(response["ok"], false, "trusted profile spawn failure is visible: {response}");
    assert!(!marker.exists());
    let events_after_failure = store.event_log(Some("spawn-failure-job")).unwrap();
    assert_eq!(events_after_failure.iter().filter(|e| e["kind"] == "LAUNCH_INTENT").count(), 1);
    assert_eq!(events_after_failure.iter().filter(|e| e["kind"] == "LAUNCH_STARTED_OBSERVED").count(), 0);
    assert_eq!(events_after_failure.iter().filter(|e| e["kind"] == "LAUNCH_NOT_CREATED_OBSERVED").count(), 0,
        "post-intent spawn error remains unknown under the bounded local profile contract");
    assert_eq!(store.job("spawn-failure-job").unwrap()["state"], "LAUNCHING");
    let balances_after_failure = balances(&mut store);
    let (replay, raw_replay) = gateway.send(request);
    assert_eq!(replay["ok"], true);
    assert_eq!(replay["result"]["state"], "unknown");
    assert_eq!(store.event_log(Some("spawn-failure-job")).unwrap(), events_after_failure);
    assert_eq!(balances(&mut store), balances_after_failure);
    let finalize_request = json!({"op":"local_finalize","job_id":"spawn-failure-job","launch_id":"spawn-failure-launch","outcome":"failed"});
    let (finalize_response, raw_finalize) = gateway.send(finalize_request);
    assert_eq!(finalize_response["ok"], false, "unknown creation result cannot be finalized");
    assert_eq!(store.job("spawn-failure-job").unwrap()["state"], "LAUNCHING");
    assert_eq!(store.event_log(Some("spawn-failure-job")).unwrap(), events_after_failure);
    assert_eq!(balances(&mut store), balances_after_failure);
    drop(store);
    persist("native-gateway-post-intent-spawn-failure.json", json!({
        "source_sha256":source_hashes(), "trusted_profile_program":loader_failure,
        "absent_interpreter":nonexistent_interpreter,
        "request":raw_request, "response":response, "events_after_failure":events_after_failure,
        "balances_after_failure":balances_after_failure, "replay_request":raw_replay,
        "replay_response":replay, "finalize_request":raw_finalize,
        "finalize_response":finalize_response, "worker_marker_exists":false
    }));
}

fn sleep_copy(dir: &Path, name: &str) -> PathBuf {
    let path = dir.join(name);
    fs::copy("/bin/sleep", &path).unwrap();
    fs::set_permissions(&path, fs::Permissions::from_mode(0o755)).unwrap();
    path
}

fn preflight_profile(program: &Path, cwd: &Path) -> Value {
    json!({"program":program,"args":["0.05"],"cwd":cwd,"env":{},
        "account_id":ACCOUNT,"project_id":PROJECT,"environment_id":ENVIRONMENT})
}

#[test]
fn filesystem_preflight_preserves_authorized_job_for_repair_and_retry() {
    for case in ["missing-program", "non-executable-program", "missing-cwd", "non-directory-cwd"] {
        let dir = tempfile::tempdir().unwrap();
        let job = format!("preflight-{case}");
        let (db, revision) = setup(dir.path(), &job);
        let program = match case {
            "missing-program" => dir.path().join("worker-to-install"),
            "non-executable-program" => {
                let path = dir.path().join("worker-no-x");
                fs::copy("/bin/true", &path).unwrap();
                fs::set_permissions(&path, fs::Permissions::from_mode(0o644)).unwrap();
                path
            }
            _ => PathBuf::from("/bin/true"),
        };
        let cwd = match case {
            "missing-cwd" => dir.path().join("cwd-to-create"),
            "non-directory-cwd" => {
                let path = dir.path().join("cwd-file");
                fs::write(&path, b"not a directory").unwrap();
                path
            }
            _ => std::env::current_dir().unwrap(),
        };
        let profile = preflight_profile(&program, &cwd);
        let gateway = Gateway::start(dir.path(), &db, &policy_admin(), &profile);
        let request = json!({"op":"local_launch","job_id":job,"launch_id":"repair-launch","expected_catalog":revision});
        let (failed, _) = gateway.send(request.clone());
        assert_eq!(failed["ok"], false, "{case} must fail preflight: {failed}");
        let mut store = Store::open(&db).unwrap();
        assert_eq!(store.job(&job).unwrap()["state"], "AUTHORIZED", "{case} must not consume authorization");
        let before_repair = store.event_log(Some(&job)).unwrap();
        assert!(!before_repair.iter().any(|event| event["kind"] == "LAUNCH_INTENT"), "{case} created no launch intent");
        let balances_before_repair = balances(&mut store);
        assert_eq!(balances_before_repair[0]["active_reserved_remaining"], json!(50));
        drop(store);

        match case {
            "missing-program" => { fs::copy("/bin/true", &program).unwrap(); fs::set_permissions(&program, fs::Permissions::from_mode(0o755)).unwrap(); }
            "non-executable-program" => fs::set_permissions(&program, fs::Permissions::from_mode(0o755)).unwrap(),
            "missing-cwd" => fs::create_dir(&cwd).unwrap(),
            "non-directory-cwd" => { fs::remove_file(&cwd).unwrap(); fs::create_dir(&cwd).unwrap(); }
            _ => unreachable!(),
        }
        let (retried, _) = gateway.send(request.clone());
        assert_eq!(retried["ok"], true, "same authorized job succeeds after repairing {case}: {retried}");
        let store = Store::open(&db).unwrap();
        let after_retry = store.event_log(Some(&job)).unwrap();
        assert_eq!(after_retry.iter().filter(|event| event["kind"] == "LAUNCH_INTENT").count(), 1);
        assert_eq!(after_retry.iter().filter(|event| event["kind"] == "LAUNCH_STARTED_OBSERVED").count(), 1);
        let (replay, _) = gateway.send(request);
        assert_eq!(replay["ok"], true, "post-retry replay: {replay}");
        let after_replay = store.event_log(Some(&job)).unwrap();
        assert_eq!(after_replay.iter().filter(|event| event["kind"] == "LAUNCH_INTENT").count(), 1,
            "retry replay does not dispatch again");
        assert_eq!(after_replay.iter().filter(|event| event["kind"] == "LAUNCH_STARTED_OBSERVED").count(), 1);
        persist(&format!("native-gateway-preflight-{case}.json"), json!({
            "source_sha256":source_hashes(), "case":case, "profile":profile,
            "failed_preflight_response":failed, "events_before_repair":before_repair,
            "balances_before_repair":balances_before_repair, "retry_response":retried,
            "events_after_retry":after_retry, "replay_response":replay,
            "events_after_replay":after_replay
        }));
    }
}

#[test]
fn running_child_remains_owned_after_profile_executable_is_unlinked() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), "unlinked-program-job");
    let program = sleep_copy(dir.path(), "temporary-sleep");
    let profile = json!({"program":program,"args":["30"],"cwd":std::env::current_dir().unwrap(),"env":{},
        "account_id":ACCOUNT,"project_id":PROJECT,"environment_id":ENVIRONMENT});
    let gateway = Gateway::start(dir.path(), &db, &policy_admin(), &profile);
    let launch = json!({"op":"local_launch","job_id":"unlinked-program-job","launch_id":"unlinked-launch","expected_catalog":revision});
    let (started, _) = gateway.send(launch.clone());
    assert_eq!(started["ok"], true, "sleep child launched: {started}");
    fs::remove_file(&program).unwrap();

    let (replay, _) = gateway.send(launch.clone());
    assert_eq!(replay["ok"], true, "exact replay skips filesystem preflight: {replay}");
    assert_eq!(replay["result"]["state"], "running");
    let (poll, _) = gateway.send(json!({"op":"local_poll","job_id":"unlinked-program-job","launch_id":"unlinked-launch"}));
    assert_eq!(poll["ok"], true, "poll after unlink: {poll}");
    assert_eq!(poll["result"]["state"], "running");
    let (resume, _) = gateway.send(json!({"op":"local_resume","job_id":"unlinked-program-job","launch_id":"unlinked-launch"}));
    assert_eq!(resume["ok"], true, "resume after unlink: {resume}");
    assert_eq!(resume["result"]["local_state"], "owned_child_unobserved");
    let (stopped, _) = gateway.send(json!({"op":"local_stop","job_id":"unlinked-program-job","launch_id":"unlinked-launch","stop_id":"unlink-stop"}));
    assert_eq!(stopped["ok"], true, "stop after unlink: {stopped}");
    assert_eq!(stopped["result"]["state"], "exit_observed");
    let (finalized, _) = gateway.send(json!({"op":"local_finalize","job_id":"unlinked-program-job","launch_id":"unlinked-launch","outcome":"completed"}));
    assert_eq!(finalized["ok"], true, "finalize after unlink: {finalized}");
    let store = Store::open(&db).unwrap();
    assert_eq!(store.job("unlinked-program-job").unwrap()["state"], "CLOSED");
    let events = store.event_log(Some("unlinked-program-job")).unwrap();
    assert_eq!(events.iter().filter(|event| event["kind"] == "LAUNCH_INTENT").count(), 1);
    persist("native-gateway-unlinked-executable.json", json!({
        "source_sha256":source_hashes(), "program_path":program,
        "launch_request":launch, "launch_response":started,
        "program_unlinked_before_replay_poll_resume_stop_finalize":true,
        "replay_response":replay, "poll_response":poll, "resume_response":resume,
        "stop_response":stopped, "finalize_response":finalized, "events_after_finalize":events
    }));
}

