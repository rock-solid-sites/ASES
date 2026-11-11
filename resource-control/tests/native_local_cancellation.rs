//! Composition test: a native local launch races generic CLI cancellation.
//! Cancellation and begin_launch share Store's transactional state machine.
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
use std::sync::{Arc, Barrier};
use std::thread;
use std::time::{Duration, Instant};

const ACCOUNT: &str = "cancellation-account";
const PROJECT: &str = "cancellation-project";
const ENVIRONMENT: &str = "cancellation-environment";
fn admin_policy()->Policy{Policy{administrators:vec![unsafe{libc::geteuid()}],callers:vec![]}}
fn collector_policy()->Policy{Policy{administrators:vec![],callers:vec![Grant{uid:unsafe{libc::geteuid()},role:"collector".into(),accounts:vec![ACCOUNT.into()],projects:vec![PROJECT.into()]}]}}
fn account()->Account{Account{id:ACCOUNT.into(),provider:"local".into(),payer_ref:"cancel-test-only".into(),registration_status:"verified".into(),credential_status:"working".into(),entitlement_status:"active".into(),allowed_projects:vec![PROJECT.into()],source:"synthetic-native-local-cancellation".into(),observed_at:now(),ttl_seconds:3600}}
fn meter()->Meter{Meter{id:"cancellation-meter".into(),account:ACCOUNT.into(),provider:"local".into(),product:"fixed-cancellation-worker".into(),period:"cancellation-test".into(),unit:"units".into(),limit:100,guard:0,observed_at:now(),ttl_seconds:3600,source:"synthetic-native-local-cancellation".into(),period_start:None,period_end:None,price_per_unit_micros:0,price_currency:None,chargeable:false}}
fn environment()->Environment{Environment{id:ENVIRONMENT.into(),account:ACCOUNT.into(),provider:"local".into(),max_parallel:1,observed_at:now(),ttl_seconds:3600,source:"synthetic-native-local-cancellation".into()}}
fn proposal(job:&str)->Proposal{Proposal{job_id:job.into(),account_id:ACCOUNT.into(),project_id:PROJECT.into(),environment_id:ENVIRONMENT.into(),estimated_wall_seconds:60,claims:vec![Claim{meter_id:"cancellation-meter".into(),amount:50}],paid_spend_cap_micros:None,paid_spend_cap_currency:None,forecast_context:None}}
fn setup(dir:&Path,job:&str)->(PathBuf,i64){let db=dir.join("control.sqlite");let mut store=Store::open(&db).unwrap();store.register_account(&account()).unwrap();store.register_meter(&meter()).unwrap();store.register_environment(&environment()).unwrap();let rev=store.catalog_version().unwrap();store.reserve(&proposal(job),rev,now()).unwrap();store.acknowledge(job,&format!("ack-{job}"),rev,now()).unwrap();(db,rev)}
fn profile(marker:&Path,release:&Path)->Value{json!({"program":std::env::current_exe().unwrap(),"args":["--exact","cancellation_fixed_worker","--nocapture"],"cwd":std::env::current_dir().unwrap(),"env":{"ASES_CANCEL_WORKER_MARKER":marker,"ASES_CANCEL_WORKER_RELEASE":release},"account_id":ACCOUNT,"project_id":PROJECT,"environment_id":ENVIRONMENT})}
struct Gateway{child:Child,socket:PathBuf}
impl Gateway{fn start(dir:&Path,name:&str,db:&Path,policy:&Policy,profile:Option<&Value>)->Self{let socket=dir.join(format!("{name}.sock"));let pol=dir.join(format!("{name}-policy.json"));fs::write(&pol,serde_json::to_vec(policy).unwrap()).unwrap();let mut cmd=Command::new(env!("CARGO_BIN_EXE_resource-gateway"));cmd.arg(db).arg(&socket).arg(pol).arg(env!("CARGO_BIN_EXE_ases-resource-control"));let profile_path=if let Some(profile)=profile{let p=dir.join(format!("{name}-profile.json"));fs::write(&p,serde_json::to_vec(profile).unwrap()).unwrap();cmd.arg(&p);Some(p)}else{None};let _=profile_path;let child=cmd.stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null()).spawn().unwrap();let until=Instant::now()+Duration::from_secs(10);while Instant::now()<until{if socket.exists(){return Self{child,socket};}thread::sleep(Duration::from_millis(10));}panic!("gateway socket did not appear: {}",socket.display())}fn send(&self,r:&Value)->Value{send_to(&self.socket,r)}}
impl Drop for Gateway{fn drop(&mut self){let _=self.child.kill();let _=self.child.wait();}}
fn send_to(socket:&Path,request:&Value)->Value{let mut s=UnixStream::connect(socket).unwrap();s.write_all(serde_json::to_string(request).unwrap().as_bytes()).unwrap();s.shutdown(std::net::Shutdown::Write).unwrap();let mut b=Vec::new();s.read_to_end(&mut b).unwrap();serde_json::from_slice(&b).unwrap()}
struct Release(PathBuf);impl Drop for Release{fn drop(&mut self){let _=fs::write(&self.0,b"release\n");}}
fn wait_for(path:&Path){let end=Instant::now()+Duration::from_secs(10);while Instant::now()<end{if path.exists(){return}thread::sleep(Duration::from_millis(10));}panic!("fixed worker did not reach marker {}",path.display())}
fn worker_rows(path:&Path)->Vec<Value>{fs::read_to_string(path).unwrap_or_default().lines().map(|l|serde_json::from_str(l).unwrap()).collect()}
fn events(db:&Path,job:&str)->Vec<Value>{Store::open(db).unwrap().event_log(Some(job)).unwrap()}
fn remaining(db:&Path)->i64{Store::open(db).unwrap().balances(now()).unwrap().into_iter().find(|b|b.meter_id=="cancellation-meter").unwrap().active_reserved_remaining}
fn alive(pid:u32,token:&str)->bool{let Ok(raw)=fs::read_to_string(format!("/proc/{pid}/stat"))else{return false};let Some((_,tail))=raw.rsplit_once(") ")else{return false};let mut f=tail.split_whitespace();let state=f.next().and_then(|s|s.chars().next());let start=f.nth(18);matches!(state,Some('R'|'S'))&&start==Some(token)}
fn persist(file:&str,data:Value){if let Some(dir)=std::env::var_os("ASES_LOCAL_CANCELLATION_EVIDENCE_DIR"){let dir=PathBuf::from(dir);fs::create_dir_all(&dir).unwrap();fs::write(dir.join(file),serde_json::to_vec_pretty(&data).unwrap()).unwrap();}}
fn source_hashes()->Value{let root=PathBuf::from(env!("CARGO_MANIFEST_DIR"));let mut m=serde_json::Map::new();for p in ["src/main.rs","src/lib.rs","src/local.rs","src/bin/resource-gateway.rs","tests/native_local_cancellation.rs","../docs/research/phase-ii-local-execution/CANCELLATION.md"]{if let Ok(b)=fs::read(root.join(p)){m.insert(p.into(),json!(format!("{:x}",Sha256::digest(b))));}}Value::Object(m)}

