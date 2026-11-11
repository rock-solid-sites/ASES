//! Actual gateway-loss history: cold liveness is unknown and cannot be adopted.
//! The only launched executable is this fixed test binary. Cleanup releases the
//! worker through its bounded file gate; the saved process identity is evidence,
//! never a handle used to signal or adopt the child.
use ases_resource_control::{now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::access::{Grant, Policy};
use ases_resource_control::catalog::Account;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::os::unix::net::UnixStream;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

const ACCOUNT: &str = "cold-test-account";
const PROJECT: &str = "cold-test-project";
const ENVIRONMENT: &str = "cold-test-environment";
const JOB: &str = "cold-loss-job";
const LAUNCH: &str = "cold-loss-launch";

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
    Account { id: ACCOUNT.into(), provider: "local".into(), payer_ref: "cold-test-only".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec![PROJECT.into()],
        source: "synthetic-native-local-cold-test".into(), observed_at: now(), ttl_seconds: 3600 }
}

fn meter() -> Meter {
    Meter { id: "cold-test-meter".into(), account: ACCOUNT.into(), provider: "local".into(),
        product: "fixed-cold-worker".into(), period: "cold-gateway-test".into(), unit: "units".into(),
        limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-local-cold-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false }
}

fn environment() -> Environment {
    Environment { id: ENVIRONMENT.into(), account: ACCOUNT.into(), provider: "local".into(),
        max_parallel: 1, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-local-cold-test".into() }
}

fn proposal(job: &str) -> Proposal {
    Proposal { job_id: job.into(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(), estimated_wall_seconds: 60,
        claims: vec![Claim { meter_id: "cold-test-meter".into(), amount: 50 }],
        paid_spend_cap_micros: None, paid_spend_cap_currency: None, forecast_context: None }
}

fn setup(dir: &Path, job: &str) -> (PathBuf, i64) {
    let db = dir.join("cold-control.sqlite");
    let mut store = Store::open(&db).unwrap();
    store.register_account(&account()).unwrap();
    store.register_meter(&meter()).unwrap();
    store.register_environment(&environment()).unwrap();
    let revision = store.catalog_version().unwrap();
    store.reserve(&proposal(job), revision, now()).unwrap();
    store.acknowledge(job, &format!("cold-test-ack-{job}"), revision, now()).unwrap();
    drop(store);
    (db, revision)
}

fn profile(marker: &Path, release: &Path, exited: &Path) -> Value {
    json!({
        "program": std::env::current_exe().unwrap(),
        "args": ["--exact", "cold_gateway_fixed_worker", "--nocapture"],
        "cwd": std::env::current_dir().unwrap(),
        "env": {
            "ASES_COLD_WORKER_MARKER": marker,
            "ASES_COLD_WORKER_RELEASE": release,
            "ASES_COLD_WORKER_EXITED": exited
        },
        "account_id": ACCOUNT, "project_id": PROJECT, "environment_id": ENVIRONMENT
    })
}

struct Gateway { child: Child, socket: PathBuf }

impl Gateway {
    fn start(dir: &Path, name: &str, db: &Path, policy: &Policy, profile: &Value) -> Self {
        let socket = dir.join(format!("{name}.sock"));
        let policy_path = dir.join(format!("{name}-policy.json"));
        let profile_path = dir.join(format!("{name}-profile.json"));
        fs::write(&policy_path, serde_json::to_vec(policy).unwrap()).unwrap();
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

    fn request(&self, request: Value) -> Value {
        let mut stream = UnixStream::connect(&self.socket).unwrap();
        stream.write_all(serde_json::to_string(&request).unwrap().as_bytes()).unwrap();
        stream.shutdown(std::net::Shutdown::Write).unwrap();
        let mut bytes = Vec::new();
        stream.read_to_end(&mut bytes).unwrap();
        serde_json::from_slice(&bytes).unwrap()
    }

}

impl Drop for Gateway { fn drop(&mut self) { let _ = self.child.kill(); let _ = self.child.wait(); } }

struct Release(PathBuf);
impl Drop for Release { fn drop(&mut self) { let _ = fs::write(&self.0, b"release\n"); } }

fn events(db: &Path, job: &str) -> Value { serde_json::to_value(Store::open(db).unwrap().event_log(Some(job)).unwrap()).unwrap() }

fn balances(db: &Path) -> Value { serde_json::to_value(Store::open(db).unwrap().balances(now()).unwrap()).unwrap() }

fn worker_lines(marker: &Path) -> Vec<Value> {
    fs::read_to_string(marker).unwrap_or_default().lines()
        .map(|line| serde_json::from_str(line).unwrap()).collect()
}

fn wait_for(path: &Path) {
    let until = Instant::now() + Duration::from_secs(10);
    while Instant::now() < until {
        if path.exists() { return; }
        thread::sleep(Duration::from_millis(10));
    }
    panic!("fixed cold worker did not reach expected gate: {}", path.display());
}

fn source_hashes() -> Value {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut out = serde_json::Map::new();
    for relative in ["src/bin/resource-gateway.rs", "src/lib.rs", "src/main.rs", "tests/native_local_cold.rs"] {
        if let Ok(bytes) = fs::read(root.join(relative)) {
            out.insert(relative.into(), json!(format!("{:x}", Sha256::digest(bytes))));
        }
    }
    Value::Object(out)
}

fn record(records: &mut Vec<Value>, phase: &str, request: Value, response: Value, before: Value, after: Value) {
    records.push(json!({"phase":phase,"request":request,"response":response,
        "events_before":before,"events_after":after}));
}

fn persist(value: Value) {
    if let Some(dir) = std::env::var_os("ASES_LOCAL_COLD_EVIDENCE_DIR") {
        let dir = PathBuf::from(dir);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join("cold-history.json"), serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

fn balance_remaining(value: &Value) -> i64 {
    value.as_array().unwrap().iter()
        .find(|row| row.get("meter_id").and_then(Value::as_str) == Some("cold-test-meter"))
        .and_then(|row| row.get("active_reserved_remaining"))
        .and_then(Value::as_i64).unwrap()
}

/// Durable exact exit evidence survives loss of the native Child owner and
/// permits explicit finalization after restart.
fn cold_finalize_after_hot_exit(parent: &Path) -> Value {
    const EXIT_JOB: &str = "cold-exit-observed-job";
    const EXIT_LAUNCH: &str = "cold-exit-observed-launch";
    let dir = parent.join("exit-observed");
    fs::create_dir_all(&dir).unwrap();
    let (db, revision) = setup(&dir, EXIT_JOB);
    let marker = dir.join("worker-launch-counter.jsonl");
    let release_path = dir.join("worker-release");
    let exited = dir.join("worker-exited");
    let _release = Release(release_path.clone());
    let trusted = profile(&marker, &release_path, &exited);
    let mut records = Vec::new();

    let mut hot = Gateway::start(&dir, "gateway-hot-exit", &db, &admin_policy(), &trusted);
    let launch_request = json!({"op":"local_launch","job_id":EXIT_JOB,"launch_id":EXIT_LAUNCH,"expected_catalog":revision});
    let before_launch = events(&db, EXIT_JOB);
    let launch_reply = hot.request(launch_request.clone());
    wait_for(&marker);
    record(&mut records,"hot-launch",launch_request,launch_reply,before_launch,events(&db, EXIT_JOB));
    assert_eq!(worker_lines(&marker).len(),1);

    let stop_request = json!({"op":"local_stop","job_id":EXIT_JOB,"launch_id":EXIT_LAUNCH,"stop_id":"hot-stop-exit-1"});
    let before_stop = events(&db, EXIT_JOB);
    let stop_reply = hot.request(stop_request.clone());
    let after_stop = events(&db, EXIT_JOB);
    record(&mut records,"hot-stop-wait-exit",stop_request,stop_reply.clone(),before_stop,after_stop.clone());
    assert_eq!(stop_reply["ok"],true);
    assert_eq!(stop_reply["result"]["state"],"exit_observed");
    assert!(after_stop.as_array().unwrap().iter().any(|event|
        event["kind"] == "LAUNCH_EXIT_OBSERVED" && event["payload"]["launch_id"] == EXIT_LAUNCH));
    let before_loss = after_stop;
    hot.child.kill().unwrap();
    hot.child.wait().unwrap();
    drop(hot);
    let after_loss = events(&db, EXIT_JOB);

    let cold = Gateway::start(&dir,"gateway-cold-exit",&db,&admin_policy(),&trusted);
    let resume_request = json!({"op":"local_resume","job_id":EXIT_JOB,"launch_id":EXIT_LAUNCH});
    let before_resume = events(&db, EXIT_JOB);
    let resume_reply = cold.request(resume_request.clone());
    let after_resume = events(&db, EXIT_JOB);
    record(&mut records,"cold-resume-with-exit",resume_request,resume_reply.clone(),before_resume,after_resume.clone());
    assert_eq!(resume_reply["ok"],true);
    assert_eq!(resume_reply["result"]["local_state"],"unknown");
    assert_eq!(resume_reply["result"]["resume_view"]["evidence"]["outcome"]["kind"],"LAUNCH_EXIT_OBSERVED");

    let held = balances(&db);
    assert!(balance_remaining(&held) > 0,"durable exit evidence alone must retain the reservation");
    let finalize_request = json!({"op":"local_finalize","job_id":EXIT_JOB,"launch_id":EXIT_LAUNCH,"outcome":"completed"});
    let before_finalize = events(&db, EXIT_JOB);
    let finalize_reply = cold.request(finalize_request.clone());
    let after_finalize = events(&db, EXIT_JOB);
    record(&mut records,"cold-finalize-from-exact-exit",finalize_request,finalize_reply.clone(),before_finalize,after_finalize.clone());
    assert_eq!(finalize_reply["ok"],true,"exact durable exit evidence must allow explicit finalize after restart");
    let released = balances(&db);
    assert_eq!(balance_remaining(&released),0,"explicit cold finalization releases reserved capacity");

    json!({
        "job_id":EXIT_JOB,"launch_id":EXIT_LAUNCH,"catalog_revision":revision,
        "worker_launch_counter":worker_lines(&marker),"worker_exit_marker":exited.exists(),
        "gateway_before_loss_event_snapshot":before_loss,"gateway_after_loss_event_snapshot":after_loss,
        "held_balances_before_cold_finalize":held,"released_balances_after_cold_finalize":released,
        "records":records
    })
}

/// The only profile executable: records identity, then waits for release or timeout.
#[test]
fn cold_gateway_fixed_worker() {
    let Some(marker) = std::env::var_os("ASES_COLD_WORKER_MARKER") else { return };
    let marker = PathBuf::from(marker);
    let release = PathBuf::from(std::env::var_os("ASES_COLD_WORKER_RELEASE").unwrap());
    let exited = PathBuf::from(std::env::var_os("ASES_COLD_WORKER_EXITED").unwrap());
    let pid = std::process::id();
    let stat = fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let start_token = stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap().to_string();
    let evidence = json!({"pid":pid,"start_token":start_token,"worker":"fixed-cold-worker"});
    let mut file = OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file, &evidence).unwrap();
    file.write_all(b"\n").unwrap();
    file.sync_all().unwrap();
    let until = Instant::now() + Duration::from_secs(25);
    while !release.exists() && Instant::now() < until { thread::sleep(Duration::from_millis(10)); }
    fs::write(exited, b"self-released-or-timed-out\n").unwrap();
}

#[test]
fn actual_gateway_loss_preserves_unknown_and_capacity() {
    let dir = tempfile::tempdir().unwrap();
    let (db, revision) = setup(dir.path(), JOB);
    let marker = dir.path().join("worker-launch-counter.jsonl");
    let release_path = dir.path().join("worker-release");
    let exited = dir.path().join("worker-exited");
    let _release = Release(release_path.clone());
    let trusted = profile(&marker, &release_path, &exited);
    let mut records = Vec::new();

    let mut first = Gateway::start(dir.path(), "gateway-hot", &db, &admin_policy(), &trusted);
    let before_launch = events(&db, JOB);
    let launch_request = json!({"op":"local_launch","job_id":JOB,"launch_id":LAUNCH,"expected_catalog":revision});
    let launch_response = first.request(launch_request.clone());
    wait_for(&marker);
    record(&mut records,"hot-launch",launch_request.clone(),launch_response,before_launch,events(&db, JOB));
    assert_eq!(worker_lines(&marker).len(),1,"one gateway dispatch must create one fixed worker");

    let before_forgery = events(&db, JOB);
    let forged = json!({"op":"local_poll","job_id":JOB,"launch_id":LAUNCH,
        "pid":worker_lines(&marker)[0]["pid"],"process_identity":{"pid":worker_lines(&marker)[0]["pid"],"start_token":worker_lines(&marker)[0]["start_token"]},
        "observation":{"kind":"LAUNCH_EXIT_OBSERVED","code":0},"command":"/bin/true"});
    let forged_reply = first.request(forged.clone());
    let after_forgery = events(&db, JOB);
    record(&mut records,"forged-client-evidence",forged,forged_reply,before_forgery.clone(),after_forgery.clone());
    assert_eq!(after_forgery,before_forgery,"caller process/observation/command fields cannot append evidence");

    let before_kill = events(&db, JOB);
    first.child.kill().unwrap();
    let gateway_exit = first.child.wait().unwrap();
    drop(first);
    assert!(!exited.exists(),"worker must outlive gateway loss until self-release/timeout");
    let after_kill = events(&db, JOB);

    let viewer = Gateway::start(dir.path(),"gateway-viewer",&db,&viewer_policy(),&trusted);
    let before_denial = events(&db, JOB);
    let denied = json!({"op":"local_resume","job_id":JOB,"launch_id":LAUNCH});
    let denied_reply = viewer.request(denied.clone());
    let after_denial = events(&db, JOB);
    record(&mut records,"viewer-peer-denied",denied,denied_reply,before_denial.clone(),after_denial.clone());
    assert_eq!(after_denial,before_denial,"viewer SO_PEERCRED role cannot access local admin operations");
    drop(viewer);

    let cold = Gateway::start(dir.path(),"gateway-cold",&db,&admin_policy(),&trusted);
    let wrong_selector = json!({"op":"local_stop","job_id":JOB,"launch_id":"forged-launch","stop_id":"wrong-selector"});
    let before_wrong = events(&db, JOB);
    let wrong_reply = cold.request(wrong_selector.clone());
    let after_wrong = events(&db, JOB);
    record(&mut records,"wrong-launch-selector",wrong_selector,wrong_reply,before_wrong.clone(),after_wrong.clone());
    assert_eq!(after_wrong,before_wrong,"wrong launch selector must be effect free");

    let wrong_job = json!({"op":"local_resume","job_id":"other-job","launch_id":LAUNCH});
    let before_wrong_job = events(&db, JOB);
    let wrong_job_reply = cold.request(wrong_job.clone());
    let after_wrong_job = events(&db, JOB);
    record(&mut records,"wrong-job-selector",wrong_job,wrong_job_reply,before_wrong_job.clone(),after_wrong_job.clone());
    assert_eq!(after_wrong_job,before_wrong_job,"wrong job selector must be effect free");

    let before_replay = events(&db, JOB);
    let replay = cold.request(launch_request.clone());
    let after_replay = events(&db, JOB);
    record(&mut records,"cold-launch-replay",launch_request,replay.clone(),before_replay.clone(),after_replay.clone());
    assert_eq!(worker_lines(&marker).len(),1,"cold replay must not create a second worker");
    assert_eq!(after_replay,before_replay,"cold replay must not create durable launch evidence");

    let resume_request = json!({"op":"local_resume","job_id":JOB,"launch_id":LAUNCH});
    let before_resume = events(&db, JOB);
    let resume = cold.request(resume_request.clone());
    record(&mut records,"cold-resume",resume_request,resume.clone(),before_resume.clone(),events(&db, JOB));
    assert_eq!(resume["ok"],true);
    assert_eq!(resume["result"]["local_state"],"unknown");

    let stop_request = json!({"op":"local_stop","job_id":JOB,"launch_id":LAUNCH,"stop_id":"cold-stop-1"});
    let before_stop = events(&db, JOB);
    let stop = cold.request(stop_request.clone());
    let after_stop = events(&db, JOB);
    record(&mut records,"cold-stop-request",stop_request.clone(),stop.clone(),before_stop,after_stop.clone());
    assert_eq!(stop["ok"],true);
    assert_eq!(stop["result"]["state"],"unknown");
    assert!(after_stop.as_array().unwrap().len() > records.last().unwrap()["events_before"].as_array().unwrap().len(),"cold stop must be durable");
    assert!(!exited.exists(),"cold stop must not signal the worker whose Child handle was lost");

    let before_stop_replay = events(&db, JOB);
    let stop_replay = cold.request(stop_request.clone());
    let after_stop_replay = events(&db, JOB);
    record(&mut records,"cold-stop-replay",stop_request,stop_replay, before_stop_replay.clone(),after_stop_replay.clone());
    assert_eq!(after_stop_replay,before_stop_replay,"exact cold stop replay is idempotent");

    let finalize_request = json!({"op":"local_finalize","job_id":JOB,"launch_id":LAUNCH,"outcome":"completed"});
    let before_finalize = events(&db, JOB);
    let finalize = cold.request(finalize_request.clone());
    let after_finalize = events(&db, JOB);
    record(&mut records,"finalize-without-exit",finalize_request,finalize.clone(),before_finalize.clone(),after_finalize.clone());
    assert_eq!(finalize["ok"],false,"finalize requires exact exit evidence");
    assert_eq!(after_finalize,before_finalize,"blocked finalization must not append an event");
    let held_balances = balances(&db);

    let worker = worker_lines(&marker);
    let durable_exit_history = cold_finalize_after_hot_exit(dir.path());
    let report = json!({
        "why":"gateway loss destroys the in-memory Child handle; a persisted intent must remain unknown and cannot release capacity",
        "what":"actual Unix gateway, actual test-owned gateway Child kill, Store event_log/balance reads, and one fixed profile worker",
        "how_certain":"experimental; assertions and captured native records",
        "what_not_tested":["whole-host power loss","hostile same-UID code","arbitrary programs","remote providers","general process containment","authority/catalog change cancellation"],
        "catalog_revision":revision,"job_id":JOB,"launch_id":LAUNCH,
        "gateway_before_loss_event_snapshot":before_kill,"gateway_after_loss_event_snapshot":after_kill,
        "gateway_exit_code_after_test_owned_kill":gateway_exit.code(),
        "worker_launch_counter":worker,"worker_exited_before_release":false,
        "worker_exit_marker_after_release":exited.exists(),"held_balances_after_blocked_finalize":held_balances,
        "records":records,"durable_exit_cold_finalize_history":durable_exit_history,
        "source_sha256":source_hashes()
    });
    persist(report);
    fs::write(release_path,b"release\n").unwrap();
    wait_for(&exited);
}
