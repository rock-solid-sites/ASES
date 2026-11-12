//! Native cancellation-driver histories over the existing session client,
//! Unix gateway, retained Child, and Store. Workers are fixed tests in this
//! binary; no shell command or caller-supplied executable is used.
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
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use std::time::{Duration, Instant};

static TERM_REQUESTED: AtomicBool = AtomicBool::new(false);
const ACCOUNT: &str = "cancel-drive-account";
const PROJECT: &str = "cancel-drive-project";
const ENVIRONMENT: &str = "cancel-drive-environment";

extern "C" fn term_flag_only(_: libc::c_int) { TERM_REQUESTED.store(true, Ordering::Relaxed); }
fn admin_policy() -> Policy { Policy { administrators: vec![unsafe { libc::geteuid() }], callers: vec![] } }
fn account() -> Account {
    Account { id: ACCOUNT.into(), provider: "local".into(), payer_ref: "cancel-drive-test".into(),
        registration_status: "verified".into(), credential_status: "working".into(),
        entitlement_status: "active".into(), allowed_projects: vec![PROJECT.into()],
        source: "synthetic-native-cancel-drive-test".into(), observed_at: now(), ttl_seconds: 3600 }
}
fn meter() -> Meter {
    Meter { id: "cancel-drive-meter".into(), account: ACCOUNT.into(), provider: "local".into(),
        product: "fixed-cancel-worker".into(), period: "cancel-drive-test".into(), unit: "units".into(),
        limit: 100, guard: 0, observed_at: now(), ttl_seconds: 3600,
        source: "synthetic-native-cancel-drive-test".into(), period_start: None, period_end: None,
        price_per_unit_micros: 0, price_currency: None, chargeable: false }
}
fn environment() -> Environment {
    Environment { id: ENVIRONMENT.into(), account: ACCOUNT.into(), provider: "local".into(), max_parallel: 1,
        observed_at: now(), ttl_seconds: 3600, source: "synthetic-native-cancel-drive-test".into() }
}
fn proposal(job: &str) -> Proposal {
    Proposal { job_id: job.into(), account_id: ACCOUNT.into(), project_id: PROJECT.into(),
        environment_id: ENVIRONMENT.into(), estimated_wall_seconds: 60,
        claims: vec![Claim { meter_id: "cancel-drive-meter".into(), amount: 50 }],
        paid_spend_cap_micros: None, paid_spend_cap_currency: None, forecast_context: None }
}
fn setup(dir: &Path, job: &str) -> PathBuf {
    let db = dir.join("control.sqlite");
    let mut store = Store::open(&db).unwrap();
    store.register_account(&account()).unwrap(); store.register_meter(&meter()).unwrap();
    store.register_environment(&environment()).unwrap();
    let revision = store.catalog_version().unwrap();
    store.reserve(&proposal(job), revision, now()).unwrap();
    store.acknowledge(job, &format!("ack-{job}"), revision, now()).unwrap();
    db
}
fn profile(dir: &Path, marker: &Path, term: &Path, cleanup: &Path, exited: &Path, mode: &str) -> Value {
    json!({"program":std::env::current_exe().unwrap(),
        "args":["--exact","cancel_drive_fixed_worker","--nocapture"],"cwd":dir,
        "env":{"ASES_CANCEL_MARKER":marker,"ASES_CANCEL_TERM":term,"ASES_CANCEL_CLEANUP":cleanup,
            "ASES_CANCEL_EXITED":exited,"ASES_CANCEL_RELEASE":dir.join("release"),"ASES_CANCEL_MODE":mode},
        "account_id":ACCOUNT,"project_id":PROJECT,"environment_id":ENVIRONMENT})
}
struct Gateway { child: Child, socket: PathBuf }
impl Gateway {
    fn start(dir:&Path,name:&str,db:&Path,profile:&Value)->Self {
        let socket=dir.join(format!("{name}.sock"));
        let policy=dir.join(format!("{name}-policy.json")); let prof=dir.join(format!("{name}-profile.json"));
        fs::write(&policy,serde_json::to_vec(&admin_policy()).unwrap()).unwrap();
        fs::write(&prof,serde_json::to_vec(profile).unwrap()).unwrap();
        let child=Command::new(env!("CARGO_BIN_EXE_resource-gateway")).arg(db).arg(&socket).arg(&policy)
            .arg(env!("CARGO_BIN_EXE_ases-resource-control")).arg(&prof).stdin(Stdio::null())
            .stdout(Stdio::null()).stderr(Stdio::null()).spawn().unwrap();
        wait_for(&socket,Duration::from_secs(10)); Self{child,socket}
    }
    fn kill(&mut self){let _=self.child.kill();let _=self.child.wait();}
}
impl Drop for Gateway { fn drop(&mut self){self.kill();} }
struct Release(PathBuf);
impl Drop for Release { fn drop(&mut self){let _=fs::write(&self.0,b"test cleanup release\n");} }
fn invoke_session(socket:&Path,args:&[&str])->Output {
    Command::new(env!("CARGO_BIN_EXE_resource-session")).arg(socket).args(args)
        .stdin(Stdio::null()).output().unwrap()
}
fn invoke_cancel(socket:&Path,job:&str,launch:&str,stop:&str,grace:&str)->Output {
    Command::new(env!("CARGO_BIN_EXE_resource-drive")).arg("cancel").arg(socket).arg(job).arg(launch)
        .arg(stop).arg(grace).stdin(Stdio::null()).output().unwrap()
}
fn parse(out:&Output)->Value { serde_json::from_slice(&out.stdout).unwrap_or_else(|_|panic!(
    "not JSON: status={:?}, stdout={}, stderr={}",out.status.code(),String::from_utf8_lossy(&out.stdout),String::from_utf8_lossy(&out.stderr))) }