#[test]
fn cancellation_fixed_worker(){let Some(marker)=std::env::var_os("ASES_CANCEL_WORKER_MARKER")else{return};let release=PathBuf::from(std::env::var_os("ASES_CANCEL_WORKER_RELEASE").unwrap());let pid=std::process::id();let stat=fs::read_to_string(format!("/proc/{pid}/stat")).unwrap();let token=stat.rsplit_once(") ").unwrap().1.split_whitespace().nth(19).unwrap();let mut f=OpenOptions::new().create(true).append(true).open(marker).unwrap();serde_json::to_writer(&mut f,&json!({"pid":pid,"start_token":token})).unwrap();f.write_all(b"\n").unwrap();f.sync_all().unwrap();let until=Instant::now()+Duration::from_secs(20);while !release.exists()&&Instant::now()<until{thread::sleep(Duration::from_millis(10));}std::process::exit(0)}

#[test]
fn generic_cancel_and_native_launch_have_only_safe_transactional_outcomes(){
    let mut evidence=Vec::new();
    // Cancellation first closes the authorized job; a later native launch is denied and never spawns.
    {
        let dir=tempfile::tempdir().unwrap();let(db,revision)=setup(dir.path(),"cancel-first-job");let marker=dir.path().join("cancel-first-worker.jsonl");let release=dir.path().join("cancel-first-release");let _r=Release(release.clone());let trusted=profile(&marker,&release);
        let native=Gateway::start(dir.path(),"native",&db,&admin_policy(),Some(&trusted));let cli=Gateway::start(dir.path(),"collector",&db,&collector_policy(),None);
        let cancel=json!({"op":"finalize","job_id":"cancel-first-job","outcome":"cancelled"});let before=events(&db,"cancel-first-job");let cancel_reply=cli.send(&cancel);let after_cancel=events(&db,"cancel-first-job");
        assert_eq!(cancel_reply["ok"],true,"generic controller cancellation response");assert_eq!(Store::open(&db).unwrap().job("cancel-first-job").unwrap()["state"],"CLOSED");assert_eq!(remaining(&db),0);
        let launch=json!({"op":"local_launch","job_id":"cancel-first-job","launch_id":"cancel-first-launch","expected_catalog":revision});let launch_reply=native.send(&launch);
        assert_eq!(launch_reply["ok"],false,"closed job cannot dispatch");assert!(worker_rows(&marker).is_empty());let final_events=events(&db,"cancel-first-job");assert_eq!(final_events.iter().filter(|e|e["kind"]=="LAUNCH_INTENT").count(),0);assert_eq!(final_events.iter().filter(|e|e["kind"]=="FINALIZED").count(),1);
        evidence.push(json!({"phase":"cancel-first","cancel_request":cancel,"cancel_response":cancel_reply,"events_before":before,"events_after_cancel":after_cancel,"launch_request":launch,"launch_response":launch_reply,"events_after_launch_attempt":final_events,"worker_count":0,"capacity_after_cancel":0}));
    }
    // Launch first records a living child; generic CLI cancellation cannot release its reservation.
    {
        let dir=tempfile::tempdir().unwrap();let(db,revision)=setup(dir.path(),"launch-first-job");let marker=dir.path().join("launch-first-worker.jsonl");let release=dir.path().join("launch-first-release");let _r=Release(release.clone());let trusted=profile(&marker,&release);
        let native=Gateway::start(dir.path(),"native",&db,&admin_policy(),Some(&trusted));let cli=Gateway::start(dir.path(),"collector",&db,&collector_policy(),None);
        let launch=json!({"op":"local_launch","job_id":"launch-first-job","launch_id":"launch-first-launch","expected_catalog":revision});let launch_reply=native.send(&launch);assert_eq!(launch_reply["ok"],true);wait_for(&marker);let worker=worker_rows(&marker);assert_eq!(worker.len(),1);
        let cancel=json!({"op":"finalize","job_id":"launch-first-job","outcome":"cancelled"});let before=events(&db,"launch-first-job");let held_before=remaining(&db);let cancel_reply=cli.send(&cancel);let after=events(&db,"launch-first-job");
        assert_eq!(cancel_reply["ok"],false,"generic finalize is blocked for a live intent-backed child");assert_eq!(after,before,"blocked cancellation writes no terminal event");assert_eq!(Store::open(&db).unwrap().job("launch-first-job").unwrap()["state"],"RUNNING");assert_eq!(remaining(&db),held_before);assert!(alive(worker[0]["pid"].as_u64().unwrap().try_into().unwrap(),worker[0]["start_token"].as_str().unwrap()));
        let stop=json!({"op":"local_stop","job_id":"launch-first-job","launch_id":"launch-first-launch","stop_id":"launch-first-stop"});let stop_reply=native.send(&stop);assert_eq!(stop_reply["ok"],true);let finish=json!({"op":"local_finalize","job_id":"launch-first-job","launch_id":"launch-first-launch","outcome":"cancelled"});let finish_reply=native.send(&finish);assert_eq!(finish_reply["ok"],true);assert_eq!(remaining(&db),0);
        evidence.push(json!({"phase":"launch-first","launch_request":launch,"launch_response":launch_reply,"worker":worker[0],"generic_cancel_request":cancel,"generic_cancel_response":cancel_reply,"events_before_cancel":before,"events_after_cancel":after,"capacity_held":held_before,"worker_alive_after_block":true,"stop_request":stop,"stop_response":stop_reply,"explicit_finalize_request":finish,"explicit_finalize_response":finish_reply,"events_final":events(&db,"launch-first-job"),"capacity_after_finalize":remaining(&db)}));
    }
    // Actual simultaneous calls on separate gateways must linearize to one of the safe histories above.
    {
        let dir=tempfile::tempdir().unwrap();let(db,revision)=setup(dir.path(),"racing-job");let marker=dir.path().join("racing-worker.jsonl");let release=dir.path().join("racing-release");let _r=Release(release.clone());let trusted=profile(&marker,&release);
        let native=Gateway::start(dir.path(),"native-race",&db,&admin_policy(),Some(&trusted));let cli=Gateway::start(dir.path(),"collector-race",&db,&collector_policy(),None);
        let launch=json!({"op":"local_launch","job_id":"racing-job","launch_id":"racing-launch","expected_catalog":revision});let cancel=json!({"op":"finalize","job_id":"racing-job","outcome":"cancelled"});let barrier=Arc::new(Barrier::new(3));let nbar=barrier.clone();let cbar=barrier.clone();let ns=native.socket.clone();let cs=cli.socket.clone();let lr=launch.clone();let cr=cancel.clone();
        let n=thread::spawn(move||{nbar.wait();send_to(&ns,&lr)});let c=thread::spawn(move||{cbar.wait();send_to(&cs,&cr)});barrier.wait();let launch_reply=n.join().unwrap();let cancel_reply=c.join().unwrap();
        let job=Store::open(&db).unwrap().job("racing-job").unwrap();let rows=worker_rows(&marker);let ev=events(&db,"racing-job");
        if launch_reply["ok"]==true{
            assert_eq!(rows.len(),1);assert_eq!(cancel_reply["ok"],false);assert_eq!(job["state"],"RUNNING");assert_eq!(remaining(&db),50);assert!(ev.iter().any(|e|e["kind"]=="LAUNCH_INTENT"));assert!(ev.iter().any(|e|e["kind"]=="LAUNCH_STARTED_OBSERVED"));assert!(alive(rows[0]["pid"].as_u64().unwrap().try_into().unwrap(),rows[0]["start_token"].as_str().unwrap()));
            let stop=json!({"op":"local_stop","job_id":"racing-job","launch_id":"racing-launch","stop_id":"race-cleanup-stop"});let stop_reply=native.send(&stop);assert_eq!(stop_reply["ok"],true);let finish=json!({"op":"local_finalize","job_id":"racing-job","launch_id":"racing-launch","outcome":"cancelled"});let finish_reply=native.send(&finish);assert_eq!(finish_reply["ok"],true);assert_eq!(remaining(&db),0);
            evidence.push(json!({"phase":"simultaneous-race","outcome":"launch-linearized-first","launch_request":launch,"launch_response":launch_reply,"cancel_request":cancel,"cancel_response":cancel_reply,"events_before_cleanup":ev,"worker":rows[0],"capacity_held_before_cleanup":50,"cleanup_stop":stop_reply,"cleanup_finalize":finish_reply,"capacity_after_cleanup":remaining(&db)}));
        }else{
            assert_eq!(cancel_reply["ok"],true);assert!(rows.is_empty());assert_eq!(job["state"],"CLOSED");assert_eq!(job["outcome"],"cancelled");assert_eq!(remaining(&db),0);assert!(!ev.iter().any(|e|e["kind"]=="LAUNCH_INTENT"));assert_eq!(ev.iter().filter(|e|e["kind"]=="FINALIZED").count(),1);
            evidence.push(json!({"phase":"simultaneous-race","outcome":"cancellation-linearized-first","launch_request":launch,"launch_response":launch_reply,"cancel_request":cancel,"cancel_response":cancel_reply,"events":ev,"worker_count":0,"capacity_after_cancel":0}));
        }
    }
    persist("cancellation-history.json",json!({"source_sha256":source_hashes(),"records":evidence}));
}
