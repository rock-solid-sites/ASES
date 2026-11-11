//! Fresh resource-session processes exercised against the actual Unix gateway.
//! Every worker is this fixed test binary; no client or test adopts a saved PID.
use ases_resource_control::{now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::access::{Grant, Policy};
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

const ACCOUNT: &str = "session-client-account";
const PROJECT: &str = "session-client-project";
const ENVIRONMENT: &str = "session-client-environment";

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
    Account { id: ACCOUNT.into(), provider: "local".into(), payer_ref: "session-test-only".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec![PROJECT.into()],
        source: "synthetic-native-session-client-test".into(), observed_at: now(), ttl_seconds: 3600 }
}

fn meter() -> Meter {
    Meter { id: "session-client-meter".into(), account: ACCOUNT.into(), provider: "local".into(),
        product: "fixed-session-worker".into(), period: "session-client-test".into(), unit: "units".into(),
        limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-session-client-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false }
}

fn environment() -> Environment {
    Environment { id: ENVIRONMENT.into(), account: ACCOUNT.into(), provider: "local".into(),
        max_parallel: 1, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-session-client-test".into() }
}

fn proposal(job: &str) -> Proposal {
    Proposal { job_id: job.into(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(), estimated_wall_seconds: 90,
        claims: vec![Claim { meter_id: "session-client-meter".into(), amount: 50 }],
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

fn profile(marker: &Path, release: &Path, exited: &Path) -> Value {
    json!({
        "program": std::env::current_exe().unwrap(),
        "args": ["--exact", "session_client_fixed_worker", "--nocapture"],
        "cwd": std::env::current_dir().unwrap(),
        "env": {
            "ASES_SESSION_WORKER_MARKER": marker,
            "ASES_SESSION_WORKER_RELEASE": release,
            "ASES_SESSION_WORKER_EXITED": exited
        },
        "account_id": ACCOUNT, "project_id": PROJECT, "environment_id": ENVIRONMENT
    })
}

fn invalid_program_profile(dir: &Path) -> Value {
    json!({
        "program": dir.join("missing-fixed-worker"),
        "args": [], "cwd": dir,
        "env": {},
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
        panic!("resource gateway did not create socket {}", socket.display());
    }
    fn kill(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}
impl Drop for Gateway { fn drop(&mut self) { self.kill(); } }

struct Release(PathBuf);
impl Drop for Release { fn drop(&mut self) { let _ = fs::write(&self.0, b"release\n"); } }

fn invoke(socket: &Path, args: &[&str]) -> Output {
    let mut command = Command::new(env!("CARGO_BIN_EXE_resource-session"));
    command.arg(socket);
    command.args(args);
    command.stdin(Stdio::null()).output().unwrap()
}

fn parse_stdout(output: &Output) -> Value {
    serde_json::from_slice(&output.stdout).unwrap_or_else(|_| panic!(
        "client stdout was not JSON: status={:?}, stdout={}, stderr={}",
        output.status.code(), String::from_utf8_lossy(&output.stdout), String::from_utf8_lossy(&output.stderr)))
}

fn events(db: &Path, job: &str) -> Value {
    serde_json::to_value(Store::open(db).unwrap().event_log(Some(job)).unwrap()).unwrap()
}

fn balances(db: &Path) -> Value {
    serde_json::to_value(Store::open(db).unwrap().balances(now()).unwrap()).unwrap()
}

fn active_reserved(value: &Value) -> i64 {
    value.as_array().unwrap().iter()
        .find(|row| row["meter_id"] == "session-client-meter")
        .and_then(|row| row["active_reserved_remaining"].as_i64()).unwrap()
}

fn worker_lines(path: &Path) -> Vec<Value> {
    fs::read_to_string(path).unwrap_or_default().lines()
        .map(|line| serde_json::from_str(line).unwrap()).collect()
}

fn wait_for(path: &Path) {
    let until = Instant::now() + Duration::from_secs(10);
    while Instant::now() < until {
        if path.exists() { return; }
        thread::sleep(Duration::from_millis(10));
    }
    panic!("fixed session worker did not create {}", path.display());
}

fn capture_call(records: &mut Vec<Value>, phase: &str, args: &[&str], socket: &Path,
                output: &Output, before: Value, after: Value) {
    let mut argv = vec![socket.to_string_lossy().to_string()];
    argv.extend(args.iter().map(|arg| (*arg).to_string()));
    records.push(json!({"phase":phase,"argv_after_executable":argv,
        "exit_code":output.status.code(),"stdout":String::from_utf8_lossy(&output.stdout),
        "stderr":String::from_utf8_lossy(&output.stderr),"events_before":before,"events_after":after}));
}

fn source_hashes() -> Value {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut out = serde_json::Map::new();
    for relative in ["src/bin/resource-session.rs", "src/bin/resource-gateway.rs", "src/local.rs",
        "src/lib.rs", "tests/native_session_client.rs"] {
        if let Ok(bytes) = fs::read(root.join(relative)) {
            out.insert(relative.into(), json!(format!("{:x}", Sha256::digest(bytes))));
        }
    }
    Value::Object(out)
}

fn persist(name: &str, value: Value) {
    if let Some(path) = std::env::var_os("ASES_LOCAL_CLIENT_EVIDENCE_DIR") {
        let dir = PathBuf::from(path);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join(name), serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

fn persist_lost_reply(value: Value) {
    if let Some(path) = std::env::var_os("ASES_LOCAL_CLIENT_LOST_REPLY_EVIDENCE_DIR") {
        let dir = PathBuf::from(path);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join("accepted-launch-reply-lost.json"), serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

fn forward_once_then_drop(proxy_path: PathBuf, gateway_path: PathBuf) -> thread::JoinHandle<Value> {
    thread::spawn(move || {
        let listener = UnixListener::bind(&proxy_path).unwrap();
        let (mut downstream, _) = listener.accept().unwrap();
        downstream.set_read_timeout(Some(Duration::from_secs(3))).unwrap();
        let mut request_bytes = Vec::new();
        let mut chunk = [0u8; 1024];
        loop {
            let read = downstream.read(&mut chunk).unwrap();
            if read == 0 { break; }
            assert!(request_bytes.len() + read <= 8 * 1024, "thin client request exceeded fixture bound");
            request_bytes.extend_from_slice(&chunk[..read]);
        }
        let request: Value = serde_json::from_slice(&request_bytes).unwrap();

        // This proxy only forwards bytes once. The actual gateway, still using
        // the test process UID and real Policy/SO_PEERCRED, makes the decision.
        let mut upstream = UnixStream::connect(&gateway_path).unwrap();
        upstream.set_read_timeout(Some(Duration::from_secs(3))).unwrap();
        upstream.set_write_timeout(Some(Duration::from_secs(3))).unwrap();
        upstream.write_all(&request_bytes).unwrap();
        upstream.shutdown(std::net::Shutdown::Write).unwrap();
        let mut response_bytes = Vec::new();
        loop {
            let read = upstream.read(&mut chunk).unwrap();
            if read == 0 { break; }
            assert!(response_bytes.len() + read <= 8 * 1024, "gateway reply exceeded fixture bound");
            response_bytes.extend_from_slice(&chunk[..read]);
        }
        let actual_gateway_response: Value = serde_json::from_slice(&response_bytes).unwrap();
        drop(upstream);
        drop(downstream); // Deliberately discard the actual reply to the client.

        // Check briefly for a reconnect. The client must make exactly one
        // connection even though its first request may already have applied.
        listener.set_nonblocking(true).unwrap();
        let until = Instant::now() + Duration::from_millis(200);
        let mut additional_connections = 0;
        while Instant::now() < until {
            match listener.accept() {
                Ok((mut retry, _)) => {
                    additional_connections += 1;
                    retry.set_read_timeout(Some(Duration::from_millis(100))).unwrap();
                    let _ = retry.read(&mut chunk);
                }
                Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => {
                    thread::sleep(Duration::from_millis(5));
                }
                Err(error) => panic!("proxy accept failed while checking retry: {error}"),
            }
        }
        json!({"request":request,"forwarded_once":true,"actual_gateway_response":actual_gateway_response,
            "actual_reply_discarded":true,"additional_client_connections":additional_connections})
    })
}

/// Fixed trusted test worker. Its own release gate and timeout bound orphan cleanup.
#[test]
fn session_client_fixed_worker() {
    let Some(marker) = std::env::var_os("ASES_SESSION_WORKER_MARKER") else { return };
    let marker = PathBuf::from(marker);
    let release = PathBuf::from(std::env::var_os("ASES_SESSION_WORKER_RELEASE").unwrap());
    let exited = PathBuf::from(std::env::var_os("ASES_SESSION_WORKER_EXITED").unwrap());
    let pid = std::process::id();
    let stat = fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let start_token = stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap().to_string();
    let mut file = OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file, &json!({"pid":pid,"start_token":start_token,"worker":"fixed-session-worker"})).unwrap();
    file.write_all(b"\n").unwrap();
    file.sync_all().unwrap();
    let until = Instant::now() + Duration::from_secs(25);
    while !release.exists() && Instant::now() < until { thread::sleep(Duration::from_millis(10)); }
    fs::write(exited, b"released-or-timed-out\n").unwrap();
}

#[test]
fn fresh_session_client_drives_hot_cold_and_server_error_histories() {
    let root = tempfile::tempdir().unwrap();
    let mut histories = serde_json::Map::new();

    // Hot path: each CLI call is a new OS process and a new gateway connection.
    let hot_dir = root.path().join("hot");
    fs::create_dir_all(&hot_dir).unwrap();
    let hot_job = "session-hot-job";
    let hot_launch = "session-hot-launch";
    let (hot_db, hot_revision) = setup(&hot_dir, hot_job);
    let hot_marker = hot_dir.join("worker-counter.jsonl");
    let hot_release = hot_dir.join("worker-release");
    let hot_exited = hot_dir.join("worker-exited");
    let _hot_release = Release(hot_release.clone());
    let hot_profile = profile(&hot_marker, &hot_release, &hot_exited);
    let hot_gateway = Gateway::start(&hot_dir, "gateway-hot", &hot_db, &admin_policy(), &hot_profile);
    let mut hot_records = Vec::new();

    let hot_revision_arg = hot_revision.to_string();
    let launch_args = ["launch", hot_job, hot_launch, hot_revision_arg.as_str()];
    let before = events(&hot_db, hot_job);
    let launch_output = invoke(&hot_gateway.socket, &launch_args);
    wait_for(&hot_marker);
    let launch_response = parse_stdout(&launch_output);
    assert_eq!(launch_output.status.code(), Some(0));
    assert_eq!(launch_response["ok"], true);
    assert_eq!(launch_response["result"]["state"], "running");
    capture_call(&mut hot_records,"fresh-launch",&launch_args,&hot_gateway.socket,&launch_output,before,events(&hot_db,hot_job));
    let worker_identity = worker_lines(&hot_marker);
    assert_eq!(worker_identity.len(),1,"fresh launch must create one fixed worker");

    let resume_args = ["resume", hot_job, hot_launch];
    let before = events(&hot_db, hot_job);
    let resume_output = invoke(&hot_gateway.socket, &resume_args);
    let resume_response = parse_stdout(&resume_output);
    assert_eq!(resume_output.status.code(), Some(0));
    assert_eq!(resume_response["result"]["local_state"], "owned_child_unobserved");
    assert_eq!(worker_lines(&hot_marker).len(),1,"fresh resume never dispatches another child");
    capture_call(&mut hot_records,"fresh-resume-no-redispatch",&resume_args,&hot_gateway.socket,&resume_output,before,events(&hot_db,hot_job));

    let poll_args = ["poll", hot_job, hot_launch];
    let before = events(&hot_db, hot_job);
    let poll_output = invoke(&hot_gateway.socket, &poll_args);
    let poll_response = parse_stdout(&poll_output);
    assert_eq!(poll_output.status.code(), Some(0));
    assert_eq!(poll_response["result"]["state"], "running");
    capture_call(&mut hot_records,"fresh-poll",&poll_args,&hot_gateway.socket,&poll_output,before,events(&hot_db,hot_job));

    let stop_args = ["stop", hot_job, hot_launch, "session-hot-stop"];
    let before = events(&hot_db, hot_job);
    let stop_output = invoke(&hot_gateway.socket, &stop_args);
    let stop_response = parse_stdout(&stop_output);
    assert_eq!(stop_output.status.code(), Some(0));
    assert_eq!(stop_response["result"]["state"], "exit_observed");
    capture_call(&mut hot_records,"fresh-stop-observed-exit",&stop_args,&hot_gateway.socket,&stop_output,before,events(&hot_db,hot_job));

    let finalize_args = ["finalize", hot_job, hot_launch, "completed"];
    let before = events(&hot_db, hot_job);
    let finalize_output = invoke(&hot_gateway.socket, &finalize_args);
    let finalize_response = parse_stdout(&finalize_output);
    assert_eq!(finalize_output.status.code(), Some(0));
    assert_eq!(finalize_response["ok"],true);
    assert_eq!(active_reserved(&balances(&hot_db)),0);
    capture_call(&mut hot_records,"fresh-finalize-releases-capacity",&finalize_args,&hot_gateway.socket,&finalize_output,before,events(&hot_db,hot_job));
    histories.insert("hot_launch_resume_stop_finalize".into(),json!({
        "job_id":hot_job,"launch_id":hot_launch,"worker_launch_counter":worker_identity,
        "worker_exit_marker":hot_exited.exists(),"records":hot_records,"final_balances":balances(&hot_db)
    }));
    drop(hot_gateway);

    // Natural completion path: the worker's release gate lets it return code 0;
    // a fresh client poll records that exact wait result before finalization.
    let natural_dir = root.path().join("natural-exit");
    fs::create_dir_all(&natural_dir).unwrap();
    let natural_job = "session-natural-job";
    let natural_launch = "session-natural-launch";
    let (natural_db, natural_revision) = setup(&natural_dir,natural_job);
    let natural_marker = natural_dir.join("worker-counter.jsonl");
    let natural_release = natural_dir.join("worker-release");
    let natural_exited = natural_dir.join("worker-exited");
    let _natural_release = Release(natural_release.clone());
    let natural_profile = profile(&natural_marker,&natural_release,&natural_exited);
    let natural_gateway = Gateway::start(&natural_dir,"gateway-natural",&natural_db,&admin_policy(),&natural_profile);
    let mut natural_records = Vec::new();
    let natural_revision_arg = natural_revision.to_string();
    let natural_launch_args = ["launch",natural_job,natural_launch,natural_revision_arg.as_str()];
    let before = events(&natural_db,natural_job);
    let natural_launch_output = invoke(&natural_gateway.socket,&natural_launch_args);
    wait_for(&natural_marker);
    assert_eq!(natural_launch_output.status.code(),Some(0));
    capture_call(&mut natural_records,"fresh-launch",&natural_launch_args,&natural_gateway.socket,&natural_launch_output,before,events(&natural_db,natural_job));
    fs::write(&natural_release,b"release\n").unwrap();
    wait_for(&natural_exited);
    let natural_poll_args = ["poll",natural_job,natural_launch];
    let deadline = Instant::now() + Duration::from_secs(5);
    let natural_poll_response = loop {
        let before = events(&natural_db,natural_job);
        let output = invoke(&natural_gateway.socket,&natural_poll_args);
        let response = parse_stdout(&output);
        assert_eq!(output.status.code(),Some(0));
        let state = response["result"]["state"].as_str().unwrap_or("");
        capture_call(&mut natural_records,"fresh-poll-natural-completion",&natural_poll_args,&natural_gateway.socket,&output,before,events(&natural_db,natural_job));
        if state == "exit_observed" { break response; }
        assert_eq!(state,"running","natural worker poll must remain owned until exact exit");
        assert!(Instant::now() < deadline,"worker failed to complete within bounded test interval");
        thread::sleep(Duration::from_millis(10));
    };
    assert_eq!(natural_poll_response["result"]["exit"]["code"],0);
    let natural_held = balances(&natural_db);
    assert!(active_reserved(&natural_held)>0,"exact natural exit alone must retain capacity");
    let natural_finalize_args = ["finalize",natural_job,natural_launch,"completed"];
    let before = events(&natural_db,natural_job);
    let natural_finalize_output = invoke(&natural_gateway.socket,&natural_finalize_args);
    let natural_finalize_response = parse_stdout(&natural_finalize_output);
    assert_eq!(natural_finalize_output.status.code(),Some(0));
    assert_eq!(natural_finalize_response["ok"],true);
    assert_eq!(active_reserved(&balances(&natural_db)),0);
    capture_call(&mut natural_records,"fresh-finalize-after-natural-exit",&natural_finalize_args,&natural_gateway.socket,&natural_finalize_output,before,events(&natural_db,natural_job));
    histories.insert("natural_completion_via_fresh_poll".into(),json!({
        "job_id":natural_job,"launch_id":natural_launch,"worker_launch_counter":worker_lines(&natural_marker),
        "worker_exit_marker":natural_exited.exists(),"balances_after_poll_before_finalize":natural_held,
        "balances_after_finalize":balances(&natural_db),"records":natural_records
    }));
    drop(natural_gateway);

    // Cold path: loss of gateway ownership is visible as unknown and stays read-only.
    let cold_dir = root.path().join("cold");
    fs::create_dir_all(&cold_dir).unwrap();
    let cold_job = "session-cold-job";
    let cold_launch = "session-cold-launch";
    let (cold_db, cold_revision) = setup(&cold_dir, cold_job);
    let cold_marker = cold_dir.join("worker-counter.jsonl");
    let cold_release = cold_dir.join("worker-release");
    let cold_exited = cold_dir.join("worker-exited");
    let _cold_release = Release(cold_release.clone());
    let cold_profile = profile(&cold_marker, &cold_release, &cold_exited);
    let mut hot_cold_gateway = Gateway::start(&cold_dir,"gateway-cold-hot",&cold_db,&admin_policy(),&cold_profile);
    let mut cold_records = Vec::new();
    let cold_revision_arg = cold_revision.to_string();
    let cold_launch_args = ["launch", cold_job, cold_launch, cold_revision_arg.as_str()];
    let before = events(&cold_db,cold_job);
    let cold_launch_output = invoke(&hot_cold_gateway.socket,&cold_launch_args);
    wait_for(&cold_marker);
    assert_eq!(cold_launch_output.status.code(),Some(0));
    capture_call(&mut cold_records,"launch-before-gateway-loss",&cold_launch_args,&hot_cold_gateway.socket,&cold_launch_output,before,events(&cold_db,cold_job));
    assert_eq!(worker_lines(&cold_marker).len(),1);
    hot_cold_gateway.kill();
    drop(hot_cold_gateway);

    let cold_gateway = Gateway::start(&cold_dir,"gateway-cold-restarted",&cold_db,&admin_policy(),&cold_profile);
    let cold_resume_args = ["resume",cold_job,cold_launch];
    let before = events(&cold_db,cold_job);
    let cold_resume_output = invoke(&cold_gateway.socket,&cold_resume_args);
    let cold_resume_response = parse_stdout(&cold_resume_output);
    assert_eq!(cold_resume_output.status.code(),Some(0));
    assert_eq!(cold_resume_response["result"]["local_state"],"unknown");
    assert_eq!(worker_lines(&cold_marker).len(),1,"cold resume never redispatches");
    let after = events(&cold_db,cold_job);
    assert_eq!(after,before,"cold resume does not mutate durable events");
    capture_call(&mut cold_records,"fresh-cold-resume-unknown",&cold_resume_args,&cold_gateway.socket,&cold_resume_output,before,after);
    let viewer_gateway = Gateway::start(&cold_dir,"gateway-cold-viewer",&cold_db,&viewer_policy(),&cold_profile);
    let before_denial = events(&cold_db,cold_job);
    let denied_output = invoke(&viewer_gateway.socket,&cold_resume_args);
    let denied_response = parse_stdout(&denied_output);
    assert_eq!(denied_output.status.code(),Some(3));
    assert_eq!(denied_response["ok"],false,"peer role denial comes from gateway policy");
    assert_eq!(events(&cold_db,cold_job),before_denial,"policy denial has no event effect");
    capture_call(&mut cold_records,"actual-viewer-peer-policy-denial",&cold_resume_args,&viewer_gateway.socket,&denied_output,before_denial.clone(),events(&cold_db,cold_job));
    drop(viewer_gateway);
    histories.insert("cold_resume_and_actual_policy".into(),json!({
        "job_id":cold_job,"launch_id":cold_launch,"worker_launch_counter":worker_lines(&cold_marker),
        "worker_exited_before_release":cold_exited.exists(),"records":cold_records,
        "event_snapshot":events(&cold_db,cold_job)
    }));
    drop(cold_gateway);

    // Server error path: spawn failed after durable intent; the client must not
    // label the received server reply as transport-unknown or as no-effect proof.
    let error_dir = root.path().join("server-error");
    fs::create_dir_all(&error_dir).unwrap();
    let error_job = "session-server-error-job";
    let error_launch = "session-server-error-launch";
    let (error_db, error_revision) = setup(&error_dir,error_job);
    let bad_profile = invalid_program_profile(&error_dir);
    let error_gateway = Gateway::start(&error_dir,"gateway-server-error",&error_db,&admin_policy(),&bad_profile);
    let mut error_records = Vec::new();
    let error_revision_arg = error_revision.to_string();
    let error_args = ["launch",error_job,error_launch,error_revision_arg.as_str()];
    let before_error = events(&error_db,error_job);
    let error_output = invoke(&error_gateway.socket,&error_args);
    let error_response = parse_stdout(&error_output);
    assert_eq!(error_output.status.code(),Some(3));
    assert_eq!(error_response["ok"],false);
    assert!(error_response.get("outcome_unknown").is_none());
    let after_error = events(&error_db,error_job);
    let durable_job = Store::open(&error_db).unwrap().job(error_job).unwrap();
    assert_eq!(durable_job["state"],"LAUNCHING","server spawn error followed durable launch intent");
    assert!(active_reserved(&balances(&error_db))>0,"ambiguous launch intent retains capacity");
    capture_call(&mut error_records,"server-declared-spawn-error-after-intent",&error_args,&error_gateway.socket,&error_output,before_error,after_error.clone());
    let recover_args = ["resume",error_job,error_launch];
    let before_recover = events(&error_db,error_job);
    let recover_output = invoke(&error_gateway.socket,&recover_args);
    let recover_response = parse_stdout(&recover_output);
    assert_eq!(recover_output.status.code(),Some(0));
    assert_eq!(recover_response["result"]["local_state"],"unknown");
    capture_call(&mut error_records,"explicit-fresh-resume-after-server-error",&recover_args,&error_gateway.socket,&recover_output,before_recover,events(&error_db,error_job));
    histories.insert("server_error_after_durable_intent".into(),json!({
        "job_id":error_job,"launch_id":error_launch,"job_after_error":durable_job,
        "balances_after_error":balances(&error_db),"records":error_records
    }));
    drop(error_gateway);

    persist("session-client-history.json",json!({
        "why":"each client call is a fresh process; authority remains with SO_PEERCRED and gateway policy",
        "what":"actual resource-session binary, actual Unix gateway, fixed profile worker, durable Store events and balance reads",
        "how_certain":"experimental; native assertions and retained client/server records",
        "what_not_tested":["remote providers","hostile same-UID code","whole-host power loss","arbitrary executable delegation","automatic retry or hidden recovery"],
        "histories":histories,"source_sha256":source_hashes()
    }));
}

#[test]
fn actual_client_loses_accepted_launch_reply_then_recovers_without_redispatch() {
    let dir = tempfile::tempdir().unwrap();
    let job = "session-lost-reply-job";
    let launch = "session-lost-reply-launch";
    let (db, revision) = setup(dir.path(), job);
    let marker = dir.path().join("worker-counter.jsonl");
    let release = dir.path().join("worker-release");
    let exited = dir.path().join("worker-exited");
    let _release = Release(release.clone());
    let trusted = profile(&marker, &release, &exited);
    let mut gateway = Gateway::start(dir.path(), "gateway-lost-reply", &db, &admin_policy(), &trusted);

    let proxy_path = dir.path().join("drop-reply-proxy.sock");
    let proxy = forward_once_then_drop(proxy_path.clone(), gateway.socket.clone());
    wait_for(&proxy_path);
    let revision_arg = revision.to_string();
    let launch_args = ["launch", job, launch, revision_arg.as_str()];
    let before_launch = events(&db, job);
    let lost_output = invoke(&proxy_path, &launch_args);
    let proxy_capture = proxy.join().expect("bounded response-drop proxy panicked");
    let client_unknown = parse_stdout(&lost_output);
    let after_launch = events(&db, job);

    assert_eq!(lost_output.status.code(), Some(4));
    assert_eq!(client_unknown["ok"], false);
    assert_eq!(client_unknown["outcome"], "outcome_unknown");
    assert_eq!(proxy_capture["forwarded_once"], true);
    assert_eq!(proxy_capture["additional_client_connections"], 0, "client must not retry after loss");
    assert_eq!(proxy_capture["request"], json!({"op":"local_launch","job_id":job,"launch_id":launch,"expected_catalog":revision}));
    assert_eq!(proxy_capture["actual_gateway_response"]["ok"], true);
    assert_eq!(proxy_capture["actual_gateway_response"]["result"]["state"], "running");
    let started = after_launch.as_array().unwrap().iter().filter(|event| event["kind"] == "LAUNCH_STARTED_OBSERVED").count();
    assert_eq!(started, 1, "actual gateway accepted launch and durably observed the fixed child");
    let job_after_launch = Store::open(&db).unwrap().job(job).unwrap();
    assert_eq!(job_after_launch["state"], "RUNNING");
    let held_after_launch = balances(&db);
    assert!(active_reserved(&held_after_launch) > 0);
    let worker = worker_lines(&marker);
    assert_eq!(worker.len(), 1);

    let mut records = vec![json!({
        "phase":"actual-launch-reply-lost-after-gateway-acceptance",
        "client":{"argv_after_executable":[proxy_path.to_string_lossy().to_string(),launch_args[0].to_string(),launch_args[1].to_string(),launch_args[2].to_string(),launch_args[3].to_string()],
            "exit_code":lost_output.status.code(),"stdout":String::from_utf8_lossy(&lost_output.stdout),
            "stderr":String::from_utf8_lossy(&lost_output.stderr)},
        "proxy_capture":proxy_capture,"events_before":before_launch,"events_after":after_launch,
        "job_after_launch":job_after_launch,"balances_after_launch":held_after_launch,
        "worker_launch_counter":worker
    })];

    // Recovery is an explicit fresh read. Exact launch replay is also explicit
    // and idempotent; neither creates a second child.
    let resume_args = ["resume", job, launch];
    let before_resume = events(&db, job);
    let resume_output = invoke(&gateway.socket, &resume_args);
    let resume_response = parse_stdout(&resume_output);
    assert_eq!(resume_output.status.code(), Some(0));
    assert_eq!(resume_response["result"]["local_state"], "owned_child_unobserved");
    capture_call(&mut records, "fresh-resume-after-lost-reply", &resume_args, &gateway.socket,
        &resume_output, before_resume, events(&db, job));

    let before_replay = events(&db, job);
    let replay_output = invoke(&gateway.socket, &launch_args);
    let replay_response = parse_stdout(&replay_output);
    assert_eq!(replay_output.status.code(), Some(0));
    assert_eq!(replay_response["result"]["state"], "running");
    assert_eq!(worker_lines(&marker).len(), 1, "exact fresh launch replay never spawns a second child");
    assert_eq!(events(&db, job), before_replay, "exact replay adds no duplicate launch evidence");
    capture_call(&mut records, "explicit-exact-launch-replay-no-redispatch", &launch_args, &gateway.socket,
        &replay_output, before_replay, events(&db, job));

    let stop_args = ["stop", job, launch, "session-lost-reply-stop"];
    let before_stop = events(&db, job);
    let stop_output = invoke(&gateway.socket, &stop_args);
    let stop_response = parse_stdout(&stop_output);
    assert_eq!(stop_output.status.code(), Some(0));
    assert_eq!(stop_response["result"]["state"], "exit_observed");
    capture_call(&mut records, "fresh-stop-owned-child", &stop_args, &gateway.socket,
        &stop_output, before_stop, events(&db, job));
    let held_before_finalize = balances(&db);
    assert!(active_reserved(&held_before_finalize) > 0, "stop/exit alone must not finalize");

    let finalize_args = ["finalize", job, launch, "completed"];
    let before_finalize = events(&db, job);
    let finalize_output = invoke(&gateway.socket, &finalize_args);
    let finalize_response = parse_stdout(&finalize_output);
    assert_eq!(finalize_output.status.code(), Some(0));
    assert_eq!(finalize_response["ok"], true);
    let released_after_finalize = balances(&db);
    assert_eq!(active_reserved(&released_after_finalize), 0);
    capture_call(&mut records, "fresh-finalize-releases-capacity", &finalize_args, &gateway.socket,
        &finalize_output, before_finalize, events(&db, job));

    persist_lost_reply(json!({
        "why":"a lost client reply does not undo the gateway's one-use dispatch or durable start evidence",
        "what":"fresh resource-session process, bounded one-forward proxy, actual SO_PEERCRED gateway and fixed worker",
        "how_certain":"experimental; proxy captured actual successful gateway reply, Store event and balance snapshots, worker identity, and client unknown result",
        "what_not_tested":["hostile same-UID proxy","remote provider","whole-host power loss","arbitrary executable delegation","client automatic retry"],
        "proxy_role":"bounded transport fixture only; it forwards once and is not an authority or lifecycle witness",
        "job_id":job,"launch_id":launch,"catalog_revision":revision,
        "worker_launch_counter":worker,"records":records,
        "balances_before_finalize":held_before_finalize,"balances_after_finalize":released_after_finalize,
        "source_sha256":source_hashes()
    }));
    drop(gateway);
}