fn events(db:&Path,job:&str)->Value { serde_json::to_value(Store::open(db).unwrap().event_log(Some(job)).unwrap()).unwrap() }
fn balances(db:&Path)->Value { serde_json::to_value(Store::open(db).unwrap().balances(now()).unwrap()).unwrap() }
fn reserved(v:&Value)->i64 { v.as_array().unwrap().iter().find(|r|r["meter_id"]=="cancel-drive-meter")
    .and_then(|r|r["active_reserved_remaining"].as_i64()).unwrap() }
fn lines(path:&Path)->Vec<Value>{fs::read_to_string(path).unwrap_or_default().lines().map(|l|serde_json::from_str(l).unwrap()).collect()}
fn wait_for(path:&Path,d:Duration){let end=Instant::now()+d;while Instant::now()<end{if path.exists(){return}thread::sleep(Duration::from_millis(10));}panic!("marker did not appear: {}",path.display())}
fn event_count(v:&Value,kind:&str)->usize{v.as_array().unwrap().iter().filter(|e|e["kind"]==kind).count()}
fn launch(g:&Gateway,db:&Path,job:&str,launch:&str,marker:&Path){
    let rev=Store::open(db).unwrap().catalog_version().unwrap().to_string();
    let out=invoke_session(&g.socket,&["launch",job,launch,&rev]); let reply=parse(&out);
    assert_eq!(out.status.code(),Some(0),"launch failed: {reply}");
    assert_eq!(reply["result"]["state"],"running");wait_for(marker,Duration::from_secs(5));
}
fn hashes()->Value { let root=PathBuf::from(env!("CARGO_MANIFEST_DIR"));let mut m=serde_json::Map::new();
    for f in ["src/bin/resource-drive.rs","src/bin/resource-session.rs","src/bin/resource-gateway.rs","src/local.rs","src/lib.rs","tests/native_cancel_drive.rs"]{
        if let Ok(b)=fs::read(root.join(f)){m.insert(f.into(),json!(format!("{:x}",Sha256::digest(b))));}}
    Value::Object(m)
}
fn persist(v:Value){if let Some(p)=std::env::var_os("ASES_CANCEL_DRIVE_EVIDENCE_DIR"){
    let p=PathBuf::from(p);fs::create_dir_all(&p).unwrap();fs::write(p.join("native-cancel-drive.json"),serde_json::to_vec_pretty(&v).unwrap()).unwrap();}}

/// The fixed trusted profile executable. Its signal handler only sets a flag;
/// cleanup runs in ordinary code. The independent deadline bounds orphan life.
#[test]
fn cancel_drive_fixed_worker(){
    let Some(marker)=std::env::var_os("ASES_CANCEL_MARKER") else{return};
    let marker=PathBuf::from(marker);let term=PathBuf::from(std::env::var_os("ASES_CANCEL_TERM").unwrap());
    let cleanup=PathBuf::from(std::env::var_os("ASES_CANCEL_CLEANUP").unwrap());
    let exited=PathBuf::from(std::env::var_os("ASES_CANCEL_EXITED").unwrap());
    let release=PathBuf::from(std::env::var_os("ASES_CANCEL_RELEASE").unwrap());
    let mode=std::env::var("ASES_CANCEL_MODE").unwrap();
    if mode=="ignore" { assert_ne!(unsafe{libc::signal(libc::SIGTERM,libc::SIG_IGN)},libc::SIG_ERR); }
    else {let mut action:libc::sigaction=unsafe{std::mem::zeroed()};action.sa_sigaction=term_flag_only as *const () as libc::sighandler_t;
        unsafe{libc::sigemptyset(&mut action.sa_mask);assert_eq!(libc::sigaction(libc::SIGTERM,&action,std::ptr::null_mut()),0);}}
    TERM_REQUESTED.store(false,Ordering::Relaxed);
    let pid=std::process::id();let stat=fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();
    let start_token=stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap().to_string();
    let mut f=OpenOptions::new().create(true).append(true).open(marker).unwrap();
    serde_json::to_writer(&mut f,&json!({"pid":pid,"start_token":start_token,"mode":mode})).unwrap();f.write_all(b"\n").unwrap();f.sync_all().unwrap();
    let deadline=Instant::now()+Duration::from_secs(12);
    while Instant::now()<deadline {
        if release.exists(){fs::write(&exited,b"test cleanup release\n").unwrap();std::process::exit(0);}
        if TERM_REQUESTED.swap(false,Ordering::Relaxed){fs::write(&term,b"term observed\n").unwrap();
            thread::sleep(Duration::from_millis(60));fs::write(&cleanup,b"cleanup completed\n").unwrap();
            fs::write(&exited,b"cooperative exit\n").unwrap();std::process::exit(0);}
        thread::sleep(Duration::from_millis(5));
    }
    fs::write(&exited,b"bounded self timeout\n").unwrap();std::process::exit(0);
}

