//! Native cooperative stop through resource-session -> Unix gateway -> owned Child.
//! Signal handlers only set an atomic flag; the fixed worker writes markers and
//! performs cleanup from its ordinary execution loop.
use ases_resource_control::{now, Claim, Environment, Meter, Proposal, Store};
use ases_resource_control::access::{Grant, Policy};
use ases_resource_control::catalog::Account;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::os::unix::net::UnixStream;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Output, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

static TERM_REQUESTED: AtomicBool = AtomicBool::new(false);
const ACCOUNT: &str = "cooperative-stop-account";
const PROJECT: &str = "cooperative-stop-project";
const ENVIRONMENT: &str = "cooperative-stop-environment";

extern "C" fn term_flag_only(_: libc::c_int) {
    TERM_REQUESTED.store(true, Ordering::Relaxed);
}

fn now_ms() -> u128 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis()
}

fn admin_policy() -> Policy { Policy { administrators: vec![unsafe { libc::geteuid() }], callers: vec![] } }
fn viewer_policy() -> Policy {
    Policy { administrators: vec![], callers: vec![Grant {
        uid: unsafe { libc::geteuid() }, role: "viewer".into(),
        accounts: vec![ACCOUNT.into()], projects: vec![PROJECT.into()],
    }] }
}
fn account() -> Account {
    Account { id: ACCOUNT.into(), provider: "local".into(), payer_ref: "cooperative-test".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec![PROJECT.into()],
        source: "synthetic-native-cooperative-stop-test".into(), observed_at: now(), ttl_seconds: 3600 }
}
fn meter() -> Meter {
    Meter { id: "cooperative-stop-meter".into(), account: ACCOUNT.into(), provider: "local".into(),
        product: "fixed-cooperative-worker".into(), period: "cooperative-stop-test".into(), unit: "units".into(),
        limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-cooperative-stop-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false }
}
fn environment() -> Environment {
    Environment { id: ENVIRONMENT.into(), account: ACCOUNT.into(), provider: "local".into(),
        max_parallel: 1, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-cooperative-stop-test".into() }
}
fn proposal(job: &str) -> Proposal {
    Proposal { job_id: job.into(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(), estimated_wall_seconds: 120,
        claims: vec![Claim { meter_id: "cooperative-stop-meter".into(), amount: 50 }],
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
fn profile(dir: &Path, marker: &Path, term_seen: &Path, cleanup: &Path, exited: &Path,
           release: &Path, mode: &str, cleanup_delay_ms: u64, exit_code: i32) -> Value {
    json!({
        "program":std::env::current_exe().unwrap(),
        "args":["--exact","cooperative_stop_fixed_worker","--nocapture"],
        "cwd":dir,
        "env":{
            "ASES_COOP_MARKER":marker,"ASES_COOP_TERM_SEEN":term_seen,
            "ASES_COOP_CLEANUP":cleanup,"ASES_COOP_EXITED":exited,
            "ASES_COOP_RELEASE":release,"ASES_COOP_MODE":mode,
            "ASES_COOP_DELAY_MS":cleanup_delay_ms.to_string(),"ASES_COOP_EXIT_CODE":exit_code.to_string()
        },
        "account_id":ACCOUNT,"project_id":PROJECT,"environment_id":ENVIRONMENT
    })
}

struct Gateway { child: Child, socket: PathBuf }
impl Gateway {
    fn start(dir: &Path, name: &str, db: &Path, policy: &Policy, profile: &Value) -> Self {
        let socket=dir.join(format!("{name}.sock"));
        let policy_path=dir.join(format!("{name}-policy.json"));
        let profile_path=dir.join(format!("{name}-profile.json"));
        fs::write(&policy_path,serde_json::to_vec(policy).unwrap()).unwrap();
        fs::write(&profile_path,serde_json::to_vec(profile).unwrap()).unwrap();
        let child=Command::new(env!("CARGO_BIN_EXE_resource-gateway"))
            .arg(db).arg(&socket).arg(&policy_path)
            .arg(env!("CARGO_BIN_EXE_ases-resource-control")).arg(&profile_path)
            .stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null()).spawn().unwrap();
        wait_for(&socket,Duration::from_secs(10));
        Self{child,socket}
    }
    fn kill(&mut self) { let _=self.child.kill(); let _=self.child.wait(); }
}
impl Drop for Gateway { fn drop(&mut self) { self.kill(); } }

struct Release(PathBuf);
impl Drop for Release { fn drop(&mut self) { let _=fs::write(&self.0,b"test cleanup release\n"); } }

fn invoke(socket:&Path,args:&[&str])->Output {
    let mut cmd=Command::new(env!("CARGO_BIN_EXE_resource-session"));
    cmd.arg(socket).args(args).stdin(Stdio::null()).output().unwrap()
}
fn parse(output:&Output)->Value {
    serde_json::from_slice(&output.stdout).unwrap_or_else(|_|panic!("not JSON: status={:?}, stdout={}, stderr={}",
        output.status.code(),String::from_utf8_lossy(&output.stdout),String::from_utf8_lossy(&output.stderr)))
}
fn raw_request(socket:&Path,request:&Value)->(Value,Value) {
    let mut stream=UnixStream::connect(socket).unwrap();
    stream.set_read_timeout(Some(Duration::from_secs(3))).unwrap();
    let bytes=serde_json::to_vec(request).unwrap();
    stream.write_all(&bytes).unwrap();
    stream.shutdown(std::net::Shutdown::Write).unwrap();
    let mut reply=Vec::new(); stream.read_to_end(&mut reply).unwrap();
    (serde_json::from_slice(&reply).unwrap(),request.clone())
}
fn events(db:&Path,job:&str)->Value { serde_json::to_value(Store::open(db).unwrap().event_log(Some(job)).unwrap()).unwrap() }
fn balances(db:&Path)->Value { serde_json::to_value(Store::open(db).unwrap().balances(now()).unwrap()).unwrap() }
fn reserved(value:&Value)->i64 {
    value.as_array().unwrap().iter().find(|row|row["meter_id"]=="cooperative-stop-meter")
        .and_then(|row|row["active_reserved_remaining"].as_i64()).unwrap()
}
fn read_marker(path:&Path)->Vec<Value> {
    fs::read_to_string(path).unwrap_or_default().lines().map(|s|serde_json::from_str(s).unwrap()).collect()
}
fn wait_for(path:&Path,timeout:Duration) {
    let until=Instant::now()+timeout;
    while Instant::now()<until {if path.exists(){return;}thread::sleep(Duration::from_millis(5));}
    panic!("bounded worker/gateway marker missing: {}",path.display());
}
fn record(records:&mut Vec<Value>,phase:&str,request:Value,output:&Output,before:Value,after:Value) {
    records.push(json!({"phase":phase,"request":request,"exit_code":output.status.code(),
        "stdout":String::from_utf8_lossy(&output.stdout),"stderr":String::from_utf8_lossy(&output.stderr),
        "events_before":before,"events_after":after}));
}
fn source_hashes()->Value {
    let root=PathBuf::from(env!("CARGO_MANIFEST_DIR"));let mut out=serde_json::Map::new();
    for file in ["src/bin/resource-session.rs","src/bin/resource-gateway.rs","src/local.rs","src/lib.rs","tests/native_cooperative_stop.rs"] {
        if let Ok(bytes)=fs::read(root.join(file)){out.insert(file.into(),json!(format!("{:x}",Sha256::digest(bytes))));}
    }
    Value::Object(out)
}
fn persist(value:Value) {
    if let Some(path)=std::env::var_os("ASES_COOPERATIVE_STOP_EVIDENCE_DIR") {
        let dir=PathBuf::from(path);fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join("native-history.json"),serde_json::to_vec_pretty(&value).unwrap()).unwrap();
    }
}

/// The only executable selected by the trusted local profiles.
#[test]
fn cooperative_stop_fixed_worker() {
    let Some(marker)=std::env::var_os("ASES_COOP_MARKER") else{return};
    let marker=PathBuf::from(marker);
    let term_seen=PathBuf::from(std::env::var_os("ASES_COOP_TERM_SEEN").unwrap());
    let cleanup=PathBuf::from(std::env::var_os("ASES_COOP_CLEANUP").unwrap());
    let exited=PathBuf::from(std::env::var_os("ASES_COOP_EXITED").unwrap());
    let release=PathBuf::from(std::env::var_os("ASES_COOP_RELEASE").unwrap());
    let mode=std::env::var("ASES_COOP_MODE").unwrap();
    let delay=std::env::var("ASES_COOP_DELAY_MS").unwrap().parse::<u64>().unwrap();
    let exit_code=std::env::var("ASES_COOP_EXIT_CODE").unwrap().parse::<i32>().unwrap();
    if mode=="ignore" {
        let prior=unsafe{libc::signal(libc::SIGTERM,libc::SIG_IGN)};
        assert_ne!(prior,libc::SIG_ERR,"SIGTERM ignore installation failed");
    } else {
        let mut action:libc::sigaction=unsafe{std::mem::zeroed()};
        action.sa_sigaction=term_flag_only as libc::sighandler_t;
        action.sa_flags=0;
        unsafe{libc::sigemptyset(&mut action.sa_mask);assert_eq!(libc::sigaction(libc::SIGTERM,&action,std::ptr::null_mut()),0);}
    }
    TERM_REQUESTED.store(false,Ordering::Relaxed);
    let pid=std::process::id();
    let stat=fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let token=stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap().to_string();
    let mut file=OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut file,&json!({"pid":pid,"start_token":token,"mode":mode,"started_at_ms":now_ms()})).unwrap();
    file.write_all(b"\n").unwrap();file.sync_all().unwrap();
    let deadline=Instant::now()+Duration::from_secs(25);
    let mut handled=false;
    loop {
        if !handled && TERM_REQUESTED.swap(false,Ordering::Relaxed) {
            handled=true;
            fs::write(&term_seen,serde_json::to_vec(&json!({"at_ms":now_ms()})).unwrap()).unwrap();
            let cleanup_until=Instant::now()+Duration::from_millis(delay);
            while Instant::now()<cleanup_until && !release.exists(){thread::sleep(Duration::from_millis(5));}
            fs::write(&cleanup,serde_json::to_vec(&json!({"at_ms":now_ms(),"cleanup":"completed"})).unwrap()).unwrap();
            break;
        }
        if release.exists(){break;}
        if Instant::now()>=deadline {break;}
        thread::sleep(Duration::from_millis(5));
    }
    fs::write(&exited,serde_json::to_vec(&json!({"at_ms":now_ms(),"exit_code":exit_code})).unwrap()).unwrap();
    std::process::exit(exit_code);
}

#[test]
fn actual_cooperative_stop_histories_preserve_owned_child_and_explicit_finalize() {
    let root=tempfile::tempdir().unwrap();let mut histories=serde_json::Map::new();

    // Cooperative TERM: async handler only raises a flag; normal worker code
    // leaves a cleanup marker and exits with code 0 during the grace interval.
    let coop=root.path().join("cooperative");fs::create_dir_all(&coop).unwrap();
    let job="coop-worker-job";let launch="coop-worker-launch";let stop_id="coop-stop-id";
    let (db,revision)=setup(&coop,job);
    let started=coop.join("started.jsonl");let term_seen=coop.join("term-seen.json");
    let cleanup=coop.join("cleanup.json");let exited=coop.join("exited.json");let release=coop.join("release");
    let _release=Release(release.clone());
    let trusted=profile(&coop,&started,&term_seen,&cleanup,&exited,&release,"cooperative",80,0);
    let mut gateway=Gateway::start(&coop,"gateway-admin",&db,&admin_policy(),&trusted);
    let mut records=Vec::new();
    let revision_arg=revision.to_string();let launch_args=["launch",job,launch,revision_arg.as_str()];
    let before_launch=events(&db,job);let launch_output=invoke(&gateway.socket,&launch_args);let launch_reply=parse(&launch_output);
    assert_eq!(launch_output.status.code(),Some(0));assert_eq!(launch_reply["result"]["state"],"running");wait_for(&started,Duration::from_secs(5));
    record(&mut records,"native-launch",json!({"socket":gateway.socket,"args":launch_args}),&launch_output,before_launch,events(&db,job));

    // Real viewer peer denial uses SO_PEERCRED against a scoped viewer policy.
    let viewer=Gateway::start(&coop,"gateway-viewer",&db,&viewer_policy(),&trusted);
    let stop_args=["stop-graceful",job,launch,stop_id,"600"];
    let before_viewer=events(&db,job);let viewer_output=invoke(&viewer.socket,&stop_args);let viewer_reply=parse(&viewer_output);
    let after_viewer=events(&db,job);assert_eq!(viewer_output.status.code(),Some(3));assert_eq!(viewer_reply["ok"],false);assert_eq!(after_viewer,before_viewer);
    record(&mut records,"viewer-peer-policy-denial",json!({"socket":viewer.socket,"args":stop_args}),&viewer_output,before_viewer,after_viewer);
    drop(viewer);

    // Caller PID and unknown fields cannot be accepted as process authority.
    let worker_pid=read_marker(&started)[0]["pid"].clone();
    let forged=json!({"op":"local_stop_graceful","job_id":job,"launch_id":launch,"stop_id":"forged-stop","grace_ms":600,"pid":worker_pid});
    let before_forged=events(&db,job);let (forged_reply,forged_request)=raw_request(&gateway.socket,&forged);let after_forged=events(&db,job);
    assert_eq!(forged_reply["ok"],false);assert_eq!(after_forged,before_forged);
    records.push(json!({"phase":"forged-pid-field-rejected","request":forged_request,"response":forged_reply,"events_before":before_forged,"events_after":after_forged}));
    let unknown=json!({"op":"local_stop_graceful","job_id":job,"launch_id":launch,"stop_id":"unknown-field-stop","grace_ms":600,"signal":9});
    let before_unknown=events(&db,job);let (unknown_reply,unknown_request)=raw_request(&gateway.socket,&unknown);let after_unknown=events(&db,job);
    assert_eq!(unknown_reply["ok"],false);assert_eq!(after_unknown,before_unknown);
    records.push(json!({"phase":"unknown-request-field-rejected","request":unknown_request,"response":unknown_reply,"events_before":before_unknown,"events_after":after_unknown}));

    let before_stop=events(&db,job);let started_at=Instant::now();
    let stop_output=invoke(&gateway.socket,&stop_args);let elapsed=started_at.elapsed();let stop_reply=parse(&stop_output);
    let after_stop=events(&db,job);assert_eq!(stop_output.status.code(),Some(0));
    assert_eq!(stop_reply["ok"],true);assert_eq!(stop_reply["result"]["state"],"exit_observed");
    assert_eq!(stop_reply["result"]["mode"],"term_then_kill");assert_eq!(stop_reply["result"]["grace_ms"],600);
    assert_eq!(stop_reply["result"]["term_attempted"],true);assert_eq!(stop_reply["result"]["kill_attempted"],false);
    assert_eq!(stop_reply["result"]["exit"]["code"],0);assert!(elapsed>=Duration::from_millis(50));
    let stop_events=after_stop.as_array().unwrap().iter().filter(|e|e["kind"]=="LOCAL_STOP_REQUESTED").count();assert_eq!(stop_events,1);
    assert_eq!(read_marker(&started).len(),1);let term=read_marker(&term_seen);assert_eq!(term.len(),1);
    let cleanup_json:Value=serde_json::from_slice(&fs::read(&cleanup).unwrap()).unwrap();
    let term_json:Value=serde_json::from_slice(&fs::read(&term_seen).unwrap()).unwrap();
    assert!(cleanup_json["at_ms"].as_u64().unwrap()>=term_json["at_ms"].as_u64().unwrap());
    let held_before_finalize=balances(&db);assert!(reserved(&held_before_finalize)>0,"stop/exit does not finalize");
    record(&mut records,"graceful-term-cleanup-exit",json!({"socket":gateway.socket,"args":stop_args,"elapsed_ms":elapsed.as_millis()}),&stop_output,before_stop,after_stop.clone());

    let before_replay=events(&db,job);let replay_output=invoke(&gateway.socket,&stop_args);let replay_reply=parse(&replay_output);
    assert_eq!(replay_output.status.code(),Some(0));assert_eq!(replay_reply["result"]["replayed"],true);
    assert_eq!(read_marker(&term_seen).len(),1);assert_eq!(read_marker(&cleanup).len(),1);assert_eq!(events(&db,job),before_replay);
    record(&mut records,"exact-graceful-replay-no-second-term",json!({"socket":gateway.socket,"args":stop_args}),&replay_output,before_replay,events(&db,job));

    let conflict_grace=["stop-graceful",job,launch,stop_id,"601"];
    let before_grace_conflict=events(&db,job);let grace_conflict_output=invoke(&gateway.socket,&conflict_grace);let grace_conflict=parse(&grace_conflict_output);
    assert_eq!(grace_conflict_output.status.code(),Some(3));assert_eq!(grace_conflict["ok"],false);assert_eq!(events(&db,job),before_grace_conflict);
    record(&mut records,"conflicting-grace-rejected",json!({"socket":gateway.socket,"args":conflict_grace}),&grace_conflict_output,before_grace_conflict,events(&db,job));
    let conflict_mode=["stop",job,launch,stop_id];
    let before_mode_conflict=events(&db,job);let mode_conflict_output=invoke(&gateway.socket,&conflict_mode);let mode_conflict=parse(&mode_conflict_output);
    assert_eq!(mode_conflict_output.status.code(),Some(3));assert_eq!(mode_conflict["ok"],false);assert_eq!(events(&db,job),before_mode_conflict);
    assert_eq!(read_marker(&term_seen).len(),1);assert_eq!(read_marker(&cleanup).len(),1);
    record(&mut records,"conflicting-force-mode-rejected",json!({"socket":gateway.socket,"args":conflict_mode}),&mode_conflict_output,before_mode_conflict,events(&db,job));

    let resume_args=["resume",job,launch];let before_resume=events(&db,job);let resume_output=invoke(&gateway.socket,&resume_args);let resume_reply=parse(&resume_output);
    assert_eq!(resume_output.status.code(),Some(0));assert_eq!(resume_reply["result"]["stop"]["stop_id"],stop_id);
    assert_eq!(resume_reply["result"]["stop"]["mode"],"term_then_kill");assert_eq!(resume_reply["result"]["stop"]["grace_ms"],600);
    record(&mut records,"resume-retains-exact-plan",json!({"socket":gateway.socket,"args":resume_args}),&resume_output,before_resume,events(&db,job));
    let finalize_args=["finalize",job,launch,"completed"];let before_finalize=events(&db,job);let finalize_output=invoke(&gateway.socket,&finalize_args);
    assert_eq!(parse(&finalize_output)["ok"],true);assert_eq!(reserved(&balances(&db)),0);
    record(&mut records,"explicit-finalize-releases-capacity",json!({"socket":gateway.socket,"args":finalize_args}),&finalize_output,before_finalize,events(&db,job));
    histories.insert("cooperative_cleanup_before_sigkill".into(),json!({"job_id":job,"launch_id":launch,
        "worker_start":read_marker(&started),"term_seen":term_json,"cleanup":cleanup_json,
        "worker_exit":serde_json::from_slice::<Value>(&fs::read(&exited).unwrap()).unwrap(),
        "stop_event_payload":after_stop.as_array().unwrap().iter().find(|e|e["kind"]=="LOCAL_STOP_REQUESTED").unwrap()["payload"],
        "held_balances_before_finalize":held_before_finalize,"balances_after_finalize":balances(&db),"records":records}));
    drop(gateway);

    // An ignoring fixed worker proves grace expiry escalates through the owned
    // Child handle and records the actual signal 9 wait status.
    let ignore=root.path().join("ignore-term");fs::create_dir_all(&ignore).unwrap();
    let job="ignore-worker-job";let launch="ignore-worker-launch";let stop_id="ignore-stop-id";
    let (db,revision)=setup(&ignore,job);let started=ignore.join("started.jsonl");let term_seen=ignore.join("term-seen.json");
    let cleanup=ignore.join("cleanup.json");let exited=ignore.join("exited.json");let release=ignore.join("release");let _release=Release(release.clone());
    let trusted=profile(&ignore,&started,&term_seen,&cleanup,&exited,&release,"ignore",0,0);
    let gateway=Gateway::start(&ignore,"gateway-ignore",&db,&admin_policy(),&trusted);
    let revision_arg=revision.to_string();let launch_args=["launch",job,launch,revision_arg.as_str()];let launch_output=invoke(&gateway.socket,&launch_args);assert_eq!(parse(&launch_output)["result"]["state"],"running");wait_for(&started,Duration::from_secs(5));
    let grace_ms="240";let stop_args=["stop-graceful",job,launch,stop_id,grace_ms];let before=events(&db,job);let start=Instant::now();
    let stop_output=invoke(&gateway.socket,&stop_args);let elapsed=start.elapsed();let reply=parse(&stop_output);let after=events(&db,job);
    assert_eq!(stop_output.status.code(),Some(0));assert_eq!(reply["result"]["exit"]["signal"],9);
    assert_eq!(reply["result"]["term_attempted"],true);assert_eq!(reply["result"]["kill_attempted"],true);
    assert!(elapsed>=Duration::from_millis(200),"SIGKILL escalation must wait selected grace: {elapsed:?}");
    assert!(!term_seen.exists());assert!(!cleanup.exists());assert!(!exited.exists());assert_eq!(read_marker(&started).len(),1);
    assert_eq!(after.as_array().unwrap().iter().filter(|e|e["kind"]=="LOCAL_STOP_REQUESTED").count(),1);
    let held=balances(&db);assert!(reserved(&held)>0);
    let before_replay=events(&db,job);let replay=invoke(&gateway.socket,&stop_args);let replay_reply=parse(&replay);
    assert_eq!(replay_reply["result"]["replayed"],true);assert_eq!(events(&db,job),before_replay);assert_eq!(read_marker(&started).len(),1);
    let finalize_args=["finalize",job,launch,"failed"];let finalize_output=invoke(&gateway.socket,&finalize_args);
    assert_eq!(parse(&finalize_output)["ok"],true);assert_eq!(reserved(&balances(&db)),0);
    histories.insert("ignored_term_escalates_to_signal9".into(),json!({"job_id":job,"launch_id":launch,
        "worker_start":read_marker(&started),"launch_stdout":String::from_utf8_lossy(&launch_output.stdout),
        "term_seen_marker":term_seen.exists(),"cleanup_marker":cleanup.exists(),
        "exit_marker":exited.exists(),"stop_response":reply,"elapsed_ms":elapsed.as_millis(),
        "events_before_stop":before,"events_after_stop":after,"held_balances_before_finalize":held,
        "finalize_stdout":String::from_utf8_lossy(&finalize_output.stdout),"balances_after_finalize":balances(&db),
        "launch_command":["resource-session",gateway.socket,"launch",job,launch,revision],
        "stop_command":["resource-session",gateway.socket,"stop-graceful",job,launch,stop_id,grace_ms]}));
    drop(gateway);

    // Controller loss after TERM enters ordinary cleanup but before its marker:
    // cold replay must not signal/adopt the still-live orphan or finalize it.
    let cold=root.path().join("cold-cleanup-delay");fs::create_dir_all(&cold).unwrap();
    let job="cold-cleanup-job";let launch="cold-cleanup-launch";let stop_id="cold-cleanup-stop";
    let (db,revision)=setup(&cold,job);let started=cold.join("started.jsonl");let term_seen=cold.join("term-seen.json");
    let cleanup=cold.join("cleanup.json");let exited=cold.join("exited.json");let release=cold.join("release");let _release=Release(release.clone());
    let trusted=profile(&cold,&started,&term_seen,&cleanup,&exited,&release,"cooperative",1200,0);
    let mut hot_gateway=Gateway::start(&cold,"gateway-hot",&db,&admin_policy(),&trusted);
    let revision_arg=revision.to_string();let launch_args=["launch",job,launch,revision_arg.as_str()];let launch_output=invoke(&hot_gateway.socket,&launch_args);assert_eq!(parse(&launch_output)["result"]["state"],"running");wait_for(&started,Duration::from_secs(5));
    let grace="1800";let stop_args=["stop-graceful",job,launch,stop_id,grace];let stop_socket=hot_gateway.socket.clone();
    let stop_thread=thread::spawn(move||invoke(&stop_socket,&stop_args));
    wait_for(&term_seen,Duration::from_secs(5));assert!(!cleanup.exists(),"gateway loss is injected during bounded cleanup delay");
    let before_loss=events(&db,job);let held_before_loss=balances(&db);assert!(reserved(&held_before_loss)>0);
    hot_gateway.kill();drop(hot_gateway);
    let lost_output=stop_thread.join().unwrap();let lost_reply=parse(&lost_output);
    assert_eq!(lost_output.status.code(),Some(4));assert_eq!(lost_reply["outcome"],"outcome_unknown");
    let cold_gateway=Gateway::start(&cold,"gateway-cold",&db,&admin_policy(),&trusted);
    let before_cold=events(&db,job);let cold_output=invoke(&cold_gateway.socket,&stop_args);let cold_reply=parse(&cold_output);let after_cold=events(&db,job);
    assert_eq!(cold_output.status.code(),Some(0));assert_eq!(cold_reply["result"]["state"],"unknown");
    assert_eq!(cold_reply["result"]["replayed"],true);
    assert!(cold_reply["result"]["term_attempted"].is_null(),"lost Child progress must not be fabricated as false");
    assert!(cold_reply["result"]["kill_attempted"].is_null(),"lost Child progress must not be fabricated as false");
    assert_eq!(after_cold,before_cold);
    assert!(!cleanup.exists(),"cold replay occurs before delayed cleanup completes");
    assert_eq!(read_marker(&started).len(),1);assert_eq!(read_marker(&term_seen).len(),1);assert!(reserved(&balances(&db))>0);
    wait_for(&cleanup,Duration::from_secs(5));wait_for(&exited,Duration::from_secs(5));
    let after_orphan_exit=events(&db,job);assert_eq!(after_orphan_exit,after_cold,"orphan natural exit is not fabricated into Store evidence");
    assert_eq!(Store::open(&db).unwrap().job(job).unwrap()["state"],"RUNNING");assert!(reserved(&balances(&db))>0);
    histories.insert("gateway_loss_during_term_cleanup_cold_unknown".into(),json!({
        "job_id":job,"launch_id":launch,"worker_start":read_marker(&started),
        "term_seen":serde_json::from_slice::<Value>(&fs::read(&term_seen).unwrap()).unwrap(),
        "cleanup_after_cold_replay":serde_json::from_slice::<Value>(&fs::read(&cleanup).unwrap()).unwrap(),
        "worker_exit":serde_json::from_slice::<Value>(&fs::read(&exited).unwrap()).unwrap(),
        "lost_client":{"command":["resource-session",hot_gateway.socket,"stop-graceful",job,launch,stop_id,grace],
            "exit_code":lost_output.status.code(),"stdout":String::from_utf8_lossy(&lost_output.stdout),"stderr":String::from_utf8_lossy(&lost_output.stderr)},
        "cold_client":{"command":["resource-session",cold_gateway.socket,"stop-graceful",job,launch,stop_id,grace],
            "exit_code":cold_output.status.code(),"stdout":String::from_utf8_lossy(&cold_output.stdout),"stderr":String::from_utf8_lossy(&cold_output.stderr)},
        "events_before_gateway_loss":before_loss,"events_before_cold_replay":before_cold,
        "events_after_cold_replay":after_cold,"events_after_orphan_exit":after_orphan_exit,
        "balances_before_gateway_loss":held_before_loss,"balances_after_cold_replay":balances(&db)}));
    drop(cold_gateway);

    persist(json!({
        "why":"cooperative stop adds orderly cleanup while preserving exact owned-child custody and explicit finalization",
        "what":"actual resource-session requests, real SO_PEERCRED gateway, fixed workers, signal/cleanup markers, Store events and balances",
        "how_certain":"experimental; native assertions and retained reply/event/marker records",
        "what_not_tested":["hostile same-UID or root","remote providers","whole-host loss","arbitrary programs","descendant termination","hard wall-time stop","canonical disposal semantics"],
        "histories":histories,"source_sha256":source_hashes()
    }));
}