#[test]
fn native_cancel_driver_histories(){
    let root=tempfile::tempdir().unwrap();let mut histories=serde_json::Map::new();

    // Cooperative cleanup: stop-graceful produces exact exit evidence, then
    // the driver alone chooses cancelled and performs one explicit finalize.
    let d=root.path().join("cooperative");fs::create_dir_all(&d).unwrap();let job="cancel-coop-job";let lid="cancel-coop-launch";
    let db=setup(&d,job);let marker=d.join("worker.jsonl");let term=d.join("term");let cleanup=d.join("cleanup");let exited=d.join("exited");let _release=Release(d.join("release"));
    let prof=profile(&d,&marker,&term,&cleanup,&exited,"cooperative");let gateway=Gateway::start(&d,"gateway",&db,&prof);launch(&gateway,&db,job,lid,&marker);
    let before=events(&db,job);let held_before=balances(&db);assert!(reserved(&held_before)>0);
    let output=invoke_cancel(&gateway.socket,job,lid,"coop-stop","700");let reply=parse(&output);let after=events(&db,job);
    assert_eq!(output.status.code(),Some(0),"{reply}");assert_eq!(reply["action"],"cancel");assert_eq!(reply["outcome"],"finalized");
    assert_eq!(reply["selected_outcome"],"cancelled");assert_eq!(reply["finalization"]["result"]["outcome"],"cancelled");
    assert_eq!(reply["stop_response"]["result"]["state"],"exit_observed");
    assert_eq!(reply["stop_response"]["result"]["mode"],"term_then_kill");assert_eq!(reply["stop_response"]["result"]["grace_ms"],700);
    assert_eq!(reply["stop_response"]["result"]["replayed"],false);
    assert!(term.exists()&&cleanup.exists()&&exited.exists());assert_eq!(lines(&marker).len(),1);
    assert_eq!(event_count(&after,"LOCAL_STOP_REQUESTED"),1);assert_eq!(event_count(&after,"LAUNCH_EXIT_OBSERVED"),1);
    assert_eq!(event_count(&after,"FINALIZED"),1);assert!(reserved(&balances(&db))<reserved(&held_before));
    assert_eq!(reserved(&balances(&db)),0);
    histories.insert("cooperative_cleanup_then_cancelled_finalize".into(),json!({"command":["resource-drive","cancel",gateway.socket,job,lid,"coop-stop","700"],
        "output":{"status":output.status.code(),"stdout":String::from_utf8_lossy(&output.stdout),"stderr":String::from_utf8_lossy(&output.stderr)},
        "events_before":before,"events_after":after,"worker_markers":{"start":lines(&marker),"term":term.exists(),"cleanup":cleanup.exists(),"exit":exited.exists()},"balances_after":balances(&db)}));
    drop(gateway);

    // SIG_IGN forces bounded grace expiry and exact owned-child SIGKILL wait.
    let d=root.path().join("forced");fs::create_dir_all(&d).unwrap();let job="cancel-force-job";let lid="cancel-force-launch";let db=setup(&d,job);
    let marker=d.join("worker.jsonl");let term=d.join("term");let cleanup=d.join("cleanup");let exited=d.join("exited");let _release=Release(d.join("release"));
    let prof=profile(&d,&marker,&term,&cleanup,&exited,"ignore");let gateway=Gateway::start(&d,"gateway",&db,&prof);launch(&gateway,&db,job,lid,&marker);
    let t=Instant::now();let output=invoke_cancel(&gateway.socket,job,lid,"force-stop","180");let elapsed=t.elapsed();let reply=parse(&output);let after=events(&db,job);
    assert_eq!(output.status.code(),Some(0),"{reply}");assert_eq!(reply["stop_response"]["result"]["exit"]["signal"],9);
    assert_eq!(reply["stop_response"]["result"]["term_attempted"],true);assert_eq!(reply["stop_response"]["result"]["kill_attempted"],true);
    assert!(elapsed>=Duration::from_millis(150));assert!(!term.exists()&&!cleanup.exists());assert_eq!(lines(&marker).len(),1);
    assert_eq!(event_count(&after,"LOCAL_STOP_REQUESTED"),1);assert_eq!(event_count(&after,"FINALIZED"),1);assert_eq!(reserved(&balances(&db)),0);
    histories.insert("sigkill_fallback".into(),json!({"output":String::from_utf8_lossy(&output.stdout),"elapsed_ms":elapsed.as_millis(),"events":after,
        "worker_markers":{"start":lines(&marker),"term":term.exists(),"cleanup":cleanup.exists(),"exit":exited.exists()},"balances_after":balances(&db)}));drop(gateway);

    // A real stop is forwarded and committed, then its reply is dropped. The
    // driver must preserve uncertainty and must not issue finalize or retry.
    let d=root.path().join("stop-loss");fs::create_dir_all(&d).unwrap();let job="cancel-stop-loss-job";let lid="cancel-stop-loss-launch";let db=setup(&d,job);
    let marker=d.join("worker.jsonl");let term=d.join("term");let cleanup=d.join("cleanup");let exited=d.join("exited");let _release=Release(d.join("release"));
    let prof=profile(&d,&marker,&term,&cleanup,&exited,"cooperative");let gateway=Gateway::start(&d,"gateway",&db,&prof);launch(&gateway,&db,job,lid,&marker);
    let proxy_path=d.join("drop-stop.sock");let (proxy_tx,proxy_rx)=std::sync::mpsc::channel();let proxy=drop_reply_once(proxy_path.clone(),gateway.socket.clone(),"local_stop_graceful",proxy_tx);
    wait_for(&proxy_path,Duration::from_secs(3));let output=invoke_cancel(&proxy_path,job,lid,"lost-stop","600");let reply=parse(&output);let captured=proxy_rx.recv_timeout(Duration::from_secs(3)).unwrap();let extras=proxy.join().unwrap();let after=events(&db,job);
    assert_eq!(output.status.code(),Some(3),"{reply}");assert_eq!(reply["outcome"],"recovery_needed");assert_eq!(reply["last_action"],"stop-graceful");
    assert_eq!(reply["stop_id"],"lost-stop");assert_eq!(reply["client_status"],4);assert_eq!(reply["client_reply"]["outcome"],"outcome_unknown");
    assert_eq!(captured["request"]["op"],"local_stop_graceful");assert_eq!(captured["gateway_reply"]["result"]["state"],"exit_observed");
    assert_eq!(extras,0);assert_eq!(event_count(&after,"LOCAL_STOP_REQUESTED"),1);assert_eq!(event_count(&after,"LAUNCH_EXIT_OBSERVED"),1);
    assert_eq!(event_count(&after,"FINALIZED"),0);assert!(reserved(&balances(&db))>0);assert!(term.exists()&&cleanup.exists());
    // This is explicit test cleanup through the existing client after assertions.
    let cleanup_finalize=invoke_session(&gateway.socket,&["finalize",job,lid,"cancelled"]);assert_eq!(parse(&cleanup_finalize)["ok"],true);
    histories.insert("forwarded_stop_reply_lost_no_finalize".into(),json!({"driver_output":String::from_utf8_lossy(&output.stdout),"proxy_exchange":captured,"additional_connections":extras,
        "events_before_test_cleanup":after,"balances_before_test_cleanup":balances(&db),"test_cleanup_finalize":String::from_utf8_lossy(&cleanup_finalize.stdout)}));drop(gateway);

    // The operation succeeds in Store but its selector is changed in transit.
    // The driver must reject the mismatched observation and keep capacity held.
    let d=root.path().join("stop-selector-mutation");fs::create_dir_all(&d).unwrap();let job="cancel-stop-mutate-job";let lid="cancel-stop-mutate-launch";let db=setup(&d,job);
    let marker=d.join("worker.jsonl");let term=d.join("term");let cleanup=d.join("cleanup");let exited=d.join("exited");let _release=Release(d.join("release"));
    let prof=profile(&d,&marker,&term,&cleanup,&exited,"cooperative");let gateway=Gateway::start(&d,"gateway",&db,&prof);launch(&gateway,&db,job,lid,&marker);
    let proxy_path=d.join("mutate-stop.sock");let (proxy_tx,proxy_rx)=std::sync::mpsc::channel();
    let proxy=mutate_reply_once(proxy_path.clone(),gateway.socket.clone(),"local_stop_graceful","stop_id",proxy_tx);
    wait_for(&proxy_path,Duration::from_secs(3));let output=invoke_cancel(&proxy_path,job,lid,"selector-bound","600");let reply=parse(&output);
    let captured=proxy_rx.recv_timeout(Duration::from_secs(3)).unwrap();let extras=proxy.join().unwrap();let after=events(&db,job);
    assert_eq!(output.status.code(),Some(3),"{reply}");assert_eq!(reply["reason"],"unsupported_reply");assert_eq!(reply["phase"],"stop-graceful");
    assert_eq!(reply["last_action"],"stop-graceful");assert_eq!(reply["stop_id"],"selector-bound");assert_eq!(extras,0);
    assert_eq!(captured["gateway_reply"]["result"]["stop_id"],"selector-bound");
    assert_eq!(captured["forwarded_reply"]["result"]["stop_id"],"mutated-stop_id");
    assert_eq!(event_count(&after,"LOCAL_STOP_REQUESTED"),1);assert_eq!(event_count(&after,"LAUNCH_EXIT_OBSERVED"),1);
    assert_eq!(event_count(&after,"FINALIZED"),0);assert!(reserved(&balances(&db))>0);assert!(cleanup.exists());
    let cleanup_finalize=invoke_session(&gateway.socket,&["finalize",job,lid,"cancelled"]);assert_eq!(parse(&cleanup_finalize)["ok"],true);
    histories.insert("mutated_stop_selector_reply_rejected_no_finalize".into(),json!({"driver_output":String::from_utf8_lossy(&output.stdout),"proxy_exchange":captured,
        "additional_connections":extras,"events_before_test_cleanup":after,"balances_before_test_cleanup":balances(&db),"test_cleanup_finalize":String::from_utf8_lossy(&cleanup_finalize.stdout)}));drop(gateway);

    // Real stop and finalize commit, but finalization reply is dropped. The
    // Store is CLOSED and capacity released; the failed invocation does not retry.
    let d=root.path().join("finalize-loss");fs::create_dir_all(&d).unwrap();let job="cancel-final-loss-job";let lid="cancel-final-loss-launch";let db=setup(&d,job);
    let marker=d.join("worker.jsonl");let term=d.join("term");let cleanup=d.join("cleanup");let exited=d.join("exited");let _release=Release(d.join("release"));
    let prof=profile(&d,&marker,&term,&cleanup,&exited,"cooperative");let gateway=Gateway::start(&d,"gateway",&db,&prof);launch(&gateway,&db,job,lid,&marker);
    let proxy_path=d.join("drop-finalize.sock");let (proxy_tx,proxy_rx)=std::sync::mpsc::channel();let proxy=drop_reply_once(proxy_path.clone(),gateway.socket.clone(),"local_finalize",proxy_tx);
    wait_for(&proxy_path,Duration::from_secs(3));let output=invoke_cancel(&proxy_path,job,lid,"lost-final","600");let reply=parse(&output);let captured=proxy_rx.recv_timeout(Duration::from_secs(3)).unwrap();let extras=proxy.join().unwrap();let after=events(&db,job);
    assert_eq!(output.status.code(),Some(3),"{reply}");assert_eq!(reply["outcome"],"recovery_needed");assert_eq!(reply["last_action"],"finalize");
    assert_eq!(reply["stop_id"],"lost-final");assert_eq!(reply["client_status"],4);assert_eq!(reply["client_reply"]["outcome"],"outcome_unknown");
    assert_eq!(captured["request"]["op"],"local_finalize");assert_eq!(captured["gateway_reply"]["ok"],true);assert_eq!(captured["gateway_reply"]["result"]["finalization"],"CLOSED");
    assert_eq!(extras,0);assert_eq!(Store::open(&db).unwrap().job(job).unwrap()["state"],"CLOSED");
    assert_eq!(event_count(&after,"LOCAL_STOP_REQUESTED"),1);assert_eq!(event_count(&after,"LAUNCH_EXIT_OBSERVED"),1);assert_eq!(event_count(&after,"FINALIZED"),1);
    assert_eq!(reserved(&balances(&db)),0);assert_eq!(lines(&marker).len(),1);
    histories.insert("forwarded_finalize_reply_lost_closed_no_retry".into(),json!({"driver_output":String::from_utf8_lossy(&output.stdout),"proxy_exchange":captured,
        "additional_connections":extras,"events_after":after,"balances_after":balances(&db)}));drop(gateway);

    // Finalization really commits as cancelled, then a proxy changes only the
    // returned outcome. The consumer rejects the inconsistent confirmation;
    // Store remains durably CLOSED and capacity is already released.
    let d=root.path().join("final-outcome-mutation");fs::create_dir_all(&d).unwrap();let job="cancel-final-mutate-job";let lid="cancel-final-mutate-launch";let db=setup(&d,job);
    let marker=d.join("worker.jsonl");let term=d.join("term");let cleanup=d.join("cleanup");let exited=d.join("exited");let _release=Release(d.join("release"));
    let prof=profile(&d,&marker,&term,&cleanup,&exited,"cooperative");let gateway=Gateway::start(&d,"gateway",&db,&prof);launch(&gateway,&db,job,lid,&marker);
    let proxy_path=d.join("mutate-finalize.sock");let (proxy_tx,proxy_rx)=std::sync::mpsc::channel();
    let proxy=mutate_reply_once(proxy_path.clone(),gateway.socket.clone(),"local_finalize","outcome",proxy_tx);
    wait_for(&proxy_path,Duration::from_secs(3));let output=invoke_cancel(&proxy_path,job,lid,"final-bound","600");let reply=parse(&output);
    let captured=proxy_rx.recv_timeout(Duration::from_secs(3)).unwrap();let extras=proxy.join().unwrap();let after=events(&db,job);
    assert_eq!(output.status.code(),Some(3),"{reply}");assert_eq!(reply["reason"],"unsupported_reply");assert_eq!(reply["phase"],"finalize");
    assert_eq!(reply["last_action"],"finalize");assert_eq!(reply["stop_id"],"final-bound");assert_eq!(extras,0);
    assert_eq!(captured["gateway_reply"]["result"]["outcome"],"cancelled");
    assert_eq!(captured["forwarded_reply"]["result"]["outcome"],"mutated-outcome");
    assert_eq!(Store::open(&db).unwrap().job(job).unwrap()["state"],"CLOSED");
    assert_eq!(event_count(&after,"LOCAL_STOP_REQUESTED"),1);assert_eq!(event_count(&after,"LAUNCH_EXIT_OBSERVED"),1);
    assert_eq!(event_count(&after,"FINALIZED"),1);assert_eq!(reserved(&balances(&db)),0);
    histories.insert("mutated_finalize_outcome_rejected_after_actual_commit".into(),json!({"driver_output":String::from_utf8_lossy(&output.stdout),"proxy_exchange":captured,
        "additional_connections":extras,"events_after":after,"balances_after":balances(&db)}));drop(gateway);

    // Gateway/controller loss destroys Child custody. A fresh driver sees
    // unknown, never adopts the worker PID, dispatches, stops, or finalizes.
    let d=root.path().join("cold");fs::create_dir_all(&d).unwrap();let job="cancel-cold-job";let lid="cancel-cold-launch";let db=setup(&d,job);
    let marker=d.join("worker.jsonl");let term=d.join("term");let cleanup=d.join("cleanup");let exited=d.join("exited");let release=d.join("release");let _release=Release(release.clone());
    let prof=profile(&d,&marker,&term,&cleanup,&exited,"cooperative");let mut hot=Gateway::start(&d,"gateway-hot",&db,&prof);launch(&hot,&db,job,lid,&marker);hot.kill();drop(hot);
    let gateway=Gateway::start(&d,"gateway-cold",&db,&prof);let before=events(&db,job);let output=invoke_cancel(&gateway.socket,job,lid,"cold-stop","600");let reply=parse(&output);let after=events(&db,job);
    assert_eq!(output.status.code(),Some(3),"{reply}");assert_eq!(reply["outcome"],"recovery_needed");assert_eq!(reply["reason"],"unknown_custody");
    assert_eq!(reply["last_action"],"stop-graceful");assert_eq!(reply["stop_id"],"cold-stop");assert_eq!(lines(&marker).len(),1);
    assert!(!term.exists()&&!cleanup.exists()&&!exited.exists());
    assert_eq!(after.as_array().unwrap().len(),before.as_array().unwrap().len()+1);
    assert_eq!(event_count(&after,"LOCAL_STOP_REQUESTED"),1,"cold controller may persist the selector but cannot act on the unowned PID");
    assert_eq!(event_count(&after,"LAUNCH_INTENT"),1,"cold cancellation must not redispatch");
    assert_eq!(event_count(&after,"FINALIZED"),0);assert!(reserved(&balances(&db))>0);
    let blocked_finalize=invoke_session(&gateway.socket,&["finalize",job,lid,"cancelled"]);assert_eq!(parse(&blocked_finalize)["ok"],false);
    assert_eq!(Store::open(&db).unwrap().job(job).unwrap()["state"],"RUNNING");assert!(reserved(&balances(&db))>0);
    drop(gateway);fs::write(&release,b"bounded cold cleanup\n").unwrap();wait_for(&exited,Duration::from_secs(4));
    histories.insert("cold_controller_unknown_no_adoption_finalize_dispatch".into(),json!({"driver_output":String::from_utf8_lossy(&output.stdout),"events_before":before,"events_after":after,
        "worker_markers":{"start":lines(&marker),"term":term.exists(),"cleanup":cleanup.exists(),"exit_after_release":exited.exists()},"blocked_finalize":String::from_utf8_lossy(&blocked_finalize.stdout),"balances":balances(&db)}));

    // Changed stop selector reaches the server as an error. It must not be
    // silently retried with the recorded selector or followed by finalization.
    let d=root.path().join("changed-selector");fs::create_dir_all(&d).unwrap();let job="cancel-selector-job";let lid="cancel-selector-launch";let db=setup(&d,job);
    let marker=d.join("worker.jsonl");let term=d.join("term");let cleanup=d.join("cleanup");let exited=d.join("exited");let _release=Release(d.join("release"));
    let prof=profile(&d,&marker,&term,&cleanup,&exited,"cooperative");let gateway=Gateway::start(&d,"gateway",&db,&prof);launch(&gateway,&db,job,lid,&marker);
    let seeded=invoke_session(&gateway.socket,&["stop-graceful",job,lid,"original-selector","600"]);assert_eq!(parse(&seeded)["ok"],true);
    let before=events(&db,job);let proxy_path=d.join("count-selector.sock");let (proxy_tx,proxy_rx)=std::sync::mpsc::channel();let proxy=record_one_error(proxy_path.clone(),gateway.socket.clone(),proxy_tx);
    wait_for(&proxy_path,Duration::from_secs(3));let output=invoke_cancel(&proxy_path,job,lid,"changed-selector","600");let reply=parse(&output);let request=proxy_rx.recv_timeout(Duration::from_secs(3)).unwrap();let extras=proxy.join().unwrap();let after=events(&db,job);
    assert_eq!(output.status.code(),Some(3),"{reply}");assert_eq!(reply["outcome"],"recovery_needed");assert_eq!(reply["last_action"],"stop-graceful");
    assert_eq!(reply["stop_id"],"changed-selector");assert_eq!(reply["client_status"],3);assert_eq!(reply["client_reply"]["ok"],false);
    assert_eq!(request["request"]["stop_id"],"changed-selector");assert_eq!(request["reply"]["ok"],false);assert_eq!(extras,0);
    assert_eq!(after,before);assert_eq!(event_count(&after,"LOCAL_STOP_REQUESTED"),1);assert_eq!(event_count(&after,"FINALIZED"),0);assert!(reserved(&balances(&db))>0);
    let cleanup_finalize=invoke_session(&gateway.socket,&["finalize",job,lid,"cancelled"]);assert_eq!(parse(&cleanup_finalize)["ok"],true);
    histories.insert("changed_selector_received_server_error_no_retry".into(),json!({"output":String::from_utf8_lossy(&output.stdout),"request_reply":request,
        "additional_connections":extras,"events_before":before,"events_after":after,"test_cleanup_finalize":String::from_utf8_lossy(&cleanup_finalize.stdout)}));drop(gateway);

    // Invalid grace is rejected by the driver before any Unix socket connect.
    let d=root.path().join("invalid");fs::create_dir_all(&d).unwrap();let socket=d.join("count-invalid.sock");let (tx,rx)=std::sync::mpsc::channel();
    let listener=thread::spawn(move||{let l=UnixListener::bind(&socket).unwrap();l.set_nonblocking(true).unwrap();tx.send(()).unwrap();let until=Instant::now()+Duration::from_millis(350);let mut count=0;
        while Instant::now()<until{match l.accept(){Ok((_s,_))=>count+=1,Err(e) if e.kind()==std::io::ErrorKind::WouldBlock=>thread::sleep(Duration::from_millis(5)),Err(e)=>panic!("listener: {e}")}}count});
    rx.recv_timeout(Duration::from_secs(2)).unwrap();let output=invoke_cancel(&d.join("count-invalid.sock"),"valid-job","valid-launch","valid-stop","0");let reply=parse(&output);let connections=listener.join().unwrap();
    assert_eq!(output.status.code(),Some(2),"{reply}");assert_eq!(reply["outcome"],"invalid_input");assert_eq!(connections,0,"invalid input must not connect");
    histories.insert("invalid_input_preconnect".into(),json!({"argv":["cancel",d.join("count-invalid.sock"),"valid-job","valid-launch","valid-stop","0"],"output":String::from_utf8_lossy(&output.stdout),"accepted_connections":connections}));

    persist(json!({"why":"cancel is a bounded explicit stop then finalize consumer; only exact exit evidence permits the separate cancelled finalization",
        "what":"resource-drive cancel -> resource-session -> actual Unix gateway -> retained fixed Child -> Store events and balances; transport proxies only forward and discard one actual reply",
        "how_certain":"native integration histories asserted; raw requests/replies, worker markers, lifecycle events, balances and hashes retained",
        "what_not_tested":["host or power loss","arbitrary process trees or programs","hostile same-UID exclusion","provider workloads","hard wall quiescence"],
        "histories":histories,"source_sha256":hashes()}));
}

/// Relay actual gateway requests. Forward one selected operation, capture its
/// real reply, discard it, and count later connections without affecting Store.
fn drop_reply_once(proxy:PathBuf,gateway:PathBuf,selected:&'static str,ready:std::sync::mpsc::Sender<Value>)->thread::JoinHandle<usize>{
    thread::spawn(move||{let listener=UnixListener::bind(proxy).unwrap();let mut dropped=false;let mut extras=0;let until=Instant::now()+Duration::from_secs(8);let mut buf=[0u8;1024];
        while Instant::now()<until{listener.set_nonblocking(true).unwrap();let (mut down,_)=match listener.accept(){Ok(v)=>v,Err(e) if e.kind()==std::io::ErrorKind::WouldBlock=>{thread::sleep(Duration::from_millis(3));continue},Err(e)=>panic!("accept: {e}")};
            down.set_read_timeout(Some(Duration::from_secs(3))).unwrap();let mut bytes=Vec::new();loop{let n=down.read(&mut buf).unwrap();if n==0{break}assert!(bytes.len()+n<=8192);bytes.extend_from_slice(&buf[..n]);}
            let request:Value=serde_json::from_slice(&bytes).unwrap();let mut up=UnixStream::connect(&gateway).unwrap();up.set_read_timeout(Some(Duration::from_secs(3))).unwrap();up.write_all(&bytes).unwrap();up.shutdown(std::net::Shutdown::Write).unwrap();let mut response=Vec::new();up.read_to_end(&mut response).unwrap();let reply:Value=serde_json::from_slice(&response).unwrap();
            if !dropped&&request["op"]==selected{dropped=true;ready.send(json!({"request":request,"gateway_reply":reply})).unwrap();drop(down);break}
            down.write_all(&response).unwrap();down.shutdown(std::net::Shutdown::Write).unwrap();
        }
        let until=Instant::now()+Duration::from_millis(250);while Instant::now()<until{match listener.accept(){Ok((mut s,_))=>{extras+=1;s.set_read_timeout(Some(Duration::from_millis(100))).unwrap();let _=s.read(&mut buf);},Err(e) if e.kind()==std::io::ErrorKind::WouldBlock=>thread::sleep(Duration::from_millis(5)),Err(e)=>panic!("accept: {e}")}}assert!(dropped,"selected op not observed");extras})
}
fn mutate_reply_once(proxy:PathBuf,gateway:PathBuf,selected:&'static str,field:&'static str,ready:std::sync::mpsc::Sender<Value>)->thread::JoinHandle<usize>{
    thread::spawn(move||{let listener=UnixListener::bind(proxy).unwrap();let mut mutated=false;let mut extras=0;let until=Instant::now()+Duration::from_secs(8);let mut buf=[0u8;1024];
        while Instant::now()<until{listener.set_nonblocking(true).unwrap();let (mut down,_)=match listener.accept(){Ok(v)=>v,Err(e) if e.kind()==std::io::ErrorKind::WouldBlock=>{thread::sleep(Duration::from_millis(3));continue},Err(e)=>panic!("accept: {e}")};
            down.set_read_timeout(Some(Duration::from_secs(3))).unwrap();let mut bytes=Vec::new();loop{let n=down.read(&mut buf).unwrap();if n==0{break}assert!(bytes.len()+n<=8192);bytes.extend_from_slice(&buf[..n]);}
            let request:Value=serde_json::from_slice(&bytes).unwrap();let mut up=UnixStream::connect(&gateway).unwrap();up.set_read_timeout(Some(Duration::from_secs(3))).unwrap();up.write_all(&bytes).unwrap();up.shutdown(std::net::Shutdown::Write).unwrap();let mut response=Vec::new();up.read_to_end(&mut response).unwrap();let actual:Value=serde_json::from_slice(&response).unwrap();
            if !mutated&&request["op"]==selected{let mut changed=actual.clone();changed["result"][field]=json!(format!("mutated-{field}"));let forwarded=serde_json::to_vec(&changed).unwrap();mutated=true;
                ready.send(json!({"request":request,"gateway_reply":actual,"forwarded_reply":changed})).unwrap();down.write_all(&forwarded).unwrap();down.shutdown(std::net::Shutdown::Write).unwrap();drop(down);break}
            down.write_all(&response).unwrap();down.shutdown(std::net::Shutdown::Write).unwrap();
        }
        let end=Instant::now()+Duration::from_millis(250);while Instant::now()<end{match listener.accept(){Ok((mut s,_))=>{extras+=1;s.set_read_timeout(Some(Duration::from_millis(100))).unwrap();let _=s.read(&mut buf);},Err(e) if e.kind()==std::io::ErrorKind::WouldBlock=>thread::sleep(Duration::from_millis(5)),Err(e)=>panic!("accept: {e}")}}assert!(mutated,"selected op not observed");extras})
}
fn record_one_error(proxy:PathBuf,gateway:PathBuf,ready:std::sync::mpsc::Sender<Value>)->thread::JoinHandle<usize>{
    thread::spawn(move||{let listener=UnixListener::bind(proxy).unwrap();listener.set_nonblocking(true).unwrap();let end=Instant::now()+Duration::from_secs(5);let mut buf=[0u8;1024];
        let (mut down,_)=loop{match listener.accept(){Ok(v)=>break v,Err(e) if e.kind()==std::io::ErrorKind::WouldBlock&&Instant::now()<end=>thread::sleep(Duration::from_millis(3)),Err(e)=>panic!("accept: {e}")}};
        down.set_read_timeout(Some(Duration::from_secs(3))).unwrap();let mut bytes=Vec::new();loop{let n=down.read(&mut buf).unwrap();if n==0{break}bytes.extend_from_slice(&buf[..n]);}
        let request:Value=serde_json::from_slice(&bytes).unwrap();let mut up=UnixStream::connect(gateway).unwrap();up.set_read_timeout(Some(Duration::from_secs(3))).unwrap();up.write_all(&bytes).unwrap();up.shutdown(std::net::Shutdown::Write).unwrap();let mut response=Vec::new();up.read_to_end(&mut response).unwrap();let reply:Value=serde_json::from_slice(&response).unwrap();ready.send(json!({"request":request,"reply":reply})).unwrap();down.write_all(&response).unwrap();down.shutdown(std::net::Shutdown::Write).unwrap();drop(down);
        let end=Instant::now()+Duration::from_millis(250);let mut extra=0;while Instant::now()<end{match listener.accept(){Ok((mut s,_))=>{extra+=1;let _=s.read(&mut buf);},Err(e) if e.kind()==std::io::ErrorKind::WouldBlock=>thread::sleep(Duration::from_millis(5)),Err(e)=>panic!("accept: {e}")}}extra})
}
